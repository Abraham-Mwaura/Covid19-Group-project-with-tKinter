from os import name
from threading import Timer
from tkinter import *
from tkinter import font
from PIL import ImageTk, Image
from tkinter import messagebox
import pandas as pd
import requests
import json
import pyrebase
import webbrowser
import mysql.connector
from sqlalchemy import create_engine
import serial
import time
from tkinter import ttk
from tkinter.font import BOLD

from sqlalchemy.engine import result
from sqlalchemy.sql.expression import label, text

#from tooltip import ToolTip
#from tkinter.constants import BOTH

my_conn = create_engine("mysql+mysqldb://root:root@localhost/users")

name=''
def get_data():
    apidata = requests.get("https://api.covid19api.com/summary").text
    # loading the string into python and converting it into
    apidata_info = json.loads(apidata)

    # parsing through the dictionary and extracting the info we need
    country_list = []
    for country_info in apidata_info['Countries']:
        country_list.append([country_info['Country'], country_info['TotalConfirmed'],
                            country_info['TotalDeaths'], country_info['Date']])
    # appends the global data at the end of the database
    country_list.append(["Global", apidata_info["Global"]['TotalConfirmed'],
                        apidata_info["Global"]['TotalDeaths'], apidata_info["Global"]['Date']])

    country_df = pd.DataFrame(data=country_list, columns=[
                              'Country', 'TotalConfirmed', 'TotalDeaths', 'Date'])
    country_df.index_name = "Country"
    country_df.head()

    mycursor1 = myDb.cursor()
    mycursor1.execute("DROP TABLE live_cases")
    mycursor1.execute(
        "CREATE TABLE live_cases(Country VARCHAR(255),TotalConfirmed VARCHAR(255),TotalDeaths VARCHAR(255),Date VARCHAR(255))")

    country_df.to_sql(con=my_conn, name='live_cases',
                      if_exists='append', index=False)


myDb = mysql.connector.connect(  # connecting to database
    host="127.0.0.1",
    user="root",
    password="root",
    database="users"
)

myCursor = myDb.cursor()
# the function get_data in executed after every five minutes
t = Timer(60.0, get_data)
t.start()
# this line of code is run on the 1st instance of the code
#myCursor.execute( "CREATE DATABASE users ")
#myCursor.execute("CREATE TABLE userinfo(firstname VARCHAR(30),secondname VARCHAR(30),username VARCHAR(30),email VARCHAR(30),password VARCHAR(30))")


Config = {
    # this data is stored as a dictionary; they are the parameters for firebase connection
    "apiKey": "AIzaSyDusq6Crtup5gEtC7uTvtMtkDZjuJorQQc",
    "authDomain": "covid-19-group-project.firebaseapp.com",
    "databaseURL": "https://covid-19-group-project-default-rtdb.firebaseio.com",
    "projectId": "covid-19-group-project",
    "storageBucket": "covid-19-group-project.appspot.com",
    "messagingSenderId": "320687700566",
    "appId": "1:320687700566:web:2b18881b3850ae72b6d9f7",
    "measurementId": "G-PNJPHDFBMC"
}
# Initialize Firebase


def connFirebase():
    global db
    firebase = pyrebase.initialize_app(Config)
    print(firebase)
    db = firebase.database()


fbTimer = Timer(6.0, connFirebase)
fbTimer.start()


# create the first instance of the screen
root = Tk()
# This is the title for our app
root.title("Covid1-19 Tracker and predictions")
# App logo
root.iconbitmap(
    "C:/Users/use/Desktop/Covid-19 Group project/images/logo_icon.ico")
# The initial set size for our app
#root.geometry("1600x900")
root.state('zoomed') 
#root.attributes('-fullscreen', True)


# creating the first frame
frame = Frame(root)
# this ensures that the frame spans in the whole window
frame.place(x=0, y=0, relheight=1, relwidth=1, anchor=NW)

# mounting the image on the frame
Label(frame, text="Wash your hands, sanitize & Observe social distancing ", fg="#2E8BC0", font= 'helvetica 15 bold').place(relx= 0.32, rely=0.1)

my_img = ImageTk.PhotoImage(Image.open("images/logo_icon.ico"))
my_icon = Label(frame, image=my_img)
my_icon.place(rely=0.18148, relx=0.27, relheight=0.333, relwidth=0.1875)


label_haveAccount = Label(
    frame, text="Already have an account?", anchor=W, font='helvetica 15 bold')
label_haveAccount.place(relx=0.5, rely=0.1848)

label_username = Label(frame, text="username", anchor=W,
                       font='helvetica  15 bold ')
label_username.place(relx=0.5199, rely=0.2644)

enter_usernamel = Entry(frame, width=30, font='helvetica  15')
enter_usernamel.place(relx=0.5, rely=0.3233)


label_password = Label(frame, text="Password", anchor=W,
                       font='helvetica  15 bold')
label_password.place(relx=0.5199, rely=0.3822)

enter_passwordl = Entry(frame, width=30, font='helvetica 15')
enter_passwordl.place(relx=0.5, rely=0.4411)


