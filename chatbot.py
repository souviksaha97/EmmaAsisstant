from wit import Wit
import json
import pycurl
import os
from io import BytesIO
from gtts import gTTS
import random
import wikipedia
import pyaudio
import wave
from newsapi import NewsApiClient
from datetime import datetime
import numpy as np
import vlc
import pafy
import time
import board
import digitalio
from PIL import Image, ImageDraw, ImageFont, ImageOps
import adafruit_ssd1306
from config import *
import youtube_dl
from gpiozero import Button

form_1 = pyaudio.paInt16 # 16-bit resolution
chans = 1 # 1 channel
samp_rate = 44100 # 44.1kHz sampling rate
chunk = 4096 # 2^12 samples for buffer
record_secs = 5 # seconds to record
dev_index =  2 # device index found by p.get_device_info_by_index(i)
wav_output_filename = 'test1.wav' # name of .wav file

today = datetime.today()
today = today.strftime("20%y-%m-%d")

def_timezone = 'Asia/Kolkata'
def_location = 'Mumbai'

am_pm = 'AM'

CONFIDENCE_INDEX = 0.9

FONT_SIZE_LARGE = 22
FONT_SIZE_MEDIUM = 18
FONT_SIZE_SMALL = 16

PLAYLIST_URL = 'https://www.youtube.com/playlist?list=PLFepKcct_CJG0mu-nb-HvQ52FRKTEO6hT'
WEATHER_URL = 'http://api.weatherstack.com/current?access_key='+WEATHER_API+'&query='
TIME_URL = 'http://worldtimeapi.org/api/timezone/'

DELAY = 2

month_dict = {'01':'January', '02':'February', '03':'March', '04':'April', '05':'May', '06':'June', '07':'July', '08':'August', '09':'September',
              '10':'October', '11':'November', '12':'December'}

time_phrases_list = ['The time is ', 'It is ', 'Right now it is ', 'Presently it is ']
greet_phrases_list = ['Hey! My name is Emma. Nice to meet you! ',
                      'Hello there! Good day to you! I am Emma, your personal Assistant! ',
                      'Howdy! I am your partner Emma. You can call me Em, Emmie or Emily ',
                      'Wassup ', 'Hi! My name is Emma! Happy to be at your service! ']
unsure_phrases_list = ["I'm not sure what you meant. Please try again. " , "I didn't get you. Can you repeat what you said? ", "I think I missed you. Please repeat. "]

def query_function():
    audio = pyaudio.PyAudio();
    
##    exit_check = input('Press a button to start listening')
    PPbutton.wait_for_press()
    os.system("omxplayer ding.wav");
    stream = audio.open(format = form_1,rate = samp_rate,channels = chans, \
                    input_device_index = dev_index,input = True, \
                    frames_per_buffer=chunk);
    print("recording")
    frames = []

    for i in range(0,int((samp_rate/chunk)*record_secs)):
        data = stream.read(chunk, exception_on_overflow = False)
        frames.append(data)

    print("finished recording")

    # stop the stream, close it, and terminate the pyaudio instantiation
    stream.close()
    audio.terminate()
    # save the audio frames as .wav file
    wavefile = wave.open(wav_output_filename,'wb')
    wavefile.setnchannels(chans)
    wavefile.setsampwidth(audio.get_sample_size(form_1))
    wavefile.setframerate(samp_rate)
    wavefile.writeframes(b''.join(frames))
    wavefile.close()
    
    os.system("omxplayer dong.wav");

    with open(wav_output_filename, 'rb') as f:
        resp = client_wit.speech(f, None, {'Content-Type': 'audio/wav'})
        

    print(resp)
 
    


    task_dict = resp['entities']
    if "intent_entity" in task_dict:
        intent_value =  task_dict['intent_entity'][0]['value']
        intent_confidence = task_dict['intent_entity'][0]['confidence']
        if intent_confidence >= CONFIDENCE_INDEX:
            if intent_value == 'time':
                print('time')
                get_time()
            elif intent_value == 'weather':
                print('weather')
                try:
                    get_weather(location=resp['entities']['location'][0]['value'])
                except:
                    get_weather()
            elif intent_value == 'news':
                print('news')
                get_news()
            elif intent_value == 'music':
                print('music')
                music_player()
        else:
            unsure_resp()
    elif "greetings" in task_dict:
        print('greet')
        if task_dict['greetings'][0]['confidence'] >= CONFIDENCE_INDEX:
            greet_fn()
    elif "wikipedia_search_query" in task_dict:
        print('wikipedia_search_query')
        if task_dict['wikipedia_search_query'][0]['confidence'] >= CONFIDENCE_INDEX:
            try:
                search_query = resp['entities']['wikipedia_search_query'][0]['value']
            except:
                search_query = resp['entities']['location'][0]['resolved']['values'][0]['name']
        search_fn(search_query)
    else:
        unsure_resp()



