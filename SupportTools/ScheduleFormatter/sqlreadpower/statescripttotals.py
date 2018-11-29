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
addedfields = True #If true, this will add all fields as in the order of the original dataset to the printout - works only for CSV
blankheaders=False #Use to remove all header info above the text to be used in data of the state info - helpful when quick combining in a text editor

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

runcounter = 0 #Holder for variable that counts the total days in analysis for averaging
dbrecordpost = 0
#Counters for tabulation totals:
#CPU States
day_total_time_ON = [0, 0, 0, 0, 0, 0, 0]
day_total_time_ALLNOTON = [0, 0, 0, 0, 0, 0, 0]
day_total_time_SLEEP = [0, 0, 0, 0, 0, 0, 0]
day_total_time_OFF = [0, 0, 0, 0, 0, 0, 0]
day_total_time_CPUUnknown = [0, 0, 0, 0, 0, 0, 0]

#User States
day_total_Time_Idle = [0, 0, 0, 0, 0, 0, 0]
day_total_Time_ALLNOTActive = [0, 0, 0, 0, 0, 0, 0]
day_Total_Time_Active = [0, 0, 0, 0, 0, 0, 0]
day_Total_Time_UserUnknown= [0, 0, 0, 0, 0, 0, 0]


#Sum Totals
day_Total_Time_AllCPUStates = [0, 0, 0, 0, 0, 0, 0]
day_Total_Time_AllUSERStates = [0, 0, 0, 0, 0, 0, 0]

#collect and display unique states in the query
subjecttallylist = [] #total list of states found
statetallylist = [] #total list of states found
datetallylist = []  #total list of dates found


subjectlist = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118]

##Program Functions
def query_updatevalue(key_to_find, definition):
    for key in query_modifications.keys():
        if key == key_to_find:
           query_modifications[key] = definition

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
    
    

def pushsummarytodb(generatetable, table_name, subject_identifier, desktop_type, MPID, State, Unit, Total_Study_Days, valMonday, valTuesday, valWednesday, valThursday, valFriday, valSaturday, valSunday, State_Weekend_Day_Avg, State_Weekday_Day_Avg, State_Total_Day_Avg):
    entryData = []
    if (generatetable == True):
        # Sample table create sequence 
        #cursor.execute("CREATE TABLE `statesummary` ( `subject_identifier` tinyint(4) DEFAULT NULL, `desktop_type` varchar(5) COLLATE utf8mb4_unicode_ci DEFAULT '', `MPID` tinyint(4) DEFAULT NULL, `State` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT '', `Unit` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT '', `Total_Study_Days` tinyint(4) DEFAULT NULL, `Monday` float DEFAULT NULL, `Tuesday` float DEFAULT NULL, `Wednesday` float DEFAULT NULL, `Thursday` float DEFAULT NULL, `Friday` float DEFAULT NULL, `Saturday` float DEFAULT NULL, `Sunday` float DEFAULT NULL, `State_Weekend_Day_Avg` float DEFAULT NULL, `State_Weekday_Day_Avg` float DEFAULT NULL, `State_Total_Day_Avg` float DEFAULT NULL, `update_time` datetime DEFAULT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
                print("Not Fully implemented: nothing to see here")
      
    #Assemble array to insert into DB
    entryData.append (subject_identifier)
    entryData.append (desktop_type)
    entryData.append (MPID)
    entryData.append (State)
    entryData.append (Unit)
    entryData.append (Total_Study_Days)
    entryData.append (valMonday)
    entryData.append (valTuesday)
    entryData.append (valWednesday)
    entryData.append (valThursday)
    entryData.append (valFriday)
    entryData.append (valSaturday)
    entryData.append (valSunday)
    entryData.append (State_Weekend_Day_Avg)
    entryData.append (State_Weekday_Day_Avg)
    entryData.append (State_Total_Day_Avg)
    entryData.append (str(datetime.now()))
    #print (str(entryData)) #print out contents of array to enter - comment out when not debug
    #Insert the array by element into the DB
    cursor.execute('''INSERT IGNORE INTO %s (subject_identifier, desktop_type, MPID, State, Unit, Total_Study_Days, Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday, State_Weekend_Day_Avg, State_Weekday_Day_Avg, State_Total_Day_Avg, update_time) VALUES (%%s, %%s, %%s, %%s, %%s, %%s, %%s, %%s, %%s, %%s, %%s, %%s, %%s, %%s, %%s, %%s, %%s)''' % table_name, (entryData))
    db.commit()
    #print ("Records posted to DB - Total this session:")
    global dbrecordpost  #need to make a reference to this global variable
    dbrecordpost=dbrecordpost+1
    #print(dbrecordpost)  #comment out when not debug

#++++++++++++++++End of Functions+++++++++++++++++++++

# Open database connection
db = mysql.connector.connect(host="xxxxx.calit2.uci.edu",    # host
                     user="xxxxxxx",         # username
                     passwd="xxxxxxxx",  # password
                     db="VerdiemStudy")        # DBName

cursor = db.cursor() # Cursor object for database query

query = ("SELECT * FROM DATA "
         "WHERE subject_identifier = %(s_ID)s AND (date BETWEEN %(start_DATE)s AND %(end_DATE)s)") #base query

#Query for device states
query_modifications= {'s_ID': 1,'start_DATE': "2014-01-01",'end_DATE': "2014-12-31"} #query records updated by defined variables in dictionary, for device, start and end dates - alternatively use this style for datetime hire_start = datetime.date(1999, 1, 1), for date time printout: #for (first_name, last_name, hire_date) in cursor: print("{}, {} was hired on {:%d %b %Y}".format(last_name, first_name, hire_date))

