import math

from design_patterns import *
from constants import *
from bus import Bus

LRU = CACHE_SET_SIZE

class Cache(Observer):

	def __init__(self, p_id, p_bus, p_window):
		self.id          = p_id
		self.blocks_num  = CACHE_BLOCKS
		self.block_size  = CACHE_BLOCK_SIZE
		self.set_size    = CACHE_SET_SIZE
		self.blocks      = list()
		self.bus         = p_bus
		self.init_blocks()
		self.main_window = p_window

	def get_id(self) -> int:
		return self.id

	def get_blocks_num(self) -> int:
		return self.blocks_num

	def get_block_size(self) -> int:
		return self.block_size

	def get_set_size(self) -> int:
		return self.set_size

	def get_blocks(self) -> list:
		return self.blocks

	#------------------------------------------------------------------------
	# CACHE BLOCKS
	#------------------------------------------------------------------------
	def init_blocks(self) -> None:
		for i in range(self.blocks_num//self.set_size):
			block_set = []
			for j in range(self.set_size):
				block = self.create_block(self.int_to_str_bin(j + i*self.set_size, self.blocks_num), 
										  INVALID, 
										  self.int_to_str_bin(0, MEM_BLOCKS), 
										  self.int_to_str_hex(0, self.block_size))
				block_set.append(block)
			block_set.append(0)
			self.blocks.append(block_set)

	def create_block(self, p_dir, p_state, p_mem_dir, p_data) -> dict:
		return {"dir": p_dir, "state": p_state, "mem_dir": p_mem_dir, "data": p_data}

	#------------------------------------------------------------------------
	# CACHE CONTROLLER
	#------------------------------------------------------------------------
	def change_block_state(self, p_block, p_state) -> None:
		p_block["state"] = p_state

	def update(self, subject: Subject) -> str:
		snooped_msg = subject.get_message()
		snooped_dir = subject.get_dir()
		#Tries to find the block in cache
		block = self.fetch_local_block(snooped_dir)
		data = None
		#The requested block is in the cache
		if (block != None):
			print("Cache reacted to bus event {}".format(snooped_msg))
			#---------------------------------------------------------------
			# SHARED state
			#---------------------------------------------------------------
			if (block["state"] == SHARED):
				if (snooped_msg == WRITE_MISS or snooped_msg == INVALIDATE):
					self.change_block_state(block, INVALID)
				elif (snooped_msg == READ_MISS):
					subject.set_not_exclusive()
			#---------------------------------------------------------------
			# EXCLUSIVE state
			#---------------------------------------------------------------
			elif (block["state"] == EXCLUSIVE):
				if (snooped_msg == READ_MISS):
					subject.set_not_exclusive()
					self.change_block_state(block, SHARED)
				elif (snooped_msg == WRITE_MISS or snooped_msg == INVALIDATE):
					self.change_block_state(block, INVALID)
			#---------------------------------------------------------------
			# MODIFIED state
			#---------------------------------------------------------------
			elif (block["state"] == MODIFIED):
				if (snooped_msg == WRITE_MISS):
					self.write_back_block(block)
					self.change_block_state(block, INVALID)
				elif (snooped_msg == READ_MISS):
					subject.set_not_exclusive()
					self.change_block_state(block, OWNED)
					data = block["data"]
			#---------------------------------------------------------------
			# OWNED state
			#---------------------------------------------------------------
			elif (block["state"] == OWNED):
				if (snooped_msg == WRITE_MISS or snooped_msg == INVALIDATE):
					self.write_back_block(block)
					self.change_block_state(block, INVALID)
				elif (snooped_msg == READ_MISS):
					subject.set_not_exclusive()
					data = block["data"]
			#Updates cache blocks labels
			self.main_window.update_cpu_cache_label(self.id)
		#The requested block is not in the cache 
		#The cache does not have to supply a block to the request
		return data

	def read_inst(self, p_dir) -> None:
		#Tries to find the block in cache
		block = self.fetch_local_block(p_dir)
		#The block is not in the cache -> CACHE READ MISS
		if (block == None):
			mem_data  = self.fetch_mem_block(READ_MISS, p_dir)
			state     = EXCLUSIVE if (self.bus.is_exclusive()) else SHARED 
			self.place_block(state, p_dir, mem_data)
			#Updates cache blocks labels
			self.main_window.update_cpu_cache_label(self.id)

	def write_inst(self, p_dir, p_data) -> None:
		#Tries to find the block in cache
		block = self.fetch_local_block(p_dir)
		# The block is not in the cache -> CACHE WRITE MISS
		if (block == None):
			mem_data = self.fetch_mem_block(WRITE_MISS, p_dir)
			self.place_block(MODIFIED, p_dir, p_data)
		#The block is in the cache -> CACHE WRITE HIT
		else:
			self.local_write(block, p_data)
		#Updates cache blocks labels
		self.main_window.update_cpu_cache_label(self.id)

	def local_write(self, p_block, p_data) -> None:
		if (p_block["state"] == SHARED):
			#Acquires the bus and close the lock
			self.bus.get_lock().acquire()
			print("Cache {} acquire the bus to invalidate data".format(self.id))
			self.bus.notify_invalidate(p_block["mem_dir"], self.id)
			#Releases the bus and open the lock
			self.bus.get_lock().release()
			print("Cache {} release the bus to invalidate data".format(self.id))
		#Writes the new data in the block 
		p_block["data"]  = p_data
		#Changes the block state to "MODIFIED"
		p_block["state"] = MODIFIED
		#Updates the LRU block
		set_n = int(p_block["dir"][-1])
		self.blocks[set_n][LRU] = 0 if (self.blocks[set_n][LRU]) else 1

	def fetch_local_block(self, p_dir) -> dict:
		set_n = int(p_dir[-1])
		for i in range(self.set_size):
			block = self.blocks[set_n][i]
			if (block["mem_dir"] == p_dir and block["state"] != INVALID):
				return block
		return None

	def fetch_mem_block(self, p_bus_msg, p_dir) -> str:
		#Acquires the bus and close the lock
		self.bus.get_lock().acquire()
		print("Cache {} acquire the bus to fetch data".format(self.id))
		#Uses the bus to fecth the data
		data = self.bus.fetch_data(p_bus_msg, p_dir, self.id)
		#Releases the bus and open the lock
		self.bus.get_lock().release()
		print("Cache {} release the bus to fetch data".format(self.id))
		return data

	def place_block(self, p_state, p_mem_dir, p_data) -> None:
		#Determines the cache position
		set_n = int(p_mem_dir[-1])
		pos   = self.blocks[set_n][LRU]
		#Checks the status of the block to determine if the value needs to be updated in memory
		old_block = self.blocks[set_n][pos]
		if (old_block["state"] == OWNED or old_block["state"] == MODIFIED):
			self.write_back_block(old_block)
		#Puts the new information on the block
		self.blocks[set_n][pos]["state"]   = p_state 
		self.blocks[set_n][pos]["mem_dir"] = p_mem_dir
		self.blocks[set_n][pos]["data"]    = p_data
		#Updates the LRU block
		self.blocks[set_n][LRU] = 0 if (self.blocks[set_n][LRU]) else 1

	def write_back_block(self, p_block) -> None:
		#Acquires the bus and close the lock
		self.bus.get_lock().acquire()
		print("Cache {} acquire the bus to write back data".format(self.id))
		#Uses the bus to write back the data
		self.bus.write_back_block(p_block["mem_dir"], p_block["data"])
		#Releases the bus and open the lock
		self.bus.get_lock().release()
		print("Cache {} release the bus to write back data".format(self.id))

	#------------------------------------------------------------------------

	def int_to_str_bin(self, p_num, p_digits) -> str:
		return format(p_num, "0{}b".format(int(math.log2(p_digits))))

	def int_to_str_hex(self, p_num, p_digits) -> str:
		return "0x{0:0{1}X}".format(p_num, int(math.log2(p_digits)))
