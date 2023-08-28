import socket
import os
import subprocess
import signal
import time

REQUEST_SERVER_UP = 1
REQUEST_SERVER_DOWN = 2

VERSION = '0.08'

def get_choice(prompt):
    return input(prompt)

def load_file():
    file = open('server.data', 'r')
    #0: port | 1: server path |2: batch file path
    data = []

    for each in file:
        data.append(each)

    port = int(data[0][0:len(data[0])-1])
    ip = data[1][0:len(data[1])-1]
    batch_file = data[2][0:len(data[2])-1]

    return [port,ip,batch_file]

def init_data_in_file():
    port = int(input("Enter Sever Port\n>>> "))
    path = input('\nEnter Path to .bat file\nEX: C:\\Users\\Desktop\\Minecraft Server\n>>> ')
    batch_file_name = input("\nEnter Bat file name\nEX: run.bat\n>>>")

    f = open("server.data","wt")

    f.write(str(port)+'\n')
    f.write(path+'\n')
    f.write(batch_file_name+'\n')

    f.close()

def run(client_prem):
    CAN_CLIENTS_SHUTDOWN = True
    IS_SERVER_UP = False

    if client_prem == 2:
        CAN_CLIENTS_SHUTDOWN = False

    port,path,batch_file = load_file()

    s = socket.socket()
    s.bind(('',port))

    s.listen(5)

    pro = None
    pro_pid = None

    while True:
        c,addr = s.accept()

        print('\n[Received Connection] ',addr)

        #receiving the request
        request = c.recv(1024)
        request = int.from_bytes(request,"big")

        print("Request Sent: "+str(request))

        result_message = b''

        if request == REQUEST_SERVER_UP and not IS_SERVER_UP:
            result_message = b'Sending Server Up'
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            pro = subprocess.Popen(['cmd', '/c', path + '\\' + batch_file], startupinfo=si)
            pro_pid = pro.pid
            IS_SERVER_UP = True

        elif request == REQUEST_SERVER_DOWN and CAN_CLIENTS_SHUTDOWN and IS_SERVER_UP:
            result_message = b'Requesting to shutdowns server'
            command = ['TASKKILL', '/F', '/T', '/PID', str(pro_pid)]
            subprocess.Popen(command)

            IS_SERVER_UP = False
        else:
            result_message = b'Request Rejected | Clients cannot shutdown or server is off | Or Server is already up'

        c.send(result_message)
        print('Result Message Sent')

        c.close()

def parse_preference_data():
    preferences = []
    preferences_file = open('preferences.txt', 'r')

    curr_line = 0
    for line in preferences_file.readlines():
        for i in range(len(line)-1,0,-1):
            if line[i]=='=':
                final = line[i+1:]
                if final[len(final)-1]=='\n':
                    final = final[:len(final)-1]
                preferences.append(final)
        curr_line+=1

    preferences_file.close()
    return preferences

def start():
    START_UP = 0
    CLIENT_SHUTDOWN = 1

    server_data_file = open('server.data','r')
    data = server_data_file.read()
    if data == '' or len(data) > 0 and data[0] == ' ':
        init_data_in_file()
        start()
    server_data_file.close()

    preferences = parse_preference_data()

    if preferences[START_UP]=='false':
        prompt = "[1] Start |[2] For Changing Sever Settings\n>>> "
        choice = int(input(prompt))

        if choice == 2:
            init_data_in_file()
            start()
        else:
            user_perm = int(get_choice('[1] Users can shutdown sever |[2] Users cannot shutdown sever\n>>> '))
            run(user_perm)
    else:
        user_perm = preferences[CLIENT_SHUTDOWN]
        if user_perm.lower() == 'true':
            run(1)
        else:
            run(2)


print("CURRENT VERSION: "+VERSION)
start()
