#include <string.h>
#include <Servo.h>
#include <SoftwareSerial.h>
#include <ArduinoJson.h>


#define LED1 8
#define LED2 9

void setup(){

    Serial.begin(9600);
    Serial.println("Starting...");

    pinMode(LED1, OUTPUT);
    pinMode(LED2, OUTPUT);
}

void loop(){
   

    if (Serial.available()){
        String instruction = Serial.readString();

        if (instruction.equals("off")){
            digitalWrite(LED1, LOW);
            digitalWrite(LED1, LOW);
            return;
        }

        else {
          StaticJsonDocument<1024> jdoc;
  
          DeserializationError error = deserializeJson(jdoc, instruction);
          
          if(error){
              Serial.println("Error parsing JSON");
              Serial.write("Error parsing JSON\n");
          }
          else{
  
              int fanSpeed = jdoc["fanspeed"];
              bool light1 = jdoc["light1"];
              bool light2 = jdoc["light2"];
  
              digitalWrite(LED1, LOW); 
              digitalWrite(LED2, LOW);
              
              if (light1){
                digitalWrite(LED1, HIGH);
              }
                    
              if (light2){
                digitalWrite(LED2, HIGH);
              }
         
  //            Serial.println(fanSpeed);
  //            Serial.println(light1);
  //            Serial.println(light2);
          }
        }
        Serial.write("done");

    }

    else;
      //Serial.println("Not available");
  
}
