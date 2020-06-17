import pandas as pd
from time import sleep
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options  # for suppressing the browser
from bs4 import BeautifulSoup as bs

class nomura_monthly_target_crawler:
    def __init__(self,date:str):
        # Basic settings
        self.ALL = ['201506','201507','201508','201509','201510','201511','201512','201601',
                    '201602','201603','201604','201605','201606','201607','201608','201609',
                    '201610','201611','201612','201701','201702','201703','201704','201705',
                    '201706','201707','201708','201709','201710','201711','201712','201801',
                    '201802','201803','201804','201805','201806','201807','201808','201809',
                    '201810','201811','201812','201901','201902','201903','201904','201905',
                    '201906','201907','201908','201909','201910','201911','201912','202001',
                    '202002','202003']

        # Get data settings
        self.df_inv_target = ''
        self.data_to_df = [] # Final result as a list of list
        self.DATE = date
        self.UNIT = 'A0032'
        self.FUND_TYPE = 'AC23'

        # Check input format
        if date.lower() == 'all':
            for date in self.ALL:
                self.DATE = date
                self.request()
                self.to_csv()
        elif len(date) != '6' or date not in self.ALL:
            print('Error: Date format is wrong! It should be [YYYYMM]')

    def request(self):
        # Run without screen
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        # Start modify
        self.driver = webdriver.Chrome(options = options)
        self.driver.get("https://www.sitca.org.tw/ROC/Industry/IN2629.aspx")
        sleep(5)

        # Select Date
        self.driver.find_element_by_xpath('//option[@value="{}"]'.format(self.DATE)).click()
        sleep(2)

        # Select Unit
        self.driver.find_element_by_id('ctl00_ContentPlaceHolder1_rbComCL').click()
        self.driver.find_element_by_xpath("//select[@id='ctl00_ContentPlaceHolder1_ddlQ_Comid1']/option[@value='{}']".format(self.UNIT)).click()
        sleep(2)

        # Select Fund Type
        self.driver.find_element_by_xpath("//select[@id='ctl00_ContentPlaceHolder1_ddlQ_Class1']/option[@value='{}']".format(self.FUND_TYPE)).click()
        sleep(2)

        # Submit search
        self.driver.find_element_by_id("ctl00_ContentPlaceHolder1_BtnQuery").click()
        self.process_data()

    def process_data(self):
        soup = bs(self.driver.page_source,'html.parser') # Clear tag after decode
        pre_save = [] # Temporary save before create a row
        count = 0 # Download 10 unit data then break loop
        start_to_save = False # A switch for getting data if it's 野村美利堅高收益債基金
        raw_data = soup.find_all('td',{ 'class' : ['DTeven','DTodd'] }) # Find tag by multiple class name

        try:
            # Start to clear and get data
            for data in raw_data:
                if start_to_save: # bool
                    pre_save.append(data.string)
                    if len(pre_save) == 9: # fulfilled condition of a rows
                        self.data_to_df.append(pre_save)
                        pre_save = [] # Reset temp data
                        count+=1
                    if count == 10: # Break if get all data
                        break
                if data.string == '野村美利堅高收益債基金': # Turn on switch for saving data
                    start_to_save = True
            if len(self.data_to_df) == False:
                print("Error: {} doesn't have fund data!".format(self.DATE))
        except Exception as e:
            print("Error: " + str(e))

    def to_csv(self):
        if len(self.data_to_df) == False:
            print("Error: {} doesn't have fund data!".format(self.DATE))
            self.driver.close()
            return

        # Create dataframe with rows and columns
        columns = ['no','t_type','bloomberg_code','t_name','amount','guarentee_institution','s-order_bonds','num_beneficiary_unit','net_ass_val_rate']
        self.df_inv_target = pd.DataFrame(self.data_to_df[-10:], columns = columns)

        # Get the share code
        self.df_inv_target['t_name'] = self.df_inv_target['t_name'].apply(lambda x : x.split(' ')[0])

        # Drop the unused coloumns
        self.df_inv_target = self.df_inv_target[['no','t_name']]

        # Convert to csv
        self.df_inv_target.to_csv('nomura_monthly_target_{}.csv'.format(self.DATE),index = False,header = True)
        print('COMPLETE: nomura_monthly_target_{}.csv !'.format(self.DATE))
        self.driver.close()

################ TEST FORMAT ################
if __name__ == "__main__":
    nmr_crawler = nomura_monthly_target_crawler('202002')
    nmr_crawler.request()
    nmr_crawler.to_csv()
    # print(nmr_crawler.df_inv_target)
