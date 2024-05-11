// Parameters
const int upperThreshold = 818; // 4.0V
const int lowerThreshold = 307; // 1.5V

// Pins
const int sensorPin = 14; // A0

// Variable Declaration
int peakValue = 1023;
volatile int geigerVoltage = 0;

bool awaitingFirstThreshold = true;
bool awaitingSecondThreshold = false;
bool awaitingPeak = false;
bool awaitingLowerDescend = false;

unsigned long lastPulseTime = 0;
unsigned long peakTime = 0;
unsigned long timeSinceLastPulse = 0;
volatile unsigned long currentTime = 0;


void setup() {
  Serial.begin(9600);
  pinMode(sensorPin, INPUT);
}

void loop() {
  currentTime = millis();
  geigerVoltage = analogRead(sensorPin);

  if (awaitingFirstThreshold) {
    if (geigerVoltage < upperThreshold) {
      awaitingFirstThreshold = false;
      awaitingSecondThreshold = true;
    }
  } else if (awaitingSecondThreshold) {
    if (geigerVoltage < lowerThreshold) {
      awaitingSecondThreshold = false;
      awaitingPeak = true;
      peakValue = geigerVoltage;
      peakTime = currentTime;
    }
  } else if (awaitingPeak) {
    if (geigerVoltage < peakValue) {
      peakValue = geigerVoltage;
      peakTime = currentTime;
    }
    if (geigerVoltage > lowerThreshold) {
      awaitingLowerDescend = true;
      awaitingPeak = false;
    }
  } else if (awaitingLowerDescend) {
    if (geigerVoltage > upperThreshold) {
      timeSinceLastPulse = peakTime - lastPulseTime;
      peakValue = int(peakValue * 5000 / 1023);
      
      // Print Output
      // Peak Value (mV); Peak Timestamp (ms); Time since last Peak (ms); 
      Serial.print(peakValue); Serial.print(" ");
      Serial.print(peakTime); Serial.print(" ");
      Serial.println(timeSinceLastPulse);
      
      peakValue = 1023;
      lastPulseTime = currentTime;
      awaitingFirstThreshold = true;
      awaitingLowerDescend = false;
    }
  }
}
