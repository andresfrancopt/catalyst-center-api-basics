# Quick Start Guide

## File Naming Convention

Files are prefixed to make the approach immediately clear:

| Prefix | Approach |
|--------|----------|
| `api-` | Pure Python — raw REST calls with `requests` |
| `sdk-` | Catalyst Center SDK (`catalystcentersdk`) |
| `nb-api-` | Jupyter notebook — raw REST |
| `nb-sdk-` | Jupyter notebook — SDK |

## First Time Setup (5 minutes)

```bash
# 1. Clone and enter directory
git clone <your-repo-url>
cd catalyst-center-api-examples

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure credentials
cp .env.example .env
nano .env  # Edit with your Catalyst Center credentials

# 5. Test it works
python api-get-switches.py
```

## Scripts

### 🔹 Pure Python — raw REST (`api-` prefix)
```bash
python api-get-switches.py             # Basic: list switches with uptime
python api-get-devices-paginated.py    # Pagination + caching examples
```
- Direct REST calls via `requests`
- No SDK dependency — educational and minimal

### 🔹 Catalyst Center SDK (`sdk-` prefix)
```bash
python sdk-demo.py                     # Basic SDK usage + tag management
python sdk-get-devices-paginated.py    # SDK pagination + caching examples
```
- Official Cisco SDK — automatic auth, attribute access on responses
- Best for production scripts

### 🔹 Jupyter Notebooks (`nb-` prefix)
```bash
jupyter notebook nb-api-switches-tutorial.ipynb   # REST tutorial (step-by-step)
jupyter notebook nb-sdk-devices-tutorial.ipynb    # SDK tutorial (step-by-step)
```
- Interactive, with explanations and exercises

## Your .env File Should Look Like:

```env
CATALYST_USERNAME=admin
CATALYST_PASSWORD=YourPassword123
CATALYST_BASE_URL=https://10.10.20.85
CATALYST_VERSION=2.3.7.9
```

## Common Commands

```bash
# Activate virtual environment
source venv/bin/activate

# Install/Update dependencies
pip install -r requirements.txt

# Run a script
python api-get-switches.py
python sdk-demo.py

# Start Jupyter
jupyter notebook

# Deactivate virtual environment
deactivate
```

## Troubleshooting Quick Fixes

**Problem:** Module not found
```bash
source venv/bin/activate
pip install -r requirements.txt
```

**Problem:** Authentication failed
- Check credentials in `.env`
- Verify network access to Catalyst Center

**Problem:** No devices returned
- Try without `family` filter
- Check permissions in Catalyst Center

**Problem:** Jupyter kernel not found
```bash
source venv/bin/activate
python -m ipykernel install --user --name=catalyst-center --display-name="Python (Catalyst Center)"
```

## Next Steps

1. ✅ Run `api-get-switches.py` to verify setup
2. 📚 Open `README.md` for detailed documentation
3. 🎓 Try `nb-api-switches-tutorial.ipynb` for a REST walkthrough
4. 🎓 Try `nb-sdk-devices-tutorial.ipynb` for an SDK walkthrough
5. 🚀 Build your own scripts using these examples
