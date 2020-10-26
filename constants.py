#-----------------------------------------------
# SYSTEM CONFIGURATION
#-----------------------------------------------
PROCESSORS_NUM =  4
PROCESSOR_FREQ =  3

#-----------------------------------------------
# 0 | Execute a specified numer of cycles
# 1 | Step by step, just execute the next cycle
# 2 | Continuos execution
#-----------------------------------------------
OPERATION_MODE =  1
CYCLES_NUMBER  = 10

#-----------------------------------------------
# MEMORY CONFIGURATION
#-----------------------------------------------
MEM_BLOCKS     = 16
MEM_BLOCK_SIZE = 16
MEM_DELAY      = PROCESSOR_FREQ + 2

#-----------------------------------------------
# CACHE CONFIGURATION
#-----------------------------------------------
CACHE_BLOCK_SIZE = 16
CACHE_BLOCKS     =  4
CACHE_SET_SIZE   =  2

#-----------------------------------------------
# BUS MESSAGES
#-----------------------------------------------
READ_MISS  = "Read Miss"
WRITE_MISS = "Write Miss"
INVALIDATE = "Invalidate"

#-----------------------------------------------
# INSTRUCTION TYPES
#-----------------------------------------------
CALC_INST  = "CALC"
WRITE_INST = "WRITE"
READ_INST  = "READ"

#-----------------------------------------------
# COHERENCE STATES
#-----------------------------------------------
MODIFIED  = "M"
OWNED     = "O"
EXCLUSIVE = "E"
SHARED    = "S"
INVALID   = "I"

#-----------------------------------------------
# GUI CONFIGURATIONS
#-----------------------------------------------
WINDOW_WIDTH    = 1800 + 2
WINDOW_HEIGHT   =  950 + 2
WINDOW_TITLE    = "Multiprocessors Cache Coherence Simulator"
SYSTEM_IMG_PATH = "images/multicore-system.jpg"
