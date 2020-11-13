# -*- coding:utf-8 -*-

#author:Edge
#email:zhengxiao@gac-nio.com
#time: 2020/10/30

from bs4 import BeautifulSoup
import requests
import random
import sys
import pdb
import re
import os
import time
import random
from retry import retry

reload(sys)
sys.setdefaultencoding('utf8')
#Ignore requests warning
requests.packages.urllib3.disable_warnings()

def connect_timeout_retry(sub_url,sub_headers,sub_cookies):
    tmp_response = requests.get(sub_url, stream = True, verify = False, headers = sub_headers, cookies = sub_cookies, timeout = 30)
    return tmp_response


#Edit cookies
def edit_cookies(download_ID):
    sub_cookies = {}
    if download_ID == 0:
        f = open(r'cookies.txt',"r")
        for line in f.read().split(';'):
            name,value = line.strip().split('=',1)
            sub_cookies[name] = value
        f.close()
    else:
        sub_cookies = {'_ga':'GA1.2.1642749091.1602295950', 'visitor_id799323':'193345229', 'visitor_id799323-hash':'d15576d2b8ab2646ba087e0a08d52856aa582112636bafeafe9347721b55e328e3cc64425b8cea92c52ea629c44d0ee2cc986f29', 'cis_download_cookie':'1u5kGwva17PrGkFgIsjEvj2ae2NQyEfcDRM2SgzW', 'documentId':'32'}
        sub_cookies['documentId'] = download_ID.strip()
    return sub_cookies

#Get response from all urls.
def get_response(url,download_ID):
    headers = {
    "Connection": "close",
    "Accept": "*/*",
    "DNT": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-CN,en-US;q = 0.7,en;q = 0.3",
    "Upgrade-Insecure-Requests": "1",
    "Cache-Control": "max-age = 0"
}
    cookies = edit_cookies(download_ID)
    resp = requests.get(url,headers = headers,cookies = cookies)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.content, 'lxml')
    return soup

#List technology_id id = benchmark_id = documentid title = filename location
def get_technology_info(technology_url):
    soup = get_response(technology_url,0)
    pre_info = soup
    combinestr = []
    for string in pre_info.stripped_strings:
        combinestr = combinestr+[string]
#    print(len(combinestr))
    categories = combinestr[0].split(']')
#    lencat = len(categories)
#    for n in range(lencat):
#        print(categories[n])
#        '\n'
    splandcom(categories,technology_url)

#Category string split and combination
def splandcom(categoriestext,tech_url):
    objectnames = []
    all_info = {}
    ID = []
    id_num = 0
    tmp = categoriestext
    lentmp = len(tmp)
    #Extract string from double quotes and braces
    setpat1 = re.compile(r'\"(.*)\"')
    for n in range(lentmp-1):
        #Get object names
        name = tmp[n].split('[')[0]
        save_names = setpat1.findall(name)
        #Get all other infomations
        info = tmp[n].split('[')[1]
        objectnames = objectnames+[save_names]
        for line in info.split('},'):
            line = line.strip('{}')
            ID = ID+[line.split(',')[0].split(':')[1]]
#            print(ID[id_num],id_num)
            #Get all category ID numbers
            id_num = id_num+1
    categoriestext = objectnames
    get_subcategory_info(tech_url,id_num,ID)
    return categoriestext
#Get list index
def get_list_index(lists, item):
    tmp_list = []
    list_tag = 0
    for i in lists:
        if item in i:
            tmp_list.append(list_tag)
        list_tag = list_tag+1
    return tmp_list

def get_subcategory_info(tech_url,id_num,ID):
    suburls = []
    benchmark_ID = []
    sub_filename = []
    sub_info = []
    sub_location = []
    sub_pre_info = []
    sub_combinestr = []
    download_ID = []
    list_index = []
    for m in range(id_num):
