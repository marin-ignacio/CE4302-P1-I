import math
import time

from design_patterns import *
from constants import *

class Memory:

	def __init__(self, p_window):
		self._delay      = MEM_DELAY
		self._blocks_num = MEM_BLOCKS
		self._block_size = MEM_BLOCK_SIZE
		self._blocks     = list()
		self.init_blocks()

		self.main_window = p_window

	def init_blocks(self):
		for i in range(self._blocks_num):
			self._blocks.append({"dir": self.int_to_str_bin(i, self._blocks_num), 
								 "data": self.int_to_str_hex(0, self._block_size)})

	#------------------------------------------------------------------------

	def get_delay(self) -> int:
		return self._delay

	def get_blocks_num(self) -> int:
		return self._blocks_num

	def get_block_size(self) -> int:
		return self._block_size

	def get_blocks(self) -> list:
		return self._blocks

	#------------------------------------------------------------------------

	def fetch_data(self, p_dir) -> str:
		#Goes through all blocks
		for block in self._blocks:
			if (block["dir"] == p_dir):
				#Delay to simulate "memory wall" problem
				time.sleep(self._delay)
				#Reads the searched data
				return block["data"]
		return None

	def write_data(self, p_dir, p_data) -> None:
		#Delay to simulate "memory wall" problem
		time.sleep(self._delay)
		#Writes the new data
		pos = int(p_dir, 2)
		self._blocks[pos]["data"] = p_data

		#Updates block memory label
		self.main_window.update_ram_label(pos, p_data)

	#------------------------------------------------------------------------

	def int_to_str_bin(self, p_num, p_digits) -> str:
		return format(p_num, "0{}b".format(int(math.log2(p_digits))))

	def int_to_str_hex(self, p_num, p_digits) -> str:
		return "0x{0:0{1}X}".format(p_num, int(math.log2(p_digits)))
