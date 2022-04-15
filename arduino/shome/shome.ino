#include <string.h>
#include <Servo.h>
#include <SoftwareSerial.h>
#include <ArduinoJson.h>



#define RX 3
#define TX 4

SoftwareSerial Bluetooth(RX, TX);

void setup(){

    Serial.begin(9600);
    Bluetooth.begin(38400);
    Serial.println("Starting...");
}

void loop(){
   

    if (Bluetooth.available()){
        String instruction = Bluetooth.readString();

        Serial.print(instruction);

        DynamicJsonDocument jdoc(2048);

        DeserializationError jsonParseError = deserializeJson(jdoc, instruction);
      
        if(jsonParseError){
            Serial.println("Error parsing JSON");
        }
        else{

            int fanSpeed = jdoc["fanspeed"];
            bool light1 = jdoc["light1"];
            bool light2 = jdoc["light2"];

            Serial.println(fanSpeed);
            Serial.println(light1);
            Serial.println(light2);
        }

        Bluetooth.write("done");

    }

    else
      Serial.println("Not available");
  
}
