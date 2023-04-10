import socket
import struct
import sys
import pyuv


class Session:
    def __init__(self, seq, addr, timer):
        self.seq = seq
        self.addr = addr
        self.timer = timer

BUFFER_SIZE = 2048

loop = pyuv.Loop.default_loop()
s = pyuv.UDP(loop)
k = pyuv.TTY(loop, sys.stdin.fileno(), True)
HELLO = 0
DATA = 1
ALIVE = 2
GOODBYE = 3
INTERVAL = 2.0
sessionDict = {}

def main():

    if len(sys.argv) != 2:
        print("Incorrect number of arguments. Please enter 1 arguments for the port number.")
        return
    
    PORT = int(sys.argv[1])
    HOST = '0.0.0.0'
    s.bind((HOST, PORT))
    s.start_recv(handle_recv_packet)
    k.start_read(handle_keyboard_input)
    loop.run()
    # timer.start()


def handle_recv_packet(handle, addr, flags, packet, error): #used for socket communication
    header = unpack(packet[:12])
    if checkMagicAndVersion(header) == False: 
        return
    sequence = int(header[3])
    sessionID = int(header[4])
    if sessionDict.get(sessionID) is None: #session does not already exist. create a new one.
        #first message must be a hello message
        if int(header[2]) == HELLO:
            message = pack(HELLO, sequence, sessionID)
            handle.send(addr, message)
            timer = pyuv.Timer(loop)
            newSession = Session(sequence, addr, timer)
            sessionDict[sessionID] = newSession
            timer.start(timeoutSession, 10, 0)
        else: #first message in a session is not a hello. discard packet.
            return
    else: #session already exists
        curSession = sessionDict[sessionID]
        curSession.timer.stop()
        curSession.timer.start(timeoutSession, 10, 0)
        if int(header[2]) != DATA or sequence < curSession.seq:
            endSession(handle, sequence, sessionID, addr)
            return
        if sequence == curSession.seq: #Duplicate packet. discard packet but keep session alive.
            message = pack(ALIVE, sequence, sessionID)
            handle.send(addr, message)
            print("Duplicate packet!")
            return
        if sequence > curSession.seq + 1: #Greater sequence # than expected
            packetsLost = sequence - (curSession.seq + 1)
            for i in range(packetsLost):
                print("Lost packet!")
        
        curSession.seq = sequence
        data = packet[12:].decode('utf-8')
        print(data)
        message = pack(ALIVE, sequence, sessionID)
        handle.send(addr, message)
    
    return

def handle_keyboard_input(tty_handle, data, error):
    # Terminates client if input is EOF or 'q'
    if (not data or (data == b'q\n')):
        endServer()
        return
    
def endServer():
    for sessionID in list(sessionDict):
        sessionData = sessionDict.get(sessionID)
        endSession(s, sessionID, sessionData)
    s.stop_recv()
    k.stop_read()
    loop.stop()
    pyuv.Async(loop, empty_event_func)
    return

def timeoutSession(timer):
    for sessionID in sessionDict:
        session = sessionDict.get(sessionID)
        if session.timer == timer:
            endSession(s, sessionID, session)
            return
    print("Error. Tried to timeout session that is not in session dictionary.")

def endSession(handle, sessionID, session):
    message = pack(GOODBYE, session.seq, sessionID)
    handle.send(session.addr, message)
    session.timer.stop()
    sessionDict.pop(sessionID)
    return

def empty_event_func(async_handle): #empty_event_func is needed for pyuv. check documentation for reason.
    pass            

def checkMagicAndVersion(header): #checks magic number and version
    if int(header[0]) == 0xC356 and int(header[1]) == 1:
        return True
    return False    

def pack(command, seq, sessionID):
    return struct.pack('!HBBII', 0xC356, 1, command, seq, sessionID)

def unpack(data):
    return struct.unpack('!HBBII', data)


if __name__ == "__main__":
    main()