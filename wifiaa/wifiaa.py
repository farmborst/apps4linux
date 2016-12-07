# -*- coding: utf-8 -*-
"""
author: Felix Kramer
mail:   felix.kramer@physik.hu-berlin.de
"""
from __future__ import division, print_function
from os import system
from subprocess import Popen, PIPE
from shlex import split
from time import sleep, strftime
from numpy import nanmean, nanstd, array, linspace, save, load, arange
from matplotlib import rcdefaults, rcParams
from matplotlib.pyplot import figure, show, cm

print('=========================================')
print('Welcome to the Antenna Alignment Helper')
print('=========================================')

modes = ['fromfile', 'measurement']
mode = modes[1]
interface = 'wlan3'
ssid = 'eduroam'
wlancards = [
    'Intel Corporation Wireless 3160 (rev 83)',
    'Qualcomm Atheros AR928X Wireless Network Adapter (PCI-Express) (rev 01)']
filename = 'ubnt_axial_run1'
wlancard = 2
statistic = 40
#positions = arange(13.4,13.85,.05)
positions = arange(0, 26, 5)
savefig = False

print('Mode:       {}'.format(mode))
print('Interface:  {}'.format(interface))
print('SSID:       {}'.format(ssid))
print('Statistics: {}'.format(statistic))
print('Positions:  {}'.format(positions))
print('')

if mode == 'measurement':
    savefig = True

rcdefaults()
params = {'figure.figsize': [24, 13.5],
          'figure.dpi': 100,
          'figure.autolayout': False,
          'font.size': 14,
          'lines.linewidth': 2,
          'savefig.dpi': 100,
          'savefig.format': 'svg',
          'savefig.bbox': 'tight',
          'savefig.pad_inches': 0.1,
          'axes.grid': True,
          'axes.formatter.limits': (0, 3)}
rcParams.update(params)


def getdata(wlancard, ssid):
    if wlancard in [1, 2]:
        command = '/sbin/iwlist {} scanning'.format(interface)
        arg = split(command)
        proc = Popen(arg, stdout=PIPE)
        sleep(2)
        stdout, stderr = proc.communicate()
        data = stdout.split()
        match = 'ESSID:"' + ssid + '"'
        matchingcells = []
        for i, cell in enumerate(data):
            if cell == match:
                matchingcells.append(data[i-12:i-3])
        bssids, freqs, signals, qualities = [[] for i in range(4)]
        for cell in matchingcells:
            bssids.append(cell[0])
            freqs.append(float(cell[2][10:]))
            qualities.append(float(cell[6][8:10]))  # from 70
            signals.append(float(cell[8][6:]))
    elif wlancard == 3:
        command = '/sbin/iwlist {} scanning'.format(interface)
        arg = split(command)
        proc = Popen(arg, stdout=PIPE)
        sleep(2)
        stdout, stderr = proc.communicate()
        data = stdout.split()
        match = 'ESSID:"' + ssid + '"'
        matchingcells = []
        for i, cell in enumerate(data):
            if cell == match:
                matchingcells.append(data[i-12:i-3])
        bssids, freqs, signals, qualities = [[] for i in range(4)]
        for cell in matchingcells:
            print(cell[0])
            print(float(cell[2][10:]))
            print(float(cell[6][8:10]))  # from 70
            print(float(cell[8][6:]))
            sleep(5)
            bssids.append(cell[0])
            freqs.append(float(cell[2][10:]))
            qualities.append(float(cell[6][8:10]))  # from 70
            signals.append(float(cell[8][6:]))
    return bssids, freqs, signals, qualities


def update_dict(bssid_dict, bssid_tmpdict, pos):
    for bssid in bssid_tmpdict:
        freq = bssid_tmpdict[bssid]['frequency'][0]
        mean_signal = nanmean(bssid_tmpdict[bssid]['signal'])
        std_signal = nanstd(bssid_tmpdict[bssid]['signal'])
        mean_quality = nanmean(bssid_tmpdict[bssid]['quality'])
        std_quality = nanstd(bssid_tmpdict[bssid]['quality'])
        try:
            bssid_dict[bssid]['frequency'].append(freq)
            bssid_dict[bssid]['signal'].append([pos, mean_signal, std_signal])
            bssid_dict[bssid]['quality'].append([pos, mean_quality, std_quality])
        except:
            bssid_dict[bssid] = {}
            bssid_dict[bssid]['frequency'] = [freq]
            bssid_dict[bssid]['signal'] = [[pos, mean_signal, std_signal]]
            bssid_dict[bssid]['quality'] = [[pos, mean_quality, std_quality]]


