# Local listener for TwinCAT and MQTT Explorer
listener 1883 0.0.0.0
allow_anonymous true

# -------- Bridge to AWS IoT Core --------
connection aws
address a3rq4sh4gv4om5-ats.iot.eu-central-1.amazonaws.com:8883
clientid MQTT-Bridge-User1
cleansession true
notifications false
try_private false
bridge_protocol_version mqttv311
bridge_tls_version tlsv1.2
keepalive_interval 60

# TLS certificates (use your working ones)
bridge_cafile C:\Users\user1\MQTT_CERT\AmazonRootCA1.pem
bridge_certfile C:\Users\user1\MQTT_CERT\my-certificate.pem.crt
bridge_keyfile C:\Users\user1\MQTT_CERT\key-private.pem.key

# Topics to forward both ways (this is key!)
topic # both 1
topic test/topic both 1
