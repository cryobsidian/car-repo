#include <WiFi.h>
#include <WebServer.h>
#include <ESP32Servo.h>

// WiFi
const char* ssid = "LWK_Network";
const char* password = "LWK888kepong";

// Servo
#define SERVO_PIN 13
Servo steeringServo;

int currentAngle = 90;

WebServer server(80);

// ===== 转向控制 =====
void handleSteer() {
  if (server.hasArg("value")) {
    int angle = server.arg("value").toInt();

    if (angle < 60) angle = 60;
    if (angle > 120) angle = 120;

    steeringServo.write(angle);
    currentAngle = angle;

    Serial.println(angle);
    server.send(200, "text/plain", "OK");
  } else {
    server.send(400, "text/plain", "No value");
  }
}

void handleRoot() {
  server.send(200, "text/plain", "ESP32 Steering OK");
}

void setup() {
  Serial.begin(115200);

  steeringServo.setPeriodHertz(50);
  steeringServo.attach(SERVO_PIN, 500, 2400);
  steeringServo.write(90);

  WiFi.begin(ssid, password);
  Serial.print("Connecting...");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println();
  Serial.println(WiFi.localIP());

  server.on("/", handleRoot);
  server.on("/steer", handleSteer);

  server.begin();
}

void loop() {
  server.handleClient();
}