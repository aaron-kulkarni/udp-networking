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

    while True:
        packet, remote_addr = s.recvfrom(BUFFER_SIZE)
        print(packet)
        
        header = unpack(packet[:12])
        if checkHeader(header) == False:
            continue

        sequence = header[3]
        session = header[4]
        
        if int(header[2]) == 0: #HELLO message
            message = pack(0, sequence, session)
            s.sendto(message, remote_addr)
        elif int(header[2]) == 1: #DATA message
            data = packet[12:].decode('utf-8')
            print(data, end='')
            message = pack(2, sequence, session)
            s.sendto(message, remote_addr)
        # elif int(header[2]) == 2: #ALIVE message
        #     print("alive")
        elif int(header[2]) == 3: #GOODBYE message
            message = pack(3, sequence, session)
            s.sendto(message, remote_addr)
            return
            

def checkHeader(header):
    if header[0] != 0xC356 or header[1] != 1:
        return False
    return True   

def pack(command, seq, sessionID):
    return struct.pack('!HBBII', 0xC356, 1, command, seq, sessionID)

def unpack(data):
    return struct.unpack('!HBBII', data)

if __name__ == "__main__":
    main()