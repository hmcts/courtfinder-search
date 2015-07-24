import argparse
import os
import subprocess

import requests


HIPCHAT_URL = 'https://api.hipchat.com/v1/rooms/message'


def get_commit_data(commit):
    output = subprocess.check_output(
        ['git', 'log', '-1', "--format=format:%an <%ae>|%aD|%s|%b", commit])
    return zip(['author', 'date', 'title', 'message'], output.split('|'))


def post_message(token, room, success, project, commit=None):
    params = {'auth_token': token}
    headers = {'Content-type': 'application/x-www-form-urlencoded'}
    if commit is None:
        commit = os.environ['COMMIT']
    data = {
        'room_id': room,
        'from': 'Shippable',
        'color': 'green' if success else 'red',
        'notify': True,
        'message': (
            '<a href="{BUILD_URL}">Build #{BUILD_NUMBER}</a> {status_text} '
            'for project <strong>{project}</strong> on branch {BRANCH}'
            '<br>'
            '<strong>{author}</strong><br>'
            '{date}<br>'
            '<strong>{title}</strong><br>'
            '{message}').format(
                status_text='succeeded' if success else 'failed',
                project=project,
                **dict(get_commit_data(commit), **os.environ))
    }

    response = requests.post(
        HIPCHAT_URL, params=params, data=data, headers=headers)
    print response.text


def main():
    parser = argparse.ArgumentParser(
        description='Notify HipChat of Shippable build status')
    parser.add_argument(
        '-s', '--success',
        dest='success', action='store_true', default=False,
        help='The build was successful')
    parser.add_argument(
        '-p', '--project',
        dest='project', action='store', required=True,
        help='The project being built')
    parser.add_argument(
        '-r', '--room',
        dest='room', action='store', required=True,
        help='The HipChat room to send the message to')
    parser.add_argument(
        '-t', '--token',
        dest='token', action='store', required=True,
        help='The HipChat auth token')
    parser.add_argument(
        'commit',
        action='store', nargs='?', default=None,
        help='git commit SHA of build (Optional, defaults to $COMMIT)')
    args = parser.parse_args()

    post_message(
        args.token, args.room, args.success, args.project, args.commit)


if __name__ == '__main__':
    main()