def get_time():
    #print('time')
    base_url = TIME_URL
    #print(resp)
    try:
        timezone = resp['entities']['location'][0]['resolved']['values'][0]['timezone']
        location = resp['entities']['location'][0]['resolved']['values'][0]['name']
    except:
        timezone = def_timezone
        location = def_location

    print(location)
    base_url=base_url+timezone
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, base_url)
    c.setopt(c.WRITEDATA, buffer)
    c.perform()
    c.close()
    body = buffer.getvalue()
    json_data = json.loads(body.decode('iso-8859-1'))
    #print(json_data)
    datetime_list = json_data['datetime'].split('T')
    date_list = datetime_list[0].split('-')
    time_list = datetime_list[1].split(':')

    
    print(time_list)
    print(date_list)

    if (int(time_list[0]) > 12):
        time_list[0] = str(int(time_list[0]) - 12);
        am_pm = 'PM'
    elif (int(time_list[0]) < 12):
        am_pm = 'AM'
    else:
        am_pm = 'PM'

    
    rand_seq = random.randint(0,len(time_phrases_list)-1)

    sentence = time_phrases_list[rand_seq] + time_list[0] + ":" + time_list[1] + " " + am_pm + " in " + location + ". It is the " + date_list[2] + " of " + month_dict[date_list[1]] + "," + date_list[0] + "  ."
    
    print(sentence)
    time_output = gTTS(sentence, lang = 'en-gb')
    time_output.save('time.mp3')
    os.system("omxplayer time.mp3");
    print(timezone)
    query_function()
    
def get_weather(location='mumbai'):
    base_url = WEATHER_URL
    print(location)

    base_url=base_url+location
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, base_url)
    c.setopt(c.WRITEDATA, buffer)
    c.perform()
    c.close()
    body = buffer.getvalue()
    forecast = json.loads(body.decode('iso-8859-1'))
    print(forecast)
    temp = str(forecast['current']['temperature'])
    print(temp)
    humidity = str(forecast['current']['humidity'])
    print(humidity)
    feelslike = str(forecast['current']['feelslike'])
    print(feelslike)
    img_url = forecast['current']['weather_icons'][0]
    print(img_url)
    text = forecast['current']['weather_descriptions'][0]
    print(text)
    sentence = "The weather in " + location + " is , " + " " + text + " with a temperature of " + temp + " degrees celsius and a humidity of " + humidity + "%. It feels like " + feelslike + " degrees celsius. "
    print(sentence)

    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, img_url)
    c.setopt(c.WRITEDATA, buffer)
    c.perform()
    c.close()
    draw.rectangle((0, 0, oled.width, oled.height),
                           outline=0, fill=0)
    image = (
        ImageOps.grayscale(Image.open(buffer))
        .resize((oled.width, oled.height), Image.BICUBIC)
        .convert("1")
    )
    oled.image(image)
    oled.show()
    
    if forecast['current']['temperature'] > 35:
        sentence += "That's so hot! I'll melt my circuits for sure.  "
    elif forecast['current']['temperature'] < 5:
        sentence += "Brrrr! I'll  freeze my circuits short in this cold!  "
    if "Rain" in text or "rainy" in text or "rain" in text:
        sentence += "Don't forget an umbrella! I'm sure you'll need one    ."
    elif "Snow" in text:
        sentence += "You might need a jacket! It could snow in a while!   "
    elif "Sunny" in text:
        sentence += "It's nice and sunny outside! Have a great day!   "

    print(sentence)
##    except:
##        sentence = "I'm not sure what place you asked for. Please try again!  "
    
    weather_output = gTTS(sentence, lang = 'en-gb')
    weather_output.save('weather.mp3')
    os.system("omxplayer weather.mp3");
    query_function()

def greet_fn():
    rand_seq = random.randint(0, len(greet_phrases_list)-1)
    greet_output = gTTS(greet_phrases_list[rand_seq], lang = 'en-gb')
    os.system("omxplayer greet.mp3");
    query_function()

def search_fn(search_query):
    
    print(search_query)
    try:
        sentence = wikipedia.summary(search_query, sentences=3)
        print("Got data")
    except:
        sentence = "I'm sorry. I couldn't find the relevant article online.   "

    print(sentence)                
    search_output = gTTS(sentence, lang = 'en-gb')
    search_output.save('search.mp3')
    os.system("omxplayer search.mp3");
    query_function()
    

def get_news():
    print('here')
    sentence = " " 
    try:
        news_query = client_news.get_top_headlines(country = 'in')
        print('got news')
    except:
        news_query = resp['entities']['location'][0]['resolved']['values'][0]['name']

    for i in news_query['articles']:
        sentence += i['title'] + ". "

    #print(sentence)
    search_output = gTTS(sentence, lang = 'en-gb')
    search_output.save('news.mp3')
    os.system("omxplayer news.mp3");
    query_function()

