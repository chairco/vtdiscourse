# vtdiscourse
這個工具是專為 [talk vTaiwan](https://talk.vtaiwan.tw/) 所建立。
目的是當法案建立一個 gitbook 後要根據內容建立對應的討論區與問題，而 gitbook 建立在 g0v 的 gihub repo，因此想法是根據 g0v repo 名稱去爬出 `package.json`, `SUMMARY.md` 兩個檔案內容。


## 說明
+ `package.json`: gitbook 相關設定，用其來建立討論區分類中文名稱
+ `SUMMARY.md`: gitbook 大綱，用他產生分類內的討論話題（topics）


## 安裝方法
+ 將 repo 拉到本機端(client)並且安裝（支援 Python2.7, Python3.x）

`git clone https://github.com/chairco/vtdiscourse.git`

+ 安裝套件

`cd vtdiscourse`

`python setup.py install`


## 使用方法（透過指令）

需要先建立 json 檔案, ex: vtaiwan.json：
```
{
  "github":[
        {
            "name":"directors-election-gitbook"
        } 
    ]
}
```

接著執行：


`vtd -n "api_user" -p "api_key" -s GET`



## 使用方法（透過程式）
請注意某些內容必須要有管理員權限的 API User, Key 才能存取。

### 設定 API
```
>>> discourse = Discourse(
        url = 'https://talk.vtaiwan.tw',
        api_username='使用者',
        api_key='金鑰')
```

### 設定 json 參數檔案與要讀取 repo 名稱
+ 預設 `vtdiscourse/vtaiwan.json` 可修改檔案內容 `name` 對應 repo 名稱
```
{
  "github":[
        {
            "name":"repo 名稱",
        } 
    ]
}
```
+ 設定參數檔案、讀取 github 的檔案名稱：

`>>> parm = Parser(filename='vtaiwan.json', githubfile='package.json')`


### 快樂的取得 `package.json` 相對應內容：
```
# Get 法案的中文名稱
>>> print(parm.get_name)
```


### 快樂的取得 `SUMMARY.md` 內容有兩種方式：
+ 尚未建立物件時，直接設定物件參數 `parm = Parser(filename='vtaiwan.json', githubfile='SUMMARY.md')`
+ 已經建立物件 `parm = Parser(filename='vtaiwan.json', githubfile='package.json')`，直接透過 `setter` 方法 `parm.githubfile = "SUMMARY.md"` 轉為讀取 `SUMMARY.md`

```
# Get SUMMARY.md content
>>> print(parm.get_topics_content)
```



