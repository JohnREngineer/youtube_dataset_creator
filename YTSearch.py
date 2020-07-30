import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import html

class YTSearch:
  
  def __init__(self,base_dir):
    scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]
    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = base_dir+"data/client_secret.json"

    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)
    credentials = flow.run_console()
    youtube = googleapiclient.discovery.build(api_service_name, api_version, credentials=credentials)
    self.youtube = youtube

  def search(self,name,keyword):
    tuples, nextPageToken = self.makeRequest(name,keyword)
    tuplesUnique = list(set(tuples))
    previousUniqueCount = 0
    while len(tuplesUnique) > previousUniqueCount:
      previousUniqueCount = len(tuplesUnique)
      newTuples, nextPageToken = self.makeRequest(name,keyword,nextPageToken)
      tuples += newTuples
      tuplesUnique = list(set(tuples))
    return tuplesUnique

  def makeRequest(self,name,keyword,nextPageToken=''):
    pageWargs = {'pageToken':nextPageToken} if len(nextPageToken) > 0 else {}
    request = self.youtube.search().list(
      part = "snippet",
      q=name+' '+keyword,
      # channelId = channel_id,
      type = "video",
      videoDuration = "long",
      safeSearch = 'none',
      maxResults = 50,
      **pageWargs
    )
    response = request.execute()
    nextPageToken = response.get('nextPageToken')
    tuples = [(name,
               keyword,
               item.get('id').get('videoId'), 
               html.unescape(item.get('snippet').get('title')),
               html.unescape(item.get('snippet').get('description')),
               html.unescape(item.get('snippet').get('channelTitle'))) for item in response.get('items')]
    return tuples, nextPageToken