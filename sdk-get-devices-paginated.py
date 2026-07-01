"""
Catalyst Center SDK — Pagination Demo
--------------------------------------
Shows how to use offset and limit with the Catalyst Center Python SDK
(catalystcentersdk) to paginate through network devices.

Unlike raw REST calls (requests library), the SDK wraps the same
/dna/intent/api/v1/network-device endpoint but gives you:
  • Python attribute access on responses  (device.hostname, device.upTime)
  • Automatic JSON parsing
  • Built-in session / retry handling
  • Type-hinted parameters

The SDK does NOT auto-paginate for you — you still need to manage
offset and limit yourself, exactly as with raw REST calls.

SDK docs: https://github.com/cisco-en-programmability/catalystcentersdk

Dependencies: catalystcentersdk, python-dotenv
Configuration: set CATALYST_USERNAME, CATALYST_PASSWORD, CATALYST_BASE_URL,
               and CATALYST_VERSION in a .env file.
"""

import os
import time
import warnings
warnings.filterwarnings("ignore", message=".*urllib3.*", category=Warning)

from dotenv import load_dotenv
from catalystcentersdk import api

load_dotenv()

# ---------------------------------------------------------------------------
# SDK initialisation
# The SDK handles authentication automatically — no manual token management.
# ---------------------------------------------------------------------------
catalyst = api.CatalystCenterAPI(
    username=os.getenv("CATALYST_USERNAME"),
    password=os.getenv("CATALYST_PASSWORD"),
    base_url=os.getenv("CATALYST_BASE_URL"),
    version=os.getenv("CATALYST_VERSION"),
    verify=False,
)


# ---------------------------------------------------------------------------
# Helper — formatted table output
# ---------------------------------------------------------------------------

def print_devices(devices, title="Network Devices"):
    """Print a list of SDK device objects as a formatted table.

    Each item in `devices` is a catalystcentersdk MyDict object, so fields
    are accessed as attributes (device.hostname) rather than dict keys.
    """
    print(f"\n{title}")
    print("=" * 100)
    print(f"{'HOSTNAME':<40} {'IP ADDRESS':<20} {'FAMILY':<25} {'TYPE'}")
    print("-" * 100)
    for device in devices:
        print(
            f"{getattr(device, 'hostname', 'N/A'):<40}"
            f" {getattr(device, 'managementIpAddress', 'N/A'):<20}"
            f" {getattr(device, 'family', 'N/A'):<25}"
            f" {getattr(device, 'type', 'N/A')}"
        )
    print("-" * 100)
    print(f"Total: {len(devices)} device(s)\n")


# ---------------------------------------------------------------------------
# Core pagination helpers
# ---------------------------------------------------------------------------

def get_devices_page(offset=1, limit=10, **filters):
    """Fetch a single page of network devices via the SDK.

    SDK method: catalyst.devices.get_device_list()

    Default SDK behaviour (when offset/limit are omitted):
      - offset : not sent → API defaults to 1 (first record)
      - limit  : not sent → API defaults to 500 (its own maximum per page)

    Args:
        offset  (int): 1-based starting position in the full result set.
                       offset=1  → start from the first device.
                       offset=11 → skip the first 10, start from the 11th.
        limit   (int): Maximum records to return in this call (max 500).
        **filters    : Any additional SDK filter keyword arguments, e.g.
                       family="Switches and Hubs",
                       reachability_status="Reachable",
                       role="ACCESS",
                       software_version="17.3.4a"

    Returns:
        list: SDK MyDict objects for the requested page (may be empty on
              last page when fewer records remain than limit).
    """
    response = catalyst.devices.get_device_list(
        offset=offset,
        limit=limit,
        **filters,
    )
    # The SDK wraps the JSON body; `.response` is the list of device objects.
    return response.response or []


def get_all_devices_sdk(page_size=50, **filters):
    """Retrieve ALL network devices by iterating pages with the SDK.

    The SDK does NOT auto-paginate, so we loop manually — advancing offset
    by page_size each iteration — until the API returns fewer records than
    page_size (signals the last page) or an empty list.

    Default SDK behaviour (when page_size / filters are omitted):
      - The SDK would return up to 500 devices in one call; devices beyond
        500 would be silently missing.  This function ensures completeness.

    Args:
        page_size (int): Records per SDK call (default 50, max 500).
                         Larger values mean fewer round-trips but bigger
                         payloads.  500 is the API-enforced maximum.
        **filters       : Passed straight to get_device_list(), e.g.
                          family="Routers",
                          reachability_status="Reachable"

    Returns:
        list: All matching device objects across all pages.
    """
    all_devices = []
    offset = 1

    while True:
        print(f"  SDK call → offset={offset}, limit={page_size} ...")
        page = get_devices_page(offset=offset, limit=page_size, **filters)

        if not page:
            break                     # empty page → no more data

        all_devices.extend(page)
        print(f"  ↳ got {len(page)} device(s)  (total so far: {len(all_devices)})")

        if len(page) < page_size:
            break                     # partial page → last page reached

        offset += page_size

    return all_devices


# ---------------------------------------------------------------------------
# Cache (in-memory, 5-minute TTL)
# ---------------------------------------------------------------------------

_cache    = {}
CACHE_TTL = 300   # seconds


