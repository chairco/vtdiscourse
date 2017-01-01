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

    -s, --service
        GET: get .md content
        NAME: get description

    -h, --help
        show usage

    -v, --verbose

EXAMPLES
    vtd -n "api_user" -p "api_key"



COPYRIGHT
    MIT Licence

SOURCE
    https://github.com/chairco/vtdiscourse
"""

import sys
import getopt

from vtdiscourse.vtdiscourse import Discourse, Parser

def main(argv=None):
    if not argv:
        argv = sys.argv[1:]

    if len(argv) == 0:
        print(__doc__)
        sys.exit(0)

    try:
        opts, args = getopt.getopt(argv, "s:n:p:hv", ["service", "name", "password", "help"])
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
        elif o in ('-s', '--service'):
            service_type = a

    if not name and not password:
        try:
            name = ""
            password = ""
        except KeyError:
            sys.exit("invalid type")

    discourse = Discourse(
        url = 'https://talk.vtaiwan.tw',
        api_username=name,
        api_key=password)

    if service_type == 'GET':
        parm = Parser(filename='vtaiwan.json', githubfile='SUMMARY.md')
        print(parm.get_topics_content)
    elif service_type == "NAME":
        parm = Parser(filename='vtaiwan.json', githubfile='package.json')
        description = parm.get_name
    else:
        print(discourse)


if __name__ == "__main__":
    main(sys.argv[1:])
