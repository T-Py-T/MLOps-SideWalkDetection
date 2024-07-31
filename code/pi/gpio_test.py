import RPi.GPIO as GPIO
import time

# define GPIO 
ledBlue = 22 
ledGreen = 27 
horn = 23
blinkL = 17
blinkR = 18
pushIn = 25
pushOut = 19

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM) # Use physical pin numbering
GPIO.setup(ledGreen, GPIO.OUT, initial=GPIO.LOW) 
GPIO.setup(ledBlue, GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(blinkL, GPIO.IN,GPIO.PUD_DOWN) 
GPIO.setup(blinkR, GPIO.IN,GPIO.PUD_DOWN) 
GPIO.setup(horn, GPIO.IN,GPIO.PUD_DOWN)
GPIO.setup(pushOut, GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(pushIn, GPIO.IN, GPIO.PUD_DOWN)


leds = 0
while True:
	horn_in = GPIO.input(horn)
	blinkL_in = GPIO.input(blinkL)
	blinkR_in = GPIO.input(blinkR)
	pushIn_in = GPIO.input(pushIn)

	print(horn_in, blinkL_in, blinkR_in, pushIn_in)
	GPIO.output(ledGreen, leds & 1)
	GPIO.output(ledBlue, (leds & 2) // 2 )
	time.sleep(0.5)
	leds += 1

