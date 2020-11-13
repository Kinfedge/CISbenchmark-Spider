import sys
import requests
import os
import pdb
import time
import random
from retrying import retry

requests.packages.urllib3.disable_warnings()

@retry(retry_on_result = requests, stop_max_attempt_number = 50, wait_fixed = 1000)

def download(url, file_path):
    headers1 = {
    'Connection': 'close',
    'Accept': '*/*',
    'DNT': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,like Gecko) Chrome/81.0.4044.129 Safari/537.36',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,en-US;q = 0.7,en;q = 0.3',
    'Referer': 'https://downloads.cisecurity.org/',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age = 0',
    }  
    cookies = {'_ga':'GA1.2.1642749091.1602295950', 'visitor_id799323':'193345229', 'visitor_id799323-hash':'d15576d2b8ab2646ba087e0a08d52856aa582112636bafeafe9347721b55e328e3cc64425b8cea92c52ea629c44d0ee2cc986f29', 'cis_download_cookie':'1u5kGwva17PrGkFgIsjEvj2ae2NQyEfcDRM2SgzW', 'documentId':'32'}
    r1 = requests.get(url, stream=True, verify=False, headers=headers1, cookies=cookies)
    total_size = int(r1.headers['content-length'])

    if os.path.exists(file_path):
        temp_size = os.path.getsize(file_path)  
    else:
        temp_size = 0
    print(temp_size)
    print(total_size)
    headers2 = {
    'Connection': 'close',
    'Accept': '*/*',
    'DNT': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,like Gecko) Chrome/81.0.4044.129 Safari/537.36',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,en-US;q = 0.7,en;q = 0.3',
    'Referer': 'https://downloads.cisecurity.org/',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age = 0',
    'Range': 'bytes=%d-' % temp_size
    }  
    r = requests.get(url, stream=True, verify=False, headers=headers2, cookies=cookies, timeout=30)

    with open(file_path, "ab") as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                temp_size += len(chunk)
                f.write(chunk)
                f.flush()
                done = int(50 * temp_size / total_size)
                sys.stdout.write("\r[%s%s] %d%%" % (' ' * done, ' ' * (50 - done), 100 * temp_size / total_size))
                sys.stdout.flush()
    print()  


if __name__ == '__main__':
    link = r'https://downloads.cisecurity.org/download?u=1603942000'
    path = r'/home/CIS20spider/test1.pdf'
    url = os.path.join(link)
    download(url, path)
