
# -*- coding: utf-8 -*-
import io
import os
import time

import requests
import telebot
from telebot import types

import main


class User:
    def __init__(self):
        self.mng = main.Manager()
        self.status = None
        self.cur_filter = None
        self.nick = None

    def set_status(self, status):
        self.status = status

    def get_status(self):
        return self.status

    def set_cur_filter(self, cur_filter):
        self.cur_filter = cur_filter

    def get_cur_filter(self):
        return self.cur_filter
    
    def set_nick(self, nick):
        self.nick = nick

    def get_nick(self):
        return self.nick


def filter_kbd(message):
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton('Gaussian Blur')
    btn2 = types.KeyboardButton('Box Blur')
    btn3 = types.KeyboardButton('Rotate')
    btn4 = types.KeyboardButton('Resize')
    btn5 = types.KeyboardButton('Flip L-R')
    btn6 = types.KeyboardButton('Flip T-B')
    btn7 = types.KeyboardButton('Adj Color')
    btn8 = types.KeyboardButton('Adj Contrast')
    btn9 = types.KeyboardButton('Adj Sharpness')
    btn10 = types.KeyboardButton('Adj Brightness')
    markup.row(btn1, btn2)
    markup.row(btn3, btn4)
    markup.row(btn5, btn6)
    markup.row(btn7, btn8)
    markup.row(btn9, btn10)
    markup.resize_keyboard, markup.one_time_keyboard = True, True
    BOT.send_message(message.chat.id, "Выбирай фильтр:", reply_markup=markup)


def edit_kbd(message):
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton('Добавить фильтр')
    btn2 = types.KeyboardButton('Список фильтров')
    btn3 = types.KeyboardButton('Загрузить фильтры')
    btn4 = types.KeyboardButton('Сохранить фильтры')
    btn5 = types.KeyboardButton('Удалить последний фильтр')
    btn6 = types.KeyboardButton('Применить фильтры')
    btn7 = types.KeyboardButton('Закончить')
    markup.row(btn1, btn2)
    markup.row(btn3, btn4)
    markup.row(btn5, btn6)
    markup.row(btn7)
    markup.resize_keyboard, markup.one_time_keyboard = True, True
    BOT.send_message(message.chat.id, "Выбери, что хочешь сделать:", reply_markup=markup)


FILTER_SWITCH = {"Gaussian Blur": "blur",
                 'Box Blur': "boxblur",
                 'Rotate': "rotate",
                 'Resize': "resize",
                 'Flip L-R': "flip",
                 'Flip T-B': "flip",
                 'Adj Color': "color",
                 'Adj Contrast': "contrast",
                 'Adj Sharpness': "sharpness",
                 'Adj Brightness': "brightness"}

API_TOKEN = "1046577086:AAF9ddY3UYl34imgmjPVhaIiB0nWbVXi_t8"

BOT = telebot.TeleBot(API_TOKEN)

USERS = {}


@BOT.message_handler(commands=['admin_nfo'])
def admin_info(message):
    print(str(message.chat.id) + ': ' + str(message.chat.username) + ' = ' + '/admin_nfo')
    BOT.send_message(message.chat.id, str(message.chat.id) + ': ' + str(message.chat.username) + ' = ' + '/admin_nfo')
    print("list of users:")
    u_list = []
    for user in USERS.keys():
        u_list.append(str(USERS.get(user).get_nick()) + ': ' + str(USERS.get(user).get_status()))
    print('\n'.join(u_list))
    BOT.send_message(message.chat.id, "list of users:\n\n" + '\n'.join(u_list))


@BOT.message_handler(commands=['start'])
def send_welcome(message):
    print(str(message.chat.id) + ': ' + str(message.chat.username) + ' = ' + '/start')
    BOT.send_message(message.chat.id,
                     "Хей, я умею обрабатывать картиночки! "
                     "\nЗагрузи ее как ДОКУМЕНТ, дальше расскажу что можно сделать.")
    USERS.update({message.chat.id: User()})
    USERS.get(message.chat.id).set_status('start')
    USERS.get(message.chat.id).set_nick(message.chat.username)


@BOT.message_handler(commands=['help'])
def send_help(message):
    print(str(message.chat.id) + ': ' + str(message.chat.username) + ' = ' + '/help')
    BOT.send_message(message.chat.id,
                     message.chat.first_name + ", введи /start и следуй инструкциям, зачем тебе хелп")


@BOT.message_handler(content_types=['photo'],
                     func=lambda message: USERS.get(message.chat.id, User()).get_status() == "start")
def error_image(message):
    print(str(message.chat.id) + ': ' + str(message.chat.username) + ' = ' + 'send image, not document')
    BOT.send_message(message.chat.id, message.chat.first_name + ", я же просил документом (ФАЙЛОМ), а не картинкой."
                                                                "Пожалуйста, исправься")