def global_window():
    global globe_welcome_Label, world_label
    global icon_backHome, icon_backHome1, icon_world, icon_world1
    frame_globe = Frame(root)
    frame_globe.place(x=0, y=0, relheight=1, relwidth=1, anchor=NW)
    frame.forget()

    icon_world = Image.open(
        "C:/Users/use/Desktop/Covid-19 Group project/images/world.jpg")
    icon_world = icon_world.resize((1600, 900), Image.ANTIALIAS)
    icon_world1 = ImageTk.PhotoImage(icon_world)
    world_label = Label(frame_globe, image=icon_world1)
    world_label.place(x=0, y=0, relheight=1, relwidth=1, anchor=NW)

    # using treeview to display the data from the data  from the database
    trv = ttk.Treeview(frame_globe, selectmode='browse')
    vsb = ttk.Scrollbar(frame_globe, orient="vertical", command=trv.yview)
    vsb.place(relx=0.900, rely=0.1, relheight=0.856)
    trv.configure(yscrollcommand=vsb.set)

    trv.place(relx=0.0668, rely=0.1, relheight=0.856, relwidth=0.856)
    # number of columns
    trv["columns"] = ("1", "2", "3", "4")

    # Defining heading
    trv['show'] = 'headings'

    # width of columns
    trv.column("1", width=300)
    trv.column("2", width=300)
    trv.column("3", width=300)
    trv.column("4", width=300)
    # trv.pack(fill=BOTH,expand=1)

    # respective columns
    trv.heading("1", text="Country")
    trv.heading("2", text="TotalConfirmed")
    trv.heading("3", text="TotalDeaths")
    trv.heading("4", text="Date")

    # getting data from MySQL table
    results = my_conn.execute('''SELECT * from live_cases''')
    for dt in results:
        trv.insert("", 'end', iid=dt[0], text=dt[0],
                   values=(dt[0], f'{int(dt[1]):,}', f'{int(dt[2]):,}', dt[3]))

    def globalWindowQuit():
        frame_globe.place_forget()

    icon_backHome = Image.open(
        "C:/Users/use/Desktop/Covid-19 Group project/images/backHome_icon.png")
    icon_backHome = icon_backHome.resize((70, 50), Image.ANTIALIAS)
    icon_backHome1 = ImageTk.PhotoImage(icon_backHome)
    backHome_btn = Button(frame_globe, image=icon_backHome1,
                          relief=RAISED, command=globalWindowQuit)
    backHome_btn.grid(row=0, column=0, pady=5)


