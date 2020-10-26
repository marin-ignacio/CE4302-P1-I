from typing import List
import threading

from design_patterns import *
from constants import *
from memory import Memory

class Bus(Subject):

	_message:   str            = None
	_dir:       str            = None
	_exclusive: int            = 1
	_observers: List[Observer] = []
	_lock                      = threading.RLock()

	def __init__(self, p_mem, p_window):
		self.memory      = p_mem
		self.main_window = p_window

	#------------------------------------------------------------------------

	def get_message(self) -> str:
		return self._message

	def get_dir(self) -> str:
		return self._dir

	def is_exclusive(self) -> int:
		return self._exclusive

	def set_not_exclusive(self) -> None:
		self._exclusive = 0

	def get_lock(self):
		return self._lock

	#------------------------------------------------------------------------

	def attach(self, observer: Observer) -> None:
		self._observers.append(observer)

	def detach(self, observer: Observer) -> None:
		self._observers.remove(observer)

	def notify(self) -> str:
		print("Subject (Bus): Notifying observers...")
		for observer in self._observers:
			observer.update(self)

	#------------------------------------------------------------------------

	def notify_invalidate(self, p_dir, p_id) -> None:
		print("Bus: Notifying {} to attached caches...".format(INVALIDATE))
		self._message = INVALIDATE
		self._dir     = p_dir
		#Updates bus message label 
		self.main_window.update_bus_msg_label(p_id, self._message, self._dir)
		for observer in self._observers:
			if (observer.get_id() != p_id):
				observer.update(self)

	def notify_read_miss(self, p_id) -> str:
		print("Bus: Notifying {} to attached caches...".format(READ_MISS))
		data = None
		for observer in self._observers:
			if (observer.get_id() != p_id):
				tmp_data = observer.update(self)
				if (tmp_data != None):
					data = tmp_data
					break
		return data

	def notify_write_miss(self, p_id) -> None:
		print("Bus: Notifying {} to attached caches...".format(WRITE_MISS))
		for observer in self._observers:
			if (observer.get_id() != p_id):
				observer.update(self)

	#------------------------------------------------------------------------

	def fetch_data(self, p_msg: str, p_dir: str, p_id: int) -> str:
		self._message   = p_msg
		self._dir       = p_dir
		self._exclusive = True
		#Updates bus message label 
		self.main_window.update_bus_msg_label(p_id, self._message, self._dir)
		#READ MISS on bus
		if (self._message == READ_MISS):
			data = self.notify_read_miss(p_id)
			if (data == None):
				data = self.memory.fetch_data(self._dir)
			return data
		#WRITE MISS on bus
		else:
			self.notify_write_miss(p_id)
			return self.memory.fetch_data(self._dir)

	def write_back_block(self, p_dir, p_data) -> None:
		self.memory.write_data(p_dir, p_data)
