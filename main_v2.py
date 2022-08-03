# pip install pydub SpeechRecognition playsound
import random
import time
import playsound
import speech_recognition as sr

import config
import requests
from pydub import AudioSegment

from datetime import datetime


def synthesize(folder_id, iam_token, text):
    url = 'https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize'
    headers = {
        'Authorization': 'Bearer ' + iam_token,
    }

    data = {
        'text': text,
        'lang': 'ru-RU',
        'voice': 'filipp',  #alena
        'folderId': folder_id
    }

    with requests.post(url, headers=headers, data=data, stream=True) as resp:
        if resp.status_code != 200:
            raise RuntimeError("Invalid response received: code: %d, message: %s" % (resp.status_code, resp.text))

        for chunk in resp.iter_content(chunk_size=None):
            yield chunk


def get_date(date, split='-'):
    day_list = ['первое', 'второе', 'третье', 'четвёртое',
        'пятое', 'шестое', 'седьмое', 'восьмое',
        'девятое', 'десятое', 'одиннадцатое', 'двенадцатое',
        'тринадцатое', 'четырнадцатое', 'пятнадцатое', 'шестнадцатое',
        'семнадцатое', 'восемнадцатое', 'девятнадцатое', 'двадцатое',
        'двадцать первое', 'двадцать второе', 'двадцать третье',
        'двадацать четвёртое', 'двадцать пятое', 'двадцать шестое',
        'двадцать седьмое', 'двадцать восьмое', 'двадцать девятое',
        'тридцатое', 'тридцать первое']
    month_list = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
           'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря']
    date_list = date.split(split)
    return (day_list[int(date_list[0]) - 1] + ' ' +
        month_list[int(date_list[1]) - 1] + ' ' +
        date_list[2] + ' года')


def save_voice_to_file(message, file_voice_name):
    with open(config.output, "wb") as f:
        for audio_content in synthesize(config.folder_id, config.aim_token, message):
            f.write(audio_content)
    sound = AudioSegment.from_ogg(config.output)
    sound.export(file_voice_name, format="mp3")


def listen_command():
    # obtain audio from the microphone
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Скажите вашу команду: ")
        audio = r.listen(source)

    # recognize speech using Google Speech Recognition
    try:
        our_speech = r.recognize_google(audio, language="ru")
        print("Вы сказали: "+our_speech)
        return our_speech
    except sr.UnknownValueError:
        return "ошибка"
    except sr.RequestError:
        return "ошибка"

    #return input("Скажите вашу команду: ")

def do_this_command(message):
    message = message.lower()
    if "привет" in message:
        say_message("Привет друг!")
    elif "загадка" in message or "загадку" in message:
        say_message("На носу сидим, На мир глядим, За уши держимся.")       # Очки
    elif "время" in message or "времени" in message:
        now = datetime.now()
        say_message(f"Сейчас {now.hour} часов {now.minute} минут")
    elif "дата" in message:
        now = datetime.now().strftime("%d-%m-%Y")
        say_message(f"Сегодня {get_date(now)}")
    elif "пока" in message:
        say_message("Пока!")
        exit()
    else:
        say_message("Команда не распознана! Попробуйте еще раз!")

def say_message(message):
    file_voice_name = "_audio_"+str(time.time())+"_"+str(random.randint(0,100000))+".mp3"
    save_voice_to_file(message, file_voice_name)
    playsound.playsound(file_voice_name)

    print("Голосовой ассистент: "+message)

if __name__ == '__main__':
    while True:
        command = listen_command()
        do_this_command(command)
