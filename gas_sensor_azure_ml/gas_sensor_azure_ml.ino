#include <ArduinoJson.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SH110X.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1

Adafruit_SH1106G display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

bool displayInitialized = false;

#define PH_MIN 6.5
#define PH_MAX 7.5
#define BIOGAS_MIN 50
#define BIOGAS_MAX 80
#define GAS_THRESHOLD 350

void setup() {
  Serial.begin(9600);
  
  pinMode(A0, INPUT);
  pinMode(A1, INPUT);
  
  Wire.begin();
  
  Serial.println("Starting display initialization...");
  
  display.begin(0x3C, true);
  delay(100);
  
  display.clearDisplay();
  
  display.setTextColor(SH110X_WHITE);
  display.setTextSize(1);
  
  display.setCursor(0, 0);
  display.println("BIOSERDE");
  display.display();
  
  displayInitialized = true;
  Serial.println("Display setup complete");
  
  delay(1000);
}

void loop() {
  float temperature = random(300, 450) / 10.0;
  float ph = analogRead(A0) * 0.01;
  float biogas = analogRead(A1) * 0.1;
  int gas_level = analogRead(A1) * 2;
  
  Serial.print(temperature, 1);
  Serial.print(",");
  Serial.print(ph, 2);
  Serial.print(",");
  Serial.println(gas_level);
  
  if (displayInitialized) {
    display.clearDisplay();
    
    display.setTextSize(1);
    display.setCursor(0, 0);
    display.println("BIOSERDE");
    
    display.setCursor(0, 10);
    display.print("TEMP: ");
    display.print(temperature, 1);
    display.println("C");
    
    display.setCursor(0, 20);
    display.print("pH: ");
    display.println(ph, 1);
    
    String phStatus = getStatus(ph, PH_MIN, PH_MAX);
    display.setCursor(80, 20);
    display.print(phStatus);
    
    display.setCursor(0, 30);
    display.print("GAS: ");
    display.println(gas_level);
    
    String gasStatus = (gas_level < GAS_THRESHOLD) ? "NORMAL" : "HIGH";
    display.setCursor(80, 30);
    display.print(gasStatus);
    
    display.drawLine(0, 40, display.width(), 40, SH110X_WHITE);
    
    display.setCursor(0, 50);
    display.print("STATUS: ");
    
    if (phStatus == "HIGH" || gasStatus == "HIGH") {
      display.println("HIGH");
    } else if (phStatus == "LOW") {
      display.println("LOW");
    } else {
      display.println("NORMAL");
    }
    
    display.display();
  }
  
  delay(5000);
}

String getStatus(float value, float minThreshold, float maxThreshold) {
  if (value < minThreshold) {
    return "LOW";
  } else if (value > maxThreshold) {
    return "HIGH";
  } else {
    return "NORMAL";
  }
}