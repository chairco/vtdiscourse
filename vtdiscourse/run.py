# -*- coding: utf-8
# create talk.vTaiwan category and topic

try:
    from vtdiscourse.vtdiscourse import Discourse, Parser
except Exception as e:
    from vtdiscourse import Discourse, Parser

from pprint import pprint
from collections import OrderedDict
from pydiscourse import DiscourseClient
from bs4 import BeautifulSoup

import json
import random
import logging
import threading
import itertools
import time
import sys
import os
import CommonMark


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


def create_content(name, githubfile):
    logger.info('start creare JSON file.')
    parm = Parser(name=name, githubfile=githubfile)  # Get SUMMARY.md content and create to json.
    
    # Parser the md file.
    topics = parm.get_topics_content
    parm.dumps(data=topics)
    logger.info('create JSON file "content.json" success.')
    return 'Create content.json Success.'


def read_content(filename='content.json'):
    if not os.path.exists(filename): raise IOError(filename+' not exist.')
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
                content = content + v2 + '\n'
    return content


def parser_markdown(markdown_data):    
    from markdown_to_json.vendor import CommonMark
    from markdown_to_json.markdown_to_json import Renderer, CMarkASTNester

    ast = CommonMark.DocParser().parse(markdown_data)
    list_nested = CMarkASTNester().nest(ast)
    stringified = Renderer().stringify_dict(list_nested)
    return stringified


def inset_topic(md, contents, parm, discourse):
    parm.githubfile = md
    order_data = parser_markdown(markdown_data=parm.get_content)
    for k , v in order_data.get(contents[0]).items():
        post_title = k
        if isinstance(v, list):
            post_content = '。\n'.join(["* "+i for i in v])
        elif isinstance(v, dict):
            for k2, v2 in v.items():
                content = '。\n'.join(["* "+i for i in v2])
            post_content = k2 + '\n' + content
        else:
            if len(v) < 20:
                post_content = v + str('。'*int(20-len(v)))
            post_content = v
        logger.info("{0}\n內容：\n{1}\n".format(post_title, post_content))
        
        if not DEBUG:
            logger.info(discourse.post_topics(content=post_content,
                                              title=post_title, 
                                              category=contents[0]))


def insert_discourse(id, category, summary_data, parm, discourse):
    """insert discourse, 先檢查有沒有 README.md"""
    # 讀取 content.json
    # 根據 MD 檔案建立對應的 category 和內容。並且 Insert。改用 OrderedDict 結構
    # TODO()改成讀取網站上的 content.json
    json_data = read_content()
    discourse_data = list()
    for md in json_data:
        for summary in summary_data:
            if md.get(summary):
                discourse_data.append((summary, parser_html(json_data=md.get(summary))))
    datas = OrderedDict(discourse_data)

    topics = discourse.get_category_topics(name=str(id)+'-category')
    topics_data = OrderedDict([(topic.get('id'), topic.get('title'))for topic in topics]) # 所有的 category

    for md in datas:
        if md != 'README.md':
            contents = datas.get(md).split('\r\n')
            print("建立 {0} 的 Topic: {1}" .format(md, contents[0]))
            logger.info("建立 {0} 的 Topic: {1}" .format(md, contents[0]))
            topic_data = search_discourse(discourse=discourse, term=contents[0])
            if topic_data == None:
                print('準備建立子類別 {0} 與內容.'.format(contents[0]))
                logger.info('準備建立子類別 {0} 與內容.'.format(contents[0])) # 建立 sub_catrgory
                #logger.info(discourse.post_category(name=contents[0],parent=category))
                inset_topic(md=md, contents=contents, parm=parm, discourse=discourse)
            else:
                #inset_topic(md=md, contents=contents, parm=parm, discourse=discourse) # 暫時
                print("已經存在，請手動修改 Title: {0}, ID: {1}".format(topic_data.get('title'),
                                                                     topic_data.get('id')))
                logger.info("已經存在，請手動修改 Title: {0}, ID: {1}".format(topic_data.get('title'),
                                                                           topic_data.get('id')))


def search_discourse(discourse, term):
    c = discourse.serarch_topic(term=term, key='topics')
    for t in c:
        try:
            if term in t.get('title'):
                return t
        except Exception as e:
            raise ValueError("Not exist {0} search result: {1}".format(term, c))
    return None           


def deploy(api_username, api_key, name):
    # Get package.json content
    parm = Parser(name=name, githubfile='package.json')
    category = parm.get_name
    print('Start deploy, 法案: ' + category)
    logger.info('Start deploy, 法案: ' + category)
    
    # Get the SUMMARY file content
    parm.githubfile = 'SUMMARY.md'
    summary_data = parm.get_summary
    print('Summary_data: {0}' .format(', '.join(summary_data)))
    logger.info('Summary_data: {0}' .format(', '.join(summary_data)))

    # Discourse settings
    discourse = Discourse(
        host = 'https://talk.vtaiwan.tw/',
        api_username=api_username,
        api_key=api_key)

    # Create category
    if not DEBUG:
        ret = discourse.post_category(category=category)
        if ret == False:
            print('Category already exist.')
            logger.info('Category already exist.')
            category_id = search_discourse(discourse=discourse, term=category).get('category_id')
        else:
            print('Create Category success.')
            logger.info('Create Category success.')
            category_id = ret.get('category').get('id')
    else:
        category_id = 134

    insert_discourse(id=category_id,
                     category=category,
                     summary_data=summary_data,
                     parm=parm,
                     discourse=discourse)
    logger.info('{0} Finish {1}'.format('-'*10, '-'*10))
    
    return 'Deploy to talk.vTaiwan Success, Please check vtd.log.'


def supervisors(api_key, api_username, name):
    signal = Signal()
    spinner = threading.Thread(target=spin,
                               args=('\u2603  Deploy ', signal))
    #print('spinner object:', spinner)
    spinner.start()
    try:
        result = create_content(name=name,
                                githubfile='SUMMARY.md')
        print('Result:', result)
        result = deploy(api_username=api_username,
                        api_key=api_key,
                        name=name)
    except Exception as e:
        raise e
    finally:
        signal.go = False
        spinner.join()
    return result


if __name__ == '__main__':
    logging.basicConfig(filename='vtd.log',
                        level=logging.INFO, 
                        format='%(asctime)s:%(name)s:%(levelname)s:%(message)s')
    
    #create_content(name='directors-election-gitbook', githubfile='SUMMARY.md')
    #deploy(api_username=os.environ.get('vTaiwan_api_user'),
    #       api_key=os.environ.get('vTaiwan_api_key'),
    #       name='directors-election-gitbook')

    result = supervisors(api_key=os.environ.get('vTaiwan_api_key'),
                         api_username=os.environ.get('vTaiwan_api_user'),
                         name='directors-election-gitbook')
    print('Result:', result)



    

