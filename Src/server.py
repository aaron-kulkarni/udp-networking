import socket
import struct
import sys
import pyuv

BUFFER_SIZE = 2048

def main():

    if len(sys.argv) != 2:
        print("Incorrect number of arguments. Please enter 1 arguments for the port number.")
        return
    
    PORT = int(sys.argv[1])
    HOST = b'0.0.0.0'
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((HOST, PORT))
    # sessions = {}
    # sessionId = 0
    # if remote_addr not in sessions: #starting a session with a new remote addr
    #         sessions[remote_addr] = sessionId
    #         sessionId += 1

    
    loop = pyuv.Loop.default_loop()
    serverSocket = pyuv.UPD(loop) # UDP socket read
    #serverTTY = pyuv.TTY(loop, sys.stdin.fileno(), True) # keyboard read
    serverSocket.bind(HOST, PORT)
    serverSocket.start_recv(handle_recv_packet) # start receiving packet from the socket
    #serverTTY.start_read(handle_keyboard_input) # start listening to keyboard
    loop.run()

    
    while True:
        packet, remote_addr = s.recvfrom(BUFFER_SIZE)
        
        header = unpack(packet[:12])
        if checkHeader(header) == False:
            continue
        
        if int(header[2]) == 0: #HELLO message
            message = pack(0, 1, 1)
            s.sendto(message, remote_addr)
        elif int(header[2]) == 1: #DATA message
            data = packet[12:].decode('utf-8')
            print(data, end='')
            message = pack(2, 1, 1)
            s.sendto(message, remote_addr)
        # elif int(header[2]) == 2: #ALIVE message
        #     print("alive")
        elif int(header[2]) == 3: #GOODBYE message
            message = pack(3, 1, 1)
            s.sendto(message, remote_addr)
            serverSocket.stop_recv()
            loop.stop()
            return
            

def checkHeader(header):
    if header[0] != 0xC356 or header[1] != 1:
        return False
    return True   

def pack(command, seq, sessionID):
    return struct.pack('!HBBII', 0xC356, 1, command, seq, sessionID)

def unpack(data):
    return struct.unpack('!HBBII', data)

def handle_recv_packet()

if __name__ == "__main__":
    main()