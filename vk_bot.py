#!/usr/bin/python3
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard
from  random import randint
import os

class MyVkBot(vk_api.VkApi):
    def __init__(self, key_file_path:str, path_foldeg_imgs:str, words_file_path:str) -> None:
        api_key = self._get_api_key(key_file_path)
        super().__init__(token=api_key)

        print('Старт загрузки картинок...')
        self.imgs = self._load_defaul_img(path_foldeg_imgs, words_file_path)
        print('Картинки загружены.')

    def _load_defaul_img(self, path_foldeg_imgs:str, words_file_path:str) -> dict:
        upload = vk_api.VkUpload(self)
        imgs = dict()
        with open(words_file_path, 'r', encoding='utf-8') as f:
            words = [i[:-1].split('\t') for i in f.readlines()]
        words = dict(zip([i[0] for i in words], [i[1].split(' ') for i in words]))
        for im in os.listdir(path_foldeg_imgs):
            num = im.split('.')[0]
            photo = upload.photo_messages(os.path.join(path_foldeg_imgs, im))
            attachment = f'photo{photo[0]["owner_id"]}_{photo[0]["id"]}_{photo[0]["access_key"]}'
            words_im = words[im]
            imgs.update({num:{'attachment':attachment, 'words':words_im}})
        return imgs

    def _get_api_key(self, path:str) -> str:
        with open(path, 'r', encoding='utf-8') as f:
            api_key = f.read()
        return api_key

    def _send_text_msg(self, user_id:str, message:str, keyboard:object = None) -> None:
        if keyboard:
            self.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': randint(99999, 999999), 'keyboard': keyboard})
        else:
            self.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': randint(99999, 999999)})

    def _send_images(self, user_id:str, images_attachment:list) -> None:
        self.method("messages.send", {'user_id': user_id, 'message': '' , 'attachment': ','.join(images_attachment), 'random_id': randint(99999, 999999)})

    def _get_random_cards(self, count_cards:int) -> dict:
        cards = dict()
        for i in range(count_cards):
            nums_imgs = list(self.imgs.keys())
            rand_int = randint(0, len(nums_imgs)-1)
            cards.update({nums_imgs[rand_int]: self.imgs[nums_imgs[rand_int]]})
            del self.imgs[nums_imgs[rand_int]]
        return cards
    
    def _make_word(self, cards:dict) -> tuple:
        words = [i['words'] for i in cards.values()]
        word_make = set(words[0])
        for word in words[1:]:
            word_make = word_make ^ set(word)
        result_word = list(word_make)[0]
        for num in cards.keys():
            if result_word in cards[num]['words']:
                return (result_word, num)
        return (None,)

    def main_circle(self) -> None:
        longpoll = VkLongPoll(self)
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                if event.to_me:
                    request = event.text
                    if request == "Старт":
                        user_score = {str(event.user_id):0}
                        cards = self._get_random_cards(5)
                        self._send_images(event.user_id, [i['attachment'] for i in cards.values()])
                        word = self._make_word(cards)
                        if word[0]:
                            keyboard = VkKeyboard(one_time=True, inline=False)
                            for num_img in cards.keys():
                                keyboard.add_button(num_img)
                            self._send_text_msg(event.user_id, f'Угадайте картинку по её описнанию: {word[0]}', keyboard.get_keyboard())
                    elif request in cards.keys():
                        if request == word[1]:
                            user_score[str(event.user_id)] += 3
                            self._send_text_msg(event.user_id, f'Ваш счет: {str(user_score[str(event.user_id)])}')
                        else:
                            self._send_text_msg(event.user_id, f'За этот ход баллов набрано не было. (')

                    else:
                        self._send_text_msg(event.user_id, "Упс, что-то пошло не так. =(")


if __name__ == "__main__":
    bot = MyVkBot('api.txt', '/home/slawa/HDD/my_scripts/my_bots/vk_bot/imgs', '/home/slawa/HDD/my_scripts/my_bots/vk_bot/words.txt')
    bot.main_circle()