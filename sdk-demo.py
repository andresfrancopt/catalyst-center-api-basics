"""
Catalyst Center SDK Demo
------------------------
This script connects to a Cisco Catalyst Center instance using credentials
loaded from a .env file. It performs the following actions:

  1. Retrieves and displays all network devices in the 'Switches and Hubs'
     family, showing their hostname and uptime.
  2. Fetches all tags and deletes any that contain 'Demo' in their name.

Dependencies: catalystcentersdk, python-dotenv
Configuration: set CATALYST_USERNAME, CATALYST_PASSWORD, CATALYST_BASE_URL,
               and CATALYST_VERSION in a .env file.

-------------------------------------------------------------------------------
DISCLAIMER
-------------------------------------------------------------------------------
This script is intended for educational and demonstration purposes only.
It is provided "as is" without warranty of any kind, express or implied.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES, OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

This code has not been validated for production use. Test thoroughly in a
lab environment before using in any production or critical system. The author
assumes no responsibility for network outages, data loss, or any other issues
resulting from the use of this script.
-------------------------------------------------------------------------------
"""

import os
import warnings
warnings.filterwarnings("ignore", message=".*urllib3.*", category=Warning)

from dotenv import load_dotenv
from catalystcentersdk import api

load_dotenv()

catalyst = api.CatalystCenterAPI(username=os.getenv("CATALYST_USERNAME"),
                        password=os.getenv("CATALYST_PASSWORD"),
                        base_url=os.getenv("CATALYST_BASE_URL"),
                        version=os.getenv("CATALYST_VERSION"),
                        verify=False)

# Find all devices that have 'Switches and Hubs' in their family
devices = catalyst.devices.get_device_list(family='Switches and Hubs')

# Print all devices with formatted table
print(f"\n{'HOSTNAME':<50} {'UPTIME'}")
print("-" * 75)
for device in devices.response:
    print(f"{device.hostname:<50} {device.upTime}")
print("-" * 75)
print(f"Total devices: {len(devices.response)}\n")

# Find all tags
all_tags = catalyst.tag.get_tag(sort_by='name', order='des')
demo_tags = [tag for tag in all_tags.response if 'Demo' in tag.name]

# Delete all demo tags with feedback
if not demo_tags:
    print("No Demo tags found.")
else:
    print(f"Found {len(demo_tags)} Demo tag(s):")
    for tag in demo_tags:
        catalyst.tag.delete_tag(tag.id)
        print(f"  ✓ Deleted tag: '{tag.name}'")