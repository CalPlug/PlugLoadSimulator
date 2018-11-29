#Analysis script for Verdiem data from CalPlug 2014 study - Idle Time Reporter using XOR
#Developed by M. Klopfer Sept 11, 2018 - V1.5
#Operation:  This script is a stand-alone processor that takes the Verdiem data and formats it into a style used as a .CSV input into the PLSin program.  This script will not actually output a .CSV file its current state, just format the text in a way that can be quickly formatted into the specific PLSim format.   
            #The script reads from a database/table with the following entries:  record_id    subject_identifier    desktop_type    MPID    device    status    int_record    date    day_of_week P1  P2...[There are 96 entries that correspond to 15 minute periods across the day]

#Dependencies and setup considerations:  This program uses Miniconda/Eclipse in development and is within an Eclipse workshop - it shares identical dependencies as PLSim:  https://github.com/CalPlug/PlugLoadSimulator-PLSim
#Note, if the console is not large enough in Eclipse to display the return, consider the following:  https://stackoverflow.com/questions/2600653/adjusting-eclipse-console-size


import sys
import calendar
from datetime import timedelta, datetime, date, time
from time import mktime
import pyximport; pyximport.install() #pyximport cython accelerator
import mysql.connector
#from distutils.core import setup
#from Cython.Build import cythonize


#Run Options for Output Formatting
elapsedminortime=True #Print headers as time (False) or minutes since 00:00 (True)
writetosummarydb = True #Option allows summary to be written to a summary table in the database
dbrecordpost = 0  #counter for posted records
finaldeltalist =[] #holder for the total collected delta values across all days
periodlength=15  #assume a standard 15 min period length
totalperiods = 96  #total number of columns devoted to the periods
periodstartcolumn = 9 #column which the period info starts in
record_idrow = 0 #position original identifier is in
subjectrow = 1 #Row the subject info is in
desktop_typerow = 2 #position for the desktop type info
MPIDrow = 3 #row MPID info is placed in
devicerow = 4 #Identify row for the device (CPU or USER) that is being reported on 
stateposition = 5 #position of the state/status identifier column
int_recordrow = 6
daterow = 7 #row that date information is placedin
day_of_weekrow = 8 #Day of the Week identifier


#define global variables
resultsreviewcount = 0
idleaverage = 0
perdayidleaverage = 0
minutebaseinday = 1425 #Time base for min in day, Verdiem based periods= 1425, alternatively 1440

subjectlist = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118]

##Program Functions
def query_updatevalue(key_to_find, definition):
    for key in query_modifications.keys():
        if key == key_to_find:
           query_modifications[key] = definition
           
#Used to search for transitions in the dateset to identify timing:
def transitionsearch(inputarray, mask):  #input array used for comparison and a mask of always
    results = []
    resultswithstart= []
    resultswithstartandstop = []
    option1start = ((0,0))
    option2start = ((0,1))   
    updatedoptionend = []  #needs to be a list, converted to tuple later upon insert

    
    deltaidle = []
    deltaactive = []
    deltaactiveOn = []
    deltaactiveOff = []
    deltacombined = []

    results=[(n+1, b) for (n, (a,b)) in enumerate(zip(inputarray,inputarray[1:])) if a!=b]  #Return the point of transition (to the new value) and the prior value to the transition as the function return  
    resultswithstart.extend(results)
    
    if (inputarray[0]==inputarray[1]):  #take care of the 0 case and add it to the array "resultswithstart"
        if (inputarray[0]==0):
            resultswithstart.insert(0, tuple(option1start))
        if (inputarray[0]==1):
            resultswithstart.insert(0, tuple(option2start))
            
    resultswithstartandstop.extend(resultswithstart)
    
    if (inputarray[len(inputarray)-2]==inputarray[len(inputarray)-1]):  #take care of the 0 case 
        if (inputarray[len(inputarray)-1]==1):
            endval=0
            
        if (inputarray[len(inputarray)-1]==0):
            endval=1
            
        updatedoptionend.append(len(inputarray)) #rem-1
        updatedoptionend.append(endval)
        if (len(results)!= 0):
            t= tuple(updatedoptionend)
            resultswithstartandstop.insert((len(inputarray)), t)   #rem-1
           
    for x in range(0, len(resultswithstartandstop)-1):     
        deltacombined.append(resultswithstartandstop[x+1][0] - resultswithstartandstop[x][0])
        if (resultswithstartandstop[x][1] == 1): #count transition to idle and period until activity comes back
            deltaidle.append(resultswithstartandstop[x+1][0] - resultswithstartandstop[x][0])
        if (resultswithstartandstop[x][1] == 0 and mask[resultswithstartandstop[x][0]] == 0):
            deltaactiveOff.append(resultswithstartandstop[x+1][0] - resultswithstartandstop[x][0])
        if (resultswithstartandstop[x][1] == 0):    
            deltaactive.append(resultswithstartandstop[x+1][0] - resultswithstartandstop[x][0])
        if (resultswithstartandstop[x][1] == 0 and mask[resultswithstartandstop[x][0]] == 1):    
            deltaactiveOn.append(resultswithstartandstop[x+1][0] - resultswithstartandstop[x][0])
            
    
   
    return [resultswithstartandstop, deltaidle, deltaactive, deltacombined, deltaactiveOff, deltaactiveOn, results, resultswithstart]

