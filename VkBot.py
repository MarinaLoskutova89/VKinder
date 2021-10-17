import requests
import datetime
import time
from VKUser import vk_client
from functools import cmp_to_key
import compare
import json
import os.path

dict_queue = {}


def load_queue():
    global dict_queue
    if os.path.isfile('vk_queue_db.json'):
        dict_queue = json.load(open('vk_queue_db.json', 'r', encoding='utf-8'))
    else:
        save_queue(dict_queue)

    return dict_queue


def save_queue(queue):
    json.dump(queue, open('vk_queue_db.json', 'w', encoding='utf-8'))

class VkBot:
    info = {}

    url = 'https://api.vk.com/method/'

    def __init__(self, user_id):
        self.user_id = user_id

    def _get_user_info_from_user_id(self, user_id):
        all_user_info_url = self.url + 'users.get'
        user_params = {
            'user_id': user_id,
            'fields': 'bdate, city, relation, sex'
        }
        info_res = requests.get(all_user_info_url, params={**vk_client.params, **user_params}).json()

        info = info_res['response'][0]
        user_first_name = info['first_name']

        if 'city' not in info:
            user_city = None
        else:
            user_city = info['city']['title']

        if 'relation' not in info:
            user_relation = None
        else:
            user_relation = info['relation']

        if 'sex' not in info:
            user_gender = None
        else:
            user_gender = info['sex']

        if 'bdate' not in info:
            year_of_birth = None
            user_age = None
        else:
            year_of_birth = info['bdate'][-4:]

            now = datetime.datetime.now()
            user_age = now.year - int(year_of_birth)

        info[user_id] = {
            'first_name': user_first_name, 'sex': user_gender,
            'city': user_city, 'year_of_birth': year_of_birth,
            'age': user_age, 'status': user_relation
        }
        return info[user_id]

    def _search_a_couple_for_user(self):
        date_list = []
        user_info = self._get_user_info_from_user_id(self.user_id)
        all_couples_for_user_url = self.url + 'users.search'
        user_params = {
            'count': 1000,
            'fields': 'sex',
            'has_photo': 1,
            'is_closed': 0,
            'birth_year': user_info['year_of_birth'],
            'hometown': user_info['city'],
            'status': user_info['status']
        }
        couples_res = requests.get(all_couples_for_user_url, params={**vk_client.params, **user_params}).json()

        i = 0
        for user in couples_res['response']['items']:
            if i > 10:
                break

            if str(self.user_id) in dict_queue:
                x = dict_queue[str(self.user_id)]
                if user['id'] in x:
                    continue

            if user['is_closed'] == True:
                continue

            if user['sex'] != user_info['sex'] and user['sex'] != 0:
                date_list.append(user['id'])
                i = i + 1

            dict_queue[str(self.user_id)].append(user['id'])

        return date_list, dict_queue

    def get_photos(self, count=3):
        couples, dict_queue = self._search_a_couple_for_user()

        list_u = []

        for owner_id in couples:

            all_photos_url = self.url + 'photos.get'
            photos_params = {
                'owner_id': owner_id,
                'album_id': 'profile',
                'extended': 1,
                'photo_sizes': 1,
                'count': count
            }
            res = requests.get(all_photos_url, params={**vk_client.params, **photos_params}).json()

            time.sleep(1)

            photo_list = []
            photo = []
            for item in res['response']['items']:
                photo_list.append({'owner_id': item['owner_id'],
                                   'media_id': item['id'],
                                   'likes': item['likes']['count'],
                                   'comments': item['comments']['count'],
                                   'url': item['sizes']})

            pop_photo = sorted(photo_list, key=lambda x: (x['likes'], x['comments']), reverse=True)[0:3]
            for i in pop_photo:
                max_photo_sorted = sorted(i['url'], key=cmp_to_key(compare.compare), reverse=True)[0]['url']
                photo.append(max_photo_sorted)

                final_info = {
                    'user_id': self.user_id,
                    'owner_id': i['owner_id'],
                    'photo_url': photo
                }

            list_u.append(final_info)

        return list_u, dict_queue