"""
EzLift Automated Ad Creator
============================
Daily pipeline that:
1. Reads product images from a Google Drive source folder
2. Uses Gemini to generate 10 ad concepts × 3 formats (square/vertical/horizontal)
3. Uses Gemini Imagen to generate the actual ad images
4. Uploads results to organized subfolders in Google Drive

Run manually:   python main.py
Run daily:      GitHub Actions cron (see .github/workflows/daily_ads.yml)
"""

import os
import sys
import datetime
import time

from google import genai
from dotenv import load_dotenv

from drive_handler import (
    get_drive_service,
    list_images_in_folder,
    download_image,
    build_output_folder_structure,
    upload_image_bytes,
)
from image_generator import (
    analyze_product_image,
    generate_ad_concepts,
    generate_ad_image,
    parse_concepts,
)

load_dotenv()

# ─── CONFIG ────────────────────────────────────────────────────────────────────

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
DRIVE_SOURCE_FOLDER_ID = os.environ.get(
    "DRIVE_SOURCE_FOLDER_ID", "1nLcb76jDDuMYZBGk-8fpLtT9MhvK4M0c"
)
DRIVE_OUTPUT_FOLDER_ID = os.environ.get(
    "DRIVE_OUTPUT_FOLDER_ID", DRIVE_SOURCE_FOLDER_ID  # defaults to same folder
)

FORMAT_LABELS = {
    "square": "1080x1080",
    "vertical": "1080x1350",
    "horizontal": "1200x628",
}

# ─── MAIN PIPELINE ─────────────────────────────────────────────────────────────

def run():
    if not GEMINI_API_KEY:
        print("ERROR: GEMINI_API_KEY not set.")
        sys.exit(1)

    client = genai.Client(api_key=GEMINI_API_KEY)

    run_date = datetime.date.today().strftime("%Y-%m-%d")
    print(f"\n{'='*60}")
    print(f"  EzLift Ad Creator — {run_date}")
    print(f"{'='*60}\n")

    # ── Step 1: Connect to Drive ──────────────────────────────────────────────
    print("Connecting to Google Drive...")
    drive = get_drive_service()

    # ── Step 2: Get source images ─────────────────────────────────────────────
    print(f"Reading source images from folder: {DRIVE_SOURCE_FOLDER_ID}")
    image_files = list_images_in_folder(drive, DRIVE_SOURCE_FOLDER_ID)

    if not image_files:
        print("No images found in source folder. Upload product images and retry.")
        sys.exit(1)

    # Process the first image found (or loop all — controlled below)
    source_file = image_files[0]
    print(f"Using: {source_file['name']} ({source_file['id']})\n")

    image_bytes = download_image(drive, source_file["id"], source_file["mimeType"])
    mime_type = source_file["mimeType"]

    # ── Step 3: Analyze product image ─────────────────────────────────────────
    print("Analyzing product image with Gemini Vision...")
    product_description = analyze_product_image(client, image_bytes, mime_type)
    print(f"Product description:\n{product_description}\n")

    # ── Step 4: Generate 10 concept prompts ───────────────────────────────────
    print("Generating 10 ad concepts with 3 formats each...")
    raw_concepts = generate_ad_concepts(client, image_bytes, product_description, mime_type)

    # Save raw output for debugging
    with open(f"concepts_{run_date}.txt", "w") as f:
        f.write(raw_concepts)
    print("Raw concepts saved to concepts_{run_date}.txt\n")

    concepts = parse_concepts(raw_concepts)
    if not concepts:
        print("ERROR: Could not parse any concepts from Gemini output.")
        print("Check concepts_{run_date}.txt for the raw output.")
        sys.exit(1)

    # ── Step 5: Build Drive output folders ────────────────────────────────────
    concept_names = [c["name"] for c in concepts.values()]
    print(f"Creating Drive folder structure for {len(concepts)} concepts...")
    concept_folder_ids = build_output_folder_structure(
        drive, DRIVE_OUTPUT_FOLDER_ID, run_date, concept_names
    )
    print()

    # ── Step 6: Generate & upload all ads ────────────────────────────────────
    total_ads = len(concepts) * len(FORMAT_LABELS)
    generated = 0
    failed = 0

    for concept_num, concept in concepts.items():
        folder_id = concept_folder_ids.get(concept_num)
        if not folder_id:
            continue

        print(f"\nConcept {concept_num:02d}: {concept['name']} — {concept['angle']}")

        for fmt_key, size_label in FORMAT_LABELS.items():
            prompt = concept["formats"].get(fmt_key)
            if not prompt:
                print(f"  [{fmt_key}] No prompt found — skipping")
                continue

            filename = f"concept_{concept_num:02d}_{fmt_key}_{size_label}.png"
            print(f"  Generating {fmt_key} ({size_label})...", end=" ", flush=True)

            img_bytes = generate_ad_image(client, prompt, image_bytes, mime_type)

            if img_bytes:
                upload_image_bytes(drive, img_bytes, filename, folder_id, mime_type="image/png")
                print(f"✓ uploaded ({len(img_bytes)//1024}KB)")
                generated += 1
            else:
                print("✗ failed")
                failed += 1

            # Small delay to respect API rate limits
            time.sleep(1.5)

    # ── Step 7: Summary ───────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"  Run complete: {run_date}")
    print(f"  Generated: {generated}/{total_ads} ads")
    if failed:
        print(f"  Failed:    {failed} ads")
    print(f"  Output folder: https://drive.google.com/drive/folders/{DRIVE_OUTPUT_FOLDER_ID}")
    print(f"{'='*60}\n")

    if failed > 0:
        sys.exit(1)  # Signal partial failure to CI


if __name__ == "__main__":
    run()
