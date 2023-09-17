import socket

VERSION = '0.08'

def get_choice(prompt):
    return input(prompt)

def load_data_from_file():
    file = open('client.data', 'r')
    # 0: port | 1: server path |2: batch file path
    data = []

    for each in file:
        data.append(each)

    port = int(data[0][0:len(data[0]) - 1])
    ip = data[1][0:len(data[1]) - 1]
    name = data[2][0:len(data[2]) - 1]

    return [port,ip,name]
def init_data_in_file():
    port = int(input("Enter Sever Port\n>>> "))
    ip = input('Enter Server ip\n>>> ')
    name = input('Enter username (10 characters max)\n>>> ')

    #error checkinag
    if len(name) > 10:
        name = name[0:10]

    f = open("client.data","wt")

    f.write(str(port)+'\n')
    f.write(ip+'\n')
    f.write(name+'\n')

    f.close()
def run():
    port,ip,name = load_data_from_file()
    request = int(input("[1] Sever Up | [2]  Server Down | [3] Server Status\n>>> "))

    s = socket.socket()
    s.connect((ip,port))

    s.send(request.to_bytes(2,'big'))

    result = s.recv(2048)
    print(result)

    input(">>> ")

    s.close()

    if int(input('[1] continue |[2] quit\n>>> ')) == 1:
        start()

def start():
    #checking to make sure data is setup
    f = open('client.data','r')
    data = f.read()
    if data == '' or len(data) > 0 and data[0] == ' ':
        init_data_in_file()
    f.close()

    prompt = "[1] connecting |[2] For Changing Client Settings\n>>> "
    choice = int(input(prompt))

    if choice == 2:
        init_data_in_file()
        start()
    else:
        run()

print("CURRENT VERSION: "+VERSION)
start()