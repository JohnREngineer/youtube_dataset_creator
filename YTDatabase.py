import pandas as pd
import ipywidgets as widgets
from IPython.display import HTML

from PIL import Image
import requests
from io import BytesIO
import io
import html
from google.colab.patches import cv2_imshow
from matplotlib.pyplot import imshow
import numpy as np

class YTDatabase:

  def __init__(self,tuples,columns=['name','keyword','youtube_id','title','description','channel']):
    df = pd.DataFrame(tuples,columns=columns)
    df['has_name'] = [self.hasName(name,title+description+channel) for name,title,description,channel in zip(df.name,df.title,df.description,df.channel)]
    df['is_conversation'] = [self.isConversation(title+description+channel) for title,description,channel in zip(df.title,df.description,df.channel)]
    self.df = df
  
  def getRelevant(self):
    return db.df.loc[self.df.has_name & self.df.is_conversation]

  def hasName(self,name,text):
    first = name.split(' ')[0].casefold()
    last = name.split(' ')[-1].casefold()
    hasFirst = first in text.casefold()
    hasLast = last in text.casefold()
    answer = hasFirst and hasLast
    return answer
  
  def isConversation(self,text):
    goodKeywords = ['podcast','convers','discuss','chat',' #','ep.','episode','interview','q&a','guest','sit down','town hall','speech']
    badKeywords = ['clip','panel']
    return self.matchesKeywords(text,goodKeywords,badKeywords)

  def matchesKeywords(self,text,goodKeywords,badKeywords):
    hasGoodKeywords = any([keyword in text.casefold() for keyword in goodKeywords])
    hasBadKeywords = any([keyword in text.casefold() for keyword in badKeywords])
    matches = hasGoodKeywords and not hasBadKeywords
    return matches
  
  def getByteArray(self,youtube_id):
    image = self.getImage(youtube_id)
    imageByteArray = io.BytesIO()
    image.save(imageByteArray, format='PNG')
    imageByteArray = imageByteArray.getvalue()
    return imageByteArray

  def getImage(self,youtube_id):
    url = 'https://i.ytimg.com/vi/'+youtube_id+'/mqdefault.jpg'
    imageResponse = requests.get(url)
    image = Image.open(BytesIO(imageResponse.content))
    return image

  def toggle(self,**toggles):
    for key,value in toggles.items():
      if value:
        self.buttons[key].icon = 'check'
        self.buttons[key].button_style = 'success'
      else:
        self.buttons[key].icon = 'close'
        self.buttons[key].button_style = 'danger'

  def finalize(self,**toggles):
    finalIndexes = []
    if toggles.get('final'):
      for key,button in self.buttons.items():
        if button.value:
          finalIndexes.append(int(key))
      self.dfFinal = self.df.loc[[index in finalIndexes for index in self.df.index]].reset_index(drop=True)
      # self.vidDisplay.layout.visibility = 'hidden'
      self.vidDisplay.layout.display = 'none'
      # self.vidDisplay.disabled = True
      self.finalButton.get('final').disabled = True

  def displayOptions(self):
    display(HTML('<link rel="stylesheet" href="//stackpath.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css"/>'))

    # df = self.getRelevant()
    df = self.df.loc[self.df.has_name]
    
    buttons = {}
    texts = []
    images = []
    for index,youtube_id, title, description, channel, is_conversation in zip(df.index,df.youtube_id,df.title,df.description,df.channel,df.is_conversation):
      
      initialize_on = is_conversation

      buttons[str(index)] = widgets.ToggleButton(
        layout={'width':'50px','height':'179px'},
        value=initialize_on,
        description='',
        disabled=False,
        button_style='success' if initialize_on else 'danger', # 'success', 'info', 'warning', 'danger' or ''
        tooltip='Description',
        icon='' # (FontAwesome names without the `fa-` prefix)
      )
      
      text = widgets.HTML(
          value='<body style="background-color:black;">'+\
            '<h3 style="color:white"><a href="https://youtube.com/watch?v='+youtube_id+'">'+title+'</a></h3>'+\
            '<p style="color:lightgrey">'+channel+'</p>'+\
            '<p style="color:lightgrey">'+description+'</p></body>',
          placeholder='',
          description='',
      )
      texts.append(text)

      imageByteArray = self.getByteArray(youtube_id)
      image = widgets.Image(
        value=imageByteArray,
        format='png',
        height = 200,
        width = 300
      ) 
      images.append(image)
  
    hBoxes=[]
    for button,image,text in zip(list(buttons.values()),images,texts):
      hBoxes.append(widgets.HBox([button,image,text]))
    hBoxes.append
    vidDisplay = widgets.VBox(hBoxes)

    self.buttons = buttons
    self.vidDisplay = vidDisplay

    interact = widgets.interactive_output(self.toggle, self.buttons)
    display(vidDisplay,interact)

    finalButton = {}
    finalButton['final'] = widgets.ToggleButton(
        # layout={'width':'100px','height':'50px'},
        value=False,
        description='Finalize',
        disabled=False,
        button_style='info', # 'success', 'info', 'warning', 'danger' or ''
        tooltip='Description',
        icon='' # (FontAwesome names without the `fa-` prefix)
      )
    self.finalButton = finalButton
    finalInteract = widgets.interactive_output(self.finalize, finalButton)
    display(finalButton['final'],finalInteract)

  def saveToPickle(self,path,filename):
    self.dfFinal.to_pickle(path+'/'+filename+'.pkl')