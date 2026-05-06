# Fake News Detector (CSV First • Web Second)

Streamlit app that verifies a news claim using:
1) **Local CSV knowledge base** (True/Fake), and if not found
2) **Real web search** via **SerpApi (Google News engine)**, scoring results from credible outlets.

---

## Features

- **Fast local matching** against `data/True.csv` and `data/Fake.csv`
- **Automatic fallback to web search** when the claim is not found in CSV
- **Credibility-based scoring** (based on a list of known credible domains)
- **Admin panel** to upload CSV files and configure SerpApi

---

## Project Structure

- `app.py` — Streamlit UI + orchestrates verification (CSV first, web second)
- `utils/` — preprocessing + optional web search helpers
- `graph/` — graph building + algorithms (BFS/DFS/union-find). (Currently not wired into `app.py`.)
- `model/` — training script for an ML model (Logistic Regression + TF-IDF). (Currently not wired into `app.py`.)
- `data/True.csv`, `data/Fake.csv` — local datasets
- `serpapi_key.txt` — **local** SerpApi API key file (do not commit)
- `requirement.txt` — Python dependencies

---

## Screenshots / UI Flow (What to do)

### User Panel
1. Paste a claim or news text
2. App checks **CSV database first**
3. If not found, it performs **web search** using SerpApi
4. Displays verdict: **TRUE / FAKE / UNCLEAR** and a confidence meter

### Admin Panel
1. Upload `True.csv` and/or `Fake.csv`
2. Click **TRAIN / LOAD DATA** (loads the CSVs into memory)
3. Configure SerpApi by adding an API key to `serpapi_key.txt`

---

## Setup

### 1) Install dependencies

```bash
pip install -r requirement.txt
```

### 2) Provide SerpApi key (required for real web search)

Create a file named `serpapi_key.txt` in the project root and paste your key:

```text
YOUR_SERPAPI_KEY_HERE
```

> If the key is missing, the app warns and web search may fall back/return limited results.

### 3) Run the app

```bash
streamlit run app.py
```

---

## Admin Login

- Username: `admin`
- Password: `admin123`

(These are hardcoded in the current version of `app.py`.)

---

## How Verification Works

### Step 1 — CSV match (local)

- Loads `data/True.csv` and `data/Fake.csv` (if present)
- Compares the input text against dataset rows using a simple token-set similarity:
  - similarity = `|intersection| / |union| * 100`
- If best similarity is above a threshold, verdict is returned from the matched dataset.

### Step 2 — Web search + credibility scoring

- Uses SerpApi Google News endpoint
- Collects top results and scores them using a curated credible source list
- Produces:
  - verdict: **TRUE / UNCLEAR / FAKE**
  - confidence: 0–100 based on credible vs non-credible sources

---

## Notes / Limitations

- The **CSV matching** logic uses a lightweight similarity approach (token set overlap). For better accuracy, an ML model/graph approach can be integrated.
- SerpApi key handling:
  - stored in `serpapi_key.txt`
  - should be excluded from GitHub

---

## Deployment

This app can be deployed anywhere that supports Streamlit (local machine, Streamlit Community Cloud, etc.).

For deployments, prefer environment variables / secrets management instead of committing `serpapi_key.txt`.

---
Note:
paste your serp_api key or any web api key here:
utils/_pycache_/real_web_search.py:
def init_web_search():
    """Initialize web search with API key"""
    # You can set your key here directly (temporary)
    # Get free key from https://serpapi.com/
    YOUR_API_KEY = "*******************************************************"  # <-- PASTE YOUR API KEY HERE


---

## License

Custom License

Copyright (c) 2026 ORCHEYMAN MAZUMDER/mz570

TERMS AND CONDITIONS:

1. FREE USE
   This software is provided free of charge for any person to use, modify, and distribute.

2. SUBLICENSE REQUIREMENT
   Any person wishing to create a sublicense or grant rights to third parties must obtain explicit written permission from the copyright holder (ORCHEYMAN MAZUMDER/mz570) before doing so.

3. COMMERCIAL USE AND REVENUE SHARING
   If any person or entity generates revenue, profit, or financial gain through the use, distribution, modification, or commercialization of this software, they must share 20% of such earnings with the copyright holder (ORCHEYMAN MAZUMDER/mz570).

4. REVENUE REPORTING
   Users generating revenue from this software agree to provide transparent reporting of earnings to the copyright holder upon request.

5. PERMISSION AND CONTACT
   All requests for sublicensing permissions and revenue sharing inquiries should be directed to the copyright holder at the official project repository.

6. WARRANTY DISCLAIMER
   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

7. ENFORCEMENT
   The copyright holder reserves the right to enforce these terms and seek legal remedies for violations of this license agreement.

