import mysql.connector as mysql
import socket
import threading

#Variables
host = "localhost"
user = "root"
password = "123456"

HOST = '127.0.0.1'
POST = 9090

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, POST))

server.listen()

connections = []
clients = []
chat_ports = []
nicknames = []



################ DATABASE #############

#Connecting to existing database
try:
    db1 = mysql.connect(host=host, user=user, password=password,database="users")
    command_handler = db1.cursor()
    print("Connect succesfully")
except Exception as e:
    print(e)
    print("Failed to connect")

def CreatingAccount(name, password):
    try:
        query = "INSERT INTO ACCOUNT(name, password) VALUES (%s,%s)"
        query_vals = (name, password)
        command_handler.execute(query, query_vals)
        db1.commit()
        print(command_handler.rowcount, "record inserted")
    except Exception as e:
        print(e)

def FindSameUsername(name):
    try:
        query = "SELECT * FROM ACCOUNT WHERE ACCOUNT.NAME = %s"
        query_vals = (name,)
        command_handler.execute(query, query_vals)
        
        if len(list(command_handler)) != 0:
            return True
        else:
            return False

    except Exception as e:
        print(e)

def FindAccount(name, password):
    try:
        query = "SELECT * FROM ACCOUNT WHERE ACCOUNT.NAME = %s"
        query_vals = (name,)
        command_handler.execute(query, query_vals)
        for command in command_handler:
            if (command[2] == password):
                return True

        return False

    except Exception as e:
        print(e)

################ SERVER #############

def handleLogin(conection, username, password):
    rightAccount = FindAccount(username, password)
    if rightAccount:
        print("Login successfully")
        return True
    else:
        print("Username or password incorrect")
        return False

def handleRegister(conection, username, password):
    hasSameUsername = FindSameUsername(username)
    if hasSameUsername:
        print("Has same user name")
    else:
        print("Successful created")
        CreatingAccount(username, password)
    return

def handle(connection):
    while True:
        try:
            message = connection.recv(1024).decode("utf-8")

            [type, username, password, chat_port] = message.split('-')
            if type == "LOGIN":
                if handleLogin(connection, username, password):
                    clients.append(connection)
                    chat_ports.append(chat_port)
                    nicknames.append(username)

                    response = "SUCCESS-" + username
                    connection.send(response.encode("utf-8"))
                    connections.remove(connection)
                    sendListFriend()
                    break
            else:
                handleRegister(connection, username, password)
            
        except:
            connection.close()
            print("Disconnected")
            break

def sendListFriend():
    for client in clients:
        client_index = clients.index(client)
        try:
            list_friend = ""
            for i in range(len(clients)):
                if i != client_index:
                    list_friend += f"{chat_ports[i]}-{nicknames[i]}/"
            print(list_friend)
            client.send(list_friend.encode('utf-8'))
        except:
            print("Error client")
            clients.remove(clients[client_index])
            client.close()
            nicknames.remove(nicknames[client_index])
            chat_ports.remove(chat_ports[client_index])


# receive
def receive():
    while True: 
        connection, address = server.accept()
        print(connection)
        print(f"Connected with {(address)} !")

        connections.append(connection)

        thread = threading.Thread(target=handle, args=(connection,))
        thread.start()


print("Server running...")
receive()
