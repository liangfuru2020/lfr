#-*-coding:utf-8-*-
from lxml import html
import requests
import json
import re
import csv
import glob
import codecs
import time,datetime

import sys,io

# try:
#     reload(sys)
#     sys.setdefaultencoding( "utf-8" )
# except:
#     import importlib
#     importlib.reload(sys)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')

class CrawlWeibo:
    # 获取指定博主的所有微博card的list

    def getWeibo(self,id, page, cid = '107603'):
        #id（字符串类型）：博主的用户id，page（整型）：微博翻页参数
        url='https://m.weibo.cn/api/container/getIndex?type=uid&value='+id+'&containerid=' + cid + id +'&page='+str(page)
        print("url:",url)
        response=requests.get(url)
        html = response.text.encode('utf-8', 'ignore')
        html1 = html.decode("utf-8", 'ignore')
        ob_json=json.loads(html1)
        #print("ob_json:",ob_json)
        #ob_json: {'ok': 0, 'msg': '这里还没有内容', 'data': {'cards': []}}
        list_card=ob_json['data']
        list_cards=list_card['cards']
        #print("list_cards:",list_cards)
        return list_cards# 返回本页所有的cards



    def getContent(self, id, max_page, startDate, endDate, csv_filename1,csv_filename2):

        start_date = datetime.datetime.strptime(startDate,"%Y-%m-%d").date()
        end_date = datetime.datetime.strptime(endDate,"%Y-%m-%d").date()
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        yes_date = str(yesterday.month) + '-' + str(yesterday.day)
        if csv_filename1 == "":
            return
        # 福克斯id: 1890650350遍历当页所有微博，输出内容
        row0 = [u'发布时间',u'微博内容',u'转发量',u'评论量',u'点赞量']
        #csv_file = open('./weibo.csv','a+', newline='',encoding='utf-8')
        csv_file1 =codecs.open(csv_filename1, 'w+', 'utf_8_sig') #a+ 表示在文件内容后追加
        writer1 = csv.writer(csv_file1)
        writer1.writerow(row0) #写入标题

        row2 = [u'作者',u'时间',u'评论内容',u'点赞量']
        #csv_file = open('./weibo.csv','a+', newline='',encoding='utf-8')
        csv_file2 =codecs.open(csv_filename2, 'w+', 'utf_8_sig') #a+ 表示在文件内容后追加
        writer2 = csv.writer(csv_file2)
        writer2.writerow(row2) #写入标题

        expiredNo = 50
        for i in range(1,max_page+1):
            list_cards = self.getWeibo(id,i)
            print("list_cards:%s"%list_cards)
            if len(list_cards) ==0:
                if csv_file1.closed == False:
                    csv_file1.close()
                    return
            for card in list_cards:
                if card['card_type']==9:# 过滤出微博，card_type=9的是微博card，card_type=11的是推荐有趣的人
                    #print(card['mblog']['reposts_count'])
                    create_time = card['mblog']['created_at']
                    # print("create_time:%s"%create_time)
                    # 转换日期
                    if '昨天' in create_time:
                        create_time = yes_date
                    if '刚刚' in create_time:
                        create_time = today    
                    if '前' in create_time:
                        a = create_time.find('小')
                        t = time.time()
                        t = time.strftime('%Y-%m-%d', time.localtime(t))
                        #t = t.replace('-','月')
                        #t = t.replace('-','日') + '点'
                        create_time = t
                    create_time = create_time.replace('月', '-')
                    create_time = create_time.replace('日', '-')
                    if create_time.count('-') == 1:
                        create_time = str(yesterday.year) + "-" + create_time
                    create_date = datetime.datetime.strptime(create_time, "%Y-%m-%d").date()
                    # print("create_date",create_date)
                    # print("start_date",start_date)
                    # print("end_date",end_date)
                    if create_date >= start_date and create_date <= end_date:
                        text = card['mblog']['text']
                        #print("text:%s"%text)
                        tree=html.fromstring(text)
                        content=tree.xpath('string(.)')# 用string函数过滤掉多余标签
                        zhuanfa = card['mblog']['reposts_count']
                        dianzhan = card['mblog']['attitudes_count']
                        pinglun = card['mblog']['comments_count']
                        content_list = [create_time,content,zhuanfa,pinglun,dianzhan]
                        #print ("content_list:",content_list)
                        writer1.writerow(content_list)
                
                if card['card_type']==11:# 过滤出微博，card_type=9的是微博card，card_type=11的是推荐有趣的人
                    #text = card['mblog']['text']
                    #tree=html.fromstring(text)
                    #content=tree.xpath('string(.)')# 用string函数过滤掉多余标签
                    print(11)
                    print("start_date:",start_date)
                    print("create_date:",create_date)
                    print("end_date:",end_date)
                    if card['card_type']==11:
                        #print("card['card_group']:",card['card_group'])
                        zuozhe1 = card['card_group']
                        print("zuozhe1:",zuozhe1)
                        zuozhe2 = zuozhe1['users'][0]
                        print("zuozhe2:",zuozhe2)
                        zuozhe3 = zuozhe2['screen_name'] 
                        print("zuozhe3:",zuozhe3)
                        dianzhan1 = card['card_group']['users']['urank']
                        pinglun1 = card['card_group']['users']['description']
                        content_list1 = [zuozhe1,2018-2-2,pinglun1,dianzhan1]
                        print ("content_list:",content_list1)
                        writer2.writerow(content_list1)
                    else:
                        expiredNo = expiredNo - 1
                        if expiredNo <=0:
                            if csv_file1.closed == False:
                                csv_file1.close()
                            return


        if csv_file1.closed == False:
            csv_file1.close()

if __name__ == '__main__':
    crawl_weibo = CrawlWeibo()
    # 获取1-10页的微博，每页11条，获取更多可以修改range(11,21)
    #crawl_weibo.getContent('1644395354',10, '2018-04-24','2018-04-25', r'C:\Users\Administrator\Desktop\weibo\5.csv',r'C:\Users\Administrator\Desktop\weibo\6.csv')
    crawl_weibo.getContent('1644395354',10, '2018-04-24','2020-07-25', r'C:\Users\hp\Desktop\weibo\5.csv',r'C:\Users\hp\Desktop\weibo\6.csv')
    #crawl_weibo.getContent('2236550925',100, '2018-03-17','2018-04-17', r'C:\Users\Administrator\Desktop\weibo\WeiboWarner.csv')
    #crawl_weibo.getContent('2724964653',100, '2018-03-17','2018-04-17', r'C:\Users\Administrator\Desktop\weibo\WeiboSpider.csv')