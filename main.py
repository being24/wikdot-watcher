#!/usr/bin/env python
# coding: utf-8


import datetime
import html
import json
import os

import feedparser
import gspread
import pandas as pd
import requests
from oauth2client.service_account import ServiceAccountCredentials


def send_not_in_gs_list(not_in_gs_list, json_name):
    msg = f"スプレッドシートにない下書きを発見しました!"
    init_msg = gen_webhook_msg(msg)
    send_webhook(init_msg)

    cnt = 0

    for draft in not_in_gs_list:
        msg = f"title : {draft[0]}\nurl : {draft[1]}"
        main_content = gen_webhook_msg(msg)

        send_webhook(main_content)
        cnt += 1
        current_key_num = len(notified_json) + 1

        notified_json[str(current_key_num)] = {
            "title": draft[0],
            "url": draft[1],
        }

    msg = f"以上、{cnt}件"
    last_msg = gen_webhook_msg(msg)
    send_webhook(last_msg)

    dump_json(notified_json)

    print("webhookの送信完了")


def gen_webhook_msg(content):
    msg = {
        "username": "スプレッドシート監視",
        "content": content
    }
    return msg


def send_webhook(main_content):
    webhook_url = "https://discordapp.com/api/webhooks/709479351204184174/xC8ORQ_s3ddNxVstCcO8-bm-8af5xpElps2euO440tCOiRAoMLqfiuwLw-MEipLfiq79"
    response = requests.post(webhook_url, main_content)
    if response.status_code != 204:
        print(response.text)


def return_df_from_gs():
    print("gsへのアクセス開始")
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/drive"]

    SPREADSHEET_KEY = "1he4CNLJi6a2BsM7mptmeUe6gOuQCDNc7GJ5-hlZVLDs"

    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        current_path + "/rookie-contest-ecc5f6c1c767.json", scope)

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
    print("DataFlame生成完了")

    return df


def return_list_of_not_in_gs(df):
    print("rssへのアクセス開始")

    RSS_C_and_C = "http://scp-jp-sandbox3.wikidot.com/feed/pages/pagename/draft%3A3396310-91-c0ad/category/draft/tags/%2B_contest%2C%2B_criticism-in/order/updated_at+desc/limit/1/t/%E3%82%B3%E3%83%B3%E3%83%86%E3%82%B9%E3%83%88%E6%89%B9%E8%A9%95%E5%BE%85%E3%81%A1"
    rss_data = feedparser.parse(RSS_C_and_C)

    rss_url_list = []
    not_in_gs_list = []
    notified_url_list = []

    for entry in rss_data.entries:
        rss_url_list.append(entry.id)
        for gs_url in df["下書きURL"]:
            if gs_url == entry.id:
                rss_url_list.remove(entry.id)

    # rss_url_list gsとrssで被ってないリストから通知したURLリストを引けばいい、眠い

    for key in notified_json.keys():
        notified_url_list.append(notified_json[key]["url"])

    result_list = list(set(rss_url_list) - set(notified_url_list))

    for entry in rss_data.entries:
        if any([entry.id == i for i in result_list]):
            not_in_gs_list.append([entry.title, entry.id])

    print("記録されていないurlのリスト更新完了")

    return not_in_gs_list


if __name__ == "__main__":
    current_path = os.path.dirname(__file__)
    json_name = current_path + "/notified.json"

    print(datetime.datetime.now())

    def dump_json(json_data):
        with open(json_name, "w", encoding="utf-8") as f:
            json.dump(
                json_data,
                f,
                ensure_ascii=False,
                indent=4,
                separators=(
                    ",",
                    ": "))

    if not os.path.isfile(json_name):
        notified_json = {}
        dump_json(notified_json)

    with open(json_name, encoding="utf-8") as f:
        notified_json = json.load(f)

    df = return_df_from_gs()

    not_in_gs_list = return_list_of_not_in_gs(df)

    if len(not_in_gs_list) > 0:
        send_not_in_gs_list(not_in_gs_list, json_name)
        pass

    print("done")
