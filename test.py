from kad import DHT

nodes = []
port = []
peer = DHT("localhost", 8600)
nodes.append(peer)

for i in range(1, 5):
    peer = DHT("localhost", 8600+i, seeds=[("localhost", 8600)])
    print(peer.peers())
    nodes.append(peer)

for i in range(5):
    print(nodes[i].peers())
