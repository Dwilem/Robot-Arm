#include <WiFi.h>
#include <WebSocketsClient.h>
#include <ArduinoJson.h>
#include <ESP32Servo.h>

// Wi-Fi
const char* ssid     = "***"; // CHANGE HERE
const char* password = "***"; // CHANGE HERE


// Server
const char* serverIP = "192.168.0.101";
const int serverPort = 8765;

// Servos
Servo Base, Shoulder, Elbow, WristX, WristY;

// Target angles
int targetBase = 90;
int targetShoulder = 90;
int targetElbow = 90;
int targetWristX = 90;
int targetWristY = 90;

// Speed (degrees per update)
int moveSpeed = 2;

WebSocketsClient webSocket;

// Smooth move function
int moveTowards(int current, int target, int step) {
  if (current < target) return min(current + step, target);
  if (current > target) return max(current - step, target);
  return current;
}

void webSocketEvent(WStype_t type, uint8_t * payload, size_t length) {
    switch(type) {
    case WStype_DISCONNECTED:
      Serial.println("[WebSocket] Disconnected");
      break;
    case WStype_CONNECTED:
      Serial.println("[WebSocket] Connected to server");
      break;
    case WStype_TEXT:
    {
      Serial.print("[WebSocket] Received: ");
      Serial.println((char*)payload);
      StaticJsonDocument<200> doc;
      if (deserializeJson(doc, payload) == DeserializationError::Ok) {
        targetBase = doc["Base"];
        targetShoulder = doc["Shoulder"];
        targetElbow = doc["Elbow"];
        targetWristX = doc["WristX"];
        targetWristY = doc["WristY"];
        moveSpeed = doc["Speed"];
      
      }
    }
  }
}

void setup() {
  Serial.begin(115200);

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(300);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected");

  // Attach servos to pins
  Base.attach(14);
  Shoulder.attach(13);
  Elbow.attach(12);
  WristX.attach(11);
  WristY.attach(10);

  // Initial positions
  Base.write(90);
  Shoulder.write(90);
  Elbow.write(90);
  WristX.write(90);
  WristY.write(90);

  webSocket.begin(serverIP, serverPort, "/");
  webSocket.onEvent(webSocketEvent);
  webSocket.setReconnectInterval(2000);
}

void loop() {
  webSocket.loop();

  // Gradually move servos toward targets
  Base.write(moveTowards(Base.read(), targetBase, moveSpeed));
  Shoulder.write(moveTowards(Shoulder.read(), targetShoulder, moveSpeed));
  Elbow.write(moveTowards(Elbow.read(), targetElbow, moveSpeed));
  WristX.write(moveTowards(WristX.read(), targetWristX, moveSpeed));
  WristY.write(moveTowards(WristY.read(), targetWristY, moveSpeed));

  delay(20); // ~50 updates per second
}