def yourHealth_window():
    global health_welcLabel,tempSum
    global icon_backHome, icon_backHome1, predict1, text1, text2, predict2, predict3

    frame_health = Frame(root)
    frame_health.place(x=0, y=0, relheight=1, relwidth=1, anchor=NW)
    frame.forget()

    health_welcLabel = Label(
        frame_health, text="This is the Customers Health Window", font="Helvetica  25 bold")
    health_welcLabel.grid(column=1, row=0, rowspan=4)

    def HealthWindowQuit():
        frame_health.place_forget()

    icon_backHome = Image.open(
        "C:/Users/use/Desktop/Covid-19 Group project/images/backHome_icon.png")
    icon_backHome = icon_backHome.resize((70, 50), Image.ANTIALIAS)
    icon_backHome1 = ImageTk.PhotoImage(icon_backHome)
    backHome_btn = Button(frame_health, image=icon_backHome1,
                          relief=RAISED, command=HealthWindowQuit)
    backHome_btn.grid(row=0, column=0, pady=5)

    def measureTemp():
        serInit = serial.Serial('COM5', 9600)
        # delay 2s
        time.sleep(2)
        global tempSum
        tempSum = 0
        global countTemp
        countTemp = 0

        def ReadData():
            global i
            for i in range(10):
                # reads serial data in byte string
                byteTemp = serInit.readline()

            # convert byte code to unicode string
                UniTemp1 = byteTemp.decode()
            # removes escape characters
                global UniTemp2
                UniTemp2 = UniTemp1.rsplit()

            # Typecasts string to float
                pointTemp = float(UniTemp2[0])
                print(pointTemp)
                # arData.append(UniTemp2)
                # temp_label = Label(frame_health, text=str(pointTemp))
                # temp_label.grid(column=4, row=4)

                global tempSum

                tempSum += pointTemp
                time.sleep(0.5)

            serInit.close()
        # Find average temperature
        # execute function
        ReadData()

        # close serial port

        def avg(a, b):
            return a/b
        # final temperature
        finalTemp = round(avg(tempSum, 10), 1)

        avgTemp_label = Label(
            frame_health, text="Your Average temperature is \n " + str(finalTemp)+u"\N{DEGREE SIGN}"+"C ", font= 'helvetica 20 bold')
        avgTemp_label.grid(column=5, row=8)

        #print("Your temperature is= ", finalTemp, "C")

    measureTemp_Btn = Button(
        frame_health, text="Click here to measure temperature", command=measureTemp, fg="#2E8BC0", font="helvetica 15 bold")
    measureTemp_Btn.place(relx=0.6, rely=0.125)

    t1 = IntVar()
    t2 = IntVar()
    t3 = IntVar()
    t4 = IntVar()
    t5 = IntVar()
    t6 = IntVar()
    t7 = IntVar()
    t8 = IntVar()
    t9 = IntVar()
    t10 = IntVar()
    t11 = IntVar()
    t12 = IntVar()
    t13 = IntVar()
    t14 = IntVar()
    t15 = IntVar()
    t16 = IntVar()
    t17 = IntVar()
    t18 = IntVar()
    text1 = ''
    text2 = ''

    def exposureRate():
        global predict1
        predict1 = t1.get()+t2.get()+t3.get()+t4.get()+t18.get()
        # +t5.get()+t6.get()+t7.get()+t8.get()
        Label(frame_health, text="Your exposure rate is :"+str(predict1)+"%" +
              "\n", fg="#2E8BC0", font="helvetica 15 bold", ).grid(row=9, column=1)
    exposureRate()

    Label(frame_health, text='Have you been in contact with a confirmed COVID-19 patient?',
          font=0.1).grid(row=4, column=1, sticky=W, padx=20)
    Radiobutton(frame_health, text='Yes', variable=t1, value=20,
                command=exposureRate, font=0.1).grid(row=4, column=2, sticky=W)
    Radiobutton(frame_health, text='No', variable=t1, value=0.00,
                command=exposureRate, font=0.1).grid(row=4, column=3, sticky=W)

    Label(frame_health, text="Have you  traveled from a country declared as a hotspot zone?",
          font=0.1).grid(row=5, column=1, sticky=W, padx=20)
    Radiobutton(frame_health, text='Yes', variable=t2, value=20,
                command=exposureRate, font=0.1).grid(row=5, column=2)
    Radiobutton(frame_health, text='No', variable=t2, value=0.00,
                command=exposureRate, font=0.1).grid(row=5, column=3)

    Label(frame_health, text="Do have asthma, chronic bronchitis, pulmonary hypertension,diabetes,\n sickle cell anaemia, chronic liver or kidney disease?",
          font=0.1).grid(row=6, column=1, sticky=W, padx=20, pady=2.5)
    Radiobutton(frame_health, text='Yes', variable=t3, value=20,
                command=exposureRate, font=0.1).grid(row=6, column=2)
    Radiobutton(frame_health, text='No', variable=t3, value=0.00,
                command=exposureRate, font=0.1).grid(row=6, column=3)

    Label(frame_health, text='Are you living in a town declared as Covid-19  hotspot zone?',
          font=0.1).grid(row=7, column=1, sticky=W, padx=20, pady=2.5)
    Radiobutton(frame_health, text='yes', variable=t4, value=20,
                command=exposureRate, font=0.1).grid(row=7, column=2)
    Radiobutton(frame_health, text='No', variable=t4, value=0.00,
                command=exposureRate, font=0.1).grid(row=7, column=3)

    Label(frame_health, text='Have you been vaccinated?', font=0.1).grid(
        row=8, column=1, sticky=W, padx=20, pady=2.5)
    Radiobutton(frame_health, text='Yes', variable=t18, value=0.00,
                command=exposureRate, font=0.1).grid(row=8, column=2)
    Radiobutton(frame_health, text='No', variable=t18, value=20,
                command=exposureRate, font=0.1).grid(row=8, column=3)

    def symptomsPercent():
        global predict2
        predict2 = t5.get()+t6.get()+t7.get()+t8.get()
        Label(frame_health, text="Your severe symptoms percentage rate is :" +
              str(predict2)+"\n", fg="#2E8BC0", font="helvetica 15 bold",).grid(row=14, column=1)
    symptomsPercent()

    Label(frame_health, text='Does patient have a temperature higher than 38??c?',
          font=0.1).grid(row=10, column=1, sticky=W, padx=20, pady=2.5)
    Radiobutton(frame_health, text='yes', variable=t5, value=25,
                command=symptomsPercent, font=0.1).grid(row=10, column=2)
    Radiobutton(frame_health, text='No', variable=t5, value=0.00,
                command=symptomsPercent, font=0.1).grid(row=10, column=3)

    Label(frame_health, text='Does patient have chest pain or pressure',
          font=0.1).grid(row=11, column=1, sticky=W, padx=20, pady=2.5)
    Radiobutton(frame_health, text='yes', variable=t6, value=25,
                command=symptomsPercent, font=0.1).grid(row=11, column=2)
    Radiobutton(frame_health, text='No', variable=t6, value=0.00,
                command=symptomsPercent, font=0.1).grid(row=11, column=3)

    Label(frame_health, text='Does patient have trouble breathing').grid(
        row=12, column=1, sticky=W, padx=20, pady=2.5)
    Radiobutton(frame_health, text='yes', variable=t7, value=25,
                command=symptomsPercent, font=0.1).grid(row=12, column=2)
    Radiobutton(frame_health, text='No', variable=t7, value=0.00,
                command=symptomsPercent, font=0.1).grid(row=12, column=3)

    Label(frame_health, text='Is  Patient experiencing loss of speech or movement?',
          font=0.1).grid(row=13, column=1, sticky=W, padx=20, pady=2.5)
    Radiobutton(frame_health, text='yes', variable=t8, value=25,
                command=symptomsPercent, font=0.1).grid(row=13, column=2)
    Radiobutton(frame_health, text='No', variable=t8, value=0.00,
                command=symptomsPercent, font=0.1).grid(row=13, column=3)

    def mildSymptoms():
        global predict3
        predict3 = t9.get()+t10.get()+t11.get()+t12.get()+t13.get() + \
            t14.get()+t15.get()+t16.get()+t17.get()
        Label(frame_health, text="mild symptoms%:"+str(predict3)+"\n",
              fg="#2E8BC0", font="helvetica 15 bold",).grid(row=24, column=1)
    mildSymptoms()

    Label(frame_health, text="Does patient have a fever?", anchor=W,
          font=0.1).grid(row=15, column=1, sticky=W, padx=20, pady=2.5)
    Radiobutton(frame_health, text='yes', variable=t9, value=10,
                command=mildSymptoms, font=0.1).grid(row=15, column=2)
    Radiobutton(frame_health, text='No', variable=t9, value=0.00,
                command=mildSymptoms, font=0.1).grid(row=15, column=3)

    Label(frame_health, text='Does patient have a dry cough?', font=0.1).grid(
        row=16, column=1, sticky=W, padx=20, pady=2.5)
    Radiobutton(frame_health, text='yes', variable=t10, value=10,
                command=mildSymptoms, font=0.1).grid(row=16, column=2)
    Radiobutton(frame_health, text='No', variable=t10, value=0.00,
                command=mildSymptoms, font=0.1).grid(row=16, column=3)

    Label(frame_health, text='Does patient have a running nose?',
          font=0.1).grid(row=17, column=1, sticky=W, padx=20, pady=2.5)
    Radiobutton(frame_health, text='yes', variable=t11, value=10,
                command=mildSymptoms, font=0.1).grid(row=17, column=2)
    Radiobutton(frame_health, text='No', variable=t11, value=0.00,
                command=mildSymptoms, font=0.1).grid(row=17, column=3)

    Label(frame_health, text='Is patient experiencing loss of smell or taste?',
          font=0.1).grid(row=18, column=1, sticky=W, padx=20, pady=2.5)
    Radiobutton(frame_health, text='yes', variable=t12, value=10,
                command=mildSymptoms, font=0.1).grid(row=18, column=2)
    Radiobutton(frame_health, text='No', variable=t12, value=0.00,
                command=mildSymptoms, font=0.1).grid(row=18, column=3)

    Label(frame_health, text="Does patient have a sore throat?", font=0.1).grid(
        row=19, column=1, sticky=W, padx=20, pady=2.5)
    Radiobutton(frame_health, text='yes', variable=t13, value=10,
                command=mildSymptoms, font=0.1).grid(row=19, column=2)
    Radiobutton(frame_health, text='No', variable=t13, value=0.00,
                command=mildSymptoms, font=0.1).grid(row=19, column=3)

    Label(frame_health, text='Is patient experiencing loss of appetite?',
          font=0.1).grid(row=20, column=1, sticky=W, padx=20, pady=2.5)
    Radiobutton(frame_health, text='yes', variable=t14, value=10,
                command=mildSymptoms, font=0.1).grid(row=20, column=2)
    Radiobutton(frame_health, text='No', variable=t14, value=0.00,
                command=mildSymptoms, font=0.1).grid(row=20, column=3)

    Label(frame_health, text='Is patient experiencing fatigue?', font=0.1).grid(
        row=21, column=1, sticky=W, padx=20, pady=2.5)
    Radiobutton(frame_health, text='yes', variable=t15, value=10,
                command=mildSymptoms, font=0.1).grid(row=21, column=2)
    Radiobutton(frame_health, text='No', variable=t15, value=0.00,
                command=mildSymptoms, font=0.1).grid(row=21, column=3)

    Label(frame_health, text='Does patient have diarrhea?', font=0.1).grid(
        row=22, column=1, sticky=W, padx=20, pady=2.5)
    Radiobutton(frame_health, text='yes', variable=t16, value=10,
                command=mildSymptoms, font=0.1).grid(row=22, column=2)
    Radiobutton(frame_health, text='No', variable=t16, value=0.00,
                command=mildSymptoms, font=0.1).grid(row=22, column=3)

    Label(frame_health, text='Does patient have muscle or joint pain',
          font=0.1).grid(row=23, column=1, sticky=W, padx=20, pady=2.5)
    Radiobutton(frame_health, text='yes', variable=t17, value=10,
                command=mildSymptoms, font=0.1).grid(row=23, column=2)
    Radiobutton(frame_health, text='No', variable=t17, value=0.00,
                command=mildSymptoms, font=0.1).grid(row=23, column=3)

    def recommendations():
        global text2, text1

        top = Toplevel()
        top.geometry("400x200")
        top.title("RECOMMENDATIONS")

        test_percentage = (predict1+predict2+predict3)/3
        #Label(top,text='Your test Percentage is '+ str(test_percentage) ).grid(row=25,column=1)
        #messagebox.showinfo("RECCOMMENDATIONS",text+text1 )

    #Label(frame_health,text='RECCOMMENDATIONS ').grid(row=26,column=1)
        if(test_percentage == 0):
            text1 = '''You do not need to be tested for COVID-19.stay
                safe by taking  precautions,
                such as social distancing, wearing a  
                mask, keeping rooms well   ventilated, 
                avoiding crowds, 
                cleaning your hands, and coughing into 
                a bent elbow or tissue. '''

        if(test_percentage > 0 and test_percentage < 30):
            text1 = '''self-quarantine for 14 days\n.
                Monitor your health daily and If your symptoms get worse, 
                call your health care provider immediately.'''

        if(test_percentage > 30 and test_percentage < 50):
            text1 = '"please get tested for covid 19"'

        if (test_percentage > 50 and test_percentage < 80):
            text1 = '''covid test percentage is higher than 50%!!\n 
            Please seek medical advice and call before going
            to nearest emergency department.'+ test_percentage'''

        if(test_percentage > 80):
            text1 = '''seek medical attention immediately!!!\n 
            Call before going to the nearest emergency department.\n\n'''

        # e is the exposure pecentage, predict 1

        # s is the severe sypmptoms percentage predict 2
        if(predict1 > 50):
            text2 = "you have more than 2 severe symptoms.\n Please seek medical advice as soon as possible and call before   going to nearest emergency department.\n\n"
        if (predict2 > 50):
            text2 = '"High risk exposure.\n Stay safe by taking  precautions, such as social distancing, wearing a   mask, keeping rooms well   ventilated, avoiding crowds, cleaning your hands, and coughing into a bent elbow or tissue.\n"'

        l2 = Label(top, text=text1 + "\n" + text2, font=10, fg="#2E8BC0")
        l2.pack()

    Button(frame_health, text="show Recommendations",
           command=recommendations).grid(row=34, column=1)





