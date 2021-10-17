from random import randrange
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from VkBot import VkBot, load_queue, save_queue
from VKUser import UserName
import psycopg2


HOST = 'https://vk.com/id'

user_info = {}

def write_msg(user_id, message):
    vk.method('messages.send', {'user_id': user_id,
                                'message': message,
                                'random_id': randrange(10 ** 7)
                                })

with open('token_vk_bot.txt', 'r', encoding='utf-8') as file_object:
    token = file_object.read().strip()

vk = vk_api.VkApi(token=token)
longpoll = VkLongPoll(vk)

def check_info(event):
    bot = VkBot(event.user_id)
    ask = ''
    global user_info

    if user_info == {}:
        user_info[event.user_id] = bot._get_user_info_from_user_id(event.user_id)

    if user_info[event.user_id]['sex'] is None:
        write_msg(event.user_id, 'Укажите свой пол: ')
        ask = 'sex'

    if user_info[event.user_id]['city'] is None:
        write_msg(event.user_id, 'Укажите свой город: ')
        ask = 'city'

    if user_info[event.user_id]['year_of_birth'] is None or \
            len(user_info[event.user_id]['year_of_birth']) == 8 or \
            len(user_info[event.user_id]['year_of_birth']) == 10:
        write_msg(event.user_id, 'Укажи год своего рождения: ')
        ask = 'year_of_birth'

    if user_info[event.user_id]['status'] is None:
        write_msg(event.user_id, 'Укажите свой семейный статус: ')
        ask = 'status'

    return ask


def ask_logic(ask, event):
    if ask == 'sex':
        if event.text.lower().strip() in ['женщина', 'женский']:
            user_info[event.user_id]['sex'] = 1
        elif event.text.lower().strip() in ['мужчина', 'мужской']:
            user_info[event.user_id]['sex'] = 2

    if ask == 'year_of_birth':
        if event.text.lower().strip().isnumeric():
            user_info[event.user_id]['year_of_birth'] = int(event.text.lower().strip())

    if ask == 'status':
        if event.text.lower().strip() in ['не женат (не замужем)', 'не женат', 'не замужем']:
            user_info[event.user_id]['status'] = 1
        elif event.text.lower().strip() == 'встречается':
            user_info[event.user_id]['status'] = 2
        elif event.text.lower().strip() in ['помолвлен(-а)', 'помолвлен', 'помолвлена']:
            user_info[event.user_id]['status'] = 3
        elif event.text.lower().strip() in ['женат (замужем)', 'женат', 'замужем']:
            user_info[event.user_id]['status'] = 4
        elif event.text.lower().strip() == 'всё сложно':
            user_info[event.user_id]['status'] = 5
        elif event.text.lower().strip() == 'в активном поиске':
            user_info[event.user_id]['status'] = 6
        elif event.text.lower().strip() in ['влюблен(-а)', 'влюблен', 'влюблена']:
            user_info[event.user_id]['status'] = 7
        elif event.text.lower().strip() == 'встречается':
            user_info[event.user_id]['в гражданском браке'] = 8

    if ask == 'city':
        city = event.user_id.text.lower().strip()
        if city is not None:
            user_info[event.user_id]['city'] = city
        else:
            write_msg(event.user_id, "Неизвестный город(или не в России)")

    if ask == 'sex' and user_info[event.user_id]['sex'] is not None:
        ask = ''
    if ask == 'age' and user_info[event.user_id]['age'] is not None:
        ask = ''
    if ask == 'city' and user_info[event.user_id]['city'] is not None:
        ask = ''
    if ask == 'status' and user_info[event.user_id]['status'] is not None:
        ask = ''

    return ask

def return_photos(event):
    bot = VkBot(event.user_id)
    result, dict_queue2 = bot.get_photos()

    list_id = []
    for item in result:
        list_id.append(item['owner_id'])
        write_msg(event.user_id, f"Ссылки на фото: {item['photo_url']} \n"
                                 f"Ссылка на профиль: {HOST + str(item['owner_id'])}")
        insert_data(str(event.user_id), str(item['owner_id']))

    if event.user_id in dict_queue2.keys():
        dict_queue2[event.user_id].extend(list_id)
    else:
        dict_queue2[event.user_id] = list_id

    save_queue(dict_queue2)


def pull():

    load_queue()

    check = ''
    for event in longpoll.listen():

        if event.type == VkEventType.MESSAGE_NEW:

            if event.to_me:

                welcome_commands = [
                    'ПРИВЕТ', 'Привет', 'Hi', 'Здравствуй',
                    'хай', 'Хай', 'Здаров', 'Приветики', 'Ещё', 'Другую',
                    'Другого', 'Погнали'
                ]

                bye_commands = [
                    'ПОКА', 'Пока', 'Bye', 'До свидания',
                    'бай', 'Покеда', 'Ой, ну все', 'Пока-пока',
                    'нет', 'Нет', 'НЕТ', 'NO', 'no', 'No'
                ]

                vk_user = UserName(event.user_id)

                if event.text in welcome_commands:

                    write_msg(event.user_id, f"Хай, {vk_user._get_user_name_from_user_id(event.user_id)}, "
                                             f"я чат-бот!\n")

                    check = check_info(event)

                    if check == '':
                        return_photos(event)

                elif event.text in bye_commands:
                    write_msg(event.user_id,
                              f"Жаль прощаться с тобой, {vk_user._get_user_name_from_user_id(event.user_id)}.\n"
                              f"Пока, до скорых встреч!")

                else:
                    if check in ['sex', 'city', 'age', 'status']:
                        check = ask_logic(check, event)
                    else:
                        write_msg(event.user_id, "Не поняла вашего ответа...")

                    if check == '':
                        return_photos(event)

def get_all_data():
    conn = psycopg2.connect(dbname='vk', user='', password='', host='127.0.0.1')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM vk')
    records = cursor.fetchall()
    cursor.close()
    conn.close()

    return records

def get_data_by_user(user_id):
    conn = psycopg2.connect(dbname='vk', user='', password='', host='127.0.0.1')
    cursor = conn.cursor()
    cursor.execute(f'SELECT couple_id FROM vk WHERE user_id = \'{user_id}\'')
    result = [r[0] for r in cursor.fetchall()]
    cursor.close()
    conn.close()

    return result

def insert_data(user_id, couple_id):
    conn = psycopg2.connect(dbname='vk', user='', password='', host='127.0.0.1')
    cursor = conn.cursor()
    cursor.execute(f'INSERT INTO vk(user_id,couple_id) VALUES (\'{user_id}\',\'{couple_id}\')')
    conn.commit()
    cursor.close()
    conn.close()

