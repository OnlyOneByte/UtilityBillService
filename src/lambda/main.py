from google_client import GoogleClient


# folders in google drive
GDRIVE_FOLDERS = {
    "ROOT_FOLDER" : "",

}

# parameters stored in SSM
SSM_KEYS = {
    "GOOGLE_CREDENTIALS" : 'UtilityBillService-GoogleDriveServiceAccount'
}



def handler(event, context):
    # logging
    print("Event:", event)
    print("Context:", context)

    googleClient = GoogleClient(SSM_KEYS["GOOGLE_CREDENTIALS"])

    
    return "Hiiii"