import sys, re
import requests
import numpy as np
import pandas as pd
import openpyxl
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from time import sleep


def scrape_yodosya(export_as):
    #ベースページのURL
    baseurl = 'https://www.yodosha.co.jp/yodobook/word/'

    #ベースページのHTMLソースを取得
    html = requests.get(baseurl)

    #取得したHTMLをパース
    soup = BeautifulSoup(html.text, "html.parser")

    #ベースページの中のリンクのリストを取得
    head_li = soup.find_all("ul", {"class": "breadcrumb"})[0].findChildren('li', recursive = False)

    #結果を格納する２次元配列
    result = np.empty((0,3), dtype=str)

    #イニシャルのリンクをイテレーション
    for li in head_li:

        #リンク先のHTMLを取得
        link = li.find('a')
        head_page = requests.get(urljoin(baseurl, link['href']))
        soup = BeautifulSoup(head_page.text, 'html.parser')

        #単語ページへのリンクの部分を取得
        word_ul = soup.find('ul', {'class': 'ruledline_column'})
        #単語が一つも登録されていない場合は次のイニシャルへ
        if word_ul == None:
            continue
        word_li = word_ul.find_all('li')

        #各単語をイテレーション
        for wli in word_li:
            #リンク先のHTMLを取得
            link_to_word = wli.find('a')
            word_page = requests.get(urljoin(baseurl, link_to_word['href']))
            soup = BeautifulSoup(word_page.text, 'html.parser')
            
            #日英の単語名が記載されているタグを取得
            eng_tag = soup.find('li', {'class': 'eng'})
            jp_tag = eng_tag.find('li', {'class': 'jap'})
            #日本語名が登録されていない場合はnot found
            if jp_tag != None:
                jp_word = jp_tag.text
            else:
                jp_word = "not found"
            
            #英語タグに含まれるulタグを削除し、単語の部分のみ取得
            eng_tag.ul.decompose()
            eng_word = eng_tag.text.rstrip()

            #結果の配列に格納
            result = np.append(result, np.array([[link_to_word.text, eng_word, jp_word]]), axis=0)
            sleep(0.01)
        sleep(0.01)
    #配列をData Frameへ変換
    df = pd.DataFrame(result)
    #excel出力
    df.to_excel(export_as, sheet_name='word list', index = False, header = False)

#コマンドラインから呼ばれた時の処理
if __name__ == "__main__":
    
    if len(sys.argv) < 2:
        print('出力ファイル名を入力してください')
        exit(0)
    filename = sys.argv[1]
    if not re.match('^.+.xlsx$', filename):
        print('拡張子はxlsxとしてください')
        exit(0)
    
    scrape_yodosya(filename)

    