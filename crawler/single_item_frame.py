#-*- coding: UTF-8 -*- 
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

hd = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36'}#请求头
kv = {'order':'update'}#设置url后置参数，此处设置的提取最近的评论
class one_item:
    def __init__(self, base_html):
        """
            初始化每一款游戏产品页面的基础地址
            形如
            https://www.taptap.com/app/xxxxx/review
        """
        self.base_html = base_html#初始化，赋予该款游戏产品评论页面的基址url
        self.item_id = ''#游戏id初始化
        self.item_name = ''#游戏名称初始化
        self.developer_id = ''#厂商1id初始化
        self.developer_name = ''#厂商名称初始化
        self.follow_num = ''#关注人数初始化
        self.total_score = ''#总评分初始化
        self.comments = []#评论信息初始化
        
        self.ini_bs0bj = None#初始化bs
        
    def is_crawlable(self):
        """
            确认是否可爬
        """
        #设置超时(timeout)重新请求
        for times in range(50):#默认最多重新请求50次，并假定50次内必定请求成功
            try:
                html = requests.get(self.base_html, timeout = 5, headers = hd, params = kv)#设置timeout,headers,params 
                html.raise_for_status()#状态不是200，将引发httperror
                #html.encoding = html.apparent_encoding
                bs0bj = BeautifulSoup(html.text)
                break
            except:
                print('在检测是否可爬时，请求网址:\t'+ self.base_html + '\t超时\n再尝试一次，已累计尝试' + str(times + 1) + '次')#出错输出
     
        if len(bs0bj.findAll('section',{'class':r'taptap-error-title'})) != 0:#如果有该页面信息，则说明不可爬
            print(self.base_html + "页面信息不存在")
            return False
        else:
            self.ini_bs0bj = bs0bj
            print(self.base_html + "页面信息存在,可爬取")
            return True
        
    def info_item(self):
        """
            获取游戏id、游戏名称
        """
        #获取游戏id
        match = re.search(r'[0-9]+', self.base_html)
        self.item_id = match.group(0)
        
        #获取游戏名称
        self.item_name = self.ini_bs0bj.find('h1', {'itemprop':'name'}).get_text()
        
        info_ga = {'item_id':self.item_id,'item_name':self.item_name}
        return info_ga#返回该字典
    
#     def info_developer(self):
#         """
#             获取开发者id、开发者名称
#         """
#         LV1 = self.ini_bs0bj.find('div', {'class':'header-text-author'})#定位1级标签到开发者相关信息的栏目
        
#         #获取开发者id
#         developer_url = LV1.a['href']#开发者信息的url，收集开发者id
#         match = re.search(r'[0-9]+', developer_url)
#         self.developer_id = match.group(0)
        
#         #获取开发者名称
#         self.developer_name = LV1.find('span',{'itemprop' : 'name'}).get_text()
        
#     def info_follow(self):
#         """
#             获取关注人数
#         """
#         self.follow_num = self.ini_bs0bj.find('span', {'class':'count-stats'}).get_text()
    
