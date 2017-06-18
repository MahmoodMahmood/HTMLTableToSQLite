import urllib.request
from bs4 import BeautifulSoup
import sqlite3

def init_db(cur, name):
    cur.execute("CREATE TABLE %s (DateVal TEXT PRIMARY KEY, Day TEXT,Emsak TEXT, Fajr TEXT, Shurooq TEXT, Zuhr TEXT, Asr TEXT, Maghrib TEXT, Isha TEXT)" % name)

def convertDayToEnglish(arabicDay):
    if arabicDay == 'السبت' :
        return 'Saturday'
    elif arabicDay == 'الأحد' :
        return 'Sunday'
    elif arabicDay == 'الإثنين' :
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
        return None

db = sqlite3.connect(':memory:')
cur = db.cursor()
url = "https://www.awqaf.gov.ae/MonthlyPrayerTimes.aspx?lang=EN"
htmltext = urllib.request.urlopen(url).read()
soup =  BeautifulSoup(htmltext, "lxml")
table = soup.find('table', {'id': 'Contents_MonthlyPrayerTimes1_GridView1'}) #this is the table we are looking for

colNames = []
init_db(cur, 'ramadan2017AbuDhabi')#name is a tuple

#for th in table.findAll('th'):
#    colNames.append(th.text)

for tr in table.findAll('tr')[1:]:#need to skip the first element for duplication reasons
    arabicDay = tr.findNext('td')
    date = arabicDay.findNext('td')
    hijriDay = date.findNext('td')
    emsak = hijriDay.findNext('td')
    fajr = emsak.findNext('td')
    shurooq = fajr.findNext('td')
    zuhr = shurooq.findNext('td')
    asr = zuhr.findNext('td')
    maghrib = asr.findNext('td')
    isha = maghrib.findNext('td')
    row = (date.text, convertDayToEnglish(arabicDay.text), emsak.text, fajr.text, shurooq.text, zuhr.text, asr.text, maghrib.text, isha.text)
    cur.execute("INSERT INTO ramadan2017AbuDhabi VALUES (?,?,?,?,?,?,?,?,?)", row)
    db.commit()

    #print(date)
cur.execute("SELECT * FROM ramadan2017AbuDhabi")
for element in cur.fetchall():
    print (element)