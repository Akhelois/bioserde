#include <ArduinoJson.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SH110X.h>

// OLED display configuration (simplified)
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1

// Try different display libraries
// Option 1: SH1106 - Most common
Adafruit_SH1106G display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// Global variables
bool displayInitialized = false;

// Define thresholds for status
#define PH_MIN 6.5
#define PH_MAX 7.5
#define BIOGAS_MIN 50
#define BIOGAS_MAX 80
#define GAS_THRESHOLD 350

void setup() {
  Serial.begin(9600);
  
  // Basic sensor setup
  pinMode(A0, INPUT); // pH sensor
  pinMode(A1, INPUT); // gas sensor
  
  // Initialize I2C with standard clock
  Wire.begin();
  
  Serial.println("Starting display initialization...");
  
  // Try with address 0x3C first (most common)
  display.begin(0x3C, true);
  delay(100);
  
  // Check if display responds correctly
  display.clearDisplay();
  
  // CRITICAL: Set display to BLACK, not WHITE (inverted)
  display.setTextColor(SH110X_WHITE); // WHITE text on BLACK background
  display.setTextSize(1); // Small text
  
  // Try to show some minimal text
  display.setCursor(0, 0);
  display.println("BIOSERDE");
  display.display();
  
  displayInitialized = true;
  Serial.println("Display setup complete");
  
  delay(1000);
}

void loop() {
  // Read sensor data
  float ph = analogRead(A0) * 0.01;
  float biogas = analogRead(A1) * 0.1;
  int gas_level = analogRead(A1) * 2;
  
  // Create and send JSON
  StaticJsonDocument<128> doc;
  doc["ph"] = ph;
  doc["biogas_production"] = biogas;
  doc["gas_level"] = gas_level;
  serializeJson(doc, Serial);
  Serial.println();
  
  // Very minimal display update
  if (displayInitialized) {
    // BLACK BACKGROUND with WHITE text is the normal mode
    // (opposite would make screen all white)
    display.clearDisplay(); // Important to clear the display
    
    // Simple text only
    display.setTextSize(1);
    display.setCursor(0, 0);
    display.println("BIOSERDE");
    
    display.setCursor(0, 10);
    display.print("pH: ");
    display.println(ph, 1);
    
    // Get pH status
    String phStatus = getStatus(ph, PH_MIN, PH_MAX);
    display.setCursor(80, 10);
    display.print(phStatus);
    
    display.setCursor(0, 20);
    display.print("BG: ");
    display.println(biogas, 1);
    
    // Get biogas status
    String biogasStatus = getStatus(biogas, BIOGAS_MIN, BIOGAS_MAX);
    display.setCursor(80, 20);
    display.print(biogasStatus);
    
    display.setCursor(0, 30);
    display.print("GAS: ");
    display.println(gas_level);
    
    // Get gas status
    String gasStatus = (gas_level < GAS_THRESHOLD) ? "NORMAL" : "HIGH";
    display.setCursor(80, 30);
    display.print(gasStatus);
    
    // Draw horizontal line
    display.drawLine(0, 40, display.width(), 40, SH110X_WHITE);
    
    // Overall system status
    display.setCursor(0, 50);
    display.print("STATUS: ");
    
    // Check if any parameter has HIGH or LOW status
    if (phStatus == "HIGH" || biogasStatus == "HIGH" || gasStatus == "HIGH") {
      display.println("HIGH");
    } else if (phStatus == "LOW" || biogasStatus == "LOW") {
      display.println("LOW");
    } else {
      display.println("NORMAL");
    }
    
    // Always call display() at the end
    display.display();
  }
  
  delay(1000);
}

// Helper function to determine status based on thresholds
String getStatus(float value, float minThreshold, float maxThreshold) {
  if (value < minThreshold) {
    return "LOW";
  } else if (value > maxThreshold) {
    return "HIGH";
  } else {
    return "NORMAL";
  }
}