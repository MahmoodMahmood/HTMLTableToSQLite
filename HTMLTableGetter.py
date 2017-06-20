import sqlite3
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import Select

def init_db(cur, name):
    cur.execute("CREATE TABLE %s (DateVal TEXT PRIMARY KEY, Day TEXT,Emsak TEXT, "
                "Fajr TEXT, Shurooq TEXT, Zuhr TEXT, Asr TEXT, Maghrib TEXT, Isha TEXT)" % name)

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


def runThroughMonth(cur, htmltext):
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
            cur.execute("INSERT INTO AbuDhabi VALUES (?,?,?,?,?,?,?,?,?)", row)
    return

db = sqlite3.connect(':memory:')
cur = db.cursor()
url = "https://www.awqaf.gov.ae/MonthlyPrayerTimes.aspx?lang=EN"

browser = webdriver.Firefox()
browser.get(url)

element = browser.find_element_by_id('Contents_MonthlyPrayerTimes1_ddlMonths')

init_db(cur, 'AbuDhabi')

for i in range(12): #loop through the 12 months
    select = Select(browser.find_element_by_name('ctl00$Contents$MonthlyPrayerTimes1$ddlMonths'))
    month = select.select_by_index(i)
    htmltext = browser.page_source
    runThroughMonth(cur, htmltext)  # add all the data from that month to the database

db.commit()


cur.execute("SELECT * FROM AbuDhabi")
for element in cur.fetchall():
    print (element)