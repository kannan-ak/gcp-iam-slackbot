from googleapiclient.discovery import build
from googleapiclient import _auth, errors
from google.oauth2 import service_account
import sys
import logging

ORG_ID = "C04ca0air"

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s')
logger = logging.getLogger(__name__)

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/admin.directory.group', 'https://www.googleapis.com/auth/groups',
          'https://www.googleapis.com/auth/cloud-platform', 'https://www.googleapis.com/auth/cloud-identity']

# source_credentials = (
#    service_account.Credentials.from_service_account_file(
#        '/Users/kannan/Downloads/dcr-orchestration-qa-d0147b2b4964.json',
#        scopes=SCOPES))


service = build('cloudidentity', 'v1')
# create_group(service)
# Fetching the canonical id of the group


def fetch_group_id(service, group_name, next_page_token):
    # Call the Admin SDK Directory API
    # List groups
    results = service.groups().list(parent=f'customers/{ORG_ID}', pageToken=next_page_token).execute()
    print(results)

    for details in results['groups']:
        if group_name == details['groupKey']['id']:
            print("Gotcha")
            print(details)
            print(details['name'])
            return details['name']
        else:
            #print("continue")
            continue

    if 'nextPageToken' in results:
        next_page_token = results['nextPageToken']
        print("Token is " + next_page_token)
        return fetch_group_id(service, group_name, next_page_token=next_page_token)
    else:
        print("Not found")
        return "Group doesn't exist. Please check with infra team"


#group_name = fetch_group_id(service, "zeotap-virgin-media-uk-group-editor@zeotap.com", next_page_token='')
#print(f"We got what we want {group_name}")


def group_lookup():
    try:
        results = service.groups().lookup(groupKey_id="xxxx@domain.com").execute()
        return results['name']

    except errors.HttpError as e:
        logger.error(e)
        return "Invalid Group or No access to the group. Please check with Infra team."

    except Exception as e:
        logger.error(e)
        return "Full error"

# print(group_lookup())