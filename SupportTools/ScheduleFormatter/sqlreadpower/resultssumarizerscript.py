#Read the mySQL table summary results for power analysis and print contents of the .CSV file summary to the console
#California Plug Load Research Center, 2018


#Library setup:
import sys
from datetime import timedelta, datetime, date, time
from time import mktime
import mysql.connector

#return row locations Table locations:
idlepercent = 0 #column for this value
perdaysavings = 1
returnval1 = 2
returnval2 = 3
returnval3 = 4
returncountval = 5

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
db = mysql.connector.connect(host="XXXXXXX.calit2.uci.edu",    # host
                     user="XXXXXXXX",         # username
                     passwd="XXXXXX",  # password
                     db="VerdiemStudy")        # DBName

cursor = db.cursor() # Cursor object for database query

#Queries against the summary and summary 2 Database tables
 
query_1 = ("SELECT AVG(`summary_idle_percent`), AVG(`projected_per_day_savings_kWh`), AVG(`weekday_only_estimate_kwhperyear`), count(*) FROM summary5 WHERE (delta_computer_W = %(delta_computer_W)s AND delta_acessories_W = %(delta_acessories_W)s AND external_pm_control_min = %(external_pm_control_min)s AND invervention_setting_min = %(invervention_setting_min)s AND all_days_even_estimate_kwhperyear =-1 AND weekday_and_weekends_estimate_kwhperyear=-1)")
query_2 = ("SELECT AVG(`summary_idle_percent`), AVG(`projected_per_day_savings_kWh`), AVG(`weekday_and_weekends_estimate_kwhperyear`), count(*) FROM summary5 WHERE (delta_computer_W = %(delta_computer_W)s AND delta_acessories_W = %(delta_acessories_W)s AND external_pm_control_min = %(external_pm_control_min)s AND invervention_setting_min = %(invervention_setting_min)s AND `weekday_only_estimate_kwhperyear` =-1 AND all_days_even_estimate_kwhperyear=-1)")
query_3 = ("SELECT AVG(`summary_idle_percent`), AVG(`projected_per_day_savings_kWh`), AVG(`all_days_even_estimate_kwhperyear`), count(*) FROM summary5 WHERE (delta_computer_W = %(delta_computer_W)s AND delta_acessories_W = %(delta_acessories_W)s AND external_pm_control_min = %(external_pm_control_min)s AND invervention_setting_min = %(invervention_setting_min)s AND `weekday_only_estimate_kwhperyear` =-1 AND weekday_and_weekends_estimate_kwhperyear=-1)")
query_4 = ("SELECT AVG(`summary_idle_percent`), AVG(`projected_per_day_savings_kWh`), AVG(`weekday_and_weekends_estimate_kwhperyear`), AVG(`all_days_even_estimate_kwhperyear`), AVG(`weekday_only_estimate_kwhperyear`),count(*) FROM summary5 WHERE (delta_computer_W = %(delta_computer_W)s AND delta_acessories_W = %(delta_acessories_W)s AND external_pm_control_min = %(external_pm_control_min)s AND invervention_setting_min = %(invervention_setting_min)s AND ( (weekday_only_estimate_kwhperyear != -1 AND all_days_even_estimate_kwhperyear !=-1) OR (weekday_only_estimate_kwhperyear != -1 AND weekday_and_weekends_estimate_kwhperyear !=-1) OR (all_days_even_estimate_kwhperyear !=-1 AND weekday_and_weekends_estimate_kwhperyear !=-1)))")

#Default Query for replacing elements of return with dictionary - change subject number to view other subjects
query_modifications_1 = {'delta_computer_W': 1,'delta_acessories_W': 0,'external_pm_control_min': 0, 'invervention_setting_min': 5} #query records default case
query_modifications_2 = {'delta_computer_W': 1,'delta_acessories_W': 0,'external_pm_control_min': 0, 'invervention_setting_min': 5} #query records default case
query_modifications_3 = {'delta_computer_W': 1,'delta_acessories_W': 0,'external_pm_control_min': 0, 'invervention_setting_min': 5} #query records default case
query_modifications_4 = {'delta_computer_W': 1,'delta_acessories_W': 0,'external_pm_control_min': 0, 'invervention_setting_min': 5} #query records default case


#values to use for the summary evaluation report
delta_acessories_W_report_vals = [0, 5, 10 ,20]
delta_computer_W_report_vals = [20,40,50,100,120]
external_pm_control_min_report_vals = [0, 5, 10, 15, 20, 30, 45, 60, 120]
invervention_setting_min_report_vals = [5, 10, 15, 60]

    

#Print CSV Headers:
print("Imposed PM Setting (min),Computer Power (delta W),Intervention Setting (min),Idle Percent,Per Day Energy Usage (kWh) [Weekday Only],Total Weekday Contribution (kWh),Weekday Contribution Std. Dev (kWh),Weekend Contribution  (kWh),Weekday Contribution Std. Dev (kWh), Total Savings(kWh)")

