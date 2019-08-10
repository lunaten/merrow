#coding: UTF-8
import json
import requests
import urllib3
from urllib.parse import urljoin
from urllib3.exceptions import InsecureRequestWarning
urllib3.disable_warnings(InsecureRequestWarning)
from bs4 import BeautifulSoup
from datetime import datetime
import logging
import shutil
import os
from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():

    file_list = runMerrow()
    return file_list

# -------------------------------------------------
# runMerrow
# -------------------------------------------------
def runMerrow():
    # クローリング・設定ファイル
    crawler_settings = json.load(open('./config/crawler.json', 'r'))

    # Slack配信・設定ファイル
    distributer_settings = json.load(open('./config/distributer.json', 'r'))
    latest_path = distributer_settings['output.latestPath']
    histry_path = distributer_settings['output.historyPath']

    os.makedirs(latest_path, exist_ok=True)
    os.makedirs(histry_path, exist_ok=True)
    for p in os.listdir(latest_path):
        shutil.move(os.path.join(latest_path, p), histry_path)

    # クローリング
    crawling(crawler_settings, latest_path)

    # outputのファイル一覧を返却
    file_list = ""
    file_list += "<h3>" + latest_path + "</h3>"
    file_list += "<ul>"
    for p in os.listdir(latest_path):
        file_list += "<li>" + p + "</li>"
    else:
        file_list += "</ul>"

    file_list += "<h3>" + histry_path + "</h3>"
    file_list += "<ul>"
    for p in os.listdir(histry_path):
        file_list += "<li>" + p + "</li>"
    else:
        file_list += "</ul>"

    return file_list

# -------------------------------------------------
# crawling
# -------------------------------------------------
def crawling(crawler_settings, out_folder_path):
    
    # サイトごとにクローリングを実行
    for settings in crawler_settings:

        # 初期化
        write_array = []     # スクレイピング結果の保管用（配列）
        date_and_url = {}    # 日付とURLの保管用（辞書）

        # サイトへアクセス
        site_url = settings['siteUrl']
        site_name = settings['siteName']
        request = requests.get(site_url, verify=False)

        # リクエストの結果をxmlに変換 -> htmlでもいいが、lxmlの方が10倍速い…らしい
        soup = BeautifulSoup(request.text, 'lxml')
        
        # スクレイピング実行（再帰処理）
        scraping(soup, settings, date_and_url, write_array, site_url)

        # スクレイピング結果をjsonに書き出し
        writeToJson(out_folder_path, site_name, write_array)

    #else:
        
# -------------------------------------------------
# scraping
# -------------------------------------------------
def scraping(soup, settings, val, write_array, url):
    # ---------------------------------------------
    # repeat scraping
    # ---------------------------------------------
    for setting in settings['scraping']:

        #refrash
        results = None

        #get find elements
        if setting['attrs'] is not None:
            results = soup.find_all(setting['tagName'], attrs={setting['attrs'], setting['attrsName']})
        else:
            results = soup.find_all(setting['tagName'])

        for result in results:
        
            #set to variable if type is not null 
            if setting['type'] is not None:

                #set key
                key = setting['type']

                #set value
                if setting['get'] is not None:
                    value = result.get(setting['get'])
                else:
                    value = result.text

                #if the key is url then urljoin
                if key == 'url' and value.find('http') == -1:
                    value = urljoin(url, value)

                #set to variable
                #exec("{} = '{}'".format(key, value))
                execString = "val['{}'] = '{}'".format(key, value)
                exec(execString)

                #log
                print("{} = {}".format(key, value))

                #set to variable if add to array
                if len(val) > 0 and 'date' in val and 'url' in val:

                    #append
                    entry_dictionary = {'date': val['date'], 'url': val['url']}
                    write_array.append(entry_dictionary)

                    #log
                    print("date:{} url:{}".format(val['date'], val['url']))

                    #refresh
                    entry_dictionary = None
                    

            #run scraping if scraiping is not null
            elif setting['scraping'] is not None:

                #recursive call
                scraping(result, setting, val, write_array, url)

                #refrash
                val = {}
            
        #else:

    # ---------------------------------------------
    # scraping is finish 
    # ---------------------------------------------
    # else:

# -------------------------------------------------
#  サイトごとにスクレイピングの結果をJSONに書き出し
# -------------------------------------------------
def writeToJson(out_folder_path, site_name, write_array):

    #file name
    fileName = '{}_{}.json'.format(datetime.now().strftime('%Y%m%d%H%M%S'), site_name)
    filePath = out_folder_path + fileName
    
    #json parse
    enc = json.dumps(write_array, sort_keys=True, indent=2, separators=(',', ': '))

    #write json
    f = open(filePath, 'w')
    f.write(enc)
    f.close()


# -------------------------------------------------
# app start
# -------------------------------------------------
if __name__ == '__main__':
    app.run()