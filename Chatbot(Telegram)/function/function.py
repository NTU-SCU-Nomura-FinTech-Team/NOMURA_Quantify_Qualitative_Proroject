import json
import ast
import pandas as pd

class Function:
    def __init__(self,excelize:object):
        """
        To initialize object and variable.

        params:
            *excel : object :  get data-require from package(Excelize) 
        """
        excel = excelize.Excelize()
        # excel.local('C:/Users/sefx5/Desktop/Fintech_Nomura_Chatbot/Telegram_Import_Document.xlsx')
        AWS = {
            'aws_access_key_id' : 'ASIA3KNCBNJVOL2FZOPU',
            'aws_secret_access_key' : '9pQMA6tVeh4F4JU1H1tn8X9DKZJhx8Q+J48PoUWs',
            'aws_session_token' : 'FwoGZXIvYXdzENr//////////wEaDEMDIEz3gvCo4TvSryLCAUun/SGJ0PKMCYS3sdYIkoIETMJaFP1nsKQcI1l66bb4W94dX8Y2YA3Lq45Uc5PcQ7CQM/VMDChKlwCk+Vnund/sU+Kxz+LvM7o3n75oz7U1G9LO6E/mFltOq3wmCwWG+B2NoGSr6n9tT5wrD4lGVQVatGE6DUGqFiwnOuxKilF6ILGbzsJFF2bqIBdR3MTj0fRKRKAyw41QtV7PWkhruRFnZZAfuWKRYUb4KbKxpfHaK7+SZa6X+R/Sh3m7Xdc3o3kEKIXOh/cFMi1t5ocUfwlJUrkimpeoRdWRiRJOHWN9CkZPHqigChYBtvBqYp2KU6JK7NKl6Fg='
        }
        excel.boto(aws = AWS)

        self.temp_fund = []
        self.temp_client_aly = {}
        self.status = 'unlogin'
        self.user = ''
        ########## Status ##########
        # unlogin 未登錄
        # check_acc 確認賬號
        # check_pass 確認密碼
        # login 登陸中
        ########## Status ##########
        print(excel)
        self.df_input = excel.df_input
        self.df_survey = excel.df_survey
        self.df_fund = excel.df_fund
        self.df_acc = excel.df_acc

    def main(self,chat_id:str,status=None):
        """
        To show main menu in the chatbot.

        params:
            *chat_id : str : chat id given by Telegram.

        ways:
            *direct message(['/start','menu','Hello','哈嘍','野村小夥伴','小夥伴'])
            *button from any
        """
        print('System(main) : Running...')
        if status == None:
            status = self.status

        if status == 'login':
            text = list(self.df_input[self.df_input['symbol'] == 'main_login']['reply_text'])[0]
            reply_inline_keyword = {                                                                                                           \
                "inline_keyboard" : ast.literal_eval(list(self.df_input[self.df_input['symbol'] == 'main_login']['reply_inline_keyword'])[0])  \
            }
        else:
            text = list(self.df_input[self.df_input['symbol'] == 'main_unlogin']['reply_text'])[0]
            reply_inline_keyword = {                                                                                                             \
                "inline_keyboard" : ast.literal_eval(list(self.df_input[self.df_input['symbol'] == 'main_unlogin']['reply_inline_keyword'])[0])  \
            }
        json_ = self.tool_to_json(chat_id = chat_id,text = text,reply_markup = reply_inline_keyword)
        return [json_]

    def suggestion(self,chat_id:str,fund_particular:str):
        """
        To show recommend fund item.

        params:
            *chat_id : str : chat id given by Telegram.
            *fund_particular : str : fund particular to recommend.

        ways:
            *button from function(main)

        bug:
            *function will get error in same fund particular in different currency
        """
        print('System(suggestion) : Running...')
        self.temp_fund = [fund_particular]
        fund_data = self.df_fund[self.df_fund['fund_particular'] == fund_particular].values.tolist()[0]
        text = list(self.df_input[self.df_input['symbol'] == 'suggestion']['reply_text'])[0]
        text = text.format(                                            \
            fund_data[1],fund_data[2],fund_data[3],fund_data[4],       \
            fund_data[5],fund_data[6],fund_data[7],                    \
            str(fund_data[8]).replace('<br/>','\n')                    \
        )
        reply_inline_keyword = {                                                                                                           \
            "inline_keyboard" : ast.literal_eval(list(self.df_input[self.df_input['symbol'] == 'suggestion']['reply_inline_keyword'])[0])  \
        }
        json_ = self.tool_to_json(chat_id = chat_id,text = text,reply_markup = reply_inline_keyword)
        return [json_]

    def fund_search(self,chat_id:str,type_:str):
        """
        To get list of fund type.

        params:
            *chat_id : str : chat id given by Telegram.
            *type_ : str : fund particular type to search for.

        ways:
            *direct send
            *button from function(main)
        
        step:
            *主目錄 -> 基金查詢 -> 基金類型列表 -> 基金項目列表 -> 基金資訊（單筆）
            *main -> fund_search -> fund_search_result -> fund_item_indv
        """
        print('System(fund_search) : Running...')
        text = list(self.df_input[self.df_input['symbol'] == 'fund_search']['reply_text'])[0]
        reply_inline_keyword = {                                                                                                      \
            "inline_keyboard" : ast.literal_eval(list(self.df_input[self.df_input['symbol'] == 'fund_search']['reply_inline_keyword'])[0])  \
        }
        json_ = self.tool_to_json(chat_id = chat_id,text = text,reply_markup = reply_inline_keyword)
        return [json_]

    def qa(self,chat_id:str):
        """
        To understand the issues by website.

        params:
            *chat_id : str : chat id given by Telegram.

        ways:
            *direct message(['fund_qa','我有問題'])
        """
        print('System(qa) : Running...')
        text = '歡迎參考野村基Q & A！'
        reply_inline_keyword = {                                                                                                       \
            "inline_keyboard" : ast.literal_eval(list(self.df_input[self.df_input['symbol'] == 'fund_qa']['reply_inline_keyword'])[0]) \
        }
        json_ = self.tool_to_json(chat_id = chat_id,text = text,reply_markup = reply_inline_keyword)
        return [json_]

    def website(self,chat_id:str):
        """
        To search for NOMURA official website.

        params:
            *chat_id : str : chat id given by Telegram.

        ways:
            *button from function(main)
        """
        print('System(website) : Running...')
        text = '歡迎參考野村基金官網！'
        reply_inline_keyword = {                                                                                                       \
            "inline_keyboard" : ast.literal_eval(list(self.df_input[self.df_input['symbol'] == 'fund_website']['reply_inline_keyword'])[0]) \
        }
        json_ = self.tool_to_json(chat_id = chat_id,text = text,reply_markup = reply_inline_keyword)
        return [json_]

    def login(self,chat_id:str,action,log_data=None):
        """
        To execute each step of login.

        params:
            *chat_id : str : chat id given by Telegram.
            *action : any : the step to take action.
            *log_data(optional) : dict : only require in the step of confirm password.

        ways:
            *button from function(main)
        """
        print('System(login) : Running...')
        if self.status == 'login':
            text = '抱歉，您已登錄賬號喲！'
        else:
            if action == '會員登錄':
                text_msg = list(self.df_input[self.df_input['symbol'] == 'login']['reply_text'])[0]
                reply_inline_keyword = {                                                                                                     \
                    "inline_keyboard" : ast.literal_eval(list(self.df_input[self.df_input['symbol'] == 'login']['reply_inline_keyword'])[0]) \
                }
                json_msg = self.tool_to_json(chat_id = chat_id,text = text_msg,reply_markup = reply_inline_keyword)
                
                text_keyboard = '確認賬號後，請點擊【確認賬號】！'
                reply_keyboard = {                                                                                              \
                    "keyboard" : ast.literal_eval(list(self.df_input[self.df_input['symbol'] == 'login']['reply_keyboard'])[0]) \
                }
                json_keyboard = self.tool_to_json(chat_id = chat_id,text = text_keyboard,reply_markup = reply_keyboard)
                return [json_msg,json_keyboard]
            elif action == '確認賬號':
                text_msg = list(self.df_input[self.df_input['symbol'] == 'check_acc']['reply_text'])[0]
                reply_inline_keyword = {                                                                                                     \
                    "inline_keyboard" : ast.literal_eval(list(self.df_input[self.df_input['symbol'] == 'check_acc']['reply_inline_keyword'])[0]) \
                }
                json_msg = self.tool_to_json(chat_id = chat_id,text = text_msg,reply_markup = reply_inline_keyword)

                text_keyboard =  '確認密碼後，請點擊【確認密碼】！'
                reply_keyboard = {                                                                                                  \
                    "keyboard" : ast.literal_eval(list(self.df_input[self.df_input['symbol'] == 'check_acc']['reply_keyboard'])[0]) \
                }
                json_keyboard = self.tool_to_json(chat_id = chat_id,text = text_keyboard,reply_markup = reply_keyboard)
                self.tool_status_update('check_acc')
                return [json_msg,json_keyboard]
            elif action == '確認密碼':
                check_acc = self.tool_check_acc(log_data)
                self.tool_status_update('check_pass')
                if check_acc:
                    self.user = log_data['log_acc']
                    self.tool_status_update('login')
                    role = list(self.df_acc[self.df_acc['log_acc'] == log_data['log_acc']]['role'])[0]
                    if role == 'manager':
                        text = list(self.df_input[self.df_input['symbol'] == 'check_log_s_manager']['reply_text'])[0]
                        reply_inline_keyword = {                                                                                                                   \
                            "inline_keyboard" : ast.literal_eval(list(self.df_input[self.df_input['symbol'] == 'check_log_s_manager']['reply_inline_keyword'])[0]) \
                        }
                    if role == 'client':
                        text = list(self.df_input[self.df_input['symbol'] == 'check_log_s_client']['reply_text'])[0]
                        reply_inline_keyword = {                                                                                                                   \
                            "inline_keyboard" : ast.literal_eval(list(self.df_input[self.df_input['symbol'] == 'check_log_s_client']['reply_inline_keyword'])[0])  \
                        }
                else:
                    text = list(self.df_input[self.df_input['symbol'] == 'check_log_f']['reply_text'])[0]
                    reply_inline_keyword = {                                                                                                           \
                        "inline_keyboard" : ast.literal_eval(list(self.df_input[self.df_input['symbol'] == 'check_log_f']['reply_inline_keyword'])[0]) \
                    }
                json_ = self.tool_to_json(chat_id = chat_id,text = text,reply_markup = reply_inline_keyword)
                return [json_]
            else:
                text = '抱歉，登錄出現問題！'
        json_ = self.tool_to_json(chat_id = chat_id,text = text)
        return [json_]

    def freshman(self,chat_id:str):
        """
        To lead freshman with different action to function(sign_up/freshman_question/main).

        params:
            *chat_id : str : chat id given by Telegram.

        ways:
            *button from function(main)            
        """
        print('System(freshman) : Running...')
        text = list(self.df_input[self.df_input['symbol'] == 'freshman']['reply_text'])[0]
        reply_inline_keyword = {                                                                                                        \
            "inline_keyboard" : ast.literal_eval(list(self.df_input[self.df_input['symbol'] == 'freshman']['reply_inline_keyword'])[0]) \
        }
        json_ = self.tool_to_json(chat_id = chat_id,text = text,reply_markup = reply_inline_keyword)
        return [json_]

    def fund_item_indv(self,chat_id:str,fund_particular:str):
        """
        To show fund data individually with backtest result, fund data, result's link and picture.

        params:
            *chat_id : str : chat id given by Telegram.
            *fund_particular : str : fund particular to search for.

        ways:
            *direct message(<基金項目>)

        bug:
            *function will get error in same fund particular in different currency
            *backtest result, the result's link and picture had missed currently
        """
        print('System(fund_item_indv) : Running...')
        self.temp_fund = [fund_particular]
        fund_data = self.df_fund[self.df_fund['fund_particular'] == fund_particular].values.tolist()[0]
        text = list(self.df_input[self.df_input['symbol'] == 'search_fund_s']['reply_text'])[0]
        text = text.format(                                            \
            fund_data[1],fund_data[2],fund_data[3],fund_data[4],       \
            fund_data[5],fund_data[6],fund_data[7],                    \
            str(fund_data[8]).replace('<br/>','\n')                    \
        )
        reply_inline_keyword = {                                                                                                           \
            "inline_keyboard" : ast.literal_eval(list(self.df_input[self.df_input['symbol'] == 'suggestion']['reply_inline_keyword'])[0])  \
        }
        json_ = self.tool_to_json(chat_id = chat_id,text = text,reply_markup = reply_inline_keyword)
        return [json_]

    def fund_item_group(self,chat_id:str,fund_particular:list):
        """
        To show fund data in group with backtest result, fund data.

        params:
            *chat_id : str : chat id given by Telegram.
            *fund_particular : list : fund particular to search for.

        ways:
            *button from function(freshman_qustion[q8])

        bug:
            *function will get error in same fund particular in different currency
            *backtest result, the result's link and picture had missed currently
        """
        print('System(fund_item_group) : Running...')
        json_list = []
        for item in fund_particular:
            fund_data = self.df_fund[self.df_fund['fund_particular'] == item].values.tolist()
            if len(fund_data) > 0:
                text = list(self.df_input[self.df_input['symbol'] == 'search_fund_s']['reply_text'])[0]
                text = text.format(                                                    \
                    fund_data[0][1],fund_data[0][2],fund_data[0][3],fund_data[0][4],   \
                    fund_data[0][5],fund_data[0][6],fund_data[0][7],                   \
                    str(fund_data[0][8]).replace('<br/>','\n')                         \
                )
                reply_inline_keyword = {                                                                                                            \
                    "inline_keyboard" : ast.literal_eval(list(self.df_input[self.df_input['symbol'] == 'search_fund_s']['reply_inline_keyword'])[0])  \
                }
                json_ = self.tool_to_json(chat_id = chat_id,text = text,reply_markup = reply_inline_keyword)
            else:
                text = f'無法找到{item}，請再嘗試！'
                json_ = self.tool_to_json(chat_id = chat_id,text = text)
            json_list.append(json_)
        return json_list

    def fund_search_result(self,chat_id:str,fund_type:str):
        """
        To return the list of result(fund particular).

        params:
            *chat_id : str : chat id given by Telegram.
            *fund_type : str : the fund type to search for.

        ways:
            *button from function(fund_search)

        bug:
            *list of fund particular out of require length  
        """
        print('System(fund_search_result) : Running...')
        check_type = self.df_fund[self.df_fund['fund_type'] == fund_type]['fund_particular']
        len_ = len(check_type)
        if len_ > 0:
            text = f'小夥伴找到了關於{fund_type}之基金結果！'
            reply_inline_keyboard = self.tool_keyboard(check_type)
            json_ = self.tool_to_json(chat_id = chat_id,text = text,reply_markup = reply_inline_keyboard)
        else:
            text = '抱歉，小夥伴查無基金項目！'
            json_ = self.tool_to_json(chat_id = chat_id,text = text)
        return [json_]

    def create_acc(self,chat_id:str,username=None,password=None,set_fund='None'):
        """
        To create an account through Telegram chatbot.

        params:
            *chat_id : str : chat id given by Telegram.
            *username : str | None : username for login use.
            *password : str | None : password for login use.
            *set_fund : list | None : set default fund item.
        
        ways:
            *direct message(['建立賬號','辦理賬號'])
            *button from function(main)
        """
        print('System(create_acc) : Running...')
        if (username != None) & (password != None):
            if set_fund != 'None':
                set_fund = self.tool_keyboard(set_fund,keyboard_method = '')
            try:
                self.df_acc.append({
                    'log_acc' : username,
                    'log_pass' : password,
                    'fund_item' : set_fund,
                    'role' : 'client'
                },ignore_index = True)
                print('System(create_acc) : Register Successfully!')
            except Exception as e:
                print('Error(create_acc): ',e)
        text = list(self.df_input[self.df_input['symbol'] == 'sign_up']['reply_text'])[0]
        reply_inline_keyword = {                                                                                                        \
            "inline_keyboard" : ast.literal_eval(list(self.df_input[self.df_input['symbol'] == 'sign_up']['reply_inline_keyword'])[0])  \
        }
        json_ = self.tool_to_json(chat_id = chat_id,text = text,reply_markup = reply_inline_keyword)
        return [json_]

    def freshman_question(self,chat_id:str,current_ans:str,confirm_list=None):
        """
        To start a survey to analyze data for an appropriate fund combination.

        params:
            *chat_id : str : chat id given by Telegram.
            *current_ans : str : the answer of current question.
            *confirm_list : list : only input when client click confirm button

        ways:
            *direct message(['用戶分析'])
            *button from function(main)

        bug:
            *The pattern of question 10
        """
        print('System(freshman_question) : Running...')
        try:
            print(confirm_list)
            print(current_ans)
            cur_no = int(current_ans.split('q')[1].split('_')[0])
            ans = current_ans.split('_')[1]
            print('cur_no',cur_no)
            print('ans',ans)
            if cur_no != 0:
                if confirm_list != None:
                    self.temp_client_aly[cur_no] = confirm_list
                else:
                    self.temp_client_aly[cur_no] = ans
            if cur_no != 10:
                text_msg = list(self.df_survey[self.df_survey['no'] == cur_no+1]['question'])[0]
                list_msg = ast.literal_eval(list(self.df_survey[self.df_survey['no'] == cur_no+1]['reply_inline_keyboard'])[0])
                reply_inline_keyboard = self.tool_keyboard(list_msg,before = f'q{cur_no+1}_')
                json_msg = self.tool_to_json(chat_id = chat_id,text = text_msg,reply_markup = reply_inline_keyboard)
                if cur_no in [3,4,5,7,8]:
                    text_keyboard = '完成選擇後，點擊【確認選擇】！'
                    reply_keyboard = {                                                                                              \
                        "keyboard" : ast.literal_eval(list(self.df_survey[self.df_survey['no'] == cur_no+1]['option_keyboard'])[0]) \
                    }
                    json_keyboard = self.tool_to_json(chat_id = chat_id,text = text_keyboard,reply_markup = reply_keyboard)
                    return [json_msg,json_keyboard]
            else:
                text = '感謝您完成本次分析，希望您找到 CP 值高的基金項目。'
                json_msg = self.tool_to_json(chat_id = chat_id,text = text)
            return [json_msg]
        except Exception as e:
            print('Error(freshman_question): ',e)

    def buy_fund(self,chat_id:str):
        """
        To buy fund by providing an auto generate link.

        params:
            *chat_id : str : chat id given by Telegram.

        ways:
            button from function(suggestion,<fund particular>)
            *direct message(['我想購買'])
            *developing... / redirect to website
        """
        print('System(buy_fund) : Running...')
        text = '官網下單'
        reply_inline_keyword = {                                                                                                       \
            "inline_keyboard" : ast.literal_eval(list(self.df_input[self.df_input['symbol'] == 'fund_qa']['reply_inline_keyword'])[0]) \
        }
        json_ = self.tool_to_json(chat_id = chat_id,text = text,reply_markup = reply_inline_keyword)
        return [json_]

    def log_out(self,chat_id:str):
        """
        To log out account.

        params:
            *chat_id : str : chat id given by Telegram.

        ways:
            *button from function(main)
        """
        print('System(log_out) : Running...')
        if self.status == 'login':
            self.status = 'unlogin'
            self.user = ''
            text = '完成登出！'
        else:
            text = '抱歉！目前您仍未登錄賬號！'
        json_log_out = [self.tool_to_json(chat_id = chat_id,text = text)]
        json_main = self.main(chat_id,'')
        json_log_out.extend(json_main)
        return json_log_out

    def my_fund_list(self,chat_id:str):
        """
        To get self bought of the fund list.

        params:
            *chat_id : str : chat id given by Telegram.

        ways:
            *button from function(main)
        """
        print('System(my_fund_list) : Running...')
        if self.status == 'login':
            text = list(self.df_input[self.df_input['symbol'] == 'fund_list_s']['reply_text'])[0]
            reply_inline_keyword = {                                                                                          \
                "inline_keyboard" : ast.literal_eval(list(self.df_acc[self.df_acc['log_acc'] == self.user]['fund_item'])[0])  \
            }
        else:
            self.temp_text = text = list(self.df_input[self.df_input['symbol'] == 'fund_list_f']['reply_text'])[0]
            reply_inline_keyword = {                                                                                                            \
                "inline_keyboard" : ast.literal_eval(list(self.df_input[self.df_input['symbol'] == 'fund_list_f']['reply_inline_keyword'])[0])  \
            }
        json_ = self.tool_to_json(chat_id = chat_id,text = text,reply_markup = reply_inline_keyword)
        return [json_]

    def news(self,chat_id:str):
        """
        To send the latest news for client or manager real time.

        params:
            *chat_id : str : chat id given by Telegram.

        ways:
            *developing... {INPUT}            
        """
        return []

    def others(self,chat_id:str,content):
        """
        To send back message which are not match the function above.

        params:
            *chat_id : str : chat id given by Telegram.
            *content : any : the content in wrong send.

        ways:
            *the last action execute when all of the function are not match.
        """
        print('System(others) : Running...')
        text = content
        json_ = self.tool_to_json(chat_id = chat_id,text = text)
        return [json_]


    def tool_status_update(self,to:str):
        """
        To update status manually in case.

        params:
            *to : str : the status to change
        """
        if to in ['login','unlogin','check_acc','check_pass']:
            self.status = to
            return self.status

    def tool_to_json(self,**kwargs):
        """
        To convert data in json format.

        params:
            **kwargs : any data.
        """
        _json  = kwargs
        json_ = json.dumps(_json)
        return json_

    def tool_to_dict(self,**kwargs):
        """
        To convert data in dict format.

        params:
            **kwargs : any data.
        """
        _dict = kwargs
        return _dict

    def tool_keyboard(self,list_:list,split_count=2,before='',after='',keyboard_method='inline_keyboard'):
        """
        To convert data to Telegram's keyborad format.

        params:
            *list_ : list : item to convert.
            *split_count : int : the number of button that each row contains.
            *before : str : the pattern to insert before word
            *after : str : the pattern to insert after word
            *keyborad_method : str : the keyborad type,eg :
                Chat Area     -> { 'inline_keyboard' : inline_keyboard_item } 
                Keyboard Area -> { 'keyboard' : keyboard_item }
        """
        reply_keyboard,temp = [],[]
        len_ = len(list_)
        for no,item in enumerate(list_):
            json_ = self.tool_to_dict(text = item,callback_data = before+item+after)
            temp.append(json_)
            if (((no+1) % split_count) == 0) | (no+1 == len_):
                reply_keyboard.append(temp)
                temp = []
        if keyboard_method == '':
            return reply_keyboard
        return { keyboard_method : reply_keyboard }
    
    def tool_check_acc(self,log_data:dict):
        """
        To check account whether is exist.

        params:
            *log_data : dict : account detail(account and passowrd) to login
        """
        try:
            checking = len(self.df_acc[                               \
                (self.df_acc['log_pass'] == log_data['log_pass']) &   \
                (self.df_acc['log_acc'] == log_data['log_acc'])       \
            ])
        except:
            checking = False
        print(checking)
        return True if checking == True else False