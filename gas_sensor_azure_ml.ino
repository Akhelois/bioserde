#include <Wire.h>

const int phSensorPin = A0;
const int biogasProductionSensorPin = A1;
const int alarmLedPin = 13;
const int buzzerPin = 8;

const long readingInterval = 7200000;
const long testingInterval = 10000;
unsigned long lastReadingTime = 0;

float phValue = 0.0;
float biogasProduction = 0.0;

bool anomalyDetected = false;
int anomalyCount = 0;
String anomalyCause = "";

void setup() {
  Serial.begin(9600);
  delay(1000);
  
  pinMode(phSensorPin, INPUT);
  pinMode(biogasProductionSensorPin, INPUT);
  pinMode(alarmLedPin, OUTPUT);
  pinMode(buzzerPin, OUTPUT);
  
  Wire.begin();
  
  Serial.println("Biogas Monitoring System Started");
  Serial.println("Using wired connection to send data to Azure ML");
  
  for (int i = 0; i < 3; i++) {
    digitalWrite(alarmLedPin, HIGH);
    delay(100);
    digitalWrite(alarmLedPin, LOW);
    delay(100);
  }
}

void loop() {
  unsigned long currentMillis = millis();
  
  if (currentMillis - lastReadingTime >= testingInterval || lastReadingTime == 0) {
    lastReadingTime = currentMillis;
    takeReading();
  }
  
  checkForCommands();
  
  if (anomalyDetected) {
    triggerAlarm();
  }
  
  delay(100);
}

void takeReading() {
  readSensors();
  sendDataToSerial();
}

void readSensors() {
  int rawpH = analogRead(phSensorPin);
  phValue = map(rawpH, 0, 1023, 0, 140) / 10.0;
  
  int rawBiogas = analogRead(biogasProductionSensorPin);
  biogasProduction = map(rawBiogas, 0, 1023, 10, 90);
}

void sendDataToSerial() {
  Serial.print("{");
  Serial.print("\"ph\":");
  Serial.print(phValue, 2);
  Serial.print(",\"biogas_production\":");
  Serial.print(biogasProduction, 2);
  Serial.println("}");
}

void checkForCommands() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    
    if (command == "READ") {
      takeReading();
    }
    else if (command.startsWith("RESULT:")) {
      processMLResult(command.substring(7));
    }
    else if (command == "RESET_ALARM") {
      anomalyDetected = false;
      anomalyCount = 0;
      anomalyCause = "";
      digitalWrite(alarmLedPin, LOW);
      digitalWrite(buzzerPin, LOW);
    }
  }
}

void processMLResult(String result) {
  int commaIndex = result.indexOf(',');
  if (commaIndex > 0) {
    String anomalyStr = result.substring(0, commaIndex);
    String cause = result.substring(commaIndex + 1);
    
    int anomalyStatus = anomalyStr.toInt();
    
    if (anomalyStatus == 1) {
      anomalyDetected = true;
      anomalyCount++;
      anomalyCause = cause;
      
      Serial.print("ANOMALY DETECTED! Cause: ");
      Serial.println(anomalyCause);
    } else {
      Serial.println("System normal");
      anomalyDetected = false;
    }
  }
}

void triggerAlarm() {
  digitalWrite(alarmLedPin, HIGH);
  delay(100);
  digitalWrite(alarmLedPin, LOW);
  delay(100);
  
  if (anomalyCount > 3) {
    digitalWrite(buzzerPin, HIGH); 
    delay(50);
    digitalWrite(buzzerPin, LOW);
  }
}