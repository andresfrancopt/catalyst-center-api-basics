# Cisco Catalyst Center API Examples

A collection of Python scripts and Jupyter notebooks demonstrating how to interact with Cisco Catalyst Center's REST API. Examples cover two distinct approaches — raw REST calls and the official Python SDK — including pagination, caching, and best practices.

## 📋 Table of Contents

- [Overview](#overview)
- [File Naming Convention](#file-naming-convention)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Scripts](#scripts)
  - [Pure Python REST (`api-`)](#pure-python-rest-api--prefix)
  - [Catalyst Center SDK (`sdk-`)](#catalyst-center-sdk-sdk--prefix)
  - [Jupyter Notebooks (`nb-`)](#jupyter-notebooks-nb--prefix)
- [Project Structure](#project-structure)
- [API Endpoints Used](#api-endpoints-used)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview

This project demonstrates two ways to interact with Cisco Catalyst Center, each available as standalone scripts and as interactive Jupyter notebooks:

| Approach | Scripts | Notebooks |
|----------|---------|-----------|
| **Pure Python REST** — `requests` library, manual auth | `api-get-switches.py` · `api-get-devices-paginated.py` | `nb-api-switches-tutorial.ipynb` |
| **Catalyst Center SDK** — `catalystcentersdk`, auto-auth | `sdk-demo.py` · `sdk-get-devices-paginated.py` | `nb-sdk-devices-tutorial.ipynb` |

---

## 🏷️ File Naming Convention

Files are prefixed so the approach is clear at a glance:

| Prefix | Approach |
|--------|----------|
| `api-` | Pure Python — raw REST calls with `requests` |
| `sdk-` | Catalyst Center SDK (`catalystcentersdk`) |
| `nb-api-` | Jupyter notebook — raw REST |
| `nb-sdk-` | Jupyter notebook — SDK |

---

## ✅ Prerequisites

- **Python 3.9+** (Python 3.8 may work but 3.9+ recommended)
- **Cisco Catalyst Center** instance with API access
- **Network connectivity** to your Catalyst Center
- **API credentials** (username and password)

---

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/catalyst-center-api-examples.git
cd catalyst-center-api-examples
```

### 2. Create a Virtual Environment

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Register the Jupyter Kernel

Required once before opening any notebook:

```bash
python -m ipykernel install --user --name=catalyst-center --display-name="Python (Catalyst Center)"
```

---

## ⚙️ Configuration

### Create Your Environment File

1. **Copy the example environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` with your credentials:**
   ```bash
   nano .env  # or use your preferred editor
   ```

3. **Update the values:**
   ```env
   CATALYST_USERNAME=your_username_here
   CATALYST_PASSWORD=your_password_here
   CATALYST_BASE_URL=https://your-catalyst-center-ip-or-hostname
   CATALYST_VERSION=2.3.7.9
   ```

   **Example:**
   ```env
   CATALYST_USERNAME=admin
   CATALYST_PASSWORD=C1sc0123!
   CATALYST_BASE_URL=https://10.10.20.85
   CATALYST_VERSION=2.3.7.9
   ```

### Important Notes:

- ⚠️ **Never commit your `.env` file** - it's already in `.gitignore`
- 🔒 **Keep credentials secure** - don't share your `.env` file
- 🌐 **Use HTTPS** - ensure your BASE_URL uses `https://`
- 🔐 **SSL Certificates** - Examples use `verify=False` for simplicity. In production, use proper SSL certificates.

---

## 📚 Scripts

### Pure Python REST (`api-` prefix)

**Best for:** Understanding the raw API, maximum control, minimal dependencies.  
Auth is manual: POST credentials → receive token → include token in every request header.

#### `api-get-switches.py`

Authenticates and retrieves all devices in the "Switches and Hubs" family.

```bash
python api-get-switches.py
```

**Code highlights:**
```python
# Manual authentication
def get_auth_token():
    url = f"{BASE_URL}/dna/system/api/v1/auth/token"
    response = requests.post(url, auth=HTTPBasicAuth(USERNAME, PASSWORD), verify=False)
    return response.json()["Token"]

# Token passed explicitly in every call
def get_switches(token):
    headers = {"X-Auth-Token": token}
    params  = {"family": "Switches and Hubs"}
    response = requests.get(url, headers=headers, params=params, verify=False)
    return response.json().get("response", [])
```

#### `api-get-devices-paginated.py`

Demonstrates `offset` / `limit` pagination and in-memory caching (5-minute TTL).

```bash
python api-get-devices-paginated.py
```

Runs five examples:
1. First 10 devices (`offset=1, limit=10`)
2. Next 10 devices (`offset=11, limit=10`)
3. All devices — automatic pagination loop
4. Filtered page — switches only
5. Caching demo — MISS then HIT

---

### Catalyst Center SDK (`sdk-` prefix)

**Best for:** Production use, rapid development.  
The SDK handles authentication, token refresh, and JSON parsing automatically.

| Feature | Pure REST | SDK |
|---------|-----------|-----|
| Token management | Manual | **Automatic** |
| Token refresh | Manual | **Automatic** |
| Response access | `device["hostname"]` | `device.hostname` |
| Error handling | Custom | Built-in |
| Pagination | Manual | Still manual |

#### `sdk-demo.py`

Basic SDK usage: list switches and clean up Demo tags.

```bash
python sdk-demo.py
```

**Code highlights:**
```python
# One-time initialisation — no token code needed anywhere else
catalyst = api.CatalystCenterAPI(
    username=os.getenv("CATALYST_USERNAME"),
    password=os.getenv("CATALYST_PASSWORD"),
    base_url=os.getenv("CATALYST_BASE_URL"),
    version=os.getenv("CATALYST_VERSION"),
    verify=False
)

devices = catalyst.devices.get_device_list(family='Switches and Hubs')
all_tags = catalyst.tag.get_tag(sort_by='name', order='des')
```

#### `sdk-get-devices-paginated.py`

Same pagination and caching patterns as `api-get-devices-paginated.py` but using the SDK.

```bash
python sdk-get-devices-paginated.py
```

---

### Jupyter Notebooks (`nb-` prefix)

Both notebooks use the **Python (Catalyst Center)** kernel and walk through concepts step-by-step with explanations and exercises. Run cells with `Shift + Enter`.

```bash
# Start Jupyter (venv must be active)
jupyter notebook
```

#### `nb-api-switches-tutorial.ipynb` — REST approach

Step-by-step walkthrough of raw REST calls:
1. Imports & setup
2. Load credentials
3. Manual authentication flow
4. Device query with filters
5. Inspect device objects
6. Formatted display
7. **Pagination** — `offset`/`limit` examples
8. **Caching** — 5-minute TTL demo
9. Exercises

#### `nb-sdk-devices-tutorial.ipynb` — SDK approach

Step-by-step walkthrough using `catalystcentersdk`:
1. Why the SDK? (comparison table)
2. Imports
3. SDK initialisation — auto-auth explained
4. Basic device query — default behaviour
5. Inspect SDK device objects (`MyDict` attribute access)
6. **Pagination** — `offset`/`limit` with SDK
7. **Auto-pagination** — loop until last page
8. **Caching** — filter-aware TTL cache
9. Exercises + additional SDK categories

---

## 📁 Project Structure

```
catalyst-center-api-examples/
├── README.md                          # This file
├── QUICKSTART.md                      # 5-minute setup guide
├── .env                               # Your credentials (git-ignored)
├── .gitignore
├── requirements.txt
│
├── api-get-switches.py                # Pure REST: basic device list
├── api-get-devices-paginated.py       # Pure REST: pagination + caching
│
├── sdk-demo.py                        # SDK: basic usage + tag management
├── sdk-get-devices-paginated.py       # SDK: pagination + caching
│
├── nb-api-switches-tutorial.ipynb     # Notebook: REST tutorial
└── nb-sdk-devices-tutorial.ipynb      # Notebook: SDK tutorial
```

---

## 🔌 API Endpoints Used

### Authentication
- **POST** `/dna/system/api/v1/auth/token`
  - **Purpose:** Get authentication token
  - **Auth:** HTTP Basic (username/password)
  - **Returns:** JWT-style token (1-hour expiry)

### Network Devices
- **GET** `/dna/intent/api/v1/network-device`
  - **Purpose:** Query network devices
  - **Auth:** X-Auth-Token header
  - **Parameters:** 
    - `family` - Filter by device type (Switches and Hubs, Routers, etc.)
    - `hostname` - Filter by hostname
    - `managementIpAddress` - Filter by IP
    - `serialNumber` - Filter by serial number

### Tags (SDK example only)
- **GET** `/dna/intent/api/v1/tag`
  - **Purpose:** Retrieve all tags
  - **Parameters:** `sort_by`, `order`

- **DELETE** `/dna/intent/api/v1/tag/{id}`
  - **Purpose:** Delete a tag by ID

---

## 🛠️ Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'requests'`
**Solution:** Activate venv and install dependencies
```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Issue: `KeyError: 'Token'` or Authentication Failed
**Solution:** Check your credentials in `.env`
- Verify username and password
- Ensure BASE_URL is correct (include `https://`)
- Test login via Catalyst Center web UI first

### Issue: SSL Certificate Errors
**Solution:** Examples use `verify=False` to bypass SSL verification. For production:
```python
# Add your CA certificate
response = requests.get(url, headers=headers, verify='/path/to/ca-bundle.crt')
```

### Issue: `Connection refused` or timeout
**Solution:** 
- Check network connectivity to Catalyst Center
- Verify firewall rules
- Ensure Catalyst Center API is enabled
- Try pinging the BASE_URL

### Issue: Jupyter kernel not found
**Solution:** Re-register the kernel
```bash
source venv/bin/activate
python -m ipykernel install --user --name=catalyst-center --display-name="Python (Catalyst Center)"
```

### Issue: Empty device list
**Solution:**
- Verify devices exist in Catalyst Center
- Check if devices are in "Switches and Hubs" family
- Try removing the `family` parameter to see all devices
- Check your user permissions in Catalyst Center

---

## 🤝 Contributing

Contributions are welcome! Here are some ideas:

- 🐛 Bug fixes
- 📝 Documentation improvements
- ✨ New API examples
- 🧪 Additional Jupyter tutorials
- 🎨 Enhanced output formatting

### How to Contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is provided as-is for educational purposes. Modify and use as needed for your environment.

---

## 🔗 Additional Resources

- [Cisco Catalyst Center API Documentation](https://developer.cisco.com/docs/dna-center/)
- [Catalyst Center SDK on GitHub](https://github.com/cisco-en-programmability/catalystcentersdk)
- [Catalyst Center DevNet Sandbox](https://devnetsandbox.cisco.com/)
- [Python Requests Documentation](https://requests.readthedocs.io/)
- [Jupyter Notebook Documentation](https://jupyter-notebook.readthedocs.io/)

---

## 📞 Support

For issues related to:
- **This repository:** Open an issue on GitHub
- **Catalyst Center API:** Check Cisco DevNet forums
- **Catalyst Center SDK:** Check the SDK GitHub repository

---

**Happy Coding! 🚀**

*Last updated: July 2026*