def developer_window():
    global dev_welcLabel
    global icon_backHome, icon_backHome1, icon_abraham1, icon_abraham, icon_trevor1, icon_trevor, icon_mirriam, icon_mirriam1

    frame_dev = Frame(root)
    frame_dev.place(x=0, y=0, relheight=1, relwidth=1, anchor=NW)
    frame.forget()

    # C:/Users/use/Desktop/Covid-19 Group project/images

    icon_abraham = Image.open(
        "C:/Users/use/Desktop/Covid-19 Group project/images/abraham.jpg")
    icon_abraham = icon_abraham.resize((200, 200), Image.ANTIALIAS)
    icon_abraham1 = ImageTk.PhotoImage(icon_abraham)
    abraham_btn = Button(frame_dev, image=icon_abraham1)
    abraham_btn.place(relx=0.061, rely=0.136)
    label_abraham = Label(frame_dev, text="Name :Abraham Mwaura\n\n Profession:Biomedical Engineering Student\nRoles:Team leader,GUI development\n\nSkills: Web Development,Desktop GUI development,Leadership, Strategist\n\n Languages and frameworks:C,C++,Python, Tkinter, React\n Contact: amwaura101@gmail.com", relief=FLAT, font="Helvetica  10")
    label_abraham.place(relx=0.01, rely=0.443, relheight=0.45, relwidth=0.34)

    icon_trevor = Image.open(
        "C:/Users/use/Desktop/Covid-19 Group project/images/trevor.jpg")
    icon_trevor = icon_trevor.resize((200, 200), Image.ANTIALIAS)
    icon_trevor1 = ImageTk.PhotoImage(icon_trevor)
    trevor_btn = Button(frame_dev, image=icon_trevor1)
    trevor_btn.place(relx=0.396, rely=0.136)
    label_trevor = Label(frame_dev, text="Name: Trevor Agola\n\n Profession: Electrical and Electronics Engineering\nRole: Microcontroller programming, Hardware Intergration, UI Design.\n\n Skills: Graphic design, Hardware Programming, team player, creative\n\n.Languages/Framework: C,C++, Arduino, Python, CSS\n.Contact: trevoragola5968@gmail.com ", relief=FLAT, font="Helvetica  10")
    label_trevor.place(relx=0.366, rely=0.443, relheight=0.45, relwidth=0.323)

    icon_mirriam = Image.open(
        "C:/Users/use/Desktop/Covid-19 Group project/images/mirriam.jpg")
    icon_mirriam = icon_mirriam.resize((200, 200), Image.ANTIALIAS)
    icon_mirriam1 = ImageTk.PhotoImage(icon_mirriam)
    mirriam_btn = Button(frame_dev, image=icon_mirriam1)
    mirriam_btn.place(relx=0.750, rely=0.136)
    label_mirriam = Label(frame_dev, text="Name: Mirriam Mwende Mbithi\n\nProfession: Electrical and Electronics Engineering student\nRole: Database Management, GUI development\n\nSkills: Database Management, GUI programming,\ngoal-oriented, team player\n\nLanguages/Frameworks: SQL,Tkinter,C++,C, Python\nContact: mirriammwende001@gmail.com", relief=FLAT, font="Helvetica  10")
    label_mirriam.place(relx=0.700, rely=0.443, relheight=0.45, relwidth=0.323)

    dev_welcLabel = Label(
        frame_dev, text="Developers Information", font="Helvetica  20 bold", padx=100)
    dev_welcLabel.grid(column=1, row=0)

    def devWindowQuit():
        frame_dev.place_forget()

    icon_backHome = Image.open(
        "C:/Users/use/Desktop/Covid-19 Group project/images/backHome_icon.png")
    icon_backHome = icon_backHome.resize((70, 50), Image.ANTIALIAS)
    icon_backHome1 = ImageTk.PhotoImage(icon_backHome)
    backHome_btn = Button(frame_dev, image=icon_backHome1,
                          relief=RAISED, command=devWindowQuit)
    backHome_btn.grid(row=0, column=0, pady=5)


