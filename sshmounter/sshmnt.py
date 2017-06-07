#!/usr/bin/python
# -*- coding: utf-8 -*-
# ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
from __future__ import print_function, division
try:
    from Tkinter import Tk, mainloop, Button
except:
    from tkinter import Tk, mainloop, Button
from subprocess import call


def mount():
    cmd = 'sshfs '
    for option in options:
        cmd += '-o ' + option + ' '
    cmd += '-p ' + port + ' '
    cmd += user + '@' + address + ':' + remotepath + ' ' + localpath
    call(cmd, shell=True)


def unmount():
    cmd = 'fusermount -u ' + localpath
    call(cmd, shell=True)


if __name__ == '__main__':
    root = Tk()
    root.title('SSHFS GUI')
    options = ['follow_symlinks']
    user = 'media'
    address = '192.168.0.1'
    remotepath = ''
    localpath = '/home/user/mnt/media/'
    port = '22'
    but_mount = Button(root, text='mount', width=25, command=mount).pack()
    but_unmount = Button(root, text='unmount', width=25, command=unmount).pack()
    mainloop()
