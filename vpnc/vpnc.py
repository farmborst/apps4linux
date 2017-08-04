#!/usr/bin/python
# -*- coding: utf-8 -*-
# ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
from __future__ import print_function, division
try:
    from Tkinter import Tk, StringVar, Label, Button
    from Queue import Queue, Empty
except ImportError:
    from tkinter import Tk, StringVar, Label, Button
    from queue import Queue, Empty
from subprocess import Popen, PIPE, call
from time import sleep, strftime
from threading import Thread


class NBSR:  # Non blocking stream reader
    def __init__(self, stream):
        def _populateQueue(stream, queue):
            while True:
                try:
                    queue.put(stream.readline())
                except:
                    pass

        self._q = Queue()
        self._t = Thread(target=_populateQueue, args=(stream, self._q))
        self._t.daemon = True
        self._t.start()

    def readline(self, timeout=0.1):
        try:
            return self._q.get(timeout=timeout)
        except Empty:
            return None


def check(r, q, proc):

    nbsr = NBSR(proc.stdout)

    def execute(cmd):
        proc.stdin.write(cmd + ' \n')

    def emptystdout():
        while 1:
            output = nbsr.readline(timeout=0.5)
            if not output:
                break

    def printstdout():
        while 1:
            output = nbsr.readline(timeout=0.5)
            if not output:
                break
            print(output)

    def getstdout():
        output = []
        while 1:
            tmpoutput = nbsr.readline(timeout=0.5)
            if not tmpoutput:
                return output
                break
            output.append(tmpoutput)

    emptystdout()

    while q['run'].empty():
        timestring = strftime('   (%H:%M:%S)')
        execute('ping -I wlan0 -c1 8.8.8.8 | grep ttl')
        wlnout = getstdout()
        execute('ping -I tun0 -c1 8.8.8.8 | grep ttl')
        tunout = getstdout()
        try:
            wlanstr = wlnout[0].split("time=", 1)[1].rstrip()
            wlanstr = '        WLAN:   ' + wlanstr + timestring
        except:
            wlanstr = '        WLAN:   ' + 'failed' + timestring
        try:
            tunstr = tunout[0].split("time=", 1)[1].rstrip()
            tunstr = '    TUNNEL:   ' + tunstr + timestring
        except:
            tunstr = 'TUNNEL:   ' + 'failed' + timestring
        q['str'].put([wlanstr, tunstr])
        r.event_generate('<<update_label>>', when='tail')
        sleep(1)


def status(r, q, proc):
    t_run = Thread(target=check, args=(r, q, proc))
    t_run.setDaemon(True)
    t_run.start()


def restartopenvpn():
    sleep(3)


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


class GUI:
    def __init__(self):
        self.r = Tk()
        self.r.title('VPN STATS & CTRL')
        self.r.protocol("WM_DELETE_WINDOW", self.kill)
        self.threadsafe()
        self.layout()
        self.r.bind('<<update_label>>', self.updatelabels)

    def mainloop(self):
        self.r.mainloop()

    def threadsafe(self):
        self.q = {}
        self.q['run'] = Queue()
        self.q['str'] = Queue()

    def layout(self):
        self.wlnstr, self.tunstr = StringVar(), StringVar()
        Label(self.r, fg='blue', textvariable=self.wlnstr).pack()
        Label(self.r, fg='red', textvariable=self.tunstr).pack()
        Button(self.r, text='Restart', width=25, command=restartopenvpn).pack()
        Button(self.r, text='Mount Media', width=25, command=mountmedia).pack()
        Button(self.r, text='Unmount Media', width=25, command=unmountmedia).pack()
        Button(self.r, text='Mount Felix', width=25, command=mountfelix).pack()
        Button(self.r, text='Unmount Felix', width=25, command=unmountfelix).pack()

    def updatelabels(self, event):
        wlnstr, tunstr = self.q['str'].get()
        self.wlnstr.set(wlnstr)
        self.tunstr.set(tunstr)

    def kill(self):
        self.q['run'].put(False)
        self.r.after(20)
        self.r.destroy()
        self.r.quit()


if __name__ == '__main__':
    app = GUI()
    proc = Popen('ssh -T root@192.168.0.1', shell=True, stdin=PIPE,
                 stderr=PIPE, stdout=PIPE, universal_newlines=True, bufsize=0)
    status(app.r, app.q, proc)
    app.mainloop()
