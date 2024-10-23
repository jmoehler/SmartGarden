const int TimePerPump = 5000; //Time per Pump - for fertilizer
const long TimePerPumpWater = 300000; //300000 = 5min = 500ml to pump for water to refill
//---------------------------------
const int WaterPump1 = 7;  // Every Pump gets initialized and has 3 variables
long timePump1 = 0 ;
bool Pump1 = false;
//----------------------------------
const int WaterPump2 = 8;  // Der Pin, an dem das Relais von der Pumpe2 angeschlossen ist
long timePump2 = 0 ;
bool Pump2 = false;
//------------------------------------------
const int WaterPump3 = 9;  // Der Pin, an dem das Relais von der Pumpe3 angeschlossen ist
long timePump3 = 0 ;
bool Pump3 = false;
//----------------------------------------------------
#define Water_SensorPin 6  //digitalPin. Water Pin on the Shield
bool waterlevel = true;             // true = water allowed, false = no more water allowed

//----------------------------------------------------


void setup() {
  Serial.begin(115200); 
  pinMode(WaterPump1, OUTPUT); //Set Up Waterpump1 for Water
  pinMode(WaterPump2, OUTPUT); // Set Up Waterpump2
  pinMode(WaterPump3, OUTPUT); // Set Up Waterpump3
  pinMode(Water_SensorPin, INPUT); // Set Up Watersensor
  waterCheck();
}

void loop() {
  //------------------------------------------ avoid overpumping
waterCheck();
if(waterlevel == false) { // if water ius full
  Serial.println("MSG:waterlevel is full!"); //Water is full in general
  if(Pump1 == true|| Pump2 == true || Pump3 == true) { // if just one of the pumps is pumping
    digitalWrite(WaterPump1, LOW); // stop waterpump1 pumping
    Pump1 = false;
    digitalWrite(WaterPump2, LOW); // stop waterpump2 pumping
    Pump2 = false;
    digitalWrite(WaterPump3, LOW); // stop waterpump3 pumping
    Pump3 = false;
  }
}


//----------------------------------------------   Every Pump gets shutdown after x seconds
/*-------timelimit-pump1----------*/
if(millis()>(timePump1 + TimePerPumpWater) && Pump1){ // if pump1 reached timelimit
  Pump1 = false; // shut down Pump1
  digitalWrite(WaterPump1, LOW);
  Serial.println("Switching off Pump1");
}
//-----------------------------------------------
/*-------timelimit-pump2----------*/
if(millis()>timePump2 + TimePerPump && Pump2){ // if pump2 reached timelimit
  Pump2 = false;// shut down Pump2
  digitalWrite(WaterPump2, LOW);
  Serial.println("Switching off Pump2");
}
//-----------------------------------------------
/*-------timelimit-pump3----------*/
if(millis()>timePump3 + TimePerPump && Pump3){ // if pump2 reached timelimit
  Pump3 = false; // shut down Pump2
  digitalWrite(WaterPump3, LOW);
  Serial.println("Switching off Pump3");
}
//--------------------------------------------
/*---------message-handling------------*/
if (Serial.available() > 0) {                 //if a message from esp comes then react          
    String data = Serial.readStringUntil('!');
    Serial.println(data);
//--------------------------------------------
    if (data.charAt(0) == '!') {    // cuts out the ! of the string
      data = data.substring(1);
    }
    if(data.length()>0) {

      Serial.println(data);
//----------------------------------------------------------
    int index = data.indexOf(":");                           
    if(index == -1) {
      Serial.println("Warning message is in wrong form");
    }
      String actor = data.substring(0, index);                 // divide String in actor and order
      String order = data.substring(index+1, data.length());   //actor is Typeof "Pump1" and order is Typeof "1"
//----------------------------------------------------------
      Serial.println("<" + actor + ">");
      Serial.println("<" + order + ">");
//---------------------------------------------------------- After data is split into actor and order the we switch the right pump on
      if (actor == "Pump1") {  // check for pump
        if (order == "1") { //check for order ("1 = turn on")
          if (waterlevel == true) { //check for waterlevel (true = not full)
            Serial.println("Switching on Pump1"); 
            digitalWrite(WaterPump1, HIGH);
            timePump1 = millis();
            Pump1 = true;
            Serial.println("MSG:waterpump1 is on!");
          }
          
        }
      else { // is not actually used right now. Maybe useful for more complex messages from HUB
          Serial.println("Switching off...");
          digitalWrite(WaterPump1, LOW);
        }
      }
 //----------------------------------------------------------
    
      else if (actor == "Pump2") {  //same as pump1
        if (order == "1") {
          if (waterlevel == true) {
            Serial.println("Switching on Pump2");
            digitalWrite(WaterPump2, HIGH);
            timePump2 = millis();
            Pump2 = true;
            Serial.println("MSG:ECpump2 is on!"); 
          }
        } 
        else {
          digitalWrite(WaterPump2, LOW);
        }
      }
    //----------------------------------------------------------
      else if (actor == "Pump3") {  // same as pump1
        if (order == "1") {
          if (waterlevel) {
            Serial.println("Switching on Pump3");
            digitalWrite(WaterPump3, HIGH);
            timePump3 = millis() ;
            Pump3 = true;
            Serial.println("MSG:pump3 is on!");
          }
        } else {
          digitalWrite(WaterPump3, LOW);
        }
      }
    //----------------------------------------------------------
      else {
        Serial.println("Actor not supported...");
      }
      delay(200);
    }
  } 
}

void waterCheck() { //watercheck function is always checked before doing anything
  if (digitalRead(Water_SensorPin) == 0) {
    waterlevel = false;
  }
  else {
    waterlevel = true;
  }
}