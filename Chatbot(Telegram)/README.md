# 野村小夥伴
* ### 機器人流程圖
![alt text](https://telegramtest.s3.amazonaws.com/%E9%87%8E%E6%9D%91_Telegram_Chatbot_Procedure.png)
* ### 定位
客戶服務是聊天機器人最有影響力的領域，因此打造了一站式服務的任務機器人，搭配用戶使用場景，創造了有別於一般的任務機器人功能。

* ### 目標
  * 減少客戶對於銷售的距離感
  * 透過任務機器人享有一站式的服務
  * 透過推播與用戶分析，讓用戶瞭解適合自己基金項目
  
* ### 工具
  * 程式語言: Python
  * 套件使用: Pandas / ast / requests / function(自創) / excelize(自創) / stack(自創)
  * 資料來源: 專案獲取 / 野村官網
  * 部署工具與環境: AWS【Lambda / API Gateway】

* ### 函式架構
  * 【app.py】 -> 主程式
  * 【progress_latests.py】 -> 執行服務導向
  * 【config.py】-> 金鑰與 API 鏈接
  * function/【function】-> 功能執行與發送
  * tool/【stack】-> 儲存執行緒
  * tool/【excelize】-> 載入 Excel 文件
  
* ### 部署流程圖
![alt text](https://telegramtest.s3.amazonaws.com/%E9%87%8E%E6%9D%91_Telegram_Chatbot_DeploymentChart.png)


