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

uartLogFile = "uart.log"

statusLogFile = "pex.log"

testDone = False


def watchdog():
    global testDone
    for i in range(timeoutSec * 10):
        if not testDone:
            time.sleep(0.1)
        else:
            return
    print "Watchdog timeout"
    testDone = True

def launchQEMU():
    global testDone
    cwd = os.getcwd()
    try:
        runcmd = "qemu-system-riscv32"
        opts = [ "-nographic",
                 "-machine", "sifive_e",
                 "-kernel", "build/main",
                 "-serial", "file:{}".format(uartLogFile),
                 "-D", statusLogFile,
                 "--policy-validator-cfg",
                 "policy-path={policyDir},tag-info-file={tagFile}".
                 format(policyDir=cwd, tagFile=cwd+"/build/main.taginfo")]

        qemu_env = os.environ.copy()
        qemu_env['LD_LIBRARY_PATH'] = qemu_env['LD_LIBRARY_PATH'] + ':' + cwd
        rc = subprocess.Popen([runcmd] + opts, env=qemu_env)
        while rc.poll() is None:
            time.sleep(0.01)
            try:
                with open(uartLogFile, 'r') as f:
                    for line in f.readlines():
                        if terminateMSG in line or testDone:
                            rc.terminate()
                            testDone = True
                            return
            except IOError:
                #keep trying if fail to open uart log
                pass
    except Exception as e:
        print "QEMU run failed for exception {}.\n".format(e) 
        raise

def runOnQEMU():
    try:
        print "Begin QEMU test... (timeout: ", timeoutSec, ")"
        wd = threading.Thread(target=watchdog)
        wd.start()
        print "Launch QEMU..."
        qemu = threading.Thread(target=launchQEMU)
        qemu.start()
        wd.join()
        qemu.join()
        print "Test Completed"
    finally:
        pass

if __name__ == "__main__":
    runOnQEMU()

