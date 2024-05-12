import sqlite3
import sys
import threading
import time
import telebot
from telebot.types import *
from TeleBot.functions.users_functions import users_function
from TeleBot.data.config import token, admins, URL_SITE, group_id
from TeleBot.keyboards.admin import admin_keyboard as admin_keyboard
from TeleBot.keyboards.admin.admin_keyboard import get_applications_button
from TeleBot.keyboards.user import user_keyboard

bot = telebot.TeleBot(token, threaded=False)
sys.setrecursionlimit(10 ** 6)
conn = sqlite3.connect("TeleBot/data/data.db")

@bot.message_handler(commands=["admin"], func=lambda m: m.from_user.id == m.chat.id and m.from_user.id in admins)
def admin_command(message: Message):
    user_id = message.chat.id
    bot.send_message(user_id, 'Адмін панель', reply_markup=admin_keyboard.main())

@bot.message_handler(commands=["start"], func=lambda m: m.from_user.id == m.chat.id)
def start(message: Message):
    user_id = message.chat.id
    chat_id = message.chat.id
    print(message)

    c = conn.cursor()

    if c.execute("select * from clients where user_id = %s" % user_id).fetchone() is None:
        username = message.from_user.username
        last_name = message.from_user.last_name
        first_name = message.from_user.first_name
        c.execute("insert into clients (user_id, user_name, last_name, dataReq, first_name) values (?, ?, ?, ?, ?)",
                  (user_id, username, last_name, int(time.time()), first_name))
        conn.commit()

    def process_add_user(message: Message, column):
        chat_id = message.chat.id
        if message.text != '/start':
            bot.clear_step_handler(message)
            users_function.update_column_clients(chat_id, column=column, value=str(message.text))

            if column == 'apartment':
                client = users_function.get_client(chat_id)
                text = f"Верифікація! <a href='tg://user?id={chat_id}'>Написати користувачу</a>\n\n" \
                       f"Ім'я: {client['name']}\n" \
                       f"ІД: {chat_id}\n" \
                       f"Юзернейм: @{client['user_name']}\n" \
                       f"Вулиця: {client['street']}\n" \
                       f"Будинок: {client['house']}\n" \
                       f"Квартира: {client['apartment']}"
                try:
                    bot.send_message(group_id, text, parse_mode='html',
                                     reply_markup=InlineKeyboardMarkup().row(
                                         InlineKeyboardButton(text='✅', callback_data=f'acceptUser_{chat_id}')
                                     ).row(
                                         InlineKeyboardButton(text='❌', callback_data=f'declineUser_{chat_id}')
                                     ))
                except:
                    pass
        else:
            bot.send_message(chat_id, f"Не вірні данні")
        start(message)

    client = users_function.get_client(user_id)
    if not client['name']:
        bot.clear_step_handler(message)
        bot.send_message(chat_id, f"Ваше ПІП будь ласка:", reply_markup=ReplyKeyboardRemove())
        bot.register_next_step_handler(message, lambda m: process_add_user(m, 'name'))

    elif not client['street']:
        bot.send_message(chat_id, f"Щоб ідентифікувати Вас нам потрібно знати де Ви проживаєте, напишіть назву вулиці:",
                         reply_markup=ReplyKeyboardRemove())
        bot.register_next_step_handler(message, lambda m: process_add_user(m, 'street'))

    elif not client['house']:
        bot.send_message(chat_id, f"Супер! Який у Вас номер будинку?", reply_markup=ReplyKeyboardRemove())
        bot.register_next_step_handler(message, lambda m: process_add_user(m, 'house'))

    elif not client['apartment']:
        bot.send_message(chat_id, f"Чудово! А з якої Ви квартири?", reply_markup=ReplyKeyboardRemove())
        bot.register_next_step_handler(message, lambda m: process_add_user(m, 'apartment'))

    elif not client['verification']:
        bot.send_message(chat_id, f"Зачекайте поки ваші данні перевірить охорона!",
                         reply_markup=ReplyKeyboardRemove())
    elif client['userBlock']:
        bot.send_message(chat_id, f"Ви заблоковані!", reply_markup=ReplyKeyboardRemove())
    else:
        bot.send_message(user_id, 'Тут ви можете подати заявку до нашої охорони', parse_mode='HTML',
                         reply_markup=user_keyboard.main())


