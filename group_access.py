from __future__ import print_function
from googleapiclient.discovery import build
from googleapiclient import _auth, errors
import datetime as dt
import sys
import requests
import logging
import json
import os
import dotenv

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/admin.directory.group', 'https://www.googleapis.com/auth/groups',
          'https://www.googleapis.com/auth/cloud-platform', 'https://www.googleapis.com/auth/cloud-identity']


dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
dotenv.load_dotenv(dotenv_path)

ORG_ID = os.environ['ORG_ID']

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s')
logger = logging.getLogger(__name__)


def main(request_form, response_url):
    """Creating the service object
    """

    global project_name
    global access_mode
    global group_name

    info = request_form['text'].split()
    user_name = request_form['user_name']
    logger.info(f"Arguments received: {info}")

    if len(info) == 2 and (info[1].lower() == "viewer" or info[1].lower() == "editor"):
        logger.info("Received two positional arguments as expected.")
        project_name = info[0].lower()
        access_mode = info[1].lower()
        group_name = project_name + "-group-" + access_mode + "@company.com"
        logger.info(f"Group name: {group_name}")

    else:
        response = {
            "response_type": "in_channel",
            "text": f"Hey {user_name}! \n Invalid format! \n Usage: /1pbot project_name access_mode(viewer/editor)"
        }
        logger.error(response)
        requests.post(response_url, data=json.dumps(response))
        sys.exit(0)

    logger.info("Creating service client")
    #creds = _auth.default_credentials(scopes=SCOPES, quota_project_id=project_name)

    #service = build('cloudidentity', 'v1', credentials=creds)
    service = build('cloudidentity', 'v1')
    # create_group(service)
    # Fetching the canonical id of the group
    group_id = fetch_group(service, group_name, user_name, response_url)

    # add the member to the group
    add_member(service, group_id, user_name, response_url)


def fetch_group(service, group_name, user_name, response_url):
    try:
        results = service.groups().lookup(groupKey_id=group_name).execute()
        print(results)
        return results['name']
    except errors.HttpError as e:
        logger.error(e)
        error_response = str("Invalid project or No access to the group. Please check with Infra team.")

    except Exception as e:
        logger.error(e)
        error_response = str(e)

    response = {
        "response_type": "in_channel",
        "text": f"Hey {user_name}! \n Error: {error_response}"
    }
    logger.error(response)
    requests.post(response_url, data=json.dumps(response))
    sys.exit(0)



#def fetch_group_id(service, group_name, user_name, response_url, next_page_token):
#    # Call the Admin SDK Directory API
#    # List groups
#    try:
#        results = service.groups().list(parent=f'customers/{ORG_ID}', pageToken=next_page_token).execute()
#        print(results)
#        # logger.info(results)
#        for details in results['groups']:
#            if group_name == details['groupKey']['id']:
#                logger.info(details)
#                return details['name']
#            else:
#                continue
#
#        if 'nextPageToken' in results:
#            next_page_token = results['nextPageToken']
#            print("Token is " + next_page_token)
#            return fetch_group_id(service, group_name, user_name, response_url, next_page_token=next_page_token)
#        else:
#            print("Not found")
#
#        logger.error("Group doesn't exist. Please check with infra team")
#
#        response = {
#            "response_type": "in_channel",
#            "text": f"Hey {user_name}! \n Error:  Invalid Project/Group! Please create a jira under XX."
#        }
#        logger.error(response)
#        requests.post(response_url, data=json.dumps(response))
#        sys.exit(0)
#    except Exception as e:
#        logger.error(e)
#        error_response = str(e)
#        response = {
#            "response_type": "in_channel",
#            "text": f"Hey {user_name}! \n Error: {error_response}"
#        }
#        logger.error(response)
#        requests.post(response_url, data=json.dumps(response))
#        sys.exit(0)
#

def add_member(service, group_id, user_name, response_url):
    current_time = dt.datetime.utcnow().replace(microsecond=0)
    lease_time = current_time + dt.timedelta(hours=12)
    lease_time_iso = lease_time.replace(microsecond=0).isoformat() + 'Z'

    try:
        body = {
            "roles": [
                {
                    "name": "MEMBER",
                    "expiryDetail": {
                        "expireTime": lease_time_iso
                    }
                }
            ],
            "preferredMemberKey": {
                "id": user_name+".1p@zeotap.com"
            }
        }
        # group ID can be found from list groups
        results = service.groups().memberships().create(parent=f'{group_id}', body=body).execute()

        print(results)
        response = {
            "response_type": "in_channel",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Your request is completed*"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*User*:\n{user_name}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Project*:\n{project_name}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Group*:\n{group_name}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Access*:\n{access_mode}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Access Granted time*:\n{current_time} UTC"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Access Expiry time:*\n{lease_time} UTC"
                        }
                    ]
                }
            ]
        }
        logger.info(response)
        requests.post(response_url, data=json.dumps(response))

    except errors.HttpError as e:
        if "Error(4003)" in str(e):
            error_message = "User already part of the group"
            logger.error(error_message)
        else:
            logger.error(str(e))
            error_message = str(e)

        response = {
            "response_type": "in_channel",
            "text": f"{error_message}"
        }
        requests.post(response_url, data=json.dumps(response))

    except Exception as e:
        logger.error(str(e))
        error_message = str(e)

        response = {
            "response_type": "in_channel",
            "text": f"{error_message}"
        }
        requests.post(response_url, data=json.dumps(response))
