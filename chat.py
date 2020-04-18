from kad import DHT
from art import *
import socket


host = "localhost"
port = 8600

""" At the beginning of peerchat application stage
    enter your username, and choice to create a new 
    lobby or join an old one.
"""

def chatroom(sock):
    
    """ based on art module, this module draw some ascii code art(Use ascii to draw or write some ascii art text)
        tfont : the font style.
    """

    tfont = "standard"
    tprint("Welcome to P2Pchat", tfont)
    tprint("Please enter your username:", tfont)
    username = input()
    tprint("Create a new lobby use 'New' or join some room using 'join + room_id': ", tfont)
    mov = input()
    """
    seeds = 
    port =  
    peer = DHT("localhost", port, )
    """

""" register username and ip, port information to bootstrap server """

def register():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
    except OSError:
        print("registry process failed, please try again")

if __name__ == "__main__":
    register()
