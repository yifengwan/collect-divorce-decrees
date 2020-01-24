# -*- coding: utf-8 -*-
import json
from pprint import pprint

import requests
from fake_useragent import UserAgent

import re
import pymongo
from pymongo import MongoClient
import time
from tenacity import retry, wait_fixed, stop_after_attempt
from datetime import date, timedelta, datetime
import datetime
from tomorrow import threads
import math
import csv
from bs4 import BeautifulSoup
import bs4
import pandas as pd
import re
from requests import ConnectionError
from io import BytesIO
import random
from PIL import Image

db = MongoClient('127.0.0.1', 27017).shanghai
nlist = db.list


class shanghai:
    def __init__(self):
        self.url = "http://www.hshfy.sh.cn/shfy/gweb2017/flws_list_content.jsp"
        self.proxy = {}  # add proxy here

    def listpage(self):
        session = requests.Session()
        ua = UserAgent().random
        baseurl = 'http://www.hshfy.sh.cn/shfy/code.do?n='
        num = random.random()
        imageurl = baseurl + str(num)
        cookies = {}  # add cookie here
        for x in range(1, 379):
            headers = {
                'User-Agent': ua, 'Cookie': cookies}
            data = {
                'fydm': '',
                'ah': '',
                'ay': '',
                'ajlb': '',
                'wslb': '%E5%88%A4%E5%86%B3%E4%B9%A6',
                'title': '%E7%A6%BB%E5%A9%9A',
                'jarqks': '2017-01-01',
                'jarqjs': '2018-12-31',
                'qwjs': '',
                'wssj': '',
                'yg': '',
                'bg': '',
                'spzz': '',
                'flyj': '',
                'pagesnum': x,
                'zbah': '', }
            try:
                response = session.post(
                    self.url, data=data, headers=headers, timeout=30)
            except ConnectionError:
                time.sleep(1)
                continue
            html = response.text
            if 'error' in html:
                print('输入验证码')
                print('从第', x, '页开始')
                image = session.get(imageurl, headers=headers)
                captcha = Image.open(BytesIO(image.content))
                captcha.show()
                code = input('vcode:')
                captcha.close()
                codeurl = 'http://www.hshfy.sh.cn/shfy/gweb2017/checkCode.jsp?code='
                codeurl2 = codeurl + str(code)
                codedata = {'code': code}
                recode = session.post(codeurl2, data=codedata, headers=headers)
                response = session.post(
                    self.url, data=data, headers=headers, timeout=30)
                html = response.text
                soup = BeautifulSoup(html, 'lxml')
                table = soup.find('table')
                trows = table.find_all('tr')[1:]
                caseid = []
                for num in trows:
                    urlid = num['onclick']
                    urlid = urlid[9:-2]
                    caseid.append(urlid)
                caselist = []
                for tr in trows:
                    td = tr.find_all('td')
                    row = [i.text for i in td]
                    s = []
                    for cell in row:
                        cell = "".join(cell.split())
                        s.append(cell)
                    caselist.append(s)
                for urlnum in range(len(caseid)):
                    case = caselist[urlnum]
                    case.append(caseid[urlnum])
                    key = ['casenumber', 'casename', 'decreetype', 'anyou',
                           'court', 'procedure', 'judge_date', 'caseid']
                    res = dict(zip(key, case))
                    nlist.insert_one(res)
                print('Page', x, 'done!')
                x = x + 1
            else:
                soup = BeautifulSoup(html, 'lxml')
                table = soup.find('table')
                trows = table.find_all('tr')[1:]
                caseid = []
                for num in trows:
                    urlid = num['onclick']
                    urlid = urlid[9:-2]
                    caseid.append(urlid)
                caselist = []
                for tr in trows:
                    td = tr.find_all('td')
                    row = [i.text for i in td]
                    s = []
                    for cell in row:
                        cell = "".join(cell.split())
                        s.append(cell)
                    caselist.append(s)
                for urlnum in range(len(caseid)):
                    case = caselist[urlnum]
                    case.append(caseid[urlnum])
                    key = ['casenumber', 'casename', 'decreetype', 'anyou',
                           'court', 'procedure', 'judge_date', 'caseid']
                    res = dict(zip(key, case))
                    db.list.insert_one(res)
                print('Page', x, 'done!')
                x = x + 1


if __name__ == '__main__':
    sh = shanghai()
    sh.listpage()
