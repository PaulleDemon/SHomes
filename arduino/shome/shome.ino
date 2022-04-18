#include <string.h>
#include <Servo.h>
#include <SoftwareSerial.h>
#include <ArduinoJson.h>


#define LED1 8
#define LED2 9
#define MOTOR 3

void setup(){

    Serial.begin(9600);
    Serial.println("Starting...");

    pinMode(LED1, OUTPUT);
    pinMode(LED2, OUTPUT);
    pinMode(MOTOR, OUTPUT);
    
}

void loop(){

    if (Serial.available()){
        String instruction = Serial.readString();
        
        if (!instruction || instruction.equals("off")){
            digitalWrite(LED1, LOW);
            digitalWrite(LED1, LOW);
            analogWrite(MOTOR, 0);
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

              analogWrite(MOTOR, fanSpeed*63); // we get 63 from dividing 255/4 because 4 is the max speed defined in frontend
 
          }
        }
        Serial.write("done");

    }

  
}
