import paho.mqtt.client as mqtt 
import json
import sys
import time
import argparse
import logging
import logging.config
import logging.handlers


#Global Variable declaration
connected = False
Publish_log = False

def parse_argv(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("--conf", required=True)
    args = parser.parse_args(argv)
    args = vars(args)    
    return args

def mqtt_conn(params):
    assert params is not None, "param mqtt_conn_info missing"
    broker    = params.get("broker")
    topic     = params.get("topic")
    port      = params.get("port")
    interval  = params.get("interval")
    qos       = params.get("qos")
    keepalive = params.get("keepalive")
    log       = params.get("log")
    return broker,topic,port,interval,qos,log,keepalive

def on_connect(client, userdata, flags, rc):
    global connected 
    if rc==0:
        connected = True
        logger.info("Connected to broker '{}:{}', Broadcasting started...".format(broker,port)) 
    else:
        logger.info("Bad connection Returned code=",rc)
        connected = False

def on_disconnect(client, userdata, rc):
    if rc==0:
        logger.info("Publisher got forcefully disconnected in an active connection.")
        logger.info("Restart to reconnect")
        
    else:
        logger.info("Connection failed with return code: {}, retrying..".format(rc))
        logger.info("waiting to reconnect...")

    connected = False
    
def on_publish(client, userdata, mid):
    global Publish_log
    if Publish_log is None or Publish_log is False:
        logger.info("Message {} published on topic:'{}', Qos level:{}".format(mid,topic,qos))
        # print("Telemetry Message Published")
        Publish_log = True
    else:
        pass
    

def on_log(client, userdata, level, buf):
    print("log: ",buf)

def main():
    mqtt_client = mqtt.Client(client_id="NDC",clean_session=False)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_disconnect = on_disconnect
    mqtt_client.on_publish = on_publish
    mqtt_client.on_log = on_log

    try:
        mqtt_client.connect(broker,port,keepalive)
    except Exception as e :
        logger.exception("Mqtt client could not connect to broker")
        connected = False
        pass
    try:
        mqtt_client.loop_start()
        publish_payload = "HI"

        while True:
            mqtt_client.publish(topic,publish_payload,qos=qos)
            time.sleep(interval)

    except Exception as e:
        logger.exception("Mqtt client could not publish to broker due to:{}".format(repr(e)))
        mqtt_client.loop_stop()
        pass
    
    except KeyboardInterrupt:
        logger.info("User stopped ")
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
        sys.exit()

if __name__ == "__main__":
    #Reading Params from Conf file
    try:

        args = parse_argv(sys.argv[1:])
        
        if args is None:
            pass
                
        conf_file=args.get("conf")

        try:
            with open(conf_file,"r+") as fp:
                params   = json.load(fp)
        except Exception as e:
            print("exception in loading conf file- {}".format(repr(e)))
            pass

        broker,topic,port,interval,qos,log,keepalive = mqtt_conn(params.get("mqtt_conn_info"))
        assert keepalive is not None, "param keepalive missing"
        assert broker is not None, "param broker missing"
        assert interval is not None,"param time missing"
        assert topic is not None, "param topic missing"
        assert port is not None, "param port missing"
        assert imo is not None,"params imo missing"
        assert qos is not None, "Param qos missing"
        assert log is not None, "param log missing"

    except Exception as e:
        print("Exception in reading conf file {}".format(repr(e)))
        pass

    try:
        logging.config.fileConfig('logging.conf')
    except Exception as e:
        try:
            logging.config.fileConfig('conf/logging.conf')
        except Exception as e:
            print("exception in getting logger : {}".format(repr(e)))
            # Suppress overly verbose logs from libraries that aren't helpful
            logging.getLogger('requests').setLevel(logging.WARNING)
            logging.getLogger('urllib3').setLevel(logging.WARNING)    
            logging.getLogger('paho').setLevel(logging.WARNING)             
        # seems that you cannot change the timestamp to UTC in config file, must be done in code
    logging.Formatter.converter = time.gmtime
    logger = logging.getLogger(log)
    logger.setLevel(logging.INFO)
        
    try:
        logger.info("Publisher Started ")
        main()
    except Exception as e:
        logger.info("exception in calling main: {}".format(repr(e)))
        pass