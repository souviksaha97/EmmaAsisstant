import vlc
import pafy
import random
import time
from config import *
pafy.set_api_key(YOUTUBE_API)
plurl = 'https://www.youtube.com/playlist?list=PLFepKcct_CJG0mu-nb-HvQ52FRKTEO6hT'
playlist = pafy.get_playlist2(plurl)
url_list=[]
for i in playlist:
    pl_list=str(i).split()
    url_list.append(pl_list[2])
print(url_list)

##for i in url_list:
##    x=random.randint(0,440)
##    video=pafy.new(url_list[x])
##    x=video.getbestaudio()
##    print(x)
##    vlcInstance = vlc.Instance()
##    #url='https://www.youtube.com/watch?v=iP6XpLQM2Cs'
##    player = vlcInstance.media_player_new()
##    player.set_mrl(x.url)
##    player.play()
##    time.sleep(video.length+5)
##
##

video=pafy.new('rt7988RVMsU')
x=video.getbestaudio()
print(x)
vlcInstance = vlc.Instance()
#url='https://www.youtube.com/watch?v=iP6XpLQM2Cs'
player = vlcInstance.media_player_new()
player.set_mrl(x.url)
player.play()
##time.sleep(video.length+5)