def get_all_devices_cached(page_size=50, cache_ttl=CACHE_TTL, **filters):
    """Cached wrapper around get_all_devices_sdk().

    Stores the complete device list in memory for cache_ttl seconds.
    Subsequent calls within the TTL window return the cached list without
    making any SDK / API calls — useful for dashboards or scripts that
    call this function repeatedly.

    Default SDK behaviour (no cache):
      Every call triggers N API round-trips (one per page).  With a 5-min
      cache and 30-second dashboard refresh, you go from 120 API calls/hour
      down to ~12 — a 90 % reduction.

    Args:
        page_size (int): Passed to get_all_devices_sdk() on cache miss.
        cache_ttl (int): Cache lifetime in seconds (default 300 = 5 min).
        **filters       : Passed to get_all_devices_sdk() on cache miss.

    Returns:
        dict: {
            "devices"   : list of device objects,
            "cached"    : True if result came from cache (no API calls),
            "cache_age" : seconds since cache was last populated (0 = fresh)
        }
    """
    cache_key    = f"devices_{hash(str(sorted(filters.items())))}"
    current_time = time.time()

    if cache_key in _cache:
        age = current_time - _cache[cache_key]["timestamp"]
        if age < cache_ttl:
            print(f"✅ Cache HIT  — age: {age:.1f}s  (TTL: {cache_ttl}s)  ⚡ No API calls!")
            return {"devices": _cache[cache_key]["data"], "cached": True, "cache_age": age}
        print(f"⏰ Cache EXPIRED — age: {age:.1f}s exceeded TTL: {cache_ttl}s")
    else:
        print("❌ Cache MISS — fetching fresh data via SDK...")

    devices = get_all_devices_sdk(page_size=page_size, **filters)
    _cache[cache_key] = {"data": devices, "timestamp": time.time()}
    print(f"💾 Cached {len(devices)} device(s) for {cache_ttl}s")

    return {"devices": devices, "cached": False, "cache_age": 0}


# ---------------------------------------------------------------------------
# Main — four examples
# ---------------------------------------------------------------------------

def main():
    # -----------------------------------------------------------------------
    # Example 1: Single page — first 10 devices (no filter)
    # -----------------------------------------------------------------------
    print("\n" + "=" * 100)
    print("EXAMPLE 1: First 10 devices  (offset=1, limit=10)")
    print("=" * 100)
    page1 = get_devices_page(offset=1, limit=10)
    print_devices(page1, "First 10 Devices")

    # -----------------------------------------------------------------------
    # Example 2: Second page — devices 11-20
    # -----------------------------------------------------------------------
    print("\n" + "=" * 100)
    print("EXAMPLE 2: Next 10 devices  (offset=11, limit=10)")
    print("=" * 100)
    page2 = get_devices_page(offset=11, limit=10)
    print_devices(page2, "Devices 11–20")

    # -----------------------------------------------------------------------
    # Example 3: All devices — automatic pagination (no filter)
    # SDK does not paginate automatically; we loop until the last page.
    # -----------------------------------------------------------------------
    print("\n" + "=" * 100)
    print("EXAMPLE 3: All devices — automatic pagination  (page_size=50)")
    print("=" * 100)
    all_devices = get_all_devices_sdk(page_size=50)
    print_devices(all_devices, f"All Devices ({len(all_devices)} total)")

    # -----------------------------------------------------------------------
    # Example 4: Filtered + paginated — only reachable switches, page 1
    #
    # Optional SDK filter parameters for get_device_list():
    #   family              – e.g. "Switches and Hubs", "Routers"
    #   reachability_status – "Reachable" | "Unreachable" | "PingReachable"
    #   role                – "ACCESS" | "DISTRIBUTION" | "CORE" | "BORDER_ROUTER"
    #   software_version    – e.g. "17.3.4a"
    #   platform_id         – e.g. "C9300-48UXM"
    #   management_ip_address – exact or wildcard (192.168.1.*)
    # -----------------------------------------------------------------------
    print("\n" + "=" * 100)
    print("EXAMPLE 4: Filtered — Switches and Hubs, first 25  (offset=1, limit=25)")
    print("=" * 100)
    switches = get_devices_page(
        offset=1,
        limit=25,
        family="Switches and Hubs",
    )
    print_devices(switches, "First 25 Switches")

    # -----------------------------------------------------------------------
    # Example 5: Caching — avoid repeated SDK/API calls
    # -----------------------------------------------------------------------
    print("\n" + "=" * 100)
    print("EXAMPLE 5: Caching (5-minute TTL)")
    print("=" * 100)

    print("\n--- CALL 1 (t=0s) — expect cache MISS ---")
    r1 = get_all_devices_cached(page_size=50)
    print(f"Devices: {len(r1['devices'])}  |  From cache: {r1['cached']}")

    time.sleep(2)

    print("\n--- CALL 2 (t≈2s) — expect cache HIT ---")
    r2 = get_all_devices_cached(page_size=50)
    print(f"Devices: {len(r2['devices'])}  |  From cache: {r2['cached']}  |  Age: {r2['cache_age']:.1f}s")

    print("\n💡 Summary:")
    print(f"   Made 1 set of API calls instead of 2")
    print(f"   Cache expires in {CACHE_TTL - r2['cache_age']:.0f}s")


if __name__ == "__main__":
    main()
