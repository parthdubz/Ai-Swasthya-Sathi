#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>

// ---------- OLED SETUP ----------
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET    -1
#define SCREEN_ADDRESS 0x3C
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// ---------- PINS ----------
#define BUZZER_PIN 14   // D5
#define GREEN_LED  12   // D6
#define RED_LED    13   // D7

// ---------- SERIAL ----------
String inputString = "";

// ---------- BLINK CONFIG ----------
unsigned long lastBlinkTime = 0;
bool eyesOpen = true;
const int blinkInterval = 500;
bool blinkEnabled = true;  // controls eye blinking

// ---------- WIFI ----------
const char* ssid = "ESP8266_Hotspot";
const char* password = "12345678";
IPAddress local_IP(192,168,4,1);
IPAddress gateway(192,168,4,1);
IPAddress subnet(255,255,255,0);

// ---------- WEB SERVER ----------
ESP8266WebServer server(80);
String currentState = "NORMAL";

// ---------- TIMING ----------
bool alertActive = false;       // 1-min alert
unsigned long alertStartTime = 0;
bool buzzerActive = false;      // 5-sec buzzer
unsigned long buzzerStartTime = 0;
bool oledUpdated = false;       // tracks OLED update during buzzer

// ---------- FUNCTIONS ----------
void setupWiFi() {
  WiFi.softAP(ssid, password);
  WiFi.softAPConfig(local_IP, gateway, subnet);
}

void handleStatus() {
  server.send(200, "text/plain", currentState);
}

void setupServer() {
  server.on("/status", handleStatus);
  server.begin();
}

// Draw eyes on OLED
void drawEyes(bool open) {
  display.clearDisplay();
  if(open) {
    // Open eyes
    display.fillRect(20,20,20,20,SSD1306_WHITE);
    display.fillRect(70,20,20,20,SSD1306_WHITE);
    // Pupils
    display.fillRect(26,26,8,8,SSD1306_BLACK);
    display.fillRect(76,26,8,8,SSD1306_BLACK);
  } else {
    // Closed eyes
    display.drawLine(20,30,40,30,SSD1306_WHITE);
    display.drawLine(70,30,90,30,SSD1306_WHITE);
  }
  display.display();
}

// Draw ALERT on OLED
void drawAlertOLED() {
  display.clearDisplay();
  display.setTextSize(2);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(20,25);
  display.println("ALERT!");
  display.display();
}

// ---------- SETUP ----------
void setup() {
  Serial.begin(115200);

  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(GREEN_LED, OUTPUT);
  pinMode(RED_LED, OUTPUT);

  digitalWrite(BUZZER_PIN, LOW);
  digitalWrite(GREEN_LED, HIGH);
  digitalWrite(RED_LED, LOW);

  if (!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) while(true);
  display.clearDisplay();
  drawEyes(eyesOpen);

  inputString.reserve(50);
  Serial.println("ESP8266 ALERT SYSTEM READY");

  setupWiFi();
  setupServer();
}

// ---------- PROCESS SERIAL COMMAND ----------
void processCommand(String cmd) {
  cmd.trim();
  if(cmd=="ALERT") {
    alertActive = true;
    alertStartTime = millis();
    currentState = "EMERGENCY";

    // Start buzzer + red LED for 5 sec
    buzzerActive = true;
    buzzerStartTime = millis();
    digitalWrite(BUZZER_PIN,HIGH);
    digitalWrite(RED_LED,HIGH);
    digitalWrite(GREEN_LED,LOW);

    // OLED ALERT during buzzer
    drawAlertOLED();
    oledUpdated = true;

    // temporarily disable blinking during buzzer
    blinkEnabled = false;
  } else if(cmd=="NORMAL") {
    if(!alertActive){ // Only reset if no 1-min alert
      currentState = "NORMAL";
      digitalWrite(GREEN_LED,HIGH);
      digitalWrite(RED_LED,LOW);
      digitalWrite(BUZZER_PIN,LOW);
      blinkEnabled = true;
      oledUpdated = false;
    }
  }
}

// ---------- LOOP ----------
void loop() {
  // ---- SERIAL INPUT ----
  while(Serial.available()){
    char inChar = (char)Serial.read();
    if(inChar=='\n'){
      processCommand(inputString);
      inputString="";
    } else inputString += inChar;
  }

  // ---- BUZZER TIMER 5 SEC ----
  if(buzzerActive && millis()-buzzerStartTime>=5000){
    buzzerActive=false;
    digitalWrite(BUZZER_PIN,LOW);
    digitalWrite(RED_LED,LOW);
    digitalWrite(GREEN_LED,HIGH);

    // Enable blinking eyes after buzzer ends
    blinkEnabled = true;
    lastBlinkTime = millis();
    oledUpdated = false; // allow redraw
  }

  // ---- ALERT TIMER 1 MIN ----
  if(alertActive && millis()-alertStartTime>=60000){
    alertActive=false;
    currentState="NORMAL";
    blinkEnabled = true;
    lastBlinkTime = millis();
    oledUpdated = false;
  }

  // ---- BLINK EYES ----
  if(blinkEnabled && millis()-lastBlinkTime>blinkInterval){
    eyesOpen = !eyesOpen;
    drawEyes(eyesOpen);
    lastBlinkTime = millis();
  }

  // ---- OLED ALERT DISPLAY ----
  if(buzzerActive && !oledUpdated){
    drawAlertOLED();
    oledUpdated = true;
  }

  if(!buzzerActive) oledUpdated = false;

  // ---- WEB SERVER ----
  server.handleClient();
}
