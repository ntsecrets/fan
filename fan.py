#!/usr/bin/env python
# Version 1.0.1
import logging
import logging.handlers
import argparse
import sys
import time  # this is only being used as part of the example
import datetime
from multiprocessing import Process
#import socket
from thread import *

# 7 seg stuff
from Adafruit_LED_Backpack import SevenSegment

display = SevenSegment.SevenSegment()
display.begin()

#Clear the display
display.clear()
display.set_brightness(5)


# Deafults
LOG_FILENAME = "/home/pi/fan.log"
LOG_LEVEL = logging.INFO  # Could be e.g. "DEBUG" or "WARNING"

DispDelay = 3

# Define and parse command line arguments
parser = argparse.ArgumentParser(description="Environment controller")
parser.add_argument("-l", "--log", help="file to write log to (default '" + LOG_FILENAME + "')")

# If the log file is specified on the command line then override the default
args = parser.parse_args()
if args.log:
        LOG_FILENAME = args.log

# Configure logging to log to a file, making a new file at midnight and keeping the last 3 day's data
# Give the logger a unique name (good practice)
logger = logging.getLogger(__name__)
# Set the log level to LOG_LEVEL
logger.setLevel(LOG_LEVEL)
# Make a handler that writes to a file, making a new file at midnight and keeping 3 backups
handler = logging.handlers.TimedRotatingFileHandler(LOG_FILENAME, when="midnight", backupCount=3)
# Format each log message like this
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
# Attach the formatter to the handler
handler.setFormatter(formatter)
# Attach the handler to the logger
logger.addHandler(handler)

# Make a class we can use to capture stdout and sterr in the log
class MyLogger(object):
        def __init__(self, logger, level):
                """Needs a logger and a logger level."""
                self.logger = logger
                self.level = level

        def write(self, message):
                # Only log if there is a message (not just a new line)
                if message.rstrip() != "":
                        self.logger.log(self.level, message.rstrip())

# Replace stdout with logging to file at INFO level
sys.stdout = MyLogger(logger, logging.INFO)
# Replace stderr with logging to file at ERROR level
sys.stderr = MyLogger(logger, logging.ERROR)

# Loop forever, doing something useful hopefully:
#while True:
#        logger.info("The counter is now " + str(i))

# ~*~**~*~*~*~* settings *~*~*~*~*~*~*~

# Fan duty cycle storage area
fanStats = '/home/pi/fanstats.txt'
acMode = '/home/pi/acmode.txt'
esMode = '/home/pi/esmode.txt'
      
IDFtempSensor = "28-00000544c344"
OutsideSensor = "28-00000546550c"

Frequency = 60 # seconds
TargetTemp = 73.0
dutycycle = 80 # initial duty cycle on startup
OutsideThresh = 64.0
# read in last duty cycle setting
try:
	f = open(fanStats, 'r')
	dutycycle = int(f.readline())
	f.close()
except:
	pass
	print ('no existing fanstats file found')
	dutycycle = 50

# *~**~*~*~*~**~**~*~*~*~*~**~*~*~*~**~

# read AC mode


try:
        f = open(acMode, 'r')
        acmode = int(f.readline())
        f.close()
except:
        pass
        print ('no ac mode file found')
        acmode = 0

# read ES mode

try:
        f = open(esMode, 'r')
        esmode = int(f.readline())
        f.close()
except:
        pass
        print ('no existing esmode file found')
        esmode = 1



import os
import glob
import time

# this is the TCP server thread which returns stuff to tcp queries

def startserver():

	print 'starting up TCP server...'
#    '''
#    Simple socket server using threads
#    '''

	import socket
#	from multiprocessing import Process
        HOST = ''   # Symbolic name meaning all available interfaces
        PORT = 8888 # Arbitrary non-privileged port

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print 'Socket created'

        #Bind socket to local host and port
        try:
                s.bind((HOST, PORT))
        except socket.error as msg:
                print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
                sys.exit()

        print 'Socket bind complete'

        #Start listening on socket
        s.listen(10)
        print 'Socket now listening'

        #Function for handling connections. This will be used to create threads
        def clientthread(conn):
		global dutycycle
		global IDFTemp
		global TargetTemp	
