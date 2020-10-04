import socketserver
import threading
import random
import uuid
import json

host = "localhost"
port = 9000

class Handler(socketserver.BaseRequestHandler):
    
    def handle(self):
        data = json.loads(self.request.recv(1024))
        
        if data['message_type'] == 'join':
            accountInfo = {data['user_name'] : data['peer_info']}
            self.server.join(accountInfo)
            response = bytes('join completed!', 'ascii')

        elif data['message_type'] == 'offline':
            user_name = data['user_name']
            self.server.offline(user_name)
            response = bytes('ok', 'ascii')

        else:
            response = bytes("Hello I'm BootServer, please enter a valid command.", "ascii")

        self.request.sendall(response)
        
        print(self.server.user_list)

class BootServer(socketserver.TCPServer):
    
    def __init__(self, address, handler):
        socketserver.TCPServer.__init__(self, (host, port), handler)
        self.user_list = {}
    def join(self, user_name):
        self.user_list.update(user_name)
        return None

    def offline(self, accountInfo):
        self.user_list.pop(accountInfo)

    '''
    def creatRoom(self, user, room_id):
        self.room.append(room_id)
        self.user_list["room_id"] = user

    def joinRoom(self, room_id):
        
        """ give the host information to the applicant??
            or give the last applicant node information?
            the other way is record all of applicant of the same lobby.
        """
        pass
    '''


if __name__ == "__main__":
    try:
        server = BootServer( (host, port), Handler )
        server.serve_forever()

    except KeyboardInterrupt:
        threading.Thread(target = server.shutdown())
        print("\nServer close.")
