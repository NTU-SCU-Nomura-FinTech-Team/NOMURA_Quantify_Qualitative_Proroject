# import praw # 由於筆數限制最多1千筆
import pandas as pd
import datetime as dt
import time
import requests

# Create the columns name
reddit_save_column = ['date','score','title','content','comment']

# Customize setting
KEY_WORD = 'fund' # Searching keyword
LIMITATION = 1000 # Number of data to save
START_DATE = '2019-12-01' #FIX FORMAT YYYY-MM-DD (2020-01-02)
CURRENT_DATE = str(dt.date.today()) # To name csv follow by date

# Create a space for data collection
data_collection = []

# PushshiftAPI for submission and comments
reddit_api_submission = 'https://api.pushshift.io/reddit/search/submission/?limit={}&q={}&after={}'.format(str(LIMITATION),str(KEY_WORD),str(START_DATE))
reddit_api_comment = 'https://api.pushshift.io/reddit/search/comment/?limit={}&link_id={}&fields=body'

# To request data from API
res_data_title = requests.get(reddit_api_submission)
res_title = res_data_title.json()['data']

# Do try-except in case any error happen
try:
    # To collect forum's title and comment
    for count,each_res in enumerate(res_title):
        # date = str(pd.to_datetime(each_res['retrieved_on'])).split(' ')[0]
        date = time.strftime("%Y-%m-%d",time.gmtime(each_res['retrieved_on']))
        score = each_res['score']
        title = each_res['title']
        self_text = each_res['selftext']
        link_id = each_res['id']
        num_comment = each_res['num_comments']
        comments = ""
        if num_comment > 0: # Collect comments if exist
            res_data_comment = requests.get(reddit_api_comment.format(num_comment,link_id))
            res_comment = res_data_comment.json()['data']
            for comment in res_comment:
                comments = comments + "{}".format(comment['body'] + '\n ')
        data_collection.append([date,score,title,self_text,comments]) # Append data to created dataframe
        print("Progress in " + str(count+1) + "/{}".format(LIMITATION))
except Exception as e:
    print("Error: " + str(e) + '. Link ID:' + link_id)

# Create a dataframe with data collection
df = pd.DataFrame(data_collection,columns = reddit_save_column)

# Export dataframe to csv
df.to_csv('reddit_fund_with_comments_' + CURRENT_DATE + '.csv')