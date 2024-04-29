#include <WiFi.h>
#include <L298N.h> // Make sure this library supports controlling multiple motors

const char* ssid = "Amatrasuu";     // Replace with your WiFi SSID
const char* password = "22222222";  // Replace with your WiFi password

WiFiServer wifiServer(12345); // The port number should match the Python script

// PID constants
float Kp = 2.5;
float Ki = 0.0;
float Kd = 0.0;

// PID variables
float previous_error = 0;
float integral = 0;
float setpoint = 45; // Desired orientation

// Motor A pins
const int enA = 33;
const int in1 = 25;
const int in2 = 26;

// Motor B pins
const int enB = 12;
const int in3 = 27;
const int in4 = 14;

// Initialize L298N library instances for both motors
L298N motorA(enA, in2,in1);
L298N motorB(enB, in4,in3 );

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }

  wifiServer.begin();
  Serial.println("Server started");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
  motorA.setSpeed(100);
  motorB.setSpeed(100);
  motorA.forward();
  motorB.forward();
  delay(500);
  motorA.stop();
  motorB.stop();
}

void loop() {
  WiFiClient client = wifiServer.available();
  if (client) {
    Serial.println("Client connected");
    while (client.connected()) {
      String line = client.readStringUntil('\n');
      if (line.startsWith("STOP")) {
        motorA.stop(); // Stop Motor A
        motorB.stop(); // Stop Motor B
        Serial.println("Stopping motors");
        client.println("Motors stopped");
        client.stop();
        Serial.println("Client disconnected");
        break; // Exit the loop
      }
      else if (line.startsWith("Current:")) {
        int separator = line.indexOf(',');
        float current_orientation = line.substring(9, separator).toFloat();
        float ideal_orientation = line.substring(separator + 7).toFloat();
        
        // Calculate error based on current and ideal orientations
        float error = ideal_orientation - current_orientation;

        // PID calculations
        integral += error;
        float derivative = error - previous_error;
        float output = Kp * error + Ki * integral + Kd * derivative;
        previous_error = error;
        if (output < 20){
            output = 50;
        }

        // Convert PID output to motor speed
        int speedA = constrain(abs(output), 0, 150); // Ensure speed is within PWM range
        int speedB = constrain(abs(output), 0, 150); // Mirror speed for Motor B

        // Adjust directions based on output
        if (output > 0) {
          motorA.setSpeed(speedA);
          motorA.forward();
          motorB.setSpeed(speedB);
          motorB.forward();
        } else {
          motorA.setSpeed(speedA);
          motorA.backward();
          motorB.setSpeed(speedB);
          motorB.backward();
        }

        Serial.print("PID Output: ");
        Serial.println(output);

        client.println("PID applied");
      }
      
      // Additional client.stop() here could prematurely end the connection; consider your application's needs
    }

  }
}