import pandas as pd
import boto3
import io

class Excelize:
    def __init__(self):
        """
        To initialize the variable for dataframe.
        """
        self.df_acc,self.df_fund,self.df_survey,self.df_input = '','','',''

    def boto(self,location=None,filename='Telegram_Import_Document.xlsx',bucket='telegramtest',action='read',aws=None):
        """
        To upload or read file from AWS S3 Bucket.

        params:
            *location : str : the file location for uploading data.
            *filename : str : the file name for read or upload(withoud location) data.
            *bucket : str : the bucket name.
            *action : str : action for execute boto ('action' | 'read')
            *aws : dict : the aws cli detail for connect AWS Services.(aws_access_key_id / aws_secret_access_key /aws_session_token)
        """
        try:
            if aws == None:
                s3 = boto3.client('s3')
            else:
                s3 = boto3.client(
                    's3',
                    aws_access_key_id=aws['aws_access_key_id'],
                    aws_secret_access_key=aws['aws_secret_access_key'],
                    aws_session_token=aws['aws_session_token']
                )

            if action == 'read':
                obj = s3.get_object(Bucket = bucket,Key = filename)
                data = obj['Body'].read()
                self.df_input = pd.read_excel(io.BytesIO(data),sheet_name = 'input',encoding = 'utf-8')
                self.df_survey = pd.read_excel(io.BytesIO(data),sheet_name = 'survey',encoding = 'utf-8')
                self.df_fund = pd.read_excel(io.BytesIO(data),sheet_name = 'fund',encoding = 'utf-8')
                self.df_acc = pd.read_excel(io.BytesIO(data),sheet_name = 'acc',encoding = 'utf-8')

            if action == 'upload':
                if location == None:
                    res = s3.upload_file(filename,bucket,filename)
                else:
                    res = s3.upload_file(location+filename,bucket,filename)
                return True if res == None else False
        except Exception as e:
            print('Error(boto) :',e)

    def local(self,filename='Telegram_Import_Document.xlsx'):
        """
        To read data in local.

        params:
            *filename : str : the file location and file to read.
        """
        try:
            self.df_input = pd.read_excel(filename,sheet_name = 'input',encoding = 'utf-8')
            self.df_survey = pd.read_excel(filename,sheet_name = 'survey',encoding = 'utf-8')
            self.df_fund = pd.read_excel(filename,sheet_name = 'fund',encoding = 'utf-8')
            self.df_acc = pd.read_excel(filename,sheet_name = 'acc',encoding = 'utf-8')
            return True
        except  Exception as e:
            print('Error(local) :',e)
        return False

