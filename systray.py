#!/usr/bin/env python3
from pystray import Icon as icon, Menu as menu, MenuItem as item
from PIL import Image, ImageDraw
import threading
import subprocess
width=50
height=50
color1='white'
color2='black'
def create_image():
    # Generate an image and draw a pattern
    image = Image.new('RGB', (width, height), color1)
    dc = ImageDraw.Draw(image)
    dc.rectangle(
        (width // 2, 0, width, height // 2),
        fill=color2)
    dc.rectangle(
        (0, height // 2, width // 2, height),
        fill=color2)

    return image

installed = True if subprocess.run(["which","iproxy"]).returncode == 0 else False
running_state = False
ssh = False
debug = False


def ssh_clicked(icon, item):
    global ssh
    ssh = not item.checked

def debug_clicked(icon, item):
    global debug
    debug = not item.checked

def start_ssh_tunnel():
    subprocess.run(["iproxy", "2222", "22"])

def start_debug_tunnel():
   o = subprocess.run(["iproxy", "1234", "1234"])


ssh_thread : threading.Thread
debug_thread : threading.Thread

def start_clicked(icon, item):
    global running_state
    global ssh_thread
    global debug_thread
    running_state = True
    if ssh:
        ssh_thread = threading.Thread(target=start_ssh_tunnel)
        ssh_thread.start()
    if debug:
        debug_thread = threading.Thread(target=start_debug_tunnel)
        debug_thread.start()

def stop_clicked(icon, item):
    global running_state
    global ssh_thread
    global debug_thread
    if running_state:
        subprocess.run(["killall", "iproxy"])
        if ssh:
            ssh_thread.join()
            print(ssh_thread)
        if debug:
            debug_thread.join()
            print(debug_thread)
    running_state = False

def get_radio_state(v):
    def inner(item):
        if running_state:
            return False
        elif not running_state:
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
def running_status(v):
    return 'Running' if running_state else 'Not Running'


# Update the state in `on_clicked` and return the new state in
# a `checked` callable
icon('iProxy', create_image(), menu=menu(
    item('iProxy Installed' if installed else 'iProxy Not Installed',0,enabled=False,default=True),
    item(running_status,0,enabled=False,default=True),
    item('ssh -> 2222',ssh_clicked,checked=lambda item: ssh, enabled=get_radio_state(item.enabled)),
    item('debug -> 1234',debug_clicked,checked=lambda item: debug, enabled=get_radio_state(item.enabled)),
    item('Start',start_clicked,enabled=get_start_state(item.enabled)),
    item('Stop',stop_clicked,enabled=get_stop_state(item.enabled)),
    item('Exit',action=lambda icon:icon.stop()))).run()
