import socket
import struct
import sys
import threading
from queue import Queue
import random

BUFFER_SIZE = 2048
HELLO = 0
DATA = 1
ALIVE = 2
GOODBYE = 3
INTERVAL = 2.0

def main():

    if len(sys.argv) != 3:
        print("Incorrect number of arguments. Please enter 2 arguments. First should be host second should be the port number.")
        return
    
    HOST = sys.argv[1]
    PORT = int(sys.argv[2])

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


    global keepGoing #used for intercommunication between socketThread and keyboardThread. when one thread closes, it signals to the other to close as well.
    keepGoing = True
    global seqNumber #sequence number for messages
    seqNumber = 0
    global sessionID
    sessionID = random.randint(0, 4294967295)
    
    
    
    message = pack(HELLO, seqNumber, sessionID)
    s.sendto(message, (HOST, PORT)) #sends hello message
    

    #magic, version, command, seq, sessionID

    while True:
        timerThread = threading.Timer(INTERVAL, function=closing, args=(HOST, PORT, s))
        timerThread.start()
        packet = s.recvfrom(BUFFER_SIZE)[0] #wait for handshake hello message
        timerThread.cancel()
        header = unpack(packet[:12])
        if checkMagicAndVersion(header) == False: #ignore wrong magic and version packets
            continue
        if header[2] == GOODBYE:
            s.close()
            return
        print(0)
        if checkSessionID(header) == False or header[2] == DATA or header[2] == ALIVE:
            closing(HOST, PORT, s)
            print(1)
        break

    global q
    q = Queue()

    print(2)

    socketThread = threading.Thread(target=handle_socket, args=(HOST, PORT, s))
    socketThread.start()

    keyboardThread = threading.Thread(target=handle_keyboard, args=(HOST, PORT, s))
    keyboardThread.start()
    
    socketThread.join()
    keyboardThread.join()


def handle_keyboard(HOST, PORT, s):
    global keepGoing
    while keepGoing:
        text = sys.stdin.readline()
        # Terminates client if input is EOF or 'q'
        if (not text or (text == "q\n" and sys.stdin.isatty())):
            q.put("q")
            keepGoing = False
            closing(HOST, PORT, s)
        q.put(text)

    return


def handle_socket(HOST, PORT, s):
    global keepGoing
    global seqNumber


    while keepGoing:
        #send message
        seqNumber += 1
        text = q.get()
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
            if header[2] == GOODBYE:
                keepGoing = False
                closeSocket(s)
            if checkSessionID or header[2] == DATA or header[2] == HELLO:
                keepGoing = False
                closing(HOST, PORT, s)
            break
        
    return

def closing(HOST, PORT, s):
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
    exit(0)

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

# def session(HOST, PORT, s, q):

#     message = pack(0, 1, 1)
#     s.sendto(message, (HOST, PORT)) #sends hello message
    
#     packet, remote_addr = s.recvfrom(BUFFER_SIZE) #wait for handshake hello message
    
#     header = unpack(packet[:12])
#     if checkHeader(header) == False:
#         return
        
#     if int(header[2]) == 0: #HELLO message
#         while True:
#             text = sys.stdin.readline()
#             # Terminates server if input is EOF or 'q'
#             if (not text or (text == "q\n" and sys.stdin.isatty())):
#                 break
#             message = pack(1, 1, 1)
#             data_message = message + text.encode('utf-8')
#             s.sendto(data_message, (HOST, PORT))
#             packet, remote_addr = s.recvfrom(BUFFER_SIZE)
#             header = unpack(packet[:12])
#             if checkHeader(header) == False:
#                 break
#             if int(header[2]) != 2: #if client receives hello, data, or goodbye
#                 break
#         message = pack(3, 1, 1) #goodbye message
#         s.sendto(message, (HOST, PORT))
#         return     

    # s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # message = pack(0, 1, 1)
    # s.sendto(message, (HOST, PORT)) #sends hello message
    
    # packet, remote_addr = s.recvfrom(BUFFER_SIZE) #wait for handshake hello message
    
    # header = unpack(packet[:12])
    # if checkHeader(header) == False:
    #     return

    # if int(header[2]) == 0: #HELLO message
    #     while True:
    #         # worker_thread = threading.Thread(target=session, args=(HOST, PORT, s))
    #         # worker_thread.start()
    #         text = sys.stdin.readline()
    #         # Terminates server if input is EOF or 'q'
    #         if (not text or (text == "q\n" and sys.stdin.isatty())):
    #             break
    #         message = pack(1, 1, 1)
    #         data_message = message + text.encode('utf-8')
    #         s.sendto(data_message, (HOST, PORT))
    #         packet, remote_addr = s.recvfrom(BUFFER_SIZE)
    #         header = unpack(packet[:12])
    #         if checkHeader(header) == False:
    #             break
    #         if int(header[2]) != 2: #if client receives hello, data, or goodbye
    #             break
    #     message = pack(3, 1, 1) #goodbye message
    #     s.sendto(message, (HOST, PORT))
    #     return

    #def pack(command, seq, sessionID):
        #0 HELLO, 1 DATA, 2 ALIVE, 3 GOODBYE
        # message = pack(1, 1, 1)
        # data_message = message + text.encode('utf-8')