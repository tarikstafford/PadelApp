import os
import shutil
from pathlib import Path
from fastapi import UploadFile
import secrets # For generating unique filenames

# Define the base directory for uploads within the API app structure
# This path is relative to the root of the `api` app (padel-app/apps/api)
# FastAPI needs to be configured to serve this directory statically.
UPLOAD_DIR_NAME = "static/profile_pics"
CLUB_UPLOAD_DIR_NAME = "static/club_pics"
UPLOAD_DIR = Path(UPLOAD_DIR_NAME)
CLUB_UPLOAD_DIR = Path(CLUB_UPLOAD_DIR_NAME)

# The URL path prefix the frontend would use to access these files
# e.g., if FastAPI serves /static from ./static, then URL is /static/profile_pics/...
STATIC_URL_PREFIX = f"/{UPLOAD_DIR_NAME}"
CLUB_STATIC_URL_PREFIX = f"/{CLUB_UPLOAD_DIR_NAME}"

def save_profile_picture(file: UploadFile, user_id: int) -> str:
    """
    Saves an uploaded profile picture to a local directory and returns its relative URL path.
    The actual directory `padel-app/apps/api/static/profile_pics` will be created.
    """
    # Base path for the `api` app directory
    api_app_base_path = Path(__file__).resolve().parent.parent # up two levels from services/file_service.py to app/
    
    # Absolute path for the upload directory
    absolute_upload_dir = api_app_base_path / UPLOAD_DIR
    absolute_upload_dir.mkdir(parents=True, exist_ok=True)

    original_filename = file.filename if file.filename else "unknown_file"
    # Basic filename sanitization (replace non-alphanumeric with underscore)
    # A more robust solution might involve a library like python-slugify or Werkzeug's secure_filename
    safe_original_filename = "".join(c if c.isalnum() or c in '.' else '_' for c in original_filename)
    unique_suffix = secrets.token_hex(4)
    filename = f"user_{user_id}_{unique_suffix}_{safe_original_filename}"
    
    file_location = absolute_upload_dir / filename
    
    try:
        with open(file_location, "wb+") as file_object:
            shutil.copyfileobj(file.file, file_object)
    except Exception as e:
        # In a real app, log this error properly
        print(f"Error saving file {filename} to {file_location}: {e}")
        raise IOError(f"Could not save profile picture: {filename}")
    finally:
        file.file.close()

    # Return a relative URL path for accessing the file
    return f"{STATIC_URL_PREFIX}/{filename}" 

def save_club_picture(file: UploadFile, club_id: int) -> str:
    """
    Saves an uploaded club picture to a local directory and returns its relative URL path.
    """
    api_app_base_path = Path(__file__).resolve().parent.parent
    absolute_upload_dir = api_app_base_path / CLUB_UPLOAD_DIR
    absolute_upload_dir.mkdir(parents=True, exist_ok=True)

    original_filename = file.filename if file.filename else "unknown_file"
    safe_original_filename = "".join(c if c.isalnum() or c in '.' else '_' for c in original_filename)
    unique_suffix = secrets.token_hex(4)
    filename = f"club_{club_id}_{unique_suffix}_{safe_original_filename}"
    
    file_location = absolute_upload_dir / filename
    
    try:
        with open(file_location, "wb+") as file_object:
            shutil.copyfileobj(file.file, file_object)
    except Exception as e:
        print(f"Error saving file {filename} to {file_location}: {e}")
        raise IOError(f"Could not save club picture: {filename}")
    finally:
        file.file.close()

    return f"{CLUB_STATIC_URL_PREFIX}/{filename}" 