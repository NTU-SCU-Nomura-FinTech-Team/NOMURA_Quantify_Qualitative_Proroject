import requests
import os.path
import pyautogui as p
import datetime as dt
from time import sleep
from selenium import webdriver

# Request Nomura monthly report's link
req = requests.get("https://www.nomurafunds.com.tw/API/CommonService//File/Manual/C/19")
link_pdf = req.json()['responseBody']['data']

# Initialize webdriver
driver = webdriver.Chrome()
driver.get(link_pdf)
sleep(1)

# Press to download pdf file
p.hotkey('ctrl','s')
sleep(1)

# Format Setting
date = dt.datetime.now().strftime("%x").replace('/','')
file_name = 'Nomura_Report_'+ date +'.pdf \n'

# Check wether pdf file is exist
if os.path.isfile(file_name):
    print("System:"+ file_name +"is exist !") 
else:
    p.typewrite(file_name)
    print("System:"+ file_name + "download successfully !")