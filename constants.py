# This constant is used by the assembler to validate address values.
# The Voltmace Database does not use A13 and A14.
MAX_WORD = 8191

INITIAL_PREFS = {
    "user_name": "",
    "recent_edit": [],
    "recent_asm": [],
    "recent_bin": [],
    "recent_view": [],
    "current_edit": "",            
    "current_asm": "",
    "current_bin": "",
    "current_view": "",
    "def_asm_dir": "",      #this is actually a global default for all Open buttons
    "auto_archive": True,
    "archive_serial": 0,
    "edit_height": 30,
    "assemble_height" : 25,
    "dump_height" : 20,
    "view_height" : 20,
    "text_size" : 12
    }


REGISTER_DICT = {
   "r0":0,
   "r1":1,
   "r2":2,
   "r3":3
}
   
CONDITION_DICT = {
   "eq":0,
   "a1":0,  # bit test, all 1's
   "z" :0,
   "gt":1,
   "p" :1,
   "lt":2,
   "s0":2,  # bit test, some 0's
   "n" :2,
   "un":3
}

# index names for each element in the opcode dictionary
STRUCTURE = 0
NUMBER_OF_BYTES = 1
OPCODE = 2
CYCLES = 3

OPCODE_DICT = {
   "adda":("R*AX", 3, 140, 4),
   "addi":("R V ", 2, 132, 2),
   "addr":("R*a ", 2, 136, 3),
   "addz":("  R ", 1, 128, 2),
   "anda":("R*AX", 3, 76, 4),
   "andi":("R V ", 2, 68, 2),
   "andr":("R*a ", 2, 72, 3),
   "andz":("  r ", 1, 64, 2),
   "bcfa":("c*A ", 3, 156, 3),
   "bcfr":("c*a ", 2, 152, 3),
   "bcta":("C*A ", 3, 28, 3),
   "bctr":("C*a ", 2, 24, 3),
   "bdra":("R*A ", 3, 252, 3),
   "bdrr":("R*a ", 2, 248, 3),
   "bira":("R*A ", 3, 220, 3),
   "birr":("R*a ", 2, 216, 3),
   "brna":("R*A ", 3, 92, 3),
   "brnr":("R*a ", 2, 88, 3),
   "bsfa":("c*A ", 3, 188, 3),
   "bsfr":("c*a ", 2, 184, 3),
   "bsna":("R*A ", 3, 124, 3),
   "bsnr":("R*a ", 2, 120, 3),
   "bsta":("C*A ", 3, 60, 3),
   "bstr":("C*a ", 2, 56, 3),
   "bsxa":(" *A3", 3, 191, 3),
   "bxa" :(" *A3", 3, 159, 3),
   "coma":("R*AX", 3, 236, 4),
   "comi":("R V ", 2, 228, 2),
   "comr":("R*a ", 2, 232, 3),
   "comz":("  R ", 1, 224, 2),
   "cpsl":("  V ", 2, 117, 3),
   "cpsu":("  V ", 2, 116, 3),
   "dar" :("R   ", 1, 148, 3),  # was "  R "
   "eora":("R*AX", 3, 44, 4),
   "eori":("R V ", 2, 36, 2),
   "eorr":("R*a ", 2, 40, 3),
   "eorz":("  R ", 1, 32, 2),
   "halt":("    ", 1, 64, 2),
   "iora":("R*AX", 3, 108, 4),
   "iori":("R V ", 2, 100, 2),
   "iorr":("R*a ", 2, 104, 3),
   "iorz":("  R ", 1, 96, 2),
   "ldpl":(" *A ", 3, 16, 4),
   "loda":("R*AX", 3, 12, 4),
   "lodi":("R V ", 2, 4, 2),
   "lodr":("R*a ", 2, 8, 3),
   "lodz":("  Z ", 1, 0, 2),
   "lpsl":("  0 ", 1, 147, 2),
   "lpsu":("  0 ", 1, 146, 2),
   "nop" :("    ", 1, 192, 2),
   "ppsl":("  V ", 2, 119, 3),
   "ppsu":("  V ", 2, 118, 3),
   "redc":("R   ", 1, 48, 2),
   "redd":("R   ", 1, 112, 2),
   "rede":("R V ", 2, 84, 3),
   "retc":("C   ", 1, 20, 3),
   "rete":("C   ", 1, 52, 3),
   "rrl" :("R   ", 1, 208, 2),
   "rrr" :("R   ", 1, 80, 2),
   "spsl":("    ", 1, 19, 2),
   "spsu":("    ", 1, 18, 2),
   "stpl":(" *A ", 3, 17, 4),
   "stra":("R*AX", 3, 204, 4),
   "strr":("R*a ", 2, 200, 3),
   "strz":("  r ", 1, 192, 2),
   "suba":("R*AX", 3, 172, 4),
   "subi":("R V ", 2, 164, 2),
   "subr":("R*a ", 2, 168, 3),
   "subz":("  R ", 1, 160, 2),
   "tmi" :("R V ", 2, 244, 3),
   "tpsl":("  V ", 2, 181, 3),
   "tpsu":("  V ", 2, 180, 3),
   "wrtc":("R   ", 1, 176, 2),
   "wrtd":("R   ", 1, 240, 2),
   "wrte":("R V ", 2, 212, 3),
   "zbrr":(" *a ", 2, 155, 3),
   "zbsr":(" *a ", 2, 187, 3),
   "equ" :("D o ", 0, "X", 0),          
   "org" :("D o ", 0, "X", 0),
   "db"  :("D b ", 1, 0, 0),
   "dw"  :("D w ", 2, 0, 0)
}



ERROR_DICT = {
    "equ_label" : "No label specified for equate statement:",
    "equ_value" : "No value specified for equate statement:",
    "org_value" : "No value specified for org statement:",
    "inst_invalid" : "Unknown instruction \"{}\" in this line:",
    "bad_operand" : "Bad operand \"{}\" in this line:",
    "r0123" : " \"{}\" where r0, r1, r2 or r3 expected",
    "r123" : " \"{}\" where r1, r2 or r3 expected",
    "cond5" : " \"{}\" where eq,gt,lt,a1 or s0 expected",
    "cond6" : " \"{}\" where eq,gt,lt,a1,s0 or un expected",
    "not_expecting" : "Not expecting \"{}\" here",
    "r3" : " \"{}\" where r3 expected",
    "value" : " \"{}\" is not a valid 8-bit value",
    "word" : " \"{}\" is either not defined, cannot be evaluated or is too big",
    "indx" : " \"{}\" is not a valid indexing specification",
    "indxq" : " \"{}\" is not valid here for indexed instructions",
    "relative" : "Relative address \"{}\" is not in range -64 to +63",
    "r0" : "\"{}\" is not valid here. Should be blank or r0",
    "already_defined" : "\"{}\" is already defined."
    }
