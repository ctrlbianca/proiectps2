
#define LED_PIN 2
#define WATER_SENSOR_PIN 4
#define TEMP_SENSOR_PIN 34

#include <EEPROM.h>

float temperature = 0;
bool floodDetected = false;
String messages[10];
int messageIndex = 0;
int floodIndex = 0;

void setup() {
  Serial.begin(9600);
  pinMode(LED_PIN, OUTPUT);
  pinMode(WATER_SENSOR_PIN, INPUT);
  EEPROM.begin(512);
}

void loop() {
  int sensorValue = analogRead(TEMP_SENSOR_PIN);
  temperature = (sensorValue * 3.3 / 4095.0) * 100;
  Serial.print("Temperature: ");
  Serial.println(temperature);

  int waterState = digitalRead(WATER_SENSOR_PIN);
  if (waterState == HIGH) {
    floodDetected = true;
    Serial.println("Flood");
    saveFloodEvent();
  }

  if (Serial.available() > 0) {
    char command = Serial.read();
    if (command == 'A') {
      digitalWrite(LED_PIN, HIGH);
    } else if (command == 'S') {
      digitalWrite(LED_PIN, LOW);
    } else if (command == 'M') {
      String message = Serial.readStringUntil('\n');
      saveMessage(message);
    }
  }

  delay(2000);
}

void saveMessage(String msg) {
  if (messageIndex < 10) {
    EEPROM.put(messageIndex * 50, msg);
    messageIndex++;
  }
}

void saveFloodEvent() {
  if (floodIndex < 10) {
    String event = "Flood detected";
    EEPROM.put(500 + floodIndex * 50, event);
    floodIndex++;
  }
}
