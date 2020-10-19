# Usage:
>> python3 publisher.py --conf config.json

# Basic configuration
Add your configurations in config file for broker
{
  "mqtt_conn_info":
  {
    "broker": "127.0.0.1", "port": 1883, "topic": "ndc/sec", "interval": 1, "qos": 2, "keepalive": 60, "log": "mqtt_per_sec"
  }
}
