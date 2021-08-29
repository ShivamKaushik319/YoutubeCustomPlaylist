import os,pickle, sys
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request #Google's Request
from googleapiclient.discovery import build
import googleapiclient.discovery
import googleapiclient.errors
import datetime

credentials=None


#token.pickle stores user credentials from previous logins
if os.path.exists('token.pickle'):
    print('Loading credentials from file...')
    with open('token.pickle','rb') as token:
        credentials=pickle.load(token)

#If no valid credentials available, then either login or refresh

if not credentials or not credentials.valid:
    if credentials and credentials.expired and credentials.refresh_token:
        print('Refreshing token now...')
        credentials.refresh(Request())
    else:
        print('fetching new tokens...')
        flow=InstalledAppFlow.from_client_secrets_file(
            "client_secret.json",
            scopes=['https://www.googleapis.com/auth/youtube']
            )

        flow.run_local_server(port=8080,prompt='consent',authorization_prompt_message='')
        '''flow object is enabling local web server to use client ID and client secret from json file and
    accessing the authorization url, where it gives application access to the scopes that we listed.
    after this google sends back the authentication code and then google exchanges access token and refresh token in the background.
    '''
        #prompt='consent' will provide refresh token instead of default access token which expires as soon as provided.
        credentials=flow.credentials

        #Saving credentials for the next run
        with open ('token.pickle','wb') as credfile:
            print('Saving credentials for Future use...')
            pickle.dump(credentials,credfile)

non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
youtube_svc = build('youtube', 'v3', credentials=credentials)

request=youtube_svc.playlists().list(part='snippet',mine=True)
response = request.execute()
for item in response['items']:
    print(('For Playlist Name : '+'"'+item['snippet']['title']+'"')+(' corresponding playlist Id is : '+ item['id']))