def savingsevaluation(inputarray, timersetting, simulatedPMSetting, PMSimulationOn):
    savingsarray=[]

    newlist=[int(x) for xs in inputarray for x in xs]
    #print(newlist)
    for index in range(0, (len(newlist))):
        if ((PMSimulationOn == True)):  #no negative savings, for PMSimulation - Preconditioner and savings application - this applies a simulated power management to the data.
            if (newlist[index] < simulatedPMSetting): #initial verification of values to prevent negative savings
                if (newlist[index] < timersetting):  #no negative savings
                        savingsval=0
                        savingsarray.append(int(savingsval))
            
                else:
                    savingsval = (newlist[index] - timersetting)
                    savingsarray.append(int(savingsval))
                
        if ((PMSimulationOn == False)):  #no negative savings, for PMSimulation
            if (newlist[index] < timersetting):  #no negative savings
                savingsval=0
                savingsarray.append(int(savingsval))
            
            else:
                savingsval = (newlist[index] - timersetting)
                savingsarray.append(int(savingsval))

    return [savingsarray]
            
def pushsummarytodb(generatetable, table_name, subject_identifier, desktop_type, MPID, summary_idle_percent, delta_computer_W, delta_acessories_W, external_pm_control_min, invervention_setting_min, runtime_saved_min, projected_per_day_savings_kWh, weekday_only_estimate_kwhperyear, all_days_even_estimate_kwhperyear, weekday_and_weekends_estimate_kwhperyear, min_max_estimate_ratio, min_mid_estimate_ratio, mid_max_estimate_ratio):
    entryData = []
    if (generatetable == True):
        # Sample table create sequence 
        #cursor.execute("CREATE TABLE IF NOT EXISTS `summary` (  `subject_identifier` tinyint(4) DEFAULT NULL, `desktop_type` varchar(2) COLLATE utf8mb4_unicode_ci DEFAULT '', `MPID` tinyint(4) DEFAULT NULL, `summary_idle_percent` float DEFAULT NULL, `delta_computer_W` int(11) DEFAULT NULL, `delta_acessories_W` int(11) DEFAULT NULL, `external_pm_control_min` float DEFAULT NULL, `invervention_setting_min` float DEFAULT NULL, `runtime_saved_per_day_min` float DEFAULT NULL, `projected_per_day_savings_kWh` float DEFAULT NULL, `weekday_only_estimate_kwhperyear` float DEFAULT NULL, `all_days_even_estimate_kwhperyear` float DEFAULT NULL, `weekday_and_weekends_estimate_kwhperyear` float DEFAULT NULL, `min_max_estimate_ratio` float DEFAULT NULL, `update_time` datetime DEFAULT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")
        print("Not Fully implemented: nothing to see here")
      
    #Assemble array to insert into DB
    entryData.append (subject_identifier)
    entryData.append (desktop_type)
    entryData.append (MPID)
    entryData.append (summary_idle_percent)
    entryData.append (delta_computer_W)
    entryData.append (delta_acessories_W)
    entryData.append (external_pm_control_min)
    entryData.append (invervention_setting_min)
    entryData.append (runtime_saved_min)
    entryData.append (projected_per_day_savings_kWh)
    entryData.append (weekday_only_estimate_kwhperyear)
    entryData.append (all_days_even_estimate_kwhperyear)
    entryData.append (weekday_and_weekends_estimate_kwhperyear)
    entryData.append (min_max_estimate_ratio)
    entryData.append (min_mid_estimate_ratio)
    entryData.append(mid_max_estimate_ratio)    
    entryData.append (str(datetime.now()))
    print (str(entryData)) #print out contents of array to enter
    #Insert the array by element into the DB
    cursor.execute('''INSERT IGNORE INTO %s (subject_identifier, desktop_type, MPID, summary_idle_percent, delta_computer_W, delta_acessories_W, external_pm_control_min, invervention_setting_min, runtime_saved_per_day_min, projected_per_day_savings_kWh, weekday_only_estimate_kwhperyear, all_days_even_estimate_kwhperyear, weekday_and_weekends_estimate_kwhperyear, min_max_estimate_ratio, min_mid_estimate_ratio, mid_max_estimate_ratio, update_time) VALUES (%%s, %%s, %%s, %%s, %%s, %%s, %%s, %%s, %%s, %%s, %%s, %%s, %%s, %%s, %%s, %%s, %%s)''' % table_name, (entryData))
    db.commit()
    print ("Records posted to DB - Total this session:")
    global dbrecordpost  #need to make a reference to this global variable
    dbrecordpost=dbrecordpost+1
    print(dbrecordpost)
    
