REM 因为加上-w即取消cmd窗口，若取消窗口则运行软件点击下载会抛winError6句柄无效异常
pyinstaller -F download.py ico.py -i favicon.ico
pause