from bs4 import BeautifulSoup
import requests
import sys
import re
import time

def downloadFile():
    url = 'https://downloads.cisecurity.org/download?u=1603942000'
    cookies = {'_ga':'GA1.2.1642749091.1602295950', 'visitor_id799323':'19334522    9', 'visitor_id799323-hash':'d15576d2b8ab2646ba087e0a08d52856aa582112636bafeafe9347721b5    5e328e3cc64425b8cea92c52ea629c44d0ee2cc986f29', 'cis_download_cookie':'1u5kGwva17PrGkFgI    sjEvj2ae2NQyEfcDRM2SgzW', 'documentId':'32'}
    headers = {
    "Connection": "close",
    "Accept": "*/*",
    "DNT": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,like Gecko) Chrome/81.0.4044.129 Safari/537.36",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-CN,en-US;q = 0.7,en;q = 0.3",
    "Referer": "https://downloads.cisecurity.org/",
    "Upgrade-Insecure-Requests": "1",
    "Cache-Control": "max-age = 0"
    }
    
    testfile = requests.get(url,headers = headers, cookies = cookies,stream = True)
    length = float(testfile.headers['content-length'])
    print(length)
    '\n'
    count = 0
    count_tmp = 0
    time1 = time.time()
    
    with open("test1.pdf","wb") as tpdf:
        for chunk in testfile.iter_content(chunk_size = 1024): #1024 bytes
            if chunk:
                tpdf.write(chunk)
                count = count+len(chunk)
                if time.time()-time1 > 2:
                    print('Stop here!\n')
                    p = count/length*100
                    speed = (count-count_tmp)/1024/1024/2
                    count_tmp = count
                    print('test1.pdf' + ': ' + formatFloat(p) + '%' + ' Speed: ' + formatFloat(speed) + 'M/S')
                    time1 = time.time()
            else:
                print('Stop here!')

def formatFloat(num):
    return '{:.2f}'.format(num)

if __name__ == '__main__':
    downloadFile()
