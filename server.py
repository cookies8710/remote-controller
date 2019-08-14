#!/usr/bin/python3

import subprocess
import sys
import os
import threading
import curses
#from gi.repository import Playerctl

def get_player():
    name = Playerctl.list_players()[0]
    player = Playerctl.Player.new_from_name(name)
    return player

class cli(object):
    def __init__(self):
        pass

    def play(self):
        subprocess.call(['playerctl', 'play'])

    def pause(self):
        subprocess.call(['playerctl', 'pause'])

    def forward(self):
        subprocess.call(['playerctl', 'position', '5+'])

    def backward(self):
        subprocess.call(['playerctl', 'position', '5-'])

    def volume_up(self):
        subprocess.call(['playerctl', 'volume', '0.05+'])

    def volume_down(self):
        subprocess.call(['playerctl', 'volume', '0.05-'])

class DNY(object):
    SEEK_STEP = 5 * 1000 * 1000 # 5 seconds
    VOLUME_STEP = 0.05 # 5 %

    def __init__(self, player):
        self.player = player

    def play(self):
        self.player.play()

    def pause(self):
        self.player.pause()

    def forward(self):
        self.player.seek(+DNY.SEEK_STEP)

    def backward(self):
        self.player.seek(-DNY.SEEK_STEP)

    def volume_delta(self, delta):
        current_volume = self.player.get_property('volume')
        new_volume = max(0.0, current_volume + delta)
        self.player.set_volume(new_volume)

    def volume_up(self):
        self.volume_delta(+DNY.VOLUME_STEP)

    def volume_down(self):
        self.volume_delta(-DNY.VOLUME_STEP)

#def vlc_command(cmd, params=[]):
#    subprocess.call(["playerctl", "--player=vlc", cmd] + params);

def get_device():
    serial_devices_path = "/dev/serial/by-id"
    serial_devices = os.listdir(serial_devices_path)
    if not serial_devices:
        raise RuntimeError("no serial devices found in " + serial_devices_path)
    arduino_serial = [x for x in serial_devices if 'usb-Arduino' in x]
    if not arduino_serial:
        raise RuntimeError("no arduino serial device found in " + serial_devices_path)
    if len(arduino_serial) > 1:
        raise RuntimeError("multiple arduino serial devices found in " + serial_devices_path)
    return os.path.join(serial_devices_path, arduino_serial[0])

def accept_commands(device, t):
    cmd_dict = {
            0x8e71f609: 'volume_up',
            0x8e710ef1: 'volume_down',
            0x8e7106f9: 'play',
            0x8e7116e9: 'pause',
            0x8e7146b9: 'forward',
            0x8E71C639: 'backward',
            0x8E716A95: 'up',
            0x8E71EA15: 'down',
            0x8E715AA5: 'enter'
            }
    print("opening " + device)
    f=open(device)
    end=False
    #p = DNY(get_player()) # todo lazy getting player
    p = cli()
    s=''
    while(not end):
        s=s + f.readline()
        if '\n' in s:
            print('read: %s' % s)
            try:
                d = int(s, base=16)
                if d in cmd_dict:
                    print(cmd_dict[d])
                    if cmd_dict[d] in dir(p):
                        getattr(p, cmd_dict[d])()
                    else:
                        t.handle_input(cmd_dict[d])
                else:
                    print('unknown signal 0x%X' % d)
            except Exception as error:
                pass
            s = ''

        # todo end

print("Started")

stdscr = curses.initscr()
curses.noecho()
curses.cbreak()
stdscr.keypad(True)

class tuio(object):
    @staticmethod
    def create(stdscr):
        to = tuio(stdscr)
        to.start()
        return to

    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.directory = "/mnt/d/data/Movies/=HD="
        self.files = self._get_files(self.directory)
        self.maxy = 20
        self.wpos=0

    sel = 0
    msg = ''

    def _get_files(self, directory):
        return ['..'] + os.listdir(directory)

    #self.files = os.listdir("/mnt/d/mp3/Heather Nova/04 Oyster")
    #directory = "/mnt/d/data/Movies/=HD="
    #files = _get_files(directory)
   # self.directory = "/media/home-media/oskar"
    #files = ['..'] + os.listdir(directory)

    def redraw(self):
        self.stdscr.clear()

        self.stdscr.addstr(0,0, self.directory, curses.A_REVERSE)
        base = 2
        
        


        for i in range(0, min(self.maxy, len(self.files))):
            fl = self.files[i + self.wpos]
            if i + self.wpos == self.sel:
                self.stdscr.addstr(base + i,0, fl, curses.A_REVERSE)
            elif os.path.isdir(os.path.join(self.directory, self.files[i])):
                self.stdscr.addstr(base + i,0, fl, curses.A_BOLD)
            else:
                self.stdscr.addstr(base + i,0, fl)

        #self.stdscr.addstr(len(self.files) + 4, 0, str(last_key))
        #self.stdscr.addstr(len(self.files) + 5, 0, str(self.sel))
        #self.stdscr.addstr(len(self.files) + 6, 0, self.msg)

        self.stdscr.refresh()

    def handle_input(self, i):
        if i == 'down':
            self.sel = min(self.sel + 1, len(self.files) - 1)
            if self.sel == self.wpos + self.maxy:
                self.wpos = self.wpos + 1
        elif i == 'up':
            self.sel = max(self.sel - 1, 0)
            if self.sel < self.wpos:
                self.wpos = self.wpos - 1
        elif i == 'enter':
            fs = self.files[self.sel]
            self.selected = os.path.join(self.directory, fs)
            if fs == '..':
                self.directory = os.path.dirname(self.directory)
                self.files = ['..'] + os.listdir(self.directory)
                self.msg='will enter super'
                self.wpos=0
                self.sel = 0
            elif os.path.isdir(self.selected):
                self.directory = self.selected
                self.sel = 0
                self.wpos=0
                self.files = ['..'] + os.listdir(self.directory)
            else:
                self.msg='will play file' + self.selected
                subprocess.call(['vlc', '-f', self.selected])

        self.redraw()

    def start(self, stdscr):
        end = False
        last_key = ''

        while not end:
            self.redraw()
            last_key = self.stdscr.getch()
            if last_key == curses.KEY_DOWN:
                self.handle_input('down')
            elif last_key == curses.KEY_UP:
                self.handle_input('up')
            elif last_key == curses.KEY_ENTER or last_key == 10:
                self.handle_input('enter')
            elif last_key == ord('x'):
                end = True
            else:
                self.msg = 'unknown'

x = tuio(stdscr)

command_thread = threading.Thread(target=accept_commands, args=[get_device(), x])
print("starting command thread")
command_thread.start()

curses.wrapper(x.start)
curses.nocbreak()
stdscr.keypad(False)
curses.echo()


print("waiting for command thread to finish")
command_thread.join()

print("Done.")
