#include <Arduino.h>
#include <WiFi.h>
#include <ESPmDNS.h>
#include "secrets.h"
#include <WifiServer.h>
#include <ArduinoJson.hpp>

using namespace ArduinoJson;

void init_wifi() {
  WiFi.mode(WIFI_MODE_STA);
  WiFi.begin(wifi_ssid, wifi_pass);
  Serial.print("Establishing wifi...");
  WiFi.setHostname("sock_boss");
  while (WiFi.status()!=WL_CONNECTED) {
    delay(500);
    Serial.print('.');
  }
  
  Serial.println("");
  bool success = MDNS.begin("sock_boss");
  MDNS.addService("_http", "_tcp", 80);
  if (success) {
    Serial.println("MDNS Success!");
  }
}

JsonDocument result;
WiFiServer server(80);

void init_site() {
  server.begin();
}

//Mac of boss is D0:CF:13:27:F0:AC
void setup() {
  pinMode(A10,INPUT);
  pinMode(A9,INPUT);
  analogSetAttenuation(ADC_11db);
  Serial.begin(115200);
  while (!Serial.available()) {
    delay(500);
  }
  init_wifi();
  init_site();
}

void loop() {
  int heel = analogRead(A10);
  int ball = analogRead(A9);
  result["heel"] = heel;
  result["ball"] = ball;
  serializeJson(result, server);
  /*   int spaces = value / 52;

  for (int i = 0; i<spaces; i++) {
    Serial.print(" ");
  }
  Serial.println(value); */

  delay(200);
}