#    for m in range(2):
        suburls = suburls+[tech_url+'/'+ID[m]+'/benchmarks/latest']
        sub_soup = get_response(suburls[m],0)
        for sub_string in sub_soup.stripped_strings:
            sub_combinestr = sub_combinestr+[sub_string]
            for tmp_str1 in sub_string.split('},'):
                sub_info = sub_info + [tmp_str1.strip('{[]}')]
                sub_info_len = len(sub_info)
                print(sub_info_len)
                '\n'
    #Get benchmark_ID sub_filename sub_location write to allbaselinefiles.txt
    f1 = open('allbaselinefiles.txt','w')
    for n in range(sub_info_len):
        list_sub_info = sub_info[n].split(',')
        list_index = get_list_index(list_sub_info,'\"id\"')
        if len(list_index) == 2:
            indexn = list_index[1]
            download_ID = download_ID+[list_sub_info[indexn].split(':')[2]]
            f1.write('download'+'_'+list_sub_info[indexn].split(':',1)[1].strip('[{\"')+'\n')
        else:
            indexn =list_index[0]
            download_ID = download_ID+[list_sub_info[indexn].split(':')[1]]
            f1.write('download'+'_'+list_sub_info[indexn].strip('\"')+'\n')
        for tmp_str2 in list_sub_info:
#            print(tmp_str2)
#            '\n'
            if "benchmark_id" in tmp_str2:
                benchmark_ID = benchmark_ID+[tmp_str2.split(':')[1]]
                f1.write(tmp_str2.strip('\"')+'\n')
            elif "filename" in tmp_str2:
                sub_filename = sub_filename+[tmp_str2.split(':')[1].strip('\"')]
                f1.write(tmp_str2.strip('\"')+'\n')
            elif "location" in tmp_str2:
                sub_location = sub_location+[tmp_str2.split(':',1)[1].strip('\"')]
                f1.write(tmp_str2.strip('\"')+'\n')
            else:
                pass#do nothing
    f1.close()
    return suburls
#Download all pdf files to /home/CIS20spider/pdfs/
#Retrying requests if timeout 30 seconds
@retry(exceptions=(requests.exceptions.Timeout, requests.exceptions.ConnectionError),tries=50,delay=1)#
def download_pdfs(url, download_ID, file_path):
    headers1 = {
    'Connection': 'close',
    'Accept': '*/*',
    'DNT': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,like Gecko) Chrome/81.0.4044.129 Safari/537.36',
    'Accept-Encoding': 'gzip, deflate',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,like Gecko) Chrome/81.0.4044.129 Safari/537.36',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,en-US;q = 0.7,en;q = 0.3',
    'Referer': 'https://downloads.cisecurity.org/',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age = 0'
    }  
    cookies = edit_cookies(download_ID)
    r1 = connect_timeout_retry(url,headers1,cookies)
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
    print(headers2)
    r2 = connect_timeout_retry(url,headers2,cookies)

    with open(file_path, "ab+") as f:
        for chunk in r2.iter_content(chunk_size=1024):
            if chunk:
#                pdb.set_trace()
                temp_size += len(chunk)
                f.write(chunk)
                f.flush()
                done = int(50 * temp_size / total_size)
                sys.stdout.write("\r[%s%s] %d%%" % (' ' * done, ' ' * (50 - done), 100 * temp_size / total_size))
                sys.stdout.flush()



if __name__ == '__main__':
    url = 'https://downloads.cisecurity.org'
    technology_url = url+'/'+'technology'
    download_url = url+'/download?u='+str(random.randint(1603000000,1703000000))
    filename = ''
    file_path = ''
    files_dir = "/home/pdfs/"
    get_technology_info(technology_url)
    count_lines = 1
    f_last = open('allbaselinefiles.txt',"r")
    for line in f_last.readlines():
        print(line.strip())
        '\n'
        if 'download_id' in line:
            download_ID = line.split(':')[1]
        elif 'filename' in line:
            filename = line.split(':')[1].strip('\"')
        else:
            pass #Doing nothing
        file_path = files_dir+filename.strip()
        if count_lines == 4:
            count_lines = 1
#            pdb.set_trace()
            download_pdfs(download_url,download_ID,file_path)
        else:
            print('Count_lines less than 4')
        count_lines = count_lines+1
    f_last.close()
    print('Congraturlations! You have spidered all base line pdf files\n')
