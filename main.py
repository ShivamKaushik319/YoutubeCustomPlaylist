import os,pickle, sys, logging
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request #Google's Request
from googleapiclient.discovery import build
import googleapiclient.discovery
import googleapiclient.errors
import datetime

credentials=None
playlistId='qwertyuiopasdfghjklzxcvbnm'

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
        

def get_youtube_subs():
    print('inside get_youtube_subs()')
    non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
    youtube_svc=build('youtube','v3',credentials=credentials)
    first=None
    totalResult=[]
    itemsList=[]
    subscriptionNameList=[]
    subscriptionChannelIdList=[]
    #getting subcription Data
    request=youtube_svc.subscriptions().list(part='snippet',maxResults=50, mine=True, order='alphabetical')
    response=request.execute()
    
    totalResult.append(response)
    nextPgTk=response['nextPageToken']

    #get next page of subcription - upper limit of range can be changed as per the number of subcriptions
    for loop in range(0,50):
        nextRequest=youtube_svc.subscriptions().list_next(request,response)

        if nextRequest==None:
            break
        
        nextResponse=nextRequest.execute()

        totalResult.append(nextResponse)
        request=nextRequest
        response=nextResponse

    #print(str(response).translate(non_bmp_map))    #used for logging of the data acquired and can be activated if required
    count=0

    for resp in totalResult:
        
        for item in resp['items']:
            #print('item is : '+str(item))  #logging done for item details and can be activated if required.
            subscriptionNameList.append(item['snippet']['title'])
            #print('item result(title) : '+(str(item['snippet']['title']).translate(non_bmp_map)))  #logging done for translated item details and can be activated if required.
            
            subscriptionChannelIdList.append(item['snippet']['resourceId']['channelId'])
            #print('item result(id) : '+(str(item['snippet']['resourceId']['channelId']).translate(non_bmp_map)))
            
            count=count+1
    print("count of subcriptions are : "+str(count))    #logging done for subcription count.
    return(subscriptionChannelIdList)



def get_video_details(channelId):
    tod=datetime.datetime.now()
    days=datetime.timedelta(days =3)
    checkDate=(tod-days).strftime("%Y-%m-%dT%H:%M:%SZ")

    channelId=channelId
    videoId=''
    non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
    youtube_svc=build('youtube','v3',credentials=credentials)

    channelRequest=youtube_svc.activities().list(part='contentDetails',channelId=channelId,maxResults=1,publishedAfter=checkDate)
    channelResponse=channelRequest.execute()
    activityItems=channelResponse['items']


    if len(activityItems)==0 or activityItems[0]['contentDetails']=={}:
        return(videoId)
    else:

        if 'subscription' in (activityItems[0]['contentDetails'].keys()) :
            return videoId
        else:
            videoId=str(activityItems[0]['contentDetails']['upload']['videoId'])
            return(videoId)

    #print(str(channelResponse1).translate(non_bmp_map))  #for Debugging of video information.

    #print(str(channelResponse['items'][0]['snippet']['publishedAt']).translate(non_bmp_map))   #for Debugging of required video information.

def getViews(videoId):
    videoId = videoId
    non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
    youtube_svc = build('youtube', 'v3', credentials=credentials)
    request=youtube_svc.videos().list(part='statistics',id=videoId,)
    videoResponse = request.execute()

    return (videoResponse['items'][0]['statistics'])

def emptyPlaylist(playlistId):
    non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
    listVidId=[]
    playlistId=playlistId
    listVidId=[]
    youtube_svc=build('youtube','v3',credentials=credentials)
    requestDelete=youtube_svc.playlistItems().list(part='snippet',playlistId=playlistId,maxResults=50)
    responseDelete=requestDelete.execute()

    for item in responseDelete['items']:
        listVidId.append(item['id'])

    for vid in listVidId:
        videoDelete = youtube_svc.playlistItems().delete(id=vid)
        videoDelete.execute()


def addToPlaylist(videoId):
    videoId=videoId
    non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
    youtube_svc=build('youtube','v3',credentials=credentials)

    request=youtube_svc.playlistItems().insert(part='snippet',body={'snippet':{'playlistId':playlistId ,
                                                                               'resourceId':{"kind":r'youtube#video',
                                                                                   'videoId':videoId}}})

    response=request.execute()

    #print(str(response).translate(non_bmp_map))
    

#Press the green button in the gutter to run the script.
if __name__ == '__main__':
    subs_list = get_youtube_subs()
    cAll = 0
    cfil = 0
    vidDict = {}
    emptyPlaylist(playlistId)

    for chId in subs_list:
        vidId = get_video_details(chId)

        if vidId == '':
            cAll = cAll + 1
            continue
        else:
            viewData = getViews(vidId)
            print('vid data is : ' + str(viewData))

            if (('viewCount' in viewData) and (viewData['viewCount'] != '' or viewData['viewCount'] != '0')) and (
                    ('likeCount' in viewData) and viewData['likeCount'] != ''):
                LbVratio = (int(viewData['likeCount'])) / (int(viewData['viewCount']))
                print('LbVratio is : ' + str(LbVratio))
                vidDict[vidId] = LbVratio
            else:
                print('LbVration cant be reached for : ' + vidId)

            cAll = cAll + 1
            cfil = cfil + 1
            # addToPlaylist(vidId)

    print('cAll is :' + str(cAll) + '     and cfil is: ' + str(cfil))

    finDict = (dict(sorted(vidDict.items(), key=lambda item: item[1], reverse=True)))
    keyList = list(finDict)
    TopTenlist = keyList[0:10]
    print(str(TopTenlist))

    for item in TopTenlist:
        addToPlaylist(item)
