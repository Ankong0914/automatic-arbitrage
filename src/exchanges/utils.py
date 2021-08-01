import logging
import requests
import json
from datetime import datetime
import re
import pytz
import asyncio


logger = logging.getLogger(__name__)

def send_http_request(url, headers=None, body=None):
    if body is None:  # GET request
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise
    else:  # POST request
        try:
            response = requests.post(url, headers=headers, data=json.dumps(body))
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise


def format_timestamp(ts):
    jst = pytz.timezone("Asia/Tokyo")

    try:
        dt = datetime.fromtimestamp(float(ts))
    except ValueError:
        ts = re.sub("Z$", "+00:00", ts)
        ts = re.sub(r"(\.\d+)", "", ts)
        try:
            dt = datetime.fromisoformat(ts)
        except ValueError:
            logger.error("input timestamp can't be formatted")
            raise
    except TypeError:
        logger.error("input timestamp can't be formatted")
        raise

    dt_jst = dt.astimezone(jst)
    dt_iso = dt_jst.isoformat(timespec="seconds")
    return dt_iso


def send_async_requests(funcs, args=None):
    loop = asyncio.get_event_loop()
    loops = []
    if args is None:
        for func in funcs:
            loops.append(loop.run_in_executor(None, func))
    else:
        for func, arg in zip(funcs, args):
            loops.append(loop.run_in_executor(None, func, *arg)) 
    tasks = asyncio.gather(*loops)
    results = loop.run_until_complete(tasks)
    return results