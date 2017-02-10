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
DEBUG = False


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
    logger.info('Start creare JSON file.')
    parm = Parser(name=name, githubfile=githubfile)  # Get SUMMARY.md content and create to json.
    
    # Parser the md file.
    topics = parm.get_topics_content
    parm.dumps(data=topics)
    logger.info('Create JSON file "content.json" Success.')
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

    import CommonMark
    
    parser = CommonMark.Parser()
    ast = parser.parse(markdown_data)
    renderer = CommonMark.HtmlRenderer()
    html = renderer.render(ast)
    return html


def parser_to_hierarchical(order_data):
    import re
    from bs4 import BeautifulSoup as bs
    
    soup = bs(order_data, 'html.parser') #BeautifuleSoup Dataset
    
    h1 = soup.find_all('h1')
    if len(h1) > 1:
        print("有兩個 H1 內容，會造成資料遺失！！")
        logger.error("有兩個 H1 內容，會造成資料遺失！！")
    elif len(h1) == 0:
        logger.error("沒有 H1 內容，錯誤！！")
        raise ValueError("沒有 H1 內容，錯誤！！")

    #TODO要處理有內文的 h1
    data = [i.strip() for i in re.split('<h1>|</h1>',order_data) if i!='']
    title = data[0]
    
    h2 = soup.find_all('h2')
    h2_dict = dict()
    h2_data = [i.strip() for i in re.split('<h2>|</h2>', data[1]) if i!='']
    for i in h2:
        for j in range(0, len(h2_data)):
            if re.split('<h2>|</h2>',str(i))[1] == str(h2_data[j]):
                h2_dict.setdefault(h2_data[j], h2_data[j+1])
    hierarchical_data = {title: h2_dict}
    return hierarchical_data

    
def inset_topic(md, contents, parm, discourse):
    parm.githubfile = md
    order_data = parser_markdown(markdown_data=parm.get_content)
    hierarchical_data = parser_to_hierarchical(order_data=order_data)

    for k, v in hierarchical_data.get(contents[0]).items():
        post_title, post_content = k, v
        ret = discourse.post_category(category=contents[0])
        if ret == False:
            print("topic: {0} 建立成功，準備建立子類別: {1}。".format(contents[0],
                                                                  post_title))
        else:
            print("topic: {0} 已經存在，準備建立子類別: {1}。".format(contents[0],
                                                                  post_title))
        logger.info(discourse.post_topics(content=post_content,
                                          title=post_title, 
                                          category=contents[0]))


def insert_discourse(id, category, summary_data, parm, discourse):
    """Insert discourse, 先檢查有沒有 README.md"""
    # 根據 MD 檔案建立對應的 category 和內容。並且 Insert。改用 OrderedDict 結構
    # TODO(chairco@gmail.com)改成讀取網站上的 content.json, 因為已經轉好格式。
    json_data = read_content()
    discourse_data = list()
    # create orderdict dataset, structure is key=md's filename, value=md's value
    for md in json_data:
        for summary in summary_data:
            if md.get(summary):
                discourse_data.append((summary, parser_html(json_data=md.get(summary))))
    datas = OrderedDict(discourse_data)

    # Mark at 20170210 because can't get all the topics in category(maybe is the discourse bug)
    #topics = discourse.get_category_topics(name=str(id)+'-category')
    #topics_data = OrderedDict([(topic.get('id'), topic.get('title'))for topic in topics]) # 所有的 category
    
    for md in datas:
        if md != 'README.md':
            contents = datas.get(md).split('\r\n')
            print("準備建立 {0} 的 Topic:[{1}]" .format(md, contents[0]))
            logger.info("準備建立 {0} 的 Topic:[{1}]" .format(md, contents[0]))
            topic_data = search_discourse(discourse=discourse, term=contents[0])
            if topic_data == None:
                print('建立子類別 [{0}] 與內容'.format(contents[0]))
                logger.info('建立子類別 [{0}] 與內容'.format(contents[0]))
                inset_topic(md=md, contents=contents, parm=parm, discourse=discourse) # 建立 sub_catrgory
                print('<<建立成功>>\n')
            else:
                print("可能存在，如果相同請手動修改 'Topic':[{0}], 'ID':[{1}]".format(topic_data.get('title'),
                                                                                topic_data.get('id')))
                logger.info("可能存在，如果相同請手動修改 'Topic':[{0}], 'ID':[{1}]".format(topic_data.get('title'),
                                                                                topic_data.get('id')))
                inset_topic(md=md, contents=contents, parm=parm, discourse=discourse) # 暫時
                print('<<請手動修改>>\n')
    

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
    print('Start Deploy, 法案：{0} '.format(category))
    logger.info('Start Deploy, 法案：{0} '.format(category))
    
    # Get the SUMMARY file content
    parm.githubfile = 'SUMMARY.md'
    summary_data = parm.get_summary
    print('SUMMARY.md: {0}' .format(', '.join(summary_data)))
    logger.info('SUMMARY.md: {0}.' .format(', '.join(summary_data)))

    # Discourse settings
    discourse = Discourse(
        host = 'https://talk.vtaiwan.tw/',
        api_username=api_username,
        api_key=api_key)

    # Create category
    if not DEBUG:
        ret = discourse.post_category(category=category)
        if ret == False:
            print('Category:[{0}] 已經存在'.format(category))
            logger.info('Category:[{0}] 已經存在'.format(category))
            category_id = search_discourse(discourse=discourse, term=category).get('category_id')
            print('Category id =', str(category_id))
        else:
            print('Create Category:[{0}] Success'.format(category))
            logger.info('Create Category:[{0}] Success'.format(category))
            category_id = ret.get('category').get('id')
            print('Category id =', str(category_id))
        try:
            insert_discourse(id=category_id,
                             category=category,
                             summary_data=summary_data,
                             parm=parm,
                             discourse=discourse)
            return 'Deploy to talk.vTaiwan Success, Please check vtd.log.'
        except Exception as e:
            raise e
    else:
        print('Now DEBUG MODE')
        logger.info('{0} Now DEBUG MODE {1}'.format('-'*10, '-'*10))
        return 'Not Deploy anything, Please check vtd.log.'


def supervisors(api_key, api_username, name):
    signal = Signal()
    spinner = threading.Thread(target=spin,
                               args=('\u2603  <Deploy>', signal))
    spinner.start()
    try:
        logger.info('{0} New Job start {1}'.format('-'*10, '-'*10))

        result = create_content(name=name,
                                githubfile='SUMMARY.md')
        print('Result:', result)
        logger.info('Result: {0}'.format(result))
        
        result = deploy(api_username=api_username,
                        api_key=api_key,
                        name=name)
        logger.info('Result: {0}'.format(result))
        print('Result:', result)
        logger.info('{0} Finish {1}'.format('-'*10, '-'*10))
    except Exception as e:
        raise e
    finally:
        signal.go = False
        spinner.join()
    return result


def test():
    create_content(name='securitization-ref1-gitbook', githubfile='SUMMARY.md')
    deploy(api_username=os.environ.get('vTaiwan_api_user'),
           api_key=os.environ.get('vTaiwan_api_key'),
           name='securitization-ref1-gitbook')


if __name__ == '__main__':
    logging.basicConfig(filename='vtd.log',
                        level=logging.INFO, 
                        format='%(asctime)s:%(name)s:%(levelname)s:%(message)s')
    
    supervisors(api_key=os.environ.get('vTaiwan_api_key'),
                api_username=os.environ.get('vTaiwan_api_user'),
                name='securitization-ref1-gitbook')

