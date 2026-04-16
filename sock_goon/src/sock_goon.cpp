#include <Arduino.h>
#include <WiFi.h>

#include "secrets.h"

//Mac of boss is D0:CF:13:27:F0:AC

WiFiClient client;
IPAddress server(192, 168, 4, 1);

#define heel2 A8 //Heel sensor, number 4 - yellow
#define ball2 A0 //Ball sensor, number 6 - orange
#define balli2 A3 //Ball sensor, number 3 - blue

void setup() {
  pinMode(heel2,INPUT);
  pinMode(ball2,INPUT);
  pinMode(balli2,INPUT);
  pinMode(21,OUTPUT); //LED
  analogSetAttenuation(ADC_11db);
  
  Serial.begin(115200);
  delay(1000);
  //while (!Serial.available()) {
  //  delay(500);
  //}
  
  WiFi.mode(WIFI_STA);
  WiFi.begin("sock_boss", "smartsocks");
  
  Serial.print("Connecting wifi...");
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print('.');
    delay(1000);
  }
  Serial.println();
}

void send(int heel, int ball, int balli) {
  if (!client.connect(server, 80)) {
    Serial.println("connection failed");
  }
  client.println("POST /update HTTP/1.1");
  client.println("Host: 192.168.4.1");
  client.println("Content-Type: application/octet-stream");
  client.println("Content-Length: 8");
  client.println("Connection: keep-alive");
  client.println();
  client.write((const uint8_t*)&heel, 4);
  client.write((const uint8_t*)&ball, 4);
  client.write((const uint8_t*)&balli, 4);
}

bool blinker = false;
void loop() {
  int heel = analogRead(heel2);
  int ball = analogRead(ball2);
  int balli = analogRead(balli2);

  //for (int i = 0; i<spaces; i++) {
  //  Serial.print(" ");
  //}
  //Serial.println(heel);
  
  send(heel, ball, balli);
  
  blinker = !blinker;
  digitalWrite(21,blinker); //blinky the led to indicate board is alive
  
  
  //Reconnect logic
  if (WiFi.status() != WL_CONNECTED) {
    WiFi.disconnect();
    
    WiFi.begin("sock_boss", "smartsocks");
    Serial.print("Connecting wifi...");
    
    while (WiFi.status() != WL_CONNECTED) {
      Serial.print('.');
      delay(1000);
    }
    Serial.println();
  }
  
  delay(100);
}