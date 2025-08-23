import time
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from googleapiclient.http import MediaFileUpload
import google.auth.transport.requests
import google.oauth2.credentials
import os
import pickle


# Scope for uploading videos to YouTube
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
TOKEN_PATH = "tools/token.pickle"  # Path to store/load tokens

import json




def uploadYoutube(
    video_file,
    title="Untitled Video",
    description="""ご視聴ありがとうございます！✨
ご意見や感想がありましたら、ぜひコメントで教えてください。いつもとても嬉しく、参考にさせていただいています😊""",
    tags = ["#ショートストーリー", "#shorts", "#物語", "#感動", "#面白い", "#日常", "#ストーリーテリング", "#感情", "#ショート動画", "#心に響く"],
    privacy_status="private",
    client_secrets_file="tools/client_secrets.json"
):
    

    creds = None
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, 'rb') as token:
            creds = pickle.load(token)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(google.auth.transport.requests.Request())
            except:
                if os.path.exists(TOKEN_PATH):
                    os.remove(TOKEN_PATH)
                # Restart the flow to generate new token
                flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                    client_secrets_file, SCOPES
                )
                creds = flow.run_local_server(port=0)
        else:
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                client_secrets_file, SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open(TOKEN_PATH, 'wb') as token:
            pickle.dump(creds, token)

    youtube = googleapiclient.discovery.build("youtube", "v3", credentials=creds)

    request_body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags if tags else [],
            "categoryId": "1",
        },
        "status": {
            "privacyStatus": privacy_status
        }
    }

    media = MediaFileUpload(video_file, chunksize=-1, resumable=True)
    request = youtube.videos().insert(
        part="snippet,status",
        body=request_body,
        media_body=media
    )

    response = None
    while response is None:
        try:
            print("Uploading file, please wait...")
            status, response = request.next_chunk()
            if response and "id" in response:
                video_id = response["id"]
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                return video_url
        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")
            print("Retrying in 5 seconds...")
            time.sleep(5)

    raise RuntimeError("An unexpected error occurred during the upload process.")



def uploadVideo(video_path, title, description="""ご視聴ありがとうございます！✨
ご意見や感想がありましたら、ぜひコメントで教えてください。いつもとても嬉しく、参考にさせていただいています😊""", tags= ["#ショートストーリー", "#物語", "#感動", "#日常", "#心に響く", "#面白い", "#ストーリーテリング", "#短編動画", "#共感", "#泣ける", "#笑える", "#感情", "#話題", "#TikTokJapan", "#tiktok短編"]
):



    #uploadTikTok(video_path, title, description=description, cookie = "/mnt/c/Users/Rioss/Downloads/www.tiktok.com_cookies.txt")

    link  = uploadYoutube(
    video_path,
    title,
    description, 
    tags)
    
    print("Video uploaded to TikTok and YouTube successfully.")
    return link

if __name__ == "__main__":
    uploadVideo(
        "media/finalUploads/アル・カポネ.mp4", "アル・カポネ"
    )