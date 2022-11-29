# Copyright (c) Quectel Wireless Solution, Co., Ltd.All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@file      :dtu.py
@author    :elian.wang@quectel.com
@brief     :dtu main function
@version   :0.1
@date      :2022-05-18 09:12:37
@copyright :Copyright (c) 2022
"""

import sim, dataCall, net, modem, utime, _thread
from usr.common import Singleton
from usr.mqttIot import MqttIot
from usr.logging import getLogger
from usr.settings import settings
from usr.settings import PROJECT_NAME, PROJECT_VERSION, DEVICE_FIRMWARE_NAME, DEVICE_FIRMWARE_VERSION

import checkNet
import utime
from misc import Power

from machine import Pin  # 导入Pin模块
LED_B = Pin(Pin.GPIO32, Pin.OUT, Pin.PULL_DISABLE, 0)  # GPIO32配置成输出模式，默认输出0
LED_G = Pin(Pin.GPIO33, Pin.OUT, Pin.PULL_DISABLE, 0)  # GPIO33配置成输出模式，默认输出0

log = getLogger(__name__)




def cloud_init(data):
    protocol = data.get("protocol").lower()
    if protocol == "mqtt":
        mqtt_iot = MqttIot(data.get("url", None),
                            int(data.get("qos", 0)),
                            int(data.get("port", 1883)),
                            int(data.get("cleanSession", 0)),
                            data.get("clientID"),
                            data.get("username"),
                            data.get("passwd"),
                            int(data.get("keep_alive", 0)),
                            data.get("publish"),
                            data.get("subscribe")
                            )
        mqtt_iot.init(enforce=True)
        # mqtt_iot.addObserver(remote_sub)
        # remote_pub.add_cloud(mqtt_iot, cid)
        # self.__channel.cloud_object_dict[cid] = mqtt_iot
    else:
        log.error("no mqtt conf!")
        return False

def run():
    log.info("PROJECT_NAME: %s, PROJECT_VERSION: %s" % (PROJECT_NAME, PROJECT_VERSION))
    log.info("DEVICE_FIRMWARE_NAME: %s, DEVICE_FIRMWARE_VERSION: %s" % (DEVICE_FIRMWARE_NAME, DEVICE_FIRMWARE_VERSION))

    checknet = checkNet.CheckNetwork(PROJECT_NAME, PROJECT_VERSION)
    checknet.poweron_print_once()
    try:
        checknet.wait_network_connected()
    except BaseException:
        print('Not Net, Resatrting...')
        utime.sleep_ms(200)
        Power.powerRestart()
    
    cloud_init(settings.current_settings.get("conf"))

    while 1:
        utime.sleep_ms(100)


if __name__ == "__main__":
    run()

