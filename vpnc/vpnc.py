#!/usr/bin/python
# -*- coding: utf-8 -*-
# ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
from __future__ import print_function, division
try:
    from Tkinter import Tk, mainloop, StringVar, Label, Button
except:
    from tkinter import Tk, mainloop, StringVar, Label, Button
from subprocess import call, Popen, PIPE
from time import sleep, strftime
from threading import Thread
from Queue import Queue


def restartopenvpn():
    cmd = 'ssh root@192.168.0.1 "systemctl restart openvpn@client.service"'
    call(cmd, shell=True)
    sleep(3)


def runtun():
    tuncmd = 'ssh root@192.168.0.1 "ping -I tun0 -c1 8.8.8.8 | grep ttl"'
    while 1:
        try:
            ptuncmd = Popen(tuncmd, stdout=PIPE, shell=True)
            tuncmdout, _ = ptuncmd.communicate()
            tunstr = tuncmdout.split("time=", 1)[1].rstrip()
            tunstr = 'TUNNEL:   ' + tunstr + strftime('   (%H:%M:%S)')
        except:
            tunstr = 'TUNNEL:   ' + 'failed' + strftime('   (%H:%M:%S)')
        q.put(tunstr)
        root.event_generate('<<update_tunstrvar>>', when='tail')
        sleep(1)


def runwln():
    wlncmd = 'ssh root@192.168.0.1 "ping -I wlan0 -c1 8.8.8.8 | grep ttl"'
    while 1:
        try:
            pwlncmd = Popen(wlncmd, stdout=PIPE, shell=True)
            wlncmdout, _ = pwlncmd.communicate()
            wlanstr = wlncmdout.split("time=", 1)[1].rstrip()
            wlanstr = '   WLAN:   ' + wlanstr + strftime('   (%H:%M:%S)')
        except:
            wlanstr = '   WLAN:   ' + 'failed' + strftime('   (%H:%M:%S)')
        q.put(wlanstr)
        root.event_generate('<<update_wlnstrvar>>', when='tail')
        sleep(1)


def status():
    t1_run = Thread(target=runtun)
    t1_run.setDaemon(True)
    t1_run.start()
    t2_run = Thread(target=runwln)
    t2_run.setDaemon(True)
    t2_run.start()


if __name__ == '__main__':
    root = Tk()
    q = Queue()
    root.title('VPN STATUS')
    wlnstrvar = StringVar()
    tunstrvar = StringVar()
    update_wlnstrvar = lambda event: wlnstrvar.set(q.get())
    update_tunstrvar = lambda event: tunstrvar.set(q.get())
    root.bind('<<update_wlnstrvar>>', update_wlnstrvar)
    root.bind('<<update_tunstrvar>>', update_tunstrvar)
    wln0label = Label(root, fg='blue', textvariable=wlnstrvar).pack()
    tun0label = Label(root, fg='red', textvariable=tunstrvar).pack()
    restart = Button(root, text='Restart', width=25, command=restartopenvpn).pack()
    status()
    mainloop()
