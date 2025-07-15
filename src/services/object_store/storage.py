import boto3
import os
import asyncio
from botocore.exceptions import NoCredentialsError, ClientError

from src.core.config.settings import settings
from src.core.logging.logger import logger

s3 = None

async def connect_to_storage():
    """
    Establishes connection to object store using the credentials provided in the environment variables
    """
    global s3
    s3 = boto3.client(
    service_name ="s3",
    endpoint_url = settings.R2_PUBLIC_ENDPOINT,
    aws_access_key_id = settings.R2_PUBLIC_ACCESS_KEY_ID,
    aws_secret_access_key = settings.R2_PUBLIC_SECRET_ACCESS_KEY,
    region_name="auto",
    )
    logger.info("Connected to object store")
    


async def close_storage_connection():
    """
    Terminated the connection to object store
    """
    s3.close()
    logger.info("Connection to object store terminated")


async def upload_file(file_path: str, folder_prefix: str= '', filename:str|None = None, bucket_name:str =settings.R2_PUBLIC_BUCKET):
    """
    Uploads the given file to an Amazon S3/Cloudflare R2 bucket.

    Args:
        file_path (str): The path to the local folder containing the files.
        folder_prefix (str): An optional prefix to add to the S3 object keys.
        filename (str): An optional filename taht overrides the default file name
        bucket_name (str): The name of the R2 bucket.
        
    """
    global s3

    logger.info(f"Starting upload of file to S3 bucket '{settings.R2_PUBLIC_BUCKET}'...")
    if not(filename):
        s3_object_key = os.path.join(folder_prefix, os.path.basename(file_path)).replace("\\", "/")
    else:
        s3_object_key = os.path.join(folder_prefix, filename).replace("\\", "/")

    try:
        
        await asyncio.to_thread(s3.upload_file, file_path, bucket_name, s3_object_key)
        logger.info(f"Successfully uploaded file to '{s3_object_key}'")

    except FileNotFoundError:
        logger.error(f"Error: The file '{file_path}' was not found.")
    except NoCredentialsError:
        logger.error("Error: Credentials not found. Please configure your credentials.")
    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code")
        if error_code == 'NoSuchBucket':
            logger.error(f"Error: S3 bucket '{bucket_name}' does not exist or you don't have access.")
        else:
            logger.error(f"Error uploading '{file_path}': {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred while uploading '{file_path}': {e}")

async def delete_file(s3_object_key:str,  bucket_name:str =settings.R2_PUBLIC_BUCKET):
    """
    Deletes the file with the provided object key from the object store.
    Args:
        s3_object_key (str): Object key for the file to be deleted
        bucket_name (str): Name of the bucket where the file is stored. If unspecified, uses the bucket name in the config file
    """

    logger.info(f"Trying to delete {s3_object_key} from '{settings.R2_PUBLIC_BUCKET}'...")

    try:
        await asyncio.to_thread(s3.delete_object, Bucket= bucket_name, Key= s3_object_key)
        logger.info(f"Successfully deleted object '{s3_object_key}' from bucket '{bucket_name}'")

    except NoCredentialsError:
        logger.error("Error: Credentials not found. Please configure your credentials.")
    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code")
        if error_code == 'NoSuchBucket':
            logger.error(f"Error: S3 bucket '{bucket_name}' does not exist or you don't have access.")
        elif error_code == 'NoSuchKey':
            logger.warning(f"Warning: Object '{s3_object_key}' does not exist in bucket '{bucket_name}' (may have already been deleted).")
        else:
            logger.error(f"Error deleting object '{s3_object_key}': {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred while deleting object '{s3_object_key}': {e}")






