#!/user/bin/env python
import socket, sys

def post():
    bool = raw_input('Test Post?')

    if bool == 'no' or bool == 'n':
        return -1
    else:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        hostName = 'inferno'
        port       = 8766

        ## initiate TCP connection
        s.connect( (hostName, port) )
        print 'connected to inferno at port 8766'

        s.send("POST /posting HTTP/1.0\r\n\r\n")

        #directly from sockets page
        response = ""
        while True:
            buf = s.recv(1000) # buffer size of 1000
            if not buf:
                break
            response += buf

        s.close()

        print 'reponse: ' + response



def get():   
    bool = raw_input('Test Get?')

    if bool == 'no' or bool == 'n':
	return -1
    else:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
        hostName = 'inferno'
        port       = 8766

        ## initiate TCP connection
        s.connect( (hostName, port) )
        print 'connected to inferno at port 8766'

        s.send("GET / HTTP/1.0\r\n\r\n")

        response = ""
        while True:
            buf = s.recv(1000) # buffer size of 1000
            if not buf:
                break
            response += buf

        s.close()

        print 'reponse: ' + response


def form():

    bool = raw_input('Test Form?')

    if bool == 'no' or bool == 'n':
        return -1
    else:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

        hostName = 'inferno'
        port       = 8766

        ## initiate TCP connection
        s.connect( (hostName, port) )
        print 'connected to inferno at port 8766'

        s.send("GET /recipes_recv?name=recAddTest&ingName=testAddIng&ingAmount=123+oz HTTP/1.0\r\n\r\n")

        response = ""
        while True:
            buf = s.recv(1000) # buffer size of 1000
            if not buf:
                break
            response += buf

        s.close()

        print 'reponse: ' + response


def image():

    bool = raw_input('Test Image?')

    if bool == 'no' or bool == 'n':
        return -1
    else:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        hostName = 'inferno'
        port       = 8766

        ## initiate TCP connection
        s.connect( (hostName, port) )
        print 'connected to inferno at port 8766'

        s.send("GET /helmet HTTP/1.0\r\n\r\n")

        response = ""
        while True:
            buf = s.recv(1000) # buffer size of 1000
            if not buf:
                break
            response += buf

        s.close()

        print 'reponse: ' + response

if __name__ == '__main__':
    post()
    get()
    form()
    image()
