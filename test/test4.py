import sys
sys.path.append("/home/riosshin/code/videoAI")
LAST_FAILURE_FILE = "tools/last_failure.json"
from datetime import date
import sys
import json
today = date.today()


def set_last_failure_date(failure_date):
    with open(LAST_FAILURE_FILE, "w") as f:
        json.dump({"last_failure": failure_date.isoformat()}, f)


set_last_failure_date(today)