def unsure_resp():
    rand_seq = random.randint(0, len(unsure_phrases_list)-1)
    print('unsure')
    unsure_output = gTTS(unsure_phrases_list[rand_seq], lang = 'en-gb')
    unsure_output.save('unsure.mp3')
    os.system("omxplayer unsure.mp3");
    query_function()


def music_player():
    random.shuffle(url_list)
    exitFlag = 0
    for i in url_list:
        fastFwdFlag = 0
        try:
            video=pafy.new(i)
            x=video.getbestaudio()
        except:
            print(i)
            continue
        print(video.title)
        print(video.author)
        print(x.bitrate, x.extension)
        songStringList=video.title.split(' - ')
        if len(songStringList)==2:
            songName=songStringList[1]
            songArtist=songStringList[0]
        else:
            songName=video.title
            songArtist=video.author
        # Display image
        oled.image(image)
        oled.show()
        songStart=time.time()
        
        player.set_mrl(x.url)
        player.play()
        songPercent = 0
        (name_width, name_height) = font_l.getsize(songName)
        (artist_width, artist_height) = font_m.getsize(songArtist)
        max_width = 0
        if name_width > artist_width:
            max_width = name_width
        else:
            max_width = artist_width
        print(video.length, x.url)
        pausePlayButton = 0
        while time.time()-songStart < video.length+DELAY:
            for x in range(0, max_width+oled.width):
##                songPercent=int(((time.time()-songStart)/video.length)*100)
                songPercent=(time.time()-songStart)/video.length
                draw.rectangle((0, 0, oled.width, oled.height),
                           outline=0, fill=0)
                draw.text((oled.width-x,oled.height//2 - name_height//2 - 20),songName,font=font_l,fill=255)
                draw.text((oled.width+name_width//2-artist_width//2-x,oled.height//2 - 5),
                          songArtist,font=font_m,fill=255)
##                draw.text((oled.width//2, oled.height//2 + 12),str(songPercent),font=font_s,fill=255)
                draw.rectangle((5, oled.height - 15, int((oled.width-5)*songPercent), oled.height-5), outline=0, fill=255)
                oled.image(image)
                oled.show()
                time.sleep(0.01667)
                if PPbutton.is_pressed:
                    print('pause')
                    player.pause()
                    time.sleep(0.2)
                    PPbutton.wait_for_press()
                    print('play')
                    player.play()
                    time.sleep(0.2)
                if Stopbutton.is_pressed:
                    print('stop')
                    exitFlag = 1
                    player.stop()
                    break
                if FFbutton.is_pressed:
                    print('ff')
                    fastFwdFlag = 1
                    time.sleep(0.2)
                    break
                if time.time()-songStart > video.length+DELAY:
                    break

            if fastFwdFlag == 1:
                print('ff')
                player.stop()
                break
            if exitFlag == 1:
                player.stop()
                break
            
        if exitFlag == 1:
            player.stop()
            break

    if exitFlag == 1:
        query_function()
                

if __name__ == "__main__":
    with youtube_dl.YoutubeDL({}) as ydl:
        ydl.cache.remove()
    
    client_wit = Wit(WIT_API)
    print('Connected to wit client')
    client_news = NewsApiClient(api_key=NEWSCLI_API)
    print('Connected to news client')
    # Define the Reset Pin
    oled_reset = digitalio.DigitalInOut(board.D4)
    PPbutton = Button(4)
    FFbutton = Button(14)
    Stopbutton = Button(15)
    # Change these
    # to the right size for your display!
    WIDTH = 128
    HEIGHT = 64

    # Use for I2C.
    i2c = board.I2C()
    oled = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=0x3c, reset=oled_reset)
    oled.fill(0)
    oled.show()
    pafy.set_api_key(YOUTUBE_API)
    playlist = pafy.get_playlist2(PLAYLIST_URL)
    url_list=[]
    for i in playlist:
        pl_list=str(i).split()
        url_list.append(pl_list[2])
    print('Retrieved ' + str(len(url_list)) + ' songs from playlist')

    image = Image.new('1', (oled.width, oled.height))

    # Get drawing object to draw on image.
    draw = ImageDraw.Draw(image)

    # Load default font.
    font_l = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", FONT_SIZE_LARGE)
    font_s = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", FONT_SIZE_SMALL)
    font_m = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", FONT_SIZE_MEDIUM)

    vlcInstance = vlc.Instance()
    player = vlcInstance.media_player_new()
    player.stop()
    os.system("omxplayer startup.wav");
    query_function()
    

            
            













