import sqlite3
import sys
import time
import telebot
from telebot.types import *
from admin import db as db_admin
import config as config
import users_function
from config import token, admins
from admin import keyboards as admin_keyboards
import keyboards
from telebot import types

bot = telebot.TeleBot(token, threaded=False)
sys.setrecursionlimit(10 ** 6)
conn = sqlite3.connect("db/data.db")
conn_user = sqlite3.connect("db/users.db")

@bot.message_handler(commands=["admin"], func=lambda m: m.from_user.id == m.chat.id and m.from_user.id in config.admins)
def admin_command(message: Message):
    user_id = message.chat.id
    bot.send_message(user_id, 'Админ меню', reply_markup=admin_keyboards.main())

@bot.message_handler(commands=["start"], func=lambda m: m.from_user.id == m.chat.id)
def start(message: Message):
    user_id = message.chat.id
    chat_id = message.chat.id

    c_user = conn_user.cursor()
    c = conn.cursor()

    if c_user.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone() is None:
        c_user.execute("INSERT INTO users (user_id, state) VALUES (?, ?)", (user_id, 0))
        conn_user.commit()

    if c.execute("SELECT * FROM clients WHERE user_id = ?", (user_id,)).fetchone() is None:
        username = message.from_user.username
        last_name = message.from_user.last_name
        first_name = message.from_user.first_name
        c.execute("INSERT INTO clients (user_id, user_name, last_name, dataReq, first_name) VALUES (?, ?, ?, ?, ?)",
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
                    bot.send_message(config.group_id, text, parse_mode='html',
                                 reply_markup=InlineKeyboardMarkup().row(
                                     InlineKeyboardButton(text='✅', callback_data=f'acceptUser_{chat_id}')
                                 ).row(
                                     InlineKeyboardButton(text='❌', callback_data=f'declineUser_{chat_id}')
                                 ))
                except:
                    pass
        else:
            bot.send_message(chat_id, f"Не вірні данні")

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
                         reply_markup=keyboards.main())

@bot.message_handler(
    func=lambda m: m.text in ["👨🏼‍💻Admin Panel", '🗂 Вигрузити БД', '📊 Статистика', 'Заблокувати', 'Перезаписати',
                              'Розблокувати', 'Заявки'] and (m.chat.id in admins)
                   and m.from_user.id == m.chat.id)
def admin_panel(message: Message):
    chat_id = message.chat.id
    print(message.text)
    if message.text == "👨🏼‍💻Admin Panel":
        bot.send_message(chat_id=message.chat.id,
                         text="Авторизировались как Admin",
                         reply_markup=admin_keyboards.main())

    elif message.text == '📊 Статистика':
        conn = sqlite3.connect("db/users.db")
        c = conn.cursor()
        lively = c.execute("""SELECT COUNT(*) FROM users where lively = ('block')""").fetchone()[0]
        allusers = c.execute("""SELECT COUNT(*) FROM users""").fetchone()[0]
        c.close()
        text = "🙂 *Кількість користувачів* {0}\n" \
               "*% від числа всіх:* {1}%\n" \
               "*💩 Кількість заблокованих:* {2}\n".format(
            str(allusers), str(round(lively / allusers * 100, 2)), str(lively), )
        bot.send_message(message.chat.id, text, parse_mode='Markdown')

    elif message.text == '🗂 Вигрузити БД':
        bot.send_message(message.chat.id, "Процес вигрузки ...")
        bot.send_document(message.chat.id, users_function.get_DB(), caption=f"База користувачів")
        bot.send_document(message.chat.id, users_function.get_requests_DB(), caption=f"База запитів")
 
    elif message.text == 'Заявки':
        bot.send_message(message.chat.id, text='<a href="google.com">Відкрити заявки</a>', parse_mode='HTML')

    elif message.text == 'Заблокувати':
        def process_block_user(message: Message):
            bot.clear_step_handler(message)
            if message.text in ['/start', '❌ Відмінити']:
                bot.send_message(chat_id, f"Відміна", reply_markup=admin_keyboards.main())
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
                                     reply_markup=admin_keyboards.main())
            else:
                bot.send_message(chat_id, f"Не вірний формат. Спробуйте ще раз!", reply_markup=admin_keyboards.main())

        bot.send_message(chat_id, f"Введіть user_id користувача, якого бажаєте заблокувати\n"
                                  f"Приклад вводу: 1068853244\n\n"
                                  f"<code> * user_id Ви можете отримати при вигрузці бази даних з користувачами</code>",
                         parse_mode='HTML', reply_markup=keyboards.cancel())
        bot.clear_step_handler(message)
        bot.register_next_step_handler(message, process_block_user)

    elif message.text == 'Розблокувати':
        def process_unblock_user(message: Message):
            bot.clear_step_handler(message)
            if message.text in ['/start', '❌ Відмінити']:
                bot.send_message(chat_id, f"Відміна", reply_markup=admin_keyboards.main())
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
                                     reply_markup=admin_keyboards.main())
            else:
                bot.send_message(chat_id, f"Не вірний формат. Спробуйте ще раз!", reply_markup=admin_keyboards.main())

        bot.send_message(chat_id, f"Введіть user_id користувача, якого бажаєте розблокувати\n"
                                  f"Приклад вводу: 1068853244\n\n"
                                  f"<code> * user_id Ви можете отримати при вигрузці бази даних з користувачами</code>",
                         parse_mode='HTML', reply_markup=keyboards.cancel())
        bot.clear_step_handler(message)
        bot.register_next_step_handler(message, process_unblock_user)

    elif message.text == 'Перезаписати':
        def process_rewrite(message: Message):
            bot.clear_step_handler(message)
            if message.text in ['/start', '❌ Відмінити']:
                bot.send_message(chat_id, f"Відміна", reply_markup=admin_keyboards.main())
            elif str(message.text).isnumeric():
                client_id = message.text
                client = users_function.get_client(client_id)
                if client:
                    bot.send_message(chat_id, f"Користувача {client['name']} успішно видалено щоб він перезаписався!")
                    users_function.del_user(client_id)

                    try:
                        bot.send_message(chat_id=client_id, text=f"Ваш обліковий запис було видалено! Натисніть /start щоб оновити дані")
                    except:
                        pass
                else:
                    bot.send_message(chat_id, f"Такого користувача не знайдено. Спробуйте ще раз!",
                                     reply_markup=admin_keyboards.main())
            else:
                bot.send_message(chat_id, f"Не вірний формат. Спробуйте ще раз!", reply_markup=admin_keyboards.main())

        bot.send_message(chat_id, f"Введіть user_id користувача, якого бажаєте перезаписати\n"
                                  f"Приклад вводу: 1068853244\n\n"
                                  f"<code> * user_id Ви можете отримати при вигрузці бази даних з користувачами</code>",
                         parse_mode='HTML', reply_markup=keyboards.cancel())
        bot.clear_step_handler(message)
        bot.register_next_step_handler(message, process_rewrite)