###ADMIN PANEL ####
@bot.message_handler(
    func=lambda m: m.text in ["👨🏼‍💻Admin Panel", '🗂 Вигрузити БД', '📊 Статистика', 'Заблокувати', 'Перезаписати',
                              'Розблокувати', 'Заявки'] and (m.chat.id in admins)
                   and m.from_user.id == m.chat.id)
def admin_panel(message: Message):
    chat_id = message.chat.id
    if message.text == "👨🏼‍💻Admin Panel":
        bot.send_message(chat_id=message.chat.id,
                         text="Увійшли в Адмін Панель",
                         reply_markup=admin_keyboard.main())

    elif message.text == '📊 Статистика':
        conn = sqlite3.connect("TeleBot/data/data.db")
        c = conn.cursor()
        allusers = c.execute("""SELECT COUNT(*) FROM clients""").fetchone()[0]
        c.close()
        text = "👤 *Кількість користувачів:* {0}".format(str(allusers))
        bot.send_message(message.chat.id, text, parse_mode='Markdown')

    elif message.text == '🗂 Вигрузити БД':
        bot.send_message(message.chat.id, "Процес вигрузки ...")
        bot.send_document(message.chat.id, users_function.get_DB(), caption=f"База користувачів")
        bot.send_document(message.chat.id, users_function.get_requests_DB(), caption=f"База запитів")

    elif message.text == 'Заявки':
        keyboard = get_applications_button(f"{URL_SITE}/main")
        bot.send_message(message.chat.id, text="Відкрити заявки:", reply_markup=keyboard)

    elif message.text == 'Заблокувати':
        def process_block_user(message: Message):
            bot.clear_step_handler(message)
            if message.text in ['/start', '❌ Відмінити']:
                bot.send_message(chat_id, f"Відміна", reply_markup=admin_keyboard.main())
            elif str(message.text).isnumeric():
                client = users_function.get_client(message.text)
                if client:
                    bot.send_message(chat_id, f"Користувача {client['name']} успішно заблоковано!")
                    users_function.update_column_clients(chat_id, column='userBlock', value=1)

                    try:
                        bot.send_message(chat_id=message.text, text=f"Ваш обліковий запис було заблоковано!")
                    except:
                        pass
                else:
                    bot.send_message(chat_id, f"Такого користувача не знайдено. Спробуйте ще раз!",
                                     reply_markup=admin_keyboard.main())
            else:
                bot.send_message(chat_id, f"Не вірний формат. Спробуйте ще раз!", reply_markup=admin_keyboard.main())

        bot.send_message(chat_id, f"Введіть user_id користувача, якого бажаєте заблокувати\n"
                                  f"Приклад вводу: 1068853244\n\n"
                                  f"<code> * user_id Ви можете отримати при вигрузці бази даних з користувачами</code>",
                         parse_mode='HTML', reply_markup=user_keyboard.cancel())
        bot.clear_step_handler(message)
        bot.register_next_step_handler(message, process_block_user)

    elif message.text == 'Розблокувати':
        def process_unblock_user(message: Message):
            bot.clear_step_handler(message)
            if message.text in ['/start', '❌ Відмінити']:
                bot.send_message(chat_id, f"Відміна", reply_markup=admin_keyboard.main())
            elif str(message.text).isnumeric():
                client = users_function.get_client(message.text)
                if client:
                    bot.send_message(chat_id, f"Користувача {client['name']} успішно розблоковано!")
                    users_function.update_column_clients(chat_id, column='userBlock', value=0)

                    try:
                        bot.send_message(chat_id=message.text, text=f"Ваш обліковий запис було розблоковано!")
                    except:
                        pass
                else:
                    bot.send_message(chat_id, f"Такого користувача не знайдено. Спробуйте ще раз!",
                                     reply_markup=admin_keyboard.main())
            else:
                bot.send_message(chat_id, f"Не вірний формат. Спробуйте ще раз!", reply_markup=admin_keyboard.main())

        bot.send_message(chat_id, f"Введіть user_id користувача, якого бажаєте розблокувати\n"
                                  f"Приклад вводу: 1068853244\n\n"
                                  f"<code> * user_id Ви можете отримати при вигрузці бази даних з користувачами</code>",
                         parse_mode='HTML', reply_markup=user_keyboard.cancel())
        bot.clear_step_handler(message)
        bot.register_next_step_handler(message, process_unblock_user)

    elif message.text == 'Перезаписати':
        def process_rewrite(message: Message):
            bot.clear_step_handler(message)
            if message.text in ['/start', '❌ Відмінити']:
                bot.send_message(chat_id, f"Відміна", reply_markup=admin_keyboard.main())
            elif str(message.text).isnumeric():
                client_id = message.text
                client = users_function.get_client(client_id)
                if client:
                    bot.send_message(chat_id, f"Користувача {client['name']} успішно видалено щоб він перезаписався!")
                    users_function.del_user(client_id)

                    try:
                        bot.send_message(chat_id=client_id,
                                         text=f"Ваш обліковий запис було видалено! Натисніть /start щоб оновити дані")
                    except:
                        pass
                else:
                    bot.send_message(chat_id, f"Такого користувача не знайдено. Спробуйте ще раз!",
                                     reply_markup=admin_keyboard.main())
            else:
                bot.send_message(chat_id, f"Не вірний формат. Спробуйте ще раз!", reply_markup=admin_keyboard.main())

        bot.send_message(chat_id, f"Введіть user_id користувача, якого бажаєте перезаписати\n"
                                  f"Приклад вводу: 1068853244\n\n"
                                  f"<code> * user_id Ви можете отримати при вигрузці бази даних з користувачами</code>",
                         parse_mode='HTML', reply_markup=user_keyboard.cancel())
        bot.clear_step_handler(message)
        bot.register_next_step_handler(message, process_rewrite)



