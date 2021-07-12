import os
import time
import datetime
import random
from enum import Enum

import pyautogui
from pynput import keyboard

import tkinter as tk
import threading

import json

"""
# AFKSaver 

"""
_appname = 'ASKSaver'
_version = '3(20200710)'


notepad_hwnd = None
gkeypressed = False



def todayAt (hr, min=0, sec=0, micros=0):
    now = datetime.datetime.now()
    return now.replace(hour=hr, minute=min, second=sec, microsecond=micros)


class APP_STATUS(Enum):
    STOPPED = 0
    DEACTIVATED = 1
    ACTIVATED = 2


class Main_App():
    app = tk.Tk()
    ui = {}
    status = APP_STATUS.STOPPED
    _thread_handler = None
    focused = False
    conf = {}

    def __init__(self, version=_version):
        self.app.title (f"{_appname} - v{_version}")
        window_width = 360
        window_height = 320
        screen_width = self.app.winfo_screenwidth()
        screen_height = self.app.winfo_screenheight()

        x_cordinate = int((screen_width / 2) - (window_width / 2))
        y_cordinate = int((screen_height / 2) - (window_height / 2))

        self.app.geometry(f"{window_width}x{window_height}+{x_cordinate}+{y_cordinate}")
        self.app.resizable(height=False, width=False)

        # status label
        # button start / stop
        # textarea
        # configuration - off time begin / finish
        #               - text to write
        self.conf['interval'] = 10
        self.conf['counter'] = 5
        self.conf['time_start_working'] = None
        self.conf['time_end_working'] = None

        # init UI
        status_label = tk.Label(self.app, text='Stopped')
        status_label.pack(fill=tk.BOTH, expand=True)
        self.ui['status_label'] = status_label

        frame1 = tk.Frame(self.app)
        frame1.pack(anchor=tk.CENTER)

        status_interval = tk.Label(frame1, text=f"interval[{self.conf['interval']}sec]")
        status_interval.pack(side='left')

        status_cnt = tk.Label(frame1, text=f"CNT[0>{self.conf['counter']}]")
        status_cnt.pack(side='left')
        self.ui['status_cnt'] = status_cnt
        status_mouse = tk.Label(frame1, text='M[None]')
        status_mouse.pack(side='left')
        self.ui['status_mouse'] = status_mouse
        status_kbd = tk.Label(frame1, text='K[None]')
        status_kbd.pack(side='left')
        self.ui['status_kbd'] = status_kbd

        # opt_button = tk.Button(self.app, text='RUN', command=self.opt_button_handler)
        opt_button = tk.Button(self.app, text='RUN')
        opt_button.bind('<Button-1>', self.opt_button_handler)
        opt_button.bind('<Double-Button-1>', self.opt_button_handler)
        opt_button.pack(fill=tk.BOTH, expand=True)
        self.ui['opt_button'] = opt_button

        notepad = tk.Text(self.app, height=1, borderwidth=0)
        notepad.pack(fill=tk.BOTH, expand=True)
        self.ui['notepad'] = notepad

        # TODO: configuration UI


    def run(self):
        self.app.mainloop()

    def opt_button_handler(self, event):
        if self.status == APP_STATUS.STOPPED:
            self._thread_handler = MockingUser(self, conf=self.conf, sleep_interval=self.conf['interval'])
            self._thread_handler.start()
            self.set_status('deactivate')
            self.ui['opt_button']['text'] =  'STOP'
            # print(time.asctime(), 'started')
        else:
            self._thread_handler.kill()
            del self._thread_handler
            self.set_status('stop')
            self.ui['opt_button']['text'] =  'RUN'
            # print(time.asctime(), 'stopped')

    def focus(self):
        self.app.focus_force()
        if not self.focused:
            self.app.iconify()
            self.app.update()
            self.app.deiconify()
            self.focused = True
        self.ui['notepad'].focus_set()


    def press(self):
        txt = "You cannot learn how to write drama without writing plays, putting it on in front of an audience and getting humiliated."  # David Mamet
        s = txt.strip().split()
        word = s[random.randint(0, len(s)-1)]
        # print(f'{time.asctime()} writing: {word}')
        self.ui['notepad'].delete(1.0, 'end')
        pyautogui.write(word, interval=0.25)
        pyautogui.write(' ')

    def set_status(self, status_str):
        if status_str == 'activate' and self.status != APP_STATUS.ACTIVATED :
            self.ui['status_label']['text'] = 'Running - Activated'
            self.status = APP_STATUS.ACTIVATED
            # print(f'{time.asctime()} {status_str}')

        elif status_str == 'deactivate' and self.status != APP_STATUS.DEACTIVATED:
            self.ui['status_label']['text'] = 'Running - Deactivated'
            self.status = APP_STATUS.DEACTIVATED
            self.focused = False
            # print(f'{time.asctime()} {status_str}')

        elif status_str == 'stop' and self.status != APP_STATUS.STOPPED:
            self.ui['status_label']['text'] = 'Stopped'
            self.status = APP_STATUS.STOPPED
            # print(f'{time.asctime()} {status_str}')

    def update_cmk_status(self, c, m, k):
        self.ui['status_cnt']['text'] = f"CNT[{c}>{self.conf['counter']}]"
        self.ui['status_mouse']['text'] = f'M[{m}]'
        self.ui['status_kbd']['text'] = f'K[{k}]'

class MockingUser(threading.Thread):
    kpressed = False
    mmoved = False
    o_x, o_y = 0, 0
    cnt = 0

    def __init__(self, Main_App, conf={}, sleep_interval=3):
        super().__init__()
        self._kill = threading.Event()
        self._interval = sleep_interval
        self.Main_App = Main_App
        self.listener = keyboard.Listener(on_press=self.key_on_press)
        self.listener.start()
        self.o_x, self.o_y = pyautogui.position()
        self.conf = conf

    def key_on_press(self, key):
        self.kpressed = True

    def working_time(self):
        self.conf['time_start_working'] = todayAt(hr=8, min=30)
        self.conf['time_end_working'] = todayAt(hr=22, min=0)
        if self.conf['time_start_working'] < datetime.datetime.now() < self.conf['time_end_working']:
            # print("working_time", True, self.conf['time_start_working'], datetime.datetime.now(), self.conf['time_end_working'])
            return True
        else:
            print("working_time", False, self.conf['time_start_working'], datetime.datetime.now(), self.conf['time_end_working'])
            return False

    def run(self):
        while True:
            is_killed = self._kill.wait(self._interval)
            if is_killed:
                break

            c_x, c_y = pyautogui.position()
            if self.o_x != c_x or self.o_y != c_y:
                self.mmoved = True

            if self.mmoved or self.kpressed or not self.working_time():
                self.cnt = 0
                self.Main_App.set_status('deactivate')
            else:
                self.cnt += 1
            # print(f'{time.asctime()} cnt:[{self.cnt}] mmoved[{self.mmoved}] kpressed[{self.kpressed}]')
            self.Main_App.update_cmk_status(self.cnt, self.mmoved, self.kpressed)

            if self.cnt > self.conf['counter']:
                self.Main_App.set_status('activate')
                self.Main_App.focus()
                self.Main_App.press()

            self.o_x, self.o_y = c_x, c_y
            self.kpressed = False
            self.mmoved = False

    def kill(self):
        self._kill.set()

if __name__ == '__main__':
    app = Main_App()
    app.run()
    exit()