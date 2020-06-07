import requests
from urllib.parse import urlencode
from pprint import pprint
from tqdm import tqdm
import time
import json

class Users:


    def __init__(self, username, user_id):
        self.username = username
        self.user_id = user_id

    def get_params(self):
        return {
            'access_token': '2d29bb4e6dd81c26dd01a7b5fdd0794ccc0481df3d05cf399fa32fa35e67b8889087e42e400894be7837e',
            'user_id': self.user_id,
            'v': '5.89'
        }

    def friends_list(self):     # Получить список друзей пользователя
        params = self.get_params()
        response = requests.get('https://api.vk.com/method/friends.get', params=params)
        return response.json()['response']['items']

    def get_groups_info(self):      #Вывести уникальные группы пользователя в виде словаря
        params = self.get_params()
        params['extended'] = 1
        params['v'] = 5.61
        params['fields'] = 'members_count'
        response = requests.get('https://api.vk.com/method/groups.get', params=params)
        response = response.json()['response']['items']
        groups_info_list = []
        for gid in self.find_unic_groups():
            for data in response:
                if data['id'] != gid:
                    continue
                elif data['id'] == gid:
                    try:
                        groups_info_list.append({
                            'gid': data['id'], 
                            'name': data['name'], 
                            'members_count': data['members_count']
                        })
                    except KeyError:
                        continue    
        return groups_info_list

    def get_groups_info_set(self):      #Множество групп пользователя
        params = self.get_params()
        params['extended'] = 1
        params['v'] = 5.61
        time.sleep(.5)
        response = requests.get('https://api.vk.com/method/groups.get', params=params)
        response = response.json()['response']['items']
        group_info_set = set()
        for data in response:
            group_info_set.add(data.setdefault('id'))
        return group_info_set

    def get_friends_groups(self):       # Создаем множество из групп друзей
        group_info_set = set()
        for friend_id in tqdm(self.friends_list()):
            time.sleep(0.5)
            params = self.get_params()
            params['extended'] = 1
            params['v'] = 5.61
            params['user_id'] = friend_id
            try:
                response = requests.get('https://api.vk.com/method/groups.get', params=params, timeout=5)
                response = response.json()['response']['items']
                for data in response:
                    for key, value in data.items():
                        if key == 'id':
                            group_info_set.add(value)
            except KeyError:
                continue
            except TimeoutError:
                time.sleep(2)
                return self.get_friends_groups()
        return group_info_set

    def find_unic_groups(self):     # Находим уникальные группы в которых нет друзей
        unic_groups = set()
        unic_groups = self.get_groups_info_set().difference(self.get_friends_groups())
        return unic_groups
        
    def friends_groups(self):       # Создаем список групп друзей
        friends_group_info_list = []
        for friend in tqdm(self.friends_list()):
            time.sleep(.5)
            params = self.get_params()
            params['extended'] = 1
            params['v'] = 5.61
            params['user_id'] = friend
            try:
                response = requests.get('https://api.vk.com/method/groups.get', params=params)
                response = response.json()['response']['items']
                for item in response:
                    friends_group_info_list.append(item['id'])
            except KeyError:
                continue        
        return friends_group_info_list

    def define_groups_with_friends(self, friend_limit=50):      #Показывать в том числе группы, в которых есть друзья, но не более, чем N человек, где N задается в коде.
        friends_groups = self.friends_groups()
        groups_with_friends = []
        for group_id in self.get_groups_info_set():
            quantity =  friends_groups.count(group_id)
            if quantity < friend_limit and quantity > 0:
                groups_with_friends.append({'group_id': group_id, 'friends_quantity': quantity})
            else:
                continue              
        return groups_with_friends

if __name__ == "__main__":
    User1 = Users('snusma.kuzmina', '4367825')        
    with open('groups.json', 'w', encoding='utf-8') as f:
        json.dump(User1.get_groups_info(), f, ensure_ascii=False, indent=4)
    print(User1.define_groups_with_friends(5))
