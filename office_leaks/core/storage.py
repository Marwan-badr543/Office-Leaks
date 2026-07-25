import uuid
import logging
import imghdr
import boto3
from botocore.exceptions import ClientError
from django.conf import settings
from core.exceptions import ValidationError, ExternalServiceError

logger = logging.getLogger(__name__)

# Allowed MIME types mapped to their expected extensions.
# We validate against both the upload's content_type AND the file's actual
# binary signature (magic bytes via imghdr) to prevent renamed executables.
ALLOWED_IMAGE_TYPES = {
    'image/jpeg': ['.jpg', '.jpeg'],
    'image/png': ['.png'],
    'image/webp': ['.webp'],
    'image/gif': ['.gif'],
}


class R2StorageService:
    """
    Centralized Cloudflare R2 storage client.

    Uses boto3's S3-compatible API since R2 implements the S3 protocol.
    Initialized lazily — the client is created on first use, not at import time,
    so missing env vars won't crash the app during collectstatic / migrations.
    """

    _client = None

    @classmethod
    def _get_client(cls):
        """
        Lazy-initialize the boto3 S3 client.

        Why lazy? During `manage.py migrate` or `collectstatic`, the R2 env vars
        may not be set. Eagerly creating the client at module level would crash
        those management commands. By deferring to first actual use, we avoid that.
        """
        if cls._client is None:
            cls._client = boto3.client(
                's3',
                endpoint_url=settings.R2_ENDPOINT,
                aws_access_key_id=settings.R2_ACCESS_KEY_ID,
                aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
                # R2 doesn't use regions, but boto3 requires one.
                # 'auto' tells R2 to route automatically.
                region_name='auto',
            )
        return cls._client

    @classmethod
    def _validate_image(cls, file):
        """
        Two-layer validation:

        1. Content-Type check — verifies the MIME type sent by the client.
           This is a first gate but can be spoofed (client controls this header).

        2. Magic bytes check — reads the first bytes of the actual file content
           using Python's `imghdr.what()`. This inspects binary signatures
           (e.g., JPEG starts with FF D8 FF, PNG with 89 50 4E 47) to confirm
           the file is genuinely an image regardless of what the client claims.

        3. Size check — enforces MAX_IMAGE_UPLOAD_SIZE from settings.
           Django's UploadedFile exposes `.size` which is determined during
           the multipart parsing phase, so this is reliable.
        """
        # --- Content-Type validation ---
        content_type = file.content_type
        if content_type not in ALLOWED_IMAGE_TYPES:
            allowed = ', '.join(ALLOWED_IMAGE_TYPES.keys())
            raise ValidationError(
                f"Invalid image type '{content_type}'. Allowed types: {allowed}"
            )

        # --- Size validation ---
        if file.size > settings.MAX_IMAGE_UPLOAD_SIZE:
            max_mb = settings.MAX_IMAGE_UPLOAD_SIZE / (1024 * 1024)
            raise ValidationError(
                f"Image size {file.size} bytes exceeds the maximum allowed size of {max_mb:.0f} MB."
            )

        # --- Magic bytes validation ---
        # imghdr.what() reads the file's binary header to detect the real format.
        # It returns a string like 'jpeg', 'png', 'gif', 'webp' or None.
        # We must seek(0) first in case the file pointer was advanced, and
        # seek(0) again after so downstream code (boto3 upload) reads from the start.
        file.seek(0)
        detected_type = imghdr.what(file)
        file.seek(0)

        if detected_type is None:
            raise ValidationError(
                "File content does not match any known image format. "
                "The file may be corrupted or not a real image."
            )

        # Map imghdr's return values to MIME types for cross-validation.
        # imghdr returns 'jpeg' not 'jpg', and 'png', 'gif', 'webp' as-is.
        detected_mime = f"image/{detected_type}"
        if detected_mime not in ALLOWED_IMAGE_TYPES:
            raise ValidationError(
                f"Detected image format '{detected_type}' is not in the allowed types."
            )

    @classmethod
    def upload_image(cls, file):
        """
        Validate, generate UUID filename, and upload to R2.

        Returns the UUID filename (e.g., 'a1b2c3d4-...-.jpg') which is
        what gets stored in the database. The full public URL is constructed
        on read via get_image_url().

        Why UUID? Prevents filename collisions, eliminates path traversal risks
        from user-supplied filenames, and keeps stored keys opaque.
        """
        cls._validate_image(file)

        # Extract extension from the original filename.
        # os.path.splitext is not used here to avoid importing os;
        # we split on the last '.' manually.
        original_name = file.name
        extension = ''
        if '.' in original_name:
            extension = '.' + original_name.rsplit('.', 1)[1].lower()

        # Generate a UUID4 filename. UUID4 is random (122 bits of entropy),
        # making collisions effectively impossible without coordination.
        filename = f"{uuid.uuid4()}{extension}"

        try:
            client = cls._get_client()
            client.put_object(
                Bucket=settings.R2_BUCKET_NAME,
                Key=filename,
                Body=file,
                ContentType=file.content_type,
            )
            logger.info(f"Uploaded image to R2: {filename}")
            return filename
        except ClientError as e:
            logger.error(f"R2 upload failed: {e}")
            raise ExternalServiceError("Failed to upload image to storage.")

    @classmethod
    def delete_image(cls, filename):
        """
        Delete an image from R2 by its key (UUID filename).

        Called when a user replaces or removes their profile image / company logo.
        This prevents orphaned files from accumulating in the bucket.

        Note: R2's DeleteObject is idempotent — deleting a non-existent key
        does NOT raise an error, so no existence check is needed.
        """
        if not filename:
            return

        try:
            client = cls._get_client()
            client.delete_object(
                Bucket=settings.R2_BUCKET_NAME,
                Key=filename,
            )
            logger.info(f"Deleted image from R2: {filename}")
        except ClientError as e:
            # Log but don't crash — the primary operation (DB update) already succeeded.
            # The orphaned file is a minor storage cost vs. failing the user's request.
            logger.error(f"R2 delete failed for {filename}: {e}")

    @classmethod
    def get_image_url(cls, filename):
        """
        Construct the public URL for an image stored in R2.

        Uses the R2_BASE_URL (public bucket URL) + filename.
        This assumes the bucket has public access enabled via R2's
        "Allow Public Access" setting (which your BASE_URL confirms).
        """
        if not filename:
            return None

        if filename.startswith(('http://', 'https://')):
            return filename

        base_url = settings.R2_BASE_URL.rstrip('/')
        return f"{base_url}/{filename}"
