import os
import socket
import struct
import sys
import threading
from queue import Queue
import random
import time

BUFFER_SIZE = 2048
HELLO = 0
DATA = 1
ALIVE = 2
GOODBYE = 3
INTERVAL = 2.0

def main():
    runClient(sys.argv, sys.stdin)

def runClient(input, scanner):
    if len(input) != 3:
        print("Incorrect number of arguments. Please enter 2 arguments. First should be host second should be the port number.")
        return
    
    HOST = input[1]
    PORT = int(input[2])

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    #used for intercommunication between socketThread and keyboardThread. when one thread closes, it signals to the other to close as well.
    global keepGoing 
    keepGoing = True
    global seqNumber #sequence number for messages
    seqNumber = 0
    global sessionID
    sessionID = random.randint(0, 4294967295)
    global closingStarted
    closingStarted = False
    
    
    
    message = pack(HELLO, seqNumber, sessionID)
    s.sendto(message, (HOST, PORT)) #sends hello message
    

    #magic, version, command, seq, sessionID

    while True:
        timerThread = threading.Timer(INTERVAL, function=closing, args=(HOST, PORT, s))
        timerThread.start()
        packet = s.recvfrom(BUFFER_SIZE)[0] #wait for handshake hello message
        timerThread.cancel()
        header = unpack(packet[:12])
        if checkMagicAndVersion(header) ==  False: #ignore wrong magic and version packets
            continue
        if int(header[2]) == GOODBYE:
            s.close()
            return
        if checkSessionID(header) == False or int(header[2]) == DATA or int(header[2]) == ALIVE:
            closing(HOST, PORT, s)
        break

    global q
    q = Queue()

    socketThread = threading.Thread(target=handle_socket, args=(HOST, PORT, s))
    socketThread.start()

    keyboardThread = threading.Thread(target=handle_keyboard, args=(HOST, PORT, s, scanner))
    keyboardThread.start()
    
    socketThread.join()
    keyboardThread.join()


def handle_keyboard(HOST, PORT, s, scanner):
    global keepGoing

    while keepGoing:
        text = scanner.readline()
        # Terminates client if input is EOF or 'q'
        if (not text or (text == "q\n" and scanner.isatty())):
            q.put("q")
            keepGoing = False
            closing(HOST, PORT, s)
        q.put(text.rstrip())

    return


def handle_socket(HOST, PORT, s):
    global keepGoing
    global seqNumber


    while keepGoing:
        while q.empty(): #if there are no outgoing messages, listen for a goodbye from the server.
            try:
                packet = s.recvfrom(BUFFER_SIZE, socket.MSG_DONTWAIT)[0]
                header = unpack(packet[:12])
                if int(header[2]) == GOODBYE:
                    keepGoing = False
                    closeSocket(s)
            except BlockingIOError as e:
                time.sleep(0.1)
                pass
            
        #send message
        seqNumber += 1
        text = q.get()
        if text == "q":
            keepGoing = False
            message = pack(GOODBYE, seqNumber, sessionID)
            closing(HOST, PORT, s)
            return
        message = pack(DATA, seqNumber, sessionID)
        data_message = message + text.encode('utf-8')
        s.sendto(data_message, (HOST, PORT))

        while True:
            timerThread = threading.Timer(INTERVAL, function=closing, args=(HOST, PORT, s))
            timerThread.start()
            packet = s.recvfrom(BUFFER_SIZE)[0] #wait for handshake hello message
            timerThread.cancel()
            header = unpack(packet[:12])
            if checkMagicAndVersion(header) == False: #ignore wrong magic and version packets
                continue
            if int(header[2]) == GOODBYE:
                keepGoing = False
                closeSocket(s)
            if checkSessionID(header) == False or int(header[2]) == DATA or int(header[2] == HELLO):
                keepGoing = False
                closing(HOST, PORT, s)
            break
        
    return

def closing(HOST, PORT, s):
    global closingStarted

    if closingStarted == True: #closing has already been initiated before.
        return     

    closingStarted = True
    message = pack(GOODBYE, seqNumber, sessionID)
    s.sendto(message, (HOST, PORT))

    
    while True:
        timerThread = threading.Timer(INTERVAL, function=closeSocket, args=(s))
        timerThread.start()
        packet = s.recvfrom(BUFFER_SIZE)[0]
        timerThread.cancel()
        header = unpack(packet[:12])
        if header[2] == GOODBYE:
            closeSocket(s)
        else:
            continue
        
def closeSocket(s):
    s.close()
    os._exit(0)

def checkSessionID(header): #checks sessionID
    if int(header[4] == sessionID):
        return True
    return False    

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
