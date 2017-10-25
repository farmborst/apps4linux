#!/usr/bin/python
# -*- coding: utf-8 -*-
# ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
from __future__ import print_function, division
try:
    from Tkinter import Tk, StringVar, Label, Button, W, BOTH, LEFT
    from Queue import Queue, Empty
except ImportError:
    from tkinter import Tk, StringVar, Label, Button, W, BOTH, LEFT
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


def check(r, q):

    def execute(proc, cmd):
        proc.stdin.write(cmd + ' \n')

    def emptystdout(nbsr):
        while 1:
            output = nbsr.readline(timeout=1)
            if not output:
                break

    def getstdout(nbsr):
        output = []
        while 1:
            tmpoutput = nbsr.readline(timeout=2)
            if not tmpoutput:
                return output
                break
            output.append(tmpoutput)

    def out2str(iface, nbsr, results, index, timestring):
        out = getstdout(nbsr)
        try:
            resptime = out[0].split("time=", 1)[1].rstrip()
        except:
            resptime = 'failed'
        results[index] = '{0:>8}: {1:<8} {2}'.format(iface, resptime, timestring)

    results = [None] * 3
    procs, nbsrs = [], []

    cmnds = ['bash',
             'ssh -T root@192.168.0.1',
             'ssh -T root@192.168.0.1']

    for cmd in cmnds:
        procs.append(Popen(cmd, shell=True, stdin=PIPE, stderr=PIPE,
                           stdout=PIPE, universal_newlines=True, bufsize=0))
    for proc in procs:
        nbsrs.append(NBSR(proc.stdout))

    for nbsr in nbsrs:
        emptystdout(nbsr)

    ifaces = ['SERVER',
              'WLAN',
              'TUNNEL']
    cmnds = ['ping -c1 -W1.5 192.168.0.1 | grep ttl',
             'ping -I wlp2s0 -c1 -W1.5 8.8.8.8 | grep ttl',
             'ping -I tun0 -c1 -W1.5 8.8.8.8 | grep ttl']

    while q['run'].empty():
        timestring = strftime('   (%H:%M:%S)')

        for proc, cmd in zip(procs, cmnds):
            execute(proc, cmd)

        threads = []
        for i, iface in enumerate(ifaces):
            threads.append(Thread(target=out2str, args=(iface, nbsrs[i], results, i, timestring)))
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        q['str'].put(results)
        r.event_generate('<<update_label>>', when='tail')
        sleep(0.1)


def status(r, q):
    t_run = Thread(target=check, args=(r, q))
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
        packsets = {'fill'   : BOTH,
                    'expand' : 1,
                    'anchor' : 'w'}
        lablsets = {'font'   : 'mono',
                    'anchor' : 'w'}
        self.srvstr, self.wlnstr, self.tunstr = StringVar(), StringVar(), StringVar()
        Label(self.r, fg='green', textvariable=self.srvstr, **lablsets).pack(packsets)
        Label(self.r, fg='blue', textvariable=self.wlnstr, **lablsets).pack(packsets)
        Label(self.r, fg='red', textvariable=self.tunstr, **lablsets).pack(packsets)
        Button(self.r, text='Restart', width=25, command=restartopenvpn).pack(packsets)
        Button(self.r, text='Mount Media', width=25, command=mountmedia).pack(packsets)
        Button(self.r, text='Unmount Media', width=25, command=unmountmedia).pack(packsets)
        Button(self.r, text='Mount Felix', width=25, command=mountfelix).pack(packsets)
        Button(self.r, text='Unmount Felix', width=25, command=unmountfelix).pack(packsets)

    def updatelabels(self, event):
        srvstr, wlnstr, tunstr = self.q['str'].get()
        self.srvstr.set(srvstr)
        self.wlnstr.set(wlnstr)
        self.tunstr.set(tunstr)

    def kill(self):
        self.q['run'].put(False)
        self.r.after(20)
        self.r.destroy()
        self.r.quit()


if __name__ == '__main__':
    app = GUI()
    status(app.r, app.q)
    app.mainloop()