####USER######
@bot.message_handler(func=lambda m: m.text in ["Пропустити автомобіль"] and m.from_user.id == m.chat.id)
def car(message: Message):
    def process_time(message: Message, data):
        bot.clear_step_handler(message)
        if message.text in ['/start', '❌ Відмінити']:
            start(message)
        else:
            data['time'] = message.text
            bot.send_message(chat_id, f"Ваша заява сформована! Вдалого дня)",
                             reply_markup=user_keyboard.main())

            client = users_function.get_client(chat_id)
            text = f"Пропустити автомобіль! <a href='tg://user?id={chat_id}'>Написати</a>\n\n" \
                   f"Ім'я: {client['name']}\n" \
                   f"ІД: {chat_id}\n" \
                   f"Юзернейм: @{client['user_name']}\n" \
                   f"Вулиця: {client['street']}\n" \
                   f"Будинок: {client['house']}\n" \
                   f"Квартира: {client['apartment']}\n" \
                   f"Номер машини: {data['car']}\n" \
                   f"К-сть гостей: {data['pcsQuests']}\n" \
                   f"Час: {data['time']}"

            users_function.create_request(user_id=chat_id, name=client['name'],
                                          first_name=client['first_name'], last_name=client['last_name'],
                                          user_name=client['user_name'],
                                          phone=client['phone'], street=client['street'], house=client['house'],
                                          apartment=client['apartment'], typeReq='Пропустити автомобіль',
                                          pcsQuests=data['pcsQuests'],
                                          car=data['car'], timeQuests=data['time'])

            try:
                bot.send_message(group_id, text, parse_mode='html')
            except:
                for admin_id in admins:
                    try:
                        bot.send_message(admin_id, text, parse_mode='html')
                    except:
                        pass

    def process_car(message: Message, data):
        bot.clear_step_handler(message)
        if message.text in ['/start', '❌ Відмінити']:
            start(message)
        else:
            data['car'] = message.text
            bot.send_message(chat_id, f"Який орієнтовний час прибуття гостей?", reply_markup=user_keyboard.cancel())
            bot.register_next_step_handler(message, lambda m: process_time(m, data))

    def process_pcs_quests(message: Message, data):
        bot.clear_step_handler(message)
        if message.text in ['/start', '❌ Відмінити']:
            start(message)
        else:
            data['pcsQuests'] = message.text
            bot.send_message(chat_id, f"Напишіть реєстраційний номер автомобіля", reply_markup=user_keyboard.cancel())
            bot.register_next_step_handler(message, lambda m: process_car(m, data))

    chat_id = message.chat.id
    client = users_function.get_client(chat_id)
    if not client['verification']:
        start(message)
    elif client['userBlock']:
        bot.send_message(chat_id, f"Ви заблоковані!", reply_markup=ReplyKeyboardRemove())
    else:
        bot.clear_step_handler(message)
        bot.send_message(chat_id,
                         f"Тепер можемо формувати заяву на дозвіл проїзду. Яку кількість гостей очікуєте?",
                         reply_markup=user_keyboard.cancel())
        bot.register_next_step_handler(message, lambda m: process_pcs_quests(m, {}))


