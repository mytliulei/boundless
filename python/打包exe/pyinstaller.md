_有时候我们不得不将python程序打包成exe发布_

# 介绍
pyinstaller是一个打包工具，下面是其[官方](http://www.pyinstaller.org/)给出的介绍
>PyInstaller bundles a Python application and all its dependencies into a single package. The user can run the packaged app without installing a Python interpreter or any modules. PyInstaller supports Python 2.7 and Python 3.3+, and correctly bundles the major Python packages such as numpy, PyQt, Django, wxPython, and others.

>PyInstaller is tested against Windows, Mac OS X, and Linux. However, it is not a cross-compiler: to make a Windows app you run PyInstaller in Windows; to make a Linux app you run it in Linux, etc. PyInstaller has been used successfully with AIX, Solaris, and FreeBSD, but is not tested against them.

# 安装
使用pip安装，[安装文档](https://pyinstaller.readthedocs.io/en/stable/installation.html)

推荐结合[virtualenv](http://www.liaoxuefeng.com/wiki/0014316089557264a6b348958f449949df42a6d3a2e542c000/001432712108300322c61f256c74803b43bfd65c6f8d0d0000)使用

# 使用方法

见[官方文档](https://pyinstaller.readthedocs.io/en/stable/usage.html)

# 注意事项

## 源码运行 or 打包运行？

我们总希望打包运行与源码运行是一致的，但实际上是不行的

[官方](https://pyinstaller.readthedocs.io/en/stable/runtime-information.html)的说明
>Your app should run in a bundle exactly as it does when run from source. However, you may need to learn at run-time whether the app is running from source, or is “frozen” (bundled). For example, you might have data files that are normally found based on a module’s __file__ attribute. That will not work when the code is bundled.

官方给出了解决方法：

The PyInstaller bootloader adds the name ```frozen``` to the ```sys``` module. So the test for “are we bundled?” is:
```python
import sys
if getattr( sys, 'frozen', False ) :
        # running in a bundle
else :
        # running live
```
当程序被打包执行时，pyinstaller的bootloader向sys中添加了frozen的属性，通过查看这个属性，可以判断程序是否是打包的exe环境

## data file
如果程序要访问data file，一般分3种情况

* data file被放置在程序目录里
* data file被放置在用户工作目录里
* data file被打包到程序里

一般，我们可以通过下面2种方法来解决

### ```__file__```与```sys._MEIPASS```

一般，我们都是通过```__file__```来定位执行的文件所在的目录，但打包后，就不行了

pyinstaller提供了```sys._MEIPASS```来解决，官方说明如下:
>When a bundled app starts up, the bootloader sets the sys.frozen attribute and stores the absolute path to the bundle folder in sys._MEIPASS. For a one-folder bundle, this is the path to that folder, wherever the user may have put it. For a one-file bundle, this is the path to the _MEIxxxxxx temporary folder created by the bootloader 

大概的代码就是
```python
import sys, os.path
if getattr(sys, 'frozen', False):
        # we are running in a bundle
        bundle_dir = sys._MEIPASS
else:
        # we are running in a normal Python environment
        bundle_dir = os.path.dirname(os.path.abspath(__file__))
```

### ```sys.executable```与```sys.argv[0]```

```sys.executable```：

* 源码情况下，指的是python解释器的路径
* 打包情况下，指的是打包程序所在路径

```sys.argv[0]```：

* 程序名称或路径，相对或绝对路径（取决于所在系统）
* 如果程序通过链接文件执行，则是链接文件的名称

官方解释如下：
>When a normal Python script runs, sys.executable is the path to the program that was executed, namely, the Python interpreter. In a frozen app, sys.executable is also the path to the program that was executed, but that is not Python; it is the bootloader in either the one-file app or the executable in the one-folder app. This gives you a reliable way to locate the frozen executable the user actually launched.

>The value of sys.argv[0] is the name or relative path that was used in the user’s command. It may be a relative path or an absolute path depending on the platform and how the app was launched.

>If the user launches the app by way of a symbolic link, sys.argv[0] uses that symbolic name, while sys.executable is the actual path to the executable. Sometimes the same app is linked under different names and is expected to behave differently depending on the name that is used to launch it. For this case, you would test os.path.basename(sys.argv[0])

>On the other hand, sometimes the user is told to store the executable in the same folder as the files it will operate on, for example a music player that should be stored in the same folder as the audio files it will play. For this case, you would use os.path.dirname(sys.executable)

下面这段程序：
```python
#!/usr/bin/python3
import sys, os
frozen = 'not'
if getattr(sys, 'frozen', False):
        # we are running in a bundle
        frozen = 'ever so'
        bundle_dir = sys._MEIPASS
else:
        # we are running in a normal Python environment
        bundle_dir = os.path.dirname(os.path.abspath(__file__))
print( 'we are',frozen,'frozen')
print( 'bundle dir is', bundle_dir )
print( 'sys.argv[0] is', sys.argv[0] )
print( 'sys.executable is', sys.executable )
print( 'os.getcwd is', os.getcwd() )
```

源码的执行结果：
```
(pyinstaller) E:\test\pyinstaller>python directories.py
('we are', 'not', 'frozen')
('bundle dir is', 'E:\\test\\pyinstaller')
('sys.argv[0] is', 'directories.py')
('sys.executable is', 'E:\\VirtualEnv\\pyinstaller\\Scripts\\python.exe')
('os.getcwd is', 'E:\\test\\pyinstaller')
```

打包为目录的执行结果：
```
(pyinstaller) E:\test\pyinstaller>dist\directories\directories.exe
('we are', 'ever so', 'frozen')
('bundle dir is', 'E:\\test\\PYINST~1\\dist\\DIRECT~1')
('sys.argv[0] is', 'dist\\directories\\directories.exe')
('sys.executable is', 'E:\\test\\pyinstaller\\dist\\directories\\directories.exe
')
('os.getcwd is', 'E:\\test\\pyinstaller')
```
打包为单一文件的执行结果：
```
(pyinstaller) E:\test\pyinstaller>dist\directories.exe
('we are', 'ever so', 'frozen')
('bundle dir is', 'C:\\Users\\Lenovo\\AppData\\Local\\Temp\\_MEI77~1')
('sys.argv[0] is', 'dist\\directories.exe')
('sys.executable is', 'E:\\test\\pyinstaller\\dist\\directories.exe')
('os.getcwd is', 'E:\\test\\pyinstaller')
```

