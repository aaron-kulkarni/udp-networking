import sys
import threading
sys.path.append('../Src/')


from server import runServer, endServer, output
from client import runClient


client_args = ['client.py', 'localhost', '12345']
def main():
    
    serverThread = threading.Thread(target=runServer, args=(['server.py', '12345'], ))
    serverThread.start()
    runTest(test1, ['Session created', 'one', 'two', 'three', 'GOODBYE from client.', 'Session closed'])
    runTest(test2, ['Session created', 'hello how are', 'you doing?', 'queue this process', 'GOODBYE from client.', 'Session closed'])
    runTest(test3, ['Session created', 
                    'Alexey Fyodorovitch Karamazov was the third son of Fyodor Pavlovitch', 
                    'Karamazov, a land owner well known in our district in his own day, and', 
                    'still remembered among us owing to his gloomy and tragic death, which',
                    'happened thirteen years ago, and which I shall describe in its proper',
                    'place.' 
                    'GOODBYE from client.', 
                    'Session closed'])
    endServer()

def runTest(test, expectedOutput):
    test()
    assert output == expectedOutput
    
def test1():
    file = open('test1.txt')
    runClient(client_args, file)
    
def test2():
    file = open('test2.txt')
    runClient(client_args, file) 
    
def test3():
    file = open('test3.txt')
    runClient(client_args, file) 

    
if __name__ == "__main__":
    main()