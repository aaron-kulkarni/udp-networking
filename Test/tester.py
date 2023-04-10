import sys
sys.path.append('../Src/')
sys.path.append('../Src/')


from server import runServer, endServer, output
from client import runClient


client_args = ['client.py', 'localhost', '1234']
def main():
    runServer(['server.py', '1234'])
    runTest(test1, ['Session created', 'one', 'two', 'three', 'GOODBYE from client.', 'Session closed'])
    endServer()

def runTest(test, expectedOutput):
    test()
    print(output)
    # assert output == expectedOutput
    
def test1():
    runClient(parse_file('test1.txt'))
    
    
def parse_file(file):
    with open(file) as f:
        return f.readlines()
    
if __name__ == "__main__":
    main()