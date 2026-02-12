#include "Arduino.h"
#include "WiFi.h"

//Mac of boss is D0:CF:13:27:F0:AC
void setup() {
  pinMode(A10,INPUT);
  analogSetAttenuation(ADC_11db);
  
  Serial.begin(115200);
  WiFi.mode(WIFI_MODE_STA);
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