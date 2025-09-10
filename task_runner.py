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

print("Starting Task Runner...")

path = Path(__file__).parent / "tasks.json"

with Path(path).open('r', encoding='utf-8') as f:
    tasks = json.load(f)

true_task = []
for key, value in tasks.items():
    for task in value:
        #print(f"{task['name']} : {task['enabled']}")
        if task['enabled'] == True:
            true_task.append(task['name'])

print(f"Running Task: {true_task}")
