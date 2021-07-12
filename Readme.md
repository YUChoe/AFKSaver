# AFK Saver
 > opposite meanging of ScreenSaver 
 
## Quote by David Mamet
 > You cannot learn how to write drama without writing plays, putting it on in front of an audience and getting humiliated.

## ChangeLog

### v3
- execute as .exe(Nuitka)
- working between 0830 and 2200

### v2 
- Tkinter for GUI
- Threading
- 10sec interval when it starts over AFK 5 times

### v1
- Catching KeyBoard and Mouse events
- Zigging every 30 seconds

## v1.2.1 - Get them while they're hot!
## Build for win10_x64
```
> .venv/Script/activate
(.venv)> python -m nuitka --plugin-enable=tk-inter --mingw64 --windows-disable-console --onefile main.py -o AFKSaver.exe
```

## Credit 
made by YUChoe

[Apache License](https://github.com/YUChoe/AFKSaver/blob/main/LICENSE)
