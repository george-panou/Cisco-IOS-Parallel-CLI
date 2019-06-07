import csv

def output( myLlist, name,outputdir):
    fname = '%s.csv' %name
    #with open(outputdir + '/%s.csv' % name, 'w', newline='') as csvfile:
    with open(outputdir+"/"+fname, 'w', newline='') as csvfile:
        fieldnames = ['IP', 'Failure Type']

        #fieldnames = ['NAME', 'PID', 'SN', 'IOS', 'MEMORY', 'FAN STATUS', 'TEMPERATURE']
        csvfile.write('SEP=,\n')
        writer = csv.DictWriter(csvfile, fieldnames = fieldnames)
        #writer.writerow('SEP=,')
        writer.writeheader()
        output_row={}
        writer.writerow(output_row)
        for j,element in enumerate(myLlist,start=1):

            output_row['IP']=element[0]
            output_row['Failure Type']=element[1]

            writer.writerow(output_row)
        print ('\nOutput Successfull!\n')
        return 0
