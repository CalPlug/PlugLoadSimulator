# Read the PMUI systemEvents.db data file (stored locally) and push up to mySQL table
# Reads in DB, and for all days with known starts and ends, it will push a record to the database with explicit state values
# California Plug Load Research Center, 2018
# by Zihan "Bronco" Chen

# this program takes PMUI JSON data and converts it into Verdiem data for analysis in time blocks on a per day, per state basis.

# Library setup:
from collections import defaultdict
import json
import numpy
from datetime import timedelta, datetime, date, time
import mysql.connector
import pytz  # handle timzone issues

# Operational Settings
table_name = "ExampleDATA"  # Name of database table to write to
desktop_type = "PC"  # User supplied field that identifies the OS that the parsed file was run on.
subject_ID = "120"  # User supplied field that identifies the subject - to be pushed as a string to the DB
MPID = "120"  # User supplied field that identifies the subject - to be pushed as a string to the DBName
t1 = pytz.timezone('America/Los_Angeles')  # Set timezone for subject, assume pacific for California for CalPlug studies
int_record = 1
input_file_name = "systemEvents.db"  # File name of PMUI Local database file to parse
#input_file_name = "input.txt"  # File name of PMUI Local database file to parse
total_period = 96  # number of columns in DB corresponds to minute resolution (96 is default for 15 minute blocks)
unknown_for_fringes = 1
# use_unknown_for_everyday = 1
# Constants
min_in_day = 1440  # Total minutes in a day, used as a constant, placed here for clarity in code


# Functions:
def timeconverter(datetime_currentvalue):
    datetime_currentvalue /= 1000  # remove from ms and take into seconds
    ts = int(datetime_currentvalue)  # use integer value in seconds
    datetime_newvalue = datetime.utcfromtimestamp(ts)
    # print(datetime_newvalue.strftime(
    #     '%Y-%m-%d %H:%M:%S'))  # print new datetime, UTC  - #conversion between Unix epoch (in ms) at GMT and Local-time Python Datetime object
    # t1.normalize(t1.localize(datetime.utcfromtimestamp(ts))) - use pytz for a historical lookup to convert from GMT based timestamps, #check for DST transition by interpreting the date and checking GMT against current time to determine the timezone for each day/entry, consider pytz or pendulum modules
    dowvalue = datetime_newvalue.weekday()  # identify the day of the week that the date falls on

    # Identify name of the day of the week based upon the returned day number using a lookup table
    dowValueDict = {
        0: "Monday",
        1: "Tuesday",
        2: "Wednesday",
        3: "Thursday",
        4: "Friday",
        5: "Saturday",
        6: "Sunday"
    }
    # Continue building out this function
    # return datetime object, "pretty date, i.e. 2014-04-30" as string, and Day of the week as a string - each of the return arguments
    return datetime_newvalue, dowValueDict.get(dowvalue)


state_list = [
    ("CPU", "Unknown"),
    ("CPU", "Off"),
    ("CPU", "Sleep"),
    ("CPU", "On"),
    ("User", "Unknown"),
    ("User", "Active"),
    ("User", "Idle"),

]


