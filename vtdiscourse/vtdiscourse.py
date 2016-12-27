# -*- coding: utf-8
"""An g0v's project vTaiwan module.

.. moduleauthor:: chairco <chairco@gmail.com>

"""
import json
import requests

from pydiscourse import DiscourseClient

class Parser(object):
    """Parser the markdown file, and follow format create a .json file
    Args:

    """
    def __init__(self, *args, **kwargs):
        pass

    def __del__(self):
        pass


class Discourse(object):
    """Get the Discourse content
    
    search a session from Discourse
    create a new session for Discourse
    url, username, key should exist then yield error

    :api_username: user login discourse
    :api_key: the certification key for discourse

    >>> from vtdiscourse import Discourse
    >>> Discourse.client()

    .. versionadded:: 0.0.1
    
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
        """
        client = DiscourseClient(
            self.url,
            api_username=self.api_username,
            api_key=self.api_key
        )
        return client

    def create_category(self, name, color, text_color='FFFFFF',
                      permissions=None, parent=None, **kwargs):
        """"
        Args:
            name:
            color:
            text_color:
            permissions: dict of 'everyone', 'admins', 'moderators', 'staff' with values of ???
            parent:
            **kwargs: help(DiscourseClient)
        ex:
        >>> discourse.create_category(name="自動產生", color="3c3945")
        """
        return self.client.create_category(name=name, color=color, text_color=text_color,
                                           permissions=permissions, parent=parent, **kwargs)


    def get_user(self, username):
        """Get user information for a specific user
        
        Args:
            username: username to return
        Returns:
            dict of user information
        ex:
        >>> print(discourse.get_user(username='vTaiwan'))
        """
        return self.client.user(username)

    @property
    def get_user_topics(self):
        """Gets a list of topics created by user 'vTaiwan'
        ex:
        >>> print(discourse.get_user_topics)
        """
        return self.client.topics_by('vTaiwan')

    @property
    def get_all_categories(self):
        """
        return all catreories by list type
        """
        return [category['name'] for category in self.client.categories()]

    @property
    def get_category(self, name='meta-data'):
        return self.client.category(name='meta-data')

    @property
    def get_category_topics(self):
        """
        return all meta-data topics list
        """
        return self.get_category.get('topic_list').get('topics')

    def get_category_topic_content(self, id, key):
        """Get the key's content in the topics 
        
        Args:
            id: int, index of the topics range
            key: string
        """
        if not isinstance(id, int):
            raise ValueError('{0} Should be INT'.format(id))
        if id >= len(self.get_category_topics):
            raise ValueError('{0} list index out of range, len = {1}'.format(id, len(self.get_category_topics)-1))
        if key not in self.get_category_topics[id]:
            raise KeyError('{0} Not exist in {1}'.format(key, [self.get_category_topics[id].keys()]))
        return self.get_category_topics[id].get(key)
        
    def get_posts(self, id=908):
        """Gets the posts form id, default id 908(meta-data)
        ex:
        >>> print(discourse.get_posts)
        """
        return self.client.posts(topic_id=id)

    def test(self, **kwargs):
        """
        ex:
        >>> print(discourse.test(a=1, b=2, c=3))
        """
        return self._test(**kwargs)

    def _test(self, **kwargs):
        return kwargs

    def __del__(self):
        pass


if __name__ == '__main__':
    discourse = Discourse(
        url = 'https://talk.vtaiwan.tw',
        api_username='',
        api_key='')
    print(discourse.get_category_topic_content(id=5, key='ids'))