# -*- coding: utf-8 -*-
import os
import json
from datetime import datetime
from urllib import parse
import jsonpath
import re
import time
import requests
from fake_useragent import UserAgent
import math
from bs4 import BeautifulSoup
from datetime import date, timedelta, datetime
import csv
import pymongo
from pymongo import MongoClient

db = MongoClient('127.0.0.1', 28017).pkulaw
nlist = db.list


def clear(case):
    case = "".join(case.split())
    remove = re.compile(r'<[^>]+>', re.S)
    case = remove.sub('', case)
    return case


def date_judge(year, month):
    """return the number of days in a month; need two params, year and month"""
    MONTH_TABLE = {
        '1': 31,
        '2': 28,
        '3': 31,
        '4': 30,
        '5': 31,
        '6': 30,
        '7': 31,
        '8': 31,
        '9': 30,
        '10': 31,
        '11': 30,
        '12': 31,
    }
    if month != 2:
        dates = MONTH_TABLE[str(month)]
    else:
        if year % 4 != 0 and year % 400 != 0:
            dates = 28
        else:
            dates = 29
    return dates


class getlist():
    def __init__(self):
        self.url = "http://www.pkulaw.cn/case/Search/Record"
        self.proxy = {}  # add proxy here
        self.year = 2013
        self.month = ['01', '02', '03', '04', '05',
                      '06', '07', '08', '09', '10', '11', '12']
        self.headers = {
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Cookie': '',  # add cookie here
            'Host': 'www.pkulaw.cn',
            'Origin': 'http://www.pkulaw.cn',
            'Referer': 'http://www.pkulaw.cn/Case/',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
        }

    def count(self, date):
        data = {
            'Menu': 'CASE',
            'IsFullTextSearch': False,
            'MatchType': 'Exact',
            'OrderByIndex': 0,
            'GroupByIndex': 0,
            'ShowType': 1,
            'ClassCodeKey': '002020102,',
            'OrderByIndex': 0,
            'GroupByIndex': 0,
            'ShowType': 1,
            'Library': 'PFNL',
            'FilterItems.DocumentAttr': '001',  # 判决书
            'FilterItems.LastInstanceDate': json.dumps(date),
            'SubKeyword': '在结果的标题中检索',
            'Pager.PageSize': 20,
            'Pager.PageIndex': 0,
            'X-Requested-With': 'XMLHttpRequest',
        }
        while True:
            try:
                response = requests.post(
                    self.url, data=data, headers=self.headers, proxies=self.proxy)
                html = response.text
                soup = BeautifulSoup(html, 'lxml')
                page = soup.find('span', class_='qp_totalnumber')
                page = page.text
                page = int(page)
                # print(page)
                return page
            except:
                continue

    def listpage(self):
        session = requests.Session()
        for month in range(1, 13):
            dates = date_judge(self.year, month)
            start_day = date(self.year, month, 1)
            end_day = date(self.year, month, dates)
            delta = end_day - start_day
            for da in range(0, delta.days + 1):
                day = start_day + timedelta(days=da)
                day = day.strftime('%Y.%m.%d')
                # print(day)
                sdate = {"Start": str(day), "End": str(day)}
                print(sdate)
                page = self.count(sdate)
                print(day, 'total page ', page)
                if page > 0 and page <= 20:
                    for p in range(0, page):
                        while True:
                            try:
                                data = {
                                    'Menu': 'CASE',
                                    'IsFullTextSearch': False,
                                    'MatchType': 'Exact',
                                    'OrderByIndex': 0,
                                    'GroupByIndex': 0,
                                    'ShowType': 1,
                                    'ClassCodeKey': '002020102,',
                                    'OrderByIndex': 0,
                                    'GroupByIndex': 0,
                                    'ShowType': 1,
                                    'Library': 'PFNL',
                                    'FilterItems.DocumentAttr': '001',  # 判决书
                                    'FilterItems.LastInstanceDate': json.dumps(sdate),
                                    'SubKeyword': '在结果的标题中检索',
                                    'Pager.PageSize': 20,
                                    'Pager.PageIndex': p,
                                    'X-Requested-With': 'XMLHttpRequest',
                                }
                                response = session.post(
                                    self.url, data=data, headers=self.headers, proxies=self.proxy)
                                html = response.text
                                # print(html)
                                soup = BeautifulSoup(html, 'lxml')
                                content = soup.find('dl', class_='contentList')
                                dlist = content.find_all('dd')
                                key = ['title', 'url', 'courtname',
                                       'casenumber', 'judge_date', 'procedure']
                                for d in dlist:
                                    url = d.find('a', class_='title')
                                    title = url.text
                                    title = clear(title)
                                    url = url.get('href')
                                    try:
                                        courtname = d.find(
                                            'span', title='审理法院').text
                                    except:
                                        courtname = ''
                                    try:
                                        casenumber = d.find(
                                            'span', title='案件字号').text
                                    except:
                                        casenumber = ''
                                    judge_date = d.find(
                                        'span', title='审结日期').text
                                    sp = d.find('div', class_='unfoldContent')
                                    spli = sp.find_all('a')
                                    case = [title, url, courtname,
                                            casenumber, judge_date]
                                    for a in spli:
                                        if 'AdvSearchDic.TrialStep' in a.get('href'):
                                            procedure = a.text
                                        # else:
                                        #     procedure = ''
                                        # print(procedure)
                                            case.append(procedure)
                                    res = dict(zip(key, case))
                                    nlist.insert_one(res)
                                print('finish', day, 'page ', p)
                                time.sleep(1)
                            except:
                                print('error')
                                time.sleep(0.5)
                                continue
                            else:
                                if p == page - 1:
                                    print(day, 'all done!')
                                    time.sleep(1)
                                break
                elif page == 0:
                    print(day, 'no data')
                elif page > 20:
                    with open('retry-list.csv', 'a', newline='', encoding='utf-8') as ff:
                        writer = csv.writer(ff, delimiter=',')
                        writer.writerow(
                            [day] + [page])


if __name__ == '__main__':
    pku = getlist()
    # pku.count(date)
    pku.listpage()
