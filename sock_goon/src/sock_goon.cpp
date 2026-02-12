#include <Arduino.h>
#include <WiFi.h>

#include "secrets.h"

//Mac of boss is D0:CF:13:27:F0:AC

WiFiClient client;
IPAddress server(192, 168, 4, 1);

void setup() {
  pinMode(A10,INPUT);
  pinMode(A9,INPUT);
  analogSetAttenuation(ADC_11db);
  
  Serial.begin(115200);
  while (!Serial.available()) {
    delay(500);
  }
  
  WiFi.mode(WIFI_STA);
  WiFi.begin("sock_boss", "smartsocks");
  
  Serial.print("Connecting wifi...");
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print('.');
    delay(1000);
  }
  Serial.println();
  if (!client.connect(server, 80)) {
    Serial.println("connection failed");
  }
}

void send(int ball, int heel) {
  client.println("POST /update HTTP/1.1");
  client.println("Host: 192.168.4.1");
  client.println("Content-Type: application/octet-stream");
  client.println("Content-Length: 8");
  client.println();
  client.write((const uint8_t*)&ball, 4);
  client.write((const uint8_t*)&heel, 4);
}

void loop() {
  int heel = analogRead(A10);
  int ball = analogRead(A9);
  int spaces = heel / 52;

  for (int i = 0; i<spaces; i++) {
    Serial.print(" ");
  }
  Serial.println(heel);
  
  send(heel, ball);
  
  delay(1000);
}