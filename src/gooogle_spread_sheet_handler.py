#!/usr/bin/env python
# coding: utf-8

import configparser
import itertools
import pathlib
import re

import gspread
from oauth2client.service_account import ServiceAccountCredentials


class gooogle_spread_sheet_handler():
    def __init__(self):
        READ_SECTION = 'DEFAULT'

        data_path = pathlib.Path(__file__).parent
        data_path /= '../data'
        self.data_path = str(data_path.resolve())

        config = configparser.RawConfigParser()
        config.read(self.data_path + '/config.ini', encoding='utf-8')

        self.USERNAME = config[READ_SECTION]['name']
        self.AVATOR_URL = config[READ_SECTION]['avatar_url']
        self.WEBHOOK_URL = config[READ_SECTION]['WEBHOOK_URL']
        self.SPREADSHEET_KEY = config[READ_SECTION]['spreadsheet_key']

    def get_workbook(self):
        scope = ["https://spreadsheets.google.com/feeds",
                 "https://www.googleapis.com/auth/drive"]

        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            self.data_path + "/rookie-contest-ecc5f6c1c767.json", scope)

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
        worksheet = self.create_sheet_not_exists(sheet_name)

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

        def alpha2num(c):
            return ord(c) - ord('A') + 1

        # 展開を開始するセルからA1セルの差分
        row_diff = start_cell_row - 1
        col_diff = alpha2num(start_cell_col) - alpha2num('A')

        col_lastnum = len(write_list[0])
        row_lastnum = len(write_list)

        workbook = self.get_workbook()
        worksheet = self.return_sheet_exists(sheet_name, workbook)
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
        worksheet = self.return_sheet_exists(sheet_name)

        worksheet.append_rows(write_list)

    def clear_worksheet(self, sheet_name: str):
        worksheet = self.return_sheet_exists(sheet_name)
        worksheet.clear()

    def create_sheet_not_exists(self, sheet_name):
        workbook = self.get_workbook()
        worksheet_list = workbook.worksheets()
        sheet_dict_list = self.split_workbook_name(worksheet_list)

        worksheet_name_list = [i['sheetname'] for i in sheet_dict_list]

        if sheet_name not in worksheet_name_list:
            workbook.add_worksheet(title=sheet_name, rows=1000, cols=26)
            worksheet = workbook.worksheet(sheet_name)
            return worksheet
        else:
            worksheet = workbook.worksheet(sheet_name)
            return worksheet


if __name__ == "__main__":
    gssh = gooogle_spread_sheet_handler()
    sheet_name = 'test'
    gssh.create_sheet_not_exists(sheet_name)
