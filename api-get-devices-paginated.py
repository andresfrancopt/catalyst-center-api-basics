"""
Catalyst Center - Network Devices with Pagination
--------------------------------------------------
Demonstrates how to use offset and limit parameters to paginate through
network devices in Cisco Catalyst Center.

The API endpoint supports:
- offset: Starting index for records (default: 1)
- limit: Maximum number of records to return (max: 500)

Dependencies: requests, python-dotenv
Configuration: set CATALYST_USERNAME, CATALYST_PASSWORD, CATALYST_BASE_URL
               in a .env file.
"""

import os
import time
import warnings
warnings.filterwarnings("ignore", message=".*urllib3.*", category=Warning)

import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("CATALYST_BASE_URL")
USERNAME = os.getenv("CATALYST_USERNAME")
PASSWORD = os.getenv("CATALYST_PASSWORD")


# Cache storage: {cache_key: {"data": result, "timestamp": time}}
_cache = {}
CACHE_TTL = 300  # 5 minutes (300 seconds)


def get_auth_token():
    """Authenticate and return an X-Auth-Token."""
    url = f"{BASE_URL}/dna/system/api/v1/auth/token"
    response = requests.post(url, auth=HTTPBasicAuth(USERNAME, PASSWORD), verify=False)
    response.raise_for_status()
    return response.json()["Token"]


def get_devices_paginated(token, offset=1, limit=10):
    """
    Retrieve network devices with pagination.
    
    Args:
        token: Authentication token
        offset: Starting record index (default: 1)
        limit: Number of records to retrieve (default: 10, max: 500)
    
    Returns:
        dict: Response containing devices and total count
    """
    url = f"{BASE_URL}/dna/intent/api/v1/network-device"
    headers = {"X-Auth-Token": token}
    params = {
        "offset": offset,
        "limit": limit
    }
    response = requests.get(url, headers=headers, params=params, verify=False)
    response.raise_for_status()
    return response.json()


def get_all_devices(token, page_size=50):
    """
    Retrieve ALL network devices by paginating through the entire dataset.
    
    Args:
        token: Authentication token
        page_size: Number of records per request (default: 50, max: 500)
    
    Returns:
        list: All devices from all pages
    """
    all_devices = []
    offset = 1
    
    while True:
        print(f"Fetching page starting at offset {offset}...")
        data = get_devices_paginated(token, offset=offset, limit=page_size)
        devices = data.get("response", [])
        
        if not devices:
            break
        
        all_devices.extend(devices)
        print(f"Retrieved {len(devices)} devices (Total so far: {len(all_devices)})")
        
        # Move to next page
        offset += page_size
        
        # If we got fewer devices than requested, we've reached the end
        if len(devices) < page_size:
            break
    
    return all_devices


def get_all_devices_cached(token, page_size=50, cache_ttl=CACHE_TTL):
    """
    Retrieve ALL network devices with caching support.
    
    Results are cached for cache_ttl seconds (default: 5 minutes).
    Subsequent calls within the cache period return cached data
    WITHOUT making API calls - saving time and avoiding rate limits.
    
    Args:
        token: Authentication token
        page_size: Number of records per request (default: 50, max: 500)
        cache_ttl: Cache time-to-live in seconds (default: 300 = 5 minutes)
    
    Returns:
        dict: {
            "devices": list of all devices,
            "cached": bool indicating if result came from cache,
            "cache_age": seconds since cache was populated (0 if fresh)
        }
    """
    cache_key = "all_devices"
    current_time = time.time()
    
    # Check if cache exists and is still valid
    if cache_key in _cache:
        cached_entry = _cache[cache_key]
        cache_age = current_time - cached_entry["timestamp"]
        
        if cache_age < cache_ttl:
            print(f"✅ Cache HIT! Using cached data (age: {cache_age:.1f}s, TTL: {cache_ttl}s)")
            return {
                "devices": cached_entry["data"],
                "cached": True,
                "cache_age": cache_age
            }
        else:
            print(f"⏰ Cache EXPIRED (age: {cache_age:.1f}s > TTL: {cache_ttl}s)")
    else:
        print(f"❌ Cache MISS - fetching fresh data...")
    
    # Cache miss or expired - fetch fresh data
    print(f"🌐 Making API calls to fetch all devices...")
    all_devices = get_all_devices(token, page_size)
    
    # Store in cache
    _cache[cache_key] = {
        "data": all_devices,
        "timestamp": current_time
    }
    print(f"💾 Cached {len(all_devices)} devices for {cache_ttl}s")
    
    return {
        "devices": all_devices,
        "cached": False,
        "cache_age": 0
    }


