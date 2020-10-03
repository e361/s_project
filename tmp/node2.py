from kad import DHT


def printKeyValue(data):
    print(data)
    
host, port = "localhost", 8604

peer = DHT(host, port, info = "e361", seeds=[("localhost", 8600) ] )
print(peer.peers())

peer.get("e361", printKeyValue)
print(peer["e361"])

