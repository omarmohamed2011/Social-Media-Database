## Import required libraries
from selenium import webdriver

from bs4 import BeautifulSoup

import pandas as pd
import os
import re

from selenium.webdriver.common.by import By

import time
from utilities import *
from datetime import datetime, timedelta
from constants import *
import sched
import time

## required links for scrapping task
fb_links = [hjh_fb,apc_fb,akw_fb,adc_fb,alw_fb,ahc_fb,aab_fb,and_fb,ksa_care_fb,med_tour_fb,and_egy_fb,and_vis_fb,and_car_fb, and_home_fb,dot_care_fb];        fb_pages  = ['FaceBook HJH','FaceBook APC','FaceBook AKW','FaceBook ADC','FaceBook ALW','FaceBook AHC','FaceBook AAB','FaceBook Andalusia_Group','FaceBook KSA_HomeCare','FaceBook Medical_Tour','FaceBook Andalusia_Egypt','FaceBook Andalusia_Visiting','FaceBook Andalusia_careers','FaceBook Homecare','FaceBook Dotcare']
ins_links= [hjh_ins,apc_ins,akw_ins,adc_ins,alw_ins,ahc_ins,and_ins,med_tour_ins,and_egy_ins,and_vis_ins,and_car_ins,and_home_ins,dot_care_ins,dot_care_ksa_ins];  ins_pages = ['Instagram HJH','Instagram APC','Instagram AKW','Instagram ADC','Instagram ALW','Instagram AHC','Instagram Andalusia_Group','Instagram Medical_Tour','Instagram Andalusia_Egypt','Instagram Andalusia_Visiting','Instagram Andalusia_careers','Instagram Homecare','Instagram Dotcare','Instagram KSA_Dotcare']
yt_links = [akw_yt,adc_yt,and_egy_yt]; yt_pages = ['Youtube AKW','Youtube ADC','Youtube Andalusia_Egypt']
try: ## get tweet links if there is any
    twt_links = [hjh_twt,apc_twt,akw_twt,adc_twt,alw_twt];          twt_pages = ['Twitter HJH','Twitter APC','Twitter AKW','Twitter ADC','Twitter ALW','Twitter AHC']
except:
    twt_links = []; twt_pages = []

lnk_links = [and_egy_lnk,aab_lnk,and_lnk,and_car_lnk]; lnk_pages = ['LinkedIn Andalusia_Egypt','LinkedIn AAB','LinkedIn Andalusia_Group','LinkedIn Andalusia_careers']


## open link
driver = webdriver.Chrome()
driver.maximize_window()
driver.get("https://app.agorapulse.com/")

time.sleep(10) ## wait time
log_in(driver)
time.sleep(10)

all_links = fb_links + twt_links + ins_links + yt_links + lnk_links
num_links = len(fb_links + twt_links + ins_links + yt_links + lnk_links)
all_pages = fb_pages + twt_pages + ins_pages + yt_pages + lnk_pages


## daily time in seconds for the script to repeat itself
day_time_sec = 60 * 60 * 24

def gm_date(rev_date, needed_date):
    '''
    :param rev_date: date written in agora format
    :param needed_date: current date for comparison
    :return: the date of comment according to the difference between the current datetime and the comment date.
    '''
    days_vol = {"day": 1, "week": 7, "month": 30, "year": 365}
    text = rev_date.split()
    text[0] = re.sub(r'an?', '1', text[0])
    text[1] = text[1].rstrip('s')
    num_hours = int(text[0]) * int(text[1] == "hour")

    try:
        duration = days_vol[text[1]]
    except KeyError:
        duration = 0
    num_days = int(text[0]) * duration

    return get_day(needed_date, num_days, num_hours, day_only=False)

def get_day(needed_date, past_days=0, past_hours=0, day_only=True):
    ret = needed_date - timedelta(days=past_days, hours=past_hours)
    return ret.date() if day_only else ret

def run_daily():
    '''
    :return: returns the scraping output.
    '''
    print('Scraping has begun for day ',str(datetime.now()).split(' ')[0])
    comments = []; days = [];
    names = []; indices = [];
    dates_time = []

    for i in range(num_links):
        link = all_links[i]
        driver.get(link)
        time.sleep(20)

        htmlstring = driver.page_source
        soup = BeautifulSoup(htmlstring, "html.parser")

        long_scroll(driver=driver)

        mydivs = soup.find('div', class_='item-list-cards-container')

        comments.append([]);  days.append([]);
        names.append([]);  dates_time.append([])
        indices.append(all_pages[i])

        if mydivs:
            for div in mydivs:
                try:
                    name = div.findNext("span", attrs={"class": "user-name"}).text.strip()
                    day = div.findNext("span", attrs={"class": "creation-time-ago ng-star-inserted"}).text.strip()
                    comment = div.findNext("span", attrs={"class": "item-card-message ng-star-inserted"}).text.strip()
                    current_date = datetime.now().date()

                    if (len(comments[i]) == 0):
                        names[i].append(name);
                        days[i].append(day);
                        comments[i].append(comment)
                        dates_time[i].append(current_date)
                    elif (comments[i][-1] != comment):
                        names[i].append(name);
                        days[i].append(day);
                        comments[i].append(comment)
                        dates_time[i].append(current_date)
                except:
                    j = i
        else:
            comments[i] = [''];
            days[i] = [''];
            names[i] = [''];
            dates_time[i] = ['']

    indices_column = [];
    names_column = []
    comments_column = [];
    days_column = [];
    dates_column = []

    for i in range(num_links):
        if len(comments[i]) > 0:
            for j in range(len(comments[i])):
                indices_column.append(indices[i])
                comments_column.append(comments[i][j]);  dates_column.append(dates_time[i][j])
                names_column.append(names[i][j]);  days_column.append(days[i][j])

    platform, Business_Units = [], []

    for i in range(len(indices_column)):
        social_media, bu = indices_column[i].split(' ')[0], indices_column[i].split(' ')[1]
        platform.append(social_media);  Business_Units.append(bu)

    df = pd.DataFrame()

    df['Platform'] = platform;   df['Business Unit'] = Business_Units
    df['message'] = comments_column;    df['Time ago'] = days_column
    df['Comment Author'] = names_column;   df['Current date'] = dates_column

    current_datetime = datetime.now()
    ## modified datetime is approximately 15 minutes this is almost the time taken from the beginning of the scrap to reach
    ##into here
    modified_datetime = current_datetime - timedelta(minutes=15)

    time_ago = df['Time ago'].tolist()

    dates_column = []
    for i in range(len(time_ago)):
        try:
            dates_column.append(gm_date(time_ago[i], modified_datetime))
        except:
            dates_column.append(modified_datetime)

    df['Current date'] = dates_column
    df.drop(columns=['Time ago'], inplace=True)

    datetime_str = current_datetime - timedelta(days=1,minutes=30)
    certain_date = pd.to_datetime(datetime_str)

    df = df[df['Current date'] >= certain_date]
    df = df[df['message'] != '']
    df.drop_duplicates(inplace=True)

    directory_path = 'Extracted SocialMediaComments/' + str(current_date)
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

    directory_path += '/Data_Shown.csv'
    df.to_csv(directory_path, encoding='utf-8-sig', index=False)
    print('Scraping has ended for day ',str(datetime.now()).split(' ')[0],'waiting for one day time for the scraping to work again.')

def schedule_function_one_day(scheduler):
    scheduler.enter(12, 1, run_daily, ())

while(True):
    scheduler = sched.scheduler(time.time, time.sleep)
    schedule_function_one_day(scheduler)
    scheduler.run()
