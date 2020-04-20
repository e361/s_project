from kad import DHT
from art import *
import socket


host = "localhost"
port = 9000

""" At the beginning of peerchat application stage
    enter your username, and choice to create a new 
    lobby or join an old one.
"""

def help(exception):
   pass


def chatroom():
    
    """ based on art module, this module draw some ascii code art(Use ascii to draw or write some ascii art text)
        tfont : the font style.
    """

    tfont = "standard"
    tprint("Welcome to P2Pchat", tfont)
    tprint("Please enter your username:", tfont)
    username = input()
    tprint("Create a new lobby use 'New' or join some room\n using 'join + room_id': ")
    try:
        mov = input()
        print(mov)
        register(mov)
    except Exception as e:
        help(e)
    """
        seed = scok
        peer = DHT("localhost", port, seeds=[seed])
    """


""" register username and ip, port information to bootstrap server """
def register(message):
    try:
        # sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            #sock.bind( ('', 9800))
            sock.connect( (host, port) )
            sock.sendall(bytes(message, "ascii") )
            response = str(sock.recv(1024), "ascii")
            print("Received: {}".format(response) )
            
    except OSError as e:
        print("registry process failed, please try again")

if __name__ == "__main__":
    chatroom() 
