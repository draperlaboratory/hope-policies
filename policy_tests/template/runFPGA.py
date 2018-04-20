from serial import Serial, PARITY_NONE, STOPBITS_ONE, EIGHTBITS
import threading
import time
import sys

# this script relys on either the AP or Pex printing this to end the test

terminateMSG = "MSG: End test."

# print fpga io to stdout

printIO = True

# set timeout seconds

timeoutSec = 120

# configure the test init file

testInit = "auto.init"

# configure the test log files

pexLogFile = "pex.log"
apLogFile = "ap.log"

# configure the serial connections

sysconUART = '/dev/ttyUSB0'
sysconBAUD = 115200

pexUART = '/dev/ttyUSB2'
pexBAUD = 115200

apUART = '/dev/ttyUSB1'
apBAUD = 115200

def getPrompt(s):
    global testDone
    line = ""
    reading = True
    while reading and not testDone:
        b = s.read(1)
        if b == '\r':
            reading = False
        else:
            line += b
    return line

def connect(port, baud):
    s = Serial(
	port=port,
	baudrate=baud,
	parity=PARITY_NONE,
	stopbits=STOPBITS_ONE,
	bytesize=EIGHTBITS,
        timeout=0.1
    )
    return s

def disconnect(s):
    s.close()

# expects 0xd line termination, echos characters sent.
def resetChip(s):
    s.reset_input_buffer()
    global testDone
    for i in range(10):
        prompt = ""
        s.write("\r")
        time.sleep(0.01)
        s.write("\r")
        time.sleep(0.01)
        s.write("i\r")
        time.sleep(0.01)
        s.write("\r")
        time.sleep(0.1)
        for j in range(10):
            prompt = getPrompt(s)
            if printIO:
                print "syscon: ", prompt
            if prompt == "0123456789ABCDEF":
                return
    print "Failed to reset chip"
    testDone = True
    assert False 

def loadTest(s, initFile):
    # wait for bootloader
    time.sleep(1)
    with open(initFile, "rb") as f:
        bytes = f.read()
        tick = len(bytes) / 9
        count = 0
        for b in bytes:
            s.write(b)
#            time.sleep(0.0002) # delay 200 uSec between bytes
            count = count + 1
            if count > tick:
                print "*",
                sys.stdout.flush()
                count = 0
        # add a newline
        print
        
def getLine(s):
    line = ""
    while True:
        b = s.read(1)
        if b == '':
            return ""
        if b == '\n':
            line += b
            return line
        else:
            line += b

testDone = False

def logPort(name, uart, logFile):
    global testDone
    print "logging ", name, " to: ", logFile
    f = open(logFile, "w")
    while(not testDone):
        try:
            l = getLine(uart)
            if l != '':
                if printIO:
                    print name, ": ", l,
                f.write(l)
            if terminateMSG in l:
                testDone = True
        except SerialException:
                testDone = True
                f.write("Fatal Serial Port Error!\n")
    f.close()

def watchdog():
    global testDone
    for i in range(timeoutSec * 10):
        if not testDone:
            time.sleep(0.1)
    testDone = True
    
def runOnFPGA():
    global testDone
    try:
        print "Begin serial test... (timeout: ", timeoutSec, ")"
        wd = threading.Thread(target=watchdog)
        wd.start()
        syscon = connect(sysconUART, sysconBAUD)
        pex = connect(pexUART, pexBAUD)
        ap = connect(apUART, apBAUD)
        resetChip(syscon)
        print "Chip Reset"
        print "loading test..."
        loadTest(pex, testInit)
        print "test file loaded"
        print "logging..."
        pexLogger = threading.Thread(target=logPort, args=("Pex", pex, pexLogFile))
        apLogger = threading.Thread(target=logPort, args=("AP", ap, apLogFile))
        pexLogger.start()
        apLogger.start()
        while not testDone:
            time.sleep(0.1)
        pexLogger.join()
        apLogger.join()
        wd.join()
        print "Test Completed"
    finally:
        testDone = True
        disconnect(syscon)
        disconnect(pex)
        disconnect(ap)
    
    
if __name__ == "__main__":
    runOnFPGA()
    
