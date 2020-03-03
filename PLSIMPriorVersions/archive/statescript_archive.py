#Analysis script 2 for Verdiem data from CalPlug 2014 study
#Print States and Dates for a given user in a PLSim or CSV style format
#This is a simple reformatter for a given subject - it will return DB data for that subject with minute resolution
#Developed by M. Klopfer Aug 30, 2018 - V1

#Operation:  This script is a stand-alone processor that takes the Verdiem data and formats it into a style used as a .CSV input into the PLSin program.  This script will not actually output a .CSV file its current state, just format the text in a way that can be quickly formatted into the specific PLSim format.   
            #The script reads from a database/table with the following entries:  record_id    subject_identifier    desktop_type    MPID    device    status    int_record    date    day_of_week P1  P2...[There are 96 entries that correspond to 15 minute periods across the day]

#Dependencies and setup considerations:  This program uses Miniconda/Eclipse in development and is within an Eclipse workshop - it shares identical dependencies as PLSim:  https://github.com/CalPlug/PlugLoadSimulator-PLSim
#Note, if the console is not large enough in Eclipse to display the return, consider the following:  https://stackoverflow.com/questions/2600653/adjusting-eclipse-console-size

import mysql.connector
import sys
from datetime import timedelta
from datetime import datetime
from datetime import date
from datetime import time

#Run Options for Output Formatting
plsimcompliant= False #Decide if you want the printed output to be PLSim compliant or be formatted for a CSV tyle to enter into Excel or other program that works with CSVs 
supressdate = False #Dates must be suppressed for direct PLSim compliance, help one read material when aligning data, but this must be supressed to be PLSim Compitable
elapsedminortime = False #If true, display Elapsed minutes versus time
annotatetransitions = True #Will display at the end of each line the number of transitions per row of data (in a given state) for CSV Formatting
addedfields = True #If true, this will add all fields as in the order of the original dataset to the printout - works only for CSV
blankheaders=True #Use to remove all header info above the text to be used in data of the state info - helpful when quick combining in a text editor
# Open database connection
db = mysql.connector.connect(host="cplamp.calit2.uci.edu",    # host
                     user="calplug",         # username
                     passwd="123456!",  # password
                     db="VerdiemStudy")        # DBName

cursor = db.cursor() # Cursor object for database query

query = ("SELECT * FROM DATA "
         "WHERE subject_identifier = %(s_ID)s AND (date BETWEEN %(start_DATE)s AND %(end_DATE)s)") #base query

#Query for device states
query_modifications= {'s_ID': 18,'start_DATE': "2014-01-01",'end_DATE': "2014-12-31"} #query records updated by defined variables in dictionary, for device, start and end dates - alternatively use this style for datetime hire_start = datetime.date(1999, 1, 1), for date time printout: #for (first_name, last_name, hire_date) in cursor: print("{}, {} was hired on {:%d %b %Y}".format(last_name, first_name, hire_date))
    
cursor.execute(query, query_modifications) #Process query with variable modifications
queryreturn = cursor.fetchall() #Fetch all rows with defined query for first state


sample_rate_distinguisher = "sample_rate:"
sample_rate = 60 #Define sample rate output for the dataset - typically this is 60, referring to 60 seconds corresponding to 1 period which is 1 minute.
devicemfgr = "Generic" #This is a device designator as used with PLSim.
devicename = "GenericPC" #Identifier used in the output string 
periodlength=15  #assume a standard 15 min period length
totalperiods = 95  #total number of columns devoted to the periods
periodstartcolumn = 9 #column which the period info starts in
stateposition = 5 #position of the state/status identifier column
record_idrow = 0 #position original identifier is in
desktop_typerow = 2 #position for the desktop type info
MPIDrow=3 #row MPID info is placed in
int_recordrow = 6
day_of_weekrow = 8 #Day of the Week identifier
daterow = 7 #row that date information is placedin
subjectrow = 1 #Row the subject info is in
devicerow = 4 #Identify row for the device (CPU or USER) that is being reported on 
#write the header for the output denoting the sample distinguisher info

#collect and display unique states in the query
subjecttallylist = [] #total list of states found
statetallylist = [] #total list of states found
datetallylist = []  #total list of dates found
for rowindex, row in enumerate(queryreturn): #go thru query and generate a full list of states from the dataset
    statetallylist.append(row[stateposition])
    datetallylist.append(row[daterow])
    subjecttallylist.append(row[subjectrow])



