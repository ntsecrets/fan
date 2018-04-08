# fan
This is a Python Script for controlling a small server room fan and A/C using a Raspberry Pi.  The fan's speed will adujust depending on the how much air needs to be sucked out or blown in to maintain the target temperature.  That way the fan isn't cycling on and off, its running at a rather stable speed.  

In my situation, the space the air is being blown into can get hot.  So if the outside and inside temps are higher than a threshold, it will shut the fan off and turn on the air conditioner. 

Below are the settings you'll need to update in fan.py, most importantly the IDFtempSensor and OutsideSensor w1 address. 

```python
# ~*~**~*~*~*~* settings *~*~*~*~*~*~*~

# Fan duty cycle storage area
fanStats = '/home/pi/fanstats.txt'
acMode = '/home/pi/acmode.txt'
esMode = '/home/pi/esmode.txt'
      
IDFtempSensor = "28-00000544c340"
OutsideSensor = "28-00000546550F"

Frequency = 60 # seconds
TargetTemp = 73.0
dutycycle = 80 # initial duty cycle on startup
OutsideThresh = 64.0

```


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

Update:  I believe this is the circuit used for the PWM control.  The code indicates which pin on the Pi to use.  Note that the VCC is connected to the 10v supplied from the fan itself, not from the pi.  The 1k resistor and 10k resistor values might be different, I need to check on that.  You may have to tinker a bit with that.

You'll also need to connect a pin to the Lirc IR LED via a 2N2222.

![title](https://github.com/ntsecrets/fan/blob/master/transistor-circuit.png)

For the Lirc setup, see http://www.raspberry-pi-geek.com/Archive/2015/10/Raspberry-Pi-IR-remote
For the Dallas 1 Wire setup, see https://thepihut.com/blogs/raspberry-pi-tutorials/18095732-sensors-temperature-with-the-1-wire-interface-and-the-ds18b20
