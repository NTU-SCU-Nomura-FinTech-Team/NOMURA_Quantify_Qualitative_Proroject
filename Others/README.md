# 其它文件
* ### tor_test_file.py
  * ## Tor [[YouTube Link](https://www.youtube.com/watch?v=wJfa0qEzpJc)]
    * STEP 1: Download [Tor](https://www.torproject.org/download/)
    * STEP 2: 解壓安裝，並找到及啓動 tor.exe 執行器
    * STEP 3: 找到 Read configuration file '路徑'，打開文件
    * STEP 4: 打開 Tor-FAQ 中的 [the sample torrc file](https://gitweb.torproject.org/tor.git/tree/src/config/torrc.sample.in) 網頁 
    * STEP 5: 將 FAQ 中的 text 複製並貼在一個新的 txt 檔
    * STEP 6: 去 configuration 路勁中 tor（注意：是小寫 tor 而不是大寫） 文件夾底下，以 torcc 命名儲存
    * STEP 7: 打開儲存的 torcc 檔，將以下幾行解除注解
    *   - `ControlPort 9051`
    *   - `HashedControlPassword <HASH 代碼>`
    * STEP 8: 打開 cmd，cd 到有 tor.exe 執行器的路金，接著輸入以下代碼（ `tor —hash-password <設定自己的密碼>`）以獲取 Hash 值
    * STEP 9: 拿到 Hash 值后，貼在 torcc 檔案下， 修改 HashedControlPassword 后的 Hash 值
    * STEP 10: 爲了驗證是否成功，可下載此檔案並嘗試執行（確保安裝 requests 以及 stem 套件，并在檔案中輸入之前所設定的密碼），確保所有 IP 呈貢被輸出，即爲成功
      溫馨提醒：執行前記得打開 tor.exe 執行檔案
