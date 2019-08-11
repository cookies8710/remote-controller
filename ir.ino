#include <IRremote.h>

const int RECV_PIN = 7;
IRrecv irrecv(RECV_PIN);
decode_results results;


void setup() {
   Serial.begin(9600);
   Serial.println("starting");
   pinMode(2, INPUT_PULLUP);
   pinMode(4, INPUT_PULLUP);

  irrecv.enableIRIn();
  irrecv.blink13(true);
}

boolean off = true;
boolean exitsent = false;

void loop() {
  int r = digitalRead(2);

  if ((r == HIGH) != off)
  {
     off = r==HIGH;
     Serial.println(off?"pause":"play");  
  }

  if (!exitsent && digitalRead(4)==LOW)
  {
    exitsent = true;
    Serial.println("exit");
  
  }
  delay(100);
  if (irrecv.decode(&results)){
    switch (results.value)
    {
	case 0x8e71f609:
		Serial.println("volup");
		break;
	case 0x8e710ef1:
		Serial.println("voldown");
		break;
	case 0x8e7106f9:
		Serial.println("play");
		break;
	case 0x8e7116e9:
		Serial.println("pause");
		break;
	case 0x8e7146b9:
		Serial.println("forward");
		break;
	case 0x8E71C639:
		Serial.println("backward");
		break;
	default:
		Serial.println(results.value, HEX);
		break;
      }
        irrecv.resume();
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