for q, valuesubject in enumerate(subjectlist):
    query_updatevalue('s_ID', (q+1))  #add 1 because q starts at index 0 add 1 because q starts at index 0 - this is driven by the list and automatically entered by the for loop
    print(query_modifications)
    
    cursor.execute(query, query_modifications) #Process query with variable modifications
    queryreturn = cursor.fetchall() #Fetch all rows with defined query for first state
    
    
    for rowindex, row in enumerate(queryreturn): #go thru query and generate a full list of states from the dataset
        statetallylist.append(row[stateposition])
        datetallylist.append(row[daterow])
        subjecttallylist.append(row[subjectrow])
    
    #keep a record of the last state to verify that there are no logic conflicts
    #lastlengthinstate = [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]]
    logicerrorflag = 0 #identify if there is a logic check error - reset before check, define as zero
    lastdate= "" # Holder for the last date object used
    
    
    if (blankheaders == False):
        uniqueinlist(subjecttallylist,"SUBJECT" ,"Research Subject", False) #use the function defined above
        uniqueinlist(statetallylist, "STATES","Device States", False) #use the function defined above
        uniqueinlist(datetallylist,"DATE" ,"Observation Dates", True) #use the function defined above
    
    
    
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
            for x in range(0, (totalperiods*periodlength)): #96 sets of 15 minute periods for all minutes in a 24 hour period
                timeholder = datetime.today() #initialize datetimeobject
                timeholder = (datetime.combine(date.today(), time(0,0,0)) + timedelta(minutes=1*x))
                if(elapsedminortime==False):
                    sys.stdout.write(datetime.strftime(timeholder, '%H:%M:%S'))   
                else:
                    sys.stdout.write(str(x))
                if ((x<(totalperiods*periodlength)-1)): #suppress final comma
                    sys.stdout.write(",")
            print () #print newline after the header row is finished
    if (blankheaders==False):
        if (plsimcompliant == False and addedfields == True):    
            sys.stdout.write("record_id,subject_id,desktop_type,MPID, device, status, int_record, date, day_of_week,")
            for x in range(0, (totalperiods*periodlength)): #96 sets of 15 minute periods for all minutes in a 24 hour period
                timeholder = datetime.today() #initialize datetimeobject
                timeholder = (datetime.combine(date.today(), time(0,0,0)) + timedelta(minutes=1*x))
                if(elapsedminortime==False):
                    sys.stdout.write(datetime.strftime(timeholder, '%H:%M:%S'))   
                else:
                    sys.stdout.write(str(x))
                if ((x<(totalperiods*periodlength)-1)): #suppress final comma
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
        for x in range(periodstartcolumn, periodstartcolumn+totalperiods): #page thru each of the data columns per the defined start and total number of these
            print (x)
            lengthinstate = int(row[x])  #This is used to read the value at the index each period: total the time active in the column
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
                     
                    sys.stdout.write('1') #print out all rows for inspection
                    if (plsimcompliant == False):
                        sys.stdout.write(',') #Used when formatting a non-compliant PLSim CSV file
                #sys.stdout.write(' ') #add in a space to distinguish between blocks, can be removed as needed, very helpful to turn on in testing and verification
            
            #Tablulate State Time per day - CPU States
            #ON State, (Note: idle+active)
            if ("On" in row[stateposition] and "CPU" in row[devicerow] and "Sunday" in row[day_of_weekrow]):
                day_total_time_ON [0] = day_total_time_ON [0] + int(row[x])
            
            if ("On" in row[stateposition] and "CPU" in row[devicerow] and "Monday" in row[day_of_weekrow]):
                day_total_time_ON [1] = day_total_time_ON [1] + int(row[x])
                
            if ("On" in row[stateposition] and "CPU" in row[devicerow] and "Tuesday" in row[day_of_weekrow]):
                day_total_time_ON [2] = day_total_time_ON [2] + int(row[x])
        
            if ("On" in row[stateposition] and "CPU" in row[devicerow] and "Wednesday" in row[day_of_weekrow]):
                day_total_time_ON [3] = day_total_time_ON [3] + int(row[x])
                
            if ("On" in row[stateposition] and "CPU" in row[devicerow] and "Thursday" in row[day_of_weekrow]):
                day_total_time_ON [4] = day_total_time_ON [4] + int(row[x])
                
            if ("On" in row[stateposition] and "CPU" in row[devicerow] and "Friday" in row[day_of_weekrow]):
                day_total_time_ON [5] = day_total_time_ON [5] + int(row[x])
                
            if ("On" in row[stateposition] and "CPU" in row[devicerow] and "Saturday" in row[day_of_weekrow]):
                day_total_time_ON [6] = day_total_time_ON [6] + int(row[x])
                
            #OFF State
            if ("Off" in row[stateposition] and "CPU" in row[devicerow] and "Sunday" in row[day_of_weekrow]):
                day_total_time_OFF [0] = day_total_time_OFF [0] + int(row[x])
            
            if ("Off" in row[stateposition] and "CPU" in row[devicerow] and "Monday" in row[day_of_weekrow]):
                day_total_time_OFF [1] = day_total_time_OFF [1] + int(row[x])
                
            if ("Off" in row[stateposition] and "CPU" in row[devicerow] and "Tuesday" in row[day_of_weekrow]):
                day_total_time_OFF [2] = day_total_time_OFF [2] + int(row[x])
        
            if ("Off" in row[stateposition] and "CPU" in row[devicerow] and "Wednesday" in row[day_of_weekrow]):
                day_total_time_OFF [3] = day_total_time_OFF [3] + int(row[x])
                
            if ("Off" in row[stateposition] and "CPU" in row[devicerow] and "Thursday" in row[day_of_weekrow]):
                day_total_time_OFF [4] = day_total_time_OFF [4] + int(row[x])
                
            if ("Off" in row[stateposition] and "CPU" in row[devicerow] and "Friday" in row[day_of_weekrow]):
                day_total_time_OFF [5] = day_total_time_OFF [5] + int(row[x])
                
            if ("Off" in row[stateposition] and "CPU" in row[devicerow] and "Saturday" in row[day_of_weekrow]):
                day_total_time_OFF [6] = day_total_time_OFF [6] + int(row[x])
                
            #Sleep State
            if ("Sleep" in row[stateposition] and "CPU" in row[devicerow] and "Sunday" in row[day_of_weekrow]):
                day_total_time_SLEEP [0] = day_total_time_SLEEP [0] + int(row[x])
            
            if ("Sleep" in row[stateposition] and "CPU" in row[devicerow] and "Monday" in row[day_of_weekrow]):
                day_total_time_SLEEP [1] = day_total_time_SLEEP [1] + int(row[x])
                
            if ("Sleep" in row[stateposition] and "CPU" in row[devicerow] and "Tuesday" in row[day_of_weekrow]):
                day_total_time_SLEEP [2] = day_total_time_SLEEP [2] + int(row[x])
        
            if ("Sleep" in row[stateposition] and "CPU" in row[devicerow] and "Wednesday" in row[day_of_weekrow]):
                day_total_time_SLEEP [3] = day_total_time_SLEEP [3] + int(row[x])
                
            if ("Sleep" in row[stateposition] and "CPU" in row[devicerow] and "Thursday" in row[day_of_weekrow]):
                day_total_time_SLEEP [4] = day_total_time_SLEEP [4] + int(row[x])
                
            if ("Sleep" in row[stateposition] and "CPU" in row[devicerow] and "Friday" in row[day_of_weekrow]):
                day_total_time_SLEEP [5] = day_total_time_SLEEP [5] + int(row[x])
                
            if ("Sleep" in row[stateposition] and "CPU" in row[devicerow] and "Saturday" in row[day_of_weekrow]):
                day_total_time_SLEEP [6] = day_total_time_SLEEP [6] + int(row[x])
             
             
            #Unknown State
            if ("Unknown" in row[stateposition] and "CPU" in row[devicerow] and "Sunday" in row[day_of_weekrow]):
                day_total_time_CPUUnknown [0] = day_total_time_CPUUnknown [0] + int(row[x])
            
            if ("Unknown" in row[stateposition] and "CPU" in row[devicerow] and "Monday" in row[day_of_weekrow]):
                day_total_time_CPUUnknown [1] = day_total_time_CPUUnknown [1] + int(row[x])
                
            if ("Unknown" in row[stateposition] and "CPU" in row[devicerow] and "Tuesday" in row[day_of_weekrow]):
                day_total_time_CPUUnknown [2] = day_total_time_CPUUnknown [2] + int(row[x])
        
            if ("Unknown" in row[stateposition] and "CPU" in row[devicerow] and "Wednesday" in row[day_of_weekrow]):
                day_total_time_CPUUnknown [3] = day_total_time_CPUUnknown [3] + int(row[x])
                
            if ("Unknown" in row[stateposition] and "CPU" in row[devicerow] and "Thursday" in row[day_of_weekrow]):
                day_total_time_CPUUnknown [4] = day_total_time_CPUUnknown [4] + int(row[x])
                
            if ("Unknown" in row[stateposition] and "CPU" in row[devicerow] and "Friday" in row[day_of_weekrow]):
                day_total_time_CPUUnknown [5] = day_total_time_CPUUnknown [5] + int(row[x])
                
            if ("Unknown" in row[stateposition] and "CPU" in row[devicerow] and "Saturday" in row[day_of_weekrow]):
                day_total_time_CPUUnknown [6] = day_total_time_CPUUnknown [6] + int(row[x])
             
            #Tabulate all CPU States
            if ("CPU" in row[devicerow] and "Sunday" in row[day_of_weekrow]):
                day_Total_Time_AllCPUStates [0] = day_Total_Time_AllCPUStates [0] + int(row[x])
                
            if ("CPU" in row[devicerow] and "Monday" in row[day_of_weekrow]):
                day_Total_Time_AllCPUStates [1] = day_Total_Time_AllCPUStates [1] + int(row[x])
                
            if ("CPU" in row[devicerow] and "Tuesday" in row[day_of_weekrow]):
                day_Total_Time_AllCPUStates [2] = day_Total_Time_AllCPUStates [2] + int(row[x])
        
            if ("CPU" in row[devicerow] and "Wednesday" in row[day_of_weekrow]):
                day_Total_Time_AllCPUStates [3] = day_Total_Time_AllCPUStates [3] + int(row[x])
                
            if ("CPU" in row[devicerow] and "Thursday" in row[day_of_weekrow]):
                day_Total_Time_AllCPUStates [4] = day_Total_Time_AllCPUStates [4] + int(row[x])
                
            if ("CPU" in row[devicerow] and "Friday" in row[day_of_weekrow]):
                day_Total_Time_AllCPUStates [5] = day_Total_Time_AllCPUStates [5] + int(row[x])
                
            if ("CPU" in row[devicerow] and "Saturday" in row[day_of_weekrow]):
                day_Total_Time_AllCPUStates [6] = day_Total_Time_AllCPUStates [6] + int(row[x])
            
            
            #Tablulate State Time per day - User States
                   
            #Active State        
            if ("Active" in row[stateposition] and "User" in row[devicerow] and "Sunday" in row[day_of_weekrow]):
                day_Total_Time_Active [0] = day_Total_Time_Active [0] + int(row[x])
            
            if ("Active" in row[stateposition] and "User" in row[devicerow] and "Monday" in row[day_of_weekrow]):
                day_Total_Time_Active [1] = day_Total_Time_Active [1] + int(row[x])
                
            if ("Active" in row[stateposition] and "User" in row[devicerow] and "Tuesday" in row[day_of_weekrow]):
                day_Total_Time_Active [2] = day_Total_Time_Active [2] + int(row[x])
        
            if ("Active" in row[stateposition] and "User" in row[devicerow] and "Wednesday" in row[day_of_weekrow]):
                day_Total_Time_Active [3] = day_Total_Time_Active [3] + int(row[x])
                
            if ("Active" in row[stateposition] and "User" in row[devicerow] and "Thursday" in row[day_of_weekrow]):
                day_Total_Time_Active [4] = day_Total_Time_Active [4] + int(row[x])
                
            if ("Active" in row[stateposition] and "User" in row[devicerow] and "Friday" in row[day_of_weekrow]):
                day_Total_Time_Active [5] = day_Total_Time_Active [5] + int(row[x])
                
            if ("Active" in row[stateposition] and "User" in row[devicerow] and "Saturday" in row[day_of_weekrow]):
                day_Total_Time_Active [6] = day_Total_Time_Active [6] + int(row[x])
                
                
            #Idle (Inactive) State        
            if ("Idle" in row[stateposition] and "User" in row[devicerow] and "Sunday" in row[day_of_weekrow]):
                day_total_Time_Idle [0] = day_total_Time_Idle [0] + int(row[x])
            
            if ("Idle" in row[stateposition] and "User" in row[devicerow] and "Monday" in row[day_of_weekrow]):
                day_total_Time_Idle [1] = day_total_Time_Idle [1] + int(row[x])
                
            if ("Idle" in row[stateposition] and "User" in row[devicerow] and "Tuesday" in row[day_of_weekrow]):
                day_total_Time_Idle [2] = day_total_Time_Idle [2] + int(row[x])
        
            if ("Idle" in row[stateposition] and "User" in row[devicerow] and "Wednesday" in row[day_of_weekrow]):
                day_total_Time_Idle [3] = day_total_Time_Idle [3] + int(row[x])
                
            if ("Idle" in row[stateposition] and "User" in row[devicerow] and "Thursday" in row[day_of_weekrow]):
                day_total_Time_Idle [4] = day_total_Time_Idle [4] + int(row[x])
                
            if ("Idle" in row[stateposition] and "User" in row[devicerow] and "Friday" in row[day_of_weekrow]):
                day_total_Time_Idle [5] = day_total_Time_Idle [5] + int(row[x])
                
            if ("Idle" in row[stateposition] and "User" in row[devicerow] and "Saturday" in row[day_of_weekrow]):
                day_total_Time_Idle [6] = day_total_Time_Idle [6] + int(row[x]) 
                
            #Unknown State
            if ("Unknown" in row[stateposition] and "User" in row[devicerow] and "Sunday" in row[day_of_weekrow]):
                day_Total_Time_UserUnknown [0] = day_Total_Time_UserUnknown [0] + int(row[x])
            
            if ("Unknown" in row[stateposition] and "User" in row[devicerow] and "Monday" in row[day_of_weekrow]):
                day_Total_Time_UserUnknown [1] = day_Total_Time_UserUnknown [1] + int(row[x])
                
            if ("Unknown" in row[stateposition] and "User" in row[devicerow] and "Tuesday" in row[day_of_weekrow]):
                day_Total_Time_UserUnknown [2] = day_Total_Time_UserUnknown [2] + int(row[x])
        
            if ("Unknown" in row[stateposition] and "User" in row[devicerow] and "Wednesday" in row[day_of_weekrow]):
                day_Total_Time_UserUnknown [3] = day_Total_Time_UserUnknown [3] + int(row[x])
                
            if ("Unknown" in row[stateposition] and "User" in row[devicerow] and "Thursday" in row[day_of_weekrow]):
                day_Total_Time_UserUnknown [4] = day_Total_Time_UserUnknown [4] + int(row[x])
                
            if ("Unknown" in row[stateposition] and "User" in row[devicerow] and "Friday" in row[day_of_weekrow]):
                day_Total_Time_UserUnknown [5] = day_Total_Time_UserUnknown [5] + int(row[x])
                
            if ("Unknown" in row[stateposition] and "User" in row[devicerow] and "Saturday" in row[day_of_weekrow]):
                day_Total_Time_UserUnknown [6] = day_Total_Time_UserUnknown [6] + int(row[x])
             
             
            #Tabulate all User States
            if ("User" in row[devicerow] and "Sunday" in row[day_of_weekrow]):
                day_Total_Time_AllUSERStates [0] = day_Total_Time_AllUSERStates [0] + int(row[x])
                
            if ("User" in row[devicerow] and "Monday" in row[day_of_weekrow]):
                day_Total_Time_AllUSERStates [1] = day_Total_Time_AllUSERStates [1] + int(row[x])
                
            if ("User" in row[devicerow] and "Tuesday" in row[day_of_weekrow]):
                day_Total_Time_AllUSERStates [2] = day_Total_Time_AllUSERStates [2] + int(row[x])
        
            if ("User" in row[devicerow] and "Wednesday" in row[day_of_weekrow]):
                day_Total_Time_AllUSERStates [3] = day_Total_Time_AllUSERStates [3] + int(row[x])
                
            if ("User" in row[devicerow] and "Thursday" in row[day_of_weekrow]):
                day_Total_Time_AllUSERStates [4] = day_Total_Time_AllUSERStates [4] + int(row[x])
                
            if ("User" in row[devicerow] and "Friday" in row[day_of_weekrow]):
                day_Total_Time_AllUSERStates [5] = day_Total_Time_AllUSERStates [5] + int(row[x])
                
            if ("User" in row[devicerow] and "Saturday" in row[day_of_weekrow]):
                day_Total_Time_AllUSERStates [6] = day_Total_Time_AllUSERStates [6] + int(row[x])
            
    
            
            i=i+1 #index the loop counter
        #if (lastdate != row[daterow].strftime("%B %d, %Y")): #reset the check array if we have moved on to a set of states on a new date
            #lastlengthinstate = [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]] #Reset the state check array
            #lastdate = row[daterow].strftime("%B %d, %Y") #if not equal, update the date to the new one.
        runcounter = runcounter + 1
        print() #Newline between rows - makes it formatted properly when there is final readout   
        #print(rowindex) #print the row in the query that is currently being accessed - this is helpful for testing 
    
    #if logicerrorflag == 1:
        #print("WARNING: There may a a double operational state!!  Double check this data!")         
    print()
    print()
    print("===========================================")
    print("Overall State Summary:")
    sys.stdout.write("Day of the week total (min) for ALL CPU states [Su, Mo, Tu, We, Th, Fr, Sa]:")
    print(day_Total_Time_AllCPUStates)
    sys.stdout.write("Day of the week total (min) for ALL User states [Su, Mo, Tu, We, Th, Fr, Sa]:")
    print(day_Total_Time_AllUSERStates)
    sys.stdout.write("Total days of the study for this subject: ")
    print (len(datetallylist))
    
    print()
    print("CPU States")
    print("********************")
    print("ON State Summary:")
    sys.stdout.write("Day of the week total (min) for ON state [Su, Mo, Tu, We, Th, Fr, Sa]: ")
    print(day_total_time_ON)
    
    pushsummarytodb(False, "statesummary", str(queryreturn[1][1]), str(queryreturn[1][2]), str(queryreturn[1][MPIDrow]), "On", "TotalStyMinAllDays", str(len(datetallylist)), str(day_total_time_ON[1]), str(day_total_time_ON[2]), str(day_total_time_ON[3]), str(day_total_time_ON[4]), str(day_total_time_ON[5]), str(day_total_time_ON[6]), str(day_total_time_ON[0]), -1, -1, -1)
    
    sys.stdout.write("Day of the week (per day) for ON state [Su, Mo, Tu, We, Th, Fr, Sa]: ")
    summary1 = [day_total_time_ON[index] / len(datetallylist) for index, x in enumerate(day_Total_Time_AllCPUStates)]
    print(summary1)
    
    pushsummarytodb(False, "statesummary", str(queryreturn[1][subjectrow]), str(queryreturn[1][desktop_typerow]), str(queryreturn[1][MPIDrow]), "On", "MinPerDay", str(len(datetallylist)), str(summary1[1]), str(summary1[2]), str(summary1[3]), str(summary1[4]), str(summary1[5]), str(summary1[6]), str(summary1[0]), -1, -1, -1)
    
    sys.stdout.write("Day of the week % for ON state [Su, Mo, Tu, We, Th, Fr, Sa]:")
    summary2 = [day_total_time_ON[index] / day_Total_Time_AllCPUStates[index] for index, x in enumerate(day_Total_Time_AllCPUStates)]
    print(summary2)
    
    weekenddaytotal = (day_Total_Time_AllCPUStates[0]+day_Total_Time_AllCPUStates[6])/2
    weekdaytotal = (day_Total_Time_AllCPUStates[1]+day_Total_Time_AllCPUStates[2]+day_Total_Time_AllCPUStates[3]+day_Total_Time_AllCPUStates[4]+day_Total_Time_AllCPUStates[5])/5
    weekenddayavg = (day_total_time_ON[0]+day_total_time_ON[6])/2
    weekdayavg = (day_total_time_ON[1]+day_total_time_ON[2]+day_total_time_ON[3]+day_total_time_ON[4]+day_total_time_ON[5])/5
    sys.stdout.write("State Weekend Day Avg %: ")
    print(weekenddayavg/weekenddaytotal)
    sys.stdout.write("State Weekday Day Avg %: ")
    print(weekdayavg/weekdaytotal)
    sys.stdout.write("State Total Day Avg %: ")
    print((weekdayavg*5+weekenddayavg*2)/(weekdaytotal*5+weekenddaytotal*2))
    
    pushsummarytodb(False, "statesummary", str(queryreturn[1][1]), str(queryreturn[1][2]), str(queryreturn[1][MPIDrow]), "On", "State%PerDay", str(len(datetallylist)), str(summary2[1]), str(summary2[2]), str(summary2[3]), str(summary2[4]), str(summary2[5]), str(summary2[6]), str(summary2[0]), str(weekenddayavg/weekenddaytotal), str(weekdayavg/weekdaytotal), str((weekdayavg*5+weekenddayavg*2)/(weekdaytotal*5+weekenddaytotal*2)))
    
    
    print()
    print("********************")
    print("Sleep State Summary:")
    sys.stdout.write("Day of the week total (min) for Sleep state [Su, Mo, Tu, We, Th, Fr, Sa]: ")
    print(day_total_time_SLEEP)
    
    pushsummarytodb(False, "statesummary", str(queryreturn[1][1]), str(queryreturn[1][2]), str(queryreturn[1][MPIDrow]), "Sleep", "TotalStyMinAllDays", str(len(datetallylist)), str(day_total_time_SLEEP[1]), str(day_total_time_SLEEP[2]), str(day_total_time_SLEEP[3]), str(day_total_time_SLEEP[4]), str(day_total_time_SLEEP[5]), str(day_total_time_SLEEP[6]), str(day_total_time_SLEEP[0]), -1, -1, -1)
    
    sys.stdout.write("Day of the week (per day) for Sleep state [Su, Mo, Tu, We, Th, Fr, Sa]: ")
    summary1 = [day_total_time_SLEEP[index] / len(datetallylist) for index, x in enumerate(day_Total_Time_AllCPUStates)]
    pushsummarytodb(False, "statesummary", str(queryreturn[1][subjectrow]), str(queryreturn[1][desktop_typerow]), str(queryreturn[1][MPIDrow]), "Sleep", "MinPerDay", str(len(datetallylist)), str(summary1[1]), str(summary1[2]), str(summary1[3]), str(summary1[4]), str(summary1[5]), str(summary1[6]), str(summary1[0]), -1, -1, -1)
    print(summary1)
    
    summary2 = [day_total_time_SLEEP[index] / day_Total_Time_AllCPUStates[index] for index, x in enumerate(day_Total_Time_AllCPUStates)]
    sys.stdout.write("Day of the week % for Sleep state [Su, Mo, Tu, We, Th, Fr, Sa]:")
    
    print(summary2)
    weekenddaytotal = (day_Total_Time_AllCPUStates[0]+day_Total_Time_AllCPUStates[6])/2
    weekdaytotal = (day_Total_Time_AllCPUStates[1]+day_Total_Time_AllCPUStates[2]+day_Total_Time_AllCPUStates[3]+day_Total_Time_AllCPUStates[4]+day_Total_Time_AllCPUStates[5])/5
    weekenddayavg = (day_total_time_SLEEP[0]+day_total_time_SLEEP[6])/2
    weekdayavg = (day_total_time_SLEEP[1]+day_total_time_SLEEP[2]+day_total_time_SLEEP[3]+day_total_time_SLEEP[4]+day_total_time_SLEEP[5])/5
    sys.stdout.write("State Weekend Day Avg %: ")
    print(weekenddayavg/weekenddaytotal)
    sys.stdout.write("State Weekday Day Avg %: ")
    print(weekdayavg/weekdaytotal)
    sys.stdout.write("State Total Day Avg %: ")
    print((weekdayavg*5+weekenddayavg*2)/(weekdaytotal*5+weekenddaytotal*2))
    
    pushsummarytodb(False, "statesummary", str(queryreturn[1][1]), str(queryreturn[1][2]), str(queryreturn[1][MPIDrow]), "Sleep", "State%PerDay", str(len(datetallylist)), str(summary2[1]), str(summary2[2]), str(summary2[3]), str(summary2[4]), str(summary2[5]), str(summary2[6]), str(summary2[0]), str(weekenddayavg/weekenddaytotal), str(weekdayavg/weekdaytotal), str((weekdayavg*5+weekenddayavg*2)/(weekdaytotal*5+weekenddaytotal*2)))
    
    
    print()
    print("********************")
    print("Off State Summary:")
    sys.stdout.write("Day of the week total (min) for OFF state [Su, Mo, Tu, We, Th, Fr, Sa]: ")
    print(day_total_time_OFF)
    
    pushsummarytodb(False, "statesummary", str(queryreturn[1][1]), str(queryreturn[1][2]), str(queryreturn[1][MPIDrow]), "Off", "TotalStyMinAllDays", str(len(datetallylist)), str(day_total_time_OFF[1]), str(day_total_time_OFF[2]), str(day_total_time_OFF[3]), str(day_total_time_OFF[4]), str(day_total_time_OFF[5]), str(day_total_time_OFF[6]), str(day_total_time_OFF[0]), -1, -1, -1)
    
    sys.stdout.write("Day of the week (per day) for OFF state [Su, Mo, Tu, We, Th, Fr, Sa]: ")
    summary1 = [day_total_time_OFF[index] / len(datetallylist) for index, x in enumerate(day_Total_Time_AllCPUStates)]
    pushsummarytodb(False, "statesummary", str(queryreturn[1][subjectrow]), str(queryreturn[1][desktop_typerow]), str(queryreturn[1][MPIDrow]), "Off", "MinPerDay", str(len(datetallylist)), str(summary1[1]), str(summary1[2]), str(summary1[3]), str(summary1[4]), str(summary1[5]), str(summary1[6]), str(summary1[0]), -1, -1, -1)
    print(summary1)
    
    sys.stdout.write("Day of the week % for OFF state [Su, Mo, Tu, We, Th, Fr, Sa]:")
    summary2 = [day_total_time_OFF[index] / day_Total_Time_AllCPUStates[index] for index, x in enumerate(day_Total_Time_AllCPUStates)]
    print(summary2)
    
    weekenddaytotal = (day_Total_Time_AllCPUStates[0]+day_Total_Time_AllCPUStates[6])/2
    weekdaytotal = (day_Total_Time_AllCPUStates[1]+day_Total_Time_AllCPUStates[2]+day_Total_Time_AllCPUStates[3]+day_Total_Time_AllCPUStates[4]+day_Total_Time_AllCPUStates[5])/5
    weekenddayavg = (day_total_time_OFF[0]+day_total_time_OFF[6])/2
    weekdayavg = (day_total_time_OFF[1]+day_total_time_OFF[2]+day_total_time_OFF[3]+day_total_time_OFF[4]+day_total_time_OFF[5])/5
    sys.stdout.write("State Weekend Day Avg %: ")
    print(weekenddayavg/weekenddaytotal)
    sys.stdout.write("State Weekday Day Avg %: ")
    print(weekdayavg/weekdaytotal)
    sys.stdout.write("State Total Day Avg %: ")
    print((weekdayavg*5+weekenddayavg*2)/(weekdaytotal*5+weekenddaytotal*2))
    
    pushsummarytodb(False, "statesummary", str(queryreturn[1][1]), str(queryreturn[1][2]), str(queryreturn[1][MPIDrow]), "Off", "State%PerDay", str(len(datetallylist)), str(summary2[1]), str(summary2[2]), str(summary2[3]), str(summary2[4]), str(summary2[5]), str(summary2[6]), str(summary2[0]), str(weekenddayavg/weekenddaytotal), str(weekdayavg/weekdaytotal), str((weekdayavg*5+weekenddayavg*2)/(weekdaytotal*5+weekenddaytotal*2)))
    
    print()
    print("********************")
    print("CPU Unknown State Summary:")
    sys.stdout.write("Day of the week total (min) for Unknown state [Su, Mo, Tu, We, Th, Fr, Sa]: ")
    print(day_total_time_CPUUnknown)
    
    pushsummarytodb(False, "statesummary", str(queryreturn[1][1]), str(queryreturn[1][2]), str(queryreturn[1][MPIDrow]), "CPUUnknown", "TotalStyMinAllDays", str(len(datetallylist)), str(day_total_time_CPUUnknown[1]), str(day_total_time_CPUUnknown[2]), str(day_total_time_CPUUnknown[3]), str(day_total_time_CPUUnknown[4]), str(day_total_time_CPUUnknown[5]), str(day_total_time_CPUUnknown[6]), str(day_total_time_CPUUnknown[0]), -1, -1, -1)
    
    sys.stdout.write("Day of the week (per day) for Unknown state [Su, Mo, Tu, We, Th, Fr, Sa]: ")
    summary1 = [day_total_time_CPUUnknown[index] / len(datetallylist) for index, x in enumerate(day_Total_Time_AllCPUStates)]
    pushsummarytodb(False, "statesummary", str(queryreturn[1][subjectrow]), str(queryreturn[1][desktop_typerow]), str(queryreturn[1][MPIDrow]), "CPUUnknown", "MinPerDay", str(len(datetallylist)), str(summary1[1]), str(summary1[2]), str(summary1[3]), str(summary1[4]), str(summary1[5]), str(summary1[6]), str(summary1[0]), -1, -1, -1)
    print(summary1)
    
    sys.stdout.write("Day of the week % for Unknown state [Su, Mo, Tu, We, Th, Fr, Sa]:")
    summary2 = [day_total_time_CPUUnknown[index] / day_Total_Time_AllCPUStates[index] for index, x in enumerate(day_Total_Time_AllCPUStates)]
    print(summary2)
    weekenddaytotal = (day_Total_Time_AllCPUStates[0]+day_Total_Time_AllCPUStates[6])/2
    weekdaytotal = (day_Total_Time_AllCPUStates[1]+day_Total_Time_AllCPUStates[2]+day_Total_Time_AllCPUStates[3]+day_Total_Time_AllCPUStates[4]+day_Total_Time_AllCPUStates[5])/5
    weekenddayavg = (day_total_time_CPUUnknown[0]+day_total_time_CPUUnknown[6])/2
    weekdayavg = (day_total_time_CPUUnknown[1]+day_total_time_CPUUnknown[2]+day_total_time_CPUUnknown[3]+day_total_time_CPUUnknown[4]+day_total_time_CPUUnknown[5])/5
    sys.stdout.write("State Weekend Day Avg %: ")
    print(weekenddayavg/weekenddaytotal)
    sys.stdout.write("State Weekday Day Avg %: ")
    print(weekdayavg/weekdaytotal)
    sys.stdout.write("State Total Day Avg %: ")
    print((weekdayavg*5+weekenddayavg*2)/(weekdaytotal*5+weekenddaytotal*2))
    
    pushsummarytodb(False, "statesummary", str(queryreturn[1][1]), str(queryreturn[1][2]), str(queryreturn[1][MPIDrow]), "CPUUnknown", "State%PerDay", str(len(datetallylist)), str(summary2[1]), str(summary2[2]), str(summary2[3]), str(summary2[4]), str(summary2[5]), str(summary2[6]), str(summary2[0]), str(weekenddayavg/weekenddaytotal), str(weekdayavg/weekdaytotal), str((weekdayavg*5+weekenddayavg*2)/(weekdaytotal*5+weekenddaytotal*2)))
    
    
    print()
    print("User States")
    print("********************")
    print("Active State Summary:")
    sys.stdout.write("Day of the week total (min) for Active state [Su, Mo, Tu, We, Th, Fr, Sa]: ")
    print(day_Total_Time_Active)
    
    pushsummarytodb(False, "statesummary", str(queryreturn[1][1]), str(queryreturn[1][2]), str(queryreturn[1][MPIDrow]), "Active", "TotalStyMinAllDays", str(len(datetallylist)), str(day_Total_Time_Active[1]), str(day_Total_Time_Active[2]), str(day_Total_Time_Active[3]), str(day_Total_Time_Active[4]), str(day_Total_Time_Active[5]), str(day_Total_Time_Active[6]), str(day_Total_Time_Active[0]), -1, -1, -1)
    
    sys.stdout.write("Day of the week (per day) for Active state [Su, Mo, Tu, We, Th, Fr, Sa]: ")
    summary1 = [day_Total_Time_Active[index] / len(datetallylist) for index, x in enumerate(day_Total_Time_AllUSERStates)]
    pushsummarytodb(False, "statesummary", str(queryreturn[1][subjectrow]), str(queryreturn[1][desktop_typerow]), str(queryreturn[1][MPIDrow]), "Active", "MinPerDay", str(len(datetallylist)), str(summary1[1]), str(summary1[2]), str(summary1[3]), str(summary1[4]), str(summary1[5]), str(summary1[6]), str(summary1[0]), -1, -1, -1)
    print(summary1)
    
    sys.stdout.write("Day of the week % for Active state [Su, Mo, Tu, We, Th, Fr, Sa]:")
    summary2 = [day_Total_Time_Active[index] / day_Total_Time_AllUSERStates[index] for index, x in enumerate(day_Total_Time_AllUSERStates)]
    print(summary2)
    
    weekenddaytotal = (day_Total_Time_AllUSERStates[0]+day_Total_Time_AllUSERStates[6])/2
    weekdaytotal = (day_Total_Time_AllUSERStates[1]+day_Total_Time_AllUSERStates[2]+day_Total_Time_AllUSERStates[3]+day_Total_Time_AllUSERStates[4]+day_Total_Time_AllUSERStates[5])/5
    weekenddayavg = (day_Total_Time_Active[0]+day_Total_Time_Active[6])/2
    weekdayavg = (day_Total_Time_Active[1]+day_Total_Time_Active[2]+day_Total_Time_Active[3]+day_Total_Time_Active[4]+day_Total_Time_Active[5])/5
    sys.stdout.write("State Weekend Day Avg %: ")
    print(weekenddayavg/weekenddaytotal)
    sys.stdout.write("State Weekday Day Avg %: ")
    print(weekdayavg/weekdaytotal)
    sys.stdout.write("State Total Day Avg %: ")
    print((weekdayavg*5+weekenddayavg*2)/(weekdaytotal*5+weekenddaytotal*2))
    
    pushsummarytodb(False, "statesummary", str(queryreturn[1][1]), str(queryreturn[1][2]), str(queryreturn[1][MPIDrow]), "Active", "State%PerDay", str(len(datetallylist)), str(summary2[1]), str(summary2[2]), str(summary2[3]), str(summary2[4]), str(summary2[5]), str(summary2[6]), str(summary2[0]), str(weekenddayavg/weekenddaytotal), str(weekdayavg/weekdaytotal), str((weekdayavg*5+weekenddayavg*2)/(weekdaytotal*5+weekenddaytotal*2)))
    
    
    print()
    print("********************")
    print("Idle State Summary:")
    sys.stdout.write("Day of the week total (min) for Idle state [Su, Mo, Tu, We, Th, Fr, Sa]: ")
    print(day_total_Time_Idle)
    
    pushsummarytodb(False, "statesummary", str(queryreturn[1][subjectrow]), str(queryreturn[1][desktop_typerow]), str(queryreturn[1][MPIDrow]), "Idle", "TotalStyMinAllDays", str(len(datetallylist)), str(day_total_Time_Idle[1]), str(day_total_Time_Idle[2]), str(day_total_Time_Idle[3]), str(day_total_Time_Idle[4]), str(day_total_Time_Idle[5]), str(day_total_Time_Idle[6]), str(day_total_Time_Idle[0]), -1, -1, -1)
    sys.stdout.write("Day of the week (per day) for Idle state [Su, Mo, Tu, We, Th, Fr, Sa]: ")
    summary1 = [day_total_Time_Idle[index] / len(datetallylist) for index, x in enumerate(day_Total_Time_AllUSERStates)]
    
    pushsummarytodb(False, "statesummary", str(queryreturn[1][subjectrow]), str(queryreturn[1][desktop_typerow]), str(queryreturn[1][MPIDrow]), "Idle", "MinPerDay", str(len(datetallylist)), str(summary1[1]), str(summary1[2]), str(summary1[3]), str(summary1[4]), str(summary1[5]), str(summary1[6]), str(summary1[0]), -1, -1, -1)
    print(summary1)
    
    sys.stdout.write("Day of the week % for Idle state [Su, Mo, Tu, We, Th, Fr, Sa]:")
    summary2 = [day_total_Time_Idle[index] / day_Total_Time_AllUSERStates[index] for index, x in enumerate(day_Total_Time_AllUSERStates)]
    print(summary2)
    
    weekenddaytotal = (day_Total_Time_AllUSERStates[0]+day_Total_Time_AllUSERStates[6])/2
    weekdaytotal = (day_Total_Time_AllUSERStates[1]+day_Total_Time_AllUSERStates[2]+day_Total_Time_AllUSERStates[3]+day_Total_Time_AllUSERStates[4]+day_Total_Time_AllUSERStates[5])/5
    weekenddayavg = (day_total_Time_Idle[0]+day_total_Time_Idle[6])/2
    weekdayavg = (day_total_Time_Idle[1]+day_total_Time_Idle[2]+day_total_Time_Idle[3]+day_total_Time_Idle[4]+day_total_Time_Idle[5])/5
    sys.stdout.write("State Weekend Day Avg %: ")
    print(weekenddayavg/weekenddaytotal)
    sys.stdout.write("State Weekday Day Avg %: ")
    print(weekdayavg/weekdaytotal)
    sys.stdout.write("State Total Day Avg %: ")
    print((weekdayavg*5+weekenddayavg*2)/(weekdaytotal*5+weekenddaytotal*2))
    
    pushsummarytodb(False, "statesummary", str(queryreturn[1][subjectrow]), str(queryreturn[1][desktop_typerow]), str(queryreturn[1][MPIDrow]), "Idle", "State%PerDay", str(len(datetallylist)), str(summary2[1]), str(summary2[2]), str(summary2[3]), str(summary2[4]), str(summary2[5]), str(summary2[6]), str(summary2[0]), str(weekenddayavg/weekenddaytotal), str(weekdayavg/weekdaytotal), str((weekdayavg*5+weekenddayavg*2)/(weekdaytotal*5+weekenddaytotal*2)))
    
    
    print()
    print("********************")
    print("User Unknown State Summary:")
    sys.stdout.write("Day of the week total (min) for Unknown state [Su, Mo, Tu, We, Th, Fr, Sa]: ")
    print(day_Total_Time_UserUnknown)
    
    pushsummarytodb(False, "statesummary", str(queryreturn[1][subjectrow]), str(queryreturn[1][desktop_typerow]), str(queryreturn[1][MPIDrow]), "UserUnknown", "TotalStyMinAllDays", str(len(datetallylist)), str(day_Total_Time_UserUnknown[1]), str(day_Total_Time_UserUnknown[2]), str(day_Total_Time_UserUnknown[3]), str(day_Total_Time_UserUnknown[4]), str(day_Total_Time_UserUnknown[5]), str(day_Total_Time_UserUnknown[6]), str(day_Total_Time_UserUnknown[0]), -1, -1, -1)
    
    sys.stdout.write("Day of the week (per day) for Unknown state [Su, Mo, Tu, We, Th, Fr, Sa]: ")
    summary1 = [day_Total_Time_UserUnknown[index] / len(datetallylist) for index, x in enumerate(day_Total_Time_AllUSERStates)]
    pushsummarytodb(False, "statesummary", str(queryreturn[1][subjectrow]), str(queryreturn[1][desktop_typerow]), str(queryreturn[1][MPIDrow]), "UserUnknown", "MinPerDay", str(len(datetallylist)), str(summary1[1]), str(summary1[2]), str(summary1[3]), str(summary1[4]), str(summary1[5]), str(summary1[6]), str(summary1[0]), -1, -1, -1)
    print(summary1)
    
    sys.stdout.write("Day of the week % for Unknown state [Su, Mo, Tu, We, Th, Fr, Sa]:")
    summary2 = [day_Total_Time_UserUnknown[index] / day_Total_Time_AllUSERStates[index] for index, x in enumerate(day_Total_Time_AllUSERStates)]
    print(summary2)
    
    weekenddaytotal = (day_Total_Time_AllUSERStates[0]+day_Total_Time_AllUSERStates[6])/2
    weekdaytotal = (day_Total_Time_AllUSERStates[1]+day_Total_Time_AllUSERStates[2]+day_Total_Time_AllUSERStates[3]+day_Total_Time_AllUSERStates[4]+day_Total_Time_AllUSERStates[5])/5
    weekenddayavg = (day_Total_Time_UserUnknown[0]+day_Total_Time_UserUnknown[6])/2
    weekdayavg = (day_Total_Time_UserUnknown[1]+day_Total_Time_UserUnknown[2]+day_Total_Time_UserUnknown[3]+day_Total_Time_UserUnknown[4]+day_Total_Time_UserUnknown[5])/5
    sys.stdout.write("State Weekend Day Avg %: ")
    print(weekenddayavg/weekenddaytotal)
    sys.stdout.write("State Weekday Day Avg %: ")
    print(weekdayavg/weekdaytotal)
    sys.stdout.write("State Total Day Avg %: ")
    print((weekdayavg*5+weekenddayavg*2)/(weekdaytotal*5+weekenddaytotal*2))
    
    pushsummarytodb(False, "statesummary", str(queryreturn[1][subjectrow]), str(queryreturn[1][desktop_typerow]), str(queryreturn[1][MPIDrow]), "UserUnknown", "State%PerDay", str(len(datetallylist)), str(summary2[1]), str(summary2[2]), str(summary2[3]), str(summary2[4]), str(summary2[5]), str(summary2[6]), str(summary2[0]), str(weekenddayavg/weekenddaytotal), str(weekdayavg/weekdaytotal), str((weekdayavg*5+weekenddayavg*2)/(weekdaytotal*5+weekenddaytotal*2)))

print()
print ("Operation Complete")
cursor.close()
db.close()  #close DB connection