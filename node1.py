from kad import DHT

host, port = "localhost", 8600
peer = DHT(host, port)
peer["e361" ] = "Hello World"

