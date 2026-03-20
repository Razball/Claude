# EzLift Automated Ad Creator

Generates 10 premium ad concepts × 3 formats (square/vertical/horizontal) = **30 ads per day**, automatically uploaded to Google Drive.

## What it does

1. Reads product images from your Google Drive folder
2. Sends each image to **Gemini Vision** to analyze the product
3. Uses **Gemini** to generate 10 ad concept prompts (your full style/copy requirements built in)
4. Uses **Gemini Imagen** to generate the actual ad images with your product photo composited in
5. Uploads all 30 ads to organized subfolders in Google Drive
6. Runs daily via GitHub Actions — zero human interaction

## Output structure in Drive

```
Your Drive Folder/
└── Ads_2026-03-20/
    ├── Concept_01_EmotionalIndependence/
    │   ├── concept_01_square_1080x1080.png
    │   ├── concept_01_vertical_1080x1350.png
    │   └── concept_01_horizontal_1200x628.png
    ├── Concept_02_CaregiverRelief/
    │   └── ... (3 ads)
    └── ... (10 folders total, 3 ads each)
```

---

## One-time Setup

### Step 1: Get your Gemini API key
1. Go to [aistudio.google.com](https://aistudio.google.com/)
2. Click **Get API key** → Create API key
3. Copy the key

### Step 2: Set up Google Drive access (Service Account)

This allows the script to read/write your Drive folder without human login.

1. Go to [console.cloud.google.com](https://console.cloud.google.com/)
2. Create a new project (or use existing)
3. Enable **Google Drive API**: APIs & Services → Enable APIs → search "Google Drive API"
4. Create a Service Account:
   - IAM & Admin → Service Accounts → Create Service Account
   - Name it anything (e.g., "ad-creator")
   - Skip role assignment, click Done
5. Click the service account → Keys tab → Add Key → JSON → Download
6. Open the JSON file — copy the `client_email` value (looks like `xxx@project.iam.gserviceaccount.com`)
7. **Share your Drive folder** with that email address (Editor permission)

### Step 3: Add product images to Drive
Upload your product photos to your Drive folder:
`https://drive.google.com/drive/folders/1nLcb76jDDuMYZBGk-8fpLtT9MhvK4M0c`

### Step 4: Set up GitHub Secrets

In your GitHub repo → Settings → Secrets and variables → Actions → New repository secret:

| Secret name | Value |
|---|---|
| `GEMINI_API_KEY` | Your Gemini API key |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | The entire contents of the service account JSON file |
| `DRIVE_SOURCE_FOLDER_ID` | `1nLcb76jDDuMYZBGk-8fpLtT9MhvK4M0c` |
| `DRIVE_OUTPUT_FOLDER_ID` | `1nLcb76jDDuMYZBGk-8fpLtT9MhvK4M0c` (same folder, or a different one) |

### Step 5: Push to GitHub and test

```bash
git push
```

Then go to Actions tab → Daily Ad Creator → Run workflow (to test manually before waiting for the daily schedule).

---

## Running Locally

```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API key and folder IDs
# Place service_account.json in this directory
python main.py
```

---

## Adjusting the daily schedule

Edit `.github/workflows/daily_ads.yml` — change the cron line:
- `"0 13 * * *"` = 8am EST
- `"0 16 * * *"` = 8am PST
- `"0 8 * * *"` = 8am UTC

---

## Ad directions built in

The 10 concept angles (from your requirements) are embedded in `prompt_generator.py`:
1. Emotional Independence
2. Caregiver Relief
3. Feature Spotlight
4. Social Proof / Testimonial
5. Problem → Solution
6. Trust / Risk Reversal
7. Urgency / Offer
8. Before / After
9. Editorial / Magazine
10. Aspirational Lifestyle

Each concept generates 3 layouts: **Square 1080×1080**, **Vertical 1080×1350**, **Horizontal 1200×628**
