from wit import Wit
import sys
import json
import pycurl
from io import BytesIO
from gtts import gTTS
import random
import os
import wikipedia
import pyaudio
import wave
from newsapi import NewsApiClient
from datetime import datetime

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

month_dict = {'01':'January', '02':'February', '03':'March', '04':'April', '05':'May', '06':'June', '07':'July', '08':'August', '09':'September',
              '10':'October', '11':'November', '12':'December'}

time_phrases_list = ['The time is ', 'It is ', 'Right now it is ', 'Presently it is ']
greet_phrases_list = ['Hey! My name is Emma. Nice to meet you! ',
                      'Hello there! Good day to you! I am Emma, your personal Assistant! ',
                      'Howdy! I am your partner Emma. You can call me Em, Emmie or Emily ',
                      'Wassup ', 'Hi! My name is Emma! Happy to be at your service! ']
unsure_phrases_list = ["I'm not sure what you meant. Please try again. " , "I didn't get you. Can you repeat what you said? ", "I think I missed you. Please repeat. "]

def get_time():
    #print('time')
    base_url = 'http://worldtimeapi.org/api/timezone/'
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
    os.system('omxplayer time.mp3')
    print(timezone)
    
def get_weather():
    base_url = 'http://api.weatherstack.com/current?access_key=1b189d0184fa9a1b90bb17b03e28ef2a&query='
    try:
        location = resp['entities']['location'][0]['resolved']['values'][0]['name']
    except:
        location = def_location

    print(location)
    print("Clear")
##    try:
##        forecast = client_apixu.forecast(q= location)
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

    text = forecast['current']['weather_descriptions'][0]
    print(text)
    sentence = "The weather in " + location + " is , " + " " + text + " with a temperature of " + temp + " degrees celsius and a humidity of " + humidity + "%. It feels like " + feelslike + " degrees celsius. "
    print(sentence)
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
    os.system('omxplayer weather.mp3')

def greet_fn():
    rand_seq = random.randint(0, len(greet_phrases_list)-1)
    greet_output = gTTS(greet_phrases_list[rand_seq], lang = 'en-gb')
    greet_output.save('greet.mp3')
    os.system('omxplayer greet.mp3')

def search_fn():
    try:
        search_query = resp['entities']['wikipedia_search_query'][0]['value']
    except:
        search_query = resp['entities']['location'][0]['resolved']['values'][0]['name']
    
    print(search_query)
    #print(resp['entities']['wikipedia_search_query'][0]['confidence'])
    try:
        sentence = wikipedia.summary(search_query, sentences=3)
        print("Got data")
    except:
        sentence = "I'm sorry. I couldn't find the relevant article online.   "

    print(sentence)                
    search_output = gTTS(sentence, lang = 'en-gb')
    search_output.save('search.mp3')
    os.system('omxplayer search.mp3')
    

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

    print(sentence)
    search_output = gTTS(sentence, lang = 'en-gb')
    search_output.save('news.mp3')
    os.system('omxplayer news.mp3')    

def unsure_resp():
    rand_seq = random.randint(0, len(unsure_phrases_list)-1)
    unsure_output = gTTS(unsure_phrases_list[rand_seq], lang = 'en-gb')
    unsure_output.save('unsure.mp3')
    os.system('omxplayer unsure.mp3')



client_wit = Wit('YWFXL2BL6FCUK6F7GA6JTEVNGS5Y2C5A')
client_news = NewsApiClient(api_key='94813f16596c4a428efdcae000a08756')


print()
while True:

#    query = input('Enter a query')
    audio = pyaudio.PyAudio()
    input('Press a button to start listening')
    stream = audio.open(format = form_1,rate = samp_rate,channels = chans, \
                    input_device_index = dev_index,input = True, \
                    frames_per_buffer=chunk)
    print("recording")
    frames = []

    for i in range(0,int((samp_rate/chunk)*record_secs)):
        data = stream.read(chunk, exception_on_overflow = False)
        frames.append(data)

    print("finished recording")

    # stop the stream, close it, and terminate the pyaudio instantiation
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # save the audio frames as .wav file
    wavefile = wave.open(wav_output_filename,'wb')
    wavefile.setnchannels(chans)
    wavefile.setsampwidth(audio.get_sample_size(form_1))
    wavefile.setframerate(samp_rate)
    wavefile.writeframes(b''.join(frames))
    wavefile.close()

    with open(wav_output_filename, 'rb') as f:
        resp = client_wit.speech(f, None, {'Content-Type': 'audio/wav'})
        
#    resp = client_wit.message(query)

    print(resp)
 
    #try:
        #task_dict = resp['entities']['intent'][0]
        ##print(task_dict)
        ##print(task_dict[0])
        ##print(task_dict[1])
        #print(str(task_dict['value']) + " " + str(task_dict['confidence']))
        #if task_dict['confidence'] >= CONFIDENCE_INDEX:
            #if task_dict['value'] == 'time':
                #get_time()
            #elif task_dict['value'] == 'weather':
                #get_weather()
            #elif task_dict['value'] == 'greet':
                #greet_fn()
            #elif task_dict['value'] == 'search_get':
                #search_fn()
            #elif task_dict['value'] == 'news_get':
                #get_news()
        #else:
            #unsure_resp()
    #except:
        #unsure_resp()

    try:
        task_dict = resp['entities']
        if "intent" in task_dict:
            intent_value =  task_dict['intent'][0]['value']
            intent_confidence = task_dict['intent'][0]['confidence']
            if intent_confidence >= CONFIDENCE_INDEX:
                if intent_value == 'time':
                    print('time')
                    get_time()
                elif intent_value == 'weather':
                    print('weather')
                    get_weather()
                elif intent_value == 'news':
                    print('news')
                    get_news()
            else:
                unsure_resp()
        elif "greetings" in task_dict:
            print('greet')
            if task_dict['greetings'][0]['confidence'] >= CONFIDENCE_INDEX:
                greet_fn()
        elif "wikipedia_search_query" in task_dict:
            print('wikipedia_search_query')
            if task_dict['wikipedia_search_query'][0]['confidence'] >= CONFIDENCE_INDEX:
                search_fn()
    except:
        unsure_resp()
            
            













