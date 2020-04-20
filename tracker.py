import socketserver
import threading
import uuid

host = "localhost"
port = 9000

class Handler(socketserver.BaseRequestHandler):
    
    def handle(self):
        data = str(self.request.recv(1024))
        data = data[2:].split()
        
        if str(data[0] == 'new' or data[0] == 'New'):
            
            """ 
             create a new lobby with uuid, record the network information for the host(ex. ip, port, username)
                maybe need to do some crypto to those data.
            """ 
            uid  = uuid.uuid4()
            user = self.client_address
            self.server.creatRoom(user, uid)
            print(self.server.room, self.server.user_list)
            response = bytes(uid.hex, 'ascii')
        elif str(data[0]) == 'join':
            if(data[1] not in self.server.room):
                response = bytes("Sorry there is no such room, please check your room ID", 'ascii')
            else:
                self.server.joinRoom(uid)            
        else:
            response = bytes("Hello I'm BootServer dumpAss", "ascii")

        self.request.sendall(response)
        print(data)


class bootServer(socketserver.TCPServer):
    
    def __init__(self, address, handler):
        socketserver.TCPServer.__init__(self, (host, port), handler)
        self.room = []
        self.user_list = dict()

    def creatRoom(self, user, room_id):
        self.room.append(room_id)
        self.user_list["room_id"] = user

    def joinRoom(self, room_id):
        
        """ giver the host information to the applicant??
            or give the last applicant node information?
            the other way is record all of applicant of the same lobby.
        """
        pass


if __name__ == "__main__":
    try:
        #server = socketserver.TCPServer( (host, port), Handler)
        server = bootServer( (host, port), Handler )
        server.serve_forever()
    except KeyboardInterrupt:
        threading.Thread(target = server.shutdown() 
        print("\nServer close.")
