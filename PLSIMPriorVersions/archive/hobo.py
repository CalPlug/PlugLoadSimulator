# Read the contents of an Onset HOBO Plug Load and Ligt/Motion monitor and parse into Verdiem format then upload to a mySQL table
# Reads in DB, and for all days with known starts and ends, it will push a record to the database with explicit state values
# California Plug Load Research Center, 2018
# by Zihan "Bronco" Chen


# Library setup:
from collections import defaultdict
import scipy.interpolate
import numpy as np
from datetime import timedelta, datetime
import mysql.connector
import pytz
import time

# Operational Settings
table_name = "ExampleDATAfloat"  # Name of database table to write to
desktop_type = "PC"  # User supplied field that identifies the OS that the parsed file was run on.
subject_ID = "120"  # User supplied field that identifies the subject - to be pushed as a string to the DB
MPID = "1"  # User supplied field that identifies the subject - to be pushed as a string to the DBName
int_record = 1

# Define which input file type to process, one or both:  WARNING:Do not set both to False
hobo_1_enabled = True
hobo_2_enabled = True
hobo_1_filename = "mikeofficepc_power_10.24.18.csv"  # File name of Hobo Plug Load Logger exported file
hobo_2_filename = "mikeofficepc_motionandlight_10.24.18.csv"  # File name of Hobo Motion/Light Logger exported file
total_period = 96  # number of columns in DB corresponds to minute resolution (96 is default for 15 minute blocks)
unknown_for_fringes = 1
use_unknown_for_everyday = 1

auto_timezone_adjust = True
auto_timezone = pytz.timezone(
    'America/Los_Angeles')  # Set timezone for subject, assume pacific for California for CalPlug studies
manual_offset = timedelta(hours=7)

# Constants
min_in_day = 1440  # Total minutes in a day, used as a constant, placed here for clarity in code
time_parse = "%x %I:%M:%S %p"

hobo_1_meaning = [
    ("CPU", "RMS Voltage"),  # row 2
    ("CPU", "RMS Current"),
    ("CPU", "Active Power"),
    ("CPU", "Active Energy"),
    ("CPU", "Apparent Power"),
    ("CPU", "Power Factor")
]

hobo_2_meaning = [
    ("User", "Light"),  # row 2
    ("User", "Occupancy"),
]

state_list = hobo_1_meaning + [
    ("User_Light", "0"),  # row 2
    ("User_Light", "1"),
    ("User_Light", "Unknown"),
    ("User_Occupancy", "0"),
    ("User_Occupancy", "1"),
    ("User_Occupancy", "Unknown")] \
    if unknown_for_fringes else [
    ("User_Light", "0"),  # row 2
    ("User_Light", "1"),
    ("User_Occupancy", "0"),
    ("User_Occupancy", "1"),
]


# Functions:

def timeconverter(datetime_currentvalue):
    # datetime_currentvalue /= 1000  # remove from ms and take into seconds
    ts = int(datetime_currentvalue)  # use integer value in seconds
    if auto_timezone_adjust:
        datetime_newvalue = pytz.utc.localize(datetime.utcfromtimestamp(ts)).astimezone(auto_timezone)
    else:
        datetime_newvalue = datetime.utcfromtimestamp(ts) + manual_offset

    # Continue building out this function
    # return datetime object, "pretty date, i.e. 2014-04-30" as string, and Day of the week as a string - each of the return arguments
    return datetime_newvalue


def file_preprocess(hobo_1_filename, hobo_2_filename):
    hobo_1_np = {}
    hobo_2_np = {}
    if hobo_1_enabled:
        with open(hobo_1_filename) as hobo_1:
            hobo_1_lines = hobo_1.readlines()
            hobo_1_data = defaultdict(list)
        for line in hobo_1_lines:
            try:
                seperated = line.split(",")
                if len(list(filter(lambda x: x == "", seperated[1:8]))) != 0:
                    continue
            except:
                continue
            for i in range(2, 8):
                try:
                    if auto_timezone_adjust:
                        hobo_1_data[hobo_1_meaning[i - 2]].append(
                            # (time.strptime(seperated[1], time_parse).timestamp()
                            (
                                auto_timezone.localize(
                                    datetime(*(time.strptime(seperated[1], time_parse)[0:6]))).timestamp()
                                , float(seperated[i])))
                    else:
                        hobo_1_data[hobo_1_meaning[i - 2]].append(
                            (
                                (datetime.strptime(seperated[1], time_parse) + manual_offset).timestamp(),
                                float(seperated[i])))
                except:
                    pass
        for i in hobo_1_meaning:
            hobo_1_data[i].sort()
            hobo_1_np[i] = np.array(hobo_1_data[i], dtype=[("timestamp", np.uint32), ("value", np.float16)])
    if hobo_2_enabled:
        with open(hobo_2_filename) as hobo_2:
            hobo_2_lines = hobo_2.readlines()
            hobo_2_data = defaultdict(list)
        for line in hobo_2_lines:
            try:
                seperated = line.split(",")
                if seperated[2] == "" and seperated[3] == "":
                    continue
            except:
                continue
            try:
                if auto_timezone_adjust:
                    if seperated[2] != "":
                        hobo_2_data[hobo_2_meaning[0]].append(
                            (
                                int(
                                    auto_timezone.localize(
                                        datetime(*(time.strptime(seperated[1], time_parse)[0:6]))).timestamp()
                                )
                                , float(seperated[2])))
                    if seperated[3] != "":
                        hobo_2_data[hobo_2_meaning[1]].append(
                            (int(auto_timezone.localize(
                                datetime(*(time.strptime(seperated[1], time_parse)[0:6]))).timestamp()
                                 ), float(seperated[3])))
                else:
                    if seperated[2] != "":
                        hobo_2_data[hobo_2_meaning[0]].append(
                            (int((datetime.strptime(seperated[1], time_parse) + manual_offset).timestamp()),
                             float(seperated[2])))
                    if seperated[3] != "":
                        hobo_2_data[hobo_2_meaning[1]].append(
                            (int((datetime.strptime(seperated[1], time_parse) + manual_offset).timestamp()),
                             float(seperated[3])))
            except:
                pass
        for i in hobo_2_meaning:
            hobo_2_data[i].sort()
            hobo_2_np[i] = np.array(hobo_2_data[i], dtype=[("timestamp", np.uint32), ("value", np.float16)])
    return hobo_1_np, hobo_2_np


