#include <WiFi.h>
#include <WiFiClient.h>
#include <WebServer.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <ESPmDNS.h>

#define STASSID "planthubwifi"
#define STAPSK  "WdBKADGBDRxefs6"

/* wifi connection details */
const char* ssid = STASSID;
const char* password = STAPSK;

/* hub connection details */
int ServerPort;
IPAddress ServerIp;

/* own connection details */
String mac;
IPAddress ip;
const int port = 6000;

/* authenticaion related variables */
String ServerAuth = "";                 // prototype: "http://<hub_ip_address>:<hub_port>/api/authenticate"
String apiKey;                          // API-key, used for authenication between hub and esp

/* restart timer (used to restart esp every 10 minutes) */
unsigned long genarlRestartTimer;

/* server hosted on esp */
WebServer httpServer(port); 

void setup(void) {
  Serial.begin(115200);
  genarlRestartTimer = millis();
  pinMode(19, OUTPUT);            // Pin der LED


  /* connect to wifi and authenticate at hub */
  WiFi.mode(WIFI_AP_STA);
  connectToNetwork();


  /* set server routes */
  httpServer.onNotFound(handleNotFound);
  httpServer.on("/api/led", HTTP_POST, handleLEDtoggle); 
  httpServer.on("/api/led", HTTP_GET, handleLEDstatus);
  
  /* tell server to track headers */
  const char* headerkeys[] = {"Authorization"};
  size_t headerkeysize = sizeof(headerkeys)/sizeof(char*);
  httpServer.collectHeaders(headerkeys, headerkeysize);

  /* start server */
  httpServer.begin();
}

void loop(void) {
  httpServer.handleClient();

  /* reconnect if wifi disconnects */
  if(WiFi.waitForConnectResult() != WL_CONNECTED){ 
    connectToNetwork();
  }

  /* restart esp every 10 minutes */
  if(millis() >= genarlRestartTimer + 600000){ 
    ESP.restart();
  }

}

void getServerIP(){ 
  unsigned long restartTimerIp = millis();

  /* start mDNS responder/reciever */
  while(mdns_init()!= ESP_OK){
    Serial.println("mDNS failed to start");
    /* restart if mDNS work after 30 seconds */
    if(millis() >= restartTimerIp + 30000){
      ESP.restart();
    }
  }

  /* find all services in network which host a http server using tcp transmission */
  int nrOfServices = MDNS.queryService("http", "tcp");
  while(nrOfServices == 0){
    nrOfServices = MDNS.queryService("http", "tcp");
    Serial.println("no services found ");
    /* restart if mDNS work after 30 seconds */
    if(millis() >= restartTimerIp + 30000){
      ESP.restart();
    }
  }

  Serial.print(nrOfServices);
  Serial.println(" services found ");
  
  /* check if the PlantHub is online */
  for (int i = 0; i < nrOfServices; i=i+1) {
    /* and extract the connection details provided over mDNS */
    if(MDNS.hostname(i).substring(0,8) == "PlantHub"){
      Serial.println(MDNS.hostname(i));
      Serial.println(MDNS.IP(i));
      Serial.println(MDNS.port(i));
      ServerIp = MDNS.IP(i);
      ServerPort = MDNS.port(i);
    }
  }

}

