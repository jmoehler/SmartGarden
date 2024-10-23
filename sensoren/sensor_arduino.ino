#include <DHT.h>
#include "SI114X.h"

/*----------------------------------------------------*/
#define EC_SensorPin 1  //analogPin for EC Pin
#define InputVolt 5   //input Volt
float waterTemp = 20;
float EC_Value = 0;

/*----------------------------------------------------*/
#define TemHum_SensorPin 2  //digitalPin for TemHum Pin on the Shield
#define DHTTYPE DHT22
DHT dht(TemHum_SensorPin, DHTTYPE);
float temp_hum_val[2] = { 0 };  //temp_hum_val[0] = humi; temp_hum_val[1] = temp
float temp = 0;
float humi = 0;

/*----------------------------------------------------*/
#define Water_SensorPin 6  //digitalPin. Water Pin on the Shield
int water = 0;             // 0 = water, 1 = no water

/*----------------------------------------------------*/
#define PH_SensorPin 0 //analogpin 1
float ph = 0;

/*----------------------------------------------------*/
SI114X Sunlight_Sensor = SI114X();  //Sunlight is in I2C and will recognized automatically
float vis = 0;
float ir = 0;
float uv = 0;

/*----------------------------------------------------*/
//timer
unsigned long current_Millis = 0;
unsigned long current_Millis_send = 0;
int timePerSensor = 1000;

//Count for Mean
int count = 0;

/*----------------------------------------------------*/
//Later for Debugging to be done
bool bSun = true;
bool bTempHum = true;
bool bPH = true;
bool bWater = true;
bool bEC = true;
/*----------------------------------------------------*/

void setup() {
  Serial.begin(115200);
  pinMode(EC_SensorPin, INPUT);
  pinMode(Water_SensorPin, INPUT); 
  pinMode(PH_SensorPin, INPUT);
  Sunlight_Sensor.Begin();
  
}

void loop() {

  /*----------------------------------------------------*/
  //Loop for EC Sensor
  if(bEC){
    current_Millis = millis();
    while (1) {
      if (millis() >= current_Millis + timePerSensor) {
        EC_Value = EC_Value/count;                // Mean of EC_Value   
        EC_Value = convertVoltageToPPM(EC_Value); // Convert Voltage to PPM
        count = 0;                                // reset count for next Loop
        bEC = false;
        break;
      }
      EC_Value += analogRead(EC_SensorPin);
      count ++;
      delay(100); //Sensor ließt sehr schnell
    }
  }
    
  /*----------------------------------------------------*/
  //Loop for Tem/Hum Sensor
  if(bTempHum){
    current_Millis = millis();
    while (1) {
      if (millis() >= current_Millis + timePerSensor) {
        humi = humi / count;
        temp = temp / count;
        count = 0;
        bTempHum = false;
        break;
      }
      dht.readTempAndHumidity(temp_hum_val);
      humi += temp_hum_val[0];
      temp += temp_hum_val[1];
      count ++;
    }
  }

  /*----------------------------------------------------*/
  //Loop for PH Sensor
  if(bPH){
    current_Millis = millis();
    while (1) {
      if (millis() >= current_Millis + timePerSensor) {
        ph = ph/count;        // Mean of EC_Value
        ph = phConverter(ph);
        count = 0;                        // reset count for next Loop
        bPH = false;
        break;
      }
      ph += analogRead(PH_SensorPin);
      count ++;
      delay(100);
    }
  }

   /*----------------------------------------------------*/
  //Loop for Light Sensor
  if(bSun){
    current_Millis = millis();
    while(1){
      if(millis() >= current_Millis + timePerSensor){
        vis = vis / count;
        ir = ir / count;
        uv = uv / count;
        count = 0;
        bSun = false;
        break;
      }
      vis += Sunlight_Sensor.ReadVisible();
      ir  += Sunlight_Sensor.ReadIR();
      uv  += ((float)Sunlight_Sensor.ReadUV() / 100);
      count ++;
    }
  }
  ----------------------------------------------------*/
  //Watersensor
  if(bWater){
    water = digitalRead(Water_SensorPin);
    bWater = false;
  }
/*----------------------------------------------------*/
  //Send Function
  if(millis() >= current_Millis_send + 6000){ // so we have regulared time to send

  //send function form is important for ESP to read
    String dataToWrite = "{\"waterlevel\":\"" + String(water) + "\"}!";//send waterlevel
    Serial.write(dataToWrite.c_str(), dataToWrite.length());

    dataToWrite = "{\"temperature\":\"" + String(temp) + "\"}!"; //send temperature
    Serial.write(dataToWrite.c_str(), dataToWrite.length());

    dataToWrite = "{\"humidity\":\"" + String(humi) + "\"}!"; //send humidity
    Serial.write(dataToWrite.c_str(), dataToWrite.length());

    dataToWrite = "{\"ec\":\"" + String(EC_Value) + "\"}!"; //send EC
    Serial.write(dataToWrite.c_str(), dataToWrite.length());
    
    dataToWrite = "{\"ph\":\"" + String(ph) + "\"}!"; //send ph
    Serial.write(dataToWrite.c_str(), dataToWrite.length());

    dataToWrite = "{\"visible\":\"" + String(vis) + "\"," + "\"ir\":\"" + String(ir) + "\"," + "\"uv\":\"" + String(uv) + "\"}!"; //send vis
    Serial.write(dataToWrite.c_str(), dataToWrite.length());



    resetValues();
    current_Millis_send += 6000;
}


}

/*----------------------------------------------------*///Functions
void printFunction(String SensorID, String TypeOfSensor, String NameOfValue, float Value){

  Serial.print(SensorID);
  Serial.print(TypeOfSensor);
  Serial.print("  ");
  Serial.print(NameOfValue);
  Serial.print(" :  ");
  Serial.println(Value);
  //Serial.println(millis());

}

void resetValues(){ //reset Values for the next loop
  EC_Value = 0;
  humi = 0;
  temp = 0;
  water = 0;
  ph = 0;
  vis = 0;
  ir = 0;
  uv = 0;

  bSun = true;
  bTempHum = true;
  bPH = true;
  bWater = true;
  bEC = true;

}

float phConverter(float value){
  value = value * 5 / 1024;
  value = value * 3.5;
  return value;

}

float convertVoltageToPPM(float volt){
    volt = volt * (float)InputVolt / 1024.0;
    float compensationCoefficient = 1.0 + 0.02 * (waterTemp - 25.0);
    float compensationVolatge = volt / compensationCoefficient;
    volt = (133.42 * compensationVolatge * compensationVolatge * compensationVolatge - 255.86 * compensationVolatge * compensationVolatge + 857.39 * compensationVolatge) * 0.5;
    return volt;
}