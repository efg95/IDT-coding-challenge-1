import ipinfo
import pprint
from tkinter import *
# import tkinter as tk
from pymongo import MongoClient
import datetime
from tkinter import ttk
import folium
from IPython.display import display
import webbrowser, os
import boto3
import phonenumbers as pn
import pycountry



#### CREATES DATABASE in local computer
client = MongoClient()
client = MongoClient('mongodb://localhost:27017/')
mydb = client["mydatabase"] # create database called "mydatabase"
mycol = mydb["locations"] # create a collection called locations

#the ipaddress package i use to retrieve geolocation
access_token = 'e2a9f66eee466e' #THIS IS MY OWN ACCESS CODE, YOU MAY USE IT, OR USE YOUR OWN
handler = ipinfo.getHandler(access_token)

#SNS amazon client
client = boto3.client("sns", aws_access_key_id = "AKIAIQ5OH6ZAJTWZRGWQ",
                    aws_secret_access_key = "oggvccasjB00uaczBMwVZAktbbT5v4UwTjXJ+IGr",
                        region_name = "us-east-1")

#Button option that appears if get N location number > than size(database)
def buttonOption():
    newOption = Toplevel()
    msg = Message(newOption,
    text="Number entered is greater than database size, click Dismiss to try a new number or Continue to return all documents in collection")
    msg.pack()
    button1 = Button(newOption, text="Dismiss", command=newOption.destroy)
    button1.pack()
    button2 = Button(newOption, text="Continue", command=getHistory)
    button2.pack()


#retrieves the location in a webpage, or via SMS
def getLocation(SNS):
    # print (e1.get() )# This is the text you may want to use later
    ip_address = e1.get()
    try:
        details = handler.getDetails(ip_address)
        sms = False
        if len(ip_address) == 0:
            ip_address = details.ip

        location = details.country_name
        city = details.city #use for google maps pop up
        pprint.pprint(details.all)
        latitude = details.latitude
        longitude = details.longitude
        loc = (latitude, longitude)
        # print(type(loc))
        map = folium.Map(location=loc, zoom_start=12)
        folium.Marker(location=loc, icon=folium.Icon(color='red', icon='cloud')).add_to(map)
        map.save("mymap.html")
        if SNS == False:
            webbrowser.open('file://' +os.path.realpath('mymap.html')) #in case this doesn't work

        #should add datetime tomorrow
        history = {"ip address": ip_address, "location": location.lower(), "city": city, "date": datetime.datetime.utcnow()}
        x = mycol.insert_one(history)
        return history
    except:
        newErrorWindow()

#checks the button for improper input
def getNLocation():
    # print(e2.get())
    number = e2.get()
    # print(type(number))
    if number.isdigit():
        number = int(number)
        if number == 0:
            newErrorWindow()
        elif number > mycol.count():
            # print(mycol.count())
            buttonOption()
        else:
            getNHistory(number)
    else:
        newErrorWindow()

#retrieves the information for N Locations if input is good
def newNLocation(history, number):
    newInfo = Toplevel()
    newInfo.wm_title("last " + str(number) + " ip address locations searched")
    S = Scrollbar(newInfo)
    text = Text(newInfo, height=4, width=50)
    S.pack(side=RIGHT, fill = Y)
    text.pack(side=LEFT, fill=Y)
    S.config(command=text.yview)
    text.config(yscrollcommand= S.set)
    text.insert(END, "last " + str(number) + " in descending order \n")
    for i in range(len(history)):
        # print(history[i])
        text.insert(END, history[i][0] + " " + str(history[i][1]) + '\n')


    button = Button(newInfo, text="Dismiss", command=newInfo.destroy)
    button.pack()

def getNHistory(number):
    # print("hi getNhistory")
    history = []
    output = mycol.find().sort("date", -1).limit(number)
    for x in output:
        # history.append((x["location"], x["city"], x["date"]))
        history.append([x["location"], x["date"]])
    # print(history)
    newNLocation(history, number)

#pushed out all location history
def getHistory():
    #print("hi")
    history = []
    for x in mycol.find({}, {"location":1, "city":1, "ip address":1, "_id":0}):
        history.append((x["location"], x["city"], x["ip address"]))
    # print(history)
    newWindow(history)

