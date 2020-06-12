import json
import ast
import requests
from tool import excelize
from tool import stack
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from config import TELEGRAM_WEBHOOK_URL,TELEGRAM_BASE
from PIL import Image
from io import BytesIO

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
        excel = excelize.Excelize(None)

        self.temp_job = stack.Stack()
        self.temp_text = ''
        self.temp_fund = []
        self.status = 'unlogin'
        self.log_data = {}
        self.user = ''
        ########## Status ##########
        # unlogin 未登錄
        # check_acc 確認賬號
        # check_pass 確認密碼
        # login 登陸中
        # sign out 登出
        ########## Status ##########
        self.df_input = excel.df_input
        self.df_survey = excel.df_survey
        self.df_fund = excel.df_fund
        self.df_acc = excel.df_acc

    def run_process(self,in_msg):
        #BUG 不確定 response 格式 [已解決]
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
        self.last_name = in_msg['from']['last_name']

    def run_data(self):
        SUGGESTION = '推薦:野村鴻利基金'
        keyword = self.content.replace(' ','')
        # print(keyword)
        print(self.temp_job.get_stack())
        # print(self.log_data)
        if (keyword not in ['確認賬號','確認密碼']) & (self.temp_job.top() in ['會員登錄','確認賬號','用戶分析','回測績效','輸入賬號','輸入密碼']):
            prev_job = self.temp_job.top()
            success = self.run_prev_data(prev_job)
            return success

        if keyword in self.df_fund['fund_type'].values.tolist():
            success = self.run_prev_data(keyword)
            return success

        if keyword in ['main','/start','主目錄','hello','hey']:
            self.temp_job.renew()
            success = self.f_main()
        elif keyword in ['suggestion',SUGGESTION]:
            success = self.f_suggestion(SUGGESTION)
        elif keyword in ['freshman','我是新手']:
            success = self.f_freshman()
        elif keyword in ['會員登錄','確認賬號','確認密碼']:
            success = self.f_login(keyword)
        elif keyword in ['fund_website','野村官網','官網']:
            success = self.f_website()
        elif keyword in ['fund_search','基金查詢','查詢基金']:
            success = self.f_fund_search()
        elif keyword in ['client_anl','用戶分析']:
            success = self.f_client_anl()
        elif keyword in ['backtest','回測績效']:
            success = self.f_backtest()
        elif keyword in ['fund_qa','Q & A']:
            success = self.f_fund_qa()
        elif keyword in ['sign_up','辦理注冊','申請賬號']:
            success = self.f_register()
        elif keyword in ['我的基金項目','我的基金目錄']:
            success = self.f_show_fund()
        elif keyword in ['我想購買']:
            success = self.f_buy_fund()
        else:
            success = self.f_others()
        return success

    def run_prev_data(self,prev_job:str):
        if self.content == '':
            text = '非常抱歉，賬號與密碼不能為空喲！'
            json_ = self.to_json(chat_id = self.chat_id,text = text)
            self.send_data([json_])
            return True

        try:
            #BUG 輸入密碼或内容不能爲空
            if prev_job == '會員登錄':
                self.temp_job.push('輸入賬號')
                self.log_data['log_acc'] = self.content
            elif prev_job == '確認賬號': 
                self.temp_job.push('輸入密碼')
                self.log_data['log_pass'] = self.content
            elif prev_job in self.df_fund['fund_type'].values.tolist():
                self.temp_fund = [prev_job]
                self.check_fund_data()
            else:
                checking = self.df_fund[self.df_fund['fund_type'] == prev_job]
                len_ = len(checking)
                if len_ > 0:
                    reply_keyboard,temp = [],[]
                    for no,item in enumerate(list(checking['fund_particular'])):
                        dict_ = self.to_dict(text = item,callback_data = item)
                        temp.append(dict_)
                        if (((no+1) % 2) == 0) | (no+1 == len_):
                            reply_keyboard.append(temp)
                            temp = []
                    self.temp_text = text = '請選擇基金項目以瞭解基金項目！'
                    json_ = self.to_json(chat_id = self.chat_id,text = text,reply_markup = reply_keyboard)
                else:
                    json_ = self.to_json(chat_id = self.chat_id,text = '抱歉，查無資訊！')
                self.send_data([json_])
        except Exception as e:
            print('Error(run_prev_data): ',e)
        return True

    def f_main(self):
        print('System(f_main) : Running...',self.content)
        self.temp_job.push('main')
        if self.status in ['unlogin','check_acc','check_pass']:
            self.temp_text = text = list(self.df_input[self.df_input['symbol'] == 'main_unlogin']['reply_text'])[0]
            reply_inline_keyword = {                                                                                                             \
                "inline_keyboard" : ast.literal_eval(list(self.df_input[self.df_input['symbol'] == 'main_unlogin']['reply_inline_keyword'])[0])  \
            }
        if self.status in ['login']:
            self.temp_text = text = list(self.df_input[self.df_input['symbol'] == 'main_login']['reply_text'])[0]
            reply_inline_keyword = {                                                                                                           \
                "inline_keyboard" : ast.literal_eval(list(self.df_input[self.df_input['symbol'] == 'main_login']['reply_inline_keyword'])[0])  \
            }
        json_ = self.to_json(chat_id = self.chat_id,text = text,reply_markup = reply_inline_keyword)
        success = self.send_data([json_])
        return success

    def f_suggestion(self,suggestion:str):
        #BUG 同基金不同幣別 [未解決]
        print('System(f_suggestion) : Running...',self.content)
        self.temp_job.push('suggestion')
        self.temp_fund = [suggestion.split(':')[1]]
        data = self.df_fund[self.df_fund['fund_particular'] == self.temp_fund[0]].values.tolist()[0]
        text = list(self.df_input[self.df_input['symbol'] == 'suggestion']['reply_text'])[0]
        self.temp_text = text = text.format(   \
            data[1],data[2],data[3],data[4],   \
            data[5],data[6],data[7],           \
            str(data[8]).replace('<br/>','\n') \
        )
        reply_inline_keyword = {                                                                                                           \
            "inline_keyboard" : ast.literal_eval(list(self.df_input[self.df_input['symbol'] == 'suggestion']['reply_inline_keyword'])[0])  \
        }
        json_ = self.to_json(chat_id = self.chat_id,text = text,reply_markup = reply_inline_keyword)
        success = self.send_data([json_])
        return success

    def f_freshman(self):
        print('System(f_freshman) : Running...',self.content)
        self.temp_job.push('freshman')
        self.temp_text = text = list(self.df_input[self.df_input['symbol'] == 'freshman']['reply_text'])[0]
        reply_inline_keyword = {                                                                                                        \
            "inline_keyboard" : ast.literal_eval(list(self.df_input[self.df_input['symbol'] == 'freshman']['reply_inline_keyword'])[0]) \
        }
        json_ = self.to_json(chat_id = self.chat_id,text = text,reply_markup = reply_inline_keyword)
        success = self.send_data([json_])
        return success

    def f_login(self,status):
        print('System(f_login) : Running...',self.content)
        self.temp_job.push(status)
        if status == '會員登錄':
            self.temp_text = text = list(self.df_input[self.df_input['symbol'] == 'login']['reply_text'])[0]
            reply_inline_keyword = {                                                                                                     \
                "inline_keyboard" : ast.literal_eval(list(self.df_input[self.df_input['symbol'] == 'login']['reply_inline_keyword'])[0]) \
            }
            reply_keyboard = {                                                                                              \
                "keyboard" : ast.literal_eval(list(self.df_input[self.df_input['symbol'] == 'login']['reply_keyboard'])[0]) \
            }
            json_msg = self.to_json(chat_id = self.chat_id,text = text,reply_markup = reply_inline_keyword)
            json_keyboard = self.to_json(chat_id = self.chat_id,text = '確認賬號後，請點擊【確認賬號】！',reply_markup = reply_keyboard)
            success = self.send_data([json_msg,json_keyboard],['sendMessage','sendMessage'])
        elif status == '確認賬號':
            self.temp_text = text = list(self.df_input[self.df_input['symbol'] == 'check_acc']['reply_text'])[0]
            reply_inline_keyword = {                                                                                                     \
                "inline_keyboard" : ast.literal_eval(list(self.df_input[self.df_input['symbol'] == 'check_acc']['reply_inline_keyword'])[0]) \
            }
            reply_keyboard = {                                                                                              \
                "keyboard" : ast.literal_eval(list(self.df_input[self.df_input['symbol'] == 'check_acc']['reply_keyboard'])[0]) \
            }
            json_msg = self.to_json(chat_id = self.chat_id,text = text,reply_markup = reply_inline_keyword)
            json_keyboard = self.to_json(chat_id = self.chat_id,text = '確認密碼後，請點擊【確認密碼】！',reply_markup = reply_keyboard)
            success = self.send_data([json_msg,json_keyboard],['sendMessage','sendMessage'])
            self.status = 'check_acc'
        elif status == '確認密碼':
            check_result = self.check_acc()
            self.status = 'check_pass'
            if check_result:
                role = list(self.df_acc[self.df_acc['log_acc'] == self.log_data['log_acc']]['role'])[0]
                if role == 'manager':
                    self.temp_text = text = list(self.df_input[self.df_input['symbol'] == 'check_log_s_manager']['reply_text'])[0]
                    reply_inline_keyword = {                                                                                                                   \
                        "inline_keyboard" : ast.literal_eval(list(self.df_input[self.df_input['symbol'] == 'check_log_s_manager']['reply_inline_keyword'])[0]) \
                    }
                if role == 'client':
                    self.temp_text = text = list(self.df_input[self.df_input['symbol'] == 'check_log_s_client']['reply_text'])[0]
                    reply_inline_keyword = {                                                                                                                   \
                        "inline_keyboard" : ast.literal_eval(list(self.df_input[self.df_input['symbol'] == 'check_log_s_client']['reply_inline_keyword'])[0])  \
                    }
                json_ = self.to_json(chat_id = self.chat_id,text = text,reply_markup = reply_inline_keyword)
                success = self.send_data([json_])
                self.status = 'login'
            else:
                self.temp_text = text = list(self.df_input[self.df_input['symbol'] == 'check_log_f']['reply_text'])[0]
                reply_inline_keyword = {                                                                                                           \
                    "inline_keyboard" : ast.literal_eval(list(self.df_input[self.df_input['symbol'] == 'check_log_f']['reply_inline_keyword'])[0]) \
                }
                json_ = self.to_json(chat_id = self.chat_id,text = text,reply_markup = reply_inline_keyword)
                success = self.send_data([json_])
                self.status = 'unlogin'
        else:
            success = False
        return success

    def f_website(self):
        print('System(f_website) : Running...',self.content)
        self.temp_job.push('fund_website')
        try:
            self.temp_text = text = '歡迎參考野村基金官網！'
            reply_inline_keyword = {                                                                                                            \
                "inline_keyboard" : ast.literal_eval(list(self.df_input[self.df_input['symbol'] == 'fund_website']['reply_inline_keyword'])[0]) \
            }
            json_ = self.to_json(chat_id = self.chat_id,text = text,reply_markup = reply_inline_keyword)
            success = self.send_data([json_])
        except Exception as e:
            success = False
            print('Error(f_website): ',e)
        return success

    def f_fund_qa(self):
        print('System(f_fund_qa) : Running...',self.content)
        self.temp_job.push('fund_qa')
        self.temp_text = text = '歡迎參考野村基Q & A！'
        reply_inline_keyword = {                                                                                                       \
            "inline_keyboard" : ast.literal_eval(list(self.df_input[self.df_input['symbol'] == 'fund_qa']['reply_inline_keyword'])[0]) \
        }
        json_ = self.to_json(chat_id = self.chat_id,text = text,reply_markup = reply_inline_keyword)
        success = self.send_data([json_])
        return success

    def f_others(self):
        print('System(f_others) : Running...',self.content)
        try:
            self.temp_text = text = self.content
            json_ = self.to_json(chat_id = self.chat_id,text = text)
            success = self.send_data([json_])
        except Exception as e:
            success = True
            print('Error(f_others): ',e)
        return success

    def f_backtest(self):
        return True

    def f_register(self):
        print('System(f_register) : Running...',self.content)
        self.temp_job.push('sign_up')
        self.temp_text = text = list(self.df_input[self.df_input['symbol'] == 'sign_up']['reply_text'])[0]
        reply_inline_keyword = {                                                                                                        \
            "inline_keyboard" : ast.literal_eval(list(self.df_input[self.df_input['symbol'] == 'sign_up']['reply_inline_keyword'])[0])  \
        }
        json_ = self.to_json(chat_id = self.chat_id,text = text,reply_markup = reply_inline_keyword)
        success = self.send_data([json_])
        return success

    def f_client_anl(self):
        print('System(f_client_anl) : Running...',self.content)
        self.temp_job.push('用戶分析')
        try:
            
            success = True
        except Exception as e:
            success = False
            print('Error(f_client_anl): ',e)
        return success

    def f_fund_search(self):
        print('System(f_fund_search) : Running...',self.content)
        self.temp_job.push('fund_search')
        try:
            self.temp_text = text = list(self.df_input[self.df_input['symbol'] == 'fund_search']['reply_text'])[0]
            reply_inline_keyword = {                                                                                                            \
                "keyboard" : ast.literal_eval(list(self.df_input[self.df_input['symbol'] == 'fund_search']['reply_keyboard'])[0])  \
            }
            json_ = self.to_json(chat_id = self.chat_id,text = text,reply_markup = reply_inline_keyword)
            success = self.send_data([json_])
        except Exception as e:
            success = False
            print('Error(f_fund_search): ',e)
        return success

    def f_show_fund(self):
        print('System(f_show_fund) : Running...',self.content)
        self.temp_job.push('show_fund')
        try:
            if self.status == 'login':
                self.temp_text = text = list(self.df_input[self.df_input['symbol'] == 'fund_list_s']['reply_text'])[0]
                reply_inline_keyword = {                                                                                          \
                    "inline_keyboard" : ast.literal_eval(list(self.df_acc[self.df_acc['log_acc'] == self.user]['fund_item'])[0])  \
                }
                json_ = self.to_json(chat_id = self.chat_id,text = text,reply_markup = reply_inline_keyword)
                success = self.send_data([json_])
            else:
                self.temp_text = text = list(self.df_input[self.df_input['symbol'] == 'fund_list_f']['reply_text'])[0]
                reply_inline_keyword = {                                                                                                            \
                    "inline_keyboard" : ast.literal_eval(list(self.df_input[self.df_input['symbol'] == 'fund_list_f']['reply_inline_keyword'])[0])  \
                }
                json_ = self.to_json(chat_id = self.chat_id,text = text,reply_markup = reply_inline_keyword)
                success = self.send_data([json_])
        except Exception as e:
            success = False
            print('Error(f_show_fund): ',e)
        return success

    def f_buy_fund(self):
        print('System(f_buy_fund) : Running...',self.content)
        self.temp_job.push('f_buy_fund')
        try:
            self.temp_text = text = list(self.df_input[self.df_input['symbol'] == 'buy_fund']['reply_text'])[0]
            reply_inline_keyword = {                                                                                                        \
                "inline_keyboard" : ast.literal_eval(list(self.df_input[self.df_input['symbol'] == 'buy_fund']['reply_inline_keyword'])[0]) \
            }
            json_ = self.to_json(chat_id = self.chat_id,text = text,reply_markup = reply_inline_keyword)
            success = self.send_data([json_])
        except Exception as e:
            success = False
            print('Error(f_buy_fund): ',e)
        return success

    def to_json(self,**kwargs):
        _json  = kwargs
        json_ = json.dumps(_json)
        return json_

    def to_dict(self,**kwargs):
        _dict = kwargs
        return _dict

    def send_data(self,json_:list,type_=['sendMessage']):
        headers = {"Content-Type": "application/json"}
        payload = json_
        try:
            for no,action in enumerate(type_):
                url = TELEGRAM_BASE + '/' + action
                res = requests.post(url,headers = headers,data = payload[no])
            return True if res.status_code == 200 else False
        except Exception as e:
            print('Error(send_data): ',e)

    def check_acc(self):
        try:
            checking = len(self.df_acc[
                (self.df_acc['log_pass'] == self.log_data['log_pass']) & 
                (self.df_acc['log_acc'] == self.log_data['log_acc'])
            ])
        except:
            checking = False
        self.user = self.log_data['log_acc']
        result = True if checking == True else False
        return result

    def check_fund_data(self):
        #BUG 信息内容不包括圖片及回測效率 [未解決]
        self.temp_job.push('fund_search')
        fund_particular = self.temp_fund
        for item in fund_particular:
            data = self.df_fund[self.df_fund['fund_particular'] == item].values.tolist()[0]
            text = list(self.df_input[self.df_input['symbol'] == 'search_fund_s']['reply_text'])[0]
            self.temp_text = text = text.format(   \
                data[1],data[2],data[3],data[4],   \
                data[5],data[6],data[7],           \
                str(data[8]).replace('<br/>','\n') \
            )
            reply_inline_keyword = {                                                                                                            \
                "inline_keyboard" : ast.literal_eval(list(self.df_input[self.df_input['symbol'] == 'search_fund_s']['reply_inline_keyword'])[0])  \
            }
            json_ = self.to_json(chat_id = self.chat_id,text = text,reply_markup = reply_inline_keyword)
            self.send_data([json_])

    @staticmethod
    def webhook_init(webhook_link):
        """
        To connect the API gateway service.
        """
        requests.get(webhook_link)

#TODO
# 辦理賬號
# 用戶分析