def print_devices(devices, title="Network Devices"):
    """Print devices in a formatted table."""
    print(f"\n{title}")
    print("=" * 100)
    print(f"{'HOSTNAME':<40} {'IP ADDRESS':<20} {'FAMILY':<25} {'TYPE'}")
    print("-" * 100)
    
    for device in devices:
        hostname = device.get("hostname", "N/A")
        ip = device.get("managementIpAddress", "N/A")
        family = device.get("family", "N/A")
        device_type = device.get("type", "N/A")
        print(f"{hostname:<40} {ip:<20} {family:<25} {device_type}")
    
    print("-" * 100)
    print(f"Total devices: {len(devices)}\n")


def main():
    """Main execution demonstrating different pagination approaches."""
    token = get_auth_token()
    
    # Example 1: Get first 10 devices
    print("\n" + "="*100)
    print("EXAMPLE 1: First 10 devices (offset=1, limit=10)")
    print("="*100)
    result = get_devices_paginated(token, offset=1, limit=10)
    devices = result.get("response", [])
    print_devices(devices, "First 10 Devices")
    
    # Example 2: Get next 10 devices (page 2)
    print("\n" + "="*100)
    print("EXAMPLE 2: Next 10 devices (offset=11, limit=10)")
    print("="*100)
    result = get_devices_paginated(token, offset=11, limit=10)
    devices = result.get("response", [])
    print_devices(devices, "Devices 11-20")
    
    # Example 3: Get all devices with automatic pagination
    print("\n" + "="*100)
    print("EXAMPLE 3: All devices (automatic pagination)")
    print("="*100)
    all_devices = get_all_devices(token, page_size=50)
    print_devices(all_devices, f"All Devices ({len(all_devices)} total)")
    
    # Example 4: Filtered pagination (e.g., only switches)
    print("\n" + "="*100)
    print("EXAMPLE 4: Paginated switches only (offset=1, limit=25)")
    print("="*100)
    url = f"{BASE_URL}/dna/intent/api/v1/network-device"
    headers = {"X-Auth-Token": token}
    params = {
        "family": "Switches and Hubs",
        "offset": 1,
        "limit": 25
    }
    response = requests.get(url, headers=headers, params=params, verify=False)
    response.raise_for_status()
    switches = response.json().get("response", [])
    print_devices(switches, "First 25 Switches")
    
    # Example 5: Caching (5 minutes) to avoid repeated API calls
    print("\n" + "="*100)
    print("EXAMPLE 5: Caching results for 5 minutes")
    print("="*100)
    print("\n📌 Scenario: Multiple scripts/functions need device inventory")
    print("   Without caching: Each call = multiple API requests")
    print("   With caching: First call hits API, rest use cache (5 min)")
    
    # First call - cache miss
    print("\n--- FIRST CALL (t=0s) ---")
    result1 = get_all_devices_cached(token, page_size=50)
    print(f"Devices retrieved: {len(result1['devices'])}")
    print(f"From cache: {result1['cached']}")
    print(f"Cache age: {result1['cache_age']:.1f}s")
    
    # Second call immediately - cache hit
    print("\n--- SECOND CALL (t=1s) - Immediate ---")
    time.sleep(1)
    result2 = get_all_devices_cached(token, page_size=50)
    print(f"Devices retrieved: {len(result2['devices'])}")
    print(f"From cache: {result2['cached']} ⚡ (NO API CALLS!)")
    print(f"Cache age: {result2['cache_age']:.1f}s")
    
    # Third call after 3 seconds - still cached
    print("\n--- THIRD CALL (t=4s) - After 3 seconds ---")
    time.sleep(3)
    result3 = get_all_devices_cached(token, page_size=50)
    print(f"Devices retrieved: {len(result3['devices'])}")
    print(f"From cache: {result3['cached']} ⚡ (NO API CALLS!)")
    print(f"Cache age: {result3['cache_age']:.1f}s")
    
    print("\n💡 CACHE BENEFITS:")
    print(f"   ✅ Made 1 API call instead of 3")
    print(f"   ✅ Saved ~{result3['cache_age']:.0f}s of API time")
    print(f"   ✅ Reduced load on Catalyst Center")
    print(f"   ✅ Avoided potential rate limiting")
    print(f"   ⏰ Cache expires in {CACHE_TTL - result3['cache_age']:.0f}s")
    
    print("\n📝 Production Use Case:")
    print("   - Dashboard refreshes every 30 seconds")
    print("   - Without cache: 120 API calls/hour per user")
    print("   - With 5-min cache: 12 API calls/hour per user")
    print("   - Savings: 90% reduction in API calls! 🎉")


if __name__ == "__main__":
    main()