def savingsreporting(inputrange, analysisvalues, averagebase, standbycomputerwatt, activecomputerwatt, standbyaccessorieswatt, activeaccessorieswatt, accessorycontrol, simPMsavingsval, simPMsavingsOn, energyreport):
    deltawatt = activecomputerwatt - standbycomputerwatt
    deltawattaccessories = activeaccessorieswatt - standbyaccessorieswatt 
    if (accessorycontrol==False):
        deltawattaccessories =  0
    print()
    print()
    print(",,++++++++++++++++++++++++++++++++++++++++++++++++++++")
    for x in analysisvalues:
        print()
        savingsarrayreturn = savingsevaluation (inputrange, x, simPMsavingsval,simPMsavingsOn)     
        if (simPMsavingsOn == False):
            simPMsavingsval = 0 #set to 0 if not enabled for reporting  
        sys.stdout.write(",,Applied savings for intervention at ")
        sys.stdout.write(str(x))
        sys.stdout.write(" minutes:,")
        sys.stdout.write(str(savingsarrayreturn))
        print()
        if (simPMsavingsOn ==True):
            sys.stdout.write(",,Simulated Pre-PM Savings Applied at (min):,")
            sys.stdout.write(str(simPMsavingsval))
            print()
        else:
            sys.stdout.write(",,No Simulated Pre-PM Savings Applied, accordingly the setting is (min):,")
            sys.stdout.write(str(0))
            print()
            
        savingssum = 0 #Initialize the sum counter
        for index in range(0, len(savingsarrayreturn)):
            savingssum = savingssum + int(savingsarrayreturn[0][index])
        sys.stdout.write(",,Total (min) Runtime Saved:,")
        print(str(sum(savingsarrayreturn[0])))
        perday= (sum(savingsarrayreturn[0])/averagebase)
        sys.stdout.write(",,Per day (min) Runtime Saved:,")
        print(str(perday))
        sys.stdout.write(",,Per day (Hr) Runtime Saved:,")
        print(str(perday/60))
        if (energyreport == True):
            runtimehr= perday/60
            
            sys.stdout.write(",,Projected per day Energy Saved considering a delta of ")
            #calculations
            sys.stdout.write(str(deltawatt))
            Wcontacess = (((deltawatt+deltawattaccessories)/1000)*runtimehr)
            sch1= (((deltawatt+deltawattaccessories)/1000)*runtimehr)*261
            sch2 = (((deltawatt+deltawattaccessories)/1000)*runtimehr)*365
            sch3 = ((((deltawatt+deltawattaccessories)/1000)*runtimehr)*261)+(104*24*(deltawatt/1000))
            minMaxRatio = (sch1/(sch3+0.0000001))  #added value to avoid div by zero
            minMidRatio = (sch1/(sch2+0.0000001))  #added value to avoid div by zero
            midMaxRatio = (sch2/(sch3+0.0000001))  #added value to avoid div by zero
            sys.stdout.write(" W and ")
            sys.stdout.write(str(deltawattaccessories))
            sys.stdout.write(" W controlled accessories ")
            sys.stdout.write("-- presented in (kWh/day):, ")
            sys.stdout.write(str(Wcontacess))
            print()
            sys.stdout.write(",,Weekday only (Weekends Off -- No Savings) Schedule Projected per Year Energy Saved (same W load) -- presented in (kWh/year):,")
            sys.stdout.write(str(sch1))
            print()
            sys.stdout.write(",,Identical Schedule Projected per full Year Energy Saved (same W load) -- presented in (kWh/year):,")
            sys.stdout.write(str(sch2))
            print()
            sys.stdout.write(",,Weekday and all Weekends -- Savings) Schedule Projected per Year Energy Saved (same W load) -- presented in (kWh/year):,")
            sys.stdout.write(str(sch3))
            print()
            sys.stdout.write(",,Min-Max Estimate Ratio (min/max kWh) - reference value of .28 (for s equal weekend contribution):,")
            sys.stdout.write(str(minMaxRatio))  #calculate ratio - add in a very small coefficient to avoid div by zero, value around 2.5 is expected based on ratio of weekdays to weekends assuming identical use
            print()
            sys.stdout.write(",,Min-Mid Estimate Ratio (min/mid kWh) - reference value of .28 (for s equal weekend contribution):,")
            sys.stdout.write(str(minMidRatio))  #calculate ratio - add in a very small coefficient to avoid div by zero, value around 2.5 is expected based on ratio of weekdays to weekends assuming identical use
            print()
            sys.stdout.write(",,Mid-Max Estimate Ratio (mid/max kWh) - reference value of .28 (for s equal weekend contribution):,")
            sys.stdout.write(str(midMaxRatio))  #calculate ratio - add in a very small coefficient to avoid div by zero, value around 2.5 is expected based on ratio of weekdays to weekends assuming identical use
            print()
        print (",,______________________________________________")
        if (writetosummarydb == True):
            pushsummarytodb(False, "summary2", str(row[1]), str(row[2]), str(row[3]), str(perdayidleaverage), str(deltawatt), str(deltawattaccessories), str(simPMsavingsval), str(x), str(perday), str(Wcontacess), str(sch1), str(sch2), str(sch3), str(minMaxRatio), str(minMidRatio), str(midMaxRatio)) #Push to DB, do not re-generate table
        
    print(",,**********************************************")

        
