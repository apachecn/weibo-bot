# coding: utf-8
# author: wizardforcel

import requests
from bs4 import BeautifulSoup
import datetime as dt
import pytz
import random
import time
import json
import urllib

with open('repos.json') as f:
    repos = json.loads(f.read())

with open('cookie') as f:
    cookie = f.read().strip()

hdrs = {
    "Pragma": "no-cache",
    "Cache-Control": "no-cache",
    "Origin": "https://weibo.com",
    "X-Requested-With": "XMLHttpRequest",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "*/*",
    "Referer": "https://weibo.com/2216356441/manage?default=9527",
    "Accept-Language": "zh-CN",
    "Cookie": cookie,
}

def get_title(html):
    rt = BeautifulSoup(html, 'lxml')
    h1 = rt.select('article > h1')
    if len(h1) == 0:
        return ''
    return h1[0].text

def get_summary_link(html):
    rt = BeautifulSoup(html, 'lxml')
    links = rt.select('td.content a')
    for link in links:
        if link.text == 'SUMMARY.md':
            return 'https://github.com' + \
                link.attrs['href']
    return ''

def get_random_ch(html):
    rt = BeautifulSoup(html, 'lxml')
    links = rt.select('article li a')[1:]
    link = random.choice(links)
    return 'https://github.com' + link.attrs['href']

n_post = 20
tz = pytz.timezone('PRC')
now = dt.datetime.now(tz)
    
for _ in range(n_post):
    hr = random.randint(0, 23)
    min = random.randint(0, 59)
    dt_ = now + dt.timedelta(hours=hr, minutes=min)
    dt_str = dt_.strftime('%Y-%m-%d %H:%M')
    
    repo = random.choice(repos)
    co = requests.get(repo).text
    title = get_title(co)
    summary = get_summary_link(co)
    if summary == '': continue
    co = requests.get(summary).text
    link = get_random_ch(co)
    co = requests.get(link).text
    sub_title = get_title(co)
    print(title + ' ' + sub_title)
    text = f'{title} {sub_title}（来源：Github/ApacheCN） {link}'
    
    post_str = f'location=page_100505_manage&text={urllib.parse.quote(text)}&style_type=1&pdetail=1005052216356441&isReEdit=false&rank=0&addtime={dt_str}&pub_type=dialog&_t=0'
    ts = int(time.time() * 1000)
    url = f'https://weibo.com/aj/mblog/add?ajwvr=6&__rnd={ts}'
    res = requests.post(url, data=post_str, headers=hdrs).content.decode('gbk')
    
    try:
        j = json.loads(res)
    except json.decoder.JSONDecodeError as ex:
        print(f'{dt_str} 发送失败：尚未登录')
        continue
    
    if j['code'] == '100000':
        print(f'{dt_str} 发送成功！')
    else:
        msg = j['msg']
        print(f'{dt_str} 发送失败：{msg}')
    
    