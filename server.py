#!/usr/bin/python3

import subprocess
import sys
import os
import threading
import curses
from gi.repository import Playerctl

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

def accept_commands(device):
    print("opening " + device)
    f=open(device)
    end=False
    #p = DNY(get_player()) # todo lazy getting player
    p = cli()
    while(not end):
        s=f.readline()
        print(s)
        if (s.startswith('play')):
            p.play()
        elif (s.startswith('pause')):
            p.pause()
        elif (s.startswith('volup')):
            p.volume_up()
        elif (s.startswith('voldown')):
            p.volume_down()
        elif (s.startswith('forward')):
            p.forward()
        elif (s.startswith('backward')):
            p.backward()
        elif (s.startswith('exit')):
            end = True

print("Started")

command_thread = threading.Thread(target=accept_commands, args=[get_device()])

print("starting command thread")
command_thread.start()

#stdscr = curses.initscr()
#curses.noecho()
#curses.cbreak()
#stdscr.keypad(True)

def tui(stdscr):
    end = False
    last_key = ''
    sel = 0
    msg = ''

    #files = os.listdir("/mnt/d/mp3/Heather Nova/04 Oyster")
    directory = "/mnt/d/mp3/Mindless Self Indulgence"
    files = os.listdir(directory)

    while not end:
        stdscr.clear()

        for i in range(0, len(files)):
            if i == sel:
                stdscr.addstr(i,0, files[i], curses.A_REVERSE)
            else:
                stdscr.addstr(i,0, files[i])

        stdscr.addstr(len(files) + 4, 0, str(last_key))
        stdscr.addstr(len(files) + 5, 0, str(sel))
        stdscr.addstr(len(files) + 6, 0, msg)

        stdscr.refresh()
        last_key = stdscr.getch()
        if last_key == curses.KEY_DOWN:
            msg = 'key down'
            sel = min(sel + 1, len(files) - 1)
        elif last_key == curses.KEY_UP:
            msg = 'key up'
            sel = max(sel - 1, 0)
        elif last_key == curses.KEY_ENTER or last_key == 10:
            msg = 'enter '
            vlc_command('open', [os.path.join(directory, files[sel])])
        elif last_key == ord('x'):
            end = True
        else:
            msg = 'unknown'
    
#curses.wrapper(tui)

#curses.nocbreak()
#stdscr.keypad(False)
#curses.echo()

print("waiting for command thread to finish")
command_thread.join()

print("Done.")
