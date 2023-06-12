from apiclient import discovery
from apiclient import errors
from apiclient.http import MediaFileUpload
import boto3
import json


class GoogleClient:


    def __init__(self, credentials_json):
        self.credentials = self.get_service_account_credentials(credentials_json)

        print("Constructed GoogleClient")


    def get_service_account_credentials(self, credentials_parameter):
        """
        Load Google service account credentials for the specified service account

        Args:
            credentials_parameter: Name of parameter in Parameter Store containing the Google service account credentials json.
        
        Returns: Google service account credential object
        
        https://developers.google.com/identity/protocols/OAuth2ServiceAccount    
        https://google-auth.readthedocs.io/en/latest/_modules/google/oauth2/service_account.html    
        https://developers.google.com/identity/protocols/googlescopes#drivev3
        """
        from google.oauth2 import service_account
        import googleapiclient.discovery

        # get_parameter returns a dictionary object of the json string, so convert it
        # back to a string needed for getting the Google credentials object.
        #
        # Note that WithDecryption=True would be set if using a SecureString in Parameter Store
        ssm_client = boto3.client('ssm')
        creds_dict = ssm_client.get_parameter(Name=credentials_parameter, WithDecryption=False)['Parameter']['Value']
        creds_json = json.loads(creds_dict)

        scopes_list = [
            'https://www.googleapis.com/auth/drive',
            'https://www.googleapis.com/auth/drive.file'
        ]
        return service_account.Credentials.from_service_account_info(creds_json, scopes=scopes_list)


    def upload_file(self, service, file_name_with_path, file_name, description, folder_id, mime_type):  
        """
        Uploads a file to Google Drive to the designated folder in a shared drive.
        
        Args:
            service: Google Drive API service instance.
            file_name_with_path: Source location of the file just downloaded to the Python tmp folder.
            file_name: Name of file to be saved to Google, and also for its title in the file metadata.
            description: Description of the file to insert, for the file metadata.
            folder_id: Parent folder's ID for the Google Drive shared folder where the file will be uploaded.
            mime_type: MIME type of the file to insert.
        
        Returns: file info
        """
        media_body = MediaFileUpload(file_name_with_path, mimetype=mime_type)

        body = {
            'name': file_name,
            'title': file_name,
            'description': description,
            'mimeType': mime_type,
            'parents': [folder_id]
        }
        
        # note that supportsAllDrives=True is required or else the file upload will fail
        file = service.files().create(
            supportsAllDrives=True,
            body=body,
            media_body=media_body).execute()

        # TODO: Google Drive does not overwrite existing files with a create call,
        # it will add another file with the duplicate name, so add a condition to
        # to do either create or update based on file existence

        # this will work fine, you just have to remove the parents from the body
        # file = service.files().update(
        #     fileId='somefileid',
        #     supportsAllDrives=True,
        #     body=body,
        #     media_body=media_body).execute()

        print('{}, {}'.format(file_name, file['id']))
        
        return file