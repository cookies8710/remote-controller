#include <IRremote.h>

#define STATUS_PIN 8
const int RECV_PIN = 7;
IRrecv irrecv(RECV_PIN);
decode_results results;


void setup() {
   Serial.begin(9600);
   Serial.println("starting");
   //pinMode(2, INPUT_PULLUP);
   pinMode(STATUS_PIN, OUTPUT);
   pinMode(4, INPUT_PULLUP);

  irrecv.enableIRIn();
  irrecv.blink13(true);
}

boolean off = true;
boolean exitsent = false;

void understood()
{
   digitalWrite(STATUS_PIN, HIGH);
   delay(450);
   digitalWrite(STATUS_PIN, LOW);
}

void not_understood()
{
   digitalWrite(STATUS_PIN, HIGH);
   delay(150);
   digitalWrite(STATUS_PIN, LOW);
   delay(150);
   digitalWrite(STATUS_PIN, HIGH);
   delay(150);
   digitalWrite(STATUS_PIN, LOW);
}

void loop() {
  if (!exitsent && digitalRead(4)==LOW)
  {
    exitsent = true;
    Serial.println("exit");
  
  }
  delay(100);
  if (irrecv.decode(&results)){
	Serial.println(results.value, HEX);
	understood();
        irrecv.resume();
    /*switch (results.value)
    {
	case 0x8e71f609:
		Serial.println("volup");
		understood();
		break;
	case 0x8e710ef1:
		Serial.println("voldown");
		understood();
		break;
	case 0x8e7106f9:
		Serial.println("play");
		understood();
		break;
	case 0x8e7116e9:
		Serial.println("pause");
		understood();
		break;
	case 0x8e7146b9:
		Serial.println("forward");
		understood();
		break;
	case 0x8E71C639:
		Serial.println("backward");
		understood();
		break;
	default:
		break;
      }*/
  }

}

/*


void setup(){
  Serial.begin(9600);
  irrecv.enableIRIn();
  irrecv.blink13(true);
}

void loop(){
  if (irrecv.decode(&results)){
        Serial.println(results.value, HEX);
        irrecv.resume();
  }
}



*/
