#This is a real-world style Python problem designed using the modules and concepts you’ve already completed 
#(✅ sys, pathlib, runpy, functools, traceback, datetime, decorators). The idea is to simulate an Upwork-like client 
#request — something you could actually face as a freelancer or open-source contributor.

# TODO Title: Automated Task Runner with Logging & Config

#Scenario:
    #A small company has a set of repetitive scripts (Python functions) that they need to run daily. 
    #They want a single command-line tool where they can:

        # 1. Choose which tasks to run via a tasks.json config file.
        # 2. Log all results (success/failure + timestamp) into a logs/ folder.
        # 3. Automatically retry failed tasks up to 2 times.
        # 4. Keep logs clean with tracebacks for errors.
        # 5. Allow a developer to quickly add new tasks without rewriting the runner.

import sys
from pathlib import Path
import runpy
import traceback
import functools
import json
from datetime import datetime

now = datetime.now()
print("Starting Task Runner...\n")

#Functions.....
def daily_backup():
    print('Hello!, This is daily_backup function')

def generate_report():
    print('Hello!, This is generate_report function')

def send_email():
    #raise ValueError("Email server not reachable")
    print('Hello!, This is send_email function')

path = Path(__file__).parent / "tasks.json" #Path to tasks.json file

with Path(path).open('r', encoding='utf-8') as f:
    tasks_json_file_content = json.load(f)

enabled_task_names = {} #Enabled func names...
for key, value in tasks_json_file_content.items():
    for task in value:
        #print(f"{task['name']} : {task['enabled']}")
        if task['enabled'] == True:  #If enabled is True add to dict
            func = globals()[task['name']]
            enabled_task_names[task['name']] = func

#print(f"Running Task: {enabled_task_names}")
#print(f"Running Task: {tasks_json_file_content}")

if len(sys.argv) != 2:
    print("Usage: python task_runner.py [task_name]")
    sys.exit(1)

task_name = sys.argv[1]

if task_name not in enabled_task_names and task_name != 'all':
    print(f"Task '{task_name}' is not enabled or does not exist.")
    sys.exit(1)

if task_name == 'all' : #If u raise error look here !!!!!!!!!!!!!!
    for str, obj in enabled_task_names.items():
        obj()
elif task_name in enabled_task_names:
    enabled_task_names[task_name]()


#Logging file setup...
log_dir = Path(__file__).parent / 'logs'
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / 'runner.log'
log_file.touch(exist_ok=True)

date_time_stamp = now.strftime("%Y-%m-%d %H:%M:%S")
with Path(log_file).open('a', encoding='utf-8') as log:
    log.write(date_time_stamp + "\n")