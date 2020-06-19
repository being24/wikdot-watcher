#!/usr/bin/env python
# coding: utf-8

import configparser
import logging
import pathlib
import time

import requests


class webhook():
    def __init__(self):
        # URLと名前、URLを外部から読み込む
        READ_SECTION = 'DEFAULT'

        data_path = pathlib.Path(__file__).parent
        data_path /= '../data'
        data_path = str(data_path.resolve())

        config = configparser.RawConfigParser()
        config.read(data_path + '/config.ini', encoding='utf-8')

        self.USERNAME = config[READ_SECTION]['name']
        self.AVATOR_URL = config[READ_SECTION]['avatar_url']
        self.WEBHOOK_URL = config[READ_SECTION]['WEBHOOK_URL']

    def gen_webhook_msg(self, content):
        msg = {
            "username": self.USERNAME,
            "avatar_url": self.AVATOR_URL,
            "content": content}
        return msg

    def send_webhook(self, msg):
        msg = msg or None

        if msg is None or "":
            logging.error("can't send blank msg")
            return -1

        if len(msg) >= 2000:
            logging.error('msg too long!')
            logging.error(msg)
            return -1

        main_content = self.gen_webhook_msg(msg)

        while True:
            response = requests.post(self.WEBHOOK_URL, main_content)
            if response.status_code == 204:
                break
            else:
                logging.error(response.text)
                logging.error(main_content)
                time.sleep(0.5)

        time.sleep(0.5)


if __name__ == "__main__":
    webhook().send_webhook('test')
