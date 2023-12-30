import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

import requests

import paths

# If modifying these scopes, delete the file google_token.json.
SCOPES = [
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/photoslibrary",
    "https://www.googleapis.com/auth/photoslibrary.appendonly",
    "https://www.googleapis.com/auth/photoslibrary.edit.appcreateddata",
    "https://www.googleapis.com/auth/photoslibrary.readonly",
    "https://www.googleapis.com/auth/photoslibrary.readonly.appcreateddata",
    "https://www.googleapis.com/auth/photoslibrary.sharing",
    "https://www.googleapis.com/auth/photoslibrary.readonly.originals",
    "openid"
]

album_id = "ALEeNUdYqPYVSSFOQssXd2k9tGbI1h8mH5F2UCv1jAPgfbvGNkr6woI"

def cloud_upload(name: str):
    creds = None
    # The file google_token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("google_token.json"):
        creds = Credentials.from_authorized_user_file("google_token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("google_token.json", "w") as token:
            token.write(creds.to_json())

    bearer = "Bearer " + creds.token
    headers = {
        "Authorization": bearer,
        "content-type": "application/octet-stream",
        "X-Goog-Upload-Content-Type": "image/png",
        "X-Goog-Upload-Protocol": "raw"
    }
    file = open(paths.results_directory + name, "rb")
    upload_token = requests.post("https://photoslibrary.googleapis.com/v1/uploads", data=file.read(), headers=headers).text
    creation_body = {
        # "albumId": album_id,
        "newMediaItems": [
            {
                "description": name.removesuffix(".png"),
                "simpleMediaItem": {
                    "fileName": name,
                    "uploadToken": upload_token
                }
            }
        ]
    }
    headers = {
        "content-type": "application/json",
        "Authorization": bearer
    }
    requests.post("https://photoslibrary.googleapis.com/v1/mediaItems:batchCreate", json=creation_body, headers=headers)
