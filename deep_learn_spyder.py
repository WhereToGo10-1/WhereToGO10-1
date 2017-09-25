# -*- coding: utf-8 -*-
"""
Created on Sun Sep 24 21:37:55 2017

@author: xubing
@author: xie,hanshuang
modification:add selling price on 2017-9-25
"""
from selenium import webdriver
import time
import pymysql
import matplotlib.pyplot as plt
from pylab import mpl
    #######################
conn = pymysql.connect(
        host = 'localhost',
        port = 3306,
        user = 'root',
        passwd = '',
        db = 'mysqldb',
        charset = 'utf8'
        )
cur = conn.cursor()
cur.execute('drop table if exists sights_table')
cur.execute('create table sights_table(place varchar(30) primary key,sales int,address varchar(30),hot int,price float)')
cur.execute('ALTER TABLE `sights_table` CHANGE `place` `place` VARCHAR(36) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL')
cur.execute('ALTER TABLE `sights_table` CHANGE `address` `address` VARCHAR(36) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL')

mpl.rcParams['font.sans-serif'] = ['SimHei'] 

#1.从基网址出发，爬取所关心的信息
def get_urls_useful_info(place):
    #收集网页的基本信息
    ####################
    Baseurl = 'http://piao.qunar.com/ticket/list.htm?keyword=%s&region=&from=mpl_search_suggest'%(place)
    #Baseurl = 'http://piao.qunar.com/ticket/list.htm?keyword=%s=&from=mpl_search_suggest&sort=pp&page=1'
    browser = webdriver.Chrome()#模拟出一个Chrome浏览器
    browser.set_page_load_timeout(30)#设置加载超时时间
    browser.get(Baseurl)#打开网址
    page_info = browser.find_element_by_css_selector('#pager-container > div > a:nth-child(9)')
    pages = page_info.text
    print ('%s的景点有：%d'%(place,int(pages)*15),'个')
    #######################
    #利用网站的上热度排序，模拟鼠标点击，获取点击后的url
    hot_place = browser.find_element_by_css_selector('#order-by-popularity')
    # url = hot_place.get_attribute('href')#这个可以得到按钮的属性,一般可以得到一个连接，但也可能是一个js。此时就需要用下面的browser.current_url
    #注意，一定要先点击再获取当前
    hot_place.click()
    time.sleep(3)
    url  = browser.current_url#这里的url是排序后的
    #   print (url)
    #这里对url做了一定的处理，删除了最后一个表示页面的字符
    temp_url = list(url)
    temp_url.pop()
#    print (temp_url)
    url = ''.join(temp_url)
#    print (url)

    #   利用此时的url爬取前n页的数据,并存入数据库中

    for page in range(int(pages)):
       #这里控制爬取多少页的信息
        if page > 9:
            break
        dt_url = url+str(page+1)
        browser.get(dt_url)
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        sight_items = browser.find_element_by_css_selector('#search-result-container').find_elements_by_class_name('sight_item')
        print ('正在爬取第%d页数据......'%(page+1))
#        print('........................')
        for item in sight_items:
            place = item.find_element_by_css_selector('div > div.sight_item_about > h3 > a').text
            try:
                sales = item.find_element_by_css_selector('div > div.sight_item_pop > table > tbody > tr:nth-child(4) > td').text.split('：')[1]
                sales = int(str(sales))
            except:
                sales = 0
            address=item.find_element_by_css_selector('div > div.sight_item_about > div > p > span').text.split('：')[1]
            try:
                hot=item.find_element_by_css_selector('div > div.sight_item_about > div > div.clrfix > div > span.product_star_level > em > span').text.split(' ')[1]
                hot=float(hot)
            except:
                hot=0.0
            price=item.find_element_by_css_selector('div > div.sight_item_pop > table > tbody > tr:nth-child(1) > td > span > em').text
            price=float(price)

            sql = '''insert ignore into sights_table values("{0}","{1}","{2}","{3}","{4}")'''.format(place,sales,address,hot,price)
#            cur.execute('set names gbk')
            cur.execute(sql)#这里可能出现不能插入，是由于字符集的问题。
#            print (place,sales)
#        print('........................')
    cur.close()
    conn.commit()
#    conn.close()       

def calculate(tupl,ratio_sales,ratio_hot,ratio_price):
    ratio_sales=3
    ratio_hot=5
    ratio_price=2
    recmdvalue=tupl[1]*ratio_sales+tupl[3]*ratio_hot+tupl[4]*ratio_price
    return recmdvalue
#2.对于目标城市，根据2,8原则，获取处于20%这个点左右的经典进行推荐，绘制图
def rec_sights(place,ratio_sales,ratio_hot,ratio_price):
    cur = conn.cursor()
    sql = 'select * from sights_table'
    all = cur.execute(sql)
    
    all_sights = cur.fetchmany(all)
    dict1 = {}
    for sight in all_sights:
        dict1[sight[0]] = calculate(sight,ratio_sales,ratio_hot,ratio_price)
#        print (sight)
#    print (dict1)
    cur.close()
    conn.close()
    dict2 = sorted(dict1.items(),key = lambda d:d[1],reverse = True)
#    print (dict2)
    location = int(len(dict2)*0.2)
#    print (len(dict2),location)
    rec_sig1 = dict2[location]
    rec_sig2 = dict2[location+1]
    rec_sig3 = dict2[location-1]
    
    x = []
    y = []
    z = 0
    for item in dict2:
        if z<=20:
            x.append(item[0].split(',')[0])
            y.append(int(item[1]))
        z+=1
    #print (x,y)
    x.reverse()
    y.reverse()
    plt.yticks(range(len(x)),x)
    plt.barh(range(len(x)),y,height = 0.5)
    plt.show()
    print('以2、8原则为您推荐:')
    print('在{0}为您推荐的景点是：\n{1},\n{2},\n{3}'.format(place,rec_sig1,rec_sig2,rec_sig3))
    print('这里人既不会特别多，景点也不会不好玩！')

if '__name__==__main__':
    print ('''*********欢迎来到十一去哪玩儿系统！*********\n只需要输入您想去的城市，\n系统会自动为您推荐既不是人山人海，\n又不是鸟不拉屎的景点！
           \n作者:徐卜灵''') 
    while(1):
        place = input('请输入您的目标城市(输入0退出系统)：')
        ls=list(map(int,input('以10分为总分，请输入销量，热度，售价在您心目中的比分，并以空格隔开：').split()))
        ratio_sales=ls[0]
        ratio_hot=ls[1]
        ratio_price=ls[2]
        if place =='0':
            break
        get_urls_useful_info(place)
        rec_sights(place,ratio_sales,ratio_hot,ratio_price)        
        
        
    