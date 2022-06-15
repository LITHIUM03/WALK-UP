#! /usr/bin/python3


import sched
import datetime
from datetime import date
from datetime import timedelta
from paho.mqtt import client as mqtt_client
import logging
from garminconnect import Garmin

FORMAT = '%(asctime)s %(levelname)-8s %(message)s'
logging.basicConfig(filename="garmin.log", level=logging.DEBUG, datefmt='%Y-%m-%d %H:%M:%S', format=FORMAT)
logger = logging.getLogger(__name__)
logging.debug("Debug logging")
scheduler = sched.scheduler()
steps_goal = 20

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~ MQTT DETAILS~~~~~~~~~~~~~~~~~~~~~~~~~~~#

broker = '0.1.2.3'  # RPi IP
port = 1883
topic_pi_to_esp = "pi_to_esp"

mqtt_pi_speaks = mqtt_client.Client("pi_talks")
mqtt_pi_speaks.connect(broker, port, keepalive=600)

# ~~~~~~~~~~~~~~~~~~~~~~~~~ MQTT DETAILS END ~~~~~~~~~~~~~~~~~~~~~~~~~#
FRMT = "%Y-%m-%dT%H:%M"
SEC_IN_HALFHOUR = 30 * 60


def is_roughly_now(d: dict) -> bool:
    candidate = d['startGMT'].removesuffix(":00.0")
    now = datetime.datetime.now(datetime.timezone.utc).strftime(FRMT)
    delta = datetime.datetime.strptime(now, FRMT) - datetime.datetime.strptime(candidate, FRMT)
    return delta.total_seconds() < SEC_IN_HALFHOUR


def walk_up():
    _ = mqtt_pi_speaks.publish(topic=topic_pi_to_esp,
                               payload=b'alarm_on')
    # waking up
    current_steps = 0
    try:
        api = Garmin("garmin login email", "garmin login password")
        api.login()
        while current_steps < steps_goal:
            logging.info("step goal not yet reached!")
            today = date.today()
            yesterday = date.today() - timedelta(days=1)
            yesterday_data = api.get_steps_data(today.isoformat())
            today_data = api.get_steps_data(yesterday.isoformat())

            logger.info(yesterday_data)
            logger.info(today_data)

            last_hour_response_data = ([d for d in yesterday_data[-2::] + today_data[-2::] if is_roughly_now(d)])

            # Assumption: I slept more than  half an hour. This is (Hopefully) a fair assumption.

            # current_steps = sum([d["steps"] for d in last_hour_response_data if is_roughly_now(d)])# TODO
            current_steps = sum([d["steps"] for d in last_hour_response_data])  # TODO

            logging.info(last_hour_response_data)
            logging.info("current steps:")
            logging.info(current_steps)
    except Exception as e:
        logging.info("Exception thrown!!!")
        logging.info(e)
    finally:
        a = mqtt_pi_speaks.publish(topic=topic_pi_to_esp,
                                   payload=b'alarm_off')
        print(a)
        mqtt_pi_speaks.loop(0.5)


def main():
    walk_up()


if __name__ == "__main__":
    main()
