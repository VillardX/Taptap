#-*- coding: UTF-8 -*- 
#爬取taptap上所有游戏的信息、评论
import single_item_frame as sif
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time 

hd = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36'}#请求头

#按发布时间排序的单机游戏爬取，其中“%E5%8D%95%E6%9C%BA”中文“单机的代码”
base_url = 'https://www.taptap.com/tag/%E5%8D%95%E6%9C%BA?sort=released&page='
start_url = 'https://www.taptap.com/tag/%E5%8D%95%E6%9C%BA?sort=released&page=19'#单页面基础网址
present_url = 'https://www.taptap.com/tag/%E5%8D%95%E6%9C%BA?sort=released&page=19'#当前地址

output_path = './reviews.txt'#输出路径

data_review = pd.DataFrame(columns=['game_id','user_id','issue_time','user_score','content','phone_type','fun','up','down','game_time'])#存储数据的dataframe
data_game_name = pd.DataFrame(columns=['item_id','item_name'])#寸游戏id和名称

total_num = 0#记录爬取的总游戏数据
for i in range(1000):#单机游戏数少于1000页
    for times in range(50):#默认最多重新请求50次，并假定50次内必定请求成功
                try:
                    html = requests.get(present_url, headers = hd)
                    html.raise_for_status()#状态不是200，将引发httperror
                    html.encoding = 'utf-8'
                    bs0bj = BeautifulSoup(html.text)
                    break
                except:
                    print('在检测是否可爬时，请求网址:\t'+ self.base_html + '\t超时\n再尝试一次，已累计尝试' + str(times + 1) + '次')#出错输出
    #抽出每一页上所有游戏的url
    
    games_box = bs0bj.find('div',{'class':'search-main-list ', 'id':'searchList', 'data-taptap-search-highlight-keyword':'单机'})
    games_items_box = games_box.findAll('a',{'class':'app-card-left'})#是一个列表，列表中每个元素存了一个游戏的url
    if len(games_items_box) == 0:#说明已遍历完毕
        break
    else:
        for each_game_tag in games_items_box:
            temp_game_review_url = each_game_tag['href'] + r'/review'#当前游戏的url
            
            #采集当前游戏的信息
            temp_item = sif.one_item(temp_game_review_url)
            temp_item.is_crawlable()
            
            temp_game_information = temp_item.info_item()#返回游戏名称与id的字典
            data_game_name = data_game_name.append(temp_game_information, ignore_index = True)#加入
            
            temp_comment_information = temp_item.info_comments()#返回当前游戏的所有评论的dataframe
            data_review = data_review.append(temp_comment_information,ignore_index = True)#加入
            
            total_num = total_num + 1
            #if (total_num % 5) == 0:
            print('已扫描' + str(total_num) + '款游戏')
            data_game_name.to_csv(output_path,index = False, encoding='utf-8', sep = '\t')
            data_review.to_csv(output_path,index = False, encoding='utf-8', sep = '\t')
        
        #跳页
        present_url = base_url + str(i+2)
        
        
data_game_name.to_csv(output_path,index = False, encoding='utf-8', sep = '\t')
data_review.to_csv(output_path,index = False, encoding='utf-8', sep = '\t')              
print('爬取完毕')    
