# fan
Python Script for controlling a small server room fan and A/C using a Raspberry Pi.

This script is called as a daemon from fan.sh which goes in /etc/init.d

The script has two main features and two optional features.
The two main features is it controls a fan via PWM and it can also turn on and off an air conditioner. 

The two optional parts is it can also update an Adafruit 7 segment display with the temp, mode, time
It can also be polled using something like Cacti so you can see how it does over time.

You will need to create several circuits which I'll describe briefly here.

You will need 2 Dallas 1-wire sensors, one for in the room and one for outside the building.
Another 2N2222 transistor will control the PWM to the fan - 0 to 10 volts.
And one more 2N2222 + IR LED will control the air conditioner. 

Here is a great fan by Fantech PrioAir http://a.co/fvUypiw which uses a PWM signal for speed.

The IR commands uses LIRC for sending the IR signals.  You'll have to install that part to use it.

Again, I'll see if I can provide some schematics.  The script should show what pins are used for what.

Update:  I believe this is the circuit used for the PWM control.  The code indicates which pin on the Pi to use. 
You'll also need to connect a pin to the Lirc IR LED via a 2N2222.

![title](https://github.com/ntsecrets/fan/blob/master/transistor-circuit.png)
