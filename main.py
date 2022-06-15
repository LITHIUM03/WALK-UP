import os
from datetime import datetime
from datetime import timedelta
from paho.mqtt import client as mqtt_client
import re
import subprocess

import logging

FORMAT = '%(asctime)s %(levelname)-8s %(message)s'

logging.basicConfig(filename="daemon.log", level=logging.DEBUG, datefmt='%Y-%m-%d %H:%M:%S', format=FORMAT)
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logging.debug("Debug logging")

steps_goal = 30

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~ MQTT DETAILS~~~~~~~~~~~~~~~~~~~~~~~~~~~#
broker = '0.1.2.3'  # RPi IP
port = 1883

topic_pi_to_esp = "pi_to_esp"
topic_new_alarms = "new_alarms"

mqtt_listen_new_alarms = mqtt_client.Client("pi_listen")
mqtt_listen_new_alarms.connect(broker, port, keepalive=600)
mqtt_listen_new_alarms.subscribe(topic_new_alarms)


# ~~~~~~~~~~~~~~~~~~~~~~~~~ MQTT DETAILS END ~~~~~~~~~~~~~~~~~~~~~~~~~#


def is_legal_alarm(m):
    reg = "^([0-1][0-9]|[2][0-3]):([0-5][0-9])$"
    return re.match(reg, m)


def on_message(client, userdata, message):
    s_message = message.payload.decode('utf-8')
    if re.match(r'^Alarm was', s_message):
        # print("RPi sent it. ignore.")
        return

    if is_legal_alarm(s_message):
        logger.info("legal alarm was requested, for hour" + s_message)
        # alarm will be set to the closest HH:MM.
        # This implies that an alarm can only be set 24H beforehand. We wish to calculate delta(now,HH:MM)
        delta = timedelta(hours=int(s_message.split(":")[0].removeprefix("0")),
                          minutes=int(s_message.split(":")[1].removeprefix("0"))) - \
                timedelta(hours=datetime.now().hour,
                          minutes=datetime.now().minute)
        if delta.days == -1:
            delta += timedelta(days=1)
        logger.info("it is {delta} times from now".format(delta=delta))
        # _ = mqtt_listen_new_alarms.publish(topic=topic_pi_to_esp,
        #                                    payload=(str(delta.total_seconds()).removesuffix(".0").encode('utf-8')))
        mqtt_listen_new_alarms.loop(0.1)
        _ = mqtt_listen_new_alarms.publish(topic=topic_new_alarms,
                                           payload=('Alarm was set!' + ' wake up in ' + delta.__str__().split(":")[
                                               0] + " Hours " + delta.__str__().split(":")[0] + " Minutes" \
                                                    + '.\nGood night!').encode('utf-8'))

        # Schedule with at
        walk_up_path = os.getcwd() + "/wake-up.py"
        cmd = "echo \"" + walk_up_path + "\" | at " + s_message.removesuffix(":00")
        logger.info("this is the 'at' command that wasa used for scheduling {cmd}".format(cmd=cmd))
        try:
            at_id = subprocess.check_output(cmd, shell=True,
                                            stderr=subprocess.STDOUT).decode(
                "utf-8")  # for future feature: disable set alarms
            logger.info("this is what 'at' printed: {at_id}".format(at_id=at_id))
            # print(at_id)
            # print("python scheduled an alarm using at. id is: " + at_id)
            # print("python scheduled an alarm using at.")
            _ = mqtt_listen_new_alarms.publish(topic=topic_pi_to_esp,
                                               payload=b'alarm_set')

        except Exception as e:
            logging.debug("EXCEPTION")
            logging.debug(e)
            mqtt_listen_new_alarms.publish(topic=topic_new_alarms,
                                           payload=b'Alarm was not set. Something went BAD!')
    else:
        logger.info("invalid alarm request was received: {s}".format(s=s_message))
        mqtt_listen_new_alarms.publish(topic=topic_new_alarms,
                                       payload=b'Alarm was not set. Please use DD:MM in a 24 hour format')


mqtt_listen_new_alarms.on_message = on_message
mqtt_listen_new_alarms.loop_forever()
