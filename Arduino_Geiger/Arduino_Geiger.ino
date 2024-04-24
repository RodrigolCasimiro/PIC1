// Parameters
const int threshold_mV = 2500; // mV
const int debounceTime = 10; // ms

// Define pin connections
const int geigerPin = 14; // A0

// Initialize variables
unsigned long lastPulseTime = 0; // Time of the last detected pulse
unsigned long lastTime = 0;
unsigned long timeOffset = 0;
unsigned long currentTime = 0;
unsigned long correctedTime = 0;
volatile int det = 0;
volatile unsigned long timeDet = 0;
int threshold;
int geigerValue = 0;
String output = "";

void setup() {
  Serial.begin(9600);
  pinMode(geigerPin, INPUT);

  threshold = int(threshold_mV * 1024 / 5000); // bins

  delay(3000); // Delay to start .py code
}

void loop() {
  currentTime = micros();

  // Check for micros() overflow
  if (currentTime < lastTime) {
    timeOffset += 4294967295;  // 2^32 - 1
  }

  lastTime = currentTime;
  correctedTime = currentTime + timeOffset;

  int geigerValue = analogRead(geigerPin);

  // Check if a pulse is detected considering the debounce time
  if (geigerValue > threshold) {
    // Check if this pulse is within the coincidence window and after the debounce time
    if (correctedTime - lastPulseTime > debounceTime * 1000) {
      output = String(geigerValue * 5000 / 1024); //mv
      output += " " + String(correctedTime); // µs
      output += " " + String(correctedTime - lastPulseTime); // µs

      Serial.println(output); // µs

      lastPulseTime = correctedTime; // Update the last pulse time
    }
  }
  delayMicroseconds(1);
}
