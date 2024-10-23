#include <ESP8266WiFi.h>
#include <WiFiClient.h>
#include <ESP8266HTTPClient.h>
#include <ESP8266WiFiMulti.h> 
#include <ESP8266mDNS.h>
#include <ESP8266WebServer.h>   // Include the WebServer library
#include <ArduinoJson.h>

ESP8266WiFiMulti wifiMulti;     // Create an instance of the ESP8266WiFiMulti class, called 'wifiMulti'
ESP8266WebServer server(6000);    // Create a webserver object that listens for HTTP request on port 80

String IPAdress;
String ServerPort;
String serverAuthenticate;  // IP Adress of server
String macAdress = WiFi.macAddress();
String apiKey;
int timeSetup;
int whileConnect = 0;
int whileServices = 0;
int whileResponse = 0;

String requestData = "{\"device_type\":\"actuator-device\",\"device_id\":\""+ macAdress +"\",\"actuators\":[\"waterpump\",\"ecpump\",\"phpump\"]}";  // with this string the esp will register at hub

#define WiFiName "planthubwifi"  // SSID of Wifi
#define WiFiPassword "WdBKADGBDRxefs6"    // PAssword of Wifi

void connectToWiFi() {
  while (wifiMulti.run() != WL_CONNECTED) {
    //Serial.print("Trying to connect to <");
    //Serial.print(WiFiName);
    //Serial.print("> with password <");
    //Serial.print(WiFiPassword);
    //Serial.println(">!");
    delay(500);
    if(millis() >= whileConnect + 30000)ESP.restart();
  }

  //Serial.print("Connected to ");
  //Serial.println(WiFi.SSID());
  //Serial.print("IP address:\t");
  //Serial.println(WiFi.localIP());

  MDNS.begin("device0");
  int nrOfServices = MDNS.queryService("http", "tcp");
  
  while(nrOfServices == 0) {
    nrOfServices = MDNS.queryService("http", "tcp");
    //Serial.println("No services were found.");
    delay(500);
    if(millis() >= whileServices+30000)ESP.restart();
  }
    
  for (int i = 0; i < nrOfServices; i=i+1) {

    //Serial.println("---------------");
    
    
  String hostname = MDNS.hostname(i);
      
    hostname = (hostname.substring(0, 8));
  if(hostname == "PlantHub"){ 
  IPAdress =  MDNS.IP(i).toString();
  ServerPort = String(MDNS.port(i));
  serverAuthenticate = String("http://") + IPAdress + ":" + ServerPort + "/api/authenticate";
  //Serial.println(serverAuthenticate);
    }
  }

  

}

void authenticateAtHub() {
  int httpResponseCode = 400;
  WiFiClient client;
  HTTPClient http;

  while(httpResponseCode != 200) {
    http.begin(client, serverAuthenticate);
    http.addHeader("Content-Type", "application/json");
    httpResponseCode = http.POST(requestData);
    if(httpResponseCode!= 200){
    //Serial.println("Could not authenticate at hub...");
    //Serial.println(httpResponseCode);
    }
    if(millis() >= whileResponse + 30000)ESP.restart();
    delay(500);
  }

  String payload = http.getString();     // in this block the esp get the api key of the hub and extract it from the getMethod
  //Serial.println(macAdress);
  DynamicJsonDocument doc(1024);
  deserializeJson(doc, payload);
  JsonObject obj = doc.as<JsonObject>();
  String aK = obj["api_key"];
  apiKey = aK;
  //Serial.print("api-key: ");
  //Serial.println(apiKey);
}

void setup(void){
  Serial.begin(115200);         // Start the Serial communication to send messages to the computer
  //Serial.println('\n');
  //Serial.println("In setup...");
  delay(3000);

  wifiMulti.addAP(WiFiName, WiFiPassword);    //connect with wifi
  
  connectToWiFi();  

  authenticateAtHub();
  
  server.on("/", handleRoot);               // Call the 'handleRoot' function when a client requests URI "/"
  server.onNotFound(handleNotFound);        // When a client requests an unknown URI (i.e. something other than "/"), call function "handleNotFound"
  server.on("/api/waterpump", HTTP_POST, handleWaterpumppost);  //Callback for Waterpump
  server.on("/api/phpump", HTTP_POST, handlePhpumppost);      //Callback for Phpump
  server.on("/api/ecpump", HTTP_POST, handleEcpumppost);        //Callback for Ecpump
  server.begin();                           // Actually start the server
}

void loop(void){
  server.handleClient();                    // Listen for HTTP requests from clients
  if(wifiMulti.run() != WL_CONNECTED){
    setup();
  }
  if(millis() >=  timeSetup + 600000){   // All 10 minutes it will call setup if sql restarts to register again
  timeSetup = millis();
    ESP.restart();
  }
}

void handleRoot() {
  server.send(200, "text/plain", "Device is working!");   // Send HTTP status 200 (Ok) and send some text to the browser/client
}

void handleNotFound(){
  server.send(404, "text/plain", "404: Not found"); // Send HTTP status 404 (Not Found) when there's no handler for the URI in the request
}




void handleWaterpumppost() {
  String message = server.arg("plain");
  DynamicJsonDocument doc(1024);
  deserializeJson(doc, message);
  JsonObject obj = doc.as<JsonObject>();  // Hier musst du 'doc' verwenden, nicht 'message'
  String me = obj["toggle"];
  handleMessage("Pump1", "1");
  
  // send back 200 status
  server.send(200, "application/json", "{\"status\":\"on\"}");


}
void handlePhpumppost() {
  String message = server.arg("plain");
  DynamicJsonDocument doc(1024);
  deserializeJson(doc, message);
  JsonObject obj = doc.as<JsonObject>();  // Hier musst du 'doc' verwenden, nicht 'message'
  String me = obj["toggle"];
  handleMessage("Pump2", "1");
  
  // send back 200 status
  server.send(200, "application/json", "{\"status\":\"on\"}");
   


}
void handleEcpumppost() {
  String message = server.arg("plain");
  DynamicJsonDocument doc(1024);
  deserializeJson(doc, message);
  JsonObject obj = doc.as<JsonObject>();  // Hier musst du 'doc' verwenden, nicht 'message'
  String me = obj["toggle"];
  handleMessage("Pump3", "1");
  

  // send back 200 status
  server.send(200, "application/json", "{\"status\":\"on\"}");


}

void handleMessage(String device, String order){ // writes the order to the arduino as Pump1:1!
  String dataToWrite = device + ":" + order + "!";
  Serial.write(dataToWrite.c_str(), dataToWrite.length());
  Serial.println(dataToWrite);
} 