def open_url(num):
    if num == 1:
        new_link = db.child("Story1").child("link").get()
        webbrowser.open(new_link.val())
    elif num == 2:
        new_link = db.child("Story2").child("link").get()
        webbrowser.open(new_link.val())
    elif num == 3:
        new_link = db.child("Story3").child("link").get()
        webbrowser.open(new_link.val())
    elif num == 4:
        new_link = db.child("Story4").child("link").get()
        webbrowser.open(new_link.val())
    elif num == 5:
        new_link = db.child("Story5").child("link").get()
        webbrowser.open(new_link.val())
    elif num == 6:
        new_link = db.child("Story6").child("link").get()
        webbrowser.open(new_link.val())
    elif num == 7:
        new_link = db.child("Story6").child("link").get()
        webbrowser.open(new_link.val())
    elif num == 8:
        new_link = db.child("Story6").child("link").get()
        webbrowser.open(new_link.val())
    else:
        return


def home_button():
    global name
    frame1 = Frame(root)

    frame1.place(x=0, y=0, relheight=1, relwidth=1, anchor=NW)
    frame.forget()

    def logOut():

        global response
        response = messagebox.askyesno(
            "log-out window", "Do you want to log out")
        if response == 1:
            frame1.place_forget()
        else:
            pass

    def icons():
        # This are the sidebar Menu icons
        global icon_menu, icon_globe, icon_programmer, icon_heartbeat, icon_info, ico_bg
        global menu_btn, globe_btn, programmer_btn, heartbeat_btn, info_btn
        global icon_menu1, icon_globe1, icon_programmer1, icon_heartbeat1, icon_info1, icon_bg1

        icon_bg = Image.open(
            "C:/Users/use/Desktop/Covid-19 Group project/images/bg_icon.png")
        icon_bg = icon_bg.resize((1600, 900), Image.ANTIALIAS)
        icon_bg1 = ImageTk.PhotoImage(icon_bg)
        bg_label = Label(frame1, image=icon_bg1)
        bg_label.place(x=0, y=0, relheight=1, relwidth=1, anchor=NW)

        # antialias is used to resize here
        icon_menu = Image.open(
            "C:/Users/use/Desktop/Covid-19 Group project/images/menu_icon.png")
        icon_menu = icon_menu.resize((50, 50), Image.ANTIALIAS)
        icon_menu1 = ImageTk.PhotoImage(icon_menu)
        menu_btn = Label(frame1, image=icon_menu1, relief=FLAT,bg="#233D72")
        menu_btn.place(rely=0.00625, relx=0.00625)

        icon_globe = Image.open(
            "C:/Users/use/Desktop/Covid-19 Group project/images/globe_icon.png")
        icon_globe = icon_globe.resize((50, 50), Image.ANTIALIAS)
        icon_globe1 = ImageTk.PhotoImage(icon_globe)
        globe_btn = Button(frame1, image=icon_globe1,
                           relief=RAISED, command=global_window)
        globe_btn.place(rely=0.125, relx=0.00625)

        icon_heartbeat = Image.open(
            "C:/Users/use/Desktop/Covid-19 Group project/images/heartbeat_icon.png")
        icon_heartbeat = icon_heartbeat.resize((50, 50), Image.ANTIALIAS)
        icon_heartbeat1 = ImageTk.PhotoImage(icon_heartbeat)
        heartbeat_btn = Button(frame1, image=icon_heartbeat1,
                               relief=RAISED, command=yourHealth_window)
        heartbeat_btn.place(rely=0.25, relx=0.00625)



        icon_programmer = Image.open(
            "C:/Users/use/Desktop/Covid-19 Group project/images/programmer_icon.png")
        icon_programmer = icon_programmer.resize((50, 50), Image.ANTIALIAS)
        icon_programmer1 = ImageTk.PhotoImage(icon_programmer)
        programmer_btn = Button(frame1, image=icon_programmer1,
                                relief=RAISED, command=developer_window)
        programmer_btn.place(rely=0.8, relx=0.00625)
    icons()

    def emojis():

        # Mounting the welcome label
        global welcome_label, feel_label,name
        welcome_label = Label(frame1, text="Welcome "+name,
                              font="Helvetica  25 bold", padx=100, bg="#233D72", fg="white")

        welcome_label.place(rely=0.094444, relx=0.17222,
                            relwidth=0.18, relheight=0.0370, height=16.7, width=144)
        # how are you feel

        welcome_label = Label(frame1, text="How are you feeling today?",
                              font="Helvetica  10 bold", bg="#233D72", fg="white")
        welcome_label.place(rely=0.25, relx=0.085625)

        # emoji Icons
        global icon_great, icon_bad, icon_notSure
        global great_btn, bad_btn, notSure_btn
        global icon_great1, icon_bad1, icon_notSure1
        
        def happyFeedback():
            messagebox.showinfo("Happy", "we happy to here you're doing fine \n keep on with the fight against COVID\n wash hands and sanitize frequently")

        icon_great = Image.open(
            "C:/Users/use/Desktop/Covid-19 Group project/images/great_icon.png")
        icon_great = icon_great.resize((60, 60), Image.ANTIALIAS)
        icon_great1 = ImageTk.PhotoImage(icon_great)
        great_btn = Button(frame1, image=icon_great1, text='Great !', relief=FLAT,
                           compound=TOP, font="Helvetica  8 bold", bg="#233D72", fg="white",command=happyFeedback)
        great_btn.place(rely=0.3, relx=0.06375)
        
        def askTest():
            global testResponse
            testResponse=messagebox.askyesno("prompt", "Do you want to take a test")
            if (testResponse==True):
                yourHealth_window()
            else:
                pass
        icon_notSure = Image.open(
            "C:/Users/use/Desktop/Covid-19 Group project/images/notSure_icon.png")
        icon_notSure = icon_notSure.resize((60, 60), Image.ANTIALIAS)
        icon_notSure1 = ImageTk.PhotoImage(icon_notSure)
        notSure_btn = Button(frame1, image=icon_notSure1, text="Not sure", compound=TOP,
                             font="Helvetica  8 bold", relief=FLAT, bg="#233D72", fg="white",command=askTest)
        notSure_btn.place(rely=0.3, relx=0.14126)

        icon_bad = Image.open(
            "C:/Users/use/Desktop/Covid-19 Group project/images/bad_icon.png")
        icon_bad = icon_bad.resize((60, 60), Image.ANTIALIAS)
        icon_bad1 = ImageTk.PhotoImage(icon_bad)
        bad_btn = Button(frame1, image=icon_bad1, relief=FLAT, compound=TOP,
                         text=" Bad", font="Helvetica 8 bold", bg="#233D72", fg="white",command=yourHealth_window)
        bad_btn.place(rely=0.3, relx=0.225)
    emojis()

    def kenyaData():
        # flags icons
        global icon_kenya
        global icon_kenya1
        global kenya_btn

        icon_kenya = Image.open(
            "C:/Users/use/Desktop/Covid-19 Group project/images/kenya_icon.png")
        icon_kenya = icon_kenya.resize((60, 30), Image.ANTIALIAS)
        icon_kenya1 = ImageTk.PhotoImage(icon_kenya)
        kenya_btn = Button(frame1, image=icon_kenya1, relief=FLAT, compound=LEFT,
                           text="Kenya today", font="Helvetica 12 bold", bg="#233D72", fg="white")
        kenya_btn.place(rely=0.502, relx=0.133)

        # Kenya stats label
        global label_cases, label_recoveries, label_deaths, label_vaccine
        myCursor.execute("SELECT * FROM live_cases where Country='Kenya'")
        myresult2 = myCursor.fetchall()
        global kenyaCases, KenyaDeaths, kenyaDates
        # for j in myresult2:
        #     print(j)
        kenyaCases = int(myresult2[0][1])
        KenyaDeaths = int(myresult2[0][2])
        kenyaDates = myresult2[0][3]
        print(kenyaCases)
        print(KenyaDeaths)

