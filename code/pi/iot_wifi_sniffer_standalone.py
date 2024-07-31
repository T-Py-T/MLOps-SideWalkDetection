#!/usr/bin/env python
from kismetclient import Client as KismetClient
from kismetclient import handlers
from pprint import pprint
from datetime import datetime
import time
import sys


from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import time

myMQTTClient = AWSIoTMQTTClient("mopronav1")
myMQTTClient.configureEndpoint("a2i1o7pgs400o2-ats.iot.us-east-2.amazonaws.com", 8883)
myMQTTClient.configureCredentials("cert/AmazonRootCA1.pem", "cert/ff4c1398db-private.pem.key", "cert/ff4c1398db-certificate.pem.crt")
myMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec


def customCallback(client, userdata, message):
    print(message.payload)

def publishWifiData(lat, lon, alt, time, mac, manuf, bssid):
    myMQTTClient.publish("mopronav/msg/wifi", "{ \"tim\": \"" + str(time) + "\", \"lat\": " + str(lat) + ", \"lon\":  " + str(lon) + ", \"alt\": " + str(alt) + ", \"mac\": \"" + str(mac) + "\", \"manu\": \"" + str(manuf) + "\", \"bssi\": \"" + str(bssid) + "\" }", 0)

def publishLPRData(lat, lon, alt, time, plate):
    myMQTTClient.publish("mopronav/msg/lpr", "{ \"tim\": \"" + str(time) + "\", \"lat\": " + str(lat) + ", \"lon\":  " + str(lon) + ", \"alt\": " + str(alt) + ", \"plate\": \"" + str(plate) + "\" }", 0)



# manuf_list = ['Apple', 'SamsungE', 'Htc', 'LcfcHefe', 'LgElectr', 'AmazonTe', 'Microsof', 'Motorola', 'HonHaiPr,', 'Google']
manuf_list = ['Apple', 'SamsungE', 'Htc', 'LgElectr', 'Motorola', 'Nokia', 'Zte', 'HuaweiTe', 'TclTechn']

network_array = {}

address1 = ('127.0.0.1', 2501)
k1 = KismetClient(address1)


def handle_ssid(client, **fields):
    network_array[fields['mac']] = fields['ssid']

def handle_client(client, **fields):
    # if fields['manuf'].strip() in manuf_list:
    the_network = ""
    if fields['bssid'] in network_array:
        the_network = network_array[fields['bssid']]
        if the_network.strip() is "":
            the_network = fields['bssid']
    else:
        the_network = fields['bssid']

    theResult = ("1 - " + fields['mac'] + " - " + fields['manuf'] + " - " + time.strftime('%H:%M:%S', time.localtime(int(fields['lasttime']))) + " - " + the_network )
    print (theResult)
    publishWifiData (-84.1234,39.767777,270.3,time.time(),fields['mac'], fields['manuf'], the_network)

try:
    myMQTTClient.connect()


    k1.register_handler('CLIENT', handle_client)

    k1.register_handler('SSID', handle_ssid)

    while True:
        #start = time.time()
        try:
            k1.listen()
        except KeyboardInterrupt:
            raise KeyboardInterrupt;
        except:
            print ("Unexpected error:", sys.exc_info())
        #print(time.time()-start)

except KeyboardInterrupt:
    # pprint(k.protocols)
    # pprint(source1_list)
    # pprint(source2_list)
    # pprint(network_array)
    # myMQTTClient.unsubscribe("mopronav/msg/status")
    myMQTTClient.disconnect()
    print ("")
    print ("Exiting...")
