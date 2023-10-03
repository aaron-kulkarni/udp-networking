Project Goals
This project asks you to implement what might be described as a client-server data transfer application. We don't actually need dozens of implementations of data transfer, though, so the real point is the experience of implementing communication protocols.

The operation of communication protocols always involves asynchrony, which can be an implementation challenge. This project gives you experience implementing protocols using two approaches:

Thread-based (Blocking IO). Here we use threads to provide concurrency. By carefully choosing when threads are created and what they do, we can often find a simple solution to asynchrony. The distinguishing feature is that each blocked thread is waiting for only a single thing (e.g., keyboard input, or network input). You probably have had some exposure to threads in previous courses, so this approach should be at least somewhat familiar. Additionally, threads have a long history, and so mature support for them exists in most languages/systems.  

Non-blocking IO or event-loop based. The basic idea of these alternative approaches is for a single thread to wait on more than one "event source" at a time. For example, a single thread might wait for a packet arrival from multiple ports. Also it could wait for either a keyboard input or a packet to arrive. You will be using Python3 pyuv packageLinks to an external site., which is an event loop package. 
To achieve the goals of this project, you must work in pairs. That is, there are two different developers involved. PUDP has distinct client and server sides, so there are two distinct pieces of code involved in a full solution. The work will be divided as follows but both parters are responsible for all parts of the code (both src and test code):

 	Src Code	Test Code
Thread-based Client	Partner A	Partner B
Event loop Server	Partner B	Partner A
 

P2 Messages
This project PUDP defines what messages are sent between the client and server, and how they are encoded. PUDP transfers lines of input from the client's stdin to the server, which then prints them on its stdout .

Protocol Headers
PUDP is much more realistic than the protocols shown in sections and class, in large part because it defines a message as a header plus data (rather than just data). Without a header, you can have only one kind of message, and so can't do simple things you almost certainly need to do, even if you don't realize it yet. (One example is returning an error indication, for instance, even though we don't do that in this project.) Protocols you design should always include headers in message encodings.

Protocol Sessions
PUDP supports the notion of a session. A session is a related sequence of messages coming from a single client. Sessions allow the server to maintain state about each individual client. For instance, the server could, in theory, print out how many messages it has received in each session, for instance, or it could maintain a shopping cart for each session. (We don't actually implement either of those.)

Unlike TCP (which has "connections"), UDP doesn't have any notion related to sessions, so we build them as part of our protocol.

Protocol Messages and Format
PUDP defines four message types: HELLO , DATA , ALIVE , and GOODBYE . All message encodings include a header. The header is filled with binary values. The header bytes are the initial bytes of the message. They look like this, with fields sent in order from left to right:

magic	version	command	sequence_number	session_id
16 bits	8 bits	8 bits	32 bits	32 bits
 

magic is the value 0xC356 (i.e., decimal 50006), when taken as an unsigned 16-bit integer in network byte order (big endian). An arriving packet whose first two bytes do not match the magic number is silently discarded.
version is a one byte protocol version, and is the value 1.
command is a one byte value: 0 for HELLO , 1 for DATA , 2 for ALIVE , and 3 for GOODBYE .
sequence_number s in messages sent by the client are 0 for the first packet of the session, 1 for the next packet, 2 for the one after that, etc. Server sequence numbers simply count up each time the server sends something (in any session). Sequence numbers are four bytes.
session_id is an arbitrary 32-bit integer, in network byte order. The client chooses its value at random when it starts. Both the client and the server repeat the session id in all messages that are part of that session.
 

Multi-byte values are sent big-endian (which is often called "network byte order").

In DATA messages, the header is followed by arbitrary data; the other messages do not have any data. The receiver can determine the amount of data that was sent by subtracting the known header length from the length of the UDP packet, something the language/package you use will provide some way of obtaining.

Only one PUDP message may be sent in a single UDP packet, and all PUDP messages must fit in a single UDP packet. PUDP itself does not define either maximum or minimum DATA payload sizes. It expects that all reasonable implementations will accept data payloads that are considerably larger than a typical single line of typed input.
