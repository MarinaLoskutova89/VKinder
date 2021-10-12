import requests
import datetime
from VKUser import vk_client
from functools import cmp_to_key
import compare

dict_queue = {}
user_info = {}

class VkBot:

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

        user_info[user_id] = {
            'first_name': user_first_name, 'sex': user_gender,
            'city': user_city, 'year_of_birth': year_of_birth,
            'age': user_age, 'status': user_relation
        }
        return user_info[user_id]

    def _search_a_couple_for_user(self, count=10):
        date_list = []
        user_info = self._get_user_info_from_user_id(self.user_id)
        all_couples_for_user_url = self.url + 'users.search'
        user_params = {
            'count': count,
            'fields': 'sex',
            'has_photo': 1,
            'is_closed': 0,
            'birth_year': user_info['year_of_birth'],
            'hometown': user_info['city'],
            'status': user_info['status']
        }
        couples_res = requests.get(all_couples_for_user_url, params={**vk_client.params, **user_params}).json()

        for user in couples_res['response']['items']:

            if user['is_closed'] == True:
                continue

            if user['id'] in dict_queue:
                continue

            if user['sex'] != user_info['sex'] and user['sex'] != 0:
                date_list.append(user['id'])
        return date_list

    def get_photos(self, count=3):
        couples = self._search_a_couple_for_user()

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

            return final_info
