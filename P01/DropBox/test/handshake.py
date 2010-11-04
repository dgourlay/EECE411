import socket

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("", 1234))
server_socket.listen(1)


	
cs, address = server_socket.accept()
#cs.send("hello")
	
#def client():
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(("localhost",1234))
data = client_socket.recv(4096)
if (data != "hello"):
	print "system is busy"
else:
	print "connected fine"
		
	
		
