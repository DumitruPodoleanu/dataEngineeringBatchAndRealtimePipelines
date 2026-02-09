from azure.storage.blob import BlobServiceClient, ContentSettings
import os

def upload_to_blob_storage(file_path, container_name, blob_name=None):

    # Hardcoded credentials (for demonstration/assignment purposes ONLY)
    connect_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

    try:
        # Create the BlobServiceClient object
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)

        # Create the container if it doesn't exist
        container_client = blob_service_client.get_container_client(container_name)
        if not container_client.exists():
            container_client.create_container()

        # Upload the file
        blob_name = blob_name or os.path.basename(file_path)
        blob_client = container_client.get_blob_client(blob_name)

        with open(file_path, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)

        return True, f"Uploaded to Azure Blob Storage: container='{container_name}', blob='{blob_name}'"

    except Exception as e:
        return False, f"Azure upload failed: {str(e)}"
