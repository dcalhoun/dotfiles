import sys
import argparse
from workflow import Workflow, web, PasswordNotFound


def slack_keys():
    wf = Workflow()
    try:
        slack_keys = wf.get_password('slack_api_key')
    except PasswordNotFound:
        wf.add_item(title='No API key set. Please run slt',
                    valid=False)
        wf.send_feedback()
        return 0
    keys = slack_keys.split(",")

    return keys


def slack_list(keys):
    wf = Workflow()
    slack_search = []

    for key in keys:
        api_key = str(key)
        slack_auth = web.get('https://slack.com/api/auth.test?token=' + api_key + '&pretty=1').json()
        if slack_auth['ok'] is False:
            wf.add_item(title='Authentication failed. Check your API key',
                        valid=False)
            wf.send_feedback()
            break
        else:
            slack_channels = web.get('https://slack.com/api/channels.list?token=' + api_key +
                                     '&exclude_archived=1&pretty=1').json()
            slack_users = web.get('https://slack.com/api/users.list?token=' + api_key + '&pretty=1').json()
            slack_groups = web.get('https://slack.com/api/groups.list?token=' + api_key + '&pretty=1').json()
            for channels in slack_channels['channels']:
                slack_search.append({'name': channels['name'], 'team': slack_auth['team']})
            for users in slack_users['members']:
                slack_search.append({'name': users['name'], 'team': slack_auth['team']})
            for groups in slack_groups['groups']:
                if 'name' in groups:
                    slack_search.append({'name': groups['name'], 'team': slack_auth['team']})

    return slack_search


def search_slack_names(slack_list):
    elements = []
    elements.append(slack_list['name'])
    return u' '.join(elements)


def main(wf):

    parser = argparse.ArgumentParser()
    parser.add_argument('--setkey', dest='apikey', nargs='?', default=None)
    parser.add_argument('query', nargs='?', default = None)
    args = parser.parse_args(wf.args)


    if args.apikey:
        wf.save_password('slack_api_key', args.apikey)
        return 0


    if len(wf.args):
        query=wf.args[0]
    else:
        query=None

    def wrapper():
        return slack_list(keys=slack_keys())

    slack_search = wf.cached_data('slackfred', wrapper, max_age=120)

    if query:
        slack_search = wf.filter(query, slack_search, key=search_slack_names)

    for names in slack_search:
        wf.add_item(title=names['name'],
                    subtitle=names['team'],
                    arg=names['name'],
                    valid=True)

    wf.send_feedback()

if __name__ == u"__main__":
    wf = Workflow()
    sys.exit(wf.run(main))