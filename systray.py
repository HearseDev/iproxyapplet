#!/usr/bin/env python3
from pystray import Icon as icon, Menu as menu, MenuItem as item
from PIL import Image
import subprocess
from sys import platform
from shutil import which


#disable python launcher icon on macos
if platform == "darwin":
    print("darwin detected, enabling LSBackgroundOnly")
    import AppKit
    info = AppKit.NSBundle.mainBundle().infoDictionary()
    info["LSBackgroundOnly"] = "1"

#globals
installed = which("iproxy") is not None
running_state = False
ssh = True
debug = False
ssh_process = None
debug_process = None

def create_image():
    image = Image.open('icon.png')
    return image

def ssh_clicked(icon, item):
    global ssh
    ssh = not item.checked

def debug_clicked(icon, item):
    global debug
    debug = not item.checked

def start_clicked(icon, item):
    global running_state
    global ssh_process
    global debug_process
    running_state = True
    if ssh:
        ssh_process = subprocess.Popen("iproxy 2222 22", shell=True)
        print("Started ssh_process with pid", ssh_process.pid)
    if debug:
        debug_process = subprocess.Popen("iproxy 1234 1234", shell=True)
        print("Started debug_process with pid", debug_process.pid)

def stop_clicked(icon, item):
    global running_state
    global ssh_thread
    global debug_thread
    if running_state:
        if ssh:
            print("Terminating ssh_process with pid", ssh_process.pid)
            ssh_process.terminate()
        if debug:
            print("Terminating debug_process with pid", debug_process.pid)
            debug_process.terminate()
    running_state = False

def get_radio_state(v):
    def inner(item):
        if running_state and installed:
            return False
        elif not running_state and installed:
            return True
    return inner

def get_start_state(v):
    def inner(item):
        if not ssh and not debug: #not selected
            return False
        elif not running_state and installed:
            return True
        elif running_state:
            return False
    return inner

def get_stop_state(v):
    def inner(item):
        if not ssh and not debug: #not selected
            return False
        elif not running_state:
            return False
        else:
            return True
    return inner
def running_status(_):
    return 'Running' if running_state else 'Not Running'
def exit_clicked(icon):
    if ssh_process is not None:
        if ssh_process.poll() is None:
            print("Terminating ssh_process with pid", ssh_process.pid)
            ssh_process.terminate()
    if debug_process is not None:
        if debug_process.poll() is None:
            print("Terminating debug_process with pid", debug_process.pid)
            debug_process.terminate()
    icon.stop()
    

# Update the state in `on_clicked` and return the new state in
# a `checked` callable
icon('iProxy', create_image(), menu=menu(
    item('iProxy Installed' if installed else 'iProxy Not Installed',0,enabled=False,default=True),
    item(running_status,0,enabled=False,default=True),
    item('ssh -> 2222',ssh_clicked,checked=lambda item: ssh, enabled=get_radio_state(item.enabled)),
    item('debug -> 1234',debug_clicked,checked=lambda item: debug, enabled=get_radio_state(item.enabled)),
    item('Start',start_clicked,enabled=get_start_state(item.enabled)),
    item('Stop',stop_clicked,enabled=get_stop_state(item.enabled)),
    item('Exit',exit_clicked))).run()
