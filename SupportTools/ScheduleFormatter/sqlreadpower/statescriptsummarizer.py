#Read the mySQL table summary results for power analysis and print contents of the .CSV file summary to the console
#California Plug Load Research Center, 2018


#Library setup:
import sys
from datetime import timedelta, datetime, date, time
from time import mktime
import mysql.connector

#Operational Constants/Parameters
#Computer load in off, Standby, On (Active/Idle)
CompLoadParamsOff = [0.1, 0.5, 1.5] #min/mid/max values to test
CompLoadParamsStby = [1.0, 2.5, 5.0]
CompLoadParamsOn = [20, 45, 100, 120]
#Note for reference: 100% use at 120W is 1051.2KWh/year!

#values to use for the summary evaluation report
#all possible values shown:
#Unit_values = ["TotalStyMinAllDay", "MinPerDay", "State%PerDay"]
#State_vals = ["On","Sleep","Off","Active", "Idle", "UserUnknown", "CPUUnknown"]  #more to add, finish this off

Unit_values = ["MinPerDay", "State%PerDay"]
State_vals = ["On","Sleep","Off"]  #more to add, finish this off

#Global Variables
energyaccumulator = [[0,0,0], [0,0,0], [0,0,0]] #Stores the off, standby, active values in simulation operation for weekdays, week end days, and all days



#Functions
def query_updatevalue(dictionaryname, key_to_find, definition):  #used to update a sample SQL query with a new value - easier than parsing strings manually
    #remember, if a key is missed, this will skip, be careful!!
    for index, key in enumerate(dictionaryname.keys()):
        if(len(key_to_find) == len(definition)): #check same number of entries to valid process
            if (index<len(key_to_find)):  #prevent an out of range error if not all key vaues are replaced (for some reason)
                if key == key_to_find[index]: #fix the index versus element issue with start as 0 vs 1
                    dictionaryname[key] = definition[index]
                    #print (index)  #--Debug printout
                    #print (key)    #--Debug printout
    return [dictionaryname] #returns as array, you only need/want the first [0] element, make sure this is called on the function return!



#************************************************
#Program Operation

#Open Database connection
db = mysql.connector.connect(host="xxxxxxxx.calit2.uci.edu",    # host
                     user="xxxxxxxx",         # username
                     passwd="xxxxxxxxx",  # password
                     db="VerdiemStudy")        # DBName

cursor = db.cursor() # Cursor object for database query

#Queries against the resultssummary DB
#Returns the average for all days 
query_1 = ("SELECT AVG(`Monday`), AVG(`Tuesday`), AVG(`Wednesday`), AVG(`Thursday`), AVG(`Friday`), (AVG(`Monday`)+AVG(`Tuesday`)+AVG(`Wednesday`)+AVG(`Thursday`)+AVG(`Friday`))/5, AVG(`Saturday`), AVG(`Sunday`), (AVG(`Saturday`) + AVG(`Sunday`))/2, (AVG(`Monday`)+ AVG(`Tuesday`)+ AVG(`Wednesday`)+ AVG(`Thursday`)+ AVG(`Friday`)+ AVG(`Saturday`) + AVG(`Sunday`))/7 FROM statesummary WHERE (`Unit` = %(Unit_values)s AND `State` = %(State_values)s)")
query_2 = ("SELECT STDDEV(`Monday`), STDDEV(`Tuesday`), STDDEV(`Wednesday`), STDDEV(`Thursday`), STDDEV(`Friday`), STDDEV(concat((`Monday`),(`Tuesday`),(`Wednesday`),(`Thursday`),(`Friday`))), STDDEV(`Saturday`), STDDEV(`Sunday`), STDDEV(concat((`Saturday`),(`Sunday`))), STDDEV(concat((`Monday`),(`Tuesday`),(`Wednesday`),(`Thursday`),(`Friday`),(`Saturday`),(`Sunday`))) FROM statesummary WHERE (`Unit` = %(Unit_values)s AND `State` = %(State_values)s)")

#Default Query for replacing elements of return with dictionary - change subject number to view other subjects
query_modifications = {'Unit_values': "MinPerDay",'State_values': "On"} #query records default case


    

#Print CSV Headers:
#print("MonIdle,Computer Power (delta W),Intervention Setting (min),Idle Percent,Per Day Energy Usage (kWh) [Weekday Only],Total Weekday Contribution (kWh),Weekday Contribution Std. Dev (kWh),Weekend Contribution  (kWh),Weekday Contribution Std. Dev (kWh), Total Savings(kWh)")

#Page thru parameters to extract summary for and print into a CSV style format in the console

