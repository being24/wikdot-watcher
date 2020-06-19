#!/usr/bin/env python
# coding: utf-8

import configparser
import logging
import pathlib

from gooogle_spread_sheet_handler import gooogle_spread_sheet_handler
from listpages_utils import listpages_utils
from webhook import webhook


class get_diff():
    def __init__(self):
        self.gssh = gooogle_spread_sheet_handler()
        self.lp = listpages_utils()

    def diff_of_gs_and_listpage(self, sheet_name, params):
        spreadsheet_data = self.gssh.read_spreadsheet_by_name(sheet_name)
        listpages_data = self.lp.listpages2infolist(params)

        not_in_gs_list = []
        for one in listpages_data:
            if any([one == i for i in spreadsheet_data]):
                continue
            else:
                not_in_gs_list.append(one)

        return not_in_gs_list


if __name__ == "__main__":
    READ_SECTION = 'DEFAULT'

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(levelname)s: %(message)s')
    # logging.disable(logging.WARNING)

    logging.debug('program begins.')

    data_path = pathlib.Path(__file__).parent
    data_path /= '../data'
    data_path = str(data_path.resolve())

    config = configparser.RawConfigParser()
    config.read(data_path + '/config.ini', encoding='utf-8')

    get_diff = get_diff()
    webhook = webhook()
    gssh = gooogle_spread_sheet_handler()
    params = {
        "lp_category": ['draft'],
        "lp_tags": ["_contest", "_criticism-in"],
        'lp_limit': [999999]}

    not_in_gs_list = get_diff.diff_of_gs_and_listpage('ルーキーコン2020', params)

    if len(not_in_gs_list) > 0:
        msg = '----------\n'
        msg += f'未登録の記事を{len(not_in_gs_list)} 件発見しました!\n'
        print(msg)
        webhook.send_webhook(msg)

        gssh.add_row_by_name('ルーキーコン2020', not_in_gs_list)

        for content in not_in_gs_list:
            msg = '----------\n'
            msg += f'タイトル: {content[0]}\n'
            msg += f'カテゴリ: \n著者: {content[2]}\n'
            msg += 'URL: '
            if 'draft' in content[1]:
                msg += 'http://scp-jp-sandbox3.wikidot.com'
            else:
                msg += 'http://scp-jp.wikidot.com'
            msg += f'{content[1]}'
            webhook.send_webhook(msg)

    else:
        pass

    logging.debug('program ends.')
