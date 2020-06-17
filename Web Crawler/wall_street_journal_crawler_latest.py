import requests
import pandas as pd
import json
import pickle
import multiprocessing as mp
from time import sleep
from random import randint
from selenium import webdriver
from selenium.webdriver.chrome.options import Options  # for suppressing the browser
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup as bs
from threading import Thread

class wall_street_crawler:
    def __init__(self):
        """
        To initialize the basic settings.
        """
        self.url_day = 'https://www.wsj.com/news/archive/{}' # URL for 1 day data
        self.url_day_above = 'https://www.wsj.com/search/term.html?min-date={}&max-date={}&isAdvanced={}&daysback={}&andor={}&sort={}&source={}' # URL for more than 1 days data
        self.links_each_news = {} # Draftly data print
        self.df = '' # Final data print
        self.data_to_df = [] # Save clean data in the regular format

        # Fixed Setting
        self.page = '1'
        self.isAdvanced = 'true'
        self.andor = 'AND'
        self.sort = 'date-desc'
        self.source = 'wsjarticle'

        self.headers = {
            'accept-encoding' : 'gzip, deflate, br',
            'accept-language' : 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control' : 'max-age=0',
            'referer' : self.url_day_above,
            'sec-fetch-dest' : 'document',
            'sec-fetch-mode' : 'navigate',
            'sec-fetch-site' : 'same-origin',
            'upgrade-insecure-requests' : '1',
            'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'
        }

    def request(self,day,date_start,date_end='',label_block=[]):
        """
        To request data from Wall Street Journal.
        
        ############ FORMAT VARIABLE ###############
        # day -> 1d / 2d / 7d / 30d / 90d / 1y / 4y
        # date_start -> YYYY/MM/DD
        # date_end -> YYYY/MM/DD
        # label_block -> ['Opinion']
        #############################################
        """
        self.date_start = date_start
        self.date_end = date_end
        self.day = day
        self.label_block = label_block

        # Start to request
        if self.day == '1d':
            self.date_start = date_start.replace('/','')
            res = requests.get(self.url_day.format(self.date_start),headers = self.headers)
        else:
            res = requests.get(self.url_day_above.format(
                self.date_start,self.date_end,self.isAdvanced,   # Dynamic input variable
                self.day,self.andor,self.sort,self.source        # Dynamic input variable
            ) + '&page={}'.format(self.page),headers = self.headers)
        self.get_each_news_data(res)

    def get_each_news_data(self,res):
        """
        To get link from the main website for collecting data.
        """
        skip = 0
        if self.day == '1d':
            raw_data = bs(res.content.decode(),'html.parser') # Initialize bs4 to clear data
            for no,ele in enumerate(raw_data.ol.find_all('article')): # Get the link from every news
                self.links_each_news[str(no)] = {'type' : ele.span.get_text(),'link' : ele.a['href']}
                print('Getting links from each page! Link : {}'.format(no + 1))
        else:
            raw_data = bs(res.content.decode(),'lxml')
            total_page = int(raw_data.find_all('li',class_ = 'results-count')[1].get_text().split(' ')[1])
            total_download = raw_data.find('li',class_ = 'results-count').get_text().split(' ')[2]
            count = 0

            for page_num in range(total_page):     
                res = requests.get(self.url_day_above.format(
                    self.date_start,self.date_end,self.isAdvanced,   # Dynamic input variable
                    self.day,self.andor,self.sort,self.source        # Dynamic input variable
                ) + '&page={}'.format(page_num+1),headers = self.headers)
                raw_data = bs(res.content.decode(),'lxml')

                try:
                    raw_data = self.is_empty(raw_data.find('ul',class_ = 'items hedSumm').find_all('div',class_ = 'item-container headline-item'))
                except:
                    skip+=1
                    print('Error : SKIP 1 Files!')
                    continue

                for ele in raw_data:
                    count+=1
                    self.links_each_news[str(count)] = {
                        'type' : self.is_empty(ele.a.get_text()),
                        'link' : 'https://www.wsj.com' + self.is_empty(ele.h3.a['href'])
                    }
                print('Getting links from each page! Page : {} / {}'.format(page_num + 1,total_page))
            self.to_JSON('Links_Each_News',self.links_each_news,total_download)
        print('Get links complete !')
        self.process_data(total_download)

    def process_data(self,total_download):
        """
        To process the raw data.
        """
        self.count = 0 # Count download data
        self.to_pickle(self.links_each_news)
        print('Total Download: {}'.format(total_download))
        pool = mp.Pool()
        res = pool.map(self.process_each,self.links_each_news)
        self.data_to_df = [ data for data in res if data != None ]
        # for each_no in self.links_each_news:
        #     pip = mp.Process(target = self.process_each,args = (q,each_no,label_block,))
            # result = self.process_each(each_no,label_block)
            # pip.start()
            # result = q.get()
            # if result:
            #     self.data_to_df.append(result)
            #     count+=1 # Counting number of downloaded article
            #     print('Downloading.... {} / {}'.format(count,total_download))
        print('Number of download data: {} / {}'.format(len(self.data_to_df),total_download))
        self.to_dataframe()
    
    def process_each(self,each_no):
        try:
            if self.links_each_news[each_no]['type'] not in self.label_block: # Classify data by label condition 
                content = ''
                options = webdriver.ChromeOptions()
                options.add_argument('headless')  
                driver = webdriver.Chrome(options = options)
                driver.get(self.links_each_news[each_no]['link'])
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'wsj-article-headline')))
                res_each = driver.page_source
                raw_data_each = bs(res_each,'html.parser')
                title = self.is_empty(raw_data_each.find('h1',class_ = 'wsj-article-headline')).get_text() # Get title
                # Get sub-title date with different way
                try:
                    sub_title = self.is_empty(raw_data_each.find('h2',class_ = 'sub-head')).get_text()
                except:
                    sub_title = ''
                # Get article content with different way
                try:
                    for each_para in raw_data_each.find('div',class_ = 'wsj-snippet-body').find_all('p'):
                        content = content + format(each_para.get_text()) # Get content(might be partial content)
                except:
                    for each_para in raw_data_each.find('div',class_ = 'article-content').find_all('p'):
                        content = content + format(each_para.get_text()) # Get content(might be partial content)
                # Get article date with different way
                try:
                    d_date = raw_data_each.time.get_text().split('Updated')[1].split('ET')[0].split(' ')
                    date =  d_date[2].split(',')[0] + '-' + self.convert_month(d_date[1]) + '-' + d_date[3]
                except:
                    d_date = [d for d in raw_data_each.time.get_text().split(' ') if d != '']
                    date = d_date[2].split(',')[0] + '-' + self.convert_month(d_date[1]) + '-' + d_date[3]
                # Push scrapped data to list
                # self.data_to_df.append([date,self.links_each_news[each_no]['type'],title,sub_title,content])
                driver.close()
                # self.count+=1 # Counting number of downloaded article
                # print('Downloading.... {}'.format(self.count))
                return [date,self.links_each_news[each_no]['type'],title,sub_title,content]
                # sleep(randint(1,3)) # Pause 1 sec to avoid IP block
        except Exception as e: # Print out error news
            self.print_err(self.links_each_news[each_no]['type'],self.links_each_news[each_no]['link'],each_no,e)

    def to_dataframe(self):
        """
        To change clean data to dataframe.
        """
        columns = ['date','label','title','sub_title','content'] # Columns' name
        self.df = pd.DataFrame(self.data_to_df,columns = columns)

        # Clean "ENTER" symbol
        self.df['title'] = self.df['title'].apply(self.replace_sym)
        self.df['sub_title'] = self.df['sub_title'].apply(self.replace_sym)
        self.df['content'] = self.df['content'].apply(self.replace_sym)

    def to_csv(self):
        """
        To save as csv file.
        """
        file_name = './wsj_' + self.date_start.replace('/','') + '_' + self.date_end.replace('/','') + '.csv'
        self.df.to_csv(file_name,index = False,header = True,encoding='utf-8')
    
    def to_JSON(self,file_name,dict_file,indent):
        """
        To save as JSON file.
        """
        out_file = open("{}.json".format(file_name), "w")  
        json.dump(dict_file, out_file, indent = indent)  
        out_file.close()  

    def to_pickle(self,dict_):
        if dict_:
            file_name = './wsj_' + self.date_start.replace('/','') + '_' + self.date_end.replace('/','') + '.pkl'
            with open(file_name,'wb') as f:
                pickle.dump(dict_,f)
                f.close()
            print('System: Covert pickle successfully! File name <' + file_name + '>')
        else:
            print('Error: Failed to save data! EMPTY CONTENT')

    def read_pickle(self,target_path:None,file_name):
        TARGET_PATH = 'C:/Users/sefx5/Desktop/'
        target_path = self.check_exist(target_path,TARGET_PATH)
        try:
            with open(target_path + file_name,'rb') as f:
                content = pickle.load(f)
                print('System: Read pickle successfully!')
                return content
        except:
            print('Error: Failed to read file!')
