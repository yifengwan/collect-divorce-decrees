# -*- coding: utf-8 -*-
import asyncio
import concurrent.futures
import logging
import sys
import time
import requests
import uvloop
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

from fake_useragent import UserAgent
import math
from bs4 import BeautifulSoup
import json
from datetime import datetime
from urllib import parse
import jsonpath
import re
import time
import os
import pandas as pd
import csv
import motor.motor_asyncio
client = motor.motor_asyncio.AsyncIOMotorClient('127.0.0.1', 28017)
db = client.pkulaw
case = db.case
retry = db.retrycase2


def clear(case):
    case = "".join(case.split())
    remove = re.compile(r'<[^>]+>', re.S)
    case = remove.sub('', case)
    return case


# read all urls for detail page
with open('url.json') as nplist:
    ldata = json.load(nplist)
    allurls = []
    for i in range(0, len(ldata)):
        np = ldata[i]['url']
        np = np.replace('pfnl_', 'pfnl/')
        np = np.replace('?match=Exact', '')
        allurls.append(np)


def blocks(listurl):
    proxy = {}  # add proxy here
    referurl = 'http://www.pkulaw.cn{}'.format(listurl)
    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Cookie': '',  # add cookie here
        'Host': 'www.pkulaw.cn',
        'Origin': 'http://www.pkulaw.cn',
        'Referer': referurl,
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
    }
    response = requests.get(referurl, headers=headers,
                            proxies=proxy, timeout=30)
    html = response.text
    return html


def getcase(listurl):
    s = ['【审理法官】', '【代理律师 / 律所】', '【权责关键词】']
    try:
        html = blocks(listurl)
        keys = []
        values = []
        soup = BeautifulSoup(html, 'lxml')
        tab = soup.find('table', class_='articleInfo')
        trows = tab.find_all('tr')
        for row in trows[1:(len(trows))]:
            tds = row.find_all('td')
            if len(tds) == 4:
                td40 = tds[0].text
                td42 = tds[2].text
                keys.append(td40)
                keys.append(td42)
                if td40 in s:
                    td41list = []
                    td41 = tds[1].find_all('a')
                    for t in td41:
                        i = t.text
                        td41list.append(i)
                else:
                    td41list = tds[1].text
                values.append(td41list)
                if td42 in s:
                    td43list = []
                    td43 = tds[3].find_all('a')
                    for t in td43:
                        i = t.text
                        td43list.append(i)
                else:
                    td43list = tds[3].text
                values.append(td43list)
                # values.append(tds[1].text)
            if len(tds) == 2:
                td20 = tds[0].text
                keys.append(td20)
                if td20 in s:
                    td21list = []
                    td21 = tds[1].find_all('a')
                    for t in td21:
                        i = t.text
                        td21list.append(i)
                else:
                    td21list = tds[1].text
                values.append(td21list)
            else:
                pass
        for i in range(len(keys)):
            keys[i] = keys[i][1:-1]
        casetitle = soup.find('p', align='center')
        casetitle = casetitle.text
        keys.append('casetitle')
        values.append(casetitle)
        keys.append('url')
        values.append(listurl)
        fulltext = clear(soup.find('div', class_='articleText').text)
        keys.append('fulltext')
        values.append(fulltext)
        res = dict(zip(keys, values))
        db.case.insert_one(res)
    except Exception as er:
        print('Error: ', listurl, er)
        # reurl = {'url': listurl}
        # retry.insert_one(reurl)


async def run_blocking_tasks(executor):
    loop = asyncio.get_event_loop()
    blocking_tasks = [
        loop.run_in_executor(executor, getcase, listurl)
        for listurl in allurls
    ]
    await asyncio.wait(blocking_tasks)

if __name__ == '__main__':

    executor = concurrent.futures.ThreadPoolExecutor(
        max_workers=5,
    )

    event_loop = asyncio.get_event_loop()
    try:
        event_loop.run_until_complete(
            run_blocking_tasks(executor)
        )
    finally:
        event_loop.close()
