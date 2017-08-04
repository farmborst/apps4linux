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


def check():
    cmd = 'ssh root@192.168.0.1 "ping -I wlan0 -c1 8.8.8.8 | grep ttl && ping -I tun0 -c1 8.8.8.8 | grep ttl"'
    while 1:
        timestring = strftime('   (%H:%M:%S)')
        pcmd = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
        cmdout, _ = pcmd.communicate()
        lines = cmdout.splitlines()
        try:
            wlanstr = lines[0].split("time=", 1)[1].rstrip()
            wlanstr = '        WLAN:   ' + wlanstr + timestring
        except:
            wlanstr = '        WLAN:   ' + 'failed' + timestring
        try:
            tunstr = lines[1].split("time=", 1)[1].rstrip()
            tunstr = '    TUNNEL:   ' + tunstr + timestring
        except:
            tunstr = 'TUNNEL:   ' + 'failed' + timestring
        q.put([wlanstr, tunstr])
        root.event_generate('<<update_strings>>', when='tail')
        sleep(5)


def status():
    t_run = Thread(target=check)
    t_run.setDaemon(True)
    t_run.start()


def mountmedia():
    cmd = 'sshfs -o follow_symlinks media@192.168.0.1: /mnt/media/'
    call(cmd, shell=True)


def unmountmedia():
    cmd = 'fusermount -u /mnt/media/'
    call(cmd, shell=True)


def mountfelix():
    cmd = 'sshfs -o follow_symlinks felix@192.168.0.1: /home/user/mnt/felix/'
    call(cmd, shell=True)


def unmountfelix():
    cmd = 'fusermount -u /home/user/mnt/felix/'
    call(cmd, shell=True)


if __name__ == '__main__':
    root = Tk()
    q = Queue()
    root.title('VPN STATUS')
    wlnstrvar, tunstrvar = StringVar(), StringVar()

    def update_strings(event):
        wlnstr, tunstr = q.get()
        wlnstrvar.set(wlnstr)
        tunstrvar.set(tunstr)

    root.bind('<<update_strings>>', update_strings)
    wln0label = Label(root, fg='blue', textvariable=wlnstrvar).pack()
    tun0label = Label(root, fg='red', textvariable=tunstrvar).pack()
    Button(root, text='Restart', width=25, command=restartopenvpn).pack()
    Button(root, text='mount media', width=25, command=mountmedia).pack()
    Button(root, text='unmount media', width=25, command=unmountmedia).pack()
    Button(root, text='mount felix', width=25, command=mountfelix).pack()
    Button(root, text='unmount felix', width=25, command=unmountfelix).pack()
    status()
    mainloop()