############################## OPTIONAL FUNCTION ##############################
    def check_exist(self,key_,val_):
        if key_ == None or key_ == '':
            return val_
        else:
            return key_

    def is_empty(self,content):
        """
        To check content is empty or is existing.
        """
        if content == None:
            return ''
        else:
            return content

    def replace_sym(self,content):
        """
        To replace "ENTER" symbol.
        """
        return content.replace('\n','')

    def convert_month(self,month):
        """
        To convert month in number format or word format.
        """
        month_dict = {
            'January' : 1,
            'February' : 2,
            'March' : 3,
            'April' : 4,
            'May' : 5,
            'June' : 6,
            'July' : 7,
            'August' : 8,
            'September' : 9,
            'October' : 10,
            'November' : 11,
            'December' : 12,
            'Jan.' : 1,
            'Feb.' : 2,
            'Mar.' : 3,
            'Apr.' : 4,
            'May.' : 5,
            'Jun.' : 6,
            'Jul.' : 7,
            'Aug.' : 8,
            'Sep.' : 9,
            'Sept.' : 9,
            'Oct.' : 10,
            'Nov.' : 11,
            'Dec.' : 12
        }
        
        try:
            if isinstance(month,str):
                return str(month_dict[month])
            elif isinstance(month,int):
                if month in month_dict.values():
                    key_list = list(month_dict.keys())
                    val_list = list(month_dict.values())
                    return key_list[val_list.index(month)]
                else:
                    print("Error: {}, Month input doesn't match the format!".format(month))
        except:
            print("Error: {}, Month input doesn't match the format!".format(month))

    def print_err(self,type_,link,num,err):
        """
        To print out exception error.
        """
        print('Error: Failed to download! \n' ,
        'Failed Detail: \n' ,
        '-> type: {} \n '.format(type_) ,
        '-> link: {} \n '.format(link) ,
        '-> number: {} \n '.format(num) ,
        '-> error: {} \n '.format(err)
        )
