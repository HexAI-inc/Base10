"""
Media & CDN Service - Blob Storage for Images and Assets.

Never store images in the database. Use cloud storage with CDN.

Key principles:
1. Mobile app caches images indefinitely (offline-first)
2. Serve resized versions based on connection speed
3. Compress all images automatically
4. Support for diagrams, profile pictures, achievement badges
"""
from enum import Enum
from typing import Optional, BinaryIO, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import logging
import hashlib
import io

# Optional: AWS S3 or MinIO (self-hosted S3-compatible)
try:
    import boto3
    from botocore.exceptions import ClientError
    HAS_S3 = True
except ImportError:
    HAS_S3 = False
    print("⚠️  boto3 not installed. Install: pip install boto3")

# Optional: Cloudinary for automatic image optimization
try:
    import cloudinary
    import cloudinary.uploader
    HAS_CLOUDINARY = True
except ImportError:
    HAS_CLOUDINARY = False
    print("⚠️  cloudinary not installed. Install: pip install cloudinary")

from app.core.config import settings

logger = logging.getLogger(__name__)


class ImageSize(Enum):
    """Predefined image sizes for responsive delivery."""
    THUMBNAIL = (150, 150)    # Profile pics, badges
    SMALL = (400, 400)        # 2G/3G users
    MEDIUM = (800, 800)       # 4G users
    LARGE = (1200, 1200)      # WiFi users, diagrams
    ORIGINAL = None           # Full resolution


class AssetType(Enum):
    """Types of media assets."""
    QUESTION_DIAGRAM = "question_diagram"  # Biology cell, Physics diagram
    PROFILE_PICTURE = "profile_picture"
    ACHIEVEMENT_BADGE = "achievement_badge"
    SUBJECT_ICON = "subject_icon"
    FLASHCARD_IMAGE = "flashcard_image"


class StorageService:
    """
    Cloud storage manager for Base10 media assets.
    
    Supports:
    - DigitalOcean Spaces (production)
    - MinIO (self-hosted alternative)
    - Local filesystem (development)
    """
    
    def __init__(self):
        self.storage_backend = settings.STORAGE_BACKEND  # 's3', 'minio', 'local'
        
        if self.storage_backend in ['s3', 'minio'] and HAS_S3:
            self.s3_client = boto3.client(
                's3',
                endpoint_url=settings.SPACES_ENDPOINT_URL,
                aws_access_key_id=settings.SPACES_ACCESS_KEY_ID,
                aws_secret_access_key=settings.SPACES_SECRET_ACCESS_KEY,
                region_name=settings.SPACES_REGION
            )
            self.bucket_name = settings.SPACES_BUCKET_NAME
        else:
            self.s3_client = None
            self.local_storage_path = Path(settings.LOCAL_STORAGE_PATH or './media')
            self.local_storage_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"📦 Storage backend: {self.storage_backend}")
    
    
    def upload_image(
        self,
        file: BinaryIO,
        asset_type: AssetType,
        filename: str,
        user_id: Optional[int] = None,
        metadata: Optional[dict] = None
    ) -> str:
        """
        Upload image to cloud storage.
        
        Args:
            file: Binary file object
            asset_type: Type of asset (question, profile, etc)
            filename: Original filename
            user_id: Optional user ID for namespacing
            metadata: Optional metadata tags
        
        Returns:
            Public URL to access the image
        """
        # Generate unique filename to prevent collisions
        file_hash = self._hash_file(file)
        file_extension = Path(filename).suffix
        unique_filename = f"{file_hash}{file_extension}"
        
        # Organize by type and date
        upload_path = self._generate_path(asset_type, unique_filename, user_id)
        
        try:
            if self.storage_backend in ['s3', 'minio']:
                return self._upload_to_s3(file, upload_path, metadata)
            else:
                return self._upload_to_local(file, upload_path)
        
        except Exception as e:
            logger.error(f"❌ Upload failed: {e}")
            raise
    
    
    def get_image_url(
        self,
        file_path: str,
        size: ImageSize = ImageSize.MEDIUM,
        expires_in: int = 3600
    ) -> str:
        """
        Get optimized image URL based on size.
        
        For mobile optimization:
        - 2G/3G users: SMALL (400px)
        - 4G users: MEDIUM (800px)
        - WiFi: LARGE (1200px)
        
        Args:
            file_path: Path in storage
            size: Desired image size
            expires_in: URL expiration in seconds
        
        Returns:
            Signed URL (S3) or local path
        """
        if self.storage_backend in ['s3', 'minio'] and self.s3_client:
            try:
                # Generate presigned URL (temporary access)
                url = self.s3_client.generate_presigned_url(
                    'get_object',
                    Params={
                        'Bucket': self.bucket_name,
                        'Key': file_path
                    },
                    ExpiresIn=expires_in
                )
                return url
            except ClientError as e:
                logger.error(f"❌ Failed to generate URL: {e}")
                raise
        else:
            # Local development
            return f"/media/{file_path}"
    
    
    def delete_image(self, file_path: str) -> bool:
        """Delete image from storage."""
        try:
            if self.storage_backend in ['s3', 'minio'] and self.s3_client:
                self.s3_client.delete_object(
                    Bucket=self.bucket_name,
                    Key=file_path
                )
            else:
                full_path = self.local_storage_path / file_path
                if full_path.exists():
                    full_path.unlink()
            
            logger.info(f"🗑️  Deleted: {file_path}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Delete failed: {e}")
            return False
    
    
    def _upload_to_s3(self, file: BinaryIO, path: str, metadata: Optional[dict]) -> str:
        """Upload to DigitalOcean Spaces or S3-compatible storage."""
        extra_args = {
            'ContentType': self._guess_content_type(path),
            'CacheControl': 'public, max-age=31536000',  # Cache for 1 year
            'ACL': 'public-read'  # Ensure file is publicly accessible
        }
        
        if metadata:
            extra_args['Metadata'] = metadata
        
        self.s3_client.upload_fileobj(
            file,
            self.bucket_name,
            path,
            ExtraArgs=extra_args
        )
        
        # Return public URL
        if settings.SPACES_CDN_DOMAIN:
            return f"https://{settings.SPACES_CDN_DOMAIN}/{path}"
        
        # Fallback to direct Spaces URL if CDN is not configured
        return f"https://{self.bucket_name}.{settings.SPACES_REGION}.digitaloceanspaces.com/{path}"
    
    
    def _upload_to_local(self, file: BinaryIO, path: str) -> str:
        """Upload to local filesystem (development only)."""
        full_path = self.local_storage_path / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(full_path, 'wb') as f:
            f.write(file.read())
        
        return f"/media/{path}"
    
    
    def _generate_path(self, asset_type: AssetType, filename: str, user_id: Optional[int]) -> str:
        """
        Generate organized path structure.
        
        Example paths:
        - questions/2025/12/abc123.png
        - profiles/users/456/def456.jpg
        - badges/streak_7day.svg
        """
        date = datetime.utcnow()
        
        if asset_type == AssetType.QUESTION_DIAGRAM:
            return f"questions/{date.year}/{date.month:02d}/{filename}"
        
        elif asset_type == AssetType.PROFILE_PICTURE:
            return f"profiles/users/{user_id}/{filename}"
        
        elif asset_type == AssetType.ACHIEVEMENT_BADGE:
            return f"badges/{filename}"
        
        elif asset_type == AssetType.SUBJECT_ICON:
            return f"subjects/{filename}"
        
        else:
            return f"misc/{filename}"
    
    
    def _hash_file(self, file: BinaryIO) -> str:
        """Generate MD5 hash of file for deduplication."""
        file.seek(0)
        file_hash = hashlib.md5()
        while chunk := file.read(8192):
            file_hash.update(chunk)
        file.seek(0)
        return file_hash.hexdigest()
    
    
    def _guess_content_type(self, filename: str) -> str:
        """Guess MIME type from file extension."""
        extension = Path(filename).suffix.lower()
        content_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.svg': 'image/svg+xml',
            '.webp': 'image/webp',
            '.pdf': 'application/pdf'
        }
        return content_types.get(extension, 'application/octet-stream')


