from azure.storage.blob import BlobServiceClient
import os

conn_str = os.getenv('CONN_STR')
container_name = os.getenv('CONTAINER')
blob_service_client = BlobServiceClient.from_connection_string(conn_str)


class BlobService:

    def upload_file(file_path, file_name):
        container_client = blob_service_client.get_container_client(container=container_name)

        file_extension = file_name.split(".")[-1]
        
        if file_extension == "png":
            file_name = f"{file_name}.png"
        elif file_extension == "pptx":
            file_name = f"{file_name}.pptx"
        else:
            file_name = f"{file_name}.pdf"            



        with open(file=file_path, mode="rb") as data:
            blob_client = container_client.upload_blob(name=file_name, data=data, overwrite=True)
        
        return blob_client.url
