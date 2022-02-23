#!/usr/bin/env python3
from pystray import Icon as icon, Menu as menu, MenuItem as item
from PIL import Image
import subprocess
from sys import platform
from shutil import which
import argparse
import sys

class Applet:
    running_state = False
    installed = which("iproxy") is not None
    ssh = True
    debug = False
    iproxy_process = None
    ports = ["2222:22"]
    applet : icon
    optional_port_menu = item(
                            "Extra Ports",
                            0,visible=False)
    optional_ports = {}


    def ssh_clicked(self,icon, item):
        self.ssh = not item.checked
        if self.ssh:
            if "2222:22" not in self.ports:
                self.ports.append("2222:22")
        elif not self.ssh:
            if "2222:22" in self.ports:
                self.ports.remove("2222:22")
        print("ports: ", self.ports)
        


    def debug_clicked(self,icon, item):
        self.debug = not item.checked
        if self.debug:
            if "1234:1234" not in self.ports:
                self.ports.append("1234:1234")
        elif not self.debug:
            if "1234:1234" in self.ports:
                self.ports.remove("1234:1234")
        print("ports: ", self.ports)


    def terminate_process(self):
        if self.iproxy_process is not None and self.running_state:
            if self.iproxy_process.poll() is None:
                print("Terminating iproxy_process with pid", self.iproxy_process.pid)
                self.iproxy_process.terminate()

    def start_clicked(self,icon, item):
        if len(self.ports) != 0:
            self.running_state = True
            #optional_ports
            optports = " "
            for key, value in self.optional_ports.items():
                if value:
                    optports += str(key) + " "
            command = "iproxy " + ' '.join(self.ports) + optports
            print(command)
            self.iproxy_process = subprocess.Popen(command, shell=True)
            print("Started iproxy_process with pid", self.iproxy_process.pid)


    def stop_clicked(self,icon, item):
        self.terminate_process()
        self.running_state = False


    def get_radio_state(self,v):
        def inner(item):
            if self.running_state and self.installed:
                return False
            elif not self.running_state and self.installed:
                return True

        return inner


    def get_start_state(self,v):
        def inner(item):
            if not self.ssh and not self.debug:  # not selected
                return False
            elif not self.running_state and self.installed:
                return True
            elif self.running_state:
                return False

        return inner


    def get_stop_state(self,v):
        def inner(item):
            if not self.ssh and not self.debug:  # not selected
                return False
            elif not self.running_state:
                return False
            else:
                return True

        return inner


    def running_status(self,_):
        if self.running_state:
            status = "Running: "
            if self.ssh:
                status += "ssh "
            if self.debug:
                status += "debug "
            for key,value in self.optional_ports.items():
                if value:
                    status += key + " "
            return status
        else:
            return "Idle"
        # return 'Running' if running_state else 'Not Running'


    def exit_clicked(self,icon):
        self.terminate_process()
        icon.stop()


    def get_device_state(self,v):
        def inner(item):
            if self.ssh and self.running_state:
                return True
            elif not self.running_state or not self.ssh:
                return False

        return inner

    def device_run_command(self,cmd):
        def inner(_):
            print(cmd)
            subprocess.Popen('ssh -f root@localhost -p 2222 "' + cmd + '"', shell=True)
        return inner
    def optional_port_menu_item_clicked(self,ports):
        def inner(_,item):
            self.optional_ports[ports] = not item.checked
        return inner
        
    def __init__(self) -> None:
        # disable python launcher icon in dock on darwin
        if platform == "darwin":
            print("darwin detected, enabling LSBackgroundOnly")
            import AppKit
            info = AppKit.NSBundle.mainBundle().infoDictionary()
            info["LSBackgroundOnly"] = "1"

        #parse args 
        parser = argparse.ArgumentParser()
        parser.add_argument('port_forward', metavar='LocalPort:DevicePort', type=str, nargs='*', help="port forwarding")
        args = parser.parse_args()

        optional_port_menu_items = []
        for arg in args.port_forward:
            try:
                rport, lport = arg.split(":")
                rport = int(rport)
                lport = int(lport)

                if isinstance(rport,int) and isinstance(lport,int):
                    self.optional_ports[arg] = True
                    optional_port_menu_items.append(item(arg,self.optional_port_menu_item_clicked(arg),checked=lambda _: self.optional_ports[arg],enabled=self.get_radio_state(item.enabled)))
                    self.optional_port_menu = item(
                            "Extra Ports:",
                            menu(*optional_port_menu_items),visible=True)
                    pass
            except:
                print("wrong usage")
                parser.print_help()
                sys.exit(1)
        #setup applet
        device_command_submenu = item(
            "Device",
            menu(
                item(
                    "Respring",
                    self.device_run_command("sbreload"),
                    enabled=self.get_device_state(item.enabled),
                ),
                item(
                    "LDRestart",
                    self.device_run_command("ldrestart"),
                    enabled=self.get_device_state(item.enabled),
                ),
                item(
                    "Userspace Reboot",
                    self.device_run_command("launchctl reboot userspace"),
                    enabled=self.get_device_state(item.enabled),
                ),
            ),
            enabled=self.installed
        )
        main_menu = (
            item(
                "iProxy Installed" if self.installed else "iProxy Not Installed",
                0,
                enabled=False,
                default=True,
            ),
            item(self.running_status, 0, enabled=False, default=True),
            item(
                "ssh -> 2222",
                self.ssh_clicked,
                checked=lambda _: self.ssh,
                enabled=self.get_radio_state(item.enabled),
            ),
            item(
                "debug -> 1234",
                self.debug_clicked,
                checked=lambda _: self.debug,
                enabled=self.get_radio_state(item.enabled),
            ),
            self.optional_port_menu,
            item("Start", self.start_clicked, enabled=self.get_start_state(item.enabled)),
            item("Stop", self.stop_clicked, enabled=self.get_stop_state(item.enabled)),
            device_command_submenu,
            item("Exit", self.exit_clicked),
            )
        image = Image.open("icon.png")
        self.applet = icon("iProxy", image, menu=main_menu)

def main():
    iproxyapplet = Applet()
    iproxyapplet.applet.run()

if __name__ == "__main__":
    main()
