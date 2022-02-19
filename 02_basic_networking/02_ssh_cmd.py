import paramiko


def ssh_command(ip, port, user, pwd, cmd):
    # Opens an SSH client with paramiko
    client = paramiko.SSHClient()

    # Adds the hostname and new host key to the local `.HostKeys` object,
    # and saves it
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Connects to the SSH server
    client.connect(hostname=ip, port=port, username=user, password=pwd)

    # Executes the command and gets the output and error standard streams
    _, stdout, stderr = client.exec_command(cmd)

    # Prints the output
    output = stdout.readlines() + stderr.readlines()
    if output:
        print('--- Output ---')
        for line in output:
            print(line.strip())


if __name__ == '__main__':
    import getpass
    user = input('Username: ')

    # Gets the password without showing the characters
    password = getpass.getpass()

    ip = input('Enter server IP: ') or '192.168.1.203'
    port = input('Enter port or <CR>: ') or 2222
    cmd = input('Enter command or <CR>: ') or 'id'
    ssh_command(ip, port, user, password, cmd)
