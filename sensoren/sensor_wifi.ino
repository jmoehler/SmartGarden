#include<ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>
#include <ArduinoJson.h>
#include <ESP8266mDNS.h>
#include <ESP8266WiFiMulti.h>



//Define SSID and PASSWORD
const char* ssid = "planthubwifi";
const char* password = "WdBKADGBDRxefs6";

//IP Adresses of servers
//to authenticate
IPAddress serverIPglobal; //global ServerIP
int serverPort = 8000; //globa Server Port
String serverAuthenticate;
//to add sensor data


//global unique MacAdress of ESP
String macAdress;

//Global API_KEY
String apiKey;

//restart timer
int restartTime;

/* restart function is used: 
1. in setup()-function 
2. if ESP loses connection to reconnect 
3. when ESP gets response Code 401 */
void restart(){
  restartTime = millis();
  Serial.println("start connecting");
  //waiting for connection
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(1000);
  }
  //setup connection
  Serial.println("");
  Serial.print("connected to ");
  Serial.println(ssid);
  Serial.print("IP Adress: ");
  Serial.println(WiFi.localIP());

  /*---------find-IP+Port-----------*/
  MDNS.begin("ESP-Sensor-1");
  int nrOfServices = MDNS.queryService("http", "tcp");
  unsigned long restartTime = millis();

  while(nrOfServices == 0){
    nrOfServices = MDNS.queryService("http", "tcp");
    Serial.println("no Service found");
    if(millis()>= restartTime + 30000) {
      ESP.restart();
    }
  }
    
    for (int i = 0; i < nrOfServices; i=i+1) {
      if(MDNS.hostname(i).substring(0,8)=="PlantHub") {
      Serial.println(MDNS.hostname(i));
      Serial.println(MDNS.IP(i));
      Serial.println(MDNS.port(i));
      serverIPglobal = MDNS.IP(i);
      serverPort = MDNS.port(i);
      }
    }
    /*---------end:find-IP+Port-----------*/


  //set up WIFICLIENT and HTTPClient
  WiFiClient client;
  HTTPClient http;
  
  //Authenticate ():
  serverAuthenticate = "http://" + serverIPglobal.toString() + ":" + serverPort + "/api/authenticate";
  http.begin(client, serverAuthenticate);
  //header for authentication
  http.addHeader("Content-Type", "application/json");
  //using unique macAdress as ID for Database
  int httpResponseCode = http.POST("{\"device_type\":\"sensor-device\",\"device_id\":\"" + macAdress + "\",\"sensors\":[\"waterlevel\",\"humidity\",\"temperature\",\"ec\",\"light\",\"ph\"]}");
  Serial.print("HTTP Response code: ");
  Serial.println(httpResponseCode);
  //getting payload of http answer
  String payload = http.getString();
  Serial.println(payload);
  DynamicJsonDocument doc(1024);
  //getting API_KEY from payload
  deserializeJson(doc, payload);
  JsonObject obj = doc.as<JsonObject>();
  String aK = obj["api_key"];
  apiKey = aK;
  Serial.println("restart");
  Serial.println(apiKey);
  delay(500);

}

void setup() {


  Serial.begin(115200);

  //WIFI set to station-mode
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  //setting macAdress for ID
  macAdress = WiFi.macAddress();
  restart();
  
}


void loop() {
  //ESP restarts every 10 minutes
  if(restartTime + 60000 >= millis()){
    ESP.restart();
  }
    //Check WiFi connection status
    if(WiFi.status()== WL_CONNECTED){
      //If Arduino has sent data to ESP
      if(Serial.available() > 0) {
        //data Form: "ec;10"
        String data =  Serial.readStringUntil('!');
        //? not necessary
        data = data.substring(0 , data.length());
        splitString(data);
      
      }
      else {
        //Serial.println("no data to send in serial");
      }
    }
    else {
      Serial.println("WiFi Disconnected");
      delay(200);
      Serial.println("else");
      restart();
    }
  }

//creates a HTTP-Post with right body in Json format so hub can use data
void sendDatas(String folder, String message){
        WiFiClient client;
        HTTPClient http;
        String adress = "http://"+ serverIPglobal.toString() + ":" + serverPort + "/api/sensors/" + folder;
        http.begin(client, adress);
        http.addHeader("Content-Type", "application/json");
        http.addHeader("Authorization", apiKey);
        Serial.println(message);


        int httpResponseCode = http.POST(message);
        Serial.print("HTTP Response code: ");
        Serial.println(httpResponseCode);
        //401 = authentication error restart()-function is needed to get right API_KEY
        if (httpResponseCode == 401) {
          delay(100);
          restart();
          
        }
        
        
        // Free resources
        http.end();
}

//data comes in form: !{sensor:value}
void splitString(String data){
  //cut of first '!'
  if (data.charAt(0) == '!') {
    data = data.substring(1);
  }

  int index = data.indexOf(":");
  if(index == -1) {
    Serial.println("Warning message is in wrong form");
  }
  //save the kind of sensor in folder
  String folder = data.substring(2, index-1);
  //in this case we need a change of name
  if(folder == "visible"){
    folder = "light";
  }
  Serial.println(folder);

  sendDatas(folder, data);

  
}