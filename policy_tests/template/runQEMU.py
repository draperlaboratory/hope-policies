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
runcmd = "qemu-system-riscv32"
cwd = os.getcwd()
opts = [ "-nographic",
         "-machine", "sifive_e",
         "-kernel", "build/main",
         "-serial", "file:{}".format(uartLogFile),
         "-D", statusLogFile,
         "-singlestep", #need to instrument every target instruction
         "-d", "nochain",
         "--policy-validator-cfg",
         "policy-path={policyDir},tag-info-file={tagFile}"]


def watchdog():
    global testDone
    for i in range(timeoutSec * 10):
        if not testDone:
            time.sleep(0.1)
        else:
            return
    print("Watchdog timeout")
    testDone = True

def launchQEMU(policies):
    global testDone
    try:
        print("Running qemu cmd:{}\n", str([runcmd] + opts))
        rc = subprocess.Popen([runcmd] + opts,
                              env={"LD_LIBRARY_PATH": cwd + '/' + policies,
                                   "PATH": os.environ["PATH"]})
        while rc.poll() is None:
            time.sleep(0.5)
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
        if rc.returncode != 0:
            raise Exception("exited with return code " + str(rc.returncode))
        testDone = True
    except Exception as e:
        print("QEMU run failed for exception {}.\n".format(e))
        raise

def launchQEMUDebug(policies):
    global opts
    opts += ["-S", "-gdb", "tcp::3333"]
    print("Running qemu cmd:{}\n", str([runcmd] + opts))
    rc = subprocess.Popen([runcmd] + opts,
                          env={"LD_LIBRARY_PATH": cwd + '/' + policies,
                               "PATH": os.environ["PATH"]})
    rc.wait()

def runOnQEMU():
    try:
        print("Begin QEMU test... (timeout: ", timeoutSec, ")")
        if len(sys.argv) == 3 and sys.argv[2] == "-d":
            policies = sys.argv[1]
            opts[-1] = opts[-1].format(policyDir=cwd + '/' + policies, tagFile=cwd+"/build/main.taginfo")
            launchQEMUDebug(policies)
        else:
            if len(sys.argv) != 2:
                print("Please pass policy directory name.")
            policies = sys.argv[1]
            opts[-1] = opts[-1].format(policyDir=cwd + '/' + policies, tagFile=cwd+"/build/main.taginfo")
            wd = threading.Thread(target=watchdog)
            wd.start()
            print("Launch QEMU...")
            qemu = threading.Thread(target=launchQEMU, args=(policies,))
            qemu.start()
            wd.join()
            qemu.join()
            print("Test Completed")
    finally:
        pass

if __name__ == "__main__":
    runOnQEMU()

