const int sensorPin = A0;
const float upperThreshold = 4.0; // Set the initial higher threshold (formerly lower)
const float lowerThreshold = 1.5; // Set the final lower threshold (formerly upper)
unsigned long lastPulseTime = 0;
bool awaitingFirstThreshold = true;
bool awaitingSecondThreshold = false;
bool awaitingPeak = false;
bool awaitingLowerDescend = false;
float troughValue = 5.0;
unsigned long troughTime = 0;

void setup() {
  Serial.begin(9600);
  pinMode(sensorPin, INPUT);
}

void loop() {
  float voltage = analogRead(sensorPin) * (5.0 / 1023.0); // Convert the analog reading to voltage
  unsigned long currentTime = millis();

  if (awaitingFirstThreshold) {
    if (voltage < upperThreshold) {
      awaitingFirstThreshold = false;
      awaitingSecondThreshold = true;
    }
  } else if (awaitingSecondThreshold) {
    if (voltage < lowerThreshold) {
      awaitingSecondThreshold = false;
      awaitingPeak = true;
      troughValue = voltage;
      troughTime = currentTime;
    }
  } else if (awaitingPeak) {
    if (voltage < troughValue) {
      troughValue = voltage;
      troughTime = currentTime;
    }
    if (voltage > lowerThreshold) {
      awaitingLowerDescend = true;
      awaitingPeak = false;
    }
  } else if (awaitingLowerDescend) {
    if (voltage > upperThreshold) {
      // Log the trough when it ascends above the upper threshold
      unsigned long timeSinceLastPulse = currentTime - lastPulseTime;
      Serial.print(troughTime); Serial.print(" ms ");
      Serial.print(int(troughValue * 1000)); Serial.print(" mV ");
      Serial.print(timeSinceLastPulse); Serial.println(" ms");
      
      lastPulseTime = currentTime;
      troughValue = 5.0;
      awaitingFirstThreshold = true;
      awaitingLowerDescend = false;
    }
  }
}
