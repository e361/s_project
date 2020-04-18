from kad import DHT
from art import *
import socket


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
    tprint("Create a new lobby use 'New' or join some room using 'join + room_id': ", tfont):
    mov = input()

    seeds = 
    port =  
    peer = DHT("localhost", port, )
    
