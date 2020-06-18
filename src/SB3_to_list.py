#!/usr/bin/env python
# coding: utf-8

import configparser
import itertools
import logging
import pathlib
import pprint
import re
import time
import traceback

import gspread
import requests
from bs4 import BeautifulSoup
from oauth2client.service_account import ServiceAccountCredentials


class listpages_utils():
    def __init__(self):
        self.header = [['title',
                        'url',
                        'created_by',
                        'updated_by',
                        'commented_by',
                        'created_at',
                        'updated_at',
                        'commented_at',
                        'rating',
                        'total_votes',
                        'uv',
                        'dv',
                        'tags',
                        'parent_pages_name',
                        'parent_pages_url',
                        'children_pages',
                        'size',
                        ]]

    def get_response(self, url):
        # SB3_URL = 'http://scp-jp.wikidot.com/author:ukwhatn/lp_category/_default/lp_tags/%E3%83%AB%E3%83%BC%E3%82%AD%E3%83%BC%E3%82%B3%E3%83%B3%E3%83%86%E3%82%B9%E3%83%88/lp_limit/999999/lp_p/1'
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        return soup

    def add_row_title(self, info_list):
        return_list = self.header
        return_list += info_list
        return return_list

    def listpages2infolist(self, soup):
        info_list = []
        listpages_list = [i for i in soup.select(
            "[class='list-pages-item']") if i.select_one('h5')]
        for i in listpages_list:
            created_by = updated_by = commented_by = 'None'
            created_at = updated_at = commented_at = 'None'
            parent_pages_name = parent_pages_url = 'None'
            children_pages = size = 'None'
            rating = total_votes = uv = dv = rev = total_comments = '0'
            tags = ''

            title = i.select_one(
                "[class = lp_title]").text.replace("\u3000", " ")
            url = i.select_one("[class = lp_fullname]").text
            created_by = i.select_one("[class = lp_created_by]").text
            created_at = i.select_one("[class = lp_created_at]").text
            if i.select_one("[class = lp_updated_by]"):
                updated_by = i.select_one("[class = lp_updated_by]").text
            if i.select_one("[class = lp_updated_at]"):
                updated_at = i.select_one("[class = lp_updated_at]").text
            if i.select_one("[class = lp_commented_by]"):
                commented_by = i.select_one("[class = lp_commented_by]").text
            if i.select_one("[class = lp_commented_at]"):
                commented_at = i.select_one("[class = lp_commented_at]").text

            rev = i.select_one("[class='lp_rev']").text
            total_comments = i.select_one("[class='lp_comments']").text

            rating = i.select_one("[class='lp_rating']").text
            total_votes = i.select_one("[class='lp_totalvotes']").text
            uv = i.select_one("[class='lp_uv']").text
            dv = i.select_one("[class='lp_dv']").text

            if i.select_one("[class='lp_tags']"):
                tags = i.select_one("[class='lp_tags']").text
            if i.select_one("[class='lp_hiddentags']"):
                tags += (i.select_one("[class='lp_hiddentags']").text)

            if i.select_one("[class='lp_parent']"):
                parent_pages_name = i.select_one("[class='lp_parent']").text
                if len(parent_pages_name) == 1:
                    parent_pages_name = 'None'
            if i.select_one("[class='lp_parentdir']"):
                parent_pages_url = i.select_one("[class='lp_parentdir']").text

            children_pages = i.select_one("[class='lp_children']").text

            size = i.select_one("[class='lp_size']").text

            temp_list = [
                title,
                url,
                created_by,
                updated_by,
                commented_by,
                created_at,
                updated_at,
                commented_at,
                rating,
                total_votes,
                uv,
                dv,
                tags,
                parent_pages_name,
                parent_pages_url,
                children_pages,
                size,
            ]
            info_list.append(temp_list)

        info_list = self.add_row_title(info_list)

        return(info_list)


class webhook():
    def __init__(self):
        # URLと名前、URLを外部から読み込む

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
            print("can't send blank msg")
            return -1

        main_content = self.gen_webhook_msg(msg)

        while True:
            response = requests.post(self.WEBHOOK_URL, main_content)
            if response.status_code == 204:
                break
            else:
                print(response.text)
                print(main_content)
                time.sleep(0.5)

        time.sleep(0.2)