@bot.message_handler(func=lambda m: m.text in ["Пропустити автомобіль"] and m.from_user.id == m.chat.id)
def car(message: Message):
    def process_time(message: Message, data):
        bot.clear_step_handler(message)
        if message.text in ['/start', '❌ Відмінити']:
            start(message)
        else:
            data['time'] = message.text
            bot.send_message(chat_id, f"Ваша заявка сформована! Вдалого дня)",
                             reply_markup=keyboards.main())

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
                bot.send_message(config.group_id, text, parse_mode='html')
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
            bot.send_message(chat_id, f"Який орієнтовний час прибуття гостей?", reply_markup=keyboards.cancel())
            bot.register_next_step_handler(message, lambda m: process_time(m, data))

    def process_pcs_quests(message: Message, data):
        bot.clear_step_handler(message)
        if message.text in ['/start', '❌ Відмінити']:
            start(message)
        else:
            data['pcsQuests'] = message.text
            bot.send_message(chat_id, f"Напишіть реєстраційний номер автомобіля", reply_markup=keyboards.cancel())
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
                         f"Тепер можемо формувати заявку на дозвіл проїзду. Яку кількість гостей очікуєте?",
                         reply_markup=keyboards.cancel())
        bot.register_next_step_handler(message, lambda m: process_pcs_quests(m, {}))


@bot.message_handler(func=lambda m: m.text in ["Пропустити пішохода"] and m.from_user.id == m.chat.id)
def people(message: Message):
    def process_time(message: Message, data):
        bot.clear_step_handler(message)
        if message.text in ['/start', '❌ Відмінити']:
            start(message)
        else:
            data['time'] = message.text

            bot.send_message(chat_id, f"Ваша заявка сформована! Вдалого дня)",
                             reply_markup=keyboards.main())

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
                bot.send_message(config.group_id, text, parse_mode='html')
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
            bot.send_message(chat_id, f"Орієнтовний час прибуття гостей?", reply_markup=keyboards.cancel())
            bot.register_next_step_handler(message, lambda m: process_time(m, data))


    chat_id = message.chat.id
    client = users_function.get_client(chat_id)
    if not client['verification']:
        start(message)
    elif client['userBlock']:
        bot.send_message(chat_id, f"Ви заблоковані!", reply_markup=ReplyKeyboardRemove())
    else:
        bot.send_message(chat_id,
                         f"Тепер можемо формувати заявку на дозвіл проходу для Ваших гостей, а скільки їх буде?",
                         reply_markup=keyboards.cancel())
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
            bot.send_message(chat_id, f"Ваша заявка сформована! Поспішаємо на допомогу!",
                             reply_markup=keyboards.main())

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
                bot.send_message(config.group_id, text, parse_mode='html')
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
        bot.send_message(chat_id, f"Напишіть Ваш номер телефону і охорона зателефонує Вам для вирішення питання:",
                         reply_markup=keyboards.phone())
        bot.clear_step_handler(message)
        bot.register_next_step_handler(message, process_phone)

@bot.message_handler()
def group_some(message: Message):
    start(message)

if __name__ == '__main__':
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print(e)
    