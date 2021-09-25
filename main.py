# coding: utf-8
# author: wizardforcel

import requests
from pyquery import PyQuery as pq
import datetime as dt
import pytz
import random
import time
import json
import urllib
import os

# KEY = os.environ.get('WB_KEY')
# SEC = os.environ.get('WB_SEC')
COOKIE = os.environ.get('WB_COOKIE', '')

with open('repos.json') as f:
    repos = json.loads(f.read())

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
    "Cookie": COOKIE,
}

def parse_cookie(cookie):
    res = {}
    for kv in cookie.split('; '):
        kv = kv.split('=')
        if len(kv) < 2: continue
        res[kv[0]] = kv[1]
    return res

def refresh_cookie():
    old = parse_cookie(hdrs['Cookie'])
    r = requests.get('https://weibo.com/', headers=hdrs)
    new = parse_cookie(r.headers.get('Set-Cookie', ''))
    old.update(new)
    hdrs['Cookie'] = '; '.join([
        f'{k}={v}' for k, v in old.items()
    ])
    

def get_title(html):
    rt = pq(html)
    h1 = rt.find('.markdown-body > h1').eq(0)
    return h1.text().strip()

def get_random_ch(html):
    rt = pq(html)
    el_links = rt.find('.markdown-body li a')
    links = [
        'https://gitee.com' +
        el_links.eq(i).attr('href')
        for i in range(len(el_links))
    ]
    return random.choice(links)

def main():
    refresh_cookie()
    print('Cookie: ' + hdrs.get('Cookie', ''))
    n_post = 20
    tz = pytz.timezone('PRC')
    now = dt.datetime.now(tz)

    for _ in range(n_post):
        d = random.randint(0, 5)
        hr = random.randint(0, 23)
        min = random.randint(0, 59)
        dt_ = now + dt.timedelta(days=d, hours=hr, minutes=min)
        dt_str = dt_.strftime('%Y-%m-%d %H:%M')
        
        repo = random.choice(repos)
        url = f'https://gitee.com/{repo}'
        co = requests.get(url).text
        title = get_title(co)
        summary = f'{url}/blob/master/SUMMARY.md'
        co = requests.get(summary).text
        link = get_random_ch(co)
        co = requests.get(link).text
        sub_title = get_title(co)
        text = f'『{title}』{sub_title}（来源：Gitee/@ApacheCN ）{link}' \
            .replace('https://', '')
        print(f'[{dt_str}] {text}')

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
    
if __name__ == '__main__': main()