#Begin main program
# Open database connection
db = mysql.connector.connect(host="xxxxxx.calit2.uci.edu",    # host
                     user="xxxxxxxx",         # username
                     passwd="xxxxxxxx",  # password
                     db="VerdiemStudy")        # DBName

cursor = db.cursor() # Cursor object for database query

query = ("SELECT * FROM DATA "
         "WHERE subject_identifier = %(s_ID)s AND (date BETWEEN %(start_DATE)s AND %(end_DATE)s)") #base query

#Default Query for device states - change subject number to view other subjects
query_modifications= {'s_ID': 1,'start_DATE': "2014-01-01",'end_DATE': "2014-12-31"} #query records updated by defined variables in dictionary, for device, start and end dates - alternatively use this style for datetime hire_start = datetime.date(1999, 1, 1), for date time printout: #for (first_name, last_name, hire_date) in cursor: print("{}, {} was hired on {:%d %b %Y}".format(last_name, first_name, hire_date))
#Leave this default alone in most use cases if the general query is unchanged, update the values by the function provided to perform a replacement on this dictionary object 


for q, valuesubject in enumerate(subjectlist):
    query_updatevalue('s_ID', (q+1))  #add 1 because q starts at index 0 add 1 because q starts at index 0 - this is driven by the list and automatically entered by the for loop
    print(query_modifications)
        
    cursor.execute(query, query_modifications) #Process query with variable modifications
    queryreturn = cursor.fetchall() #Fetch all rows with defined query for first state
    
    #collect and display unique states in the query
    subjecttallylist = [] #total list of states found
    subjecttallylist_unique_list = []  # intitalize a null list
    statetallylist = [] #total list of states found
    statetallylist_unique_list = [] #total list of states found
    datetallylist = []  #total list of dates found
    datetallylist_unique_list = []  #total list of dates found
    for rowindex, row in enumerate(queryreturn): #go thru query and generate a full list of states from the dataset
        statetallylist.append(row[stateposition])
        datetallylist.append(row[daterow])
        subjecttallylist.append(row[subjectrow])
        
    for x in statetallylist:
        # check if exists in unique_list or not
        if x not in statetallylist_unique_list:
            statetallylist_unique_list.append(x) 
            
    for x in subjecttallylist:
        # check if exists in unique_list or not
        if x not in subjecttallylist_unique_list:
            subjecttallylist_unique_list.append(x) 
            
    for x in datetallylist:
        # check if exists in unique_list or not
        if x not in datetallylist_unique_list:
            datetallylist_unique_list.append(x) 
            
            
    #Print out Headers for CSV
    sys.stdout.write("Subject,Date,State/Info,")
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
        
    
    for listeddate in datetallylist_unique_list: # display entries for a single date
        ontimelist = []
        activetimelist = []
        xorlist = []
           
        for rowindex, row in enumerate(queryreturn): #page thru all returned rows from query, also return an index number related to the row
            if ((("Active") in row[stateposition]) or (("On") in row[stateposition])):
                if ((("Active") in row[stateposition]) and (row[daterow] == listeddate)):
                    sys.stdout.write(str(subjecttallylist_unique_list[0]))
                    sys.stdout.write(',')
                    sys.stdout.write(row[daterow].strftime("%m/%d/%y")) # (INSERT "("%B %d, %Y")" after %d to have commas in name.  Print out the datetime for each record 
                    sys.stdout.write(",") #If record line date is not intended to be displayed, turn of this line also
                    sys.stdout.write(str(row[stateposition]))
                    sys.stdout.write(",") #If record line date is not intended to be displayed, turn of this line also
                    for x in range(periodstartcolumn, periodstartcolumn+totalperiods): #page thru each of the data columns per the defined start and total number of these
                        lengthinstate = int(row[x])  #This is used to read the value at the index each period: total the time active in the column
                        lengthnotinstate = (periodlength-int(row[x])) #This is used to read the value at the index each period: assuming a known total, subtract to find the time not in the state - there would be multiple check under this for more defined states
                        if ((("Active") in row[stateposition]) and (row[daterow] == listeddate)):   #Identify Active/On state by string comparison - for CPU this is ON, for User this is Active
                                    #need to identify this is an active state
                            for a in range(lengthinstate):
                                sys.stdout.write('1') #print out all rows for inspection
                                sys.stdout.write(',') #Used when formatting a non-compliant PLSim CSV file
                                activetimelist.append(1)
                                
                            for b in range(lengthnotinstate):
                                sys.stdout.write('0') #print out all rows for inspection
                                sys.stdout.write(',') #Used when formatting a non-compliant PLSim CSV file
                                activetimelist.append(0)
                    
                    if ((("Active") in row[stateposition]) and (row[daterow] == listeddate)):    
                        #print (len(activetimelist))  #print number of actions, helpful for debug
                        print() #Newline between rows - makes it formatted properly when there is final readout   
        
        
                if ((("On") in row[stateposition]) and (row[daterow] == listeddate)):
                    sys.stdout.write(str(subjecttallylist_unique_list[0]))
                    sys.stdout.write(',')
                    sys.stdout.write(row[daterow].strftime("%m/%d/%y")) # (INSERT "("%B %d, %Y")" after %d to have commas in name.  Print out the datetime for each record 
                    sys.stdout.write(",") #If record line date is not intended to be displayed, turn of this line also
                    sys.stdout.write(str(row[stateposition]))
                    sys.stdout.write("    ,") #If record line date is not intended to be displayed, turn of this line also - add space so text aligns up in console
        
                    for x in range(periodstartcolumn, periodstartcolumn+totalperiods): #page thru each of the data columns per the defined start and total number of these
                        lengthinstate = int(row[x])  #This is used to read the value at the index each period: total the time active in the column
                        lengthnotinstate = (periodlength-int(row[x])) #This is used to read the value at the index each period: assuming a known total, subtract to find the time not in the state - there would be multiple check under this for more defined states
                        if ((("On") in row[stateposition]) and (row[daterow] == listeddate)):   #Identify Active/On state by string comparison - for CPU this is ON, for User this is Active
                                    #need to identify this is an active state
                            for a in range(lengthinstate):
                                sys.stdout.write('1') #print out all rows for inspection
                                sys.stdout.write(',') #Used when formatting a non-compliant PLSim CSV file
                                ontimelist.append(1)
                       
                            for b in range(lengthnotinstate):
                                sys.stdout.write('0') #print out all rows for inspection
                                sys.stdout.write(',') #Used when formatting a non-compliant PLSim CSV file
                                ontimelist.append(0)
                    
                    if ((("On") in row[stateposition]) and (row[daterow] == listeddate)):    
                        #sprint (len(ontimelist))  #print number of actions, helpful for debug
                        print() #Newline between rows - makes it formatted properly when there is final readout   
    
    
    
        
        if ((len(ontimelist) == len(activetimelist)) and (sum(activetimelist) !=0 or sum(ontimelist) !=0)): #check to see if there is a list for the same day for both active and ON states
            
            xorstate=[]
            xorwaste=[]
            xorinvalid =[]
            activeperiods=[]
            offperiods=[]
            logicalstate = []
            print() #Newline between rows - makes it formatted properly when there is final readout   
            sys.stdout.write(str(subjecttallylist_unique_list[0]))
            sys.stdout.write(',')
            sys.stdout.write(listeddate.strftime("%m/%d/%y"))
            sys.stdout.write(',')
            #sys.stdout.write("XOR Both states (valid/invalid),") #calculate XOR value Raw before doing validity check
            for positionindex in range(0, len(activetimelist)):  #this is calculated but not printed - it is granularly broken down elsewhere
                    xorstate.append(int(ontimelist[positionindex] != activetimelist[positionindex]))  #Calculate Raw XOR State      
                #    sys.stdout.write(str(xorstate[positionindex])) #Print raw XOR value
                 #   sys.stdout.write(',') 
            sys.stdout.write("On Periods (Mask): ")
            sys.stdout.write(',')
            for positionindex in range(0, len(activetimelist)):
                    activeperiods.append(int(ontimelist[positionindex] == 1 and activetimelist[positionindex] == 1))  #Calculate Raw XOR State      
                    sys.stdout.write(str(activeperiods[positionindex]))
                    sys.stdout.write(',') 
            print() 
            sys.stdout.write(str(subjecttallylist_unique_list[0]))
            sys.stdout.write(',')
            sys.stdout.write(listeddate.strftime("%m/%d/%y"))
            sys.stdout.write(',')
                            
            sys.stdout.write("Off Periods (Mask):")
            sys.stdout.write(',')
            for positionindex in range(0, len(activetimelist)):
                    offperiods.append(int(ontimelist[positionindex] == 0 and activetimelist[positionindex] == 0))  #Calculate Raw XOR State      
                    sys.stdout.write(str(offperiods[positionindex]))
                    sys.stdout.write(',') 
            print() 
             
            sys.stdout.write(str(subjecttallylist_unique_list[0]))
            sys.stdout.write(',')      
            sys.stdout.write(listeddate.strftime("%m/%d/%y"))
            sys.stdout.write(',')
            sys.stdout.write("XOR Active-Idle State (Mask):,")
            for positionindex in range(0, len(activetimelist)):
                xorwaste.append(int(xorstate[positionindex] == 1 and ontimelist[positionindex] == 1))
                sys.stdout.write((str(xorwaste[positionindex])))
                sys.stdout.write(',')      
            print()  
            
            sys.stdout.write(str(subjecttallylist_unique_list[0]))
            sys.stdout.write(',')      
            sys.stdout.write(listeddate.strftime("%m/%d/%y"))
            sys.stdout.write(',')
            sys.stdout.write("XOR Invalid State (Mask):    ,")
            for positionindex in range(0, len(activetimelist)):
                xorinvalid.append(int(xorstate[positionindex] == 1 and ontimelist[positionindex] == 0))
                sys.stdout.write((str(xorinvalid[positionindex])))
                sys.stdout.write(',')      
            print() 
            
            sys.stdout.write(str(subjecttallylist_unique_list[0]))
            sys.stdout.write(',')
            sys.stdout.write(listeddate.strftime("%m/%d/%y"))  
            sys.stdout.write(',') 
            returnresultsXORWaste=[]
            returnresultsXORWaste = transitionsearch(xorwaste, activetimelist) #read back in transition points
            sys.stdout.write("Transition Points [Date Summary]:,")
            print(returnresultsXORWaste[0], sep=", ")
            sys.stdout.write(str(subjecttallylist_unique_list[0]))
            sys.stdout.write(',')
            sys.stdout.write(listeddate.strftime("%m/%d/%y"))  
            sys.stdout.write(',')
            sys.stdout.write("Transition Deltas (Idle)[Date Summary]:,")
            print(returnresultsXORWaste[1], sep=", ")
            sys.stdout.write(str(subjecttallylist_unique_list[0]))
            sys.stdout.write(',')
            sys.stdout.write(listeddate.strftime("%m/%d/%y"))  
            sys.stdout.write(',')
            sys.stdout.write("Transition Deltas (On-Active/Off)[Date Summary]:,")
            print(returnresultsXORWaste[2], sep=", ")
            sys.stdout.write(str(subjecttallylist_unique_list[0]))
            sys.stdout.write(',')
            sys.stdout.write(listeddate.strftime("%m/%d/%y"))
            sys.stdout.write(',')
            sys.stdout.write("Transition Deltas (Off)[Date Summary]:,")
            print(returnresultsXORWaste[4], sep=", ")
            sys.stdout.write(str(subjecttallylist_unique_list[0]))
            sys.stdout.write(',')
            sys.stdout.write(listeddate.strftime("%m/%d/%y"))
            sys.stdout.write(',')
            sys.stdout.write("Transition Deltas (On-Active)[Date Summary]:,")
            print(returnresultsXORWaste[5], sep=", ")
            sys.stdout.write(str(subjecttallylist_unique_list[0]))
            sys.stdout.write(',')
            sys.stdout.write(listeddate.strftime("%m/%d/%y"))  
            sys.stdout.write(',')
            sys.stdout.write("Transition Deltas (Combined)[Date Summary]:,")
            print(returnresultsXORWaste[3], sep=", ")
            finaldeltalist.append(returnresultsXORWaste[1]) #append to final delta list
            sys.stdout.write(str(subjecttallylist_unique_list[0]))
            sys.stdout.write(',')
            sys.stdout.write(listeddate.strftime("%m/%d/%y"))
            sys.stdout.write(',')
            xorsum=0    
            for positionindex in range(0, len(xorstate)):
                xorsum = xorsum + int(xorstate[positionindex])
            sys.stdout.write("XOR Active-Idle State sum [Date Summary](total -- day %):, ")
            xorwastesum=0    
            for positionindex in range(0, len(xorwaste)):
                xorwastesum = xorwastesum + int(xorwaste[positionindex])
            sys.stdout.write(str(xorwastesum))
            sys.stdout.write(', ')
            sys.stdout.write(str(xorwastesum/minutebaseinday))
            idleaverage += (xorwastesum/minutebaseinday)
            print()  
            sys.stdout.write(str(subjecttallylist_unique_list[0]))
            sys.stdout.write(',')
            sys.stdout.write(listeddate.strftime("%m/%d/%y"))
            sys.stdout.write(',')
            sys.stdout.write("Active-On State sum [Date Summary](total -- day %):, ")
            activeonstate=0    
            for positionindex in range(0, len(returnresultsXORWaste[5])):
                activeonstate = activeonstate + int(returnresultsXORWaste[5][positionindex])
            sys.stdout.write(str(activeonstate))
            sys.stdout.write(', ')
            sys.stdout.write(str(activeonstate/minutebaseinday))
            print()  
            sys.stdout.write(str(subjecttallylist_unique_list[0]))
            sys.stdout.write(',')
            sys.stdout.write(listeddate.strftime("%m/%d/%y"))
            sys.stdout.write(',')
            sys.stdout.write("Off State sum [Date Summary](total -- day %):, ")
            activeoffstate=0    
            for positionindex in range(0, len(returnresultsXORWaste[4])):
                activeoffstate = activeoffstate + int(returnresultsXORWaste[4][positionindex])
            sys.stdout.write(str(activeoffstate))
            sys.stdout.write(', ')
            sys.stdout.write(str(activeoffstate/minutebaseinday))
            print() #Newline between rows - makes it formatted properly when there is final readout   
            print() #Newline between rows - makes it formatted properly when there is final readout   
            print() #Newline between rows - makes it formatted properly when there is final readout   
            resultsreviewcount+=1 #increment total results returned
           
            #Logical State Determination - generic template (must be run per day)
            #temp1 = []
            #logicalstatelist = []
            #for positionindex in range(0, len(activetimelist)):
            
            #    if (xorwwaste[positionindex] == 1):
            #        state=0 #Idle
            #    if (activetimelist[positionindex] == 1 and xorwwaste[positionindex] == 0):
            #        state=1 #Active
            #    if (activetimelist[positionindex] == 0 and xorwwaste[positionindex] == 0):
            #        state=2 #Off
            #    else:
            #        state=-1
                
                    
            #        temp1.append(positionindex)
            #        temp1.append(endval)
            #        if (len(results)!= 0):
            #            t= tuple(temp1)
            #            logicalstatelist.insert((positionindex), t)                          
            #print(logicalstatelist)  #Per day state list - need to build list of list for all days   
            
    print()
    print()
    print()
    print()
    print(",,===================================================")
    print(",,Subject Summary Analysis:")                
    print(",,Delta (Idle) Summary across all days: ")
    sys.stdout.write(str(subjecttallylist_unique_list[0]))
    sys.stdout.write(',')
    sys.stdout.write("All Days")
    sys.stdout.write(',')
    sys.stdout.write("Idle Delta Summary:")
    sys.stdout.write(',')
    sys.stdout.write(str(finaldeltalist))
    print()
    sys.stdout.write(",,Idle time average across all days:,")
    perdayidleaverage = idleaverage/resultsreviewcount
    sys.stdout.write('{:.2%}'.format((perdayidleaverage)))
    print()
    
    
    #Run Evaluations
    #itteration parameters
    deltaWcomputerpower = [20, 30, 40, 50, 60, 80, 100, 120, 150]
    standbycomputerwatt = [0]
    deltaWaccessoriespower = [5, 10, 20, 50, 100, 500]
    pmSettings = [5, 10, 15, 20, 30, 45, 60, 120]
    
    
    #with no PM settings, no accessory control
    for i, value1 in enumerate(standbycomputerwatt):
        for j, value2 in enumerate(deltaWcomputerpower):
            savingsreporting(finaldeltalist,[5,10,15,20,25,30,35,40,45,50,55,60,120,180,240,300],resultsreviewcount,standbycomputerwatt[i],deltaWcomputerpower[j],0,0,False,0,False,True) #Arguments are: (inputrange, analysisvalues, averagebase, standbycomputerwatt, activecomputerwatt, standbyaccessorieswatt, activeaccessorieswatt, accessorycontrol, simPMsavingsval, simPMsavingsOn, energyreport):
    
    
    #with no PM settings, accessory control
    
    for i, value1 in enumerate(standbycomputerwatt):
        for j, value2 in enumerate(deltaWcomputerpower):
            for l, value3 in enumerate(deltaWaccessoriespower):
                savingsreporting(finaldeltalist,[5,10,15,20,25,30,35,40,45,50,55,60,120,180,240,300],resultsreviewcount,standbycomputerwatt[i],deltaWcomputerpower[j],0,deltaWaccessoriespower[l],True,0,False,True) #Arguments are: (inputrange, analysisvalues, averagebase, standbycomputerwatt, activecomputerwatt, standbyaccessorieswatt, activeaccessorieswatt, accessorycontrol, simPMsavingsval, simPMsavingsOn, energyreport):
    
    
    #with PM settings, no accessory control
    for i, value1 in enumerate(standbycomputerwatt):
        for j, value2 in enumerate(deltaWcomputerpower):
            for k, value3 in enumerate(pmSettings):
                savingsreporting(finaldeltalist,[5,10,15,20,25,30,35,40,45,50,55,60,120,180,240,300],resultsreviewcount,standbycomputerwatt[i],deltaWcomputerpower[j],0,0,False,pmSettings[k],True,True) #Arguments are: (inputrange, analysisvalues, averagebase, standbycomputerwatt, activecomputerwatt, standbyaccessorieswatt, activeaccessorieswatt, accessorycontrol, simPMsavingsval, simPMsavingsOn, energyreport):
    
    
    #with PM settings, accessory control
    for i, value1 in enumerate(standbycomputerwatt):
        for j, value2 in enumerate(deltaWcomputerpower):
            for k, value3 in enumerate(pmSettings):
                    for l, value4 in enumerate(deltaWaccessoriespower):
                            savingsreporting(finaldeltalist,[5,10,15,20,25,30,35,40,45,50,55,60,120,180,240,300],resultsreviewcount,standbycomputerwatt[i],deltaWcomputerpower[j],0,deltaWaccessoriespower[l],True,pmSettings[k],True,True) #Arguments are: (inputrange, analysisvalues, averagebase, standbycomputerwatt, activecomputerwatt, standbyaccessorieswatt, activeaccessorieswatt, accessorycontrol, simPMsavingsval, simPMsavingsOn, energyreport):
    
    
    
    print("Run Segment Complete") 
    print() 
print("Run Complete") 
cursor.closeca()
db.close()  #close DB connection