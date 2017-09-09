#-*- coding:utf-8 -*-
#! /usr/local/bin/python
import sys
reload(sys)
sys.setdefaultencoding('utf8')

"""
@version: 1.0
@author: Morain
@file: 1.Jianshu.py
@time: 2017/9/9 下午4:48
"""
import warnings
warnings.filterwarnings('ignore')

import urllib
import urllib2
from bs4 import BeautifulSoup

import requests
import numpy as np
import pandas as pd
import re
import time

import os
from os import path
import jieba
from wordcloud import WordCloud,ImageColorGenerator

import pdfkit
import matplotlib.pyplot as plt
from scipy.misc import imread
def getPage(url):#获取链接中的网页内容
    headers = {
       'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36'
    }
    try:
        request = urllib2.Request(url = url, headers = headers)
        response = urllib2.urlopen(request, timeout = 5)
        page = response.read().decode('utf-8')
        return page
    except (urllib2.URLError,Exception), e:
        if hasattr(e, 'reason'):
            print '抓取失败，具体原因：', e.reason
            response = urllib2.urlopen(request,timeout = 5)
            page = response.read().decode('utf-8')
            return page

#输入作者姓名，获取作者信息
def getUrl():
    userlink = []
    while len(userlink) == 0:
        authorname = raw_input('请输入想查询的作者的名称：')
        url = "http://www.jianshu.com/search/do?q=" + authorname + "&type=user&page=1&order_by=default"
        headers = {
            'Accept':'application/json',
            'Accept-Encoding':'gzip, deflate',
            'Accept-Language':'zh-CN,zh;q=0.8',
            'Connection':'keep-alive',
            'Cookie':'remember_user_token=W1s2NDAyNjk5XSwiJDJhJDEwJHlqVUVMN0MucGRnczZKNGVsdWRha2UiLCIxNTA0MDAxNzYwLjk5MDQ4MzUiXQ%3D%3D--fd0628706b69e1c56a29160d93d11f34ae58256d; Hm_lvt_0c0e9d9b1e7d617b3e6842e85b9fb068=1504957649,1504958125,1504958395,1504959596; Hm_lpvt_0c0e9d9b1e7d617b3e6842e85b9fb068=1504965945; _maleskine_session=QjQ4VFJxMURNZlJqdmhlTmJCTlZpZmk2SFhLQzM4aGRJcW1SNEkrWWw1UGN5NTF4bDhWeW56aGpzSTNqdmwrL08xbTBpRzJCNmJYL3hlNGF6eDkyWG03Ymw3ektCemZad1lnQW50OUs1Sm5YczdMKzI4VWtVMGYrNWZIejRCMzdneThhKzFIYy9HUHYrbWRIOHU3LzM1eEhvRWtncXgxK3hwYzQyWHc0SEJ4Z1hsUEMzdzdwWldFWGs4Q005MnovZ2RJZEZFUVR5NDFWeEw2STBKVFdYM216cjN4ankwUUZ5elBqUGRIQ0cxeVRrNDg3RXkwRDBuUUUyeHJ6Q0ZxZnp2L2pyTTRHRXlId3hhRC9Zc3JDcjBNQ2NqRkRiUzd0cy9EYkJvenkybGgwckpEc0tOaFZEV2x2NjZSOTBpZlprQkRUaHNRZUxwU0RHTWdjMjhDMDVLbE55UUVRL1NkZGRPVnlYNXVOOGwzT3krNzVxeHFmaUR5SnErUU5LKy90a29qcHlrdGdyMks2MHk4VE03U01rYVMzaDhnNkFlM2pjL1NFTkVXZFhwZz0tLWNOK1QybWhoYWRWY244bm51VUpUTHc9PQ%3D%3D--984ab0e50328799e0e74eee236ecae164e404e79; _ga=GA1.2.1365559118.1504001743; _gid=GA1.2.1421173038.1504885638; _gat=1',
            'Host':'www.jianshu.com',
            'If-None-Match':'W/"4bfbd077698d0530d56d0c79c5429609"',
            'Referer':'http://www.jianshu.com/search?q=%E6%80%80%E5%B7%A6%E5%90%8C%E5%AD%A6&page=1&type=user',
            'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36'
        }
        json_data = requests.get(url=url, headers=headers).json()
        for i in json_data['entries']:
            nickname = i['nickname']
            slug = i['slug']
            if nickname == authorname:
                # print i
                return slug
                break
        else:
            print '输入的作者名称不符合规范，请重新输入。'

