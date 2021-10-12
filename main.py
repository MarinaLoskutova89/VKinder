from random import randrange
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from VkBot import VkBot, user_info, dict_queue
from VKUser import UserName
import json
import os.path


def load_queue():
    if os.path.isfile('vk_queue_db.json'):
        dict_q = json.load(open('vk_queue_db.json', 'r', encoding='utf-8'))
        return dict_q
    else:
        save_queue()
        return {}

def save_queue():
    json.dump(dict_queue, open('vk_queue_db.json', 'w', encoding='utf-8'))

def write_msg(user_id, message):
    vk.method('messages.send', {'user_id': user_id,
                                'message': message,
                                'random_id': randrange(10 ** 7)
                                })

with open('token_vk_bot.txt', 'r', encoding='utf-8') as file_object:
    token = file_object.read().strip()

vk = vk_api.VkApi(token=token)
longpoll = VkLongPoll(vk)
ask = ''


def check_info():
    bot = VkBot(event.user_id)
    user_info = bot._get_user_info_from_user_id(event.user_id)

    if user_info['sex'] == None:
        write_msg(event.user_id, 'Укажите свой пол: ')
        ask = 'sex'
        return ask

    if user_info['city'] == None:
        write_msg(event.user_id, 'Укажите свой город: ')
        ask = 'city'
        return ask

    if user_info['year_of_birth'] == None or len(user_info['year_of_birth']) == 8 or len(user_info['year_of_birth']) == 10:
        write_msg(event.user_id, 'Укажи год своего рождения: ')
        ask = 'year_of_birth'
        return ask

    if user_info['status'] == None:
        write_msg(event.user_id, 'Укажите свой семейный статус: ')
        ask = 'status'
        return ask


def ask_logic():
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
        elif event.textt.lower().strip() in ['влюблен(-а)', 'влюблен', 'влюблена']:
            user_info[event.user_id]['status'] = 7
        elif event.text.lower().strip() == 'встречается':
            user_info[event.user_id]['в гражданском браке'] = 8

    if ask == 'city':
        city = event.text.lower().strip()
        if city != None:
            user_info[event.user_id]['city'] = city
        else:
            write_msg(event.user_id, "Неизвестный город(или не в России)")

    if ask == 'sex' and user_info[event.user_id]['sex'] != None:
        ask == ''
    if ask == 'age' and user_info[event.user_id]['age'] != None:
        ask == ''
    if ask == 'city' and user_info[event.user_id]['city'] != None:
        ask == ''
    if ask == 'status' and user_info[event.user_id]['status'] != None:
        ask == ''


if __name__ == '__main__':
    dict_queue = load_queue()

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
                HOST = 'https://vk.com/id'

                if event.text in welcome_commands:
                    bot = VkBot(event.user_id)
                    write_msg(event.user_id, f"Хай, {vk_user._get_user_name_from_user_id(event.user_id)}, я чат-бот!\n")

                    check_info()

                    if ask in ['sex', 'city', 'age', 'status']:
                        ask_logic()
                    else:
                        pass

                    result = bot.get_photos()

                    write_msg(event.user_id, f"Ссылки на фото: {result['photo_url']} \n"
                                             f"Ссылка на профиль: {HOST + str(result['owner_id'])}")

                    dict_queue = {'user_id': event.user_id,
                                  'couple_id': result['owner_id']}

                    save_queue()


                elif event.text in bye_commands:
                    write_msg(event.user_id, f"Жаль прощаться с тобой, {vk_user._get_user_name_from_user_id(event.user_id)}.\n"
                                             f"Пока, до скорых встреч!")

                else:
                    write_msg(event.user_id, "Не поняла вашего ответа...")