############################## OPTIONAL FUNCTION ##############################

########## 1d FORMAT ##########
# if __name__ == "__main__":
#     DAY = '1d'
#     START_DATE = '2020/04/22' 
#     END_DATE = ''
#     LABEL_BLOCK = ['Opinion']

#     wsj_crawler = wall_street_crawler()
#     wsj_crawler.request(DAY,START_DATE,END_DATE,LABEL_BLOCK)
#     wsj_crawler.to_csv()
#     print(wsj_crawler.df)

####### 1d ABOVE FORMAT #######
if __name__ == "__main__":

    DAY = '30d'
    START_DATE = ['2018/01/01','2018/02/01','2018/03/01','2018/04/01','2018/05/01','2018/06/01','2018/07/01','2018/08/01','2018/09/01','2018/10/01','2018/11/01','2018/12/01']
    END_DATE = ['2018/01/31','2018/02/28','2018/03/31','2018/04/30','2018/05/31','2018/06/30','2018/07/31','2018/08/31','2018/09/30','2018/10/31','2018/11/30','2018/12/31']
    LABEL_BLOCK = ['Opinion']

    for index in range(12):
        wsj_crawler = wall_street_crawler()
        wsj_crawler.request(DAY,START_DATE[index],END_DATE[index],LABEL_BLOCK)
        wsj_crawler.to_csv()
        # print(wsj_crawler.df)
