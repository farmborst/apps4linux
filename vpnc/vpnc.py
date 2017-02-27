#!/usr/bin/python
# -*- coding: utf-8 -*-
# ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
from __future__ import print_function, division
try:
    import Tkinter as tk
except:
    import tkinter as tk
from subprocess import call, Popen, PIPE
from time import sleep, strftime
from threading import Thread


def restartopenvpn():
    cmd = 'ssh root@192.168.0.1 "systemctl restart openvpn@client.service"'
    call(cmd, shell=True)
    sleep(3)


def run():
    tuncmd = 'ssh root@192.168.0.1 "ping -I tun0 -c1 8.8.8.8 | grep ttl"'
    wlncmd = 'ssh root@192.168.0.1 "ping -I wlan0 -c1 8.8.8.8 | grep ttl"'
    while True:
        timestr.set(strftime('%H:%M:%S'))
        try:
            ptuncmd = Popen(tuncmd, stdout=PIPE, stderr=PIPE, shell=True)
            pwlncmd = Popen(wlncmd, stdout=PIPE, stderr=PIPE, shell=True)
            tuncmdout, _ = ptuncmd.communicate()
            wlncmdout, _ = pwlncmd.communicate()
            tunstr.set(tuncmdout.split("time=", 1)[1].rstrip('\n'))
            wlanstr.set(wlncmdout.split("time=", 1)[1].rstrip('\n'))
        except:
            tunstr.set('failed')
            wlanstr.set('failed')
        sleep(1.1)


def status():
    t_run = Thread(target=run, args=())
    t_run.setDaemon(True)
    t_run.start()

root = tk.Tk()
root.title('VPN STATUS')

timestr = tk.StringVar()
wlanstr = tk.StringVar()
tunstr = tk.StringVar()
status()

timelabel = tk.Label(root, fg='green', textvariable=timestr).pack()
wlan0label = tk.Label(root, fg='green', textvariable=wlanstr).pack()
tun0label = tk.Label(root, fg='green', textvariable=tunstr).pack()
restart = tk.Button(root, text='Restart', width=20, command=restartopenvpn).pack()
quitbut = tk.Button(root, text='Exit', width=20, command=root.destroy).pack()


root.mainloop()