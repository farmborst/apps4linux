#!/usr/bin/python3
# -*- coding: utf-8 -*-
'''
author: Felix Kramer
mail: 	felix.kramer@physik.hu-berlin.de
version:
    Created         01.09.2015
    Last Update     01.09.2015
tested on python 3.4.2 and 2.7.9 (Debian 8)
'''
try:
    import Tkinter as tk
except:
    import tkinter as tk
from subprocess import call
from time import sleep


def conkynlxpanel():
    call("killall conky", shell=True)
    sleep(1)
    call("lxpanelctl restart", shell=True)
    sleep(3)
    call("conky -d -q -c /etc/conky/conky.conf", shell=True)


def internal():
    call("internal.sh", shell=True)
    conkynlxpanel()


def external():
    call("external.sh", shell=True)
    conkynlxpanel()


def extend():
    call("extend.sh", shell=True)
    conkynlxpanel()


def clone():
    call("clone.sh", shell=True)
    conkynlxpanel()

clone()

root = tk.Tk()
root.title('Display Menu')

inter = tk.Button(root, text='Internal', width=20, command=internal).pack()
exter = tk.Button(root, text='External', width=20, command=external).pack()
exten = tk.Button(root, text='Extend', width=20, command=extend).pack()
clone = tk.Button(root, text='Clone', width=20, command=clone).pack()
quitb = tk.Button(root, text='Exit', width=20, command=root.destroy).pack()

root.mainloop()
