[![Documentation Status](https://readthedocs.org/projects/vtdiscourse/badge/?version=latest)](http://vtdiscourse.readthedocs.io/en/latest/?badge=latest)

# vtdiscourse

這個工具是專為 [talk vTaiwan](https://talk.vtaiwan.tw/) 所開發。

目的是當 `talk vTaiwan` 的法案建立 `gitbook` 後要據其內容在討論區建立對應的問題。`vTaiwan` 的 `gitbook` 會建立在 `g0v` 的 `gihub repo` 例如[企業資產擔保法草案](https://github.com/g0v/securitization-ref1-gitbook)。
整個流程首先會根據對應法案的 `g0v repo` 去取得 `packeage.json` 法案名稱與 `SUMMARY.md` 與以及對應的 `.md` 檔案內容。


## 說明

+ `package.json`: `gitbook` 相關設定，用其來建立討論區分類法案的中文名稱。
+ `SUMMARY.md`: `gitbook` 大綱，用他取得子分類名稱與對應的內容。


## 安裝步驟

+ clone repo 到本機端並且安裝 (支援 Python2.7, Python3.x)

```
git clone https://github.com/chairco/vtdiscourse.git`
```

+ 安裝套件

```
cd vtdiscourse

python setup.py install
```

## 使用方法

**分成兩種，一種是安裝後透過 `command line` 一鍵完成。第二種則是撰寫一個簡單的 `script` 來完成。**


### 指令(Command line)

+ 取得法案名稱方法

```
vtd -n "api_user" -p "api_key" -g "gihub's repo name" -s GET
```

+ 建立 talk.vTaiwan 討論內容

```
vtd -n "api_user" -p "api_key" -g "gihub's repo name" -s DEPLOY
```


### 腳本(Script)

**請注意某些內容必須要有管理員權限的 API-User, API-Key 才能存取。**

#### 設定 API
```
>>> discourse = Discourse(
        url = 'https://talk.vtaiwan.tw',
        api_username='使用者',
        api_key='金鑰')
```

#### 設定要讀取 repo 名稱

+ 設定參數檔案、讀取 github 的檔案名稱

```
>>> parm = Parser(name='directors-election-gitbook', githubfile='package.json')
```

#### 快樂的取得 `package.json` 相對應內容

+ 抓取法案的中文名稱

``` 
>>> print(parm.get_name)
```

#### 快樂的取得 `SUMMARY.md` 內容有兩種方式

+ 尚未建立物件時，直接設定物件參數 `parm = Parser(name='directors-election-gitbook', githubfile='SUMMARY.md')`

+ 已經建立物件 `parm = Parser(name='directors-election-gitbook', githubfile='package.json')`，直接透過 `setter` 方法 `parm.githubfile = "SUMMARY.md"` 轉為讀取 `SUMMARY.md`

```
>>> print(parm.get_topics_content) # Get SUMMARY.md content
```


## 測試

進入專案內資料夾內執行 `py.test`


## LICENSE
MIT LICENSE
