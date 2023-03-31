import os
# import time
import datetime
import random
from enum import Enum

import pyautogui
from pynput import keyboard

import tkinter as tk
import ttkbootstrap as ttk
import threading

import json

"""
# AFKSaver
### v5 - 20230331
  - merged with win_rearrange https://github.com/noizze-net/win_rearrange

### v4 - 20200715
  - Save and Load config.json
  - Smaller window 360*320 to 300*200
  - PEP8
  - RUN/STOP button has greenish/reddish colours
"""
_appname = 'ASKSaver'
_version = '5(202300331)'


# notepad_hwnd = None
# gkeypressed = False


def todayAt(hr, min=0, sec=0, micros=0):
    now = datetime.datetime.now()
    return now.replace(hour=hr, minute=min, second=sec, microsecond=micros)


class ConfigJSON(dict):
    def __setitem__(self, key, item):
        self.__dict__[key] = item

    def __getitem__(self, key):
        return self.__dict__[key]

    def __repr__(self):
        return repr(self.__dict__)

    def __len__(self):
        return len(self.__dict__)

    def __delitem__(self, key):
        del self.__dict__[key]

    def clear(self):
        return self.__dict__.clear()

    def copy(self):
        return self.__dict__.copy()

    def has_key(self, k):
        return k in self.__dict__

    def update(self, *args, **kwargs):
        return self.__dict__.update(*args, **kwargs)

    def keys(self):
        return self.__dict__.keys()

    def values(self):
        return self.__dict__.values()

    def items(self):
        return self.__dict__.items()

    def pop(self, *args):
        return self.__dict__.pop(*args)

    def __cmp__(self, dict_):
        return self.__cmp__(self.__dict__, dict_)

    def __contains__(self, item):
        return item in self.__dict__

    def __iter__(self):
        return iter(self.__dict__)

    def __init__(self, fn='config.json'):
        if not os.path.isfile(fn):
            self.__dict__ = self.init_config_file()
        else:
            with open(fn) as fp:
                self.__dict__ = json.load(fp)
        self.fn = fn

    def init_config_file(self):
        c = self.__dict__
        c['interval'] = 10
        c['counter'] = 5
        c['time_start_working'] = '0800'
        c['time_end_working'] = '2200'
        c['window_geometry'] = ''
        c['quote'] = "You cannot learn how to write drama without writing plays, putting it on in front of an audience and getting humiliated."  # David Mamet
        self.save_all()
        return c

    def save(self, key, value):
        self.__dict__[key] = value
        self.save_all()

    def save_all(self):
        with open(self.fn, "w") as json_file:
            dict_to_save = self.__dict__.copy()
            try:
                del dict_to_save['fn']
            except AttributeError:
                pass
            json.dump(dict_to_save, json_file, indent=4, sort_keys=True)


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
        self.conf = ConfigJSON(fn='config.json')
        photo_ico = tk.PhotoImage(file='icon.png')
        self.app.wm_iconphoto(False, photo_ico)
        self.app.title(f"{_appname} - v{_version}")
        window_width = 300
        window_height = 200
        screen_width = self.app.winfo_screenwidth()
        screen_height = self.app.winfo_screenheight()
        x_cordinate = int((screen_width / 2) - (window_width / 2))
        y_cordinate = int((screen_height / 2) - (window_height / 2))
        # app_geo = f"{window_width}x{window_height}+{x_cordinate}+{y_cordinate}"
        app_geo = self.conf['window_geometry'] if self.conf['window_geometry'] else f"{window_width}x{window_height}+{x_cordinate}+{y_cordinate}"

        self.app.geometry(app_geo)
        self.app.resizable(height=False, width=False)

        # init UI
        status_label = ttk.Label(self.app, text='Stopped')
        status_label.pack(fill=tk.BOTH, expand=True)
        self.ui['status_label'] = status_label

        frame1 = tk.Frame(self.app)
        frame1.pack(anchor=tk.CENTER)

        status_interval = ttk.Label(frame1, text=f"interval[{self.conf['interval']}sec]")
        status_interval.pack(side='left')

        status_cnt = ttk.Label(frame1, text=f"CNT[0>{self.conf['counter']}]")
        status_cnt.pack(side='left')
        self.ui['status_cnt'] = status_cnt
        status_mouse = ttk.Label(frame1, text='M[None]')
        status_mouse.pack(side='left')
        self.ui['status_mouse'] = status_mouse
        status_kbd = ttk.Label(frame1, text='K[None]')
        status_kbd.pack(side='left')
        self.ui['status_kbd'] = status_kbd

        frame2 = ttk.Frame(self.app)
        frame2.pack(anchor=tk.CENTER)

        worktime_txt = 'W[{} - {}]'.format(self.conf['time_start_working'], self.conf['time_end_working'])
        worktime_lbl = ttk.Label(frame2, text=worktime_txt)
        worktime_lbl.pack()

        opt_button = ttk.Button(self.app, text='RUN', style='success') ## , bg='#41B199') green? TODO: button bg colour
        opt_button.bind('<Button-1>', self.opt_button_handler)
        opt_button.bind('<Double-Button-1>', self.opt_button_handler)
        opt_button.pack(fill=tk.BOTH, expand=True)
        self.ui['opt_button'] = opt_button

        notepad = ttk.Text(self.app, height=1, borderwidth=0)
        notepad.pack(fill=tk.BOTH, expand=True)
        self.ui['notepad'] = notepad

    def run(self):
        self.app.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.app.mainloop()

    def on_closing(self):
        self.conf.save('window_geometry', self.app.winfo_geometry())  # #3
        self.app.destroy()

    def opt_button_handler(self, event):
        if self.status == APP_STATUS.STOPPED:
            self._thread_handler = MockingUser(self, conf=self.conf, sleep_interval=self.conf['interval'])
            self._thread_handler.start()
            self.set_status('deactivate')
            self.ui['opt_button']['text'] = 'STOP'
            # self.ui['opt_button']['bg'] = '#FF6F4F'
            self.ui['opt_button'].configure(bootstyle="danger")
        else:
            self._thread_handler.kill()
            del self._thread_handler
            self.set_status('stop')
            self.ui['opt_button']['text'] = 'RUN'
            # self.ui['opt_button']['bg'] = '#41B199'
            self.ui['opt_button'].configure(bootstyle="success")

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
        word = s[random.randint(0, len(s) - 1)]
        # print(f'{time.asctime()} writing: {word}')
        self.ui['notepad'].delete(1.0, 'end')
        pyautogui.write(word, interval=0.25)
        pyautogui.write(' ')

    def set_status(self, status_str):
        if status_str == 'activate' and self.status != APP_STATUS.ACTIVATED:
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
        s = self.conf['time_start_working']
        e = self.conf['time_end_working']
        time_start_working = todayAt(hr=int(s[:2]), min=int(s[2:]))
        time_end_working = todayAt(hr=int(e[:2]), min=int(e[2:]))

        if time_start_working < datetime.datetime.now() < time_end_working:
            return True
        else:
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
