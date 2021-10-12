import requests

class VKUser:

    def __init__(self, token, version='5.131'):
        self.params = {
            'access_token': token,
            'v': version
        }
with open('token_vk_user.txt', 'r', encoding='utf-8') as file_object:
    token = file_object.read().strip()

vk_client = VKUser(token, '5.131')

class UserName:

    url = 'https://api.vk.com/method/'

    def __init__(self, user_id):
        self.user_id = user_id

    def _get_user_name_from_user_id(self, user_id, name_case='Nom'):
        all_user_name_url = self.url + 'users.get'
        user_params = {
            'user_id': user_id,
            'name_case': name_case
        }
        res = requests.get(all_user_name_url, params={**vk_client.params, **user_params}).json()
        return res['response'][0]['first_name']
