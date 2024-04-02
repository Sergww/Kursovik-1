import requests
from pprint import pprint
import time
import os
import json
import copy
from datetime import datetime
from datetime import date

TOKEN_VK = ''
TOKEN_YA = ''

class YaDisk:
    home_path = os.getcwd()
    url_ya = 'https://cloud-api.yandex.net/v1/disk/resources'
    base_path = 'Photos_vk'

    def create_log(self, existence, flag=0):
        path_log = os.path.join(self.home_path, 'logs/logs.txt')
        if flag == 1:
            print(existence)
        with open(path_log, 'a', encoding='utf-8') as file_write:
            result = f'{datetime.now()} | {existence}\n'
            file_write.write(result)
        print('*', end=' ')
        time.sleep(0.1)

    def send_photo_ya(self, photos_list):
        path_folder = f'{self.base_path}/{str(self.folder)}'

        response = requests.put(self.url_ya, headers=self.headers_ya, params={'path': path_folder})  # создаем папку

        if response.status_code == 201:
            self.create_log(f'Папка " {self.folder} " создана успешно')
        elif response.status_code == 409:
            self.create_log(f'Папка " {self.folder} " уже есть')
        else:
            return
        self.create_log('Загружаем файлы на Яндекс-диск:')
        for photo in photos_list:
            path_file = f'{path_folder}/{photo["file_name"]}'
            params = {
                'url': photo['url'],
                'path': path_file
            }

            url_up = f'{self.url_ya}/{"upload"}'
            requests.post(url_up, headers=self.headers_ya, params=params)
            self.create_log(f'{photo["file_name"]} загружен в папку "{self.folder}"', 0)

    def create_json(self, photos_list):
        photos_list_copy = copy.deepcopy(photos_list)
        path_json = os.path.join(self.home_path, 'logs', self.folder + '.json')

        for photo in photos_list_copy:
            del photo['url']

        with open(path_json, 'w') as file_write:
            json.dump(photos_list_copy, file_write)

        return self.create_log(f'json-файл для " {self.folder} " создан\n')


class VkPhoto(YaDisk):
    url_general = 'https://api.vk.com/method/'

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
        self.create_log(f'Экземпляр класса для аккаунта "{self.id_vk}" создан')

    def find_id(self):
        url_users_get = self.url_general + 'users.get'
        response = requests.get(url_users_get, self.params_vk).json()
        id_vk_res = response['response'][0]['id']

        return id_vk_res


    def photos_get(self, album_id='profile', number_photos=5):

        try:
            int(self.id_vk)
            self.create_log(f'аккаунт " {self.id_vk} " переводить в числовой вид не надо')
        except ValueError:
            self.create_log(f'Переводим аккаунт " {self.id_vk} " в числовой вид')
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
        self.create_log(f'Создаем список файлов для загрузки на яндекс-диск:')
        biggest_photos_list = []
        likes_list = []
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

            if item['likes']['count'] in likes_list:
                file_name = str(item['likes']['count']) + '-' + str(date.today()) + '.jpg'
            else:
                file_name = str(item['likes']['count']) + '.jpg'

            likes_list.append(item['likes']['count'])

            biggest_photo_dict = {
                'url': url_biggest_photo,
                'file_name': file_name,
                'size': type_big

            }
            self.create_log(f'файл {file_name} добавлен в список')
            biggest_photos_list.append(biggest_photo_dict)

        return biggest_photos_list

if __name__ == '__main__':

    begemot_korovin = VkPhoto('begemot_korovin', TOKEN_VK, TOKEN_YA)
    photos = begemot_korovin.photos_get()
    begemot_korovin.send_photo_ya(photos)
    begemot_korovin.create_json(photos)

    sergeg00d = VkPhoto(42721846, TOKEN_VK, TOKEN_YA)
    photos = sergeg00d.photos_get()
    sergeg00d.send_photo_ya(photos)
    sergeg00d.create_json(photos)
    print(f'\nВыводится для примера json-файл для "{begemot_korovin.folder}":')
    with open('logs/begemot_korovin.json', encoding='utf-8') as f:
        templates = json.load(f)
    pprint(templates)