class gooogle_spread_sheet_handler():
    def __init__(self):
        self.SPREADSHEET_KEY = config[READ_SECTION]['spreadsheet_key']

    def get_workbook(self):
        scope = ["https://spreadsheets.google.com/feeds",
                 "https://www.googleapis.com/auth/drive"]

        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            "rookie-contest-ecc5f6c1c767.json", scope)
        # current_pathに直す

        gc = gspread.authorize(credentials)

        workbook = gc.open_by_key(self.SPREADSHEET_KEY)

        return workbook

    def toAlpha(self, num):
        if num <= 26:
            return chr(64 + num)
        elif num % 26 == 0:
            return toAlpha(num // 26 - 1) + chr(90)
        else:
            return toAlpha(num // 26) + chr(64 + num % 26)

    def split_workbook_name(self, worksheet_list: list):
        sheet_dict_list = []
        for sheet in worksheet_list:
            sheet = str(sheet)
            sheet = sheet.translate(str.maketrans({'<': '', '>': '', "'": ''}))
            sheet = re.split('[ :]', sheet)
            sheet_dict_list.append({'sheetname': sheet[1], 'number': sheet[3]})
        return sheet_dict_list

    def return_sheet_exists(self, sheet_name):
        workbook = self.get_workbook()
        worksheet_list = workbook.worksheets()
        sheet_dict_list = self.split_workbook_name(worksheet_list)

        worksheet_name_list = [i['sheetname'] for i in sheet_dict_list]

        if sheet_name not in worksheet_name_list:
            print(f'sheetname {sheet_name} not in workbook')
            raise ValueError(f"{sheet_name} not found")
        else:
            worksheet = workbook.worksheet(sheet_name)
            return worksheet

    def read_spreadsheet_by_name(self, sheet_name: str):
        worksheet = self.return_sheet_exists(sheet_name)
        cell_list = worksheet.get_all_values()

        cell_list = [[j.replace("\u3000", " ") for j in i] for i in cell_list]

        return cell_list

    def overwrite_spreadsheet_by_name(
            self,
            sheet_name: str,
            write_list: list,
            start_cell: str = 'A1'):
        # start_cell = 'C4' # 列はA〜Z列まで
        start_cell_col = re.sub(r'[\d]', '', start_cell)
        start_cell_row = int(re.sub(r'[\D]', '', start_cell))

        def alpha2num(c): return ord(c) - ord('A') + 1

        # 展開を開始するセルからA1セルの差分
        row_diff = start_cell_row - 1
        col_diff = alpha2num(start_cell_col) - alpha2num('A')

        col_lastnum = len(write_list[0])
        row_lastnum = len(write_list)

        workbook = self.get_workbook()
        worksheet = self.return_sheet_exists(sheet_name)
        cell_list = worksheet.range(start_cell
                                    + ':'
                                    + self.toAlpha(col_lastnum
                                                   + col_diff)
                                    + str(row_lastnum
                                          + row_diff))

        write_list = list(itertools.chain.from_iterable(write_list))

        self.clear_worksheet(sheet_name)

        for num, cell in enumerate(cell_list):
            cell.value = write_list[num]

        worksheet.update_cells(cell_list)

    def add_row_by_name(
            self,
            sheet_name: str,
            write_list: list,
            start_cell: str = 'A1'):
        workbook = self.get_workbook()
        worksheet = self.return_sheet_exists(sheet_name)

        worksheet.append_rows(not_in_gs_list)

    def clear_worksheet(self, sheet_name: str):
        worksheet = self.return_sheet_exists(sheet_name)
        worksheet.clear()


class get_diff():
    def __init__(self):
        self.gssh = gooogle_spread_sheet_handler()
        self.lp = listpages_utils()

    def diff_of_gs_and_listpage(self, sheet_name):
        spreadsheet_data = self.gssh.read_spreadsheet_by_name(sheet_name)
        listpages_data = self.lp.listpages2infolist(soup)

        not_in_gs_list = []
        for one in listpages_data:
            if any([one == i for i in spreadsheet_data]):
                continue
            else:
                not_in_gs_list.append(one)

        return not_in_gs_list


if __name__ == "__main__":
    READ_SECTION = 'DEFAULT'
    config = configparser.RawConfigParser()
    config.read('config.ini', encoding='utf-8')
    # ここmasterpath
    SB3_URL = config[READ_SECTION]['SB3_URL']

    response = requests.get(SB3_URL)
    soup = BeautifulSoup(response.text, "html.parser")

    get_diff = get_diff()
    webhook = webhook()
    gssh = gooogle_spread_sheet_handler()
    lp = listpages_utils()

    not_in_gs_list = get_diff.diff_of_gs_and_listpage('ルーキーコン2020')
    listpages_data = lp.listpages2infolist(soup)

    for content in not_in_gs_list:
        msg = '----------\n'
        msg += f'未登録の記事を発見しました!\n{content[0]}\n'
        if 'draft' in content[1]:
            msg += 'http://scp-jp-sandbox3.wikidot.com'
        else:
            msg += 'http://scp-jp.wikidot.com'
        msg += f'{content[1]}'
        webhook.send_webhook(msg)

    gssh.add_row_by_name('ルーキーコン2020', not_in_gs_list)
