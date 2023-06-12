import tempfile
import boto3
import os
import sys
import json
from apiclient import discovery
from apiclient import errors
from apiclient.http import MediaFileUpload

# folders in google drive
GDRIVE_FOLDERS = {
    "ROOT_FOLDER" : "",

}

SSM_KEYS = {
    "GOOGLE_CREDENTIALS" : 'UtilityBillService-GoogleDriveServiceAccount'
}

def get_service_account_credentials(credentials_parameter):
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

def handler(event, context):
    # logging
    print("Event:", event)
    print("Context:", context)

    credentials = get_service_account_credentials(SSM_KEYS["GOOGLE_CREDENTIALS"])
    print(credentials)

    return "Hiiii"