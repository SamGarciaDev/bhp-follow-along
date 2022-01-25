import sys
import socket
import threading

# String containing each ASCII char if it exists, or '.' otherwise
HEX_FILTER = ''.join([(len(repr(chr(i))) == 3) and chr(i) or '.' for i in range(256)])

# Dumps the hex data both in bytes, as well as in readable clear text
def hex_dump(src, length = 16, show = True):
    if isinstance(src, bytes):
        # Convert bytes to string, using UTF-8
        src = src.decode()

    results = list()

    for i in range(0, len(src), length):
        # Get a chunk of the src
        word = src[i:i+length]
        # Maps the output using the HEX_FILTER
        printable = word.translate(HEX_FILTER)
        # Gets each character of the word in hexadecimal
        hexa = ' '.join([f'{ord(c):02X}' for c in word])
        # Prints the data, uses :< to keep alignment, so that if there are less
        # than hex_width chars, it fills the rest with spaces
        hex_width = length * 3
        results.append(f'{i:04x}  {hexa:<{hex_width}}  {printable}')

    if show:
        for line in results:
            print(line)

    else:
        return results

# Receives data from an active socket until there is none left
def receive_from(connection):
    buffer = b""
    connection.settimeout(5)

    try:
        while True:
            data = connection.recv(4096)

            if not data:
                break

            buffer += data
    except Exception as e:
        pass

    return buffer

# Modifies the request before sending it to the remote socket
def request_handler(buffer):
    return buffer

# Modifies the response before sending it to the client socket
def response_handler(buffer):
    return buffer

# Creates communication between the two sockets
def proxy_handler(client_socket, remote_host, remote_port, receive_first):
    # Configures the remote socket
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.bind((remote_host, remote_port))

    # If it's supposed to receive data first, read it
    if receive_first:
        remote_buffer = receive_from(remote_socket)
        hex_dump(remote_buffer)

    # Handle the response
    remote_buffer = response_handler(remote_buffer)

    # If there's data in the response, send it to the client_socket first
    if (len(remote_buffer)):
        print("[<==] Sending %d bytes to localhost." % len(remote_buffer))
        client_socket.send(remote_buffer)

    # Loop until there's no data from either socket
    while True:
        # Receive data from the client_socket
        local_buffer = receive_from(client_socket)

        # If there's data, print the dump, handle it and send it to the remote_socket
        if len(local_buffer):
            print("[==>] Received %d bytes from localhost." % len(local_buffer))
            hexdump(local_buffer)
            local_buffer = request_handler(local_buffer)
            remote_socket.send(local_buffer)
            print("[==>] Sent to remote.")

        # Receive data from the remote socket
        remote_buffer = receive_from(remote_socket)

        # Same process as above
        if len(remote_buffer):
            print("[<==] Received %d bytes from remote." % len(remote_buffer))
            hexdump(remote_buffer)
            remote_buffer = response_handler(remote_buffer)
            client_socket.send(remote_buffer)
            print("[<==] Sent to localhost.")

        # If there's no more data coming through, close the connections and break
        if not len(local_buffer) or not len(remote_buffer):
            client_socket.close()
            remote_socket.close()
            print("[*] No more data. Closing connections.")
            break

# Loop that runs the main server
def server_loop(local_host, local_port, remote_host, remote_port, receive_first):
    # Configure the server socket
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Try to bind to the local host and ports
        server.bind((local_host, local_port))
    except Exception as e:
        print('Problem on bind: %r' % e)
        print("[!!] Failed to listen on %s:%d" % (local_host, local_port))
        print("[!!] Check for other listening sockets or correct permissions.")
        sys.exit(0)
        
    # Listen for a maximum of 5 connections
    server.listen(5)
    print("[*] Listening on %s:%d" % (local_host, local_port))

    while True:
        #Wait for incoming connections
        client_socket, addr = server.accept()
        print("> Received incoming connection from %s:%d" % (addr[0], addr[1]))

        # Start a thread to talk to the remote host
        proxy_thread = threading.Thread(
            target = proxy_handler,
            args = (client_socket, remote_host, remote_port, receive_first)
        )

        proxy_thread.start()

if __name__ == '__main__':
    if len(sys.argv[1:]) != 5:
        print("Usage: ./proxy.py [localhost] [localport] [remotehost] [remoteport] [receive_first]")
        print("Example: ./proxy.py 127.0.0.1 9000 10.12.132.1 9000 True")
        sys.exit(0)

    local_host = sys.argv[1]
    local_port = int(sys.argv[2])
    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])
    receive_first = sys.argv[5]

    if "True" in receive_first:
        receive_first = True
    else:
        receive_first = False

    server_loop(local_host, local_port, remote_host, remote_port, receive_first)