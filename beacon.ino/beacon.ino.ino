/*
   Based on Neil Kolban example for IDF: https://github.com/nkolban/esp32-snippets/blob/master/cpp_utils/tests/BLE%20Tests/SampleScan.cpp
   Ported to Arduino ESP32 by Evandro Copercini
   Changed to a beacon scanner to report iBeacon, EddystoneURL and EddystoneTLM beacons by beegee-tokyo
*/

#include <Arduino.h>

#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEScan.h>
#include <BLEAdvertisedDevice.h>
#include <BLEBeacon.h>

#include <WiFi.h>
#include <HTTPClient.h>

int scanTime = 5; //In seconds
BLEScan *pBLEScan;

const char* ssid = "secret_ssid";
const char* password = "secret_password";

//Your Domain name with URL path or IP address with path
const char* serverName = "http://192.168.0.16:8000";

unsigned long lastTime = 0;
unsigned long timerDelay = 5000;

class MyAdvertisedDeviceCallbacks : public BLEAdvertisedDeviceCallbacks
{
    void onResult(BLEAdvertisedDevice advertisedDevice)
    {

      if (advertisedDevice.haveServiceUUID())
      {
        BLEUUID devUUID = advertisedDevice.getServiceUUID();
        Serial.print("Found ServiceUUID: ");
        Serial.println(devUUID.toString().c_str());
        Serial.println("");
      }
      
    }
};

void setup()
{
  Serial.begin(115200);
  Serial.println("Scanning...");

  pinMode(LED_BUILTIN, OUTPUT);

  BLEDevice::init("");
  pBLEScan = BLEDevice::getScan(); //create new scan
  pBLEScan->setAdvertisedDeviceCallbacks(new MyAdvertisedDeviceCallbacks());
  pBLEScan->setActiveScan(true); //active scan uses more power, but get results faster
  pBLEScan->setInterval(100);
  pBLEScan->setWindow(99); // less or equal setInterval value

  WiFi.begin(ssid, password);
  Serial.println("Connecting to WiFi");
  while(WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.print("Connected to WiFi network with IP Address: ");
  Serial.println(WiFi.localIP());
 
  Serial.println("Timer set to 5 seconds (timerDelay variable), it will take 5 seconds before publishing the first reading.");
}

void loop()
{
  if ((millis() - lastTime) > timerDelay) {
    //Check WiFi connection status
    if(WiFi.status()== WL_CONNECTED){
      digitalWrite(LED_BUILTIN, 128);
      WiFiClient client;
      
      
      // Specify content-type header
      BLEScanResults foundDevices = pBLEScan->start(scanTime, false);
      for (int i = 0; i < foundDevices.getCount(); i++)
      {
        BLEAdvertisedDevice dev = foundDevices.getDevice(i);
        for (int j = 0; j < dev.getServiceUUIDCount(); j++)
        {
          HTTPClient http;
          http.begin(client, serverName);

          BLEUUID uuid = dev.getServiceUUID(j);
          http.addHeader("Content-Type", "application/x-www-form-urlencoded");
          // Data to send with HTTP POST
          String httpRequestData = (std::string{"espid=0001&uuid="} + uuid.toString()).c_str();
          // Send HTTP POST request
          int httpResponseCode = http.POST(httpRequestData);
        
          Serial.print("HTTP Response code: ");
          Serial.println(httpResponseCode);

          if (httpResponseCode != -1)
          {
            digitalWrite(LED_BUILTIN, LOW);
          }
            
          // Free resources
          http.end();
        }
      }
      Serial.println("Scan done!");
      pBLEScan->clearResults(); // delete results fromBLEScan buffer to release memory
      
    }
    else {
      Serial.println("WiFi Disconnected");
    }
    lastTime = millis();
  }
}
