# AFK Saver
 > opposite meanging of ScreenSaver 

![image](https://user-images.githubusercontent.com/819903/125231155-30f34600-e315-11eb-9239-112b24d38a07.png)

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

## Requirements 
```
MouseInfo==0.1.3
Pillow==8.3.1
PyAutoGUI==0.9.53
PyGetWindow==0.0.9
PyMsgBox==1.0.9
pynput==1.7.3
pyperclip==1.8.2
PyRect==0.1.4
PyScreeze==0.1.27
PyTweening==1.0.3
six==1.16.0
zstandard==0.15.2
```

## Build for win10_x64
```
> .venv/Script/activate
(.venv)> python -m nuitka --plugin-enable=tk-inter --mingw64 --windows-disable-console --onefile main.py -o AFKSaver.exe
```

## Credit 
made by YUChoe

[Apache License 2.0](https://github.com/YUChoe/AFKSaver/blob/main/LICENSE)