@bot.message_handler(func=lambda m: m.text in ["Пропустити пішохода"] and m.from_user.id == m.chat.id)
def people(message: Message):
    def process_time(message: Message, data):
        bot.clear_step_handler(message)
        if message.text in ['/start', '❌ Відмінити']:
            start(message)
        else:
            data['time'] = message.text

            bot.send_message(chat_id, f"Ваша заява відправлена охороні! Вдалого дня)",
                             reply_markup=user_keyboard.main())

            client = users_function.get_client(chat_id)
            text = f"Пропустити пішохода! <a href='tg://user?id={chat_id}'>Написати</a>\n\n" \
                   f"Ім'я: {client['name']}\n" \
                   f"ІД: {chat_id}\n" \
                   f"Юзернейм: @{client['user_name']}\n" \
                   f"Вулиця: {client['street']}\n" \
                   f"Будинок: {client['house']}\n" \
                   f"Квартира: {client['apartment']}\n" \
                   f"К-сть гостей: {data['pcsQuests']}\n" \
                   f"Час: {data['time']}"

            users_function.create_request(user_id=chat_id, name=client['name'],
                                          first_name=client['first_name'], last_name=client['last_name'],
                                          user_name=client['user_name'],
                                          phone=client['phone'], street=client['street'], house=client['house'],
                                          apartment=client['apartment'], typeReq='Пропустити пішохода',
                                          pcsQuests=data['pcsQuests'],
                                          car=None, timeQuests=data['time'])

            try:
                bot.send_message(group_id, text, parse_mode='html')
            except:
                for admin_id in admins:
                    try:
                        bot.send_message(admin_id, text, parse_mode='html')
                    except:
                        pass

    def process_pcs_quests(message: Message, data):
        bot.clear_step_handler(message)
        if message.text in ['/start', '❌ Відмінити']:
            start(message)
        else:
            data['pcsQuests'] = message.text
            bot.send_message(chat_id, f"Орієнтовний час візиту гостей?", reply_markup=user_keyboard.cancel())
            bot.register_next_step_handler(message, lambda m: process_time(m, data))

    chat_id = message.chat.id
    client = users_function.get_client(chat_id)
    if not client['verification']:
        start(message)
    elif client['userBlock']:
        bot.send_message(chat_id, f"Ви заблоковані!", reply_markup=ReplyKeyboardRemove())
    else:
        bot.send_message(chat_id,
                         f"Тепер можемо формувати заяву для візиту Ваших гостей, скільки їх буде?",
                         reply_markup=user_keyboard.cancel())
        bot.clear_step_handler(message)
        bot.register_next_step_handler(message, lambda m: process_pcs_quests(m, {}))