firstDate = None


def hobo_process(hobo_1_np: dict, hobo_2_np: dict):  # output will be 15 minutes chunks
    global firstDate
    if hobo_1_enabled:
        dayRange = (datetime.fromtimestamp(next(iter(hobo_1_np.values()))[-1][0]).date() - datetime.fromtimestamp(
            next(iter(hobo_1_np.values()))[0][0]).date()).days + 1
        firstDate = datetime.fromtimestamp(next(iter(hobo_1_np.values()))[0][0])
    else:
        dayRange = (datetime.fromtimestamp(next(iter(hobo_2_np.values()))[-1][0]).date() - datetime.fromtimestamp(
            next(iter(hobo_2_np.values()))[0][0]).date()).days + 1
        firstDate = datetime.fromtimestamp(next(iter(hobo_2_np.values()))[0][0])

    sectionRange = dayRange * total_period
    result = np.zeros((len(hobo_1_meaning) + len(hobo_2_meaning) * (3 if unknown_for_fringes else 2), sectionRange),
                      np.float16)
    if hobo_1_enabled:
        for (device, state), values in hobo_1_np.items():
            firstSlotTimestamp=int(timeconverter(values[0][0]).replace(hour=0, minute=0, second=0, microsecond=0).timestamp())
            # firstSlotTimestamp = values[0][0] - (values[0][0] % (min_in_day * 60))
            interpFunc = scipy.interpolate.interp1d(values["timestamp"], values["value"], fill_value="extrapolate")
            firstSlot = (values[0][0] - firstSlotTimestamp) // (86400 // total_period)
            slotCount = (values[-1][0] - values[0][0]) // (86400 // total_period)
            for i in range(firstSlot, firstSlot + slotCount):
                result[hobo_1_meaning.index((device, state)), i] = interpFunc(
                    firstSlotTimestamp + i * (86400 // total_period))
    if hobo_2_enabled:
        minutesRange = dayRange * 24 * 60
        possible_states = 3 if unknown_for_fringes else 2

        for (user, device), values in hobo_2_np.items():
            firstSlotTimestamp=int(timeconverter(values[0][0]).replace(hour=0, minute=0, second=0, microsecond=0).timestamp())
            minutesState = np.zeros((possible_states, minutesRange), np.int8)
            # sequence: 0, 1, unknown (for axis 0 of minuteState)
            if unknown_for_fringes:
                minutesState[2, :] = 1
            for timestamp, value in values:
                if int(value) == 1:
                    minutesState[1, (timestamp - firstSlotTimestamp) // 60::] = 1
                    minutesState[0, (timestamp - firstSlotTimestamp) // 60::] = 0
                else:
                    minutesState[0, (timestamp - firstSlotTimestamp) // 60::] = 1
                    minutesState[1, (timestamp - firstSlotTimestamp) // 60::] = 0
                if unknown_for_fringes:
                    minutesState[2, (timestamp - firstSlotTimestamp) // 60::] = 0
            minutesState[(0, 1), (values[-1][0] - firstSlotTimestamp) // 60 + 1::] = 0
            if unknown_for_fringes:
                minutesState[2, (values[-1][0] - firstSlotTimestamp) // 60 + 1::] = 1
            reshaped = np.reshape(minutesState, (
                possible_states, dayRange * total_period, min_in_day // total_period)).sum(
                axis=2)
            result[len(hobo_1_meaning) + hobo_2_meaning.index((user, device)) * possible_states:len(
                hobo_1_meaning) + hobo_2_meaning.index((user, device)) * possible_states + possible_states,
            ::] = reshaped

    return result


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

# print out loaded JSON for testing
# for x in data:
#     print("%s: %d" % (x, data[x]))  # adjust fields in this example
# subjectIdDict = defaultdict(list)
# subjectIdCounter = 1

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

result = hobo_process(*file_preprocess(hobo_1_filename, hobo_2_filename))
# print(device)


# datesCountained = len(list(slotDict.values())[0])

querys = []

if hobo_1_enabled and hobo_2_enabled:
    validStateList = state_list
elif hobo_1_enabled:
    validStateList = state_list[0:6]
else:
    validStateList = state_list[6::]

for device, status in validStateList:
    currentDate = firstDate

    for chunk in chunks(result[state_list.index((device, status)), :], total_period):
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
all_zeroes = ",".join(total_period * ["0"])
list(map(lambda x: print(x[2]), filter(lambda x: all_zeroes not in x[2], querys)))
list(map(lambda x: cursor.execute(x[2]), filter(lambda x: all_zeroes not in x[2], querys)))
db.commit()
db.close()  # close DB connection
