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

## run与run_cli

上述的启动方法，最终都是使用run_cli来执行，其实也可以使用run来执行，参见run.py
```python
def run_cli(arguments, exit=True):
    """Command line execution entry point for running tests.

    :param arguments: Command line options and arguments as a list of strings.
    :param exit: If ``True``, call ``sys.exit`` with the return code denoting
        execution status, otherwise just return the rc. New in RF 3.0.1.

    Entry point used when running tests from the command line, but can also
    be used by custom scripts that execute tests. Especially useful if the
    script itself needs to accept same arguments as accepted by Robot Framework,
    because the script can just pass them forward directly along with the
    possible default values it sets itself.

    Example::

        from robot import run_cli

        # Run tests and return the return code.
        rc = run_cli(['--name', 'Example', 'tests.robot'], exit=False)

        # Run tests and exit to the system automatically.
        run_cli(['--name', 'Example', 'tests.robot'])

    See also the :func:`run` function that allows setting options as keyword
    arguments like ``name="Example"`` and generally has a richer API for
    programmatic test execution.
    """
    return RobotFramework().execute_cli(arguments, exit=exit)


def run(*tests, **options):
    """Programmatic entry point for running tests.

    :param tests: Paths to test case files/directories to be executed similarly
        as when running the ``robot`` command on the command line.
    :param options: Options to configure and control execution. Accepted
        options are mostly same as normal command line options to the ``robot``
        command. Option names match command line option long names without
        hyphens so that, for example, ``--name`` becomes ``name``.

    Most options that can be given from the command line work. An exception
    is that options ``--pythonpath``, ``--argumentfile``, ``--escape`` ,
    ``--help`` and ``--version`` are not supported.

    Options that can be given on the command line multiple times can be
    passed as lists. For example, ``include=['tag1', 'tag2']`` is equivalent
    to ``--include tag1 --include tag2``. If such options are used only once,
    they can be given also as a single string like ``include='tag'``.

    Options that accept no value can be given as Booleans. For example,
    ``dryrun=True`` is same as using the ``--dryrun`` option.

    Options that accept string ``NONE`` as a special value can also be used
    with Python ``None``. For example, using ``log=None`` is equivalent to
    ``--log NONE``.

    ``listener``, ``prerunmodifier`` and ``prerebotmodifier`` options allow
    passing values as Python objects in addition to module names these command
    line options support. For example, ``run('tests', listener=MyListener())``.

    To capture the standard output and error streams, pass an open file or
    file-like object as special keyword arguments ``stdout`` and ``stderr``,
    respectively.

    A return code is returned similarly as when running on the command line.
    Zero means that tests were executed and no critical test failed, values up
    to 250 denote the number of failed critical tests, and values between
    251-255 are for other statuses documented in the Robot Framework User Guide.

    Example::

        from robot import run

        run('path/to/tests.robot')
        run('tests.robot', include=['tag1', 'tag2'], splitlog=True)
        with open('stdout.txt', 'w') as stdout:
            run('t1.robot', 't2.robot', name='Example', log=None, stdout=stdout)

    Equivalent command line usage::

        robot path/to/tests.robot
        robot --include tag1 --include tag2 --splitlog tests.robot
        robot --name Example --log NONE t1.robot t2.robot > stdout.txt
    """
    return RobotFramework().execute(*tests, **options)
```

run与run_cli的区别：

>Most options that can be given from the command line work. An exception
>    is that options ``--pythonpath``, ``--argumentfile``, ``--escape`` ,
>    ``--help`` and ``--version`` are not supported.

原因：参见utils.application.py
```python
    def execute_cli(self, cli_arguments, exit=True):
        with self._logger:
            self._logger.info('%s %s' % (self._ap.name, self._ap.version))
            options, arguments = self._parse_arguments(cli_arguments)
            rc = self._execute(arguments, options)
        if exit:
            self._exit(rc)
        return rc

    def _parse_arguments(self, cli_args):
        try:
            options, arguments = self.parse_arguments(cli_args)
        except Information as msg:
            self._report_info(msg.message)
        except DataError as err:
            self._report_error(err.message, help=True, exit=True)
        else:
            self._logger.info('Arguments: %s' % ','.join(arguments))
            return options, arguments

    def parse_arguments(self, cli_args):
        """Public interface for parsing command line arguments.

        :param    cli_args: Command line arguments as a list
        :returns: options (dict), arguments (list)
        :raises:  :class:`~robot.errors.Information` when --help or --version used
        :raises:  :class:`~robot.errors.DataError` when parsing fails
        """
        return self._ap.parse_args(cli_args)

    def execute(self, *arguments, **options):
        with self._logger:
            self._logger.info('%s %s' % (self._ap.name, self._ap.version))
            return self._execute(list(arguments), options)
```

区别就是run_cli会执行_parse_arguments获取和进一步处理参数及选项，run不支持的选项就是在这里被处理的，具体如何，可参见章节：robot处理选项与参数


# 参考文档

- [fnmatch](https://docs.python.org/2/library/fnmatch.html)
- [python -m](https://docs.python.org/2/using/cmdline.html#cmdoption-m)
- https://github.com/robotframework/robotframework/issues/1137: 防止在windows系统上使用multiprocessing时出错，请参考以下内容
    -. http://rhodesmill.org/brandon/2010/python-multiprocessing-linux-windows/
    -. https://stackoverflow.com/questions/14175348/why-does-pythons-multiprocessing-module-import-main-when-starting-a-new-pro
    -. https://docs.python.org/2/library/multiprocessing.html#windows
    -. https://pymotw.com/2/multiprocessing/basics.html