void authenticateAtHub(){ 
  WiFiClient client; 
  HTTPClient httpclient;

  /* connect to hub under API url */ 
  ServerAuth = "http://"+ ServerIp.toString() +":"+ ServerPort +"/api/authenticate";
  httpclient.begin(client, ServerAuth);

  /* restart */
  httpclient.addHeader("Content-Type", "application/json");
  int httpResponseCode = httpclient.POST("{\"device_type\":\"actuator-device\",\"device_id\":\"" + mac + "\",\"actuators\":[\"led\"]}"); //Schickt eine Anfrage zum verifizieren an den HUB und Speichert den Response Code
  
  unsigned long restartTimerHub= millis();
  while(httpResponseCode != 200){ //Solange ein falscher Response Code gesendet wird
    httpResponseCode = httpclient.POST("{\"device_type\":\"actuator-device\",\"device_id\":\"" + mac + "\",\"actuators\":[\"led\"]}");
    if(millis() >= restartTimerHub + 30000){ //wenn der ESP nach 30s immernoch nicht verifiziert wurde oder sich garnicht erst mit dem Server verbinden konnte, wird der ESP neugestartet
      ESP.restart();
    }
    delay(100);
  
  }

  //----------- extrahieren des mitgesendeten Api keys ---------------
  String Payload = httpclient.getString(); 
  DynamicJsonDocument doc(1024);
  deserializeJson(doc, Payload);
  JsonObject obj = doc.as<JsonObject>();
  String aK = obj["api_key"];
  apiKey = aK;                               
  Serial.println(apiKey);                   
  //------------------------------------------------------------------

  Serial.println("fertig Verifiziert");
}

void connectToNetwork(){ //stellt eine Verbindung zum WLAN her und verifiziert sich anschließend beim HUB
  
  Serial.println("Connecting");
  WiFi.begin(ssid, password); // Versuch sich mit den WLAN zu verbinden
  unsigned long restartTimerWlan = millis();
  while (WiFi.waitForConnectResult() != WL_CONNECTED) { //Solange keine Verbindung zum WLAN besteht
    WiFi.begin(ssid, password); // Versuch sich mit den WLAN zu verbinden
    Serial.println("WiFi failed, retrying.");
    if(millis() >= restartTimerWlan + 30000){ //wenn nach 30s immernoch keine verbindung zum Wlan hergestellt werden konnte wird der ESP neugestartet
      ESP.restart();
    }
    delay(100);
  }

  Serial.println("WiFi connected");

  mac = WiFi.macAddress();
  ip = WiFi.localIP();

  getServerIP();

  authenticateAtHub();
}

void handleNotFound(){
  httpServer.send(404, "text/plain", "404: Not found");
}

void handleLEDtoggle(){
  //---------------- auslesen des befehls (on oder off) -------------------
  String message = httpServer.arg("plain");
  DynamicJsonDocument doc(1024);
  deserializeJson(doc, message);
  JsonObject obj = doc.as<JsonObject>();
  String cmd = obj["toggle"];
  //------------------------------------------------------------------------

  if (!isAuthentified()){
    httpServer.send(400, "application/json", "{\"error\":\"wrong api\"}");
    return;
  }

  Serial.println("Anfrage kam an");

  if(cmd =="on"){
    digitalWrite(19, HIGH);
    httpServer.send(200, "application/json", "{\"status\":\"on\"}");
    Serial.println("Led on");
  } else if(cmd == "off") {
    digitalWrite(19, LOW);
    httpServer.send(200, "application/json", "{\"status\":\"off\"}");
    Serial.println("Led off");
  } else {
    httpServer.send(400, "application/json", "{\"error\":\"something went wrong\"}");
  }
}

void handleLEDstatus(){

  if (!isAuthentified()){
    httpServer.send(400, "application/json", "{\"error\":\"wrong api\"}");
    return;
  }

  int status = digitalRead(19);
  if (status == LOW) {
    httpServer.send(200, "application/json", "{\"status\":\"off\"}");
  } else if(status == HIGH){
    httpServer.send(200, "application/json", "{\"status\":\"on\"}");
  } else {
    httpServer.send(400, "application/json", "{\"error\":\"something went wrong\"}");
  }

}

bool isAuthentified(){ // überprücft ob der mitgesendete api key mit den bei der verifizierung gesendeten api key übereinstimmt
  
  String ServerApi;
  if(httpServer.hasHeader("Authorization")){
    ServerApi = httpServer.header("Authorization");
  }
  if(apiKey == ServerApi){
    return true;
  } else {
    return false;
  }
  
}