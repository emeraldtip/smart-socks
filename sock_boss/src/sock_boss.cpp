#include <Arduino.h>
#include <WiFi.h>
#include <ESPmDNS.h>
#include <ESPAsyncWebServer.h>

#include "secrets.h"



void init_wifi() {
  WiFi.mode(WIFI_MODE_STA);
  WiFi.begin(wifi_ssid, wifi_pass);
  Serial.print("Establishing wifi...");
  
  while (WiFi.status()!=WL_CONNECTED) {
    delay(500);
    Serial.print('.');
  }
  WiFi.setHostname("sock_boss");
  Serial.println("");
  bool success = MDNS.begin("sock_boss");
  MDNS.addService("_http", "_tcp", 80);
  if (success) {
    Serial.println("MDNS Success!");
  }
}

static AsyncWebServer server(80);
static AsyncWebSocketMessageHandler wsHandler;
static AsyncWebSocket ws("/ws", wsHandler.eventHandler());

void init_websocket() {

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
  init_websocket();
}

void loop() {
  int value = analogRead(A10);
  int spaces = value / 52;

  for (int i = 0; i<spaces; i++) {
    Serial.print(" ");
  }
  Serial.println(value);
  delay(100);
}