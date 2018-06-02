# *-* coding=utf-8 *-*

from urllib import request, error, parse
import os
import sys
import http.cookiejar
from bs4 import BeautifulSoup
import re

username = 'dotomato'
password = '369258147'

# 初始化
user_agent = r'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36' \
             r' (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36'
headers = {'User-Agent': user_agent, 'Connection': 'keep-alive'}
cookie_filename = 'cookie.txt'
cookie_aff = http.cookiejar.MozillaCookieJar()
handler = request.HTTPCookieProcessor(cookie_aff)
opener = request.build_opener(handler)

# 加载cookie
if os.path.exists(cookie_filename):
    cookie_aff.load(cookie_filename)
    print('load cookie success')
else:

    # 登录1
    values = {
        "CookieDate": "1",
        "b": "d",
        "bt": "1-1",
        "UserName": username,
        "PassWord": password,
        "ipb_login_submit": "Login!",
    }
    postdata = parse.urlencode(values).encode()
    req = request.Request('https://forums.e-hentai.org/index.php?act=Login&CODE=01',
                          data=postdata, headers=headers, method='POST')
    try:
        response = opener.open(req)
    except error.URLError as e:
        print(e.reason)
        exit()

    print('login forum success')
    # 登录2
    req = request.Request('https://exhentai.org', headers=headers)
    try:
        response = opener.open(req)
    except error.URLError as e:
        print(e.reason)
        exit()
    print('login exhentai success')

    cookie_aff.save(cookie_filename, ignore_discard=True, ignore_expires=True)
    print('save cookie success')

# 获取计数
count = 0
with open('count', 'r') as f:
    count = int(f.readline())
count += 1


def get_html(url):
    req = request.Request(url, headers=headers)
    return opener.open(req).read().decode(encoding='UTF-8')


def get_data(url):
    req = request.Request(url, headers=headers)
    return opener.open(req).read()


def get_soup(data):
    return BeautifulSoup(data, 'html.parser')


# 获取参数
book = sys.argv[1]
if book[-1] != '/':
    book += '/'

page_inter = 1
if len(sys.argv) > 2:
    page_inter = int(sys.argv[2])

page_stop = -1
if len(sys.argv) > 3:
    page_stop = int(sys.argv[3])

# 获取第一页
print('========================================================')
print('getting:' + book)
book_soup = get_soup(get_html(book))

title = book_soup.find('h1', attrs={'id': 'gn'}).text
if title is None or title == '':
    title = 'exhentai'
else:
    print(title)
    title = re.sub(r'[\\/:*?\"<>| \-]', '', title)

book_path = os.path.join('data', title)
if not os.path.exists(book_path):
    os.mkdir(book_path)

page_count = book_soup.find_all('td', attrs={'class': 'gdt2'})[5]
page_count = page_count.text.split(' ')[0]
page_count = int(page_count) // 40 + 1
print('page count:', page_count)

if page_stop != -1:
    page_count = min(page_stop, page_count)

pages_0 = [i.div.a['href'] for i in book_soup.find_all('div', attrs={'class': 'gdtm'})]
page_c = 0


def deal_pages(pages):
    global page_c
    while page_c < len(pages):
        page = pages[page_c]
        print('========================================================')
        print('getting:' + page)
        page_soup = get_soup(get_html(page))
        img = page_soup.find('div', attrs={'id': 'i3'}).a.img['src']
        img_name = img.split('/')[-1]

        print('getting:' + img)
        img_data = get_data(img)
        img_path = os.path.join('data', title, img_name)
        f = open(img_path, 'wb')
        f.write(img_data)
        f.flush()
        f.close()
        page_c += page_inter
    page_c -= len(pages)

deal_pages(pages_0)

if page_count > 1:
    for i in range(1, page_count):
        book_i = book+'?p={}'.format(i)
        print('getting:' + book_i)
        book_soup = get_soup(get_html(book_i))
        pages_i = [i.div.a['href'] for i in book_soup.find_all('div', attrs={'class': 'gdtm'})]
        deal_pages(pages_i)

print('========================================================')
print('finish!!!')
with open('count', 'w') as f:
    f.write("{:04d}".format(count))
    f.flush()
