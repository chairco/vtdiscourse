# vtdiscourse
這個工具是專為 [talk vTaiwan](https://talk.vtaiwan.tw/) 所建立。
目的是當法案建立一個 gitbook 後要根據其內容建立對應的討論區與問題。gitbook 是建立在 g0v 的 gihub repo，因此做法是根據 g0v repo 名稱去爬出 `packeage.json` 的法案名稱與 `SUMMARY.md` 與對應的 `.md` 檔案的內容。


## 說明
+ `package.json`: gitbook 相關設定，用其來建立討論區分類法案的中文名稱。
+ `SUMMARY.md`: gitbook 大綱，用他取得子分類名稱與對應的內容。


## 安裝方法
+ 將 repo 拉到本機端(client)並且安裝（支援 Python2.7, Python3.x）

`git clone https://github.com/chairco/vtdiscourse.git`

+ 安裝套件

`cd vtdiscourse`

`python setup.py install`


## 使用方法 1（透過指令）

取得法案名稱方法：

`vtd -n "api_user" -p "api_key" -g "gihub's repo name" -s GET`


建立 talk.vTaiwan 討論內容：

`vtd -n "api_user" -p "api_key" -g "gihub's repo name" -s DEPLOY`


## 使用方法 2（撰寫程式）

請注意某些內容必須要有管理員權限的 API-User, API-Key 才能存取。

#### 設定 API
```
>>> discourse = Discourse(
        url = 'https://talk.vtaiwan.tw',
        api_username='使用者',
        api_key='金鑰')
```

#### 設定要讀取 repo 名稱

+ 設定參數檔案、讀取 github 的檔案名稱：

`>>> parm = Parser(name='directors-election-gitbook', githubfile='package.json')`


#### 快樂的取得 `package.json` 相對應內容
```
# Get 法案的中文名稱
>>> print(parm.get_name)
```

#### 快樂的取得 `SUMMARY.md` 內容有兩種方式
+ 尚未建立物件時，直接設定物件參數 `parm = Parser(name='directors-election-gitbook', githubfile='SUMMARY.md')`
+ 已經建立物件 `parm = Parser(name='directors-election-gitbook', githubfile='package.json')`，直接透過 `setter` 方法 `parm.githubfile = "SUMMARY.md"` 轉為讀取 `SUMMARY.md`

```
# Get SUMMARY.md content
>>> print(parm.get_topics_content)
```

## 測試

請進入專案內資料夾內執行 `py.test`


## LICENSE
MIT LICENSE
