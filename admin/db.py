import sqlite3

def get_workers(type_worker):
    conn = sqlite3.connect('db/data.db')
    c = conn.cursor()
    c.execute('select user_id, name from clients where typeWorker=(?)', (type_worker,))
    return c.fetchall()


def set_type_worker(user_id, type_worker):
    conn = sqlite3.connect('db/data.db')
    c = conn.cursor()
    c.execute(f'update clients set typeWorker=(?) where user_id=(?)', (type_worker, user_id))
    conn.commit()


def add_new_type_work(name):
    conn = sqlite3.connect('db/data.db')
    c = conn.cursor()
    c.execute("insert into typesWork (name) values (?)", (name,))
    conn.commit()

