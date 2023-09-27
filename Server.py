import socket
import subprocess

REQUEST_SERVER_UP = 1
REQUEST_SERVER_DOWN = 2
REQUEST_SERVER_STATUS = 3

VERSION = '0.10'

class Server:
    is_server_up = False
    can_clients_shutdown = True
    pro = None
    pro_pid = None
    sock = socket.socket()

    bot_pro = None
    bot_pid = None

    def __init__(self, client_prem):
        print("Hello From server!")
        port, path, batch_file = load_file()
        self.port = port
        self.path = path
        self.batch_file = batch_file

        self.sock.bind(('',port))
        self.sock.listen(5)
        
        if client_prem == 2:
            self.can_clients_shutdown = False

    def run(self):
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        self.bot_pro = subprocess.Popen(['cmd', '/c', 'dependencies\\bot.exe'], startupinfo=si)
        self.bot_pid = self.bot_pro.pid

        while True:
            self.handle_socket()


    def handle_socket(self):
            c,addr = self.sock.accept()

            print('\n[Received Connection] ',addr)
            
            #receiving the request
            request = c.recv(1024)
            request = int.from_bytes(request,"big")

            print("Request Sent: "+str(request))

            result_message = b''

            if request == REQUEST_SERVER_UP:
                result_message = self.start()
            elif request == REQUEST_SERVER_DOWN:
                result_message = self.stop()
            elif request == REQUEST_SERVER_STATUS:
                result_message = self.status()
            
            c.send(result_message)
            print('Result Message Sent')
            c.close()

    def start(self):
        if not self.is_server_up: 
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            self.pro = subprocess.Popen(['cmd', '/c', self.path + '\\' + self.batch_file], startupinfo=si)
            self.pro_pid = self.pro.pid
            self.is_server_up = True
            return b'Starting Server'
      
        #error if we cannot start
        return b'Request Rejected | Clients cannot shutdown or server is off | Or Server is already up'

    def stop(self):
        if self.can_clients_shutdown and self.is_server_up:
            command = ['TASKKILL', '/F', '/T', '/PID', str(self.pro_pid)]
            subprocess.Popen(command)
            self.is_server_up = False
            return b'Shutting Down Server'
        #error if we cannot start
        return b'Request Rejected | Clients cannot shutdown or server is off | Or Server is already up'
    
    def status(self):
        if self.is_server_up:
            return b'UP'
        else:
            return b'DOWN'
        

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

def startup():
    print('Hello form startup')
    START_UP = 0
    CLIENT_SHUTDOWN = 1

    server_data_file = open('server.data','r')
    data = server_data_file.read()
    if data == '' or len(data) > 0 and data[0] == ' ':
        init_data_in_file()
        startup()
    server_data_file.close()

    preferences = parse_preference_data()

    if preferences[START_UP]=='false':
        prompt = "[1] Start |[2] For Changing Sever Settings\n>>> "
        choice = int(input(prompt))

        if choice == 2:
            init_data_in_file()
            startup()
        else:
            user_perm = int(get_choice('[1] Users can shutdown sever |[2] Users cannot shutdown sever\n>>> '))
            return Server(user_perm)
    else:
        user_perm = preferences[CLIENT_SHUTDOWN]
        if user_perm.lower() == 'true':
            return Server(1) #1 - clients can shutdown
        else:
            return Server(2) #2 - clients cannot shutdown
    return 'error'

if __name__ == '__main__':
    startup().run()