def newWindow(history):
    newInfo = Toplevel()
    newInfo.wm_title("history of locations from searched IP addresses")
    S = Scrollbar(newInfo)
    text = Text(newInfo, height=4, width=50)
    S.pack(side=RIGHT, fill = Y)
    text.pack(side=LEFT, fill=Y)
    S.config(command=text.yview)
    text.config(yscrollcommand= S.set)
    text.insert(END, "ALL SEARCHED HISTORY:" + "\n")
    for i in range(len(history)):
        text.insert(END, history[i][0] + ", " + history[i][1] + ", " + history[i][2] + '\n')

    button = Button(newInfo, text="Dismiss", command=newInfo.destroy)
    button.pack()

def newErrorWindow():
    newError = Toplevel()
    newError.wm_title("error, only integers allowed in input")
    label = Label(newError, text="only integer variable allowed")
    label.pack()
    button = Button(newError, text="Dismiss", command=newError.destroy)
    button.pack()

def dateError():
    newError = Toplevel()
    newError.wm_title("invalid date entered")
    label = Label(newError, text="ALL ENTRIES \n MUST BE FILLED \n IF U WANT TO GET A SINGLE DATE \n DAY FROM AND TO MUST BE THE SAME DATE")
    label.pack()
    button = Button(newError, text="Dismiss", command=newError.destroy)
    button.pack()

def getDateRange():
    # print("day from: ", comboDayFrom.get(), " month from: ", comboMonthFrom.get(), " year from: ", comboYearFrom.get())
    # print("day To: ", comboDayTo.get(), " month To: ", comboMonthTo.get(), " year from: ", comboYearTo.get())
    if (len(comboDayFrom.get()) == 0) or (len(comboMonthFrom.get()) == 0) or (len(comboYearFrom.get()) == 0) or (len(comboDayTo.get()) == 0) or (len(comboMonthTo.get()) == 0) or (len(comboYearTo.get()) == 0) :
        dateError()
    else:
        history = []
        months = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4,
                "May": 5, "Jun": 6, "Jul": 7, "Aug": 8,
                "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}


        monthFrom = int(months[comboMonthFrom.get()])
        dayFrom = int(comboDayFrom.get())
        yearFrom = int(comboYearFrom.get())
        dateFROM = comboYearFrom.get()+ "-"+ comboMonthFrom.get()+ "-" + comboDayFrom.get()
        # print(yearFrom, "-", monthFrom, "-", dayFrom)

        monthTo = int(months[comboMonthTo.get()])
        dayTo = int(comboDayTo.get()) + 1
        yearTo = int(comboYearTo.get())
        # print(yearTo, "-", monthTo, "-", dayTo)
        dateTO = comboYearTo.get() + "-" + comboMonthTo.get() + "-" + comboDayTo.get()

        date = mycol.find({"date" : {"$gte" : datetime.datetime(yearFrom, monthFrom, dayFrom), "$lte" : datetime.datetime(yearTo, monthTo, dayTo)}})
        for docs in date:
            history.append([docs["location"], docs["city"], docs["ip address"], docs["date"]])
        dateRangeNewWindow(history, dateFROM, dateTO)

def dateRangeNewWindow(history, dateFROM, dateTO):
    newInfo = Toplevel()
    newInfo.geometry("500x500")
    newInfo.wm_title("From " + dateFROM + " to " + dateTO)
    S = Scrollbar(newInfo)
    text = Text(newInfo, height=4, width=50)
    S.pack(side=RIGHT, fill = Y)
    text.pack(side=LEFT, fill=Y)
    S.config(command=text.yview)
    text.config(yscrollcommand= S.set)
    text.insert(END, "From " + dateFROM + " to " + dateTO + ": \n \n")
    for i in range(len(history)):
        # print(history[i])
        text.insert(END, history[i][0] + ", " + history[i][1] + ", " + str(history[i][2]) + ":\n" + "DATE: " + str(history[i][3]) + '\n' + '\n')


    button = Button(newInfo, text="Dismiss", command=newInfo.destroy)
    button.pack()

#BELOW 3 METHODS handle desire to retrieve location via SMS
def sendNumber(phoneEntry, i_code):
    i = i_code.get()
    i_temp = i.split(" ", 1)
    international_code = i_temp[1]
    # print(international_code)
    phoneNumber = "+" + international_code + phoneEntry.get()
    # print(phoneNumber)
    SNS = True
    message = getLocation(SNS)
    # print(message)
    msg = "your ip address searched is: " + str(message["ip address"]) + "\n" + "The location found is: " + str(message["location"]) + ", " + str(message["city"])+ "\n"
    # print(msg)
    client.publish(PhoneNumber=phoneNumber, Message=msg)

