import json
import random
import socket
import socketserver
import threading
import time
from bucketset import BucketSet
from hashing import hash_function, random_id
from peer import Peer
from storage import Shelve
from shortlist import Shortlist
import hashing

k = 20
alpha = 3
id_bits = 128
iteration_sleep = 1

class DHTRequestHandler(socketserver.BaseRequestHandler):
	def handle(self):
		try:
			message = json.loads(self.request[0].decode ('utf-8').strip())
			message_type = message["message_type"]
			if message_type == "ping":
				self.handle_ping(message)
			elif message_type == "pong":
				self.handle_pong(message)
			elif message_type == "find_node":
				self.handle_find(message)
			elif message_type == "find_value":
				self.handle_find(message, find_value=True)
			elif message_type == "found_nodes":
				self.handle_found_nodes(message)
			elif message_type == "found_value":
				self.handle_found_value(message)
			elif message_type == "store":
				self.handle_store(message)
                # what do u want of KeyError or ValueError???
		except KeyError:
			pass
		except ValueError:
			pass
		client_host, client_port = self.client_address
		peer_id = message["peer_id"]
		peer_info = message["peer_info"]
		new_peer = Peer(client_host, client_port, peer_id, peer_info)
		self.server.dht.buckets.insert(new_peer)

	def handle_ping(self, message):
		client_host, client_port = self.client_address
		id = message["peer_id"]
		info = message["peer_info"]
		peer = Peer(client_host, client_port, id, info)
		peer.pong(socket=self.server.socket, peer_id=self.server.dht.peer.id, lock=self.server.send_lock)

	def handle_pong(self, message):
                # receive ping message response doesn't need to do anything.
		pass

	def handle_find(self, message, find_value=False):
		key = message["id"]
		id = message["peer_id"]
		info = message["peer_info"]
		client_host, client_port = self.client_address
		peer = Peer(client_host, client_port, id, info)
		response_socket = self.request[1]
		if find_value and (str(key) in self.server.dht.data):
			value = self.server.dht.data[str(key)]
			peer.found_value(id, value, message["rpc_id"], socket=response_socket, peer_id=self.server.dht.peer.id, peer_info=self.server.dht.peer.info, lock=self.server.send_lock)
		else:
			nearest_nodes = self.server.dht.buckets.nearest_nodes(id)
			if not nearest_nodes:
				nearest_nodes.append(self.server.dht.peer)
			nearest_nodes = [nearest_peer.astriple() for nearest_peer in nearest_nodes]
			peer.found_nodes(id, nearest_nodes, message["rpc_id"], socket=response_socket, peer_id=self.server.dht.peer.id, peer_info=self.server.dht.peer.info, lock=self.server.send_lock)

	def handle_found_nodes(self, message):
		rpc_id = message["rpc_id"]
		shortlist = self.server.dht.rpc_ids[rpc_id]
		del self.server.dht.rpc_ids[rpc_id]
		nearest_nodes = [Peer(*peer) for peer in message["nearest_nodes"]]
		shortlist.update(nearest_nodes)

	def handle_found_value(self, message):
		rpc_id = message["rpc_id"]
		shortlist = self.server.dht.rpc_ids[rpc_id]
		del self.server.dht.rpc_ids[rpc_id]
		shortlist.set_complete(message["value"])

	def handle_store(self, message):
		key = message["id"]
		self.server.dht.data[str(key)] = message["value"]


class DHTServer(socketserver.ThreadingMixIn, socketserver.UDPServer):
	def __init__(self, host_address, handler_cls):
		socketserver.UDPServer.__init__(self, host_address, handler_cls)
		self.send_lock = threading.Lock()