def uniqueinlist(tallylist, identifier, names, maxmin):   
    unique_list = []  # intitalize a null list
    for x in tallylist:
        # check if exists in unique_list or not
        if x not in unique_list:
            unique_list.append(x)
        # print list
    sys.stdout.write("The current entries in the ")
    sys.stdout.write(str(identifier))
    sys.stdout.write(" field of the query: ")
    sys.stdout.write(names)
    sys.stdout.write(": [ ")
    for x in unique_list:
        sys.stdout.write(str(x)) #print list in a row separated by a comma and space
        sys.stdout.write(" ")
    sys.stdout.write("]")
    if (maxmin == True):
        print() #End of list new line
        max_value = max(unique_list)
        min_value = min(unique_list)
        sys.stdout.write("[ ")
        sys.stdout.write("Min Value: ")
        sys.stdout.write(str(min_value))
        sys.stdout.write(" AND ")
        sys.stdout.write("Max Value: ")
        sys.stdout.write(str(max_value))
        sys.stdout.write(" ]")
    print() #End of list new line
    print() #End of list new line

if (blankheaders == False):
    uniqueinlist(subjecttallylist,"SUBJECT" ,"Research Subject", False) #use the function defined above
    uniqueinlist(statetallylist, "STATES","Device States", False) #use the function defined above
    uniqueinlist(datetallylist,"DATE" ,"Observation Dates", True) #use the function defined above


#keep a record of the last state to verify that there are no logic conflicts
#lastlengthinstate = [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]]
logicerrorflag = 0 #identify if there is a logic check error - reset before check, define as zero
lastdate= "" # Holder for the last date object used

if (blankheaders==False):
    print('Total Row(s):', cursor.rowcount) #final count of rows, useful in testing and verification
    print() #time for that needed new-line 
    print() #time for that needed new-line 
    print() #time for that needed new-line 

if (blankheaders==False):
    if (plsimcompliant == False):
        print("Start of Exportable CSV Text:") 
        print()  
    else:
        print("Start of PLSim Schedule CSV Input Text:") 
        print() 
        sys.stdout.write(sample_rate_distinguisher)
        print(str(sample_rate)) #time for that needed new-line

   
#If a Non PLSim CSV file is used, this prints out the heading names:
if (blankheaders==False):
    if (plsimcompliant == False and addedfields != True):
        sys.stdout.write("Date,Manufacturer,Device,State,")
        for x in range(0, (96*15)): #96 sets of 15 minute periods for all minutes in a 24 hour period
            timeholder = datetime.today() #initialize datetimeobject
            timeholder = (datetime.combine(date.today(), time(0,0,0)) + timedelta(minutes=1*x))
            if(elapsedminortime==False):
                sys.stdout.write(datetime.strftime(timeholder, '%H:%M:%S'))   
            else:
                sys.stdout.write(str(x))
            if ((x<(96*15)-1)): #suppress final comma
                sys.stdout.write(",")
        print () #print newline after the header row is finished
if (blankheaders==False):
    if (plsimcompliant == False and addedfields == True):    
        sys.stdout.write("record_id,subject_id,desktop_type,MPID, device, status, int_record, date, day_of_week,")
        for x in range(0, (96*15)): #96 sets of 15 minute periods for all minutes in a 24 hour period
            timeholder = datetime.today() #initialize datetimeobject
            timeholder = (datetime.combine(date.today(), time(0,0,0)) + timedelta(minutes=1*x))
            if(elapsedminortime==False):
                sys.stdout.write(datetime.strftime(timeholder, '%H:%M:%S'))   
            else:
                sys.stdout.write(str(x))
            if ((x<(96*15)-1)): #suppress final comma
                sys.stdout.write(",")
        print () #print newline after the header row is finished
    
