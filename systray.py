#!/usr/bin/env python3
from pystray import Icon as icon, Menu as menu, MenuItem as item
from PIL import Image
import subprocess
from sys import platform
from shutil import which

# disable python launcher icon on macos
if platform == "darwin":
    print("darwin detected, enabling LSBackgroundOnly")
    import AppKit

    info = AppKit.NSBundle.mainBundle().infoDictionary()
    info["LSBackgroundOnly"] = "1"

# globals
installed = which("iproxy") is not None
running_state = False
ssh = True
debug = False
ssh_process = None
debug_process = None


def ssh_clicked(icon, item):
    global ssh
    ssh = not item.checked


def debug_clicked(icon, item):
    global debug
    debug = not item.checked


def terminate_processes():
    if ssh_process is not None and running_state and ssh:
        if ssh_process.poll() is None:
            print("Terminating ssh_process with pid", ssh_process.pid)
            ssh_process.terminate()
    if debug_process is not None and running_state and debug:
        if debug_process.poll() is None:
            print("Terminating debug_process with pid", debug_process.pid)
            debug_process.terminate()


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
    terminate_processes()
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
        if not ssh and not debug:  # not selected
            return False
        elif not running_state and installed:
            return True
        elif running_state:
            return False

    return inner


def get_stop_state(v):
    def inner(item):
        if not ssh and not debug:  # not selected
            return False
        elif not running_state:
            return False
        else:
            return True

    return inner


def running_status(_):
    if running_state:
        status = "Running: "
        if ssh:
            status += "ssh "
        if debug:
            status += "debug "
        return status
    else:
        return "Idle"
    # return 'Running' if running_state else 'Not Running'


def exit_clicked(icon):
    terminate_processes()
    icon.stop()


def get_device_state(v):
    def inner(item):
        if ssh and running_state:
            return True
        elif not running_state or not ssh:
            return False

    return inner


def device_run_command(cmd):
    def inner(_):
        print(cmd)
        subprocess.Popen('ssh -f root@localhost -p 2222 "' + cmd + '"', shell=True)
    return inner
def set_udid_clicked():
    import tkinter as tk  
    from tkinter import ttk
    win = tk.Tk()# Application Name  
    win.title("iproxyapplet")# Label  
    lbl = ttk.Label(win, text = "UDID:").grid(column = 0, row = 0)# Click event  
    def click():   
        print(name.get())# Textbox widget  
    name = tk.StringVar()  
    nameEntered = ttk.Entry(win, width = 12, textvariable = name).grid(column = 0, row = 1)# Button widget  
    button = ttk.Button(win, text = "Set", command = click).grid(column = 1, row = 1)  
    win.mainloop()
# Update the state in `on_clicked` and return the new state in
# a `checked` callable

device_command_submenu = item(
    "Device",
    menu(
        item(
            "Respring",
            device_run_command("sbreload"),
            enabled=get_device_state(item.enabled),
        ),
        item(
            "LDRestart",
            device_run_command("ldrestart"),
            enabled=get_device_state(item.enabled),
        ),
        item(
            "Userspace Reboot",
            device_run_command("launchctl reboot userspace"),
            enabled=get_device_state(item.enabled),
        ),
    ),
    enabled=installed
)


menu = (
    item(
        "iProxy Installed" if installed else "iProxy Not Installed",
        0,
        enabled=False,
        default=True,
    ),
    item(running_status, 0, enabled=False, default=True),
    item(
        "ssh -> 2222",
        ssh_clicked,
        checked=lambda item: ssh,
        enabled=get_radio_state(item.enabled),
    ),
    item(
        "debug -> 1234",
        debug_clicked,
        checked=lambda item: debug,
        enabled=get_radio_state(item.enabled),
    ),
    item("Start", start_clicked, enabled=get_start_state(item.enabled)),
    item("Stop", stop_clicked, enabled=get_stop_state(item.enabled)),
    device_command_submenu,
    item("Exit", exit_clicked),
    item('Custom UDID', set_udid_clicked)
    )

image = Image.open("icon.png")


applet = icon("iProxy", image, menu=menu)


applet.run()

