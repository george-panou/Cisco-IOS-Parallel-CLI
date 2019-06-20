[![published](https://static.production.devnetcloud.com/codeexchange/assets/images/devnet-published.svg)](https://developer.cisco.com/codeexchange/github/repo/george-panou/Cisco-IOS-Parallel-CLI)

# Cisco IOS Parallel CLI

<p>This is an application to run IOS CLI commands simultaneously on multiple cisco devices. It offers a Graphical Interface to run the commands displaying the output live and reporting it in .txt and scv format.
<p>It uses multithreading to speed up the procedure, opening one parallel SSH connection per device IP 
<p>Add the device IPs on the left panel and the set of commands to be executed on the right panel.<p>The list needs to be consisted of one IP per line 
<p>You can use the formating function to remove illegal characters from the IP list, it will also delete illegal IPs and remove Duplicate IPs.<p>You can check if the IP list contains illegal IPs using the check IPs Button<p> 
<p>With format you could for example get rid of characters:

## Graphical Interface

![N|Image](https://github.com/george-panou/Cisco-IOS-Parallel-CLI/blob/master/images/Cisco-OS-Parallel-CLI-GUI-screen.png)

### Formating feature
if you format this:

- 192.168.1.1-basement
- ip:192.168.1.2-1st floor

you would get this:
- 192.168.1.1
- 192.168.1.2

<p>
You could import the IPs through a file as well using the Browse for file button, it shares the functionality with copy pasting the data.


## Installation 
While installation is not needed you need to install some dependencies:
The version of python used is python 3, it's not backwards compatible with python 2

1.  Install python3 :  https://www.python.org/ftp/python/3.7.2/python-3.7.2-webinstall.exe
2.  During installation check add to path
3.  Install libraries via cmd : 

    -	pip install pathlib
    -	pip install netmiko
    -	pip install paramiko
    -	pip install -U wxPython
    -   pip install requests 
    

    
## Usage
1. cd into the directory that ciscoCLI.py is located και and run: python ciscoCLI.py alternatively you can double click the provided run.bat file if you are on windows
2. Place one IP per line and one command per line in the IP List and Commands List respectively
3. Click the Run Commads Button
4. Live output will be displayed in the main text area - this will be asynchronous with one thread corresponding to one device 
5. The software will attempt to login using ssh and telnet if ssh fails, it will also retry at each of these two steps with alternate credentials only if they are actually supplied
6. The application will create a directory with a timestamp as its name including up to four csv files with the command's results 
    it will also crete another folder with .txt files, with detailed output - one file for each device 
7. In universal failures .csv you can find the devices that the application could not login at all or failed to execute the commands at some point

### Accessing the Results
Here are some sample results after performing a use case wich covers a SSH successful connection, a failed telnet connection and a non existing IP:

The use case senario includes one SSH enabled device one only accessible via Telnet and one non-existent:<br>
![N|Image](https://github.com/george-panou/Cisco-IOS-Parallel-CLI/blob/master/images/mainGUI2.png)

The created folder's structure after the application completed the task:<br>
![N|Image](https://github.com/george-panou/Cisco-IOS-Parallel-CLI/blob/master/images/results-folder-structure.png)

Here you can see the output of the SSH connections that were successfull:<br>
![N|Image](https://github.com/george-panou/Cisco-IOS-Parallel-CLI/blob/master/images/CSV-Output.png)

The .txt version of the output:<br>
![N|Image](https://github.com/george-panou/Cisco-IOS-Parallel-CLI/blob/master/images/results-txt-sample.png)

The reported failures:<br>
![N|Image](https://github.com/george-panou/Cisco-IOS-Parallel-CLI/blob/master/images/AllFailures-sample.png)


It can be run on windows, linux, mac 

## Known Issues

The application will fail to ignore some self signed certificates, causing the connection to the network device to close.
We are working on better identifying the issue's root cause.


## Getting Help 

If you face any issues please create an issue in the github built-in issue tracker


## Contributing

Please contact me if you want to contribute to this project and I will give you further instructions.
<br>
<br>


