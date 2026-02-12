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
  
}

void loop() {
  int ball = analogRead(A10);
  int heel = analogRead(A9);
  int spaces = heel / 52;

  for (int i = 0; i<spaces; i++) {
    Serial.print(" ");
  }
  Serial.println(heel);
  
  send(ball, heel);
  
  delay(1000);
}