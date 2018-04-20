import socket
import select
import threading
import time
import sys
import subprocess
import os

# this script relys on either the AP or Pex printing this to end the test

terminateMSG = "MSG: End test."

# print fpga io to stdout

printIO = True

# set timeout seconds

timeoutSec = 30

# configure the test log files

uartPort = 4444
uartLogFile = "uart.log"

statusPort = 3344
statusLogFile = "pex.log"

renodePort = 3320

testDone = False
    
def watchdog():
    global testDone
    for i in range(timeoutSec * 10):
        if not testDone:
            time.sleep(0.1)
    print "Watchdog timeout"
    testDone = True

def connect(host, port):
    global testDone
    res = None
    connecting = True
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while connecting and not testDone:
        try:
            s.connect((host, port))
            connecting = False
            res = s
            print "connected {0}:{1}".format(host, port)
        except:
            print "trying {0}:{1}...".format(host, port)
            time.sleep(1)
    if connecting:
        print "Failed to connect {0}:{1}...".format(host, port)
    return res

def logPort(name, logFile, port):
    global testDone
    data = ""
    print "logging ", name, " to: ", logFile
    f = open(logFile, "w")
    s = connect(socket.gethostname(), port)
    while(s and not testDone):
        time.sleep(1)
        if terminateMSG in data:
            testDone = True
        data = ""
        ready_r, ready_w, err = select.select([s], [], [],1)
        if ready_r:
            data = s.recv(1024).replace('\r', '')
            f.write(data)
                

    if s:
        s.close()
    f.close()

def launchRenode():
    global testDone
    try:
        cmdpth = os.path.join(os.environ['HOME'], "dover-repos", "renode")
        runcmd = "renode"
        opts = [ "--plain", "--disable-xwt", "--port={0}".format(renodePort)]
        rc = subprocess.Popen([os.path.join(cmdpth, runcmd)] + opts)
        while rc.poll() is None:
            time.sleep(0.01)
    finally:
        testDone = True
        
def runOnRenode():
    global testDone
    global connecting
    try:
        print "Begin Renode test... (timeout: ", timeoutSec, ")"
        wd = threading.Thread(target=watchdog)
        wd.start()
        print "Launch Renode..."
        renode = threading.Thread(target=launchRenode)
        renode.start()
        time.sleep(2)
        print "Start Logging..."
        uartLogger = threading.Thread(target=logPort, args=("Uart", uartLogFile, uartPort))
        uartLogger.start()
        statusLogger = threading.Thread(target=logPort, args=("Status", statusLogFile, statusPort))
        statusLogger.start()
        print "Start Renode..."
        s = connect(socket.gethostname(), renodePort)
        if s:
            with open('main.resc', 'r') as f:
                s.send(f.read().replace('\n', '\r\n'))
                s.send('start\r\n')
            while not testDone:
                time.sleep(0.1)
                ready_r, ready_w, err = select.select([s], [], [],1)
                if ready_r:
                    print s.recv(1024).replace('\r', '')
        if s:
            s.send('quit\r\n')
            time.sleep(1)
            s.close()
        wd.join()
        uartLogger.join()
        statusLogger.join()
        renode.join()
            # TODO: have the watchdog timer kill the renode process
#            if testDone:
#                rc.kill()
        print "Test Completed"
    finally:
        if s:
            s.send('quit\r\n')
            time.sleep(1)
            s.close()
           
if __name__ == "__main__":
    runOnRenode()
    
