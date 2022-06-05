import requests
from pprint import pprint
import time
import os
import json
import copy

class VkPhoto:
    url_general = 'https://api.vk.com/method/'
    base_path = 'Photos_vk'
    url_ya = 'https://cloud-api.yandex.net/v1/disk/resources'

    def __init__(self, id_vk, token_vk, token_ya):
        self.id_vk = id_vk
        self.folder = str(id_vk)
        self.token_vk = token_vk
        self.token_ya = token_ya
        self.params_vk = {
            'user_ids': id_vk,
            'access_token': token_vk,
            'v': '5.131'
        }
        self.headers_ya = {
            'Content-Type': 'application/json',
            'Authorization': 'OAuth {}'.format(self.token_ya)
        }

    def find_id(self):
        url_users_get = self.url_general + 'users.get'

        response = requests.get(url_users_get, self.params_vk).json()
        id_vk_res = response['response'][0]['id']

        return id_vk_res


    def photos_get(self, album_id='profile', number_photos=5):

        try:
            int(self.id_vk)
        except ValueError:
            self.id_vk = self.find_id()

        url_get = self.url_general + 'photos.get'
        get_params = {
            'owner_id': self.id_vk,
            'photo_sizes': 1,
            'count': number_photos,
            'album_id': album_id,
            'extended': 1
        }

        response = requests.get(url_get, params={**self.params_vk, **get_params}).json()['response']['items']

        biggest_photos_list = []
        for item in response:
            biggest_photo_dict = {}
            max_width = 0
            max_height = 0

            for photo in item['sizes']:
                if photo['height'] > max_height and photo['width'] > max_width:
                    max_height = photo['height']
                    max_width = photo['width']
                    url_biggest_photo = photo['url']
                    type_big = photo['type']
            biggest_photo_dict = {
                'url': url_biggest_photo,
                'size': type_big,
                'file_name': str(item['likes']['count']) + '.jpg'
            }
            biggest_photos_list.append(biggest_photo_dict)

        return biggest_photos_list

    def send_photo_ya(self, photos_list):
        path_folder = f'{self.base_path}/{str(self.folder)}'

        response = requests.put(self.url_ya, headers=self.headers_ya, params={'path': path_folder})  # создаем папку

        if response.status_code == 201:
            print(f'Папка " {self.folder} " создана успешно')
        elif response.status_code == 409:
            print(f'Папка " {self.folder} " уже есть')
        else:
            return
        print('Загружаем файлы на Яндекс-диск:')
        for photo in photos_list:
            path_file = f'{path_folder}/{photo["file_name"]}'
            params = {
                'url': photo['url'],
                'path': path_file
            }

            url_up = f'{self.url_ya}/{"upload"}'
            response = requests.post(url_up, headers=self.headers_ya, params=params)
            print('*', end=' ')
            time.sleep(1)
        print()
        return

    def create_json(self, photos_list):
        photos_list_copy = copy.deepcopy(photos_list)
        base_path = os.getcwd()
        path_json = os.path.join(base_path, 'logs', self.folder + '.json')

        for photo in photos_list_copy:
            del photo['url']

        with open(path_json, 'w') as file_write:
            json.dump(photos_list_copy, file_write)
        return print(f'json-файл для " {self.folder} " создан\n')

def read_token(object):
    with open('token.txt') as file_object:
        for list in file_object:
            if list.split('|')[0].strip() == object:
                token = list.split('|')[1].strip()
                return token
    return print('Такого токена нет')

if __name__ == '__main__':

    token_vk = read_token('vk')
    token_ya = read_token('ya')
    token_ = read_token('y')

    begemot_korovin = VkPhoto('begemot_korovin', token_vk, token_ya)
    photos = begemot_korovin.photos_get()
    begemot_korovin.send_photo_ya(photos)
    begemot_korovin.create_json(photos)
    # pprint(photos)

    sergeg00d = VkPhoto(42721846, token_vk, token_ya)
    photos = sergeg00d.photos_get()
    sergeg00d.send_photo_ya(photos)
    sergeg00d.create_json(photos)
    # pprint(photos)