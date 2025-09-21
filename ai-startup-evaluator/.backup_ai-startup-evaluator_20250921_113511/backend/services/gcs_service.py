import os
import json
from typing import Optional, BinaryIO
from google.cloud import storage
from google.auth.exceptions import DefaultCredentialsError
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class GCSService:
    def __init__(self, bucket_name: Optional[str] = None):
        self.bucket_name = bucket_name or os.getenv("GCS_BUCKET_NAME", "startup-evaluator-storage")
        try:
            self.client = storage.Client()
            self.bucket = self.client.bucket(self.bucket_name)
        except DefaultCredentialsError:
            logger.warning("Google Cloud credentials not found. GCS functionality will be limited.")
            self.client = None
            self.bucket = None
    
    def upload_file(self, file_data: BinaryIO, destination_path: str, content_type: str = None) -> str:
        """Upload a file to GCS and return the GCS path"""
        if not self.bucket:
            raise Exception("GCS client not initialized")
        
        try:
            blob = self.bucket.blob(destination_path)
            if content_type:
                blob.content_type = content_type
            
            blob.upload_from_file(file_data)
            logger.info(f"File uploaded to GCS: {destination_path}")
            return f"gs://{self.bucket_name}/{destination_path}"
        except Exception as e:
            logger.error(f"Failed to upload file to GCS: {str(e)}")
            raise
    
    def upload_text(self, text_content: str, destination_path: str, content_type: str = "text/plain") -> str:
        """Upload text content to GCS"""
        if not self.bucket:
            raise Exception("GCS client not initialized")
        
        try:
            blob = self.bucket.blob(destination_path)
            blob.content_type = content_type
            blob.upload_from_string(text_content)
            logger.info(f"Text uploaded to GCS: {destination_path}")
            return f"gs://{self.bucket_name}/{destination_path}"
        except Exception as e:
            logger.error(f"Failed to upload text to GCS: {str(e)}")
            raise
    
    def upload_json(self, json_data: dict, destination_path: str) -> str:
        """Upload JSON data to GCS"""
        json_string = json.dumps(json_data, indent=2, default=str)
        return self.upload_text(json_string, destination_path, "application/json")
    
    def download_file(self, gcs_path: str) -> bytes:
        """Download a file from GCS"""
        if not self.bucket:
            raise Exception("GCS client not initialized")
        
        try:
            # Extract blob name from GCS path
            blob_name = gcs_path.replace(f"gs://{self.bucket_name}/", "")
            blob = self.bucket.blob(blob_name)
            return blob.download_as_bytes()
        except Exception as e:
            logger.error(f"Failed to download file from GCS: {str(e)}")
            raise
    
    def download_text(self, gcs_path: str) -> str:
        """Download text content from GCS"""
        if not self.bucket:
            raise Exception("GCS client not initialized")
        
        try:
            blob_name = gcs_path.replace(f"gs://{self.bucket_name}/", "")
            blob = self.bucket.blob(blob_name)
            return blob.download_as_text()
        except Exception as e:
            logger.error(f"Failed to download text from GCS: {str(e)}")
            raise
    
    def download_json(self, gcs_path: str) -> dict:
        """Download JSON data from GCS"""
        text_content = self.download_text(gcs_path)
        return json.loads(text_content)
    
    def generate_signed_url(self, gcs_path: str, expiration_hours: int = 24) -> str:
        """Generate a signed URL for accessing a GCS file"""
        if not self.bucket:
            raise Exception("GCS client not initialized")
        
        try:
            blob_name = gcs_path.replace(f"gs://{self.bucket_name}/", "")
            blob = self.bucket.blob(blob_name)
            
            expiration = datetime.utcnow() + timedelta(hours=expiration_hours)
            signed_url = blob.generate_signed_url(expiration=expiration)
            return signed_url
        except Exception as e:
            logger.error(f"Failed to generate signed URL: {str(e)}")
            raise
    
    def delete_file(self, gcs_path: str) -> bool:
        """Delete a file from GCS"""
        if not self.bucket:
            raise Exception("GCS client not initialized")
        
        try:
            blob_name = gcs_path.replace(f"gs://{self.bucket_name}/", "")
            blob = self.bucket.blob(blob_name)
            blob.delete()
            logger.info(f"File deleted from GCS: {gcs_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete file from GCS: {str(e)}")
            return False
    
    def file_exists(self, gcs_path: str) -> bool:
        """Check if a file exists in GCS"""
        if not self.bucket:
            return False
        
        try:
            blob_name = gcs_path.replace(f"gs://{self.bucket_name}/", "")
            blob = self.bucket.blob(blob_name)
            return blob.exists()
        except Exception as e:
            logger.error(f"Failed to check file existence: {str(e)}")
            return False
    
    def list_files(self, prefix: str = "") -> list:
        """List files in GCS with optional prefix filter"""
        if not self.bucket:
            return []
        
        try:
            blobs = self.bucket.list_blobs(prefix=prefix)
            return [f"gs://{self.bucket_name}/{blob.name}" for blob in blobs]
        except Exception as e:
            logger.error(f"Failed to list files: {str(e)}")
            return []
    
    def get_file_metadata(self, gcs_path: str) -> dict:
        """Get metadata for a GCS file"""
        if not self.bucket:
            return {}
        
        try:
            blob_name = gcs_path.replace(f"gs://{self.bucket_name}/", "")
            blob = self.bucket.blob(blob_name)
            blob.reload()
            
            return {
                "name": blob.name,
                "size": blob.size,
                "content_type": blob.content_type,
                "created": blob.time_created,
                "updated": blob.updated,
                "etag": blob.etag,
                "md5_hash": blob.md5_hash
            }
        except Exception as e:
            logger.error(f"Failed to get file metadata: {str(e)}")
            return {}

# Helper functions for common GCS operations
def get_startup_folder_path(startup_id: int) -> str:
    """Get the GCS folder path for a startup"""
    return f"startups/{startup_id}"

def get_extracted_data_path(startup_id: int) -> str:
    """Get the GCS path for extracted startup data"""
    return f"{get_startup_folder_path(startup_id)}/extracted/data.json"

def get_public_data_path(startup_id: int) -> str:
    """Get the GCS path for public data"""
    return f"{get_startup_folder_path(startup_id)}/public/data.json"

def get_memo_path(startup_id: int, format: str = "md") -> str:
    """Get the GCS path for investor memo"""
    return f"{get_startup_folder_path(startup_id)}/memos/memo.{format}"

def get_interview_transcript_path(startup_id: int, interview_id: int) -> str:
    """Get the GCS path for interview transcript"""
    return f"{get_startup_folder_path(startup_id)}/interviews/{interview_id}/transcript.json"

def get_interview_audio_path(startup_id: int, interview_id: int, file_extension: str = "mp3") -> str:
    """Get the GCS path for interview audio"""
    return f"{get_startup_folder_path(startup_id)}/interviews/{interview_id}/audio.{file_extension}"

def get_pitch_deck_path(startup_id: int, file_extension: str = "pdf") -> str:
    """Get the GCS path for pitch deck"""
    return f"{get_startup_folder_path(startup_id)}/documents/pitch_deck.{file_extension}"

# Initialize global GCS service instance
gcs_service = GCSService()
