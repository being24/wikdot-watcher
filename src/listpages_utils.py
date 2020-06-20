#!/usr/bin/env python
# coding: utf-8

import configparser
import logging
import pathlib
import urllib.parse

import requests
from bs4 import BeautifulSoup


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
                        'rev',
                        'total_comments',
                        ]]
        READ_SECTION = 'DEFAULT'

        data_path = pathlib.Path(__file__).parent
        data_path /= '../data'
        self.data_path = str(data_path.resolve())

        config = configparser.RawConfigParser()
        config.read(self.data_path + '/config.ini', encoding='utf-8')

    def get_response(self, url):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        return soup

    def add_row_title(self, info_list):
        return_list = [i for i in self.header]
        return_list += info_list
        return return_list

    def return_url_with_option(self, params):
        parameter = ''
        for key in params.keys():
            if 'root_url' not in key:
                parameter += f'/{key}/'
                for val in params[key]:
                    parameter += f' +{val}'

        parameter = urllib.parse.quote(parameter)
        url = params['root_url'] + parameter
        return url

    def listpages2infolist(self, params):
        logging.debug('scraping start')
        url = self.return_url_with_option(params)
        soup = self.get_response(url)
        info_list = []
        listpages_list = []
        temp_list = []
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
                rev,
                total_comments,
            ]
            info_list.append(temp_list)

        info_list = self.add_row_title(info_list)
        logging.debug('scraping ended')

        return(info_list)