@BOT.message_handler(content_types=['document'],
                     func=lambda message: USERS.get(message.chat.id, User()).get_status() == "start")
def handle_image(message):
    print(str(message.chat.id) + ': ' + str(message.chat.username) + ' = ' + 'try upload photo')
    file_info = BOT.get_file(message.document.file_id)
    file = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(API_TOKEN, file_info.file_path))
    try:
        USERS.get(message.chat.id).mng.open_file(io.BytesIO(file.content))
        USERS.get(message.chat.id).set_status('editing')
        print(str(message.chat.id) + ': ' + str(message.chat.username) + ' = ' + 'success')
        BOT.reply_to(message, "Отлично, я получил и прочитал изображение!"
                              "\nДавай улучшим его")
        edit_kbd(message)
    except Exception as exept:
        BOT.reply_to(message, "Кривая у тебя картинка какая-то... \nИли вообще не картинка... \nДавай нормальную!")
        print(str(message.chat.id) + ': ' + str(message.chat.username) + ' = ' + 'exception ' + str(exept))


@BOT.message_handler(content_types=['document'],
                     func=lambda message: USERS.get(message.chat.id, User()).get_status() == "load_filters")
def handle_flist(message):
    print(str(message.chat.id) + ': ' + str(message.chat.username) + ' = ' + 'try upload txt')
    file_info = BOT.get_file(message.document.file_id)
    file = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(API_TOKEN, file_info.file_path))
    try:
        USERS.get(message.chat.id).mng.load_complex_filter_from_str(file.content.decode("utf-8"))
        BOT.reply_to(message, "Настройки загружены")
        print(str(message.chat.id) + ': ' + str(message.chat.username) + ' = ' + 'success')
    except Exception as exept:
        BOT.reply_to(message, "Не похоже это на список фильтров. Попробуй что-то другое")
        print(str(message.chat.id) + ': ' + str(message.chat.username) + ' = ' + 'exception ' + str(exept))
    USERS.get(message.chat.id).set_status('editing')
    edit_kbd(message)


@BOT.message_handler(func=lambda message: USERS.get(message.chat.id, User()).get_status() == "add")
def add_filter(message):
    print(str(message.chat.id) + ': ' + str(message.chat.username) + ' = ' + 'trying add filter')
    filter_name = message.text
    markup = types.ForceReply(selective=False)
    if filter_name == "Gaussian Blur":
        BOT.send_message(message.chat.id, "Радиус блюра от 0.0:", reply_markup=markup)
    elif filter_name == "Box Blur":
        BOT.send_message(message.chat.id, "Радиус блюра от 0.0:", reply_markup=markup)
    elif filter_name == "Rotate":
        BOT.send_message(message.chat.id, "Угол поворота против часовой стрелки::", reply_markup=markup)
    elif filter_name == "Resize":
        BOT.send_message(message.chat.id, "Высота(h) и ширина(w) через пробел h w:", reply_markup=markup)
    elif filter_name == "Flip L-R":
        BOT.send_message(message.chat.id, "Напиши букву \"v\":", reply_markup=markup)
    elif filter_name == "Flip T-B":
        BOT.send_message(message.chat.id, "Напиши букву \"h\":", reply_markup=markup)
    elif filter_name == "Adj Color":
        BOT.send_message(message.chat.id, ">1.0 - насыщенее, <1.0 - тусклее:", reply_markup=markup)
    elif filter_name == "Adj Contrast":
        BOT.send_message(message.chat.id, ">1.0 - контрастней, <1.0 - однородней:", reply_markup=markup)
    elif filter_name == "Adj Sharpness":
        BOT.send_message(message.chat.id, ">1.0 - четче, <1.0 - мягче:", reply_markup=markup)
    elif filter_name == "Adj Brightness":
        BOT.send_message(message.chat.id, ">1.0 - ярче, <1.0 - темнее:", reply_markup=markup)
    else:
        print(str(message.chat.id) + ': ' + str(message.chat.username) + ' = ' + 'wrong input')
        BOT.send_message(message.chat.id, "Нажимай на кнопки ниже, не выдумывай ничего нового, иначе я тебя не пойму")
        filter_kbd(message)
        return
    USERS.get(message.chat.id).set_status("args")
    USERS.get(message.chat.id).set_cur_filter(FILTER_SWITCH.get(filter_name))


