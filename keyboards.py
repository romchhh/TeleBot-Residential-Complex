from telebot.types import *
import users_function
import config as config


def back():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*[KeyboardButton(name) for name in ['Назад']])
    return keyboard


def main():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*[KeyboardButton(name) for name in ["Пропустити пішохода"]])
    keyboard.add(*[KeyboardButton(name) for name in ["Пропустити автомобіль"]])
    keyboard.add(*[KeyboardButton(name) for name in ["Викликати охорону"]])
    return keyboard


def phone():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton(text="☎️ Надіслати номер", request_contact=True))
    keyboard.add(KeyboardButton(text="❌ Відмінити"))
    return keyboard


def cancel():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton(text="❌ Відмінити"))
    return keyboard


def name(chat_id):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    client = users_function.get_client(chat_id)
    if client['name']:
        keyboard.add(KeyboardButton(text=client['name']))
    keyboard.add(KeyboardButton(text="❌ Відмінити"))
    return keyboard


def street(chat_id):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    client = users_function.get_client(chat_id)
    if client['street']:
        keyboard.add(KeyboardButton(text=client['street']))
    keyboard.add(KeyboardButton(text="❌ Відмінити"))
    return keyboard


def house(chat_id):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    client = users_function.get_client(chat_id)
    if client['house']:
        keyboard.add(KeyboardButton(text=client['house']))
    keyboard.add(KeyboardButton(text="❌ Відмінити"))
    return keyboard


def apartment(chat_id):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    client = users_function.get_client(chat_id)
    if client['apartment']:
        keyboard.add(KeyboardButton(text=client['apartment']))
    keyboard.add(KeyboardButton(text="❌ Відмінити"))
    return keyboard
