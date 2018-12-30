import os
from dotenv import load_dotenv


load_dotenv()

# auth
fb_email = os.getenv("FB_EMAIL")
assert fb_email is not None, "Please provide the facebook email"

# coordinates
lat = os.getenv("LAT")
lon = os.getenv("LON")

# bot config
like_prob = os.getenv("LIKE_PROB", 0.5)
swipe_timeout = os.getenv("SWIPE_TIMEOUT", 30) # [s]
auto_msg_on = os.getenv("AUTO_MSG_ON", False)
auto_msg_hour = os.getenv("AUTO_MSG_HOUR", 21) # 9pm
auto_msg_txt = os.getenv("AUTO_MSG_TXT")

# exceptions
exception_timeout = os.getenv("EXCEPTION_TIMEOUT", 600) # 10min
email = os.getenv("EMAIL", "orestis.zambounis@gmail.com") # for crash report