@BOT.message_handler(func=lambda message: USERS.get(message.chat.id, User()).get_status() == "args")
def setup_filter(message):
    print(str(message.chat.id) + ': ' + str(message.chat.username) + ' = ' + "trying to add " + USERS.get(
        message.chat.id).get_cur_filter() + ' ' + str(message.text))
    try:
        USERS.get(message.chat.id).set_status("editing")
        USERS.get(message.chat.id).mng.add_filter_from_str(
            USERS.get(message.chat.id).get_cur_filter() + ' ' + str(message.text))
    except Exception as exept:
        print(str(message.chat.id) + ': ' + str(message.chat.username) + ' = ' + 'exception ' + str(exept))
        BOT.send_message(message.chat.id, "Ты написал что-то не то. Вводи аргумент по шаблону и читай инструкции")
    edit_kbd(message)


@BOT.message_handler(func=lambda message: USERS.get(message.chat.id, User()).get_status() == "editing")
def edit_image(message):
    print(str(message.chat.id) + ': ' + str(message.chat.username) + ' = ' + 'editing')
    if message.text == "Добавить фильтр":
        USERS.get(message.chat.id).set_status('add')
        filter_kbd(message)
    elif message.text == "Список фильтров":
        print(str(message.chat.id) + ': ' + str(message.chat.username) + ' = ' + 'show filter list')
        BOT.send_message(message.chat.id,
                         "Вот список фильтров в очереди:\n\n" + str(USERS.get(message.chat.id).mng.get_filter_list()))
        BOT.send_message(message.chat.id, "Возможные ошибки:\n"
                                          "\t- В парметре запятая вместо точки\n"
                                          "\t- У flip что либо кроме \"v\" или \"h\"\n"
                                          "\t- У resize отсутствует пробел между параметрами\n")
        edit_kbd(message)
    elif message.text == "Загрузить фильтры":
        BOT.send_message(message.chat.id, "Отправь мне файл с настройками")
        USERS.get(message.chat.id).set_status('load_filters')
    elif message.text == "Сохранить фильтры":
        print(str(message.chat.id) + ': ' + str(message.chat.username) + ' = ' + 'save filter list')
        file_name = str(message.chat.id) + "_filter_list.txt"
        USERS.get(message.chat.id).mng.save_complex_filter(file_name)
        with open(file_name, "rb") as filter_list:
            BOT.send_document(message.chat.id, filter_list)
        os.remove(file_name)
        edit_kbd(message)
    elif message.text == "Удалить последний фильтр":
        print(str(message.chat.id) + ': ' + str(message.chat.username) + ' = ' + 'delete last filter')
        USERS.get(message.chat.id).mng.remove_filter_from_chain()
        BOT.send_message(message.chat.id, "Окей, теперь фильтров на один меньше, можешь посмотреть список")
        edit_kbd(message)
    elif message.text == "Применить фильтры":
        print(str(message.chat.id) + ': ' + str(message.chat.username) + ' = ' + 'apply filters')
        try:
            USERS.get(message.chat.id).mng.reset()
            USERS.get(message.chat.id).mng.apply_filter_chain()
            BOT.send_message(message.chat.id, "Все фильтры применились удачно, держи изображение:")
            file_name = str(message.chat.id) + "_out_img.png"
            USERS.get(message.chat.id).mng.save_file(file_name)
            with open(file_name, "rb") as out_img:
                BOT.send_document(message.chat.id, out_img)
            os.remove(file_name)
        except Exception:
            BOT.send_message(message.chat.id, "Ты ввел что-то не то. Проверь список фильтров, все ли введено верно")
        finally:
            edit_kbd(message)
    elif message.text == "Закончить":
        msg_edit = message
        msg_edit.text = "Применить фильтры"
        edit_image(msg_edit)
        print(str(message.chat.id) + ': ' + str(message.chat.username) + ' = ' + 'quit')
        USERS.get(message.chat.id).set_status(None)
        BOT.send_message(message.chat.id, "Обработаем еще картинку?")
        BOT.send_message(message.chat.id,
                         message.chat.first_name + ", для начала введи /start и следуй инструкциям")
    else:
        print(str(message.chat.id) + ': ' + str(message.chat.username) + ' = ' + 'wrong input')
        BOT.send_message(message.chat.id,
                         "Нажимай на кнопки ниже, не выдумывай ничего нового, я тупенький робот и могу тебя не понять")
        edit_kbd(message)


@BOT.message_handler(
    content_types=['text', 'entities', 'audio', 'document', 'photo', 'sticker', 'video', 'video_note', 'voice'],
    func=lambda message: True)
def echo_all(message):
    print(str(message.chat.id) + ': ' + str(message.chat.username) + ' = ' + 'wrong input')
    BOT.send_message(message.chat.id, message.chat.first_name + ", для начала введи /start и следуй инструкциям")


while True:
    try:
        BOT.polling(none_stop=true)
    except Exception as e:
        print('!! = ' + "exception " + str(e))
        time.sleep(3)