class DHT(object):
	def __init__(self, host, port, id=None, seeds=[], storage={}, info={}, hash_function=hashing.hash_function, requesthandler=DHTRequestHandler):
		if not id:
			id = random_id()
		self.storage = storage
		self.info = info
		self.hash_function = hash_function
		self.peer = Peer(host, port, id, info)
		self.data = self.storage
		self.buckets = BucketSet(k, id_bits, self.peer.id)
		self.rpc_ids = {} # should probably have a lock for this
		self.server = DHTServer (self.peer.address(), requesthandler)
		self.server.dht = self
		self.server_thread = threading.Thread(target=self.server.serve_forever)
		self.server_thread.daemon = True
		self.server_thread.start()
		self.bootstrap(seeds)

	def identity (self):
		return self.peer.id

	def iterative_find_nodes(self, key, boot_peer=None):
		shortlist = Shortlist(k, key)
		shortlist.update(self.buckets.nearest_nodes(key, limit=alpha))
		if boot_peer:
			rpc_id = random.getrandbits(id_bits)
			self.rpc_ids[rpc_id] = shortlist
			boot_peer.find_node(key, rpc_id, socket=self.server.socket, peer_id=self.peer.id, peer_info=self.peer.info)
		while (not shortlist.complete()) or boot_peer:
			nearest_nodes = shortlist.get_next_iteration(alpha)
			for peer in nearest_nodes:
				shortlist.mark(peer)
				rpc_id = random.getrandbits(id_bits)
				self.rpc_ids[rpc_id] = shortlist
				peer.find_node(key, rpc_id, socket=self.server.socket, peer_id=self.peer.id, peer_info=self.info)
			time.sleep(iteration_sleep)
			boot_peer = None
		return shortlist.results()

	def iterative_find_value(self, key):
		shortlist = Shortlist(k, key)
		shortlist.update(self.buckets.nearest_nodes(key, limit=alpha))
		while not shortlist.complete():
			nearest_nodes = shortlist.get_next_iteration(alpha)
			for peer in nearest_nodes:
				shortlist.mark(peer)
				rpc_id = random.getrandbits(id_bits)
				self.rpc_ids[rpc_id] = shortlist
				peer.find_value(key, rpc_id, socket=self.server.socket, peer_id=self.peer.id, peer_info=self.info) #####
			time.sleep(iteration_sleep)
		return shortlist.completion_result()

	# Return the list of connected peers
	def peers (self):
		return self.buckets.to_dict ()

	# Boostrap the network with a list of bootstrap nodes
	def bootstrap(self, bootstrap_nodes = []):
		for bnode in bootstrap_nodes:
			boot_peer = Peer(bnode[0], bnode[1], "", "")
			self.iterative_find_nodes(self.peer.id, boot_peer=boot_peer)

		if len (bootstrap_nodes) == 0:
			for bnode in self.buckets.to_list ():
				self.iterative_find_nodes(self.peer.id, boot_peer=Peer (bnode[0], bnode[1], bnode[2], bnode[3]))

	# Get a value in a sync way, calling an handler
	def get_sync (self, key, handler):
		try:
			d = self[key]
		except:
			d = None

		handler (d)

	# Get a value in async way
	def get (self, key, handler):
		#print ('dht.get',key)
		t = threading.Thread(target=self.get_sync, args=(key, handler))
		t.start ()


	# Iterator
	def __iter__ (self):
		return map(lambda key: int(key), self.data.__iter__ ())

	# Operator []
	def __getitem__(self, key):
		if type (key) == int:
			hashed_key = key
		else:
			hashed_key = self.hash_function (key)

		if str(hashed_key) in self.data:
			return self.data[str(hashed_key)]
		result = self.iterative_find_value(hashed_key)
		if result:
			return result
		raise KeyError

	# Operator []=
	def __setitem__(self, key, value):
		hashed_key = self.hash_function(key)
		#print ('dht.set',key,value,hashed_key)
		nearest_nodes = self.iterative_find_nodes(hashed_key)
		if not nearest_nodes:
			self.data[str(hashed_key)] = value
		for node in nearest_nodes:
			node.store(hashed_key, value, socket=self.server.socket, peer_id=self.peer.id)

	def tick():
		pass
