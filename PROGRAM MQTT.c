PROGRAM MQTT

VAR
    nStep           : INT;
    fbMqttClient    : FB_IotMqttClient;
    bConnected      : BOOL;
    sTestPayload    : STRING := '{"test": "Hello AWS"}';
    tonTimeout      : TON;
	a3rq4sh4gv4om5: INT;
	eErrorId: INT;
	Reset: INT;
	eErrId: INT;
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
	bConnect			: BOOL := TRUE;
	bSubscribed    		: BOOL := FALSE;
	ErrorOccurred		: DINT;
	eState				: DINT;
//Publish payload ------------------------------
	bPublish			: BOOL;	//MQTT Publish/send message to Cloud
	sTopicPublish     	: STRING := 'BESS/Measurements';
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
END_VAR
VAR_INPUT
	bBackup_Data							:	BOOL;	
	bReadyToTransmit						: 	BOOL;	// Trigger from Daily_Historian FB
	//Backup_LogData_In_Modbus				:	ARRAY [0..287] OF Recorder_In_Modbus; // Customize struct for Event by Modbus
	//Backup_LogData_In_Modbus_TimeStamp		:	ARRAY [0..287] OF Index_TimeStamp;
END_VAR










// MQTT Configuration: set parameters once when connecting to the mqtt broker

IF bSetParameter THEN
    bSetParameter               := FALSE;
	
    fbMqttClient.sHostName      := 'a3rq4sh4gv4om5-ats.iot.eu-central-1.amazonaws.com';
	fbMqttClient.sHostName      := '10.200.8.213';
    fbMqttClient.nHostPort      := 1883;
	fbMqttClient.sClientId 		:= 'BESS_PLC1';
	fbMqttClient.sTopicPrefix := 'plc/mydevice';
	fbMqttClient.sUserName      :=  'twincatuser';
	fbMqttClient.sUserPassword  := '1';

    fbMqttClient.ipMessageQueue := fbMessageQueue;
	fbMqttClient.ActivateExponentialBackoff(T#1S, T#30S);
	
	
END_IF
eState := fbMqttClient.eConnectionState;

fbMqttClient.Execute(bConnect);		// MQTT client must be triggered cyclically, in order to ensure that a connection to the broker is established and maintained and the message is received.
IF fbMqttClient.bError THEN			//Error checking
	ErrorOccurred := fbMqttClient.hrErrorCode;
END_IF


//MQTT client set 
IF fbMqttClient.bConnected THEN
    sTopicPublish := '/test/topic';
    //sJsonDocPublish := '{"Vg":230,"P":10}';
    bPublish := fbMqttClient.Publish(
        sTopic := sTopicPublish,
        pPayload := ADR(sJsonDocPublish),
        nPayloadSize := DINT_TO_UDINT(LEN(sJsonDocPublish)),
        eQoS := TcIotMqttQos.AtLeastOnceDelivery,
        bRetain := FALSE,
        bQueue := TRUE
    );
END_IF

// Publish to JSON to AWS when connected

IF fbMqttClient.bConnected THEN
    // Run timer continuously
    fbPublishTimer(IN := TRUE, PT := tPublishInterval);
01
    IF fbPublishTimer.Q THEN
        fbPublishTimer(IN := FALSE); // reset timer
        fbPublishTimer(IN := TRUE);  // restart for next cycle

        // ---- Build JSON payload ----
        sJsonDocPublish := 'REAL TIME BESS DATA';
        jsonDocPublish := fbJsonPublish.NewDocument();

		fbJsonPublish.AddDoubleMember(jsonDocPublish, 'BESS ID', 19029);
        fbJsonPublish.AddDoubleMember(jsonDocPublish, 'Vg', 230);
        fbJsonPublish.AddDoubleMember(jsonDocPublish, 'P', 10);
        fbJsonPublish.AddDoubleMember(jsonDocPublish, 'Q', 0);
        fbJsonPublish.AddDoubleMember(jsonDocPublish, 'S', 10);
        fbJsonPublish.AddDoubleMember(jsonDocPublish, 'Freq', 50);
        fbJsonPublish.AddDoubleMember(jsonDocPublish, 'SOC', 75);

        fbJsonPublish.CopyJson(jsonDocPublish, sJsonDocPublish, SIZEOF(sJsonDocPublish));

        // ---- Publish to MQTT ----
        bPublish := fbMqttClient.Publish(
            sTopic := sTopicPublish,
            pPayload := ADR(sJsonDocPublish),
            nPayloadSize := DINT_TO_UDINT(LEN(sJsonDocPublish)),
            eQoS := TcIotMqttQos.AtLeastOnceDelivery,
            bRetain := FALSE,
            bQueue := FALSE
        );
    END_IF
END_IF
