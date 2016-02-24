# 引用的资源

## 问题

**[When does socket.recv(recv_size) return?](http://stackoverflow.com/questions/7174927/when-does-socket-recvrecv-size-return)**

> From test, I concluded that in following three cases the socket.recv(recv_size) will return.

    After the connection was closed. For example, the client side called socket
    .close() or any socket error occurred, it would return empty string.

    Some data come, the size of data is more than recv_size.
    Some data come, the size of data is less than recv_size and no more data
     come after a short time (I found 0.1s would work).

> More details about #3:

#server.py
```python
while True:
    data = sock.recv(10)
    print data, 'EOF'
```
#client1.py
```python
sock.sendall("12345")
sock.sendall("a" * 50)
```
#client2.py
```python
sock.sendall("12345")
time.sleep(0.1)
sock.sendall("a" * 50)
```
> When I run client1.py, the server.py echos:
```
12345aaaaa EOF
aaaaaaaaaa EOF
aaaaaaaaaa EOF
aaaaaaaaaa EOF
aaaaaaaaaa EOF
aaaaa EOF
```
> When I run client2.py, the server.py echos:
```
12345 EOF
aaaaaaaaaa EOF
aaaaaaaaaa EOF
aaaaaaaaaa EOF
aaaaaaaaaa EOF
aaaaaaaaaa EOF
```
 > Are my conclusions correct? Where can I see the official description about #3?

## 相关回答
### **[Linux Programmer's Manual    RECV(2)](http://man7.org/linux/man-pages/man2/recv.2.html)**

> If no messages are available at the socket, the receive calls wait for a message to arrive, unless the socket is nonblocking (see fcntl(2)), in which case the value -1 is returned and the external variable errno is set to EAGAIN or EWOULDBLOCK. **The receive calls normally return any data available, up to the requested amount, rather than waiting for receipt of the full amount requested.**



### **[How large should my recv buffer be when calling recv in the socket library](http://stackoverflow.com/questions/2862071/how-large-should-my-recv-buffer-be-when-calling-recv-in-the-socket-library#)**


 The answers to these questions vary depending on whether you are using a stream socket (SOCK_STREAM) or a datagram socket (SOCK_DGRAM) - within TCP/IP, the former corresponds to TCP and the latter to UDP.

 How do you know how big to make the buffer passed to recv()?

    SOCK_STREAM: It doesn't really matter - just pick a size (3000 is fine). Larger buffers will be more efficient if you're transferring large amounts of data.

    SOCK_DGRAM: Use a buffer large enough to hold the biggest packet that your application-level protocol ever sends. If you're using UDP, then in general your application-level protocol shouldn't be sending packets larger than about 1400 bytes, because they'll certainly need to be fragmented and reassembled.

 What happens if recv gets a packet larger than the buffer?

    SOCK_STREAM: The question doesn't really make sense as put, because stream sockets don't have a concept of packets - they're just a continuous stream of bytes. If there's more bytes available to read than your buffer has room for, then they'll be queued by the OS and available for your next call to recv.

    SOCK_DGRAM: The excess bytes are discarded.

 How can I know if I have received the entire message?

    SOCK_STREAM: You need to build some way of determining the end-of-message into your application-level protocol. Commonly this is either a length prefix (starting each message with the length of the message) or an end-of-message delimiter (which might just be a newline in a text-based protocol, for example). A third, lesser-used, option is to mandate a fixed size for each message. Combinations of these options are also possible - for example, a fixed-size header that includes a length value.

    SOCK_DGRAM: An single recv call always returns a single datagram.

 Is there a way I can make a buffer not have a fixed amount of space, so that I can keep adding to it without fear of running out of space?

 No. However, you can try to resize the buffer using realloc() (if it was originally allocated with malloc() or calloc(), that is).

### **[Socket Programming HOWTO](https://docs.python.org/2/howto/sockets.html)**

# 背景

最近在搞robotframework的测试框架，对于RIDE实现的监听器比较感兴趣，就大概看了一些源码。

- RIDE先在localhost启动一个服务器a
- 当robot运行并加载监听器时，会建立到服务器的socket连接，而且监听器本身也会启动一个服务器b
- robot运行到相关的监控点时，监听器获取脚本运行信息，并通过这个socket连接向RIDE的服务器a发送，由此RIDE来记录相关的脚本实时运行状态
- 当通过RIDE界面来操作`pause`,`continue`,`stop`等动作时，RIDE服务器a会建立到监听器服务器b的连接，并发送动作，监听器通过event来控制脚本`pause`,`continue`,`stop`等

上述过程涉及到了socket.recv, 就顺便学习了一些recv的一些特点