#Page thru parameters to extract summary for and print into a CSV style format in the console
for value1 in delta_acessories_W_report_vals:
    if (value1 == 0): #Case where no devices are controlled in the simulation
        print("No Controlled Devices")
    else:
        sys.stdout.write("Controlled Devices (W): ")
        print(value1)
    for value2 in delta_computer_W_report_vals:
        for value3 in external_pm_control_min_report_vals:
            for value4 in invervention_setting_min_report_vals:
                ## Modify each of the queries
                updated_querymodifications_1 = query_updatevalue(query_modifications_1,['delta_computer_W', 'delta_acessories_W','external_pm_control_min','invervention_setting_min' ],[value2, value1, value3, value4])  #present values in the order to match the keys
                updated_querymodifications_2 = query_updatevalue(query_modifications_2,['delta_computer_W', 'delta_acessories_W','external_pm_control_min','invervention_setting_min' ],[value2, value1, value3, value4])  
                updated_querymodifications_3 = query_updatevalue(query_modifications_3,['delta_computer_W', 'delta_acessories_W','external_pm_control_min','invervention_setting_min' ],[value2, value1, value3, value4])  
                updated_querymodifications_4 = query_updatevalue(query_modifications_4,['delta_computer_W', 'delta_acessories_W','external_pm_control_min','invervention_setting_min' ],[value2, value1, value3, value4])  
         
                #sys.stdout.write("Query 1, post modification: ") # - Use in debug
                #print(updated_querymodifications_1[0]) # - Use in debug, returns as array, you only want the first element.

                
                #place run parameters in place:
                #Denote separately if controlled devices are in place
                if (value3 == 0):
                    sys.stdout.write("Wildtype") #Case where the original PM settings are used
                else:
                    sys.stdout.write(str(value3))
                sys.stdout.write(",") #separator
                sys.stdout.write(str(value2))
                sys.stdout.write(",") #separator
                sys.stdout.write(str(value4))
                sys.stdout.write(",") #separator
                
                #sys.stdout.write("******") #Debug test separator
                #put the parts together and query the DB:
                #process each query:
                cursor.execute(query_1, updated_querymodifications_1[0]) #Process query with variable modifications
                queryreturn_1 = cursor.fetchone() #Fetch only one row with defined query for first state
                
                cursor.execute(query_2, updated_querymodifications_2[0]) #Process query with variable modifications
                queryreturn_2 = cursor.fetchone() #Fetch only one row with defined query for first state

                cursor.execute(query_3, updated_querymodifications_3[0]) #Process query with variable modifications
                queryreturn_3 = cursor.fetchone() #Fetch only one row with defined query for first state

                cursor.execute(query_4, updated_querymodifications_4[0]) #Process query with variable modifications
                queryreturn_4 = cursor.fetchone() #Fetch only one row with defined query for first state

                
                #write out the return values - Query 1
                sys.stdout.write(str(queryreturn_1[idlepercent]))
                sys.stdout.write(",") #separator
                sys.stdout.write(str(queryreturn_1[perdaysavings]))
                sys.stdout.write(",") #separator
                sys.stdout.write(str(queryreturn_1[returnval1]))
                sys.stdout.write(",") #separator
                
                #sys.stdout.write("******") #Debug test separator
                
                #write out the return values - Query 2
                #sys.stdout.write(str(queryreturn_2[idlepercent]))
                #sys.stdout.write(",") #separator
                sys.stdout.write(str(queryreturn_2[perdaysavings]))
                sys.stdout.write(",") #separator
                sys.stdout.write(str(queryreturn_2[returnval1]))
                sys.stdout.write(",") #separator

                
                #sys.stdout.write("******") #Debug test separator
                
                #write out the return values - Query 3
                #sys.stdout.write(str(queryreturn_3[idlepercent]))
                #sys.stdout.write(",") #separator
                sys.stdout.write(str(queryreturn_3[perdaysavings]))
                sys.stdout.write(",") #separator
                sys.stdout.write(str(queryreturn_3[returnval1]))
                sys.stdout.write(",") #separator

                
                #sys.stdout.write("******") #Debug test separator
                
                #write out the return values - Query 4
                #sys.stdout.write(str(queryreturn_4[idlepercent]))
                #sys.stdout.write(",") #separator
                sys.stdout.write(str(queryreturn_4[perdaysavings]))
                sys.stdout.write(",") #separator
                sys.stdout.write(str(queryreturn_4[returnval1]))
                sys.stdout.write(",") #separator
                sys.stdout.write(str(queryreturn_4[returnval2]))
                sys.stdout.write(",") #separator
                sys.stdout.write(str(queryreturn_4[returnval3]))
                sys.stdout.write(",") #separator
                
                #sys.stdout.write("******") #Debug test separator

                print("") #send newline with each full return set
    
cursor.close()
db.close()  #close DB connection

  