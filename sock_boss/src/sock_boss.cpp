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

void init_ws() {
  wsHandler.onConnect([](AsyncWebSocket* server, AsyncWebSocketClient* client) {
    Serial.println("Client connected");
  });
  wsHandler.onDisconnect([](AsyncWebSocket* server, uint32_t client_id) {
    Serial.println("Client disconnected");
  });
  server.addHandler(&ws);
  server.begin();
}

void send(const JsonDocument& doc) {
  auto buf = std::make_shared<std::vector<uint8_t>>(measureJson(doc));
  serializeJson(doc, buf->data(), buf->size());
  ws.textAll(buf);
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
  init_ws();
}

void loop() {
  Serial.println("Hi");
  int heel = analogRead(A10);
  int ball = analogRead(A9);
  JsonDocument result;
  result["heel"] = heel;
  result["ball"] = ball;
  send(result);
/*   int spaces = value / 52;

  for (int i = 0; i<spaces; i++) {
    Serial.print(" ");
  }
  Serial.println(value); */

  delay(100);
}