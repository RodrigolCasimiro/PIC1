// Define pin connections
const int geigerPin = A0; // Geiger counter connected to A0
const int ledPin = 13;    // Built-in LED pin

// Initialize variables
unsigned long lastPulseTime = 0; // Time of the last detected pulse
unsigned long startTime;         // Start time of the program for time passed calculation

// Parameters
const long debounceTime = 10;    // Debounce time in milliseconds to prevent false triggers
const long threshold    = 2500;   // Threshold in Volts

void setup() {
  Serial.begin(9600);            // Start serial communication at 9600 baud
  pinMode(geigerPin, INPUT);     // Set the Geiger counter pin as input
  pinMode(ledPin, OUTPUT);       // Set the LED pin as output
  delay(3000);
}

void loop() {
  int geigerValue = analogRead(geigerPin); // Read the value from the Geiger counter
  int voltage = geigerValue * (5000 / 1023); // Convert the reading to voltage
  unsigned long currentTime = millis(); // Get the current time
  
  // Check if a pulse is detected considering the debounce time
  if (voltage < threshold && currentTime - lastPulseTime > debounceTime) {
    delay(debounceTime - 2);    // Short delay to visibly indicate the pulse detection
    
    // Calculate time passed since the start and since the last pulse
    unsigned long timePassed = currentTime - startTime;
    unsigned long timeSinceLastPulse = (lastPulseTime > 0) ? currentTime - lastPulseTime : 0;
    
    // Print the calculated times and total pulse count
    Serial.print(voltage);
    Serial.print(" ");
    Serial.print(timePassed);
    Serial.print(" ");
    Serial.println(timeSinceLastPulse);
    
    lastPulseTime = currentTime; // Update the last pulse time
  }
}
