# Read the PMUI systemEvents.db data file (stored locally) and push up to MySQL table
# Reads in DB, and for all days with known starts and ends, it will push a record to the database with explicit state values
# California Plug Load Research Center, 2018
# by Zihan "Bronco" Chen

# this program takes PMUI JSON data and converts it into Verdiem data for analysis in time blocks on a per day, per state basis.

# Library setup:
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
int_record = 1
input_file_name = "input_pmui_json.txt"  # File name of PMUI Local database file to parse
total_period = 96  # number of columns in DB corresponds to minute resolution (96 is default for 15 minute blocks)
unknown_for_fringes = 1
# use_unknown_for_everyday = 1

auto_timezone_adjust = True
auto_timezone = pytz.timezone(
    'America/Los_Angeles')  # Set timezone for subject, assume pacific for California for CalPlug studies
manual_offset = timedelta(hours=7)

# Constants
min_in_day = 1440  # Total minutes in a day, used as a constant, placed here for clarity in code


# Functions:
def timeconverter(datetime_currentvalue):
    datetime_currentvalue /= 1000  # remove from ms and take into seconds
    ts = int(datetime_currentvalue)  # use integer value in seconds
    if auto_timezone_adjust:
        datetime_newvalue = pytz.utc.localize(datetime.utcfromtimestamp(ts)).astimezone(auto_timezone)
    else:
        datetime_newvalue = datetime.utcfromtimestamp(ts) + manual_offset

    # Continue building out this function
    # return datetime object, "pretty date, i.e. 2014-04-30" as string, and Day of the week as a string - each of the return arguments
    return datetime_newvalue




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

    firstSlotTime = timeconverter(statusArray[0][0])
    firstSlotTimestamp = int(firstSlotTime.replace(hour=0, minute=0, second=0, microsecond=0).timestamp()) * 1000

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
db = mysql.connector.connect(host="cplamp.calit2.uci.edu",  # host
                             user="calplug",  # username
                             passwd="123456!",  # password
                             db="test")  # DBName

cursor = db.cursor()  # Cursor object for database query

# print(device)
slotDict = statusArrayToMinutesDict(eventList)
# datesCountained = len(list(slotDict.values())[0])
firstDate= timeconverter(eventList[0][0])
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
