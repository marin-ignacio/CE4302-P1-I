from PIL import ImageTk,Image
import tkinter as tk

from constants import *
from memory import Memory
from bus import Bus
from cpu import CPU

INSTS            = 0
CPU_CACHE_BLOCKS = 1
BUS_ACTION		 = 2
CURR_INST        = 0
LAST_INST        = 1

class MainWindow(tk.Tk):

	__system_canvas     = None
	__system_img        = None
	__pause_next_button = None
	__next_inst_entry   = None

	__system_on_pause   = False

	__ram_labels  = list()
	__cpus_labels = list()
	__bus_labels  = list()

	__ram  = None
	__bus  = None
	__cpus = list()

	def __init__(self):
		tk.Tk.__init__(self)
		self.wm_title(WINDOW_TITLE)
		self.geometry("{}x{}".format(WINDOW_WIDTH, WINDOW_HEIGHT))
		self.resizable(0, 0)
		self.init_system()
		self.init_main_canvas()
		self.init_cpus_labels()
		self.init_ram_labels()
		self.init_bus_msgs_labels()
		if (OPERATION_MODE != 1):
			self.launch_system()
			
	def init_system(self) -> None:
		self.__ram = Memory(p_window=self)
		self.__bus = Bus(self.__ram, p_window=self)
		for i in range(PROCESSORS_NUM):
			self.__cpus.append(CPU(p_id=i, p_bus=self.__bus, p_window=self))

	def launch_system(self) -> None:
		for i in range(PROCESSORS_NUM):
			self.__cpus[i].start()

	def is_system_on_pause(self) -> bool:
		return self.__system_on_pause

	def stop_system_execution(self) -> None:
		self.__system_on_pause = True

	def pause_system(self) -> None:
		#The system has just been paused
		if (not(self.is_system_on_pause())):
			#Enables the entry widget	
			self.__next_inst_entry.config(state=tk.NORMAL)
			#Changes button text
			self.__pause_next_button.config(text="Resume")
		#The system has just been launched
		else:
			new_inst = self.__next_inst_entry.get()
			if (new_inst != ""):
				self.set_cpu_next_inst(new_inst)
			#Cleans the entry wodget text
			self.__next_inst_entry.delete(0, "end")
			#Disables the entry widget
			self.__next_inst_entry.config(state=tk.DISABLED)
			#Changes button text
			self.__pause_next_button.config(text="Pause")
		#Changes system state
		self.__system_on_pause = not(self.__system_on_pause)

	def generate_next_inst(self) -> None:
		new_inst = self.__next_inst_entry.get()
		if (new_inst != ""):
			self.set_cpu_next_inst(new_inst)
			self.__next_inst_entry.delete(0, "end")
		#Resumes the system
		self.__system_on_pause = False
		#If it is the first cycle to execute
		if (not(self.__cpus[0].is_alive())):
			self.launch_system()

	def set_cpu_next_inst(self, p_inst: str) -> None:
		self.__cpus[int(p_inst[1])].set_entry_inst(p_inst)

	def init_main_canvas(self) -> None:
		self.__system_canvas = tk.Canvas(self, width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
		self.__system_img    = ImageTk.PhotoImage(Image.open(SYSTEM_IMG_PATH)) 
		self.__system_canvas.create_image((WINDOW_WIDTH//2), (WINDOW_HEIGHT//2), image=self.__system_img)  
		self.__system_canvas.place(x=0, y=0)
		self.__pause_next_button = tk.Button(self, width=6, height=1, font="Verdana 10", 
												text= "Next" if (OPERATION_MODE == 1) else "Pause", 
												command= self.generate_next_inst if (OPERATION_MODE == 1) else self.pause_system, 
												activebackground="dimgrey")
		self.__pause_next_button.place(x=1640, y=55)

		self.__next_inst_entry = tk.Entry(self, bg="white", fg="black", width=26, bd=1, font="Verdana 10", 
												state= tk.NORMAL if (OPERATION_MODE == 1) else tk.DISABLED)
		self.__next_inst_entry.place(x=1580, y=30)

	def init_cpus_labels(self) -> None:
		for i in range(len(self.__cpus)):
			#Create the necessary labels for a processor
			self.init_cpu_labels(self.__cpus[i])

	def init_cpu_labels(self, p_cpu: CPU) -> None:
		cpu_labels = list()
		self.init_inst_labels(p_cpu, cpu_labels)
		self.init_cache_labels(p_cpu, cpu_labels)
		self.__cpus_labels.append(cpu_labels)

	def init_inst_labels(self, p_cpu: CPU, p_cpu_labels: list) -> None:
		offset_inst  =  44
		x_inst       = 450 if (p_cpu.get_id() % 2 == 0) else 1115
		y_inst       =  62 if (p_cpu.get_id() < 2) else 850
		insts_labels = list()
		insts_labels.append(self.__system_canvas.create_text(x_inst, y_inst            , font="Verdana 10", text=""))
		insts_labels.append(self.__system_canvas.create_text(x_inst, y_inst+offset_inst, font="Verdana 10", text=""))
		p_cpu_labels.append(insts_labels)

	def init_cache_labels(self, p_cpu: CPU, p_cpu_labels: list) -> None:
		x            = 318 if (p_cpu.get_id() % 2 == 0) else 983
		y            = 255 if (p_cpu.get_id() < 2) else 648
		x_offset     = 95
		y_offset     = 35
		cache_labels = list()
		for i in range(CACHE_SET_SIZE):
			for j in range(CACHE_BLOCKS//CACHE_SET_SIZE):
				pos = j + i * CACHE_SET_SIZE
				cache_block_label = dict()
				cache_block_label["state"]   = self.__system_canvas.create_text(x           , y+y_offset*pos-pos, font="Verdana 13 bold", text=p_cpu.get_cache_l1().get_blocks()[i][j]["state"])
				cache_block_label["mem_dir"] = self.__system_canvas.create_text(x+x_offset  , y+y_offset*pos-pos, font="Verdana 13"     , text=p_cpu.get_cache_l1().get_blocks()[i][j]["mem_dir"])
				cache_block_label["data"]    = self.__system_canvas.create_text(x+x_offset*2, y+y_offset*pos-pos, font="Verdana 13"     , text=p_cpu.get_cache_l1().get_blocks()[i][j]["data"])
				cache_labels.append(cache_block_label)
		p_cpu_labels.append(cache_labels)

	def init_ram_labels(self) -> None:
		x         = 1727
		y         = 244
		y_offset  = 32
		mem_label = None
		for i in range(MEM_BLOCKS):
			if (i >= 10):
				mem_label = self.__system_canvas.create_text(x, y+y_offset*i+6    , font="Verdana 13", text=self.__ram.get_blocks()[i]["data"])
			elif (i >= 3 and i < 10):
				mem_label = self.__system_canvas.create_text(x, y+y_offset*i+4    , font="Verdana 13", text=self.__ram.get_blocks()[i]["data"])
			else:
				mem_label = self.__system_canvas.create_text(x, y+y_offset*i+(i+1), font="Verdana 13", text=self.__ram.get_blocks()[i]["data"])
			self.__ram_labels.append(mem_label)

	def init_bus_msgs_labels(self) -> None:
		for i in range(PROCESSORS_NUM):
			x = 155 if (i % 2 == 0) else 820
			y = 420 if (i < 2) else 550
			self.__bus_labels.append(self.__system_canvas.create_text(x, y, font="Verdana 10", text=""))

	def update_cpu_curr_inst_label(self, p_cpu: CPU) -> None:
		self.__system_canvas.itemconfigure(self.__cpus_labels[p_cpu.get_id()][INSTS][CURR_INST], text=p_cpu.see_curr_inst())
		self.__system_canvas.update()

	def update_cpu_last_inst_label(self, p_cpu: CPU) -> None:
		self.__system_canvas.itemconfigure(self.__cpus_labels[p_cpu.get_id()][INSTS][LAST_INST], text=p_cpu.see_last_inst())
		self.__system_canvas.update()

	def update_cpu_cache_label(self, p_id: int) -> None:
		target_cpu = self.__cpus[p_id]
		for i in range(CACHE_SET_SIZE):
			for j in range(CACHE_BLOCKS//CACHE_SET_SIZE):
				pos = j + i * CACHE_SET_SIZE
				state_label   = self.__cpus_labels[p_id][CPU_CACHE_BLOCKS][pos]["state"]
				mem_dir_label = self.__cpus_labels[p_id][CPU_CACHE_BLOCKS][pos]["mem_dir"]
				data_label    = self.__cpus_labels[p_id][CPU_CACHE_BLOCKS][pos]["data"]
				self.__system_canvas.itemconfigure(state_label,   text=target_cpu.get_cache_l1().get_blocks()[i][j]["state"])
				self.__system_canvas.itemconfigure(mem_dir_label, text=target_cpu.get_cache_l1().get_blocks()[i][j]["mem_dir"])
				self.__system_canvas.itemconfigure(data_label,    text=target_cpu.get_cache_l1().get_blocks()[i][j]["data"])
		self.__system_canvas.update()

	def update_ram_label(self, p_dir: int, p_data: str) -> None:
		self.__system_canvas.itemconfigure(self.__ram_labels[p_dir], text=p_data)
		self.__system_canvas.update()

	def update_bus_msg_label(self, p_id: int, p_msg: str, p_dir: str) -> None:
		self.clean_bus_msgs_labels()
		self.__system_canvas.itemconfigure(self.__bus_labels[p_id], text="{} {}".format(p_msg, p_dir))
		self.__system_canvas.update()

	def clean_bus_msgs_labels(self) -> None:
		for i in range(PROCESSORS_NUM):
			self.__system_canvas.itemconfigure(self.__bus_labels[i], text="")
		self.__system_canvas.update()
