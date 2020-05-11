#!/usr/bin/env python
# coding: utf-8


import html
import json

import feedparser
import gspread
import pandas as pd
import requests
from oauth2client.service_account import ServiceAccountCredentials


def send_webhook(title, url):
    webhook_url = "https://discordapp.com/api/webhooks/694187376465149972/ES5b-_e0t2orM8Je_gKfybFjTLhjeyUXFe4Zs-cnJK2JHwZ_uJjg2-_7eRS6J6LI_2Y1"
    main_content = {
        "username": "スプレッドシート監視",
        "content": f"スプレッドシートにない下書きを発見しました!\ntitle : {title}\nurl : {url}"
    }
    response = requests.post(webhook_url, main_content)
    if response.status_code != 204:
        print(response.text)


def return_df_from_gs():
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']

    SPREADSHEET_KEY = '1he4CNLJi6a2BsM7mptmeUe6gOuQCDNc7GJ5-hlZVLDs'

    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        'rookie-contest-ecc5f6c1c767.json', scope)

    gc = gspread.authorize(credentials)

    worksheet = gc.open_by_key(SPREADSHEET_KEY).sheet1
    cell_list = worksheet.get_all_values()
    del cell_list[:2]
    colum = cell_list.pop(0)
    del colum[0]

    cnt = 0
    for i, con in enumerate(colum):
        if cnt < 2:
            if any([con in j for j in ["タイトル", "URL"]]):
                colum[i] = f"下書き{con}"
                cnt += 1
        else:
            if any([con in j for j in ["タイトル", "URL"]]):
                colum[i] = f"本投稿{con}"
                cnt += 1

    cell_list = [[j.replace("\u3000", " ") for j in i] for i in cell_list]

    df = pd.DataFrame(cell_list)
    df = df.set_index(0)
    df.columns = colum

    return df


def return_list_of_not_in_gs(df):
    RSS_C_and_C = "http://scp-jp-sandbox3.wikidot.com/feed/pages/pagename/draft%3A3396310-91-c0ad/category/draft/tags/%2B_contest%2C%2B_criticism-in/order/updated_at+desc/limit/1/t/%E3%82%B3%E3%83%B3%E3%83%86%E3%82%B9%E3%83%88%E6%89%B9%E8%A9%95%E5%BE%85%E3%81%A1"
    rss_data = feedparser.parse(RSS_C_and_C)

    rss_url_list = []
    not_in_gs_list = []
    for entry in rss_data.entries:
        rss_url_list.append(entry.id)
        for gs_url in df['下書きURL']:
            if gs_url == entry.id:
                # print(f"match! {entry.title} : {entry.id}")
                rss_url_list.remove(entry.id)

    for entry in rss_data.entries:
        if any([entry.id == unmatched for unmatched in rss_url_list]):
            # print(f"{entry.title} : {entry.id}")
            not_in_gs_list.append([entry.title, entry.id])

    return not_in_gs_list


if __name__ == "__main__":

    df = return_df_from_gs()

    not_in_gs_list = return_list_of_not_in_gs(df)

    if len(not_in_gs_list) > 0:
        for li in not_in_gs_list:
            send_webhook(li[0], li[1])

    print("done")
