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

import config as cfg
from smtp_handler import TlsSMTPHandler

BASE_URL = "https://api.gotinder.com/"
KM_TO_MILES = 0.621371

logging.basicConfig(level=logging.DEBUG)
password = getpass.getpass("Enter password for {}:".format(cfg.email))
gm = TlsSMTPHandler(("smtp.gmail.com", 587), cfg.email, [cfg.email], "Tinder bot exception", (cfg.email, password))
gm.setLevel(logging.ERROR)
logger = logging.getLogger()
logger.addHandler(gm)
try:
    0 / 0
except:
    logger.exception("Tinder bot test mail")

# http_client.HTTPConnection.debuglevel = 1

def calculate_age(born):
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

s = requests.Session()
s.headers.update({
    "User-Agent": "Tinder/4.0.9 (iPhone; iOS 8.1.1; Scale/2.00)"
})

if cfg.api_token:
    api_token = cfg.api_token
else:
    # fetch tinder api token
    url = BASE_URL + "v2/auth/login/facebook"
    body = {
        "token": cfg.facebook_token,
    }
    resp = s.post(url, json=body)
    resp_json = json.loads(resp.text)
    api_token = resp_json["data"]["api_token"]
s.headers.update({
    "X-Auth-Token": api_token,
})

# fetch profile
url = BASE_URL + "v2/profile"
params = {
    "include": "user",
}
resp = s.get(url, params=params)
resp_json = json.loads(resp.text)
user_id = resp_json['data']['user']['_id']

# send coords
url = BASE_URL + "v2/meta"
body = {
    "lat": cfg.lat,
    "lon": cfg.lon,
    "force_fetch_resources": True,
}
resp = s.post(url, json=body)

core_url = BASE_URL + "v2/recs/core"
matches_url = BASE_URL + "v2/matches"
msg_url = BASE_URL + "user/matches"
like_url = BASE_URL + "like/"
pass_url = BASE_URL + "pass/"
n_liked = 0
try:
    while True:
        # fetch users
        resp = s.get(core_url)
        resp_json = json.loads(resp.text)
        results = resp_json["data"]["results"]

        if cfg.auto_msg_on:
            date_today = date.today()
            datetime_auto_msg = datetime(date_today.year, date_today.month, date_today.day, cfg.auto_msg_hour)
            datetime_now = datetime.now()
            datetime_delta = datetime_now - datetime_auto_msg
            # if datetime_delta.days == 0 and datetime_delta.seconds < 5 * 60:
            if True:
                # fetch matches
                params = {
                    "count": 60,
                }
                resp = s.get(matches_url, params=params)
                resp_json = json.loads(resp.text)
                matches = resp_json['data']['matches']
                for match in matches:
                    # message pending matches
                    if match['pending']:
                        _id = match['_id']
                        body = {
                            "matchId": _id,
                            "message": cfg.auto_msg,
                            "userId": user_id,
                        }
                        resp = s.post(msg_url + _id, json=body)
                        logging.debug("Messaged {}: {}".format(match['person']['name'], cfg.auto_msg))

        # like users
        for user in results:
            s_number = user["s_number"]
            _id = user['user']["_id"]
            params = {
                "s_number": s_number,
            }
            user_str = ", ".join([user['user']['name'], str(calculate_age(datetime.strptime(user['user']['birth_date'], "%Y-%m-%dT%H:%M:%S.%fZ"))), "{0:.0f}km".format(user['distance_mi'] / KM_TO_MILES)])
            if random.uniform(0, 1) < cfg.like_prob:
                resp = s.get(like_url + _id, params=params)
                if resp.ok:
                    n_liked += 1
                logging.debug("Like {} ({} total)".format(user_str, n_liked))
            else:
                resp = s.get(pass_url + _id, params=params)
                logging.debug("Pass {}".format(user_str))
            time.sleep(random.uniform(2, 3))
except Exception as e:
    logger.exception(e)
