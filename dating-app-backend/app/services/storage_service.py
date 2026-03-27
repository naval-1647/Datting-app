from typing import Optional, List
import logging
import os
import cloudinary
import cloudinary.uploader
from fastapi import UploadFile
import uuid

from app.config import settings

logger = logging.getLogger(__name__)


class StorageService:
    """Storage service for image uploads (Cloudinary or local)."""

    @staticmethod
    def initialize_cloudinary():
        """Initialize Cloudinary configuration."""
        if settings.storage_type == "cloudinary" and settings.cloudinary_cloud_name:
            cloudinary.config(
                cloud_name=settings.cloudinary_cloud_name,
                api_key=settings.cloudinary_api_key,
                api_secret=settings.cloudinary_api_secret
            )
            logger.info("Cloudinary initialized")

    @staticmethod
    async def upload_image(file: UploadFile, folder: str = "profiles") -> Optional[str]:
        """
        Upload an image and return the URL.
        
        Args:
            file: Uploaded file
            folder: Folder name in storage
            
        Returns:
            Image URL or None if upload failed
        """
        try:
            # Validate file type
            allowed_types = ["image/jpeg", "image/png", "image/webp"]
            if file.content_type not in allowed_types:
                logger.error(f"Invalid file type: {file.content_type}")
                return None

            # Read file content
            file_content = await file.read()

            if settings.storage_type == "cloudinary" and settings.cloudinary_cloud_name:
                # Upload to Cloudinary
                result = cloudinary.uploader.upload(
                    file_content,
                    folder=f"dating_app/{folder}",
                    public_id=str(uuid.uuid4()),
                    transformation=[
                        {"width": 800, "height": 800, "crop": "limit"},
                        {"quality": "auto"}
                    ]
                )
                logger.info(f"Image uploaded to Cloudinary: {result['public_id']}")
                return result["secure_url"]

            else:
                # Save locally
                return await StorageService._save_local(file_content, folder)

        except Exception as e:
            logger.error(f"Error uploading image: {e}")
            raise

    @staticmethod
    async def _save_local(file_content: bytes, folder: str) -> Optional[str]:
        """Save file to local storage."""
        try:
            # Create directory if it doesn't exist
            upload_dir = os.path.join(settings.local_storage_path, folder)
            os.makedirs(upload_dir, exist_ok=True)

            # Generate unique filename
            filename = f"{uuid.uuid4}.jpg"
            file_path = os.path.join(upload_dir, filename)

            # Save file
            with open(file_path, "wb") as f:
                f.write(file_content)

            # Return relative URL path
            url_path = f"/{folder}/{filename}"
            logger.info(f"Image saved locally: {url_path}")
            return url_path

        except Exception as e:
            logger.error(f"Error saving image locally: {e}")
            return None

    @staticmethod
    async def delete_image(image_url: str) -> bool:
        """Delete an image from storage."""
        try:
            if settings.storage_type == "cloudinary" and settings.cloudinary_cloud_name:
                # Delete from Cloudinary
                # Extract public_id from URL
                public_id = image_url.split("/")[-1].split(".")[0]
                result = cloudinary.uploader.destroy(f"dating_app/profiles/{public_id}")
                logger.info(f"Image deleted from Cloudinary: {public_id}")
                return result.get("result") == "ok"
            else:
                # Delete local file
                if image_url.startswith("/"):
                    file_path = os.path.join(settings.local_storage_path, image_url[1:])
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        logger.info(f"Image deleted locally: {file_path}")
                        return True
                return False

        except Exception as e:
            logger.error(f"Error deleting image: {e}")
            return False

    @staticmethod
    async def upload_multiple_images(files: List[UploadFile], folder: str = "profiles") -> List[str]:
        """Upload multiple images and return list of URLs."""
        urls = []
        for file in files:
            url = await StorageService.upload_image(file, folder)
            if url:
                urls.append(url)
        return urls
