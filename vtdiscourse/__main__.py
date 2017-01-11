"""vtdiscourse

NAME
    vtd -  create content for category and topic talk.vTaiwan

SYNOPSIS
    vtd [OPTION]

DESCRIPTION
    -n, --name
        user name for Discourse api_user.

    -p, --password
        password for Discourse api_eky.

    -g, --repo name
        github's repo name

    -s, --service
        GET: get .md content
        NAME: get description
        DEPLOY: deploy the category and sub-category in talk.vTaiwan

    -h, --help
        show usage

    -v, --verbose

EXAMPLES
    1. vtd -n "api_user" -p "api_key" -g "directors-election-gitbook" -s GET
    2. vtd -n "api_user" -p "api_key" -g "directors-election-gitbook" -s DEPLOY


COPYRIGHT
    MIT Licence

SOURCE
    https://github.com/chairco/vtdiscourse
"""

import sys
import getopt

from vtdiscourse.vtdiscourse import Discourse, Parser
from vtdiscourse.run import supervisors

def main(argv=None):
    if not argv:
        argv = sys.argv[1:]

    if len(argv) == 0:
        print(__doc__)
        sys.exit(0)

    try:
        opts, args = getopt.getopt(argv, "g:s:n:p:hv", ["github","service", "name", "password", "help"])
    except getopt.GetoptError as e:
        print(__doc__)
        sys.exit("invalid option: " + str(e))

    name = None
    password = None
    service_type = None

    for o, a in opts:
        if o in ('-h', '--help'):
            print(__doc__)
            sys.exit(0)
        elif o in ('-n', '--name'):
            name = a
        elif o in ('-p', '--password'):
            password = a
        elif o in ('-g', '--github'):
            github = a
        elif o in ('-s', '--service'):
            service_type = a

    if not name and not password:
        try:
            name = ""
            password = ""
        except KeyError:
            sys.exit("invalid type")

    discourse = Discourse(
        host = 'https://talk.vtaiwan.tw',
        api_username=name,
        api_key=password)

    service_type = str(service_type).upper()

    if service_type == 'GET':
        parm = Parser(name=github, githubfile='SUMMARY.md')
        print(parm.get_topics_content)
    elif service_type == 'NAME':
        parm = Parser(name=github, githubfile='package.json')
        description = parm.get_name
    elif service_type == 'DEPLOY':
        if not github: sys.exit("invalid type")
        result = supervisors(api_key=password, api_username=name, name=github)
        print('Result', result)
    else:
        print(discourse)


if __name__ == "__main__":
    main(sys.argv[1:])
