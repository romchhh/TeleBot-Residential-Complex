from telebot.types import *

def main():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*[KeyboardButton(name) for name in ['📊 Статистика', '🗂 Вигрузити БД']])
    keyboard.add(*[KeyboardButton(name) for name in ['Заблокувати', 'Розблокувати']])
    keyboard.add(*[KeyboardButton(name) for name in ['Перезаписати', 'Заявки']])
    return keyboard