#f'{kenyaCases:,}' f'{KenyaDeaths:,}' 
        label_cases = Label(frame1, text="CONFIRMED CASES \n " +
                            f'{kenyaCases:,}', relief=GROOVE, font="Helvetica 10 bold")
        label_cases.place(relx=0.075, rely=0.586)

        label_recoveries = Label(
            frame1, text="CONFIRMED RECOVERIES \n (not up to date) ", relief=GROOVE, font="Helvetica 10 bold")
        label_recoveries.place(relx=0.2195, rely=0.586)

        label_deaths = Label(frame1, text="CONFIRMED DEATHS \n " +
                             f'{KenyaDeaths:,}', relief=GROOVE, font="Helvetica 10 bold")
        label_deaths.place(relx=0.075, rely=0.678)

        label_vaccine = Label(frame1, text="VACCINATION RATE \n +(coming up soon)", 
                               relief=GROOVE, font="Helvetica 10 bold")
        label_vaccine.place(relx=0.2185, rely=0.678)

    kenyaData()

    # global icon for stats
    def GlobalData():
        global icon_global
        global icon_global1
        global global_btn

        icon_global = Image.open(
            "C:/Users/use/Desktop/Covid-19 Group project/images/global_icon.png")
        icon_global = icon_global.resize((50, 50), Image.ANTIALIAS)
        icon_global1 = ImageTk.PhotoImage(icon_global)
        global_btn = Button(frame1, image=icon_global1, relief=FLAT, compound=LEFT,
                            text=" Global Stats", font="Helvetica 12 bold", bg="#A8CBE6")
        global_btn.place(rely=0.4998, relx=0.610)

        myCursor.execute("SELECT * FROM live_cases where Country='global'")
        myresult3 = myCursor.fetchall()
        global globalCases, globalDeaths, globalDate

        globalCases = int(myresult3[0][1])
        globalDeaths = int(myresult3[0][2])
        globalDate = myresult3[0][3]

        #global stats
        global label_G_cases, label_G_recoveries, label_G_deaths, label_G_vaccine
        label_G_cases = Label(frame1, text="CONFIRMED CASES \n" +
                              f'{globalCases:,}' , relief=GROOVE, font="Helvetica 10 bold")
                              #f'{globalDeaths:,}' 
        label_G_cases.place(relx=0.563, rely=0.6)

        label_G_recoveries = Label(
            frame1, text="CONFIRMED RECOVERIES \n (not up do date)", relief=GROOVE, font="Helvetica 10 bold")
        label_G_recoveries.place(relx=0.647, rely=0.6)

        label_deaths = Label(frame1, text="CONFIRMED DEATHS \n" +
                             f'{globalDeaths:,}' , relief=GROOVE, font="Helvetica 10 bold")
        label_deaths.place(relx=0.563, rely=0.688)

        label_G_vaccine = Label(frame1, text="VACCINATION RATE \n(coming up soon)" ,
                                relief=GROOVE, font="Helvetica 10 bold")
        label_G_vaccine.place(relx=0.697, rely=0.688)

        global icon_logOut, icon_logOut1
        global logOut_btn
        icon_logOut = Image.open(
            "C:/Users/use/Desktop/Covid-19 Group project/images/logOut_icon.png")
        icon_logOut = icon_logOut.resize((50, 50), Image.ANTIALIAS)
        icon_logOut1 = ImageTk.PhotoImage(icon_logOut)
        logOut_btn = Button(frame1, image=icon_logOut1,
                            anchor=E, command=logOut)
        logOut_btn.place(rely=0.01111, relx=0.9475)

    GlobalData()

    def topStories():
        # Top stories
        global label_topStories,  btn_topStory1, btn_topStory2, btn_topStory3
        label_topStories = Label(frame1, text="COVID-19 TOP STORIES",
                                 font="Helvetica 15 bold", bg="#233D72", fg="white")
        label_topStories.place(relx=0.8, rely=0.15)

        #thankGod= db.child("Story1").child("link").get()
        news_source1 = db.child("Story1").child("source").get()
        news_title1 = db.child("Story1").child("title").get()
        btn_topStory1 = Button(frame1, command=lambda: open_url(1), text=news_source1.val()+"\n" + news_title1.val(),
                               relief=GROOVE, font="Helvetica 10 bold")
        btn_topStory1.place(relx=0.8, rely=0.2222)

        news_source2 = db.child("Story2").child("source").get()
        news_title2 = db.child("Story2").child("Title").get()
        btn_topStory2 = Button(frame1, text=news_source2.val()+"\n" + news_title2.val(),
                               relief=GROOVE, font="Helvetica 10 bold", command=lambda: open_url(2))
        btn_topStory2.place(relx=0.8, rely=0.30556)

        news_source3 = db.child("Story3").child("source").get()
        news_title3 = db.child("Story3").child("TITE").get()
        btn_topStory3 = Button(frame1, command=lambda: open_url(3), text=news_source3.val()+"\n" + news_title3.val(),
                               relief=GROOVE, font="Helvetica 10 bold")
        # ,ipadx=10,ipady=20,relyspan=2, sticky=N
        btn_topStory3.place(relx=0.8, rely=0.3889)

        news_source4 = db.child("Story4").child("source").get()
        news_title4 = db.child("Story4").child("Title").get()
        btn_topStory4 = Button(frame1, command=lambda: open_url(4), text=news_source4.val()+"\n" + news_title4.val(),
                               relief=GROOVE, font="Helvetica 10 bold")
        # ,ipadx=10,ipady=20,relyspan=2, sticky=N
        btn_topStory4.place(relx=0.8, rely=0.4722)

        news_source5 = db.child("Story5").child("source").get()
        news_title5 = db.child("Story5").child("Title").get()
        btn_topStory5 = Button(frame1, command=lambda: open_url(5), text=news_source5.val()+"\n" + news_title5.val(),
                               relief=GROOVE, font="Helvetica 10 bold")
        # ,ipadx=10,ipady=20,relyspan=2, sticky=N
        btn_topStory5.place(relx=0.8, rely=0.5556)

        news_source6 = db.child("Story6").child("source").get()
        news_title6 = db.child("Story6").child("TITLE").get()
        btn_topStory6 = Button(frame1, command=lambda: open_url(6), text=news_source6.val()+"\n" + news_title6.val(),
                               relief=GROOVE, font="Helvetica 10 bold")
        # ,ipadx=10,ipady=20,relyspan=2, sticky=N
        btn_topStory6.place(relx=0.8, rely=0.6389)

        news_source7 = db.child("Story7").child("source").get()
        news_title7 = db.child("Story7").child("TITLE").get()
        btn_topStory7 = Button(frame1, command=lambda: open_url(7), text=news_source7.val()+"\n" + news_title7.val(),
                               relief=GROOVE, font="Helvetica 10 bold")
        # ,ipadx=10,ipady=20,relyspan=2, sticky=N
        btn_topStory7.place(relx=0.8, rely=0.7222)

        news_source8 = db.child("Story8").child("source").get()
        news_title8 = db.child("Story8").child("TITLE").get()
        btn_topStory8 = Button(frame1, command=lambda: open_url(8), text=news_source8.val()+"\n" + news_title8.val(),
                               relief=GROOVE, font="Helvetica 10 bold")
        # ,ipadx=10,ipady=20,relyspan=2, sticky=N
        btn_topStory8.place(relx=0.8, rely=0.8055)

    topStories()

    def search():
        try:
            myCursor.execute(
                "SELECT * FROM live_cases where Country= '" + e1.get() + "'")
            e1.delete(0, END)
            myresult1 = myCursor.fetchall()
            print(myresult1)
            global myresult, var_ConfirmedCases, var_confirmedDeaths

            Label(frame1, text="Total Confirmed Cases").place(
                relx=0.547, rely=0.216)
            Label(frame1, text="Total Deaths").place(relx=0.547, rely=0.266)

            var_ConfirmedCases = myresult1[0][1]
            var_confirmedDeaths = myresult1[0][2]
            global searchConDeaths, searchCases

            searchConCases_label = Label(frame1, text=var_ConfirmedCases)
            searchConCases_label.place(relx=0.687, rely=0.216)

            searchConDeaths = Label(frame1, text=var_confirmedDeaths)
            searchConDeaths.place(relx=0.687, rely=0.266)

        except Exception as e:
            print(e)
            myDb.rollback()
            myDb.close()

    global e1, country
    e1 = Entry(frame1)
    e1.place(relx=0.546, rely=0.130)
    Label(frame1, text="Enter The Country").place(relx=0.546, rely=0.089)
    #country = e1.get()

    # print(country)
    Button(frame1, text="Search", command=search,
           height=1, width=15).place(relx=0.546, rely=0.170)

    status_label = Label(frame1,
                         text="LAST UPDATED ON " +globalDate, relief=GROOVE)
    status_label.place(relx=0.00001, rely=0.98, relwidth=1)


