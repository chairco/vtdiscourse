# -*- coding: utf-8
# An g0v's project vTaiwan module.
# module author:: chairco <chairco@gmail.com>

import os
import re
import json
import requests
import markdown
import random

from pprint import pprint

from pydiscourse import DiscourseClient

from bs4 import BeautifulSoup as bs

from collections import OrderedDict


class Create(object):
    def __init__(self, *args, **kwargs):
        self.outfile = 'content.json'

    def dumps(self, data):
        # create json file
        with open(self.outfile, 'w') as fp:
            fp.write(json.dumps(data, indent=4, ensure_ascii=False))


class Parser(Create):
    """Parser the markdown file, and follow format create a .json file
    :name
    :githubfile
    """
    def __init__(self, name, githubfile, *args, **kwargs):
        super(Parser, self).__init__(name, githubfile, *args, **kwargs)
        self.name = name
        self._githubfile = githubfile

    @property
    def get_content(self):
        if os.path.splitext(self._githubfile)[-1] == '.json':
            return json.loads(requests.get(self.get_url).text)
        elif os.path.splitext(self._githubfile)[-1] == '.md':
            return requests.get(self.get_url).text
        else:
            return None

    @property
    def get_topics_content(self, topics_data=list()):
        """create json base
        return Orderdict() format 
        """
        summary = self.get_summary
        for topic in summary:
            self.githubfile = topic # 改讀 topic file
            htmlcontent = markdown.markdown(self.get_content)
            soup = bs(htmlcontent, 'html.parser')
            topics_data.append(OrderedDict([(topic, [{tag.name: tag.string} for tag in soup.find_all(True)])])) 
        return topics_data

    @property
    def get_name(self):
        if os.path.splitext(self._githubfile)[-1] == '.json':
            return self.get_content.get('description')
        else:
            return None

    @property
    def get_summary(self):
        summary = self.get_content
        html = markdown.markdown(summary)
        soup = bs(html, 'html.parser')
        #print(soup.prettify())
        return [ link.get('href') for link in soup.find_all('a')]

    @property
    def get_url(self):
        g0v_page = "https://raw.githubusercontent.com/g0v/"
        name = self._content
        path = "/master/"
        return g0v_page + name + path + self._githubfile

    @get_url.setter
    def githubfile(self, githubfile):
        self._githubfile = githubfile 

    @property
    def get_gitbook(self):
        return requests.get(self.get_gitbook_url).text

    @property
    def get_gitbook_url(self):
        # return gitbook url
        g0v_page = "https://g0v.github.io/"
        #name = self._content().get('github')[0].get('name')
        name = self._content
        return g0v_page + name

    @property
    def _content(self):
        return str(self.name).strip()

    def __del__(self):
        pass


class Discourse(DiscourseClient):
    """Get the Discourse content
    
    Search a session from Discourse
    Create a new session for Discourse
    host, username, key should exist then yield error
    """
    def __init__(self, host, api_username, api_key, *args, **kwargs):
        super(Discourse, self).__init__(host, api_username, api_key)
        self.host = host
        self.api_username = api_username
        self.api_key = api_key
        self.args = args
        self.kwargs = kwargs

    @property
    def client(self):
        """This is the activate to get certification from discourse web
        :url     : Discourse web
        :username: Discourse user
        :key     : Discourse api key
        """
        client = DiscourseClient(
            self.host,
            api_username=self.api_username,
            api_key=self.api_key
        )
        return client

    def serarch_topic(self, term, key, **kwargs):
        keys = ['categories', 'grouped_search_result', 
                'users', 'topics', 'posts']
        if key not in keys: 
            raise KeyError('argument should be categories, grouped_search_result,'
                           'users, topics, posts')
        content = self._search(term=term, **kwargs)
        if content.get('grouped_search_result') != None:
            return content.get(key)
        else:
            return content

    def post_category(self, category, text_color='FFFFFF',
                      permissions=None, parent=None, **kwargs):
        if category in self.get_all_categories:
            return False
        else:
            r = lambda: random.randint(0,255)
            color = '%02X%02X%02X' % (r(), r(), r())
            return self._create_category(name=category,
                                        color=color,
                                        permissions=permissions,
                                        parent=parent,
                                        **kwargs)

    def post_topics(self, content, **kwargs):
        """This is create the post with the category, use kwargs
        title   :
        content :
        category:
        """
        return self.client.create_post(content=content, **kwargs)

    def catetory(self, name, parent=None, **kwargs):
        """override the DiscourseClient.category"""
        if parent:
            name = u'{0}/{1}'.format(parent, name)

        return self.client._get(u'/c/{0}.json'.format(name), **kwargs)

    def get_category(self, name, parent=None, **kwargs):
        return self.category(name=name, parent=parent, **kwargs)

    def get_category_topics(self, name='meta-data'):
        return self.get_category(name=name).get('topic_list').get('topics')

    def get_category_topic_content(self, id, key):
        """Get the key's content in the topics 
        :id : int, index of the topics range
        :key: string
        """
        if not isinstance(id, int):
            raise ValueError('{0} Should be INT'.format(id))
        if id >= len(self.get_category_topics):
            raise ValueError('{0} list index out of range, len = {1}'.format(id, len(self.get_category_topics)-1))
        if key not in self.get_category_topics[id]:
            raise KeyError('{0} Not exist in {1}'.format(key, [self.get_category_topics[id].keys()]))
        return self.get_category_topics[id].get(key)

    @property
    def get_all_categories(self):
        return [category['name'] for category in self.client.categories()]

    def _search(self, term, **kwargs):
        return self.client.search(term=term, **kwargs)

    def _create_category(self, name, color, text_color='FFFFFF',
                        permissions=None, parent=None, **kwargs):
        """Create the category on Discourse
            :name       :
            :color      :
            :text_color :
            :permissions: dict of 'everyone', 'admins', 'moderators', 'staff' with values of ???
            :parent     :
            :kwargs     :
            >>> discourse.create_category(name="自動產生", color="3c3945")
            """
        return self.client.create_category(name=name, color=color, text_color=text_color,
                                           permissions=permissions, parent=parent, **kwargs)


        