def update_tmpdict(bssid_dict, bssids, freqs, signals, qualities):
    for bssid, freq, signal, quality in zip(bssids, freqs, signals, qualities):
        try:
            bssid_dict[bssid]['frequency'].append(freq)
            bssid_dict[bssid]['signal'].append(signal)
            bssid_dict[bssid]['quality'].append(quality)
        except:
            bssid_dict[bssid] = {}
            bssid_dict[bssid]['frequency'] = [freq]
            bssid_dict[bssid]['signal'] = [signal]
            bssid_dict[bssid]['quality'] = [quality]


def prepfig(title, positions):
    fig = figure()
    fig.suptitle(title)
    ax = fig.add_subplot(1, 1, 1)
    fig.subplots_adjust(left=0.05, right=0.9, top=0.95, bottom=0.07)
    ax.set_ylabel('Signal strength / dBm')
    ax.set_xlabel('Position')
    d = positions[1] - positions[0]
    ax.set_xlim([positions[0]-d, positions[-1]+d])
    return fig, ax


def figsave(fig, filename, filetype='pdf'):
    ''' figsave(filename, fig)
    input:
        - fig handle to save
        - desired filename as string
    return:
        - none
    notice:
    '''
    timstamp = strftime('%Y%m%d%H%M%S')
    filename = ''.join([timstamp, '_', filename, '.', filetype])
    fig.savefig(filename,
                frameon=False,
                )
    print ('\img{'+filename+'}')


def plotdata(bssid_dict, positions, savefig):
    fig1, ax1 = prepfig('2.4G', positions)
    fig2, ax2 = prepfig('5.2G', positions)
    c1_len = 0
    c2_len = 0
    for bssid in bssid_dict:
        f = bssid_dict[bssid]['frequency'][0]
        if f < 3:
            c1_len += 1
        elif f < 6:
            c2_len += 1
    c1 = iter(cm.rainbow(linspace(0, 1, c1_len)))
    c2 = iter(cm.rainbow(linspace(0, 1, c2_len)))
    for bssid in bssid_dict:
        length = range(len(bssid_dict[bssid]['signal'][:]))
        xstr = array([bssid_dict[bssid]['signal'][i][0] for i in length])
        strength = array([bssid_dict[bssid]['signal'][i][1] for i in length])
        strengtherr = array([bssid_dict[bssid]['signal'][i][2] for i in length])
        length = range(len(bssid_dict[bssid]['quality'][:]))
        f = bssid_dict[bssid]['frequency'][0]
        l = bssid + ' (' + str(f) + ' GHz)'
        if f < 3:
            c=next(c1)
            ax1.errorbar(xstr, strength, yerr=strengtherr, label=l,
                         marker='.', mfc=c, ecolor=c, mec=c, color=c)
        elif f < 6:
            c=next(c2)
            ax2.errorbar(xstr, strength, yerr=strengtherr, label=l,
                         marker='.', mfc=c, ecolor=c, mec=c, color=c)
    box = ax1.get_position()
    ax1.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    box = ax2.get_position()
    ax2.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    ax1.legend(loc="upper left", bbox_to_anchor=(1,1))
    ax2.legend(loc="upper left", bbox_to_anchor=(1,1))
    if savefig:
        figsave(fig1, filename+'_2G')
        figsave(fig2, filename+'_5G')
    show()


def run(interface, positions, statistic, ssid):
    bssid_dict = {}
    for pos in positions:
        print('Position {}, press enter to start'.format(pos), end='')
        raw_input('')
        print('    ...', end='')
        bssid_tmpdict = {}
        for stat in range(statistic):
            bssids, freqs, signals, qualities = getdata(wlancard, ssid)
            update_tmpdict(bssid_tmpdict, bssids, freqs, signals, qualities)
        update_dict(bssid_dict, bssid_tmpdict, pos)
        print('...done')
        system('play  --no-show-progress --null --channels 1 synth %s sine %f' % (.3, 500))
    system('play  --no-show-progress --null --channels 1 synth %s sine %f' % (.1, 500))
    system('play  --no-show-progress --null --channels 1 synth %s sine %f' % (.1, 500))
    system('play  --no-show-progress --null --channels 1 synth %s sine %f' % (.9, 600))
    return bssid_dict

if mode == 'measurement':
    bssid_dict = run(interface, positions, statistic, ssid)
    timstamp = strftime('%Y%m%d%H%M%S')
    filename = ''.join([timstamp, '_', filename])
    save(filename, [positions, bssid_dict])
elif mode == 'fromfile':
    positions, bssid_dict = load(filename+'.npy')
plotdata(bssid_dict, positions, savefig)
