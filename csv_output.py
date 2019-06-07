import csv

def output( myList, name, outputdir):
    fname = '%s.csv' %name
    #with open(outputdir + '/%s.csv' % name, 'w', newline='') as csvfile:
    with open(outputdir+"/"+fname, 'w', newline='') as csvfile:
        fieldnames = ['IP', 'STATE', "Details"]
        commands=[]
        #print(myLlist[1]["info"])
        for i,e in enumerate(myList[0]["Commands"]):
            fieldnames.append(e)
        print(fieldnames)
        #fieldnames = ['NAME', 'PID', 'SN', 'IOS', 'MEMORY', 'FAN STATUS', 'TEMPERATURE']
        csvfile.write('SEP=,\n')
        writer = csv.DictWriter(csvfile, fieldnames = fieldnames)
        #writer.writerow('SEP=,')
        writer.writeheader()
        output_row={}
        writer.writerow(output_row)
        for element in myList:

            if "OK" in element["state"]:
                print("csv loop:", element["state"])
                if "Telnet" in name:
                    f = open(outputdir+"/SuccessTXT"+"/"+"Telnet-"+element["host"]+".txt", "w+")
                else:
                    f = open(outputdir +"/SuccessTXT"+"/"+"SSH-" + element["host"] + ".txt", "w+")
                f.write("==============================================================================================================\n"+
                        element["host"]+"\n")
                f.write("State:"+element["state"]+"\n")
                f.write("Details:" + element["details"] + "\n")
                f.write( "==============================================================================================================\n")

                output_row['IP']=element["host"]
                output_row['STATE']=element["state"]
                output_row['Details'] = element["details"]

                for i,e in enumerate(element["info"]):
                    f.write("--------------------------------------------------------------------------------------------------------------\n")
                    f.write("Command: < " +fieldnames[i+3] +">\n" +"--------------------------------------------------------------------------------------------------------------\n" + e + "\n")
                    output_row[fieldnames[i+3]] = e

                writer.writerow(output_row)
                f.close()
           # output_row['EXTRA']=element("extra")

        #    print output_row
        #    raw_input()

        print ('\nOutput Successfull!\n')
        return 0
