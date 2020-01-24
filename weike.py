# -*- coding: utf-8 -*-
import os
import json
from datetime import datetime
import jsonpath
import re
import time
import requests
from fake_useragent import UserAgent
import math
from datetime import date, timedelta, datetime
import csv
import pymongo
from pymongo import MongoClient

db = MongoClient('127.0.0.1', 28018).weike
nlist = db.list

class getlist():
    def __init__(self):
        self.url = "https://law.wkinfo.com.cn/csi/search"
        self.proxy = {} # add proxy here
        # self.year = 2015
        # self.month = ['01', '02', '03', '04', '05',
        #               '06', '07', '08', '09', '10', '11', '12']
        self.headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.5',
            'Appversion': '1.0.0',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json;charset=UTF-8',
            'Cookie': '', # add cookie here
            'Identification': '',
            'Origin': 'https://law.wkinfo.com.cn',
            'Referer': 'https://law.wkinfo.com.cn/judgment-documents/list?mode=advanced',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
        }
        self.date = "judgmentDate:[2015.01.01 TO 2015.12.31]" # example dates
        self.data = {"indexId":"law.case","query":{"queryString":"titleExtend:((\"离婚纠纷\")) AND  (( causeOfAction:01000000000000民事/01020000000000婚姻家庭、继承纠纷/01020010000000婚姻家庭纠纷/01020010020000离婚纠纷 ))  AND typeOfDecision:((001))","filterQueries":[],"filterDates":[self.date]},"searchScope":{"treeNodeIds":[]},"relatedIndexQueries":[{"indexId":"law.legislation","queryString":"bodyExtend:((\"离婚纠纷\"))"},{"indexId":"law.caseAnalysis","queryString":"bodyExtend:((\"离婚纠纷\"))"},{"indexId":"law.adminPenalty","queryString":"bodyExtend:((\"离婚纠纷\"))"},{"indexId":"law.commentaryB","queryString":"bodyExtend:((\"离婚纠纷\"))"},{"indexId":"law.specialTopic","queryString":"bodyExtend:((\"离婚纠纷\"))"},{"indexId":"law.article","queryString":"bodyExtend:((\"离婚纠纷\"))"},{"indexId":"law.utilityWriting","queryString":"bodyExtend:((\"离婚纠纷\"))"},{"indexId":"law.trainAssistant","queryString":"bodyExtend:((\"离婚纠纷\"))"},{"indexId":"law.smartChart","queryString":"bodyExtend:((\"离婚纠纷\"))"},{"indexId":"law.procuratorialCase","queryString":"bodyExtend:((\"离婚纠纷\"))"},{"indexId":"law.expertAnswer","queryString":"bodyExtend:((\"离婚纠纷\"))"},{"indexId":"law.countryStandard","queryString":"bodyExtend:((\"离婚纠纷\"))"},{"indexId":"law.treaty","queryString":"bodyExtend:((\"离婚纠纷\"))"},{"indexId":"law.news","queryString":"bodyExtend:((\"离婚纠纷\"))"},{"indexId":"law.judgment","queryString":"bodyExtend:((\"离婚纠纷\"))"}],"sortOrderList":[{"sortKey":"score","sortDirection":"DESC"},{"sortKey":"judgmentDate","sortDirection":"DESC"}],"pageInfo":{"limit":100,"offset":0},"otherOptions":{"requireLanguage":"cn","relatedIndexEnabled":True,"groupEnabled":False,"smartEnabled":True,"buy":False,"summaryLengthLimit":100,"advanced":True,"synonymEnabled":True,"isHideBigLib":0,"relatedIndexFetchRows":5,"proximateCourtID":""},"chargingInfo":{"useBalance":True}}
        self.datadump = json.dumps(self.data)

    def count(self):
        session = requests.Session()
        response = session.post(
                        self.url, data=self.datadump, headers=self.headers)
        html = response.json()
        count = html['searchMetadata']['docCount']
        print(count)
        count = int(count)
        return count

    def listpage(self):
        session = requests.Session()
        count = self.count()
        totalp = int(count / 100 + 1)
        for i in range(0, count, 100):
            while True:
                try:
                    page = int(i / 100 + 1)
                    num = '{}'.format(i)
                    num = int(num)
                    data0 = {"indexId":"law.case","query":{"queryString":"titleExtend:((\"离婚纠纷\")) AND  (( causeOfAction:01000000000000民事/01020000000000婚姻家庭、继承纠纷/01020010000000婚姻家庭纠纷/01020010020000离婚纠纷 ))  AND typeOfDecision:((001))","filterQueries":[],"filterDates":[self.date]},"searchScope":{"treeNodeIds":[]},"relatedIndexQueries":[{"indexId":"law.legislation","queryString":"bodyExtend:((\"离婚纠纷\"))"},{"indexId":"law.caseAnalysis","queryString":"bodyExtend:((\"离婚纠纷\"))"},{"indexId":"law.adminPenalty","queryString":"bodyExtend:((\"离婚纠纷\"))"},{"indexId":"law.commentaryB","queryString":"bodyExtend:((\"离婚纠纷\"))"},{"indexId":"law.specialTopic","queryString":"bodyExtend:((\"离婚纠纷\"))"},{"indexId":"law.article","queryString":"bodyExtend:((\"离婚纠纷\"))"},{"indexId":"law.utilityWriting","queryString":"bodyExtend:((\"离婚纠纷\"))"},{"indexId":"law.trainAssistant","queryString":"bodyExtend:((\"离婚纠纷\"))"},{"indexId":"law.smartChart","queryString":"bodyExtend:((\"离婚纠纷\"))"},{"indexId":"law.procuratorialCase","queryString":"bodyExtend:((\"离婚纠纷\"))"},{"indexId":"law.expertAnswer","queryString":"bodyExtend:((\"离婚纠纷\"))"},{"indexId":"law.countryStandard","queryString":"bodyExtend:((\"离婚纠纷\"))"},{"indexId":"law.treaty","queryString":"bodyExtend:((\"离婚纠纷\"))"},{"indexId":"law.news","queryString":"bodyExtend:((\"离婚纠纷\"))"},{"indexId":"law.judgment","queryString":"bodyExtend:((\"离婚纠纷\"))"}],"sortOrderList":[{"sortKey":"score","sortDirection":"DESC"},{"sortKey":"judgmentDate","sortDirection":"DESC"}],"pageInfo":{"limit":100,"offset":num},"otherOptions":{"requireLanguage":"cn","relatedIndexEnabled":True,"groupEnabled":False,"smartEnabled":True,"buy":False,"summaryLengthLimit":100,"advanced":True,"synonymEnabled":True,"isHideBigLib":0,"relatedIndexFetchRows":5,"proximateCourtID":""},"chargingInfo":{"useBalance":True}}
                    dumpJsonData = json.dumps(data0)
                    response = session.post(
                        self.url, data=dumpJsonData, headers=self.headers)
                    html = response.json()
                    # print(response.status_code)
                    # print(html)
                    fulllist = html['documentList']
                    for slist in fulllist:
                        nlist.insert_one(slist)
                    print('Page ', page, 'success!')
                except Exception as err:
                    # print(err)
                    print('Page ', page, 'failed!')
                    time.sleep(0.5)
                else:
                    if page == totalp:
                        print('All done!')
                    break


if __name__ == '__main__':
    jf = getlist()
    # jf.count()
    jf.listpage()