#*********Test for different loads
for value1 in Unit_values:
    for value2 in State_vals:
        ## Modify each of the queries
        updated_querymodifications_1 = query_updatevalue(query_modifications,['Unit_values', 'State_values'],[value1, value2]) #present values in the order to match the keys
        updated_querymodifications_2 = query_updatevalue(query_modifications,['Unit_values', 'State_values'],[value1, value2]) #present values in the order to match the keys
        #Evaluate the summation case
                              
        #Write out the values for the evaluation being tested in the current DB query
        sys.stdout.write(str(value1))
        sys.stdout.write(",") #separator
        sys.stdout.write(str(value2))
        sys.stdout.write(",") #separator
        
        #sys.stdout.write("******") #Debug test separator
        #put the parts together and query the DB:
        #process each query:
        cursor.execute(query_1, updated_querymodifications_1[0]) #Process query with variable modifications
        queryreturn_1 = cursor.fetchone() #Fetch only one row with defined query for first state
        
        cursor.execute(query_2, updated_querymodifications_2[0]) #Process query with variable modifications
        queryreturn_2 = cursor.fetchone() #Fetch only one row with defined query for first state

        if (value2 == "Off" and value1 == "State%PerDay"):
          
            energyaccumulator[0][0] =  (queryreturn_1[5]) #weekdays
            energyaccumulator[0][1] =  (queryreturn_1[8]) #weekends
            energyaccumulator[0][2] =  (queryreturn_1[9]) #all days
            
        elif (value2 == "Sleep" and value1 == "State%PerDay"): 
            
            energyaccumulator[1][0] =  (queryreturn_1[5]) #weekdays
            energyaccumulator[1][1] =  (queryreturn_1[8]) #weekends
            energyaccumulator[1][2] =  (queryreturn_1[9]) #all days
            
        elif (value2 == "On" and value1 == "State%PerDay"): 
            
            energyaccumulator[2][0] =  (queryreturn_1[5]) #weekdays
            energyaccumulator[2][1] =  (queryreturn_1[8]) #weekends
            energyaccumulator[2][2] =  (queryreturn_1[9]) #all days
        
        #write out the return values - Query 1
        sys.stdout.write(str(queryreturn_1[5]))
        sys.stdout.write(",") #separator
        sys.stdout.write(str(queryreturn_1[8]))
        sys.stdout.write(",") #separator
        sys.stdout.write(str(queryreturn_1[9]))
        sys.stdout.write(",") #separator

        
        #sys.stdout.write("******") #Debug test separator
        
        #write out the return values - Query 2
        #sys.stdout.write(str(queryreturn_2[idlepercent]))
        #sys.stdout.write(",") #separator
        sys.stdout.write(str(queryreturn_2[5]))
        sys.stdout.write(",") #separator
        sys.stdout.write(str(queryreturn_2[8]))
        sys.stdout.write(",") #separator
        sys.stdout.write(str(queryreturn_2[9]))
        sys.stdout.write(",") #separator

        print() #newline
    print() #newline
    print() #newline
print ("Off State:")
for index, items in enumerate(CompLoadParamsOff):
    OffenergyuseAllWeekdays = ((energyaccumulator[0][0] * 24)*(items/1000)*261) #number of weekdays to apply the average across
    OffenergyuseAllWeekendDays = ((energyaccumulator[0][1] * 24)*(items/1000)*104) #number of weekend days to apply the average across
    OffenergyuseAlldays = ((energyaccumulator[0][2] * 24)*(items/1000) *365) # total days in the year "
    print(CompLoadParamsOff)
    print (str(OffenergyuseAllWeekdays))
    print (str(OffenergyuseAllWeekendDays))
    print (str(OffenergyuseAlldays))
    
    print() #newline
print() #newline
print() #newline
print ("Standby State:")
for index, items in enumerate(CompLoadParamsStby):
    StbyenergyuseAllWeekdays = ((energyaccumulator[1][0] * 24)*(items/1000)*261) #number of weekdays to apply the average across
    StbyenergyuseAllWeekendDays = ((energyaccumulator[1][1] * 24)*(items/1000)*104) #number of weekend days to apply the average across
    StbyenergyuseAlldays = ((energyaccumulator[1][2] * 24)*(items/1000) *365) # total days in the year "
    print(CompLoadParamsStby)
    print (str(StbyenergyuseAllWeekdays))
    print (str(StbyenergyuseAllWeekendDays))
    print (str(StbyenergyuseAlldays))
    print() #newline
    
print() #newline
print() #newline
print ("On State:")
for index, items in enumerate(CompLoadParamsOn):
    OnenergyuseAllWeekdays = ((energyaccumulator[2][0] * 24)*(items/1000)*261) #number of weekdays to apply the average across
    OnenergyuseAllWeekendDays = ((energyaccumulator[2][1] * 24)*(items/1000)*104) #number of weekend days to apply the average across
    OnenergyuseAlldays = ((energyaccumulator[2][2] * 24)*(items/1000) *365) # total days in the year "
    print(CompLoadParamsOn)
    print (str(OnenergyuseAllWeekdays))
    print (str(OnenergyuseAllWeekendDays))
    print (str(OnenergyuseAlldays))
    print() #newline
  


cursor.close()
db.close()  #close DB connection

  