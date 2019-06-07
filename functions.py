import paramiko as pm
import csv_output
import threading
import datetime

import pathlib
import netmiko as nm
import socket
import re
import csv_failures

global threads
global list
global telnetList
global netmikoList

global username
global password

global usernameAlt
global passwordAlt

global failures

global hostFailsCount



class AllowAllKeys(pm.MissingHostKeyPolicy):
    def missing_host_key(self, client, hostname, key):
        return



def CLIPrompt():
    username=input("Enter Devices' Username:")
    newline=input(":")
    password=input("Enter Devices' Password:")

def setCredentials(user,passwd):
    global username
    global password
    username=user
    password=passwd


#hosts = filter(None, hosts)
#print(hosts)
ipregex=re.compile(r"(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])")
#ipregex=re.compile(r"\d{1, 3}\.\d{1, 3}\.\d{1, 3}\.\d{1, 3}$")
#Removes dublicates and applies regular expression to list items
#actually extracts IPs from given text
def formatInput(hosts):
    ipregex = re.compile(
        #Valid IPs
        r"(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])")

    #all ip look alikes
    #ipregex = re.compile(r"(\d+)\.(\d+)\.(\d+)\.(\d+)")
    #ipregex=re.compile(r"\d{1, 3}\.\d{1, 3}\.\d{1, 3}\.\d{1, 3}$")
    #ipregex = re.search("(\d{1, 3})\.(\d{1, 3})\.(\d{1, 3})\.(\d{1, 3})")

    tmp=hosts[:]

    # Attempt to Format list
    formatted1=[]
    formatted=[]
    for e in tmp:
        try:
            formatted1.append(re.search(ipregex,e).groups(1))
        except Exception as exeption:
           # print(exeption,e)
            pass
    for e in formatted1:
        stringIP=""
        i=0
        for ee in e:
            if i == 0 :
                stringIP=ee
            else:
                stringIP+="."+ee
            i+=1
        formatted.append(stringIP)
    #remove dublicates
    tmp2=[]
    for i in formatted:
        #tmp2.append(i)
        if i not in tmp2:
            tmp2.append(i)
   # print("Formatted",tmp2)
    return tmp2


#hosts=formatInput(hosts)
#tmp=hosts[:]

#check if the input IPs are valid and remove invalid ones
#kind of useless after formating
def checkIPs(hosts):

    illegalips = []
    #print(tmp)
    for e in hosts:
        #print("e", e)
        if re.match(ipregex, e):
            #print("regular", e)
            pass
        else:
           # print("Irreggguuull",e)
            hosts.remove(e)
            illegalips.append(e)
            continue

        if e.isspace() or not e :
            hosts.remove(e)
            illegalips.append(e)
            continue


        if not re.match(ipregex, e):
            print("regular",e)
            hosts.remove(e)
            illegalips.append(e)
            continue

        try:#if not valid ip it will throw exception
            socket.inet_aton(e)
            # legal
        except socket.error:
            hosts.remove(e)
            illegalips.append(e)
            continue
            #print("Found elegal IP", e)



    # Not legal
    print("-List of hosts :")
    for element in hosts:
        print(element)
    #print("-List of hosts :",hosts)

    print("Illegal IPs :",illegalips)
    if len(illegalips)==0:
        return True
    else :
        return False


def parseCommands(filename):
    with open('CiscoCommandsToExecute.txt', 'r') as content_file:
        commands = content_file.read()
    return commands
    #Huawei
    #'213.249.48.86'
    #62.74.241.206
    state=""

def telnetCommands(host,event,commands,type,user,passwd,retry):
    global telnetList
    global failures
    state="OK"
    output=[]
    stre = "None"
    lines = commands.splitlines()
#    print("Trying with telnet")

        #Using netmiko telnet client
    net_connect = None
    try:
        device = {
            'device_type': 'cisco_ios_telnet',
            'ip': host,
            'username': user,
            'password': passwd,

            'timeout': 40
        }
        # net_connect=nm.BaseConnection(verbose=True,ip=host,device_type="cisco_ios",username="algo",password="$$#A1g0!+$",port=22,session_log="testlog.txt")
        #print('Host: {}'.format(device))
        net_connect = nm.ConnectHandler(**device)

        lines = commands.splitlines()
        for command in lines:
            if type == 0:
                output.append(net_connect.send_config_set(command) + "\n")
            else:
                output.append(net_connect.send_command_timing(delay_factor=1.5,command_string=command) + "\n")
        try:
            net_connect.disconnect()
        except:
            print("Disconnected ",host)

    except Exception as e:
        print("type error: " + str(e))
        stre = str(e)
        state = "Exception"
        global hostFailsCount
        if ("login" in str(e) ):
            print("Trying with alternative user/pass")
            failures.append([host, "Telnet-Auth"])
            hostFailsCount[host] += 1
            if retry != 2 and (usernameAlt!="" and passwordAlt!=""):
                retry+=1
                telnetCommands(host,event,commands,type,usernameAlt,passwordAlt,retry)
                return
        elif "period" in str(e):
            print("Timed out")
            failures.append([host, "Telnet-Timeout"])
            if (usernameAlt == "" or passwordAlt == ""):
                hostFailsCount[host] += 1
            else:
                hostFailsCount[host] += 2
        else:
            hostFailsCount[host] += retry
        telnetList.append({"host": host, "state": state, "info": output, "details": stre, "Commands": lines})
        return
    telnetList.append({"host": host, "state": state, "info": output, "details": stre, "Commands": lines})
       # net_connect.disconnect()
    print("Output:", output)




