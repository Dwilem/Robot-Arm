#include <ESP32Servo.h>

Servo myServo;

char buffer[8];
uint8_t bufIndex = 0;

void setup() {
  Serial.begin(115200);
  delay(2000);
  Serial.println("Enter angle 0‑180:");

  myServo.setPeriodHertz(50);    // Standard servo
  myServo.attach(8);             // Safe pin (not GPIO0)
}

void loop() {
  while (Serial.available()) {
    char c = Serial.read();

    if (c == '\n' || c == '\r') {
      buffer[bufIndex] = '\0';
      int angle = atoi(buffer);

      if (angle >= 0 && angle <= 180) {
        myServo.write(angle);
        Serial.print("Moved to: ");
        Serial.println(angle);
      } else {
        Serial.println("Invalid angle!");
      }

      bufIndex = 0;
    }
    else if (isDigit(c) && bufIndex < sizeof(buffer) - 1) {
      buffer[bufIndex++] = c;
    }
  }
}
