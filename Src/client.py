import socket
import struct
import sys
import threading

BUFFER_SIZE = 2048

def main():

    if len(sys.argv) != 3:
        print("Incorrect number of arguments. Please enter 2 arguments. First should be host second should be the port number.")
        return
    
    HOST = sys.argv[1]
    PORT = int(sys.argv[2])

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    message = pack(0, 1, 1)
    s.sendto(message, (HOST, PORT)) #sends hello message
    
    packet, remote_addr = s.recvfrom(BUFFER_SIZE) #wait for handshake hello message
    
    header = unpack(packet[:12])
    if checkHeader(header) == False:
        return

    if int(header[2]) == 0: #HELLO message
        while True:
            # worker_thread = threading.Thread(target=session, args=(HOST, PORT, s))
            # worker_thread.start()
            text = sys.stdin.readline()
            # Terminates server if input is EOF or 'q'
            if (not text or (text == "q\n" and sys.stdin.isatty())):
                break
            message = pack(1, 1, 1)
            data_message = message + text.encode('utf-8')
            s.sendto(data_message, (HOST, PORT))
            packet, remote_addr = s.recvfrom(BUFFER_SIZE)
            header = unpack(packet[:12])
            if checkHeader(header) == False:
                break
            if int(header[2]) != 2: #if client receives hello, data, or goodbye
                break
        message = pack(3, 1, 1) #goodbye message
        s.sendto(message, (HOST, PORT))
        return
        
        

def session(HOST, PORT, s):

    message = pack(0, 1, 1)
    s.sendto(message, (HOST, PORT)) #sends hello message
    
    packet, remote_addr = s.recvfrom(BUFFER_SIZE) #wait for handshake hello message
    
    header = unpack(packet[:12])
    if checkHeader(header) == False:
        return
        
    if int(header[2]) == 0: #HELLO message
        while True:
            text = sys.stdin.readline()
            # Terminates server if input is EOF or 'q'
            if (not text or (text == "q\n" and sys.stdin.isatty())):
                break
            message = pack(1, 1, 1)
            data_message = message + text.encode('utf-8')
            s.sendto(data_message, (HOST, PORT))
            packet, remote_addr = s.recvfrom(BUFFER_SIZE)
            header = unpack(packet[:12])
            if checkHeader(header) == False:
                break
            if int(header[2]) != 2: #if client receives hello, data, or goodbye
                break
        message = pack(3, 1, 1) #goodbye message
        s.sendto(message, (HOST, PORT))
        return     


def checkHeader(header):
    if int(header[0]) == 0xC356 and int(header[1]) == 1:
        return True
    return False       

def pack(command, seq, sessionID):
    return struct.pack('!HBBII', 0xC356, 1, command, seq, sessionID)

def unpack(data):
    return struct.unpack('!HBBII', data)

if __name__ == "__main__":
    main()