#		global dutycycle
                #Sending message to connected client
                conn.send('Fan Control\n') #send only takes string

            #infinite loop so that function do not terminate and thread do not end.
                while True:
		 #Receiving from client
                        data = conn.recv(1024)
                        reply = 'OK\n'
                        if data == 'DC':
                                reply = str(dutycycle) + '\n'
                        elif data == 'INTTEMP':
                                reply = str(IDFTemp) + '\n'
			elif data == 'TARGET':
				reply = str(TargetTemp) + '\n'
			elif data == 'OUTSIDE':
				reply = str(OutsideTemp) + '\n'
			elif data == 'ACMODE':
				reply = str(acmode) + '\n'
			elif data == 'ESMODE':
				reply = str(esmode) + '\n'
			elif data == 'OUTSIDETHRESH':
				reply = str(OutsideThresh) + '\n'
                        elif data == 'BYE':
                                break


                        if not data:
                                break

                        conn.sendall(reply)

    #came out of loop
                conn.close()

#now keep talking with the client
        while 1:
    #wait to accept a connection - blocking call
                conn, addr = s.accept()
                print 'Connected with ' + addr[0] + ':' + str(addr[1])

    #start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function.
                start_new_thread(clientthread ,(conn,))

        s.close()


#os.system('modprobe w1-gpio')
#os.system('modprobe w1-therm')

#base_dir = '/sys/bus/w1/devices/'
#device_folder = glob.glob(base_dir + '28*')[0]
#device_file = device_folder + '/w1_slave'
def read_temp_raw(sensorID):
	
	base_dir = '/sys/bus/w1/devices/'
	
	device_file = base_dir +  sensorID + '/w1_slave'



        f = open(device_file, 'r')
        lines = f.readlines()
        f.close()
        return lines
	
def read_temp(sensorID):
        lines = read_temp_raw(sensorID)
	
        while lines[0].strip()[-3:] != 'YES':
                time.sleep(0.2)
                lines = read_temp_raw()
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
                temp_string = lines[1][equals_pos+2:]
                temp_c = float(temp_string) / 1000.0
                temp_f = temp_c * 9.0 / 5.0 + 32.0
                return temp_f
#	return 74.3	
#while True:
#        print(read_temp())
#        time.sleep(1)

def change_dc(dc):
	global dutycycle
	if dutycycle + dc <= 0:
		dutycycle = 0
		print "**** duty cycle maxed out at 100%"
	elif dutycycle + dc > 100:
		print "**** duty cycle minimized to 0%"
		dutycycle = 100
	else:
		dutycycle = dutycycle + dc
	
	p.ChangeDutyCycle(dutycycle)

	print "**** Setting Duty cycle: " + str(dutycycle)
	f = open(fanStats, 'w')
	f.write(str(dutycycle)+'\n')
	f.close

def control_ac(mode):
	global acmode
	if acmode != mode:
		if mode == 1:
			print "**** turned AC on ****"
			# send the on command
			os.system("/usr/bin/irsend SEND_ONCE lg_air KEY_POWER")
		
		else:
			print "**** turned AC off ****"
			# send the off command
			os.system("/usr/bin/irsend SEND_ONCE lg_air KEY_POWER")
		
		f = open(acMode, 'w')
                f.write(str(mode)+'\n')
                f.close
	
	acmode = mode

def control_es(mode):
        global esmode
        if esmode != mode:
                if mode == 1:
                        print "**** turned AC ES on ****"
                        # send the on command
                        os.system("/usr/bin/irsend SEND_ONCE lg_air KEY_MODE")

                else:
                        print "**** turned AC ES off ****"
                        # send the off command
                        os.system("/usr/bin/irsend SEND_ONCE lg_air KEY_MODE")

                f = open(esMode, 'w')
                f.write(str(mode)+'\n')
                f.close

        esmode = mode

