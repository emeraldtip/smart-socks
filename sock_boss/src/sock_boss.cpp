#include <Arduino.h>
#include <WiFi.h>
#include <ESPmDNS.h>
#include <ESPAsyncWebServer.h>
#include "secrets.h"

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

static AsyncWebServer server(80);

JsonDocument result;
std::string text;

void init_site() {
  server.on("/", HTTP_GET, [](AsyncWebServerRequest *request) {

    request->send(200, "text/html", (const uint8_t *)text.data(), text.size());
  });
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
  serializeJson(result, text);
/*   int spaces = value / 52;

  for (int i = 0; i<spaces; i++) {
    Serial.print(" ");
  }
  Serial.println(value); */

  delay(200);
}