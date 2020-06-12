import requests
import json
import ast
from function import function
from tool import excelize,stack
from config import TELEGRAM_WEBHOOK_URL,TELEGRAM_BASE

#TODO
# print 該 function 與内容
# self.temp_job 寫入工作記錄
# 寫入 text & button(optional)
# 把 text 寫入 self.temp_text 
# 將 dict 轉 json
# 修改狀態 status(optional)
# 發送信息 send_data
# return 結果
# 將 function 之 require input 補在 run_process

class TelegramBot:
    def __init__(self):
        """
        To initialize packages and variable.
        """
        self.func = function.Function(excelize)
        self.temp_job = stack.Stack()
        self.temp_text = ''
        self.status = 'unlogin'
        self.log_data = {}
        self.fund_type = ast.literal_eval(list(self.func.df_survey[self.func.df_survey['no'] == 4]['reply_inline_keyboard'])[0])
        self.fund_particular = self.func.df_fund['fund_particular'].values.tolist()
        self.survey_list = []

    def run_process(self,in_msg):
        """
        To catch basic data when machine received message.

        params:
            *in_msg : json : each message from Telegram server.
        """
        try:
            try:
                in_msg = in_msg['message']
                self.content = in_msg['text']
            except:
                in_msg = in_msg['callback_query']
                self.content = in_msg['data']
        except Exception as e:
            print('Error(run_process): ',e)

        # Assign to variable
        self.chat_id = in_msg['from']['id']
        self.first_name = in_msg['from']['first_name']
        # print(in_msg)
        # self.last_name = in_msg['from']['last_name']

    def run_data(self):
        """
        To classify content into an appropriate function.
        """
        keyword = self.content.replace(' ','')
        prev_job = self.temp_job.top()
        if (prev_job[0] == 'q') & ((keyword[0] != 'q') & (keyword != '確認選擇')):
            alert = [self.func.tool_to_json(                    \
                chat_id = self.chat_id,                         \
                text = '用戶分析已開始，請完成填寫後才能結束環節！' \
            )]
            success = self.send_data(alert)
            return success
        
        if ((keyword not in ['確認賬號','確認密碼']) & (prev_job in ['會員登錄','確認賬號'])):
            success = self.save_temp_memory(prev_job,keyword)
            return success

        if keyword in ['/start','menu','Hello','哈嘍','野村小夥伴','小夥伴','主目錄']:
            self.temp_job.renew()
            self.temp_job.push('main')
            output = self.func.main(self.chat_id)
        elif (keyword == '推薦:野村鴻利基金') & (prev_job == 'main'):
            self.temp_job.push('suggestion')
            output = self.func.suggestion(self.chat_id,'野村鴻利基金')
        elif keyword == '基金查詢':
            self.temp_job.push('fund_search')
            output = self.func.fund_search(self.chat_id,keyword)
        elif keyword in ['fund_qa','我有問題']:
            # 由於 QA 發生與用戶有疑問之時，因此不考慮實質工作範圍。
            output = self.func.qa(self.chat_id)
        elif keyword == '野村官網':
            # 由於 QA 發生與用戶有疑問之時，因此不考慮實質工作範圍。
            output = self.func.website(self.chat_id)
        elif (keyword in ['會員登錄','確認賬號','確認密碼']) & (prev_job in ['main','會員登錄','確認賬號','確認密碼','登出']):
            self.temp_job.push(keyword)
            if keyword == '確認密碼':
                output = self.func.login(self.chat_id,keyword,self.log_data)
                success = self.send_data(output)
            else:
                output = self.func.login(self.chat_id,keyword)
                success = self.send_data(output,['sendMessage','sendMessage'])
            return success
        elif keyword == '我是新手':
            self.temp_job.push('我是新手')
            output = self.func.freshman(self.chat_id)
        elif (keyword in self.fund_type) & (prev_job == 'fund_search'):
            # 由於用戶可能重複搜尋不同基金類型，因此不計工作範圍内
            output = self.func.fund_search_result(self.chat_id,keyword)
        elif keyword in self.fund_particular:
            # 由於用戶可能重複搜尋不同基金項目，因此不計工作範圍内
            output = self.func.fund_item_indv(self.chat_id,keyword)
        elif ((keyword[0] == 'q') | (keyword == '確認選擇'))     \
            & ((prev_job in ['我是新手','辦理賬號']) | (prev_job[0] == 'q')):
            print(keyword[:2])
            if keyword == 'q_start':
                self.temp_job.push('q0_start')
                output = self.func.freshman_question(self.chat_id,'q0_none') # out1
            elif keyword[:2] in ['q4','q5','q6','q8','q9']:
                success = self.save_temp_memory(keyword[:2],keyword[2:])
                return success
            elif (keyword == '確認選擇') & (prev_job[:2] in ['q3','q4','q5','q7','q8']):
                cur_quest = f'q{int(prev_job[1:2])+1}_'
                self.temp_job.push(cur_quest)
                output = self.func.freshman_question(self.chat_id,cur_quest,self.survey_list)
            elif keyword[:3] == 'q10':
                self.temp_job.push('完成分析')
                output = self.func.freshman_question(self.chat_id,keyword)
            else:
                self.temp_job.push(keyword)
                output = self.func.freshman_question(self.chat_id,keyword)
                if len(output) > 1:
                    success = self.send_data(output,['sendMessage']*len(output))
                    return success
        elif keyword[:4] in ['建立賬號','辦理賬號']:
            self.temp_job.push('辦理賬號')
            data = keyword.split(',')[1:]
            if len(data) > 2:
                username,password,set_fund = data[0],data[1],data[2:]
                output = self.func.create_acc(self.chat_id,username,password,set_fund)
            output = self.func.create_acc(self.chat_id)
        elif keyword == '我想購買':
            self.temp_job.push(keyword)
            output = self.func.buy_fund(self.chat_id)
        elif keyword == '登出':
            self.temp_job.push(keyword)
            output = self.func.log_out(self.chat_id)
            success = self.send_data(output,['sendMessage','sendMessage'])
            return success
        elif keyword == '我的基金項目':
            self.temp_job.push(keyword)
            output = self.func.my_fund_list(self.chat_id)
        else:
            # 由於用戶可能輸入有誤，因此不計工作範圍内
            output = self.func.others(self.chat_id,keyword)
        success = self.send_data(output)
        return success

    def save_temp_memory(self,prev_job,keyword):
        """
        To save temporary message, such as login detail.

        params:
            prev_job : str : previos action recorded by machine
            keyword : str | int : current message data
        """
        if prev_job in ['確認密碼','會員登錄']:
            print('Save login account!')
            self.log_data['log_acc'] = keyword
        if prev_job == '確認賬號':
            print('Save login password!')
            self.log_data['log_pass'] = keyword
        if prev_job[0] == 'q':
            print('Save favourite fund data',keyword.split('_')[1])
            self.survey_list.append(keyword.split('_')[1])
        return True

    def send_data(self,json_:list,type_=['sendMessage']):
        """
        To send data by API.

        params:
            *json_ : list : the list of message to be send
            *type_ : list : the API method use of a message
        """
        headers = {"Content-Type": "application/json"}
        payload = json_
        try:
            for no,action in enumerate(type_):
                url = TELEGRAM_BASE + '/' + action
                res = requests.post(url,headers = headers,data = payload[no])
            return True if res.status_code == 200 else False
        except Exception as e:
            print('Error(send_data): ',e)

    @staticmethod
    def webhook_init(webhook_link):
        """
        To connect the API gateway service.

        params:
            *webhook_link : str : to get connection to Telegram server
        """
        requests.get(webhook_link)

    @staticmethod
    def webhook_del(telegram_token):
        """
        To delete current connection to Telegram server.

        params:
            *telegram_token : str : a token of Telegram chatbot to disconnect
        """
        requests.get(f'https://api.telegram.org/bot{telegram_token}/deleteWebhook')