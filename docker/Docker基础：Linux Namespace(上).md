转载自[coolshell](http://coolshell.cn/),作者陈皓

### 简介

  Linux Namespace是Linux提供的一种内核级别环境隔离的方法。不知道你是否还记得很早以前的Unix有一个叫chroot的系统调用（通过修改根目录把用户jail到一个特定目录下），chroot提供了一种简单的隔离模式：chroot内部的文件系统无法访问外部的内容。Linux Namespace在此基础上，提供了对UTS、IPC、mount、PID、network、User等的隔离机制。

  举个例子，我们都知道，Linux下的超级父亲进程的PID是1，所以，同chroot一样，如果我们可以把用户的进程空间jail到某个进程分支下，并像chroot那样让其下面的进程 看到的那个超级父进程的PID为1，于是就可以达到资源隔离的效果了（不同的PID namespace中的进程无法看到彼此）

  **Linux Namespace 有如下种类**，官方文档在这里[Namespace in Operation](http://lwn.net/Articles/531114/)
  
  
  分类 | 系统调用参数 | 相关内核版本
  ---- | -----------  | -----------
  Mount namespaces | CLONE_NEWNS  | Linux 2.4.19
  UTS namespaces	 | CLONE_NEWUTS	| Linux 2.6.19
  IPC namespaces	 | CLONE_NEWIPC	| Linux 2.6.19
  PID namespaces	 | CLONE_NEWPID	| Linux 2.6.24
  Network namespaces | CLONE_NEWNET | 始于Linux 2.6.24 完成于 Linux 2.6.29
  User namespaces  | CLONE_NEWUSER | 始于 Linux 2.6.23 完成于 Linux 3.8
  
  主要是**三个系统调用**

  * clone() - 实现线程的系统调用，用来创建一个新的进程，并可以通过设计上述参数达到隔离。
  * unshare() - 使某进程脱离某个namespace
  * setns() - 把某进程加入到某个namespace
  * unshare() 和 setns() 都比较简单，大家可以自己man，我这里不说了。

  下面还是让我们来看一些示例（以下的测试程序最好在Linux 内核为3.8以上的版本中运行，我用的是ubuntu 14.04）。
  
### clone()系统调用