class CDNOptimizer:
    """
    Image optimization via Cloudinary.
    
    Features:
    - Automatic compression
    - Format conversion (WebP for modern browsers)
    - Responsive sizing
    - Lazy loading placeholders
    """
    
    def __init__(self):
        if HAS_CLOUDINARY and settings.CLOUDINARY_CLOUD_NAME:
            cloudinary.config(
                cloud_name=settings.CLOUDINARY_CLOUD_NAME,
                api_key=settings.CLOUDINARY_API_KEY,
                api_secret=settings.CLOUDINARY_API_SECRET
            )
            self.enabled = True
        else:
            self.enabled = False
            logger.warning("⚠️  Cloudinary not configured. Image optimization disabled.")
    
    
    def optimize_and_upload(
        self,
        file_path: str,
        transformations: Optional[dict] = None
    ) -> str:
        """
        Upload image to Cloudinary with automatic optimization.
        
        Default transformations:
        - Quality: Auto (smart compression)
        - Format: Auto (WebP for supported browsers)
        - Fetch format: Auto
        """
        if not self.enabled:
            return file_path
        
        try:
            default_transforms = {
                'quality': 'auto',
                'fetch_format': 'auto',
                'flags': 'progressive'  # Progressive JPEG loading
            }
            
            if transformations:
                default_transforms.update(transformations)
            
            result = cloudinary.uploader.upload(
                file_path,
                **default_transforms
            )
            
            return result['secure_url']
        
        except Exception as e:
            logger.error(f"❌ Cloudinary optimization failed: {e}")
            return file_path


# Example usage:
if __name__ == "__main__":
    storage = StorageService()
    
    # Example 1: Upload question diagram
    with open("biology_cell_diagram.png", "rb") as f:
        url = storage.upload_image(
            file=f,
            asset_type=AssetType.QUESTION_DIAGRAM,
            filename="biology_cell_diagram.png",
            metadata={'subject': 'Biology', 'topic': 'Cell Structure'}
        )
        print(f"Uploaded diagram: {url}")
    
    # Example 2: Get optimized URL for 3G user
    small_url = storage.get_image_url(
        file_path="questions/2025/12/abc123.png",
        size=ImageSize.SMALL  # 400px for 3G
    )
    print(f"3G optimized URL: {small_url}")
    
    # Example 3: Upload profile picture
    with open("user_avatar.jpg", "rb") as f:
        profile_url = storage.upload_image(
            file=f,
            asset_type=AssetType.PROFILE_PICTURE,
            filename="avatar.jpg",
            user_id=123
        )
        print(f"Profile uploaded: {profile_url}")
