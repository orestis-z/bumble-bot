import requests
import json
import sys
import time
from datetime import date, datetime
import http.client as http_client
import random
import logging
import logging.handlers
import getpass
import re
from robobrowser import RoboBrowser

import config as cfg
from smtp_handler import TlsSMTPHandler


BASE_URL = "https://bumble.com/unified-api.phtml?"

logging.basicConfig(level=logging.DEBUG)
password = getpass.getpass("Enter password for {}:".format(cfg.email))
gm = TlsSMTPHandler(("smtp.gmail.com", 587), cfg.email, [cfg.email], "Bumble bot exception", (cfg.email, password))
gm.setLevel(logging.ERROR)
logger = logging.getLogger()
logger.addHandler(gm)
try:
    0 / 0
except:
    logger.exception("Mail test")

# http_client.HTTPConnection.debuglevel = 1

def login(s):
    url = BASE_URL + "SERVER_LOGIN_BY_PASSWORD"
    body = {
        "version": 1,
        "message_type": 15,
        "message_id": 5,
        "body": [{"message_type": 15, "server_login_by_password": {
            "remember_me": True,
            "phone": cfg.phone,
            "password": getpass.getpass("Enter password for phone {}:".format(cfg.phone))}
        }]
    }
    resp = s.post(url, json=body)
    assert resp.ok, "Login Error"

s = requests.Session()

body = {"version":1,"message_type":2,"message_id":1,"body":[{"message_type":2,"server_app_startup":{"app_build":"MoxieWebapp","app_name":"moxie","app_version":"1.0.0","can_send_sms":False,"user_agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36","screen_width":1680,"screen_height":1050,"language":0,"is_cold_start":True,"external_provider_redirect_url":"https://bumble.com/static/external-auth-result.html?","locale":"en-US","app_platform_type":5,"app_product_type":400,"device_info":{"webcam_available":True,"form_factor":3},"build_configuration":2,"supported_features":[11,15,1,2,4,6,18,16,22,33,70,160,58,140,187,220,197],"supported_minor_features":[317,2,216,244,232,19,225,246,31,125,183,114,8,9,83,41,427,115,288,420,477,39,290,398],"supported_notifications":[83,73,3],"supported_promo_blocks":[{"context":92,"position":13,"types":[71]},{"position":5,"types":[160]},{"context":8,"position":13,"types":[111,112,113]},{"context":45,"position":15,"types":[137]},{"context":53,"position":18,"types":[136,93,12]},{"context":45,"position":15,"types":[93,134,135,136]},{"context":10,"position":1,"types":[265,266]}],"supported_onboarding_types":[15],"user_field_filter_client_login_success":{"projection":[210,220,230,200,91,890,340]},"a_b_testing_settings":{"tests":[]},"dev_features":["bumble_snooze"],"device_id":"ffb4ad39-ad39-3935-359f-9f418abb8c03"}}],"is_background":False}
resp = s.post(BASE_URL + "SERVER_APP_STARTUP", json=body)

login(s)

# fetch user list
url = BASE_URL + "SERVER_GET_USER_LIST"
body = {
    "version": 1,
    "message_type": 245,
    "message_id": 2,
    "body": [{
        "message_type": 245,
        "server_get_user_list": {
            "folder_id":0,
            "user_field_filter": {"projection": [200,340,230,640,580,300,860,590,591,250,700,762,592,880,582,930,585,583,305,330]},
            "preferred_count": 30
        }
    }],
    "is_background": False,
}
resp = s.post(url, json=body)
resp_json = json.loads(resp.text)

encounters_url = BASE_URL + "SERVER_GET_ENCOUNTERS"
vote_url = BASE_URL + "SERVER_ENCOUNTERS_VOTE"
n_liked = 0
errors = 0
while True:
    try:
        # fetch encounters
        body = {
            "version": 1,
            "message_type": 81,
            "message_id": 3,
            "body": [{
                "message_type": 81,
                "server_get_encounters": {
                    "number": 50,
                    "user_field_filter": {
                        "projection": [210,370,200,230,490,540,530,560,290,890,930,662,570,380,493],
                    }
                }
            }],
        }
        resp = s.post(encounters_url, json=body)
        assert resp.ok
        resp_json = json.loads(resp.text)
        results = resp_json['body'][0]['client_encounters']['results']
        assert len(results) > 0

        # like users
        for user in results:
            user = user["user"]
            user_id =user["user_id"]
            name = user["name"]
            age = user["age"]
            distance = user.get("distance_short")
            if not distance:
                distance = user.get("distance_long")
            body = {
                "version": 1,
                "message_type": 80,
                "message_id": 4,
                "body": [{
                    "message_type":80,
                    "server_encounters_vote": {
                        "person_id": user_id,
                        "vote_source": 1,
                    }
                }],
            }
            user_str = ", ".join([name, str(age), distance])
            if random.uniform(0, 1) < cfg.like_prob:
                body["body"][0]["server_encounters_vote"]["vote"] = 2
                resp = s.post(vote_url, json=body)
                if resp.ok:
                    n_liked += 1
                    logging.debug("Like {} ({} total)".format(user_str, n_liked))
            else:
                body["body"][0]["server_encounters_vote"]["vote"] = 3
                resp = s.post(vote_url, json=body)
                if resp.ok:
                    logging.debug("Pass {}".format(user_str))
            time.sleep(cfg.swipe_timeout)
        errors = 0
    except:
        if resp.status_code == 401:
            logging.debug("Session expired. Logging in...")
            login(s)
            continue
        logger.exception("Exception number {}".format(errors))
        time.sleep(cfg.exception_timeout * 2 ** errors) # double the timeout with every proceeding error
        errors += 1
