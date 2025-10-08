PROGRAM MQTT

VAR
    nStep           : INT;
    fbMqttClient    : FB_IotMqttClient;
    bConnected      : BOOL;
    sTestPayload    : STRING := '{"test": "Hello AWS"}';
    tonTimeout      : TON;
	sTopicPrefix    : STRING;
	
	

	bInit: BOOL;
	sPayload: STRING(INT#24);
END_VAR

VAR
	//fb_CmdManager : Command_Protocol_Manager;
//MQTT Instance ------------------------------

//  fbMqttClient 		: FB_IotMqttClient;
	fbMessageQueue 		: FB_IotMqttMessageQueue;
	fbMessage      		: FB_IotMqttMessage;
	ServerCertificate	: BOOL;	//if FALSE the server certificate is validated (default)
//Jason Payload ------------------------------
	fbJson				: FB_JsonSaxWriter;
	fbJsonDataType		: FB_JsonReadWriteDataType;
//State variables ------------------------------
	bSetParameter		: BOOL := TRUE;
	bConnect			: BOOL := FALSE;
	bSubscribed    		: BOOL := FALSE;
	ErrorOccurred		: DINT;
	eState				: DINT;
	
//Publish payload ------------------------------
	bPublish			: BOOL;	//MQTT Publish/send message to Cloud
	sTopicPublish     	: STRING := 'bess/telemetry';
	sTopicPub_Daily   	: STRING := 'BESS/DailyData';
	fbJsonPublish     : FB_JsonDomParser;
    jsonDocPublish    : SJsonValue;
    sJsonDocPublish   : STRING(2048);
	sJsonDocPublish_RecorderData	: STRING(50000);
// Subscribe payload
    fbJsonParse       : FB_JsonDomParser;
	sTopicSubscribe   : STRING(255) := 'BESS_Command';
    jsonDocSub        : SJsonValue;
    sPayloadRcv       : STRING(2048);
    sTopicRcv         : STRING(255);

  
// Parsed command
    rCmdP             : REAL;
    rCmdQ             : REAL;
    iCmdStartStop     : UINT;   // 1 = Start, 0 = Stop
    uiCRC_Received    : UINT;
    uiCRC_Calc        : UINT;
    bCmdValid         : BOOL;	  
// Timer for periodic publish
    fbPublishTimer    		: TON;
    tPublishInterval  		: TIME := T#5S;
	
	DailyRecorderPublished	: BOOL := TRUE;	//Daily recorder trigger
	nDailyDataIndex         : UINT := 0;
	
	bSentOnce          : BOOL := FALSE; 
	
END_VAR
VAR_INPUT
	bBackup_Data							:	BOOL;	
	bReadyToTransmit						: 	BOOL;	// Trigger from Daily_Historian FB
	//Backup_LogData_In_Modbus				:	ARRAY [0..287] OF Recorder_In_Modbus; // Customize struct for Event by Modbus
	//Backup_LogData_In_Modbus_TimeStamp		:	ARRAY [0..287] OF Index_TimeStamp;
END_VAR

//a3rq4sh4gv4om5-ats.iot.eu-central-1.amazonaws.com
//"C:\certs\AmazonRootCA1.pem"
//"C:\certs\3de3beb056b0dc2a054edfd2424904106fccfe270e167615ad0e60ef204505e8-certificate.pem.crt"
//"C:\certs\3de3beb056b0dc2a054edfd2424904106fccfe270e167615ad0e60ef204505e8-private.pem.key"



IF bSetParameter THEN
    bSetParameter := FALSE;

    fbMqttClient.sHostName     := '10.200.8.213';
    fbMqttClient.nHostPort     := 1883;
    fbMqttClient.sClientId     := 'BESS_PLC1';
    fbMqttClient.sTopicPrefix  := '';                   // << no client prefix
    fbMqttClient.sUserName     := 'twincatuser';
    fbMqttClient.sUserPassword := '1';

    fbMqttClient.ipMessageQueue := fbMessageQueue;
    fbMqttClient.ActivateExponentialBackoff(T#1S, T#30S);

    // Build full topic yourself
    sTopicPublish := 'bess/telemetry';
END_IF


// Drive client cyclically
fbMqttClient.Execute(bConnect);
eState := fbMqttClient.eConnectionState;

IF fbMqttClient.bError THEN
    ErrorOccurred := fbMqttClient.hrErrorCode;
END_IF

// Send once when connected
IF (eState = 0) AND NOT bSentOnce THEN
    // Build JSON
    sJsonDocPublish := '';
    jsonDocPublish := fbJsonPublish.NewDocument();
    fbJsonPublish.AddDoubleMember(jsonDocPublish, 'Vg',   230.0);
    fbJsonPublish.AddDoubleMember(jsonDocPublish, 'P',    10.0);
    fbJsonPublish.AddDoubleMember(jsonDocPublish, 'Q',    0.0);
    fbJsonPublish.AddDoubleMember(jsonDocPublish, 'S',    10.0);
    fbJsonPublish.AddDoubleMember(jsonDocPublish, 'Freq', 50.0);
    fbJsonPublish.AddDoubleMember(jsonDocPublish, 'SOC',  75.0);
    fbJsonPublish.CopyJson(jsonDocPublish, sJsonDocPublish, SIZEOF(sJsonDocPublish));
    //fbJsonPublish.DeleteDocument(jsonDocPublish);

    // Publish (QoS 1, non-retained)
    bPublish := fbMqttClient.Publish(
        sTopic       := sTopicPublish,                         // e.g. plc/mydevice/realtime
        pPayload     := ADR(sJsonDocPublish),
        nPayloadSize := DINT_TO_UDINT(LEN(sJsonDocPublish)),
        eQoS         := TcIotMqttQos.AtLeastOnceDelivery,      // QoS 1
        bRetain      := FALSE,
        bQueue       := FALSE
    );

    bSentOnce := TRUE; // prevent spamming
END_IF


