import os
from dotenv import load_dotenv


load_dotenv()

# auth
phone = os.getenv("PHONE")
assert phone is not None, "Please provide the phone number"

# bot config
like_prob = os.getenv("LIKE_PROB", 0.8)
swipe_timeout = int(os.getenv("SWIPE_TIMEOUT", 30)) # [s]

# exceptions
exception_timeout = os.getenv("EXCEPTION_TIMEOUT", 600) # 10min
email = os.getenv("EMAIL", "orestis.zambounis@gmail.com") # for crash report