for rowindex, row in enumerate(queryreturn): #page thru all returned rows from query, also return an index number related to the row
    #now check for the time in each state as a function of each period
    #FIRST STATE: Define the row information with the device and the state in use - First State Evaluated
    if (plsimcompliant == False and addedfields == True):
        sys.stdout.write(str(row[record_idrow])) #Print record ID
        sys.stdout.write(",")
    if (plsimcompliant == False and addedfields == True):
        sys.stdout.write(str(row[subjectrow])) #Print subject ID
        sys.stdout.write(",")
    if (plsimcompliant == False and addedfields == True):
        sys.stdout.write(str(row[desktop_typerow])) #Print desktop_type ID
        sys.stdout.write(",")
    if (plsimcompliant == False and addedfields == True):
        sys.stdout.write(str(row[MPIDrow])) #Print MPID ID
        sys.stdout.write(",")
    if (plsimcompliant == False and addedfields == True):
        sys.stdout.write(str(row[devicerow])) #Print device type ID
        sys.stdout.write(",")
    if (plsimcompliant == False and addedfields == True):
        sys.stdout.write(str(row[stateposition])) #Print device type ID
        sys.stdout.write(",")
    if (plsimcompliant == False and addedfields == True):
        sys.stdout.write(str(row[int_recordrow])) #Print device type ID
        sys.stdout.write(",")
    if (supressdate == False or addedfields == True): #suppress dates as needed
        sys.stdout.write(row[daterow].strftime("%m/%d/%y")) # (INSERT "("%B %d, %Y")" after %d to have commas in name.  Print out the datetime for each record 
        sys.stdout.write(",") #If record line date is not intended to be displayed, turn of this line also
    if (plsimcompliant == False and addedfields == True):
        sys.stdout.write(str(row[day_of_weekrow])) #Print device type ID
        sys.stdout.write(",")
    
    if (addedfields == False):
        sys.stdout.write(devicemfgr) #print out each device mfgr name per line as the standard in PLSim
        if (plsimcompliant == True):
            sys.stdout.write(" ") #designator used between MFGR and device in PLSim, comment out when using a comma in a non PLSim compliant formatting scheme
        else:
            sys.stdout.write(",")
    if (addedfields == False):
        sys.stdout.write(devicename)
        sys.stdout.write(",")
        sys.stdout.write(row[stateposition]) #identify the state name from that column in the row
        sys.stdout.write(",")
    
    i=0 #loop counter for total range of time periods for a single row
    lastlengthinstate=row[periodstartcolumn] #initialize storage for the first state in the first period of the data
    transitions=0 #initialize storage for counter of transitions
    for x in range(periodstartcolumn, periodstartcolumn+totalperiods): #page thru each of the data columns per the defined start and total number of these
        lengthinstate = int(row[x])  #This is used to read the value at the index each period: total the time active in the column
        if (lengthinstate != lastlengthinstate):
            transitions=transitions+1
            lastlengthinstate = lengthinstate 
        lengthnotinstate = (periodlength-int(row[x])) #This is used to read the value at the index each period: assuming a known total, subtract to find the time not in the state - there would be multiple check under this for more defined states
        #right now this logic is somewhat blind - there is a very rudimentary logic check for past states, there should be something here to make sure that there is no two states active at the same t
        if ("On" or "Active") in row[stateposition]:   #Identify state by string comparison, for User, identify the On state as "Active"
                            #need to identify this is an active state
            for a in range(lengthinstate):
                sys.stdout.write('1') #print out all rows for inspection
                if (plsimcompliant == False):
                    sys.stdout.write(',') #Used when formatting a non-compliant PLSim CSV file
                #lastlengthinstate[(x-periodstartcolumn)][a] = 1 #record all times this active state is on
                #lastdate= row[7].strftime("%B %d, %Y")
            for b in range(lengthnotinstate):
                sys.stdout.write('0') #print out all rows for inspection
                if (plsimcompliant == False):
                    sys.stdout.write(',') #Used when formatting a non-compliant PLSim CSV file
            #sys.stdout.write(' ') #add in a space to distinguish between blocks, can be removed as needed, very helpful to turn on in testing and verification
        else:  #For all other states, the following is valid - reverse the order as a compliment with this simple logic check!
               
            for d in range(lengthnotinstate):
                sys.stdout.write('0') #print out all rows for inspection
                if (plsimcompliant == False):
                    sys.stdout.write(',') #Used when formatting a non-compliant PLSim CSV file
            for c in range(lengthinstate):
                
                #check for logic to see if there are two states active at onceS
                #if (lastlengthinstate[(x-periodstartcolumn)][lengthnotinstate+c] == 1):
                    #logicerrorflag = 1
                    #sys.stdout.write("There may be a problem at: ")
                    #sys.stdout.write(str(rowindex)) #Print current spot in minute array index where 1 is written - this is good to keep on during testing
                    #sys.stdout.write(",") #Print current row index where 1 is written - this is good to keep on during testing
                    #print(a)
                    
                sys.stdout.write('1') #print out all rows for inspection
                if (plsimcompliant == False):
                    sys.stdout.write(',') #Used when formatting a non-compliant PLSim CSV file
            #sys.stdout.write(' ') #add in a space to distinguish between blocks, can be removed as needed, very helpful to turn on in testing and verification
        
        i=i+1 #index the loop counter
    #if (lastdate != row[daterow].strftime("%B %d, %Y")): #reset the check array if we have moved on to a set of states on a new date
        #lastlengthinstate = [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]] #Reset the state check array
        #lastdate = row[daterow].strftime("%B %d, %Y") #if not equal, update the date to the new one.
    if (annotatetransitions == True and plsimcompliant == False):
        sys.stdout.write("Transitions: ")
        sys.stdout.write(str(transitions))   
    transitions=0 #Reset transition counter for the next line
    print() #Newline between rows - makes it formatted properly when there is final readout   
    #print(rowindex) #print the row in the query that is currently being accessed - this is helpful for testing 

#if logicerrorflag == 1:
    #print("WARNING: There may a a double operational state!!  Double check this data!")         
cursor.close()
db.close()  #close DB connection