def getAuthorinf(page): #得到作者的姓名与头像链接
    #<img src="//upload.jianshu.io/users/upload_avatars/2542851/0dca220dd6bb.jpeg?imageMogr2/auto-orient/strip|imageView2/1/w/240/h/240" alt="240">
    pattern1 = re.compile(u'<img.*?src="/(.*?)\?.*?".*?alt="240".*?>.*?')
    #/upload.jianshu.io/users/upload_avatars/2542851/0dca220dd6bb.jpeg
    imgurl = pattern1.findall(page)
    imgurl = 'http:/'+ imgurl[0]
    urllib.urlretrieve(imgurl,'./bg.gif')
    #<a class="name" href="/u/62478ec15b74">怀左同学</a>
    pattern2 = re.compile(u'<a.*?class="name".*?href=".*?">(.*?)</a>')
    #怀左同学
    name = pattern2.findall(page)
    pattern3 = re.compile(u'<p>(.*?)</p>')
    metablock = pattern3.findall(page)
    #[u'19', u'67029', u'249', u'436259', u'76560']
    titleNum = int(metablock[2])
    return name[0],titleNum

def getTitle(url,titlelist,num): #读取个人页文章链接
    page = getPage(url)
    pattern = re.compile(u'<span.*?class="time".*?data-shared-at="(.*?)\+08:00"></span>.*?'
                        + u'<a.*?class="title".*?href="(.*?)">(.*?)</a>',re.S)
    titles = re.findall(pattern,page)
    for title in titles:
        titlelist.append([title[0],'http://www.jianshu.com' + title[1],title[2]])
        print '正在读取第' + str(num) + '篇文章链接'
        num +=1
    return titlelist,num

def getText(articlelist): #根据文章链接读取文章内容
    num = 0
    try:
        for url in articlelist:
            html = getPage(url[1])
            soup = BeautifulSoup(html)
            text = soup.find('div',class_="show-content").getText()
            text = text.replace("\n","")
            articlelist[num].append(text)
            time.sleep(3)
            num +=1
            print '正在读取第' + str(num) + '篇文章'
    except Exception as e:
        print e
    return articlelist

def writeArticle(articlelist,authorname): #将文章信息写入txt文件
    filePath = './' + authorname + '的文章.txt'
    fileArticle = open(filePath, 'w')
    try:
        for article in articlelist:
            fileArticle.write( '文章名称：' + article[2] + '\r\n')
            fileArticle.write( '创作时间：' + article[0] + '\r\n')
            fileArticle.write( '原文链接：' + article[1] + '\r\n')
            fileArticle.write( '原文内容：' + article[3] + '\r\n\r\n')
        print '文章读取完毕，结果存储在' + authorname + '的文章.txt中，开始绘制词云'
    finally:
            fileArticle.close()

def text_to_wordcloud(articlelist,authorname): #读取文章生成词云
    stopwords = {}
    isCN = 1 #默认启用中文分词
    back_coloring_path = "bg.jpg" # 设置背景图片路径
    text_path = authorname + '文章.txt' #设置要分析的文本路径
    font_path = '苹方黑体-准-简.ttf' # 为matplotlib设置中文字体路径没
    stopwords_path = 'stopwords1893.txt' # 停用词词表
    imgname1 =  authorname + '默认颜色.png' # 保存的图片名字1(只按照背景图片形状)
    imgname2 =  authorname + '背景图颜色.png' # 保存的图片名字2(颜色按照背景图片颜色布局生成)
    back_coloring = imread(back_coloring_path)# 设置背景图片
    mywordlist = []
    # 设置词云属性
    wc = WordCloud(font_path=font_path,  # 设置字体
               background_color="white",  # 背景颜色
               max_words=2000,  # 词云显示的最大词数
               mask=back_coloring,  # 设置背景图片
               max_font_size=100,  # 字体最大值
               random_state=42,
               width=1000, height=860, margin=2,# 设置图片默认的大小,但是如果使用背景图片的话,那么保存的图片大小将会按照其大小保存,margin为词语边缘距离
               )
    #将文章中纯文本提取
    filePath = '纯文章.txt'
    fileArticle = open(filePath, 'w')
    try:
        for article in articlelist:
            fileArticle.write(article[3])
    finally:
            fileArticle.close()
    text = open(filePath).read()
    os.remove(filePath)
    #使用jieba整理文本
    wordlist = jieba.cut(text,cut_all = False)
    wl = "/ ".join(wordlist)
    f_stop = open(stopwords_path)
    try:
        f_stop_text = f_stop.read()
        f_stop_text=unicode(f_stop_text,'utf-8')
    finally:
        f_stop.close()
    f_stop_seg_list = f_stop_text.split('\n')
    for myword in wl.split('/'):
        if not(myword.strip() in f_stop_seg_list) and len(myword.strip())>1:
            mywordlist.append(myword)
    text = ''.join(mywordlist)
    print '你关注的作者高产似XX O__O"…'
    time.sleep(1)
    print '我还在努力生中…w(ﾟДﾟ)w…'
    time.sleep(1)
    print '(๑•ᴗ•๑)去打局农药再回来看结果吧(逃'
    wc.generate(text)    # 生成词云, 用generate输入全部文本,也可以我们计算好词频后使用generate_from_frequencies函数
    image_colors = ImageColorGenerator(back_coloring) # 从背景图片生成颜色值
    plt.figure() #绘制图片
    wc.to_file(imgname1) # 保存图片
    plt.figure()
    plt.imshow(wc.recolor(color_func=image_colors))
    wc.to_file(imgname2) # 保存图片
    print '词云图片生成成功，结果存储在'+ authorname + '默认颜色.png和'+ authorname + '背景图颜色.png中'