# for reading a/c mode
#import urllib2

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setup(12, GPIO.OUT)
p = GPIO.PWM(12, 1000)
p.start(1)
change_dc(0)
IDFTemp = 0
Outsidetemp = 0
def mainscript():
	global currTemp
	global TargetTemp
	global dutycycle
	global IDFTemp
	global acmode
	global OutsideTemp
	while True:
	
		# get the current temp
		currTemp = read_temp(IDFtempSensor)
		IDFTemp = currTemp
		print "Current Temp " + str(currTemp)
		logger.info("Current Temp " + str(currTemp))

		OutsideTemp = read_temp(OutsideSensor)

		print "Outside  Temp " + str(OutsideTemp)
                logger.info("Outside Temp " + str(OutsideTemp))

		if OutsideTemp > OutsideThresh and int(acmode) == 0:
			# turn AC on
			print "Turning AC ON"
	                logger.info("Turning AC ON")
			control_ac(1)

		if OutsideTemp < OutsideThresh - 1.00  and int(acmode) == 1:
			# turn AC off
			print "Turning AC OFF"
			logger.info("Turning AC OFF")
			control_ac(0)


		if OutsideTemp > 70.0 and int(esmode) == 1:
			# turn ES mode off
			print "Turning off ES mode"
			logger.info("Turning off ES mode")
			control_es(0)

		
		if OutsideTemp < 69.0 and int(esmode) == 0:
                        # turn ES mode on
                        print "Turning on ES mode"
                        logger.info("Turning on ES mode")
                        control_es(1)

	
		tempDiff = currTemp - TargetTemp
		print "Temp difference is " + str(tempDiff)

		# check if AC is on... (we will update this when we get the 2nd sensor hooked up)
		#response = urllib2.urlopen('http://172.25.0.6/cgi-bin/acstatus.py')
		#acmode = response.read()	
		#print "acmode: " + acmode	
		if int(acmode) == 1 and currTemp < 80:
			print "AC is on!!"
			change_dc(100)
		else:

			if tempDiff > 2:
				change_dc(-20)
			elif tempDiff > 1:
				change_dc(-10)
			elif tempDiff < 1 and tempDiff > -1:
				print "Target temp reached! keeping duty cycle: " + str(dutycycle)
			elif tempDiff < -3:
				change_dc(20)
			elif tempDiff < -2:
				change_dc(10)
			elif tempDiff < -1:
				change_dc(5)
		
	
		time.sleep(Frequency)



# end of main script

def disp():
	global dutycycle
	global IDFtemp
	global DispDelay
	while True:
		currTemp = str(IDFTemp)
		dutyfill = str(100 - dutycycle).zfill(3)
#		print dutyfill


		display.clear()
	# ok show the duty cycle
	# Set hours
		display.set_digit(0, 'F')     # Tens
		
		if dutyfill[:1] == '0':
			display.set_digit(1, '')          # one hundred
		else:
			display.set_digit(1, '1')


		display.set_digit(2, dutyfill[1:2])   # Tens
		display.set_digit(3, dutyfill[-1:])        # Ones
#		print "writing the display"
		display.write_display()		
		time.sleep(DispDelay)

		# ok now show the temperature
#		print currTemp
		display.clear()
		if float(currTemp) >= 100:
			display.set_digit(0, currTemp[:1])
			display.set_digit(1, currTemp[1:2])
                        Display.set_digit(2, currTemp[2:3])
                        Display.set_digit(3, currTemp[-1:])

		else:
			# less than 100 stuff
			display.set_digit(1, currTemp[:1])
			display.set_digit(2, currTemp[1:2])
			display.set_digit(3, currTemp[3:4])
		
		display.set_fixed_decimal(True)
		display.write_display()
                time.sleep(DispDelay)

		# ok for fun lets show the time
		display.clear()
		now = datetime.datetime.now()
   		#hour = ((now.hour + 11) % 12) + 1
     		hour = now.hour
		minute = now.minute
      		second = now.second
      		# Set Hours
      		display.set_digit(0, int(hour / 10))     # Tens
      		display.set_digit(1, hour % 10)          # Ones
      		# Set Minutes
      		display.set_digit(2, int(minute / 10))   # Tens
      		display.set_digit(3, minute % 10)        # Ones
      		display.set_colon(True)
      		display.write_display()     # Tens
      		# Wait one second
      		time.sleep(DispDelay)
		# ac mode on?

		if int(acmode) == 1:
			display.clear()
#			print "printing ac mode on"
			display.set_digit(1, 'A')
			display.set_digit(2, 'C')
			display.write_display() 
			time.sleep(DispDelay)

if __name__ == '__main__':
#    Process(target=startserver).start()
#    Process(target=mainscript).start()
	start_new_thread(startserver,() )
	start_new_thread(disp,() )
	mainscript()


#raw_input('Press return to stop:')   # use raw_input for Python 2
#p.stop()
#GPIO.cleanup()

