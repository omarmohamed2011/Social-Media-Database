import pandas as pd
import glob
import os
from datetime import datetime,timedelta
import sched
import time

day_time_sec = 60*60*24
current_datetime = datetime.now()
day_name = current_datetime.strftime("%A")

def run_weekly():

    path_files = 'Extracted SocialMediaComments/*/*.csv'
    path_files = glob.glob(path_files)[:]

    dfs = []
    for path1 in path_files:
        try:
            dfs.append(pd.read_csv(path1))
        except:
            dfs.append(pd.read_excel(path1))

    result = pd.concat(dfs, ignore_index=True)
    result.drop_duplicates()
    result.sort_values(by='Platform', inplace=True)

    directory_path = 'Extracted SocialMediaComments/data to ' + str(current_datetime).split(' ')[0][5:]+' ' + \
                 str(current_datetime.strftime('%B')) +' '+ str(current_datetime).split(' ')[0][:4] +'/Results/'

    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

    directory_path = directory_path + 'Agora_comments.csv'
    result.to_csv(directory_path,index=False,encoding='utf-8-sig')


def schedule_function_one_day(scheduler):
    print('Scheduler is working on the daily check.')
    time.sleep(3)
    scheduler.enter(day_time_sec, 1, run_weekly, ())

while(True):
    scheduler = sched.scheduler(time.time, time.sleep)
    schedule_function_one_day(scheduler)
    if day_name == 'Friday':
        print('Scheduler is working on the weekly procedure of concatenating data on Saturday.')
        scheduler.run()    ## Waits for one day from Friday, collects all weekly data in a single file
        print('Scheduler finished successfully, scheduler will wait for one day again.')