def login():
    global name, i
    user_ver = enter_usernamel.get()
    print(user_ver)
    pas_ver = enter_passwordl.get()
    print(pas_ver)
    sql = "select * from userinfo where username = %s and password = %s"
    test = myCursor.execute(sql, [(user_ver), (pas_ver)])
    print(test)
    results = myCursor.fetchall()
    if results:
        for i in results:
            enter_passwordl.delete(0, END)
            enter_usernamel.delete(0, END)
            print(results)
            name= results[0][0]
            home_button()  # if credentials are correct,the function logged is executed
            # break
    else:
        messagebox.showwarning(title="Login details",
                               message="Invalid credentials")


login_Button = Button(frame, text="Login", command=login,
                      font="helvetica  15 bold")
login_Button.place(relx=0.51999, rely=0.500)

label_haveAccount = Label(
    frame, text="Don't have an account?", font="helvetica  15 bold")
label_haveAccount.place(relx=0.5, rely=0.6589)


def sign_up():

    global signUp, user, email1 
    signUp = Frame(root)
    signUp.place(x=0, y=0, relheight=1, relwidth=1, anchor=NW)

    Label(signUp, text="Wash your hands, sanitize & Observe social distancing ", fg="#2E8BC0", font= 'helvetica 15 bold').place(relx= 0.32, rely=0.085)

    def submit():
            
        user=enter_username.get()
        email1=enter_email.get()
        sql = "select username and email from userinfo where username =%s or email=%s"
        myCursor.execute(sql,[(user),(email1)])
        results = myCursor.fetchall()

        if results:
            messagebox.showerror("Invalid Details", "Username or email already take")

        else:
            if(enter_password1.get() == enter_password2.get()):

                # inserting records entered in the form into the database
                myCursor.execute("INSERT INTO userinfo VALUES('%s','%s','%s','%s','%s')" % (enter_firstname.get(), enter_secondname.get(), enter_username.get(),
                                                                                            enter_email.get(), enter_password2.get()))
                # committing changes made in the database
                myDb.commit()
                # deleting records entered into the entry boxes after inserting them into mysql table
                enter_firstname.delete(0, END)
                enter_secondname.delete(0, END)
                enter_username.delete(0, END)
                enter_email.delete(0, END)
                enter_password1.delete(0, END)
                enter_password2.delete(0, END)

                signUp.place_forget()
            else:
                # when the password do not match with any in the record.
                messagebox.showwarning(
                    title="password", message="Password do not match")

    label_CreateAccount = Label(
        signUp, text="Create account", font="Helvetica  20 bold")
    label_CreateAccount.place(relx=0.38, rely=0.123)

    label_firstname = Label(signUp, text="First name", anchor=CENTER, font= "helvetica 15 bold")
    label_firstname.place(relx=0.41, rely=0.173)
    enter_firstname = Entry(signUp, width=30, font=15)
    enter_firstname .place(relx=0.38, rely=0.223)

    label_secondname = Label(signUp, text="Second name", anchor=CENTER, font= "helvetica 15 bold")
    label_secondname.place(relx=0.41, rely=0.273)
    enter_secondname = Entry(signUp, width=30,font=15)
    enter_secondname .place(relx=0.38, rely=0.323)

    label_username = Label(signUp, text="username", anchor=CENTER, font= "helvetica 15 bold")
    label_username.place(relx=0.41, rely=0.373)
    enter_username = Entry(signUp, width=30,font=15)
    enter_username .place(relx=0.38, rely=0.423)

    label_email = Label(signUp, text="Email address", anchor=CENTER, font= "helvetica 15 bold")
    label_email.place(relx=0.41, rely=0.473)
    enter_email = Entry(signUp, width=30,font=15)
    enter_email.place(relx=0.38, rely=0.523)

    label_password1 = Label(signUp, text="Password", anchor=CENTER, font= "helvetica 15 bold")
    label_password1.place(relx=0.41, rely=0.573)
    enter_password1 = Entry(signUp, width=30,font=15)
    enter_password1 .place(relx=0.38, rely=0.623)

    label_password2 = Label(signUp, text=" Confirm Password", anchor=CENTER, font= "helvetica 15 bold")
    label_password2.place(relx=0.41, rely=0.673)
    enter_password2 = Entry(signUp, width=30,font=15)
    enter_password2 .place(relx=0.38, rely=0.723)

    submit_Button = Button(signUp, text="Submit", command=submit, anchor=CENTER, font= "helvetica 15 bold")
    submit_Button.place(relx=0.41, rely=0.823)


sign_Button = Button(frame, text="Sign Up",
                     command=sign_up, font='helvetica  15 bold')
sign_Button.place(relx=0.5199, rely=0.6900)


root.mainloop()
