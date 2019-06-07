<p>This is a programm to run IOS CLI commands simultaneously on multiple cisco devices. It offers a Graphical Interface to run the commands displaying the output live and reporting it in .txt and scv format.
<p>It uses multithreading to speed up the procedure, opening one parallel SSH connection per host IP 
<p>Add the host IPs on the left panel and the set of commands to be executed on the right panel.<p>The list needs to be consisted of one IP per line 
<p>You can use the formating function to remove illegal characters from the IP list, it will also delete illegal IPs and remove Duplicate IPs.<p>You can check if the IP list contains illegal IPs using the check IPs Button<p> 
<p>With format you could for example get rid of characters:

if you format this:

- 192.168.1.1-basement
- ip:192.168.1.2-1st floor

you would get this:
- 192.168.1.1
- 192.168.1.2

<p>

You could import the IPs through a file as well using the Browse for file button, it shares the functionality with copy pasting the data.

<b><u>Prerequiites</u></b>:

1.  Install python3 :  https://www.python.org/ftp/python/3.7.2/python-3.7.2-webinstall.exe
2.  During installation check add to path
3.  Install libraries via cmd : 

    -	pip install pathlib
    -	pip install netmiko
    -	pip install -U wxPython
    -   pip install requests 
    
<b><u>How to run</u></b>: 
1. cd into directory of ciscoCLI.py και and run: python ciscoCLI.py
2. The programm will create a directory with a timestamp including up to four csv <p>files with results an a folder with .txt files with detailed output of devices on <p>which it logged in successfully 
3. Place one IP per line and one command per line in the interface
4. The software will attempt to login using ssh and telnet if ssh fails, it will also<p> retry at each of these two steps with alternate credentials only if they are <p>actually supplied
5. In univerall failures .csv you can find the devices that the programm couldn't login at all

It can be run on windows, linux, mac 
