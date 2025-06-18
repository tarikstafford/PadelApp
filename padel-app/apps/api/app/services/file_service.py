import os
import shutil
from pathlib import Path
from fastapi import UploadFile, HTTPException
from fastapi.concurrency import run_in_threadpool
import secrets # For generating unique filenames
import cloudinary
import cloudinary.uploader
import uuid
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# 5MB
MAX_FILE_SIZE = 5 * 1024 * 1024
ALLOWED_MIME_TYPES = ["image/jpeg", "image/png", "image/gif"]

def validate_image_file(file: UploadFile):
    """
    Validates an uploaded image file.
    """
    if not file:
        raise HTTPException(status_code=400, detail="No file provided")
    
    if file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File size exceeds the limit of 5MB")

    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=400, detail="File type not allowed")

async def upload_file(file: UploadFile, folder: str) -> str:
    """
    Generic file upload to Cloudinary.
    """
    logger.info(f"Attempting to upload file to folder: {folder}")
    validate_image_file(file)
    
    try:
        public_id = f"{folder}/{uuid.uuid4()}"
        logger.info(f"Generated public_id: {public_id}")
        
        result = await run_in_threadpool(
            cloudinary.uploader.upload,
            file.file,
            public_id=public_id,
            overwrite=True,
            resource_type="image"
        )
        
        logger.info(f"Successfully uploaded image. Result: {result.get('secure_url')}")
        return result['secure_url']
    except Exception as e:
        logger.error(f"Failed to upload file to folder {folder}. Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")

async def save_profile_picture(file: UploadFile, user_id: int) -> str:
    """
    Upload a profile picture to Cloudinary and return the secure URL.
    """
    logger.info(f"Attempting to upload profile picture for user_id: {user_id}")
    validate_image_file(file)
    
    try:
        public_id = f"profile_pics/{user_id}/{uuid.uuid4()}"
        logger.info(f"Generated public_id: {public_id}")
        
        result = await run_in_threadpool(
            cloudinary.uploader.upload,
            file.file,
            public_id=public_id,
            overwrite=True,
            resource_type="image"
        )
        
        logger.info(f"Successfully uploaded image. Result: {result.get('secure_url')}")
        return result['secure_url']
    except Exception as e:
        logger.error(f"Failed to upload image for user_id: {user_id}. Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to upload image: {str(e)}")

async def save_club_picture(file: UploadFile, club_id: int) -> str:
    """
    Saves an uploaded club picture to Cloudinary and returns its relative URL path.
    """
    logger.info(f"Attempting to upload club picture for club_id: {club_id}")
    validate_image_file(file)
    
    try:
        public_id = f"club_pics/{club_id}/{uuid.uuid4()}"
        logger.info(f"Generated public_id: {public_id}")
        
        result = await run_in_threadpool(
            cloudinary.uploader.upload,
            file.file,
            public_id=public_id,
            overwrite=True,
            resource_type="image"
        )
        
        logger.info(f"Successfully uploaded image for club. Result: {result.get('secure_url')}")
        return result['secure_url']
    except Exception as e:
        logger.error(f"Failed to upload image for club_id: {club_id}. Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to upload image: {str(e)}") 