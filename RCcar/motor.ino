#include <WiFi.h>
#include <WebServer.h>
#include <ESP32Servo.h>

// ========================
// WiFi
// ========================
const char* ssid = "LWK_Network";
const char* password = "LWK888kepong";

// ========================
// TB6612FNG pins
// ========================
#define PWMA 25
#define AIN1 26
#define AIN2 27
#define STBY 14

#define SERVO_PIN 13
Servo steeringServo;

int currentAngle = 90;

// ========================
// PWM settings
// ========================
const int pwmFreq = 1000;
const int pwmResolution = 8;   // 0~255

// ========================
// Global state
// ========================
WebServer server(80);
int currentThrottle = 0;

// ========================
// Motor control
// ========================
void motorStop() {
  ledcWrite(PWMA, 0);
  digitalWrite(AIN1, LOW);
  digitalWrite(AIN2, LOW);
  currentThrottle = 0;
}

void motorForward(int speedValue) {
  if (speedValue < 0) speedValue = 0;
  if (speedValue > 255) speedValue = 255;

  digitalWrite(AIN1, HIGH);
  digitalWrite(AIN2, LOW);
  ledcWrite(PWMA, speedValue);

  currentThrottle = speedValue;
}

void motorReverse(int speedValue) {
  if (speedValue < 0) speedValue = 0;
  if (speedValue > 255) speedValue = 255;

  digitalWrite(AIN1, LOW);
  digitalWrite(AIN2, HIGH);
  ledcWrite(PWMA, speedValue);

  currentThrottle = -speedValue;
}

void setThrottle(int value) {
  if (value > 255) value = 255;
  if (value < -255) value = -255;

  if (value > 0) {
    motorForward(value);
  } else if (value < 0) {
    motorReverse(-value);
  } else {
    motorStop();
  }
}





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

// ========================
// Web handlers
// ========================
void handleRoot() {
  String html = R"rawliteral(
<!DOCTYPE html>
<html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>ESP32 Motor Receiver</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      text-align: center;
      padding: 24px;
      background: #f5f5f5;
    }
    .box {
      max-width: 360px;
      margin: auto;
      background: white;
      border-radius: 12px;
      padding: 20px;
      box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    h2 {
      margin-top: 0;
    }
    .btn {
      display: inline-block;
      margin: 8px;
      padding: 12px 18px;
      border: none;
      border-radius: 10px;
      font-size: 16px;
      background: #007bff;
      color: white;
      cursor: pointer;
    }
    .stop {
      background: #dc3545;
    }
  </style>
</head>
<body>
  <div class="box">
    <h2>ESP32 Motor Receiver</h2>
    <p>Use Raspberry Pi to send /throttle commands</p>
    <button class="btn" onclick="fetch('/throttle?value=180')">Forward 180</button>
    <button class="btn" onclick="fetch('/throttle?value=-180')">Reverse 180</button>
    <button class="btn stop" onclick="fetch('/stop')">STOP</button>
  </div>
</body>
</html>
)rawliteral";

  server.send(200, "text/html", html);
}

void handleThrottle() {
  if (!server.hasArg("value")) {
    server.send(400, "text/plain", "Missing value");
    return;
  }

  int value = server.arg("value").toInt();
  setThrottle(value);

  Serial.print("Throttle set to: ");
  Serial.println(currentThrottle);

  server.send(200, "text/plain", "Throttle set to " + String(currentThrottle));
}

void handleStop() {
  motorStop();
  Serial.println("STOP");

  server.send(200, "text/plain", "STOP");
}

void handleStatus() {
  String json = "{";
  json += "\"throttle\":" + String(currentThrottle);
  json += "}";

  server.send(200, "application/json", json);
}

// ========================
// Setup
// ========================
void setup() {
  Serial.begin(115200);
  Serial.println();
  Serial.println("ESP32 Motor Receiver starting...");

  steeringServo.setPeriodHertz(50);
  steeringServo.attach(SERVO_PIN, 500, 2400);
  steeringServo.write(90);


  pinMode(AIN1, OUTPUT);
  pinMode(AIN2, OUTPUT);
  pinMode(STBY, OUTPUT);

  digitalWrite(STBY, HIGH);

  ledcAttach(PWMA, pwmFreq, pwmResolution);

  motorStop();

  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println();
  Serial.println("WiFi connected");
  Serial.print("ESP32 IP address: ");
  Serial.println(WiFi.localIP());

  server.on("/", handleRoot);
  server.on("/throttle", handleThrottle);
  server.on("/stop", handleStop);

  server.on("/", handleRoot);
  server.on("/steer", handleSteer);

  server.on("/status", handleStatus);

  server.begin();
  Serial.println("Web server started");
}

// ========================
// Loop
// ========================
void loop() {
  server.handleClient();
}