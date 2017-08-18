本文以robotframework-3.0.2代码来分析

# robotframework执行脚本的方法

>Synopsis

```
robot [options] data_sources
python|jython|ipy -m robot [options] data_sources
python|jython|ipy path/to/robot/ [options] data_sources
java -jar robotframework.jar [options] data_sources
```
>Test execution is normally started using the robot runner script. Alternatively it is possible to execute the installed robot module or robot directory directly using the selected interpreter. The final alternative is using the standalone JAR distribution.

上述摘自[robot官方文档](http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#executing-test-cases)

## Using robot scripts

下面是windows上的pybot.bat的内容
```
@echo off
python -m robot.run %*
```

可以看到脚本最终调用`python -m robot.run`来运行

我们来看robot源码目录下的`__init__.py`和`run.py`文件


```python
# __init__.py
from robot.rebot import rebot, rebot_cli
from robot.run import run, run_cli
from robot.version import get_version


__all__ = ['run', 'run_cli', 'rebot', 'rebot_cli']
__version__ = get_version()
```

```python
# run.py

import sys

# Allows running as a script. __name__ check needed with multiprocessing:
# https://github.com/robotframework/robotframework/issues/1137
if 'robot' not in sys.modules and __name__ == '__main__':
    import pythonpathsetter
#.....
#.....

if __name__ == '__main__':
    run_cli(sys.argv[1:])
```

python会import robot.run，然后将robot.run当做脚本来运行，即执行run.py，此时__name__ == '__main__'，即执行run_cli(sys.argv[1:])

## Executing installed robot module

使用[python -m](https://docs.python.org/2/using/cmdline.html#cmdoption-m)参数来执行，格式
```
python -m robot [options] data_sources
python -m robot.run [options] data_sources
```
第一种格式会调用robot.__main__.py文件
```python
import sys

# Allows running as a script. __name__ check needed with multiprocessing:
# https://github.com/robotframework/robotframework/issues/1137
if 'robot' not in sys.modules and __name__ == '__main__':
    import pythonpathsetter

from robot import run_cli


run_cli(sys.argv[1:])
```

这里我们没有使用`if __name__ == '__main__':`，是因为只有使用python -m时才会调用__main__.py文件，并且`__name__='__main__'`


## Executing installed robot directory

命令格式
```
python path/to/robot/ tests.robot
python path/to/robot/run.py tests.robot
```
当使用目录作为参数时，会调用目录下的__main__.py文件，由于robot的目录可能不在sys.path里，会导致无法import，下面的代码可以解决这类问题
```python
if 'robot' not in sys.modules and __name__ == '__main__':
    import pythonpathsetter
```

下面是pythonpathsetter.py的内容
```python
"""Module that adds directories needed by Robot to sys.path when imported."""

import sys
import fnmatch
from os.path import abspath, dirname

# robot的目录位置
ROBOTDIR = dirname(abspath(__file__))

def add_path(path, end=False):
    if not end:
        remove_path(path)
        sys.path.insert(0, path)
    elif not any(fnmatch.fnmatch(p, path) for p in sys.path):
        sys.path.append(path)

def remove_path(path):
    sys.path = [p for p in sys.path if not fnmatch.fnmatch(p, path)]


# When, for example, robot/run.py is executed as a script, the directory
# containing the robot module is not added to sys.path automatically but
# the robot directory itself is. Former is added to allow importing
# the module and the latter removed to prevent accidentally importing
# internal modules directly.
add_path(dirname(ROBOTDIR))
remove_path(ROBOTDIR)
```

当文件作为参数时，会直接调用该文件，也可能会出现上述问题

# 参考文档

- [fnmatch](https://docs.python.org/2/library/fnmatch.html)
- [python -m](https://docs.python.org/2/using/cmdline.html#cmdoption-m)
- https://github.com/robotframework/robotframework/issues/1137: 防止在windows系统上使用multiprocessing时出错，请参考以下内容
    -. http://rhodesmill.org/brandon/2010/python-multiprocessing-linux-windows/
    -. https://stackoverflow.com/questions/14175348/why-does-pythons-multiprocessing-module-import-main-when-starting-a-new-pro
    -. https://docs.python.org/2/library/multiprocessing.html#windows
    -. https://pymotw.com/2/multiprocessing/basics.html

