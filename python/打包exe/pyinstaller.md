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

我们介绍一下前两种情况

### 第一种情况：```__file__```与```sys._MEIPASS```

一般，我们都是通过```__file__```来定位程序所在的目录，但打包后，就不行了

pyinstaller提供了```sys._MEIPASS```来解决，官方说明如下:
>When a bundled app starts up, the bootloader sets the sys.frozen attribute and stores the absolute path to the bundle folder in sys._MEIPASS. For a one-folder bundle, this is the path to that folder, wherever the user may have put it. For a one-file bundle, this is the path to the _MEIxxxxxx temporary folder created by the bootloader 

大概的代码就是
```python
import sys, os.path
if getattr( sys, 'frozen', False ) :
        # running in a bundle
        fpath = sys._MEIPASS
else :
        # running live
        fpath = os.path.dirname(__file__)
```





