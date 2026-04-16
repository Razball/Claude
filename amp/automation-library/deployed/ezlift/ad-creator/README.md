# EzLift — Automated Ad Creator

Daily ad generation pipeline. Already live in this repo (see `../../../../main.py`, `prompt_generator.py`, `image_generator.py`, `drive_handler.py`).

## What it does
Generates 10 ad concepts × 3 formats (square, vertical, horizontal) = 30 creatives per day. Uploads to Google Drive in organized folders. Zero-touch via GitHub Actions daily cron.

## Status
Live (Phase 3 Automation Library — first deployed agent).

## Template candidacy
Yes. Generalizes as: "daily creative generation against N concept angles from a single product-image source." Good fit for any DTC brand with visual inventory.

## Files
- Pipeline: `main.py`, `prompt_generator.py`, `image_generator.py`, `drive_handler.py`
- Schedule: `.github/workflows/daily_ads.yml`

## Abstraction TODO
Extract the 10 concept angles into client-configurable input. Today they're hard-coded to EzLift's caregiver audience.
