import sqlite3
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import Select

def createTable(cur, name):
    cur.execute("CREATE TABLE %s (DateVal TEXT PRIMARY KEY, Day TEXT,Emsak TEXT, "
                "Fajr TEXT, Shurooq TEXT, Zuhr TEXT, Asr TEXT, Maghrib TEXT, Isha TEXT)" % name)

def to_csv(db):
    cursor = db.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    for table_name in tables:
        table_name = table_name[0]
        table = pd.read_sql_query("SELECT * from %s" % table_name, db)
        table.to_csv(table_name + '.csv', index_label='index')


def convertDayToEnglish(arabicDay):
    if arabicDay == 'السبت' :
        return 'Saturday'
    elif arabicDay == 'الأحد' :
        return 'Sunday'
    elif arabicDay == 'الإثنين':
        return 'Monday'
    elif arabicDay == 'الثلاثاء' :
        return 'Tuesday'
    elif arabicDay == 'الأربعاء' :
        return 'Wednesday'
    elif arabicDay == 'الخميس' :
        return 'Thursday'
    elif arabicDay == 'الجمعة' :
        return 'Friday'
    else:
        print (arabicDay)
        return None

def isCurrentHijriMonth(table): #current month has an extra column
    if len(table.findAll('th')) == 10:
        return True
    else:
        return False


def runThroughMonth(cur, htmltext, city):
    #grab this month's table from the current page
    soup = BeautifulSoup(htmltext, "lxml")
    table = soup.find('table', {'id': 'Contents_MonthlyPrayerTimes1_GridView1'})  # table we are looking for

    datesSeen = set()
    currentMonth = isCurrentHijriMonth(table)  # check to ignore current hijri day

    for tr in table.findAll('tr'):
        arabicDay = tr.findNext('td')
        date = arabicDay.findNext('td')
        if currentMonth:  # current hijri month has an extra col we need to ignore
            hijriDay = date.findNext('td')
            emsak = hijriDay.findNext('td')
        else:
            emsak = date.findNext('td')
        fajr = emsak.findNext('td')
        shurooq = fajr.findNext('td')
        zuhr = shurooq.findNext('td')
        asr = zuhr.findNext('td')
        maghrib = asr.findNext('td')
        isha = maghrib.findNext('td')

        # for some reason some dates are repeated, do this to avoid repeated entries
        if date.text not in datesSeen:
            datesSeen.add(date.text)  # insert into a set for fast lookup
            row = (date.text, convertDayToEnglish(arabicDay.text), emsak.text, fajr.text,
                   shurooq.text, zuhr.text, asr.text, maghrib.text, isha.text)
            # print (row)
            cur.execute("INSERT INTO %s VALUES (?,?,?,?,?,?,?,?,?)" % city, row)
    return

db = sqlite3.connect('athanTimes.db')
cur = db.cursor()
url = "https://www.awqaf.gov.ae/MonthlyPrayerTimes.aspx?lang=EN"

browser = webdriver.Firefox()
browser.get(url)

citiesBox = browser.find_element_by_name('ctl00$Contents$MonthlyPrayerTimes1$ddlCities')
cities = []
for element in citiesBox.find_elements_by_tag_name('option'): #grab all the cities
    cities.append(element.text)#grab the city name

for city in cities:
    selectCity = Select(browser.find_element_by_name('ctl00$Contents$MonthlyPrayerTimes1$ddlCities'))
    selectCity.select_by_value(city)
    city = city.replace(" ", "") #need to remove the whitespace to be a valid table name
    city = city.replace("-", "") #this too :(
    createTable(cur, city)
    for i in range(12): #loop through the 12 months
        selectMonth = Select(browser.find_element_by_name('ctl00$Contents$MonthlyPrayerTimes1$ddlMonths'))
        selectMonth.select_by_index(i) # need to select by index due to page refreshing
        htmltext = browser.page_source
        runThroughMonth(cur, htmltext, city)  # add all the data from that month to the database

db.commit()
#to_csv(db) #uncomment this if you want to convert all the tables to csv format