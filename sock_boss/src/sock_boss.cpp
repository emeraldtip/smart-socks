#include <Arduino.h>
#include <WiFi.h>
#include <ESPmDNS.h>
#include <ESPAsyncWebServer.h>

#include "secrets.h"

void init_wifi() {
/*  WiFi.mode(WIFI_MODE_STA);
  WiFi.begin(wifi_ssid, wifi_pass);*/
  WiFi.mode(WIFI_MODE_APSTA);
  WiFi.softAP("sock_boss", "smartsocks",6);
  WiFi.softAPConfig(IPAddress(192, 168, 4, 1), IPAddress(192, 168, 4, 1), IPAddress(255, 255, 255, 0));
  Serial.println(WiFi.macAddress());
  Serial.println("");
  bool success = MDNS.begin("sock_boss");
  MDNS.addService("_http", "_tcp", 80);
  if (success) {
    Serial.println("MDNS Success!");
  }
}

static AsyncWebServer server(80);

JsonDocument result;

void init_site() {
  DefaultHeaders::Instance().addHeader("Access-Control-Allow-Origin", "*");
  server.on("/", HTTP_GET, [](AsyncWebServerRequest *request) {
    AsyncResponseStream* responseStream = request->beginResponseStream("application/json");
    serializeJson(result, *responseStream);
    request->send(responseStream);
  });
  server.on("/update", HTTP_POST, [](AsyncWebServerRequest *request) {}, nullptr, [](AsyncWebServerRequest *request, uint8_t* data, size_t len, size_t index, size_t total) {
    Serial.println(len);
    if (len == 8) {
      Serial.println(*(int*)data);
      result["ball2"] = *(int*)data;
      Serial.println(*(int*)(data+4));
      result["heel2"] = *(int*)(data+4);
    }
    request->send(200);
  });
  // maybe more cors stuff
  server.onNotFound([](AsyncWebServerRequest *request){
    if (request->method() == HTTP_OPTIONS) {
      request->send(200);
    } else {
      request->send(404);
    }
  });
  server.begin();
}

//Mac of boss is D0:CF:13:27:F0:AC
void setup() {
  pinMode(A10,INPUT);
  pinMode(A5,INPUT);
  analogSetAttenuation(ADC_11db);
  Serial.begin(115200);
  //while (!Serial.available()) {
  //  delay(500);
  //}
  init_wifi();
  init_site();
}

void loop() {
  int heel1 = analogRead(A10);
  int ball1 = analogRead(A5);
  result["heel1"] = heel1;
  result["ball1"] = ball1;
  result["time"] = millis();
/*   int spaces = value / 52;

  for (int i = 0; i<spaces; i++) {
    Serial.print(" ");
  }
  Serial.println(value); */

  delay(100);
}