#     def info_score(self):
#         """
#             获取总评分
#         """
#         self.total_score = self.ini_bs0bj.find('span', {'itemprop':'ratingValue'}).get_text()
    
    def info_comments(self):
        """
            获取用户评论
        """
        
        initial_page = self.ini_bs0bj
        present_page = self.ini_bs0bj#当前爬取的页面
        
        #一款游戏的所有评论暂寸于下dataframe中
        temp_dataframe = pd.DataFrame(columns=['game_id','user_id','issue_time','user_score','content','phone_type','fun','up','down','game_time'])#存储数据的dataframe
        
        #单条评论的数据格式
        def gen_single_comment_structure():
            """
                生成一个单条评论的数据结构
            """
            single_comment_info_temp = {
                'game_id':self.item_id,
                'user_id':'',
                'issue_time':'',
                'user_score':'',
                'content':'',
                'phone_type':'',
                'fun':'',
                'up':'',
                'down':'',
                'game_time':''
            }
            #其中fun、up、down、game_time、phone_type可能存在空值
            return single_comment_info_temp

        
        
        while True:#每一次循环爬取一页的评论
            present_page_comments = present_page.find('ul',{'class':'list-unstyled taptap-review-list', 'id':'reviewsList'})#找出该页所有的评论所在位置
            comments = present_page_comments.findAll('li', {'class':'taptap-review-item collapse in'})
            for each_comment in comments:
                temp_comment_structure = gen_single_comment_structure()#首先生成一个空的结构
                
                #获取user_id
                user_id_box = each_comment.find('div',{'class':'item-text-header'})#用find找到第一个即为评论的用户信息
                user_id = user_id_box.find('span',{'class':'taptap-user'})
                temp_comment_structure['user_id'] = user_id['data-user-id']#更新字典
                
                
                #获取issue_time
                issue_time_box = each_comment.find('a',{'class':'text-header-time'})#用find找到第一个即为评论的用户信息
                issue_time = issue_time_box.find('span',{'data-dynamic-time':re.compile('[0-9](.+)')})#有时会返回unix时间戳，有时候会返回正常的时间，到时候再区分
                temp_comment_structure['issue_time'] = issue_time.get_text()
                
                #获取user_score&game_time
                box = each_comment.find('div',{'class':'item-text-score'})#找出用户评分与游戏时间所在大栏
                    #获取user_score
                user_score = box.find('i',{'class':'colored'})#返回关于评分的内容
                temp_comment_structure['user_score'] = user_score['style']
                    #获取game_time
                game_time = box.findAll(name = 'span')#返回关于游戏时间长的内容
                if len(game_time) != 0:#说明该用户填写了游戏时长
                    temp_comment_structure['game_time'] = game_time[0].get_text()
                    
                #获取content
                content = each_comment.find('div',{'class':'item-text-body'})#找出用户评论所在大栏，第一个默认为用户评论
                temp_comment_structure['content'] = content.get_text().strip('\n')#去除开头末尾的换行符
                
                #获取phone_type、fun、up、down
                box = each_comment.find('div',{'class':'item-text-footer'})#找出所在大栏，第一个默认为所要爬取的内容位置
                    #获取phone_type
                phone_type = box.findAll('span',{'class':'text-footer-device'})#返回关于手机型号的内容
                if len(phone_type) != 0:#说明有手机型号
                    temp_comment_structure['phone_type'] = phone_type[0].get_text()
                    #获取fun、up、down
                L3 = box.find('ul',{'class':'list-unstyled text-footer-btns'})#返回关于fun、up、down的内容
                fun_box = L3.find('button',{'class':'btn btn-sm taptap-button-opinion vote-btn vote-funny'}).find('span',{'data-taptap-ajax-vote':'count'})
                up_box = L3.find('button',{'class':'btn btn-sm taptap-button-opinion vote-btn vote-up'}).find('span',{'data-taptap-ajax-vote':'count'})
                down_box = L3.find('button',{'class':'btn btn-sm taptap-button-opinion vote-btn vote-down'}).find('span',{'data-taptap-ajax-vote':'count'})
                temp_comment_structure['fun'] = fun_box.getText()
                temp_comment_structure['up'] = up_box.getText()
                temp_comment_structure['down'] = down_box.getText()
                
                ##################此步对单条评论数据作存储
                temp_dataframe = temp_dataframe.append(temp_comment_structure, ignore_index = True)#将该条评论加入dataframe中
                #print(temp_comment_structure)
                
            #换下一页
            page_box = present_page.findAll('section',{'class':'taptap-button-more'})#来到有翻页标记的地方
            
            try:#存在只有1页评论的游戏，要跳过
                present_page_num = page_box[0].find('li', {'class':'active'}).get_text()
                print('已爬完第' + str(present_page_num) + '页')
                                

                if present_page_num == '500':#500是上线不能爬了
                    print('已到500页上限')
                    break
                else:#说明没有500页
                    next_page_box = page_box[0].find('li',string = '>')
                    next_page = next_page_box.find('a')            
                    if 'class' in next_page_box.attrs:#如果有class属性，说明到底了
                        print('已经爬到底了')
                        break
                    else:#换页
                        present_url = next_page['href']#抓出新的一页的url
                        #print('新地址为：' + present_url)
                        for times in range(50):#默认最多重新请求50次，并假定50次内必定请求成功
                            try:
                                html = requests.get(present_url, timeout = 5, headers = hd, params = kv)#设置timeout,headers,params 
                                html.raise_for_status()#状态不是200，将引发httperror
                                #html.encoding = html.apparent_encoding
                                present_page = BeautifulSoup(html.text)#重置新的页面
                                break
                            except:
                                print('在检测是否可爬时，请求网址:\t'+ self.base_html + '\t超时\n再尝试一次，已累计尝试' + str(times + 1) + '次')#出错输出
            except:
                print(self.base_html + '仅一页')
                break
        return temp_dataframe
