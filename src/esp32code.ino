

/*~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~*/
/*

*/
/*~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~*/


#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <SPI.h>
#include <WiFi.h>
#include <PubSubClient.h>

#include "sound.h"
#include "XT_DAC_Audio.h"

XT_Wav_Class gaxe(GOLDEN_AXE);          
XT_DAC_Audio_Class DacAudio(25,0);   

const char* mqtt_server = "SERVER  IP";
typedef enum {STATE_SET,STATE_NOTSET,STATE_ON,STATE_OFF,ERR}ALARM_STATE;
WiFiClient espClient;
PubSubClient mqtt_client(espClient);

const char* ssid = "WIFI SSID";
const char* password = "WIFI PASS";
#define SCREEN_WIDTH 128 // OLED display width, in pixels
#define SCREEN_HEIGHT 64 // OLED display height, in pixels

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

bool alarm_on = 0;

void play_alarm(){
  int k = 0;
  while(alarm_on){
    k++;
    if (!(k%10000))
      Serial.println(k);
  DacAudio.FillBuffer();                
  if(gaxe.Playing==false)       
    DacAudio.Play(&gaxe);       
  mqtt_client.loop(); // This is essential for the ability to respond to a callback while handeling previous one.
  }  
  
}
void set_display(ALARM_STATE state){
  display.clearDisplay();
  display.setTextSize(3);
  display.setTextColor(WHITE);
  display.setCursor(0, 10);
  // Display static text
  switch (state){
    
    case STATE_ON:
      display.println(" WALK\n  UP!");
      break;
    case STATE_OFF:
      display.println(" ALARM\nNOT SET");
      break;
    case STATE_SET:
      display.println(" ALARM\n  SET");
      break;
    case STATE_NOTSET:
      display.println(" ALARM\nNOT SET");
      break;
    case ERR:
      display.println("ERROR");
      break;
  }
    display.display();
}


void reconnect() {
  // Loop until we're reconnected
  while (!mqtt_client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Attempt to connect
    if (mqtt_client.connect("ESP32")) {
      Serial.println("connected");
      // Subscribe
      mqtt_client.subscribe("pi_to_esp");
    } else {
      Serial.print("failed, rc=");
      Serial.print(mqtt_client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}
void callback(char* topic, byte* message, unsigned int length) {
//  Serial.print("Message arrived on topic: ");
//  Serial.print(topic);
//  Serial.print(". Message: ");
  String signal;
  
  for (int i = 0; i < length; i++) {
//    Serial.print((char)message[i]);
    signal += (char)message[i];
  }

    if (String("alarm_on") == signal){
      set_display(STATE_ON);
      /*PLAY MUSIC UNTIL ALARM OFF*/
      alarm_on = 1;
      play_alarm();
    }
    else if (String("alarm_off") == signal){
      set_display(STATE_OFF);
      alarm_on = 0;    
    }
    else if (String("alarm_set") == signal){
      set_display(STATE_SET);
    }
    else if (String("alarm_notset") == signal){
      set_display(STATE_NOTSET);
    }
    else {
      set_display(ERR);
      /*This on is here for debugging. 
      Only one of the above four messages should be mqtt-sent over pi_to_esp*/
    }
}

void setup_wifi() {
  delay(10);
  // We start by connecting to a WiFi network
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void setup() {

  /*sound */
  gaxe.Speed = 2;
  
  /*MQTT and WiFi*/
  setup_wifi();
  mqtt_client.setServer(mqtt_server, 1883);
  mqtt_client.setCallback(callback);
  
  Serial.begin(115200);
  /*OLED*/
  if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) { 
    Serial.println(F("SSD1306 allocation failed"));
    for(;;);
  }
  
  delay(2000);
  set_display(STATE_NOTSET);
}

void loop() {
  if (!mqtt_client.connected()) {
    reconnect();
  }
  Serial.print("loop");
  Serial.println();
  mqtt_client.loop(); // polling to the mqtt "buffer"
}