def newWindowPhone(I_list):
    newPhone = Toplevel()
    # newPhone.geometry("200x200")
    newPhone.focus_set()
    newPhone.wm_title("Enter Phone Number")
    labelcode = Label(newPhone, text = "International Code").grid(row=0, column =0)
    i_code = ttk.Combobox(newPhone, values=I_list, state="readonly", width =8)
    i_code.grid(row=0, column=1)
    phoneEntry = Entry(newPhone)
    phoneEntry.grid(row=0, column=2)
    buttonConfirm = Button(newPhone, text="confirm number to send location notification", width = 47, height=3, command=lambda: sendNumber(phoneEntry, i_code))
    buttonConfirm.grid(row=1, columnspan=3)
def getSMS():
    # print(e3.get())
    I_list = []
    for c in pycountry.countries:
        I_list.append((c.alpha_2, pn.country_code_for_region(c.alpha_2)))
    newWindowPhone(I_list)

#QUERY BASED ON country
def newErrorWin():
    newError = Toplevel()
    label = Label(newError, text="NO COUNTRIES FOUND WITH THAT INPUT")
    label.pack()
    button = Button(newError, text="click to dismiss", command=newError.destroy)
    button.pack()

def getSpecificCountry():
    print(e_location_history.get())
    input = e_location_history.get()
    input.lower()
    location = mycol.find({"location" : input})
    history = []
    if location.count() == 0:
        newErrorWin()
    else:
        for x in location:
            print(x)
            history.append(x)

#this prints our all the current locations searched by user
# for x in mycol.find():
#     print(x)
# print(mydb.locations.find())
master = Tk()
master.geometry("800x300")
master.wm_title("IPADDRESS LOCATOR, AND DATABASE HISTORY QUERY")
lbl = Label(master, text="Enter in an ipaddress below and click either option. \nReturns your current ip address location if no input:", width = 40)
lbl.grid(row=0, columnspan=2)
e1 = Entry(master, width = 40)
e2 = Entry(master)
e1.grid(row=1, column =0, columnspan=2)
e2.grid(row=4, column =1)
SNS = False

b = Button(master, text = "Click to get location \n via webpage", width = 18, height=3,  command =lambda: getLocation(SNS))
b.grid(row=2, rowspan = 2)
# b.pack()

b2 = Button(master, text = "Last N locations", width = 18,  command = getNLocation)
b2.grid(row=4)

#combobox for dates
days = []
for i in range(1, 32):
    days.append(i)
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
years = []
for i in range(1991, 2201):
    years.append(i)

labelDayFrom = Label(master, text = "Day From", width = 8).grid(row=0, column =3)
comboDayFrom = ttk.Combobox(master, values=days, state="readonly", width =8)
comboDayFrom.grid(row=1, column=3)
labelMonthFrom = Label(master, text = "Month From", width =8).grid(row=0, column = 4)
comboMonthFrom = ttk.Combobox(master, values=months, state="readonly", width = 8)
comboMonthFrom.grid(row=1, column=4)
labelYearFrom = Label(master, text = "Year From", width=8).grid(row=0, column=5)
comboYearFrom = ttk.Combobox(master, values=years, width=8, state="readonly")
comboYearFrom.grid(row=1, column=5)

labelDayTo = Label(master, text = "Day To", width = 8).grid(row=2, column =3)
comboDayTo = ttk.Combobox(master, values=days, state="readonly", width =8)
comboDayTo.grid(row=3, column=3)
labelMonthTo = Label(master, text = "Month To", width =8).grid(row=2, column = 4)
comboMonthTo = ttk.Combobox(master, values=months, state="readonly", width = 8)
comboMonthTo.grid(row=3, column=4)
labelYearTo = Label(master, text = "Year To", width=8).grid(row=2, column=5)
comboYearTo = ttk.Combobox(master, values=years, width=8, state="readonly")
comboYearTo.grid(row=3, column=5)



buttonDate = Button(master, text="Click to confirm \n date range", command=getDateRange, height=7)
buttonDate.grid(row=0, column=6, rowspan=4)



b3 = Button(master, text="Click for a history of all locations found", command = getHistory, width=40, height=3)
b3.grid(row=5, columnspan=2, rowspan=2)

# e3 = Entry(master)
# e3.grid(row=4, column =1, sticky=W)
# labelPhone = Label(master, text="Enter phone number: ", width=18).grid(row=4)
b4_phone = Button(master, text="Click to get location \n via sms", command = getSMS, width=21, height=3)
b4_phone.grid(row=2, column = 1, rowspan=2,)

b5_specific_location = Button(master, text="query specific country", command = getSpecificCountry, width=18)
b5_specific_location.grid(row=7, column=0)
e_location_history = Entry(master)
e_location_history.grid(row=7, column=1)




mainloop()
