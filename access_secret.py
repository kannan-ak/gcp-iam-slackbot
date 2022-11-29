# from google.cloud import secretmanager
import os
import google.api_core.exceptions
import logging
import traceback
import json
import requests
import google.auth.exceptions
import sys
import group_access
import dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
dotenv.load_dotenv(dotenv_path)

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s')
logger = logging.getLogger(__name__)


def token_validation(request_form, response_url):
    try:
        logger.info("Check the team domain")
        if request_form['team_domain'] == 'company':
            logger.info("Verified team successfully!")
#            if request_form['channel_name'] != '1pbot':
#                response = {
#                    "response_type": "in_channel",
#                    "text": f"Hey {request_form['user_name']}! \nError:  This channel is not allowed. Use #1pbot channel"
#                }
#                logger.critical(response)
#                requests.post(response_url,data=json.dumps(response))
#                sys.exit()
#            logger.info("Calling group access function")
        else:
            logger.critical("Invalid team domain.")
            response = {
                "response_type": "in_channel",
                "text": f"Hey {request_form['user_name']}! \nError: Invalid request. Please check with infra team."
            }
            logger.critical(response)
            requests.post(response_url, data=json.dumps(response))
            sys.exit()
    except Exception as e:
        logger.error(traceback.format_exc())
        response = {
            "response_type": "in_channel",
            "text": f"Hey {request_form['user_name']}! \nError: Invalid request. Please check with infra team."
        }
        requests.post(response_url,data=json.dumps(response))
        sys.exit()

    group_access.main(request_form, response_url)