def statusArrayToMinutesDict(statusArray):
    state_set = frozenset(state_list)
    timeRange = statusArray[-1][0] - statusArray[0][0]
    dayRange = timeRange // 1000 // 86400 + 2
    quarterHourRange = dayRange * total_period
    minutesRange = dayRange * 1440

    minutesState = numpy.zeros((len(state_list), minutesRange), numpy.int8)
    if unknown_for_fringes:
        minutesState[state_list.index(("CPU", "Unknown")), ::] = 1
        minutesState[state_list.index(("User", "Unknown")), ::] = 1

    firstSlotTimestamp = statusArray[0][0] - (statusArray[0][0] % (min_in_day * 60 * 1000))

    for timestamp, device, state in statusArray:
        if (device, state) == ("CPU", "Off"):
            minutesState[state_list.index((device, state)), (timestamp - firstSlotTimestamp) // 60000::] = 1
            minutesState[state_list.index(("User", "Unknown")), (timestamp - firstSlotTimestamp) // 60000::] = 1
            minutesState[
            [i for i, n in enumerate(state_list) if n in state_set.difference([(device, state), ("User", "Unknown")])],
            (timestamp - firstSlotTimestamp) // 60000::] = 0
        elif (device, state) == ("CPU", "Sleep"):
            minutesState[state_list.index((device, state)), (timestamp - firstSlotTimestamp) // 60000::] = 1
            minutesState[state_list.index(("User", "Unknown")), (timestamp - firstSlotTimestamp) // 60000::] = 1
            minutesState[
            [i for i, n in enumerate(state_list) if n in state_set.difference([(device, state), ("User", "Unknown")])],
            (timestamp - firstSlotTimestamp) // 60000::] = 0
        elif (device, state) == ("CPU", "On"):
            minutesState[state_list.index((device, state)), (timestamp - firstSlotTimestamp) // 60000::] = 1
            minutesState[
            [i for i, n in enumerate(state_list) if n in [("CPU", "Sleep"), ("CPU", "Off")]],
            (timestamp - firstSlotTimestamp) // 60000::] = 0
        elif (device, state) == ("User", "Idle"):
            minutesState[state_list.index((device, state)), (timestamp - firstSlotTimestamp) // 60000::] = 1
            minutesState[state_list.index(("CPU", "On")), (timestamp - firstSlotTimestamp) // 60000::] = 1
            minutesState[
            [i for i, n in enumerate(state_list) if n in state_set.difference([(device, state), ("CPU", "On")])],
            (timestamp - firstSlotTimestamp) // 60000::] = 0
        elif (device, state) == ("User", "Active"):
            minutesState[state_list.index((device, state)), (timestamp - firstSlotTimestamp) // 60000::] = 1
            minutesState[state_list.index(("CPU", "On")), (timestamp - firstSlotTimestamp) // 60000::] = 1
            minutesState[
            [i for i, n in enumerate(state_list) if n in state_set.difference([(device, state), ("CPU", "On")])],
            (timestamp - firstSlotTimestamp) // 60000::] = 0
        # for state_in_array in state_list:
        #     if state == state_in_array:
        #         minutesState[state_list.index(state_in_array), (timestamp - firstSlotTimestamp) // 60000::] = 1
        #     else:
        #         minutesState[state_list.index(state_in_array), (timestamp - firstSlotTimestamp) // 60000::] = 0

    minutesState[:, (statusArray[-1][0] - firstSlotTimestamp) // 60000 + 1::] = 0
    if unknown_for_fringes == 1:
        minutesState[state_list.index(("CPU", "Unknown")), (statusArray[-1][0] - firstSlotTimestamp) // 60000 + 1::] = 1
        minutesState[state_list.index(("User", "Unknown")),
        (statusArray[-1][0] - firstSlotTimestamp) // 60000 + 1::] = 1
    # for i in range(minutesRange):
    #     if sum(minutesState[0:3, i]) != 1 or sum(minutesState[3:6, i]) != 1:
    #         print(i)

    reshaped = numpy.reshape(minutesState, (len(state_list), quarterHourRange, min_in_day // total_period)).sum(axis=2)
    returnDict = {}
    for (device, state) in state_list:
        returnDict[(device, state)] = reshaped[state_list.index((device, state))]
    return returnDict


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield tuple(l[i:i + n])


def dateToWeekdays(adate):
    dowValueDict = {
        0: "Monday",
        1: "Tuesday",
        2: "Wednesday",
        3: "Thursday",
        4: "Friday",
        5: "Saturday",
        6: "Sunday"
    }
    return dowValueDict.get(adate.weekday())


# ************************************************
# Program Operation:
# open PUMI database file:
# open file and read in contents
with open(input_file_name, 'r', encoding='utf-8') as data_file:
    data = data_file.readlines()
    data = data[:-1]  # remove lat line
# Alternatively, use json.dumps(json_value) to convert your json object(python object) in a json string that you can insert in a text field in mysql
# read in JSON to Python dictionary
# example on this:  https://stackoverflow.com/questions/4251124/inserting-json-into-mysql-using-python

# print out loaded JSON for testing
# for x in data:
#     print("%s: %d" % (x, data[x]))  # adjust fields in this example
# subjectIdDict = defaultdict(list)
# subjectIdCounter = 1
eventList = []
for i in data:
    dataPoint = json.loads(i)
    if dataPoint["eventName"].split("_")[0] == "USER":
        device = 'User'
    elif dataPoint["eventName"].split("_")[0] == "COMPUTER":
        device = "CPU"  # change name to match verdiem data
    else:
        device = dataPoint["eventName"].split("_")[0]
    status = dataPoint["eventName"].split("_")[1].capitalize()
    if status == "AWAKE":
        status = "ON"
    eventList.append((dataPoint["timestamp"] - 7 * 3600 * 1000, device, status))
    # subjectIdDict[(dataPoint["userId"], device)].append((dataPoint["timestamp"] - 7 * 3600 * 1000, status))
eventList.sort()
# create string "p1, p2 ,p3 ..... p96"
p_series_in_query = "p1"
for i in range(2, total_period + 1):  # use the length of starter string (2) as the begin point
    p_series_in_query += "," + "p" + str(i)

# Open Database connection
db = mysql.connector.connect(host="xxxxx.calit2.uci.edu",  # host
                             user="xxxxxx",  # username
                             passwd="xxxxxxx",  # password
                             db="test")  # DBName

cursor = db.cursor()  # Cursor object for database query

# print(device)
slotDict = statusArrayToMinutesDict(eventList)
# datesCountained = len(list(slotDict.values())[0])
firstDate, _ = timeconverter(eventList[0][0])
querys = []
for device, status in slotDict.keys():
    currentDate = firstDate
    for chunk in chunks(slotDict[(device, status)], total_period):
        # if len(list(filter(lambda x: x != 0, chunk))) == 0:
        #     continue
        query = "INSERT INTO " \
                + table_name \
                + "(subject_identifier,desktop_type,MPID,device,status,int_record,date,day_of_week," \
                + p_series_in_query \
                + ') VALUES (' \
                + str(subject_ID) \
                + ',' \
                + repr(desktop_type) \
                + ',' \
                + str(MPID) \
                + ',' \
                + repr(device) \
                + ',' \
                + repr(status) \
                + ',' \
                + str(int_record) \
                + ',' \
                + repr(currentDate.strftime('%Y-%m-%d')) \
                + ',' \
                + repr(dateToWeekdays(currentDate)) \
                + ',' \
                + ",".join(map(str, chunk)) \
                + ");"

        querys.append((currentDate, (device, status), query))
        currentDate += timedelta(days=1)
querys.sort(key=lambda x: (x[0], state_list.index(x[1])))
all_zeroes = ",".join(96 * ["0"])
list(map(lambda x: print(x[2]), filter(lambda x: all_zeroes not in x[2], querys)))
list(map(lambda x: cursor.execute(x[2]), filter(lambda x: all_zeroes not in x[2], querys)))
db.commit()
db.close()  # close DB connection

# SQL Table summary
'''CREATE TABLE IF NOT EXISTS `ExampleDATATemplate` (
`record_id` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
`subject_identifier` TINYINT(4) DEFAULT NULL,
`desktop_type` VARCHAR(3) COLLATE utf8mb4_unicode_ci DEFAULT '',
`MPID` SMALLINT(6) DEFAULT NULL,
`device` VARCHAR(16) COLLATE utf8mb4_unicode_ci DEFAULT '',
`status` VARCHAR(7) COLLATE utf8mb4_unicode_ci DEFAULT '',
`int_record` MEDIUMINT(9) DEFAULT NULL,
`date` DATE DEFAULT NULL,
`day_of_week` VARCHAR(9) COLLATE utf8mb4_unicode_ci DEFAULT '',
`p1` TINYINT(4) DEFAULT NULL,
`p2` TINYINT(4) DEFAULT NULL,
`p3` TINYINT(4) DEFAULT NULL,
`p4` TINYINT(4) DEFAULT NULL,
`p5` TINYINT(4) DEFAULT NULL,
`p6` TINYINT(4) DEFAULT NULL,
`p7` TINYINT(4) DEFAULT NULL,
`p8` TINYINT(4) DEFAULT NULL,
`p9` TINYINT(4) DEFAULT NULL,
`p10` TINYINT(4) DEFAULT NULL,
`p11` TINYINT(4) DEFAULT NULL,
`p12` TINYINT(4) DEFAULT NULL,
`p13` TINYINT(4) DEFAULT NULL,
`p14` TINYINT(4) DEFAULT NULL,
`p15` TINYINT(4) DEFAULT NULL,
`p16` TINYINT(4) DEFAULT NULL,
`p17` TINYINT(4) DEFAULT NULL,
`p18` TINYINT(4) DEFAULT NULL,
`p19` TINYINT(4) DEFAULT NULL,
`p20` TINYINT(4) DEFAULT NULL,
`p21` TINYINT(4) DEFAULT NULL,
`p22` TINYINT(4) DEFAULT NULL,
`p23` TINYINT(4) DEFAULT NULL,
`p24` TINYINT(4) DEFAULT NULL,
`p25` TINYINT(4) DEFAULT NULL,
`p26` TINYINT(4) DEFAULT NULL,
`p27` TINYINT(4) DEFAULT NULL,
`p28` TINYINT(4) DEFAULT NULL,
`p29` TINYINT(4) DEFAULT NULL,
`p30` TINYINT(4) DEFAULT NULL,
`p31` TINYINT(4) DEFAULT NULL,
`p32` TINYINT(4) DEFAULT NULL,
`p33` TINYINT(4) DEFAULT NULL,
`p34` TINYINT(4) DEFAULT NULL,
`p35` TINYINT(4) DEFAULT NULL,
`p36` TINYINT(4) DEFAULT NULL,
`p37` TINYINT(4) DEFAULT NULL,
`p38` TINYINT(4) DEFAULT NULL,
`p39` TINYINT(4) DEFAULT NULL,
`p40` TINYINT(4) DEFAULT NULL,
`p41` TINYINT(4) DEFAULT NULL,
`p42` TINYINT(4) DEFAULT NULL,
`p43` TINYINT(4) DEFAULT NULL,
`p44` TINYINT(4) DEFAULT NULL,
`p45` TINYINT(4) DEFAULT NULL,
`p46` TINYINT(4) DEFAULT NULL,
`p47` TINYINT(4) DEFAULT NULL,
`p48` TINYINT(4) DEFAULT NULL,
`p49` TINYINT(4) DEFAULT NULL,
`p50` TINYINT(4) DEFAULT NULL,
`p51` TINYINT(4) DEFAULT NULL,
`p52` TINYINT(4) DEFAULT NULL,
`p53` TINYINT(4) DEFAULT NULL,
`p54` TINYINT(4) DEFAULT NULL,
`p55` TINYINT(4) DEFAULT NULL,
`p56` TINYINT(4) DEFAULT NULL,
`p57` TINYINT(4) DEFAULT NULL,
`p58` TINYINT(4) DEFAULT NULL,
`p59` TINYINT(4) DEFAULT NULL,
`p60` TINYINT(4) DEFAULT NULL,
`p61` TINYINT(4) DEFAULT NULL,
`p62` TINYINT(4) DEFAULT NULL,
`p63` TINYINT(4) DEFAULT NULL,
`p64` TINYINT(4) DEFAULT NULL,
`p65` TINYINT(4) DEFAULT NULL,
`p66` TINYINT(4) DEFAULT NULL,
`p67` TINYINT(4) DEFAULT NULL,
`p68` TINYINT(4) DEFAULT NULL,
`p69` TINYINT(4) DEFAULT NULL,
`p70` TINYINT(4) DEFAULT NULL,
`p71` TINYINT(4) DEFAULT NULL,
`p72` TINYINT(4) DEFAULT NULL,
`p73` TINYINT(4) DEFAULT NULL,
`p74` TINYINT(4) DEFAULT NULL,
`p75` TINYINT(4) DEFAULT NULL,
`p76` TINYINT(4) DEFAULT NULL,
`p77` TINYINT(4) DEFAULT NULL,
`p78` TINYINT(4) DEFAULT NULL,
`p79` TINYINT(4) DEFAULT NULL,
`p80` TINYINT(4) DEFAULT NULL,
`p81` TINYINT(4) DEFAULT NULL,
`p82` TINYINT(4) DEFAULT NULL,
`p83` TINYINT(4) DEFAULT NULL,
`p84` TINYINT(4) DEFAULT NULL,
`p85` TINYINT(4) DEFAULT NULL,
`p86` TINYINT(4) DEFAULT NULL,
`p87` TINYINT(4) DEFAULT NULL,
`p88` TINYINT(4) DEFAULT NULL,
`p89` TINYINT(4) DEFAULT NULL,
`p90` TINYINT(4) DEFAULT NULL,
`p91` TINYINT(4) DEFAULT NULL,
`p92` TINYINT(4) DEFAULT NULL,
`p93` TINYINT(4) DEFAULT NULL,
`p94` TINYINT(4) DEFAULT NULL,
`p95` TINYINT(4) DEFAULT NULL,
`p96` TINYINT(4) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci; '''

# read in JSON file except for last line (possibly remove before this point by truncating the returned dictionary object) (this is a footer)
# check to see the datetime for entry as each entry is paged thru
# check each entry with [datetime_newvalue, date, DOW] = timeconverter (datetime)
# loop thru entries and generate a list of dates (datetime objects) for all data entries
# Note: Exclude the current day if the recordtoday flag is False