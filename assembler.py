from constants import *
from os.path import exists
import datetime
import constants

symbol_table = dict()

def evaluate_to_decimal(op_str):
    '''convert operand string to integer'''
    
    def parse_int(string, base):
        '''converts string in base to integer and handles format errors'''
        error = False
        x = 0
        try:
            x = int(string,base)
        except:
            error = True
        return(x,error)
    
    
    if op_str is False:
        # there is no operand
        op_int = ( 0, True )   # says "false" is not valid 8 bit number
                                # need to find way of returning more explicit message
                                # perhaps a third element in the tuple
        return op_int
    
    global symbol_table
    if op_str.startswith('0x'):
        op_str = op_str[2:]
        op_int = parse_int(op_str,16)
    elif op_str.startswith('$'):
        op_str = op_str[1:]
        op_int = parse_int(op_str,16)
    elif op_str.startswith("h'"):
        op_str = op_str[2:]
        op_str = op_str[:-1]
        op_int = parse_int(op_str,16)
    elif op_str.isdigit():
        op_int = ( int(op_str) , False )        
    elif op_str.startswith('%'):
        op_str = op_str[1:]
        op_int = parse_int(op_str,2)
    elif op_str.startswith('0b'):
        op_str = op_str[2:]
        op_int = parse_int(op_str,2)
    elif op_str in symbol_table:
        op_int = (symbol_table[op_str], False )
    elif op_str.startswith("("):
        op_int = ( 0, True )
        label = (op_str[1:-2])
        if label in symbol_table:
            word = symbol_table[label]
            if op_str[-2:] == ")h":
                op_int = (word // 256, False)
            elif op_str[-2:] == ")l":
                op_int = (word % 256, False)
    else:
        op_int = ( 0, True )
    return op_int    # a tuple comprising the required integer and a
                     # boolean which is True if there is an error
                     
    op_int = ( 0, True )
    if op_str.startswith("("):
        label = (op_str[1:-2])
        if label in symbol_table:
            word = symbol_table[label]
            if op_str[-2:] == ")H":
                op_int = (word // 256, False)
            elif op_str[-2:] == ")L":
                op_int = (word % 256, False)
    return op_int               
                     
                                
class Line:
    def __init__(self, text):
        self.text = text
        self.label = False
        self.mnemonic = False
        self.qualifier = False
        self.indirect = False
        self.operand = False
        self.index = False
        self.start_address = False
        self.opcode1 = False
        self.opcode2 = False
        self.opcode3 = False
        self.cycles = False
        self.next_address = False
        self.symbol = (False, False)   # if there is a symbol, gets replaced with (string, value)
        self.error = (False, False)     # if there is an error, gets replaced with (type, phrase)

    def printline(self):
        ''' for testing and debugging '''
        print(self.__dict__)
        
    def format_lst(self):
        ''' Formats line of code for the .lst file'''
        # Address and machine code
        if self.opcode1 is False:
            line_str = "     "
        else:
            line_str = "{:04X} ".format(self.start_address)
        opcodes = (self.opcode1, self.opcode2, self.opcode3)
        for code in opcodes:
            if code is False:
                x = "    "
            else:
                x = "{:02X} ".format(code)            
            line_str += x
        line_str += "\t\t"
        # Number of machine cycles
        if self.cycles != False:
            line_str +=  str(self.cycles)
        else:
            line_str += " "
        # advance to next tab stop
        line_str += "\t"
        # the original text
        line_str += self.text
        return line_str
    
    def extract_code(self):
        opcodes = (self.opcode1, self.opcode2, self.opcode3)
        machine_code = []
        for code in opcodes:         
            if code is not False:
                machine_code.append(code)
        return machine_code
         
    def get_next_address(self):
        return self.next_address
    
    def get_symbol(self):
        return self.symbol
    
    def get_error(self):
        return self.error
    
    def error_reporter(self):
        '''formats any error message'''
        message = ""
        err_type, err_phrase = self.error
        if err_type != False:
            message = ERROR_DICT[err_type].format(err_phrase) + '\n' + self.text + '\n'
            err_type = True
        return err_type, message
    
    def allocate_space(self, address):
        def directive1():
            '''Handle EQU and ORG statements.'''   
            if self.mnemonic == "equ":
                # handle EQU statement
                if self.label == False:
                    self.error = ("equ_label", "")
                elif self.operand == False:
                    self.error = ("equ_value", "")
                else:
                    val, err = evaluate_to_decimal(self.operand)
                    if err:
                        self.error = ("bad_operand", self.operand) # ALSO NEED TO CHECK <64K
                    else:
                        self.symbol = (self.label, val)
            elif self.mnemonic == "org":
                # handle ORG statement
                if self.operand == False:
                    self.error = ("org_value", "")
                else:
                    val, err = evaluate_to_decimal(self.operand)
                    if err:
                        self.error = ("bad_operand", self.operand)
                    else:
                        self.next_address = val
                        self.symbol = (self.label, val)
            
        self.start_address = address
        # create symbol if this line has a label
        # this will get overwritten later if this is an EQU statement
        if self.label != False:
            self.symbol = (self.label, self.start_address)      
            # check that symbol hasn't been defined elsewhere
#            if self.symbol[0] in symbol_table:
            if self.label == "switch_player" :  ###############################################################
                print("label is ", self.label)               ###############################################################


            if self.symbol[0] in symbol_table.keys():
                print(self.symbol, "is in sym tab")
                self.error = ("already_defined", self.symbol[0])
        # handle any mnemonic
        if self.mnemonic != False:
            if self.mnemonic in OPCODE_DICT:
                # reserve space in memory
                byte_count = OPCODE_DICT[self.mnemonic][NUMBER_OF_BYTES]
                self.next_address = self.start_address + byte_count
                self.cycles = OPCODE_DICT[self.mnemonic][CYCLES]
                # deal with directives
                if OPCODE_DICT[self.mnemonic][STRUCTURE][0] == "D":
                    directive1()
            else:
                # 
                self.error = ("inst_invalid", self.mnemonic)
                return
        else:
            # no space is needed
            self.next_address = self.start_address
        
        
    def fragment(self):   
        ''' split up line of text into component parts '''
        # discard any comments
        this_line = self.text.lower()
        semicolon = this_line.find(";")
        if semicolon != -1:
            this_line = this_line[:semicolon]
        # check that there is still something on the line
        if len(this_line) == 0:
            return
        if this_line.isspace() == True:
            return
        # get chunks between white spaces:
        split_line = this_line.split()
        # split_line must have three elements
        if self.text[0].isspace() :      # there was no label
            split_line.insert(0, False)         
        if len(split_line) == 1:         # 
            split_line.insert(1, False)
        if len(split_line) == 2:         # 
            split_line.insert(2, False)         
        # label
#         self.label = split_line[0]
        
                    # strip any terminating colon for
            # compatability with WinArcadia
#             if symb.endswith(":"):
#                 symb = symb[:-1]
        if split_line[0] != False:        
            symbo = split_line[0]
            if symbo.endswith(":"):
                symbo = symbo[:-1]
            self.label = symbo
        
        # the instruction (ie loda,r0 needs subdividing)
        if split_line[1] != False:
            x = split_line[1].rsplit(",")
            self.mnemonic = x[0]
            if len(x) == 2:
                self.qualifier = x[1]
        # the operand comprises optional indirection, the core operand, optional indexing.    
        if split_line[2] != False:
            # store indirect symbol, and remove it from split_line
            if split_line[2][0] == "*":
                self.indirect = "*"
                split_line[2] = split_line[2][1:]
            # seperate operand and optional indexing
            if len(split_line[2]) != 0:
                x = split_line[2].rsplit(",")
                self.operand = x[0]
                if len(x) == 3:
                    x[1] += x[2]  # convert "r1,+"  to "r1+"
                if len(x) >= 2:
                    self.index = x[1]
                    
                    
    def r0123(self, phrase):
        if phrase not in ("r0","r1","r2","r3"):
            if phrase == False: phrase = ""
            self.error = ("r0123", phrase)      
        else:
            reg_code = REGISTER_DICT[phrase]
            self.opcode1 += reg_code
            
    def r123(self, phrase):
        if phrase not in ("r1","r2","r3"):
            self.error = ("r123", phrase)      
        else:
            reg_code = REGISTER_DICT[phrase]
            self.opcode1 += reg_code
    
    def indir(self, phrase):
        if phrase == "*":
            self.opcode2 += 128
        
    def absolute(self, phrase):
        val, err = evaluate_to_decimal(phrase)
        if (err == True or val > MAX_WORD):
            self.error = ("word", phrase)
        else:  
            self.opcode2 += (val // 256)
            self.opcode3 = (val % 256)
            
    def abs_dir(self, phrase):
        '''Special case for org and equ'''
        val, err = evaluate_to_decimal(phrase)
        if (err == True or val > MAX_WORD):  
            self.error = ("word", phrase)

    def relative(self, phrase):
        val, err = evaluate_to_decimal(phrase)
        if (err == True):
            self.error = ("relative", phrase)
        else:
            offset = val - self.next_address
            if offset not in range(-64, 64):    # the 64 is not included in the range
                self.error = ("relative", phrase)
            #convert to two's complement
            if offset < 0: 
                offset = 128 - abs(offset)
            self.opcode2 += offset  
    
    def indx(self, phrase):
        '''Optional indexing field'''
        if phrase == False: return
        # Validate
        if phrase not in ("r0","r1","r2","r3","r0+","r1+","r2+","r3+","r0-","r1-","r2-","r3-"):
            self.error = ("indx", phrase)
            return
        # Check that r1,r2,r3 not appended to the mnemonic
        if self.qualifier not in ("r0", False):
            phrase = self.qualifier
            self.error = ("indxq", phrase)
            return
        # Allow qualifier to be blank for indexed instrucion
        # Will have been marked as bad by r0123
        if self.qualifier == False:
            if self.error[0] == "r0123":
                self.error = (False, False)
        # Code the indexing instruction
        if len(phrase) == 2:
            # Indexed only
            x = 96 # $60
        else:
            if phrase[2] == "+":
                x = 32  # $20
            else: x = 64  # $40
            phrase = phrase[0:2]
        # Add the auto increment/decrement
        self.opcode2 += x
        # Add the register code
        reg_code = REGISTER_DICT[phrase]
        self.opcode1 += reg_code
    
    def value(self, phrase):
        val, err = evaluate_to_decimal(phrase)
        if (err == True or val > 255):
            self.error = ("value", phrase)
        else: self.opcode2 = val
    
    def blank(self, phrase):
        if phrase != False:
            self.error = ("not_expecting", phrase)
            
    def eq_gt_lt(self, phrase):
        if phrase not in ("eq","gt","lt","a1","s0", "z", "n", "p"):
            self.error = ("cond5", phrase)      
        else:
            cond_code = CONDITION_DICT[phrase]
            self.opcode1 += cond_code
            
    def eq_gt_lt_un(self, phrase):
        if phrase not in ("eq","gt","lt","a1","s0", "z", "n", "p","un"):
            self.error = ("cond6", phrase)      
        else:
            cond_code = CONDITION_DICT[phrase]
            self.opcode1 += cond_code
            
    def directive2(self, phrase):
        pass
    
    def r3(self, phrase):
        '''Checks index register for bsxa and bxa'''
        if phrase != "r3":
            self.error = ("r3", phrase)      

    def lodz(self, phrase):
        '''Special case for lodz r0'''
        if phrase not in ("r0","r1","r2","r3"):
            if phrase == False: phrase = ""
            self.error = ("r0123", phrase)      
        else:
            if phrase == "r0":
                self.opcode1 = 96
            else:
                reg_code = REGISTER_DICT[phrase]
                self.opcode1 += reg_code        
        
    def r0(self, phrase):
        if phrase not in ("r0", False):
            self.error = ("r0", phrase)        

    def byte(self, phrase):
        val, err = evaluate_to_decimal(phrase)
        if (err == True or val > 255):
            self.error = ("value", phrase)
        else:
            self.opcode1 = val      
         
    def word(self, phrase):
        val, err = evaluate_to_decimal(phrase)
        if (err == True or val > 65535):
            self.error = ("word", phrase)
        else:
            self.opcode1 = (val // 256)
            self.opcode2 = (val % 256)
                  
    def encode(self):
        '''Dictionary of functions'''
        # Note: this cannot be moved to constants since the functions aren't defined in that scope
        FORMAT_DICT = {
            "R":self.r0123,
            "r":self.r123,
            "*":self.indir,
            "A":self.absolute,
            "o":self.abs_dir,
            "a":self.relative,
            "X":self.indx,
            "V":self.value,
            " ":self.blank,
            "c":self.eq_gt_lt,
            "C":self.eq_gt_lt_un,
            "D":self.directive2,
            "3":self.r3,
            "Z":self.lodz,
            "0":self.r0,
            "b":self.byte,
            "w":self.word
        }
        if self.mnemonic != False:
            # Get the opcode for this mnemonic, unless
            # this is an equ or org 
            x = OPCODE_DICT[self.mnemonic][OPCODE]
            if x != "X":
                self.opcode1 = x
            # Get the format expected for this mnemonic
            form = OPCODE_DICT[self.mnemonic][STRUCTURE]
            # Using the nth character in 'form',
            # look up the appropriate function to call
            # and pass relevant phrase to it:
            
            # Handle any qualifier
            FORMAT_DICT[form[0]](self.qualifier)
            # handle indirect symbol *
            FORMAT_DICT[form[1]](self.indirect)
            # handle core operand
            FORMAT_DICT[form[2]](self.operand)
            # handle indexing
            FORMAT_DICT[form[3]](self.index)

            
def assemble_file(filename, user):
    ''' Attempts to assemble 'filename' and returns a 'report' to print on the screen,
        a boolean to indicate success or failure, a list of 'machine_code' bytes, and
        a string with the assembly listing.
    '''
    # initialise top level variables
    global symbol_table
    symbol_table.clear()
    list_of_lines = []
    address = 0
    error_count = 0
    # Initialise the report that will appear on the screen after assembly
    report = ""
    report += "\n_______________________________________________________________\n"
    # Check that the file exists
    file_exists = exists(filename)
    if file_exists == False:
        report += "Cannot find " + filename + '\n'
        return report, False

    # Transfer file to a list of objects of class Line
    with open(filename,"rt") as file: 
        for line in file:
            this_line = Line(line)
            list_of_lines.append(this_line)
          
    report += "Assembling " + filename + '\n\n'
    # PASS 1
    # Process one Line at a time. All information about the line of code
    # is held within the object of class Line
    for this_line in list_of_lines:
        # Interpret line and place fragments in appropriate variable in Line
        Line.fragment(this_line)
        # Determine space needed and evaluate any symbols 
        Line.allocate_space(this_line, address)
        address = Line.get_next_address(this_line)
        symb, value = Line.get_symbol(this_line)
        if symb != False:
#             # strip any terminating colon for
#             # compatability with WinArcadia
#             if symb.endswith(":"):
#                 symb = symb[:-1]
#            if symb in symbol_table.keys():
#                 report += "Label " {} " is defined twice."
#                 error_count += 1
                
            if symb == "switch_player" :  ###############################################################
                print(symb, "updating sym tab")               ###############################################################
                Line.printline(this_line) ###############################################################

            symbol_table.update({symb:value})
        # Report any error
        err_bool, err_msg = Line.error_reporter(this_line)
        if err_bool != False:
            report += err_msg
            error_count += 1
#         Line.printline(this_line)
#         print(symbol_table)
#         print(" ")
    if error_count != 0:
        if error_count == 1:
            report += "Pass 1 failed. There was " + str(error_count) + " error" + '\n'
        else:
            report += "Pass 1 failed. There were " + str(error_count) + " errors" + '\n'
        report += "Assembly terminated" + '\n'
        return report, False
    
    # PASS 2
    for this_line in list_of_lines:
        # Analyse Line and determine the three opcodes
        Line.encode(this_line)
        # Report any error
        err_bool, err_msg = Line.error_reporter(this_line)
        if err_bool != False:
            report += err_msg
            error_count += 1
    if error_count != 0:
        if error_count == 1:
            report += "Pass 2 failed. There was " + str(error_count) + " error" + '\n'
        else:
            report += "Pass 2 failed. There were " + str(error_count) + " errors" + '\n'
        report += "Assembly terminated" + '\n'
        return report, False
    else:
        report += "      Assembly completed successfully!" + '\n\n'
        # Create the .lst and .bin files
        machine_code = []
        list_text = ""
        x = datetime.datetime.now()
        time = x.strftime("%I:%M %p, %A, %d %B %Y")
        list_text += "Assembled by Pi2650 for " + user + " at " + time + '\n\n'
        
        for this_line in list_of_lines:
            x = Line.format_lst(this_line)
            list_text += x
            code_list = Line.extract_code(this_line)
            for code in code_list:
                machine_code.append(code)
                
        trunc_filename = filename[:-3]
        x = trunc_filename + "bin"
        with open(x, 'bw') as file:
            file.write(bytes(machine_code))
        report += "Binary file ready to dump at :  " + x + '\n'
        x = trunc_filename + "lst"            
        with open(x, 'tw') as file:
            file.write(list_text)
        report += "List file ready to view at :  " + x + '\n'
        return report, True 

