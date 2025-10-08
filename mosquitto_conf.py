
# ===================== LOCAL BROKER =====================

# ---- Plain MQTT for local clients (TwinCAT, MQTT Explorer) ----
listener 1883 0.0.0.0
allow_anonymous false
password_file C:/Program Files/mosquitto/passwd.txt
persistence true

# ---- (Optional) TLS listener for local secure clients ----
# If you don't need local TLS, comment this whole block.
listener 8883 0.0.0.0
allow_anonymous true
# Local TLS files (optional)
#cafile   "C:/Program Files/mosquitto/mosquitto_certs/AmazonRootCA1.pem"
#certfile "C:/Program Files/mosquitto/mosquitto_certs/server.crt"
#keyfile  "C:/Program Files/mosquitto/mosquitto_certs/server.key"
#require_certificate false

# ===================== AWS IOT BRIDGE =====================

connection MyAwsBridge
address a3rq4sh4gv4om5-ats.iot.eu-central-1.amazonaws.com:8883
clientid MyAwsTestClient
bridge_protocol_version mqttv311
bridge_tls_version tlsv1.2
cleansession true
keepalive_interval 60
restart_timeout 5
try_private false
bridge_attempt_unsubscribe false
notifications false

# ---- Bridge TLS (AWS device credentials) ----
# Use your AWS device certificate + private key (unencrypted) and Amazon Root CA
bridge_cafile   C:/Program Files/mosquitto/mosquitto_certs/AmazonRootCA1.pem
bridge_certfile C:/Program Files/mosquitto/mosquitto_certs/cert.pem.crt
bridge_keyfile  C:/Program Files/mosquitto/mosquitto_certs/mypem.unencrypted.key

# ---- Topic mapping between LOCAL <-> AWS ----
# Send local topics to AWS
topic plc/mydevicetest/topic both 1
topic plc/mydevice/# out 1
topic bess/telemetry out 1
topic bess/test out 0

# Receive from AWS into local broker
topic bess/telemetry in 1
topic bess/test in 0