def parse_html_to_pdf(articlelist,authorname): #将正文转为pdf格式
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
    </head>
    <body>
    {content}
    </body>
    </html>

    """
    start = time.time()
    options = {
        'page-size': 'Letter',
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
        'encoding': "UTF-8",
        'custom-header': [
            ('Accept-Encoding', 'gzip')
        ],
        'cookie': [
            ('cookie-name1', 'cookie-value1'),
            ('cookie-name2', 'cookie-value2'),
        ],
        'outline-depth': 10,
    }
    htmls = []
    for index,url in enumerate(articlelist):
        try:
            response = requests.get(url[1])
            soup = BeautifulSoup(response.content,"html.parser")
            title = soup.find('h1').get_text() #写入标题
            body = soup.find_all(class_="show-content")[0] #写入正文
            #标题加入到正文的最前面，居中显示
            center_tag = soup.new_tag("center")
            title_tag = soup.new_tag('h1')
            title_tag.string = title
            center_tag.insert(1, title_tag)
            body.insert(1, center_tag)
            html = str(body)
            pattern = "(<img.*?src=\")(//upload.*?)(\")"
            def func(m):
                if not m.group(2).startswith("http"):#检查是否以http开头
                    rtn = "".join([m.group(1), "http:", m.group(2), m.group(3)])
                    return rtn
                else:
                    return "".join([m.group(1), m.group(2), m.group(3)])
            html = re.compile(pattern).sub(func, html) #将图片相对路径转为绝对
            html = html_template.format(content=html)
            html = html.encode("utf-8")
            f_name = ".".join([str(index),"html"])
            print '正在下载' + authorname + '第' + str(index+1) +'篇文章对应html网页'
            with open(f_name, 'wb') as f:
                f.write(html)
            htmls.append(f_name)
            time.sleep(2)
        except Exception as e:
            print e
    print '正在将' + authorname + '的文章整理成pdf'
    try:
        pdfkit.from_file(htmls, authorname + "的文章合辑.pdf", options=options)##将html文件合并为pdf
    except Exception as e:
        print e
    for html in htmls:
        os.remove(html)
    total_time = time.time() - start
    print u"总共耗时：%f 秒" %total_time

class Main():
    num = 0
    articlelist = []
    pageNum = 1
    userlink = getUrl()
    titlePage = getPage("http://www.jianshu.com/u/" + userlink)
    authorname, articleMax = getAuthorinf(titlePage)
    pageMax = articleMax / 9 + 1
    articleNum = 1
    print '正在读取' + authorname + '的文章链接列表'
    while pageNum <= pageMax:
        url = 'http://www.jianshu.com/u/' + userlink + '?order_by=shared_at&page=' + str(pageNum)
        articlelist, articleNum = getTitle(url, articlelist, articleNum)
        pageNum += 1
        time.sleep(3)
    print '文章链接已读取完毕，马上从链接中读取' + authorname + '的' + str(articleMax) + '篇文章'
    articlelist = getText(articlelist)
    writeArticle(articlelist,authorname)
    text_to_wordcloud(articlelist,authorname)
    parse_html_to_pdf(articlelist,authorname)



if __name__ == '__main__':
    pass