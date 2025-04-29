from azure.storage.blob import BlobServiceClient
from models.document import DocumentMetadata
import os

conn_str = os.getenv('CONN_STR')
container_name = os.getenv('CONTAINER')
blob_service_client = BlobServiceClient.from_connection_string(conn_str)
container_client = blob_service_client.get_container_client(container=container_name)

class BlobService:

    def upload_file(file_path, file_name):
        
        file_extension = file_name.split(".")[-1]
        
        if file_extension == "png":
            file_name = f"{file_name}"
        elif file_extension == "pptx":
            file_name = f"{file_name}"
        else:
            file_name = f"{file_name}.pdf"            

        with open(file=file_path, mode="rb") as data:
            blob_client = container_client.upload_blob(name=file_name, data=data, overwrite=True)
        
        return blob_client.url

    def get_blobs_list():
        container_client = blob_service_client.get_container_client(container=container_name)
        blob_list = container_client.list_blobs()
        
        metadata = []

        for blob in blob_list:
            blob_client = container_client.get_blob_client(blob=blob)
            metadata_item=(DocumentMetadata(name=blob.name, url=blob_client.url))

            metadata.append(metadata_item)  

        return metadata