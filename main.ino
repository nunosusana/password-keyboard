// This sketch configures the Raspberry Pi Pico as a USB HID (Human Interface Device) keyboard
// and sends a username, followed by a tab, and then a password, followed by an enter when connected to a computer.

// Include the Keyboard library for USB HID functionality.
// This library is part of the Arduino core for RP2040 boards.
#include "Keyboard.h"

const char* usernameToSend = "{{USERNAME}}";
const char* passwordToSend = "{{PASSWORD}}";

// A flag to ensure the sequence is sent only once after boot.
bool sentCredentials = false;

void setup() {
  // Start the USB keyboard communication.
  // This tells the computer that the Pico is a keyboard.
  Keyboard.begin();

  // Give the computer a moment to recognize the USB device.
  // A small delay helps ensure the HID device is fully enumerated.
  delay(1000); // Delay for 1 second (1000 milliseconds)
}

void loop() {
  // Check if the credentials have already been sent.
  // This prevents them from being sent repeatedly in the loop.
  if (!sentCredentials) {
    // Send the username
    for (int i = 0; i < strlen(usernameToSend); i++) {
      char charToSend = usernameToSend[i];
      Keyboard.print(charToSend);
      delay(50); // Small delay between key presses
    }

    //Serial.println("Sending Tab key.");
    // Send the Tab key
    Keyboard.press(KEY_TAB); // KEY_TAB is the keycode for the Tab key
    delay(25);
    Keyboard.releaseAll(); // Release the Tab key

    // Send the password
    for (int i = 0; i < strlen(passwordToSend); i++) {
      char charToSend = passwordToSend[i];
      Keyboard.print(charToSend);
      delay(50); // Small delay between key presses
    }

    Keyboard.press(KEY_RETURN); // KEY_RETURN is the keycode for Enter
    delay(25); // Small delay for the Enter keypress
    Keyboard.releaseAll(); // Release all pressed keys

    // Set the flag to true so the sequence isn't sent again until reset.
    sentCredentials = true;
  }

  // The loop will continue to run, but no more keystrokes will be sent
  // unless the Pico is reset or power-cycled.
  // You could add other functionality here, like waiting for a button press.
  delay(100); // A small delay to prevent the loop from running too fast
}
