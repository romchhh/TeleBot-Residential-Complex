from telebot.types import *
from telebot import types

def main():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*[KeyboardButton(name) for name in ['📊 Статистика', '🗂 Вигрузити БД']])
    keyboard.add(*[KeyboardButton(name) for name in ['Заблокувати', 'Розблокувати']])
    keyboard.add(*[KeyboardButton(name) for name in ['Перезаписати', 'Заявки']])
    return keyboard

def get_applications_button(url):
    keyboard = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(text="Відкрити заявки", url=url)
    keyboard.add(button)
    return keyboard
