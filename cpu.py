import threading
import random
import time
import math

from constants import *
from cache import Cache

class CPU(threading.Thread):

	def __init__(self, p_id, p_bus, p_window):
		threading.Thread.__init__(self)
		self.id              = p_id
		self.current_inst    = dict()
		self.last_inst       = dict()
		self.entry_inst      = dict()
		self.read_entry_inst = False
		self.cache_l1        = Cache(p_id=self.id, p_bus=p_bus, p_window=p_window)
		p_bus.attach(self.cache_l1)
		self.main_window     = p_window

	#------------------------------------------------------------------------

	def get_id(self) -> int:
		return self.id

	def get_current_inst(self) -> dict:
		return self.current_inst

	def get_last_inst(self) -> dict:
		return self.last_inst

	def get_cache_l1(self) -> Cache:
		return self.cache_l1

	#------------------------------------------------------------------------

	def see_curr_inst(self) -> str:
		return self.see_inst(self.current_inst)

	def see_last_inst(self) -> str:
		return self.see_inst(self.last_inst)

	def see_inst(self, p_inst) -> str:
		if (p_inst["op"] == CALC_INST):
			inst_str = "P{}: {}".format(p_inst["id"], p_inst["op"])
		elif (p_inst["op"] == READ_INST):
			inst_str = "P{}: {} {}".format(p_inst["id"], p_inst["op"], p_inst["dir"])
		else:
			inst_str = "P{}: {} {}; {}".format(p_inst["id"], p_inst["op"], p_inst["dir"], p_inst["data"])
		return inst_str

	def set_entry_inst(self, p_inst: str) -> None:
		print(p_inst)
		inst = dict()
		inst["id"] = self.id
		inst["op"] = p_inst[4:8]
		if (inst["op"] != CALC_INST and inst["op"] != READ_INST):
			inst["op"]   = p_inst[4:9]
			inst["dir"]  = p_inst[10:14]
			inst["data"] = p_inst[16:22]
		elif (inst["op"] == READ_INST):
			inst["dir"] = p_inst[9:13]
		self.entry_inst      = inst
		self.read_entry_inst = True

	#------------------------------------------------------------------------

	def generate_calc_inst(self) -> dict:
		return {"id": self.id, "op": CALC_INST}

	def generate_read_inst(self, p_dir) -> dict:
		return {"id": self.id, "op": READ_INST, "dir": p_dir}

	def generate_write_inst(self, p_dir, p_data) -> dict:
		return {"id": self.id, "op": WRITE_INST, "dir": p_dir, "data": p_data}

	def generate_mem_dir(self) -> str:
		return self.int_to_str_bin(round(random.uniform(0, MEM_BLOCKS-1)))

	def generate_data(self) -> str:
		return self.int_to_str_hex(round(random.uniform(0, 2**MEM_BLOCK_SIZE)))

	def generate_inst(self) -> dict:
		insts = list()
		insts.append(self.generate_calc_inst())
		insts.append(self.generate_read_inst(self.generate_mem_dir()))
		insts.append(self.generate_write_inst(self.generate_mem_dir(), self.generate_data()))
		return insts[round(random.uniform(0,2))]

	#------------------------------------------------------------------------

	def execute_inst(self) -> None:
		if (self.current_inst["op"] != CALC_INST):
			if (self.current_inst["op"] == READ_INST):
				self.cache_l1.read_inst(self.current_inst["dir"])
			else:
				self.cache_l1.write_inst(self.current_inst["dir"], self.current_inst["data"])

	#------------------------------------------------------------------------

	def run(self):
		current_cycle = 0
		while (current_cycle < CYCLES_NUMBER):
			#The system is not paused
			if (not(self.main_window.is_system_on_pause())):
				if (self.current_inst != {}):
					self.last_inst = self.current_inst
					#Updates last instruction label
					self.main_window.update_cpu_last_inst_label(self)
				#Generates a new instruction
				self.current_inst = self.generate_inst() if (not(self.read_entry_inst)) else self.entry_inst
				#Updates current instruction label
				self.main_window.update_cpu_curr_inst_label(self)
				#If read the entry instruction
				if (self.read_entry_inst):
					self.read_entry_inst = False
				#Executes the current instruction
				self.execute_inst()

				#Execute a specified numer of cycles
				if (OPERATION_MODE == 0):
					current_cycle += 1
				#Step by step, just execute the next cycle
				elif (OPERATION_MODE == 1):
					#Pauses the system
					self.main_window.stop_system_execution()
				#Continuos execution
				else:
					#Waits a time to generate the next instruction
					time.sleep(PROCESSOR_FREQ)

	#------------------------------------------------------------------------

	def int_to_str_bin(self, p_num: int) -> str:
		return format(p_num, "0{}b".format(int(math.log2(16))))

	def int_to_str_hex(self, p_num: int) -> str:
		return "0x{0:0{1}X}".format(p_num, int(math.log2(16)))
