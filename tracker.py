import socketserver
import random
import json

host = "localhost"
port = 9000

""" BootServer message handler, only response for join and offline requests. """
class Handler(socketserver.BaseRequestHandler):
    def handle(self):
        """ load json message from any chatroom packet with 3-fold chunk json packet
                    +---------------------+--------+
            each of | user_name,          |        |
                    +---------------------+--------+
                    | message_type,       |        |    
                    +---------------------+--------+
                    | peer_info           |        |         
                    +---------------------+--------+
        """
        packet = json.loads(self.request.recv(1024))
        
        if packet['message_type'] == 'join':
            accountInfo = {packet['user_name'] : packet['peer_info']}
            response = self.server.join(accountInfo)

            if response:
                response = bytes(str(response), 'ascii')
                print("seed is %s" % str(response))
            else:
                response = bytes('join completed!\nBut theres no seed in the kademlia network.', 'ascii')
                print("No Seed!")
        elif packet['message_type'] == 'offline':
            user_name = packet['user_name']
            self.server.offline(user_name)
            response = bytes('ok', 'ascii')

        self.request.sendall(response)

""" BootSever with simple data structure,
    record every user with its username, ip, port and id while receiving join command
    delete user's record if received offline.
"""
class BootServer(socketserver.TCPServer):
    def __init__(self, handler):
        listen = (host, port)
        socketserver.TCPServer.__init__(self, listen, handler)
        self.hookList = {}
        print("Boot Server Start!")
        print("目前線上節點: %s\n " % self.hookList)
        
    def join(self, accountInfo):
        if self.hookList:
            key = random.choice(list(self.hookList.keys() ))
            seed = self.hookList[key]
        else:
            seed = None

        print("更新節點資訊...")
        self.hookList.update(accountInfo)
        print("目前線上節點: %s\n" % self.hookList)
        return seed

    def offline(self, key):
        print("收到離線訊息...")
        if self.hookList.get(key, None):
            self.hookList.pop(key)
        print("更新節點資訊...")
        print("目前線上節點: %s\n" % self.hookList)

if __name__ == "__main__":
    try:
        server = BootServer(Handler)
        server.serve_forever()

    except KeyboardInterrupt:
        server.server_close()
        print("\nServer close.")