@bot.message_handler(func=lambda m: m.text in ["Викликати охорону"] and m.from_user.id == m.chat.id)
def protection(message: Message):
    def process_phone(message: Message):
        bot.clear_step_handler(message)
        if message.text in ['/start', '❌ Відмінити']:
            start(message)
        else:
            try:
                print(message.contact.phone_number)
                users_function.update_column_clients(message.chat.id, column='phone',
                                                     value=message.contact.phone_number)
            except:
                users_function.update_column_clients(message.chat.id, column='phone', value=message.text)
            bot.send_message(chat_id, f"Ваша заява відправлена охороні! Поспішаємо на допомогу!",
                             reply_markup=user_keyboard.main())

            user = users_function.get_client(chat_id)
            text = f"Виклик охорони! <a href='tg://user?id={chat_id}'>Написати</a>\n\n" \
                   f"Ім'я: {user['name']}\n" \
                   f"ІД: {chat_id}\n" \
                   f"Юзернейм: @{user['user_name']}\n" \
                   f"Телефон: {user['phone']}\n"

            users_function.create_request(user_id=chat_id, name=user['name'],
                                          first_name=user['first_name'], last_name=user['last_name'],
                                          user_name=user['user_name'],
                                          phone=user['phone'], street=user['street'], house=user['house'],
                                          apartment=user['apartment'], typeReq='Виклик охорони')

            try:
                bot.send_message(group_id, text, parse_mode='html')
            except:
                for admin_id in admins:
                    try:
                        bot.send_message(admin_id, text, parse_mode='html')
                    except:
                        pass

    chat_id = message.chat.id
    client = users_function.get_client(chat_id)
    if not client['verification']:
        start(message)
    elif client['userBlock']:
        bot.send_message(chat_id, f"Ви заблоковані!", reply_markup=ReplyKeyboardRemove())
    else:
        bot.send_message(chat_id, f"Надішліть Ваш номер телефону і охорона зателефонує Вам для вирішення питання:",
                         reply_markup=user_keyboard.phone())
        bot.clear_step_handler(message)
        bot.register_next_step_handler(message, process_phone)

@bot.callback_query_handler(func=lambda c: c.data)
def callback(callback_query: telebot.types.CallbackQuery):
    print(callback_query.data)
    chat_id = callback_query.from_user.id
    message_id = callback_query.message.message_id
    # admin
    if 'hide' == callback_query.data:
        bot.delete_message(chat_id, message_id)
    elif 'acceptUser' in callback_query.data:
        user_id = callback_query.data.split('_')[1]
        bot.answer_callback_query(callback_query.id, f"Успішно підтверджено")
        try:
            bot.send_message(user_id, f"Вашу заяву прийнято! Тут ви можете подати заяву до нашої охорони",
                             reply_markup=user_keyboard.main())
            users_function.update_column_clients(user_id, column='verification', value=1)
        except:
            pass
        bot.edit_message_reply_markup(group_id, message_id, reply_markup=InlineKeyboardMarkup())

    elif 'declineUser' in callback_query.data:
        user_id = callback_query.data.split('_')[1]
        bot.answer_callback_query(callback_query.id, f"Успішно підтверджено")
        try:
            bot.send_message(user_id, f"Вашу заяву відхилено!")
            users_function.del_user(user_id)
        except:
            pass
        bot.edit_message_reply_markup(group_id, message_id, reply_markup=InlineKeyboardMarkup())


if __name__ == '__main__':
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print(e)
