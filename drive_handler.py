"""
Handles all Google Drive operations:
- Reading source product images from the input folder
- Creating organized output folder structure
- Uploading generated ad images
"""

import io
import os
import json
import tempfile
from pathlib import Path
from typing import Optional

from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload, MediaIoBaseUpload

SCOPES = ["https://www.googleapis.com/auth/drive"]

# Supported image types to read from source folder
SUPPORTED_IMAGE_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/heic": ".heic",
}


def get_drive_service():
    """
    Authenticate and return a Google Drive service client.

    Priority order:
    1. GOOGLE_SERVICE_ACCOUNT_JSON env var (JSON string) — for automated/CI runs
    2. credentials.json file in current directory — for local dev with OAuth
    3. token.json (cached OAuth token)
    """
    # Option 1: Service account via environment variable (GitHub Actions / automated)
    sa_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
    if sa_json:
        info = json.loads(sa_json)
        creds = service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
        return build("drive", "v3", credentials=creds)

    # Option 2: Service account file
    if Path("service_account.json").exists():
        creds = service_account.Credentials.from_service_account_file(
            "service_account.json", scopes=SCOPES
        )
        return build("drive", "v3", credentials=creds)

    # Option 3: OAuth (local dev — runs browser flow once, caches token.json)
    creds = None
    if Path("token.json").exists():
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not Path("oauth_credentials.json").exists():
                raise FileNotFoundError(
                    "No auth method found. Provide one of:\n"
                    "  - GOOGLE_SERVICE_ACCOUNT_JSON env var\n"
                    "  - service_account.json file\n"
                    "  - oauth_credentials.json file (for local OAuth flow)\n"
                    "See README.md for setup instructions."
                )
            flow = InstalledAppFlow.from_client_secrets_file("oauth_credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as f:
            f.write(creds.to_json())

    return build("drive", "v3", credentials=creds)


def list_images_in_folder(service, folder_id: str) -> list[dict]:
    """List all image files in a Drive folder."""
    mime_query = " or ".join(
        [f"mimeType='{mime}'" for mime in SUPPORTED_IMAGE_TYPES.keys()]
    )
    query = f"'{folder_id}' in parents and ({mime_query}) and trashed=false"

    results = service.files().list(
        q=query,
        fields="files(id, name, mimeType)",
        pageSize=50
    ).execute()

    files = results.get("files", [])
    print(f"Found {len(files)} image(s) in source folder.")
    return files


def download_image(service, file_id: str, mime_type: str) -> bytes:
    """Download a file from Drive and return its bytes."""
    request = service.files().get_media(fileId=file_id)
    buffer = io.BytesIO()
    downloader = MediaIoBaseDownload(buffer, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    return buffer.getvalue()


def create_folder(service, name: str, parent_id: str) -> str:
    """Create a folder in Drive and return its ID."""
    metadata = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_id],
    }
    folder = service.files().create(body=metadata, fields="id").execute()
    folder_id = folder["id"]
    print(f"  Created Drive folder: {name} ({folder_id})")
    return folder_id


def upload_image_bytes(service, image_bytes: bytes, filename: str, folder_id: str, mime_type: str = "image/jpeg"):
    """Upload image bytes directly to a Drive folder (no temp file needed)."""
    metadata = {"name": filename, "parents": [folder_id]}
    media = MediaIoBaseUpload(io.BytesIO(image_bytes), mimetype=mime_type, resumable=False)
    file = service.files().create(body=metadata, media_body=media, fields="id").execute()
    return file["id"]


def build_output_folder_structure(service, root_folder_id: str, run_label: str, concepts: list[str]) -> dict:
    """
    Create the output folder structure for a run:

    root_folder/
    └── Ads_YYYY-MM-DD/
        ├── Concept_01_Independence/
        ├── Concept_02_CaregiverRelief/
        └── ...10 folders

    Returns dict mapping concept index to folder_id.
    """
    # Create today's run folder
    run_folder_id = create_folder(service, f"Ads_{run_label}", root_folder_id)

    concept_folder_ids = {}
    for i, concept_name in enumerate(concepts, 1):
        safe_name = concept_name[:35].replace(" ", "_").replace("/", "-")
        folder_name = f"Concept_{i:02d}_{safe_name}"
        folder_id = create_folder(service, folder_name, run_folder_id)
        concept_folder_ids[i] = folder_id

    return concept_folder_ids
