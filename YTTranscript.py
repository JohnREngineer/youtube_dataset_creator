from youtube_transcript_api import YouTubeTranscriptApi
import time
import pandas as pd
import requests
import random
from bs4 import BeautifulSoup as bs
from requests.adapters import HTTPAdapter
from timeit import default_timer as timer

class YTTranscript:

  def __init__(self,df):
    df = df.loc[[len(ytid)>0 for ytid in df.youtube_id]]
    df = df.reset_index(drop=True)
    df['transcript'] = [[] for _ in df.index]
    self.df = df

  def downloadTranscripts(self,cookiePath,verbose = False):
    for row in self.df.itertuples():
      if (len(row.transcript) == 0):
        start = timer()
        video_error = False
        connection_error = True
        while connection_error:
          transcript, video_error, connection_error, exception = self.getTranscript(row.youtube_id,cookie=None)
          retried_text=''
          if video_error:
            # try with cookie
            transcript, video_error, connection_error, exception = self.getTranscript(row.youtube_id,cookie=cookiePath)
            retried_text='with cookie'
          if not connection_error:
            s = self.getWaitSeconds(1,800)
            end = timer()
            elapsed = (end - start)
            if verbose: print(elapsed,s-elapsed)
            if elapsed < s:
              time.sleep(s-elapsed)
            if exception == 0:
              self.df.at[row.Index,'transcript'] = transcript
              if verbose: print(row.Index, row.youtube_id, 'success', retried_text)
            else:
              print(row.Index, row.youtube_id, 'youtube fail', retried_text)
              if verbose: print(str(exception))
          else:
            print(row.Index, row.youtube_id, 'proxy fail', retried_text)
            if verbose: print(str(exception))
      else:
        if verbose: print(row.Index, row.youtube_id, 'skip')
  
  def getTranscript(self,youtube_id,proxy=None,cookie=None):
    video_error = False
    connection_error = False
    transcript = []
    exception = 0
    try:
      transcript = YouTubeTranscriptApi.get_transcript(youtube_id,proxies=proxy,cookies=cookie)#,max_retries=0,timeout=(1,27))
    except Exception as e:
      exception = e
      video_error = 'you are sure' in str(exception)
      # connection_error = 'HTTPSConnectionPool' in str(exception)
      connection_error = not video_error
    return transcript, video_error, connection_error, exception

  def getWaitSeconds(self, proxy_count, requests_per_hour):
    requests_per_second_user = requests_per_hour / 3600
    requests_per_second = proxy_count * requests_per_second_user
    seconds_per_request = 1/requests_per_second
    return seconds_per_request
