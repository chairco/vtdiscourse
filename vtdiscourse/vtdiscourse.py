# -*- coding: utf-8
# An g0v's project vTaiwan module.
# module author:: chairco <chairco@gmail.com>

import os
import re
import json
import requests
import markdown

from pprint import pprint

from pydiscourse import DiscourseClient

from bs4 import BeautifulSoup as bs

from collections import OrderedDict


class Parser(object):
    # Parser the markdown file, and follow format create a .json file

    def __init__(self, filename, githubfile, *args, **kwargs):
        self.filename = filename
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
        # print(soup.prettify())
        return [ link.get('href') for link in soup.find_all('a')]

    @property
    def get_topics_content(self, topics_data=list()):
        """建立一個 json base
        return Orderdict() format 
        """
        summary = self.get_summary
        for topic in summary:
            self.githubfile = topic
            htmlcontent = markdown.markdown(self.get_content)
            soup = bs(htmlcontent, 'html.parser')
            topics_data.append(OrderedDict([(topic, [{tag.name: tag.string} for tag in soup.find_all(True)])])) 
        return topics_data

    @property
    def get_url(self):
        # TODO(chairco) should check json format
        g0v_page = "https://raw.githubusercontent.com/g0v/"
        name = self._content().get('github')[0].get('name')
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
        name = self._content().get('github')[0].get('name')
        return g0v_page + name

    def _content(self):
        with open(self.filename) as fp:
            json_data = json.load(fp)
        return json_data

    def _createjson(self):
        pass

    def __del__(self):
        pass


class Discourse(object):
    """Get the Discourse content
    
    search a session from Discourse
    create a new session for Discourse
    url, username, key should exist then yield error
    """
    def __init__(self, url, api_username, api_key, *args, **kwargs):
        super(Discourse, self).__init__()
        self.args = args
        self.kwargs = kwargs
        self.url = url
        self.api_username = api_username
        self.api_key = api_key

    @property
    def client(self):
        """This is the activate to get certification from discourse web
        :url     : Discourse web
        :username: Discourse user
        :key     : Discourse api key
        """
        client = DiscourseClient(
            self.url,
            api_username=self.api_username,
            api_key=self.api_key
        )
        return client

    def create_category(self, name, color, text_color='FFFFFF',
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

    def get_user(self, username):
        # Get user information for a specific user
        return self.client.user(username)

    @property
    def get_user_topics(self):
        # Gets a list of topics created by user 'vTaiwan'
        return self.client.topics_by('vTaiwan')

    @property
    def get_all_categories(self):
        return [category['name'] for category in self.client.categories()]

    @property
    def get_category(self, name='meta-data'):
        return self.client.category(name='meta-data')

    @property
    def get_category_topics(self):
        return self.get_category.get('topic_list').get('topics')

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
        
    def get_post(self, topic_id, post_id):
        # Get the post /t/{0}/{1}.json
        return self.client.post(topic_id, post_id)

    def get_posts(self, id=908):
        # Gets the posts /t/{0}/posts.json, default id 908(meta-data)
        return self.client.posts(topic_id=id)

    def test(self, **kwargs):
        """
        >>> print(discourse.test(a=1, b=2, c=3))
        "{'a': 1, 'b': 2, 'c': 3}"
        """
        return self._test(**kwargs)

    def _test(self, **kwargs):
        return kwargs


