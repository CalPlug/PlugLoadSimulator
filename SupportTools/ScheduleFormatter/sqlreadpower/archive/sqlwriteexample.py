#Demo DB Writer Example

import mysql.connector
import sys
from datetime import timedelta
from datetime import datetime
from datetime import date
from datetime import time

#Run Options for Output Formatting
plsimcompliant= False #Decide if you want the printed output to be PLSim compliant or be formatted for a CSV tyle to enter into Excel or other program that works with CSVs 
plsimsupressdate = False #Dates must be suppressed for direct PLSim compliance, help one read material when aligning data, but this must be supressed to be PLSim Compitable
elapsedminortime = False #If true, display Elapsed minutes versus time
annotatetransitions = True #Will display at the end of each line the number of transitions per row of data (in a given state) for CSV Formatting

# Open database connection
db = mysql.connector.connect(host="cplamp.calit2.uci.edu",    # host
                     user="XXXXXXXXX",         # username
                     passwd="XXXXXXX",  # password
                     db="TEMP")        # DBName

cursor = db.cursor() # Cursor object for database query


# Create table as per requirement before inserting values or it will not work
asd = [[1.25,2.45,3.65],
       [2.78,3.59,1.58]]

asdsingle = [1.11,2.22,3.33]
#Define table name in which to insert data into
table_name= "test"

#alternate approach:
#cursor.executemany("""
#    INSERT INTO 
 #       test
#        (x, y, z)
 #   VALUES
#        (%s, %s, %s)
#""", asd)

cursor.executemany('''INSERT IGNORE INTO %s (x, y, z) VALUES (%%s, %%s, %%s)''' % table_name, (asd))

#Insert the array by element into the DB

db.commit()

cursor.execute('''INSERT IGNORE INTO %s (x, y, z) VALUES (%%s, %%s, %%s)''' % table_name, (asdsingle))

db.commit()

print("Published to SQL table")
# disconnect from server
cursor.close()
db.close()  #close DB connection