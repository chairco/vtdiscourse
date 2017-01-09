# -*- coding: utf-8

from vtdiscourse import Discourse, Parser
from pprint import pprint
from collections import OrderedDict
from pydiscourse import DiscourseClient
import json
import random
import logging
import threading
import itertools
import time
import sys


logger = logging.getLogger(__name__)
DEBUG = True


class Signal:
    go = True


def spin(msg, signal):
    write, flush = sys.stdout.write, sys.stdout.flush
    for char in itertools.cycle('|/-\\'):
        status = char + ' ' + msg
        write(status)
        flush()
        write('\x08' * len(status))
        time.sleep(.1)
        if not signal.go:
            break
    write(' ' * len(status) + '\x08' * len(status))


def slow_function():
    #假裝等待 I/O 等待一段很長的時間
    time.sleep(3)
    return 42


def supervisor():
    signal = Signal()
    spinner = threading.Thread(target=spin,
                               args=('\u2603  working', signal))
    print('spinner object:', spinner)
    spinner.start()
    result = slow_function()
    signal.go = False
    spinner.join()
    return result


def create_content(name, githubfile):
    logger.info('start creare JSON file.')
    parm = Parser(name=name, githubfile=githubfile)
    # Get SUMMARY.md content and create to json.
    #parm.githubfile = githubfile
    # Parser the md file.
    topics = parm.get_topics_content
    parm.dumps(data=topics)
    logger.info('create JSON file "content.json" success.')


def read_content(filename='content.json'):
    with open(filename) as fp:
        json_data = json.load(fp)
    return json_data


def parser_html(json_data, content=''):
    """parser html and return content
       資料結構應該要長[{[],[],[]}]，回傳 str
    """
    for c in json_data:
        for k2, v2 in c.items():
            #print(k2, '-->', v2)
            if k2 == 'h1':
                content = content + v2 + '\r\n'
            elif k2 == 'h2':
                content = content + '##' + v2 + '\n'
            elif k2 == 'p' and v2 != None:
                content = content + v2 + '\n'
            elif k2 == 'ol' and v2 != None:
                content = content + '* ' + v2 + '\n'
            elif k2 == 'li' and v2 != None:
                content = content + '+ '  + v2 + '\n'
            elif v2 != None:
                #logger.info('other tag: {0}'.format(k2))
                content = content + v2 + '\n'
    return content


def insert_discourse(datas, id, category, discourse):
    """insert discourse, 先檢查有沒有 README.md"""
    if 'README.md' not in datas.keys():
        raise KeyError(u'不存在 README.md, 無法建立類別，請檢查 content.json。')
    else:
        # 是否要把內容放在這裡建立呢？那應該要用 update
        logger.info(id)

    topics = discourse.get_category_topics(name=str(id)+'-category')
    topics_data = OrderedDict([(topic.get('id'), topic.get('title'))for topic in topics])

    for md in datas:
        if md != 'README.md':
            contents = datas.get(md).split('\r\n')
            logger.info("{0}, {1}, {2}" .format(contents[0], type(md), md))
            #topic_data = discourse.serarch_topic(term=contents[0], key='topics')
            topic_data = search_discourse(discourse=discourse, term=contents[0])
            if topic_data == None:
                logger.info('建立新的子類別 {0}'.format(contents[0]))
                # 建立 sub_catrgory
                #discourse.post_category(name=contents[0],parent=category)
            else:  
                logger.info("已經存在，請手動修改 Title, ID: {0}, {1}".format(topic_data.get('title'),
                                                                           topic_data.get('id')))
            
            # 有這個 category 才去建立
            #for k, v in topics_data.items():
            #    print(k,'--->',v)
            #    if contents[0] in v: print(k, ':match')
    

def search_discourse(discourse, term):
    c = discourse.serarch_topic(term=term, key='topics')
    for t in c:
        if term in t.get('title'):
            return t
    return None           


def deploy(api_username, api_key, name):
    # Get package.json content
    parm = Parser(name=name, githubfile='package.json')
    category = parm.get_name
    logger.info('Category: ' + category + ', Start deploy...')

    # Discourse settings
    discourse = Discourse(
        url = 'https://talk.vtaiwan.tw',
        api_username=api_username,
        api_key=api_key)

    # Create category
    if not DEBUG:
        ret = discourse.post_category(category=category)
        if ret == False:
            logger.info('Category already exist.')
            category_id = ''
        else:
            logger.info('Create Category success.')
            category_id = ret.get('category').get('id')

    # Create category and with topic:
    json_data = read_content()
    
    # Get the SUMMARY file content
    parm.githubfile = 'SUMMARY.md'
    summary_data = parm.get_summary
    logger.info('Summary_data: {0}' .format(str(summary_data)))
    logger.info('Books Counts: {0}' .format(len(json_data)))

    # 根據 md 檔案建立對應的 category 和內容。並且 Insert。
    # 放入 insert 改用 OrderedDict 結構
    discourse_data = list()
    for md in json_data:
        for summary in summary_data:
            if md.get(summary):
                discourse_data.append((summary, parser_html(json_data=md.get(summary))))
    # TODO()移到 DEBUG MODE
    insert_discourse(datas=OrderedDict(discourse_data),
                     id=134,#id=category_id,
                     category=category,
                     discourse=discourse)

    if not DEBUG:
        post_title = "您是否會因公司規模而對董監事選任方式改變有不同看法？為什麼？"
        post_content = "1.無須區分公開發行公司或非公開發行公司皆開放 \n" \
                       "2.僅須對公開發行公司開放 \n" \
                       "3.僅須對非公開發行公司開放 \n" \
                       "4.其他 \n"
        logger.info(discourse.post_topics(content=post_content,
                                          title=post_title, 
                                          category=description))


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, 
                        format='%(asctime)s:%(name)s:%(levelname)s:%(message)s')
    
    result = supervisor()
    print('Answer:', result)

    #create_content(name='directors-election-gitbook', githubfile='SUMMARY.md')
    deploy(api_username='vtaiwan',
           api_key='',
           name='')
    