def executeCommandsNetmiko(host,event,commands,type,user,passwd,retry):
    global netmikoList
    global failures
    state="OK"
    info="No output"
    stre="None"
    output=[]
    lines = commands.splitlines()
    net_connect = None
    try:
        device = {
            'device_type': 'cisco_ios',
            'ip': host,
            'username': user,
            'password': passwd,
            'port': 22,
            'global_delay_factor': 1,
            'verbose': True,
            'timeout' : 40
        }
        #net_connect=nm.BaseConnection(verbose=True,ip=host,device_type="cisco_ios",username="algo",password="$$#A1g0!+$",port=22,session_log="testlog.txt")
        net_connect = nm.ConnectHandler(**device)

        for command in lines :
            if type == 0:
                output.append(net_connect.send_config_set(command)+"\n")
            else:
                output.append(net_connect.send_command_timing(delay_factor=1.5,command_string=command)+"\n")

        #output.append("Seems OK\n")
        state="OK"

        print(output)

        try:
            net_connect.disconnect()
        except:
            print("Disconnected ",host)

    except Exception as e:
        print("type error: " + str(e))
        stre=str(e)
        state = "Exception"

        if ("Authenticat" in str(e) ):
            print("Trying with alternative user/pass")
            failures.append([host, "SSH-Auth"])
            hostFailsCount[host] += 1
            if retry != 2 and (usernameAlt!="" and passwordAlt!=""):
                retry+=1
                executeCommandsNetmiko(host,event,commands,type,usernameAlt,passwordAlt,retry)
                return
        elif "timed-out" in str(e):
            print("Timeout SSH")
            failures.append([host, "SSH-Timeout"])
            if (usernameAlt == "" or passwordAlt == ""):
                hostFailsCount[host] += 1
            else:
                hostFailsCount[host] += 2
        else:
            hostFailsCount[host] += retry
        netmikoList.append({"host": host, "state": state, "info": output, "details": stre, "Commands": lines })
        return

    netmikoList.append({"host": host, "state": state, "info": output, "details": stre,"Commands":lines})

    #list.append({"host":host,"state":state,"info":info,"details":stre})


def mainLogic(hosts,commands,user,passwd,commandType,userAlt,passwdAlt) :
    global list
    global username
    global password
    username=user
    password=passwd

    global usernameAlt
    global passwordAlt
    usernameAlt=userAlt
    passwordAlt=passwdAlt
    threads=[]
    list=[]

    global failures
    failures=[]

    global hostFailsCount
    hostFailsCount={}
    for host in hosts:
        hostFailsCount[host] = 0
    #print (hostFailsCount)

    #Stage 1
    #Try with netmiko for each failed device after stage 1

    now = datetime.datetime.now()
    outputdir = 'Results-' + now.strftime("%Y-%m-%d %H_%M")
    pathlib.Path(outputdir).mkdir(parents=True, exist_ok=True)
    pathlib.Path(outputdir + "/SuccessTXT").mkdir(parents=True, exist_ok=True)


    threads=[]
    global netmikoList
    netmikoList=[]
    #print("Netmiko",list)
    print("Trying devices with SSH Please wait... Devices: ", hosts)
    for e in hosts:
        event = threading.Event()
        # print(host)
        deviceThread = threading.Thread(target=executeCommandsNetmiko, args=(e, event,commands,commandType,username,password,1))
        threads.append(deviceThread)
        deviceThread.start()

    #wait for all threads from stage 2 to finish
    for thread in threads:
        thread.join()

    if netmikoList!=[]:
        csv_output.output(netmikoList,"SSH Results - "+now.strftime("%Y-%m-%d %H_%M"),outputdir)

    print("Check->",netmikoList)

    threads=[]
    global telnetList
    telnetList=[]
    #Start stage 3 : try with telnet connection (Netmiko)

    print("Trying failed devices with Telnet Please wait... ")
    for e in netmikoList:
        if not "OK" in e["state"]:#e.get('state', " "):
            print(str(e))
            event = threading.Event()
            deviceThread = threading.Thread(target=telnetCommands,args=(e["host"], event,commands,commandType,username,password,1))
            threads.append(deviceThread)
            deviceThread.start()


    #wait for all failed telnet accessed devices to finish
#    print("join")
    for thread in threads:
        thread.join()

    if telnetList!=[]:
        csv_output.output(telnetList, "TelnetResults - "+now.strftime("%Y-%m-%d %H_%M"), outputdir)

    failures.sort(key=lambda x: x[0])
    csv_failures.output(failures, "All failures - " + now.strftime("%Y-%m-%d %H_%M"), outputdir)

    universallFails=[]
    success=[]

    for host in hosts:
        for e in netmikoList:
            if "OK" in e["state"]:
                success.append(e["host"])
        for e in telnetList:
            if "OK" in e["state"]:
                success.append(e["host"])


    universallFails = []

    allmethosFailsTotal=0
    print(hostFailsCount)
    for host in hosts:
        if (hostFailsCount[host] >= 4 and (usernameAlt != "" and passwdAlt != "" ) ):
            universallFails.append([host, "Failed After All the Steps", hostFailsCount[host]])
        elif (hostFailsCount[host] >= 2  and (usernameAlt == "" or passwdAlt == "")):
            universallFails.append([host, "Failed After All the Steps", hostFailsCount[host]])

    print("Universally Failed" + str(len(hostFailsCount)))

    if (len(universallFails) != 0  ):
        csv_failures.output(universallFails, "Universally Failed - " + now.strftime("%Y-%m-%d %H_%M"), outputdir)
        print("Universally Failed")

    print("########################################################")
    print("Finished executing cli commands on all devices")
    print("Your results are in the " + outputdir + " folder")
    print("########################################################")




