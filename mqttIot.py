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
@file      :mqttIot.py
@author    :elian.wang@quectel.com
@brief     :universal mqtt iot inferface
@version   :0.1
@date      :2022-05-18 13:28:53
@copyright :Copyright (c) 2022
"""

import ujson
import utime
import _thread
from umqtt import MQTTClient
from usr.logging import getLogger
from usr.settings import settings
log = getLogger(__name__)

class MqttIot():

    def __init__(self, server, qos, port, clean_session, client_id, username, password, life_time=30, pub_topic=None, sub_topic=None):

        self.conn_type = "mqtt"
        self.__server = server
        self.__qos = qos
        self.__port = port
        self.__mqtt = None
        self.__clean_session = clean_session
        self.__life_time = life_time
        self.__client_id = client_id
        self.__username = username
        self.__password = password

        if pub_topic == None:
            self.pub_topic_dict = {"0": "/python/mqtt/pub"}
        else:
            self.pub_topic_dict = pub_topic
        if sub_topic == None:
            self.sub_topic_dict = {"0": "/python/mqtt/sub"}
        else:
            self.sub_topic_dict = sub_topic

    def __subscribe_topic(self):
        for id, usr_sub_topic in self.sub_topic_dict.items():
            if self.__mqtt.subscribe(usr_sub_topic, qos=0) == -1:
                log.error("Topic [%s] Subscribe Falied." % usr_sub_topic)


    def __sub_cb(self, topic, data):
        """mqtt subscribe topic callback

        Parameter:
            topic: topic info
            data: response dictionary info
        """
        topic = topic.decode()
        try:
            data = ujson.loads(data)
        except:
            pass
        log.info("topic: %s, data: %s" % (topic, data))
        if topic.endswith("/post_reply"):
            pass
        elif topic.endswith("/property/set"):
            if data["method"] == "thing.service.property.set":
                # if "Pressure" in data["params"]:
                #     pressure = data["params"].get("Pressure")
                #     log.info("set Pressure : %s" % pressure)
                # if "Temperature" in data["params"]:
                #     temperature = data["params"].get("Temperature")
                #     log.info("set Temperature : %s" % temperature)
                if "Interval" in data["params"]:
                    interval = data["params"].get("Interval")
                    log.info("set Interval : %s" % interval)
                    settings.current_settings["collectCycle"] = interval
                    

        elif topic.startswith("/ota/device/upgrade/"):
            pass
            # print("subscribe /ota/device/upgrade/")
            # self.__put_post_res(data["id"], True if int(data["code"]) == 1000 else False)
            # if int(data["code"]) == 1000:
            #     if data.get("data"):
            #         self.__ota.set_ota_info(data["data"])
            #         self.notifyObservers(self, *("object_model", [("ota_status", (data["data"]["module"], 1, data["data"]["version"]))]))
            #         self.notifyObservers(self, *("ota_plain", [("ota_cfg", data["data"])]))
        else:
            log.warning("not match topic")


    def __listen(self):
        while True:
            self.__mqtt.wait_msg()
            utime.sleep_ms(100)

    def __start_listen(self):
        """Start a new thread to listen to the cloud publish 
        """
        _thread.start_new_thread(self.__listen, ())

    def init(self, enforce=False):
        """mqtt connect and subscribe topic

        Parameter:
            enforce:
                True: enfore cloud connect and subscribe topic
                False: check connect status, return True if cloud connected

        Return:
            Ture: Success
            False: Failed
        """
        log.debug("[init start] enforce: %s" % enforce)
        if enforce is False and self.__mqtt is not None:
            log.debug("self.get_status(): %s" % self.get_status())
            if self.get_status():
                return True

        if self.__mqtt is not None:
            self.close()
        
        log.debug("__server: %s" % self.__server)
        log.debug("__port: %s" % self.__port)
        log.debug("__client_id: %s" % self.__client_id) 
        log.debug("__username: %s" % self.__username) 
        log.debug("__password: %s" % self.__password)
              
        self.__mqtt = MQTTClient(client_id=self.__client_id, server=self.__server, port=self.__port,
                              user=self.__username, password=self.__password, keepalive=self.__life_time, ssl=False)
        try:
            self.__mqtt.connect(clean_session=self.__clean_session)
        except Exception as e:
            log.error("mqtt connect error: %s" % e)
        else:
            self.__mqtt.set_callback(self.__sub_cb)
            self.__subscribe_topic()
            log.debug("mqtt n_subscribe_topic")
            self.__start_listen()
            log.debug("mqtt start.")

        log.debug("self.get_status(): %s" % self.get_status())
        if self.get_status():
            return True
        else:
            return False

    def close(self):
        self.__mqtt.disconnect()

    def get_status(self):
        """Get mqtt connect status

        Return:
            True -- connect success
            False -- connect falied
        """
        try:
            return True if self.__mqtt.get_mqttsta() == 0 else False
        except:
            return False
    
    def through_post_data(self, data, topic_id):
        try:
            self.__mqtt.publish(self.pub_topic_dict[topic_id], data, self.__qos)
        except Exception:
            log.error("mqtt publish topic %s failed. data: %s" % (self.pub_topic_dict[topic_id], data))
            return False
        else:
            return True

    def post_sensor_data(self, press, temp):
        try:
            # sensor_data = {"params":{"Pressure":press,"Temperature":temp}}
            sensor_data = {"params": {"Pressure": 10.1, "Temperature": 50.4}}
            log.info(sensor_data)
            log.info(type(sensor_data))
            data = ujson.dumps(sensor_data)
            log.info(data)
            log.info(type(data))            
            self.__mqtt.publish(self.pub_topic_dict["0"], data, self.__qos)
        except Exception:
            log.error("mqtt publish topic %s failed. data: %s" % (self.pub_topic_dict["1"], data))
            return False
        else:
            return True

    def ota_request(self):
        pass

    def ota_action(self, action, module=None):
        pass
    
    def device_report(self):
        pass
