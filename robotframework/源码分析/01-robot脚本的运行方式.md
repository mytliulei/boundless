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

## robot script

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




