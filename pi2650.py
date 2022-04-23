"""Development system for the Voltmace Database Games Computer and related consoles"""

# standard python modules
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import simpledialog
import json
import os.path
from shutil import copyfile

# pi2650 modules
from assembler import *
from constants import *
from interface import *

VERSION = "0.104"


init_interface()  # disable interface until it is needed

def update_prefs(p, k, v):
    ''' update item in both the local preferences and the json file  '''
    p[k] = v
    with open("preferences_file.json", "w") as write_file:
        json.dump(p, write_file)   #this was prefs
    return p

def add_to_recent(p, k, v):
    ''' add file path to list of recent files '''
    ''' p=prefs dict, k=recent_asm or recent_bin, v=new pathname to add'''
    recents = p.get(k)       # get list of bin or asm recents
    if v in recents:         # delete pathname if already in list 
        recents.remove(v) 
    recents.insert(0, v)     # add new pathname to top of list
    if len(recents) == 11:
        recents.pop(10)      # restrict to 10 items in list
    p = update_prefs(p, k, recents)   # update local and JSON
    return p

def init_prefs():
    '''Initialise the user preferences'''
    # Attempt to load preferences from file
    try:
        with open("preferences_file.json", "r") as read_file:
            p = json.load(read_file)
    # If there is no file, create one
    except FileNotFoundError:
        username = simpledialog.askstring("Input", "What is your name?", parent=root)
        p = INITIAL_PREFS
        p = update_prefs(p, "user_name", username) 
        with open("preferences_file.json", "w") as write_file:
            json.dump(p, write_file)
    # If there is a file, check that it has all the same fields
    # as in this current version of software
    else:
        copyjsonfile =  p.copy()
        jkeys = copyjsonfile.keys()
        ikeys = INITIAL_PREFS.keys()
        # If a key is no longer used, delete it.
        for key in jkeys:
            if key not in ikeys:
                p.pop(key)
        # If a key is new, add it.
        for key in ikeys:
            if key not in jkeys:
                p.update({key: INITIAL_PREFS[key]})
        with open("preferences_file.json", "w") as write_file:
            json.dump(p, write_file)
    return p

def open2view(file_path):
    if not file_path:
        return
    view_space.config(state="normal")
    view_space.delete(1.0, tk.END)
    with open(file_path, "r") as input_file:
        text = input_file.read()
        view_space.insert(tk.END, text)       
        update_prefs(prefs, "current_view", file_path)
        add_to_recent(prefs, "recent_view", file_path)
        viewing_frame.configure(text = file_path)     
    view_space.config(state="disabled")  
        

class TabFrame(ttk.Frame):  
    """a frame used in each tab of the root """
    def __init__(self, notebook, text):
        ttk.Frame.__init__(self, notebook)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1) 
        notebook.add(self, text= text)

def display_help_file(help_request):    
    help_message.config(state="normal")
    help_message.delete('1.0', tk.END)
#    help_path = f"help_files/{help_request}.txt"
    help_path = f"{help_request}.txt"
    with open(help_path,"rt") as file: 
        help_message_text = file.read()
    help_message.insert('1.0', help_message_text)
    help_message.config(state="disabled")


def get_and_display_help(event):
    help_request = help_topics.get()
    help_request = help_request.lower()
    display_help_file(help_request)
 
###########################################################################

root = tk.Tk()
current_asm_label = tk.StringVar()
current_bin_label = tk.StringVar()


# configure root
#root.option_add('*Font', '24')
root.title('Pi2650')
root.geometry('800x700+450+35')
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
root.configure(bg='#888')
root.lift()

workbench = ttk.Notebook(root)
workbench.grid(sticky='nesw', padx=5, pady=5)

prefs = init_prefs()
current_asm_label.set(prefs.get("current_asm"))
current_bin_label.set(prefs.get("current_bin"))


# Create sub-frame for each tab
edit_tab = TabFrame(workbench, ' EDIT   '   )
assemble_tab = TabFrame(workbench, ' ASSEMBLE   '   )
dump_tab = TabFrame(workbench, ' DUMP   '   )
view_tab = TabFrame(workbench, ' VIEW .LST   '   )
# debug_tab = TabFrame(workbench, ' DEBUG   '   )
# utilities_tab = TabFrame(workbench, ' UTILITIES   '   )
settings_tab = TabFrame(workbench, ' SETTINGS   '   )
help_tab = TabFrame(workbench, ' HELP   '   )






################### Contents of EDIT tab  #####################################
edit_frame = ttk.Frame(edit_tab)
edit_frame.grid(sticky='ewns')
edit_frame.columnconfigure(0, weight=1)
edit_frame.columnconfigure(1, weight=1)
edit_frame.columnconfigure(2, weight=1)
edit_frame.columnconfigure(3, weight=1)
edit_frame.columnconfigure(4, weight=1)
edit_frame.rowconfigure(10, weight=0)
edit_frame.rowconfigure(20, weight=0)
edit_frame.rowconfigure(30, weight=0)
edit_frame.rowconfigure(39, weight=0)
edit_frame.rowconfigure(40, weight=1)


def open2edit(file_path):
    if not file_path:
        return
    editing_space.delete(1.0, tk.END)
    with open(file_path, "r") as input_file:
        text = input_file.read()
        editing_space.insert(tk.END, text)       
        update_prefs(prefs, "current_edit", file_path)
        editing_frame.configure(text = file_path)
    
def find_new_edit_file():
    file_path = filedialog.askopenfilename(title="Select file to edit", initialdir=prefs.get("def_asm_dir"),
                                           filetypes=[("asm files", "*.asm")]) 
    if not file_path:
        return
    open2edit(file_path)
    
def save_edit_file():
    file_path = prefs.get("current_edit")
    if not file_path:
        save_as_edit_file()
    else:
        with open(file_path, "w") as output_file:
            text = editing_space.get(1.0, tk.END)
            output_file.write(text)
        update_prefs(prefs, "current_edit", file_path)
        add_to_recent(prefs, "recent_edit", file_path)
        editing_frame.configure(text = file_path)
        
        update_prefs(prefs, "current_asm", file_path)
        current_asm_label.set(file_path)
        # maybe put in a pop-up dialog box to confirm that the save was done

def save_as_edit_file():
    """Save the current file as a new file."""
    file_path = filedialog.asksaveasfilename(title="Save file as..", initialdir=prefs.get("def_asm_dir"),
                                  defaultextension=".asm", filetypes=[("Assembler Files", "*.asm")])
    if not file_path:
        return
    with open(file_path, "w") as output_file:
        text = editing_space.get(1.0, tk.END)
        output_file.write(text)
    update_prefs(prefs, "current_edit", file_path)
    add_to_recent(prefs, "recent_edit", file_path)
    editing_frame.configure(text = file_path)
    # maybe put in a pop-up dialog box to confirm that the save was done

def new_edit_file():
    editing_space.delete(1.0, tk.END)
    file_path = ""
    update_prefs(prefs, "current_edit", file_path)
    editing_frame.configure(text = file_path)
    
def hotkey_info():
    tk.messagebox.showinfo(
    title = "Editor HotKeys",
    message = "Ctrl+X\t- Cut\n"\
              "Ctrl+C\t- Copy\n"\
              "Ctrl+V\t- Paste\n"\
              "Ctrl+F\t- Find\n"\
              "Ctrl+Z\t- Undo\n"\
              "Ctrl+Y\t- Redo\n"\
              "Ctrl+>\t- Comment\n"\
              "Ctrl+<\t- UnComment"\
    )
        

open_edit_file_button = tk.Button(edit_frame, text='Open', bg='#CCC')
open_edit_file_button.grid(row=10, column=0, sticky='ew', padx=5, pady=5)
open_edit_file_button.configure(command=find_new_edit_file)

save_edit_file_button = tk.Button(edit_frame, text='Save', bg='#CCC')
save_edit_file_button.grid(row=10, column=1, sticky='ew', padx=5, pady=5)
save_edit_file_button.configure(command=save_edit_file)

save_as_edit_file_button = tk.Button(edit_frame, text='Save As', bg='#CCC')
save_as_edit_file_button.grid(row=10, column=2, sticky='ew',  padx=5, pady=5)
save_as_edit_file_button.configure(command=save_as_edit_file)

new_edit_file_button = tk.Button(edit_frame, text='New', bg='#CCC')
new_edit_file_button.grid(row=10, column=3, sticky='ew',  padx=5, pady=5)
new_edit_file_button.configure(command=new_edit_file)

hotkey_info_button = tk.Button(edit_frame, text='Hotkeys', bg='#CCC')
hotkey_info_button.grid(row=10, column=4, sticky='ew',  padx=5, pady=5)
hotkey_info_button.configure(command=hotkey_info)

ttk.Label(edit_frame, text='Recent files: '
          ).grid(sticky='e', row=20, column=0, padx=5, pady=2)



def update_recently_edited_menu():
    '''when user clicks arrow, the updated list is displayed'''
    recently_edited_menu["value"] = prefs.get("recent_edit")
    
def use_recent_edit(event):
    recent = recently_edited_menu.get()
    if recent != '':
        update_prefs(prefs, "current_edit", recent)
        open2edit(recent)


edit_file = tk.StringVar()
recently_edited_files = prefs.get("recent_edit")
recently_edited_menu = ttk.Combobox(edit_frame, 
                           value=recently_edited_files,
                           textvariable=edit_file,
                           state='readonly',
                           postcommand=update_recently_edited_menu    
                           )
recently_edited_menu.grid(row=20, column=1, columnspan=4, sticky='sew', padx=5, pady=5)
if len(recently_edited_files) > 0:
    recently_edited_menu.current(0)
recently_edited_menu.bind("<<ComboboxSelected>>", use_recent_edit)

editing_frame = ttk.LabelFrame(edit_frame, text = prefs.get("current_edit"))
editing_frame.grid(row=40, columnspan=5, pady=5, sticky='ewns')
editing_frame.columnconfigure(0, weight=1)

editing_space = tk.Text(editing_frame, height = prefs.get("edit_height"), undo=True)  #
editing_space.config(wrap='none')
editing_space.grid(sticky='ewns')
editing_space.configure(font=("", (prefs.get("text_size")) ) )

edit_scrollbar = ttk.Scrollbar(editing_frame)
edit_scrollbar.grid(row=0, column=1, sticky='nes')
edit_scrollbar.configure(command=editing_space.yview)
editing_space.configure(yscrollcommand=edit_scrollbar.set)

edit_scrollbarH = ttk.Scrollbar(editing_frame, orient='horizontal')
edit_scrollbarH.grid(row=1, column=0, sticky='ews')
edit_scrollbarH.configure(command=editing_space.xview)
editing_space.configure(xscrollcommand=edit_scrollbarH.set)

# Select all the text in editing_space
def select_all(event):
    editing_space.tag_add(tk.SEL, "1.0", tk.END)
    editing_space.mark_set(tk.INSERT, "1.0")
    editing_space.see(tk.INSERT)
    return 'break'

def comment_out(event):
    '''Inserts a ';' at the start of every line selected'''
    #get the start and end indices of selected text
    try:
        start = editing_space.index("sel.first")
        end = editing_space.index("sel.last")
    except:
        tk.messagebox.showerror(title = "You can't do that",
                               message = "Select some text first")
        return 'break'
    # how many lines selected
    lines = len(editing_space.get(start, end).split('\n'))
    # get first line
    line = start.split('.')[0]
    # add ";" to start of each line
    for idx in range(lines):
        editing_space.insert('{}.0'.format(line), ";")
        line = str(int(line) + 1)
    return 'break'

def uncomment(event):
    '''If there is one, remove a ';' at the start of every line selected'''
    #get the start and end indices of selected text
    try:
        start = editing_space.index("sel.first")
        end = editing_space.index("sel.last")
    except:
        tk.messagebox.showerror(title = "You can't do that",
                               message = "Select some text first")
        return 'break'
    # how many lines selected
    lines = len(editing_space.get(start, end).split('\n'))
    # get first line
    line = start.split('.')[0]
    # remove ";" to start of each line
    for idx in range(lines):
        if editing_space.get('{}.0'.format(line)) == ";":
            editing_space.delete('{}.0'.format(line))
        line = str(int(line) + 1)
    return 'break'   

def popup_find(event):
    editing_space.tag_delete("search")
    editing_space.tag_configure("search", background="yellow")
    find_str = tk.simpledialog.askstring('Pi2650', 'Find:')
    if find_str is not None:
        r, c = editing_space.index( 'insert' ).split( '.' )
        countVar = tk.StringVar()
        pos = editing_space.search(find_str, f"{r}.{c}", stopindex="end", count=countVar, nocase=1 )
        if not pos:return
        ending_index = "{}+{}c".format(pos, countVar.get())  # i.e. 11.41+5c
        editing_space.tag_add("search", pos, ending_index)
     #   print(pos)
    #    editing_space.see(pos)
        editing_space.mark_set("insert", ending_index)
    #    root.update_idletasks()
    editing_space.focus()


# Bind Ctrl keys to functions
editing_space.bind("<Control-Key-a>", select_all)
editing_space.bind("<Control-Key-A>", select_all) # just in case caps lock is on
editing_space.bind("<Control-Key-f>", popup_find)
editing_space.bind("<Control-Key-F>", popup_find)
editing_space.bind("<Control-Key-period>", comment_out)  # '>' - inserts ';' at start of all selected lines
editing_space.bind("<Control-Key-comma>", uncomment)     # '<' - removes ';' from start of all selected lines

open2edit(prefs.get("current_edit"))


#################### Contents of VIEW tab #####################################


view_frame = ttk.Frame(view_tab)
view_frame.grid(sticky='ewns')
view_frame.columnconfigure(0, weight=1)
view_frame.columnconfigure(1, weight=1)
view_frame.columnconfigure(2, weight=1)
view_frame.columnconfigure(3, weight=1)
view_frame.columnconfigure(4, weight=1)
view_frame.rowconfigure(10, weight=0)
view_frame.rowconfigure(20, weight=0)
view_frame.rowconfigure(30, weight=0)
view_frame.rowconfigure(39, weight=0)
view_frame.rowconfigure(40, weight=1)
      
    
def find_new_view_file():
    file_path = filedialog.askopenfilename(title="Select file to view", initialdir=prefs.get("def_asm_dir"),
                                           filetypes=[("lst files", "*.lst"),("asm files", "*.asm")]) 
    if not file_path:
        return
    open2view(file_path)
    

# def new_edit_file():
#     view_space.delete(1.0, tk.END)
#     file_path = ""
#     update_prefs(prefs, "current_edit", file_path)
#     viewing_frame.configure(text = file_path)
    
        

open_view_file_button = tk.Button(view_frame, text='Open', bg='#CCC')
open_view_file_button.grid(row=10, column=0, sticky='ew', padx=5, pady=5)
open_view_file_button.configure(command=find_new_view_file)

# new_edit_file_button = tk.Button(view_frame, text='New', bg='#CCC')
# new_edit_file_button.grid(row=10, column=3, sticky='ew',  padx=5, pady=5)
# new_edit_file_button.configure(command=new_edit_file)

ttk.Label(view_frame, text='Recent files: '
          ).grid(sticky='e', row=20, column=0, padx=5, pady=2)

def update_recently_viewed_menu():
    '''when user clicks arrow, the updated list is displayed'''
    recently_viewed_menu["value"] = prefs.get("recent_view")
    
def use_recent_view(event):
    recent = recently_viewed_menu.get()
    if recent != '':
        update_prefs(prefs, "current_view", recent)
        open2view(recent)


view_file = tk.StringVar()
recently_viewed_files = prefs.get("recent_view")
recently_viewed_menu = ttk.Combobox(view_frame, 
                           value=recently_viewed_files,
                           textvariable=view_file,
                           state='readonly',
                           postcommand=update_recently_viewed_menu    
                           )
recently_viewed_menu.grid(row=20, column=1, columnspan=4, sticky='sew', padx=5, pady=5)
if len(recently_viewed_files) > 0:
    recently_viewed_menu.current(0)
recently_viewed_menu.bind("<<ComboboxSelected>>", use_recent_view)

viewing_frame = ttk.LabelFrame(view_frame, text = prefs.get("current_view"))
viewing_frame.grid(row=40, columnspan=5, pady=5, sticky='ewns')
viewing_frame.columnconfigure(0, weight=1)

view_space = tk.Text(viewing_frame, height=prefs.get("view_height"), undo=True)
view_space.config(wrap='none')
view_space.grid(sticky='ewns')
#view_space.configure(font='TkFixedFont' + str(prefs.get("text_size")) ) 
view_space.configure(font=("", (prefs.get("text_size")) ) )
#view_space.configure(font='TkFixedFont')


view_scrollbar = ttk.Scrollbar(viewing_frame)
view_scrollbar.grid(row=0, column=1, sticky='nes')
view_scrollbar.configure(command=view_space.yview)
view_space.configure(yscrollcommand=view_scrollbar.set)

view_scrollbarH = ttk.Scrollbar(viewing_frame, orient='horizontal')
view_scrollbarH.grid(row=1, column=0, sticky='ews')
view_scrollbarH.configure(command=view_space.xview)
view_space.configure(xscrollcommand=view_scrollbarH.set)

open2view(prefs.get("current_view"))





######################### Contents of ASSEMBLE tab  ###############################
assemble_frame = ttk.Frame(assemble_tab)
assemble_frame.grid(sticky='ewns')
assemble_frame.columnconfigure(0, weight=1)
assemble_frame.columnconfigure(1, weight=1)
assemble_frame.columnconfigure(2, weight=0)
assemble_frame.rowconfigure(5, weight=1)
assemble_frame.rowconfigure(6, weight=1)
assemble_frame.rowconfigure(20, weight=2)

current_file_frame = ttk.LabelFrame(assemble_frame, text='Current file')
current_file_frame.grid(row=5, column=0, padx=5, pady=5, sticky='nwe')
current_file_frame.columnconfigure(0, weight=1)
select_file_frame = ttk.LabelFrame(assemble_frame, text='Select another file')
select_file_frame.grid(row=6, column=0, padx=5, pady=5, sticky='nwe')
select_file_frame.columnconfigure(0, weight=0)
select_file_frame.columnconfigure(1, weight=1)
assemble_options_frame = ttk.LabelFrame(assemble_frame, text='Options')
assemble_options_frame.grid(row=5,  column=2, padx=5, pady=5, sticky='e')

assemble_message_frame = ttk.LabelFrame(assemble_frame, text='Assembler progress')
assemble_message_frame.grid(row=30, columnspan=3, pady=10, sticky='ewn')
assemble_message_frame.columnconfigure(0, weight=1)


assemble_message = tk.Text(assemble_message_frame, height=prefs.get("assemble_height"))
# NOTE the tk.Text widget is not designed to resize itself to fill
# available space. It's height setting, in lines, has been chosen to maximise
# space in the text widget within the root dimensions, and with the current
# font size.
assemble_message.config(wrap=tk.WORD)
assemble_message.configure(font=(" ", (prefs.get("text_size")) ) )
assemble_message.grid(sticky='ewns')
assemble_message.config(state="normal")   ####################################

assemble_scrollbar = ttk.Scrollbar(assemble_message_frame)
assemble_scrollbar.grid(row=0, column=1, sticky='nes')
assemble_scrollbar.configure(command=assemble_message.yview)
assemble_message.configure(yscrollcommand=assemble_scrollbar.set)

ttk.Label(current_file_frame, textvariable=current_asm_label
          ).grid(sticky='w', row=0, column=0, padx=5, pady=5)


def assemble(p):
    def time_stamp():
        assemble_message.config(state="normal")
        x = datetime.datetime.now()
        time = x.strftime("%I:%M %p, %A, %d %B %Y")
        assemble_message.insert("end", time )
        assemble_message.insert("end", "\n\n" )
        assemble_message.see('end')  
        assemble_message.config(state="normal")      
        
    file2assemble = p.get("current_asm")
    add_to_recent(p, "recent_asm", file2assemble)
    user = p.get("user_name")
    report, success = assemble_file(file2assemble, user)
    if success:
        # set binary file as current in dump tab
        bin_filename = file2assemble[:-3] + "bin"
        p.update({"current_bin": bin_filename})
        current_bin_label.set(bin_filename)
        # set list file as current in view tab and open it
        list_filename = file2assemble[:-3] + "lst"
        p.update({"current_view": list_filename})
        open2view(list_filename)
        # optionally archive the assembler file
        # saves directory/game.asm in directory/archive/game_XXXX.asm
        if p.get("auto_archive"):     
            serial = p.get("archive_serial") + 1
            update_prefs(prefs, "archive_serial", serial)
            asm_filename = os.path.split(file2assemble)[1]
            s = asm_filename.split(".")
            archive_filename = s[0] + "_" + str(serial) + "." + s[1]
            asm_dir = os.path.dirname(file2assemble)
            archive_dir = os.path.join(asm_dir, "archive")
            if not os.path.exists(archive_dir):
                os.mkdir(archive_dir)
            archive_path = os.path.join(archive_dir, archive_filename)
            copyfile(file2assemble, archive_path)
            report += "Assembler file has been archived at : " + archive_path + '\n'
    # Display the report
    assemble_message.config(state="normal")
    assemble_message.insert("end", report )
    assemble_message.see('end')  
#    assemble_message.config(state="disabled")
    # Display timestamp after short delay (this helps indicate that something has happened)
    assemble_message.after(500, time_stamp)

    
assemble_button = tk.Button(current_file_frame, text='RUN \n ASSEMBLER', command=lambda:assemble(prefs), bg='#099B25')
assemble_button.grid(row=0, column=1, padx=5, pady=5, sticky="e")


def find_new_asm_file():
#    print(prefs.get("def_asm_dir"))
    file_path = filedialog.askopenfilename(title="select .asm file", initialdir=prefs.get("def_asm_dir"),
                                           filetypes=[("asm files", "*.asm")]) 
    if file_path != '':
        current_asm_label.set(file_path)
        update_prefs(prefs, "current_asm", file_path)
        



find_new_asm_file_button = tk.Button(select_file_frame, text='Open', bg='#CCC')
find_new_asm_file_button.grid(row=0, column=0, rowspan=2, sticky='sw', padx=2, pady=2)
find_new_asm_file_button.configure(command=find_new_asm_file)

ttk.Label(select_file_frame, text='Recent file: '
          ).grid(sticky='s', row=0, column=1, padx=5)

def update_recently_asm_menu():
    '''when user clicks arrow, the updated list is displayed'''
    recently_assembled_menu["value"] = prefs.get("recent_asm")
    
def use_recent_asm(event):
    recent = recently_assembled_menu.get()
    if recent != '':
        current_asm_label.set(recent)
        update_prefs(prefs, "current_asm", recent)


assembly_file = tk.StringVar()
recently_assembled_files = prefs.get("recent_asm")
recently_assembled_menu = ttk.Combobox(select_file_frame, 
                           value=recently_assembled_files,
                           textvariable=assembly_file,
                           state='readonly',
                           postcommand=update_recently_asm_menu    
                           )
recently_assembled_menu.grid(row=1, column=1, sticky='sew', padx=5, pady=4)
if len(recently_assembled_files) > 0:
    recently_assembled_menu.current(0)
recently_assembled_menu.bind("<<ComboboxSelected>>", use_recent_asm)


def clear_asm_window():
    assemble_message.config(state="normal")
    assemble_message.delete('1.0', "end")
    assemble_message.see('end')
#    assemble_message.config(state="disabled")   ##########################################

clear_asm_window_button = tk.Button(assemble_frame, text='Clear \n window',
                        command=lambda:clear_asm_window(), bg='#CCC')
clear_asm_window_button.grid(row=6, column=2, padx=10, sticky="es")


######## Contents of DUMP tab   #####################################

dump_frame = ttk.Frame(dump_tab)
dump_frame.grid(sticky='ewns')
dump_frame.columnconfigure(0, weight=1)
dump_frame.columnconfigure(1, weight=1)
dump_frame.columnconfigure(2, weight=0)
dump_frame.rowconfigure(5, weight=0)
dump_frame.rowconfigure(6, weight=0)
dump_frame.rowconfigure(20, weight=1)
current_dump_file_frame = ttk.LabelFrame(dump_frame, text='Current file')
current_dump_file_frame.grid(row=5, column=0, padx=5, pady=5, ipadx=3, ipady=3, sticky='nswe')
current_dump_file_frame.columnconfigure(0, weight=1)
select_bin_file_frame = ttk.LabelFrame(dump_frame, text='Select another file')
select_bin_file_frame.grid(row=6, column=0, padx=5, pady=5, sticky='nswe')
select_bin_file_frame.columnconfigure(0, weight=1)
select_bin_file_frame.columnconfigure(1, weight=1)
dump_message_frame = ttk.LabelFrame(dump_frame, text='Dump progress')
dump_message_frame.grid(row=20, columnspan=3, padx=5, pady=5, sticky='ewns')
dump_message_frame.columnconfigure(0, weight=1)
dump_message = tk.Text(dump_message_frame, height=prefs.get("dump_height"))  
# NOTE the tk.Text widget is not designed to resize itself to fill
# available space. It's height setting, in lines, has been chosen to maximise
# space in the text widget within the root dimensions, and with the current
# font size.

dump_message.configure(font=(" ", (prefs.get("text_size")) ) )
dump_message.config(wrap=tk.WORD)
dump_message.grid(sticky='news')
dump_message.config(state="disabled") 
dump_scrollbar = ttk.Scrollbar(dump_message_frame)
dump_scrollbar.grid(row=0, column=1, sticky='nes')
dump_scrollbar.configure(command=dump_message.yview)
dump_message.configure(yscrollcommand=dump_scrollbar.set)

ttk.Label(current_dump_file_frame, textvariable=current_bin_label
          ).grid(sticky='w', row=0, column=0, padx=5, pady=5)

def dump(p):
    '''Dump contents of current_bin to the console'''
    file2dump = p.get("current_bin")
    dump_message.config(state="normal")
    dump_message.insert("end", "\n_______________________________________________________________\n")
    #Check file exists
    file_exists = exists(file2dump)
    if file_exists == False:
        dump_message.insert("end", "Cannot find " + file2dump + '\n')
        return   
    add_to_recent(p, "recent_bin", file2dump)
    dump_message.insert("end", "Dumping " + file2dump + ' to console.\n')
    dump_message.insert("end", 'Please wait.....\n')
    dump_message.see('end')
    root.update_idletasks()
    # Read file and create list of bytes
    with open(file2dump,"rb") as file: 
        file_data = file.read()
    binary = []
    count = 0 ###
    for file_byte in file_data:
        binary.append(file_byte)
        count += 1  ###
    while count != 4096:  # fill rest of memory with HALT instructions
        binary.append(64)
        count += 1
    output(binary)
    dump_message.config(state="normal")
    dump_message.insert("end", 'Dump complete. \n')
    dump_message.insert("end", 'Press reset on console to start. \n\n')
    dump_message.see('end')
    dump_message.config(state="disabled")   
    

dump_button = tk.Button(current_dump_file_frame, text='DUMP \n TO CONSOLE',
                        command=lambda:dump(prefs), bg='#099B25')
dump_button.grid(row=0, column=1, padx=10, sticky="e")

def clear_dump_window():
    dump_message.config(state="normal")
    dump_message.delete('1.0', "end")
    dump_message.see('end')
    dump_message.config(state="disabled")   

clear_dump_window_button = tk.Button(dump_frame, text='Clear \n window',
                        command=lambda:clear_dump_window(), bg='#CCC')
clear_dump_window_button.grid(row=6, column=2, padx=10, sticky="es")


def find_new_bin_file():
    bin_file_path = filedialog.askopenfilename(title="select .bin file", initialdir=prefs.get("def_asm_dir"),
                                               filetypes=[("bin files", "*.bin")]) 
    if bin_file_path != '':
        current_bin_label.set(bin_file_path)
        update_prefs(prefs, "current_bin", bin_file_path)

find_new_bin_file_button = tk.Button(select_bin_file_frame, text='Open', bg='#CCC')
find_new_bin_file_button.grid(row=0, column=0, rowspan=2, sticky='sw', padx=0, pady=5)
find_new_bin_file_button.configure(command=find_new_bin_file)
ttk.Label(select_bin_file_frame, text='Recent file: '
          ).grid(sticky='s', row=0, column=1, padx=5, pady=5)


def update_recently_dumped_menu():
    '''post command for recently_dumped_menu combobox'''
    recently_dumped_menu["value"] = prefs.get("recent_bin")
    
    
def use_recent_bin(event):
    '''bind for recently_dumped_menu combobox'''
    recent = recently_dumped_menu.get()
    if recent != '':
        current_bin_label.set(recent)
        update_prefs(prefs, "current_bin", recent)


bin_file = tk.StringVar()
recently_dumped_files = prefs.get("recent_bin")
recently_dumped_menu = ttk.Combobox(select_bin_file_frame, 
                           value=recently_dumped_files,
                           textvariable=bin_file,
                           width=50,
                           state='readonly',
                           postcommand=update_recently_dumped_menu    
                           )
recently_dumped_menu.grid(row=1, column=1, sticky='se', padx=5, pady=5)
if len(recently_dumped_files) > 0:
    recently_dumped_menu.current(0)
recently_dumped_menu.bind("<<ComboboxSelected>>", use_recent_bin)












# ################### Contents of DEBUG tab #####################################
# debug_frame = ttk.Frame(debug_tab)
# debug_frame.columnconfigure(1, weight=1)
# debug_frame.grid(sticky='ew')
# ttk.Label(debug_frame, text='The debug feature is not yet implemented. '
#           ).grid(sticky='we', padx=5, pady=5)
# ttk.Label(debug_frame, text='It is going to require a lot more hardware. '
#           ).grid(sticky='we', padx=5, pady=5)
# ttk.Label(debug_frame, text='It may never happen. '
#           ).grid(sticky='we', padx=5, pady=5)
# 
# ################ Contents of UTILITIES tab #################################
# utilities_frame = ttk.Frame(utilities_tab)
# utilities_frame.columnconfigure(1, weight=1)
# utilities_frame.grid(sticky='ew')
# ttk.Label(utilities_frame, text='The utilities feature is not yet implemented. '
#           ).grid(sticky='we', padx=5, pady=5)
# ttk.Label(utilities_frame, text='*Compare two binary files '
#           ).grid(sticky='we', padx=5, pady=20)
# ttk.Label(utilities_frame, text='*Display binary file graphically to search for sprite decriptors '
#           ).grid(sticky='we', padx=5, pady=20)
# ttk.Label(utilities_frame, text='*draw a sprite '
#           ).grid(sticky='we', padx=5, pady=20)
# ttk.Label(utilities_frame, text='*Hex-Decimal-Binary converter '
#           ).grid(sticky='we', padx=5, pady=20)
#



#################### Contents of SETTINGS tab #####################################
settings_frame = ttk.Frame(settings_tab)
settings_frame.grid(sticky='ewns', pady=20)
settings_frame.columnconfigure(0, weight=0)
settings_frame.columnconfigure(1, weight=1)

def auto_archive_state():
    if (auto_archive_button.get() == 1):
        update_prefs(prefs, "auto_archive", True)
    else:
        update_prefs(prefs, "auto_archive", False)
        
auto_archive_button = tk.IntVar()
auto_archive_button.set(prefs.get("auto_archive"))
auto_archive = tk.Checkbutton(settings_frame, text='Auto-archive .asm files', highlightthickness=0,
                              variable=auto_archive_button, command=auto_archive_state)
auto_archive.grid(column=0, row=4, padx=5, pady=1,  sticky='w')
ttk.Label(settings_frame, text='Enables automatic archiving of .asm file. See HELP > File organization. ',
          foreground='blue' ).grid(column=1, row=4, sticky='we', padx=5, pady=1)

def set_default_asm_dir():
    ini_dir = ""  
    if prefs.get("def_asm_dir") != "":
        ini_dir = prefs.get("def_asm_dir")
    def_asm_dir = filedialog.askdirectory(title="Set a default directory for the Open function", initialdir=ini_dir) 
    if def_asm_dir != "":
        update_prefs(prefs, "def_asm_dir", def_asm_dir)
        
default_asm_dir_button = tk.Button(settings_frame, text='Set default directory', bg='#CCC')
default_asm_dir_button.grid(row=50, column=0, sticky='ew', padx=2, pady=20)
default_asm_dir_button.configure(command=set_default_asm_dir)
ttk.Label(settings_frame, text='Set a default directory for all "Open" buttons',
          foreground='blue' ).grid(column=1, row=50, sticky='w', padx=5, pady=1)

ttk.Separator(settings_frame, orient='horizontal').grid(row =100, column=0, columnspan=2, sticky='ew')

ttk.Label(settings_frame, text='Set text size before adjusting box heights:',
          foreground='grey36' ).grid(column=1, row=120, sticky='w', padx=5, pady=1)



def set_text_size():
    x = text_size_value.get()
    update_prefs(prefs, "text_size", x)
    dump_message.config(font = ("", x))
    assemble_message.config(font = ("", x))
    editing_space.config(font = ("", x))
    view_space.config(font = ("", x))
    
    
text_size_value = tk.IntVar()
text_size_value.set(prefs.get("text_size"))
text_font_box = ttk.Spinbox(settings_frame, from_=8, to=32, increment=1, textvariable=text_size_value,
                          command=set_text_size, width = 3, wrap=True)
text_font_box.grid(row=130, column=0, sticky='e', padx=2, pady=5)
ttk.Label(settings_frame, text='Text size, pt',
          foreground='blue' ).grid(column=1, row=130, sticky='w', padx=5, pady=1)

    
ttk.Label(settings_frame, text='Set height of various text boxes (number of lines):',
          foreground='grey36' ).grid(column=1, row=140, sticky='w', padx=5, pady=1)

def save_edit_height():
    x = edit_height_value.get()
    update_prefs(prefs, "edit_height", x)
    editing_space.config(height = x)
    
edit_height_value = tk.IntVar()
edit_height_value.set(prefs.get("edit_height"))
edit_height = ttk.Spinbox(settings_frame, from_=14, to=76, increment=2, textvariable=edit_height_value,
                          command=save_edit_height, width = 3, wrap=True)
edit_height.grid(row=150, column=0, sticky='e', padx=2, pady=5)
ttk.Label(settings_frame, text='EDIT text box height',
          foreground='blue' ).grid(column=1, row=150, sticky='w', padx=5, pady=1)


def save_assemble_height():
    x = assemble_height_value.get()
    update_prefs(prefs, "assemble_height", x)
    assemble_message.config(height = x)
    
assemble_height_value = tk.IntVar()
assemble_height_value.set(prefs.get("assemble_height"))
assemble_height = ttk.Spinbox(settings_frame, from_=14, to=76, increment=2, textvariable=assemble_height_value,
                          command=save_assemble_height, width = 3, wrap=True)
assemble_height.grid(row=153, column=0, sticky='e', padx=2, pady=5)
ttk.Label(settings_frame, text='ASSEMBLE text box height',
          foreground='blue' ).grid(column=1, row=153, sticky='w', padx=5, pady=1)

def save_dump_height():
    x = dump_height_value.get()
    update_prefs(prefs, "dump_height", x)
    dump_message.config(height = x)
    
dump_height_value = tk.IntVar()
dump_height_value.set(prefs.get("dump_height"))
dump_height = ttk.Spinbox(settings_frame, from_=14, to=76, increment=2, textvariable=dump_height_value,
                          command=save_dump_height, width = 3, wrap=True)
dump_height.grid(row=156, column=0, sticky='e', padx=2, pady=5)
ttk.Label(settings_frame, text='DUMP text box height',
          foreground='blue' ).grid(column=1, row=156, sticky='w', padx=5, pady=1)

def save_view_height():
    x = view_height_value.get()
    update_prefs(prefs, "view_height", x)
    view_space.config(height = x)
    
view_height_value = tk.IntVar()
view_height_value.set(prefs.get("view_height"))
view_height = ttk.Spinbox(settings_frame, from_=14, to=76, increment=2, textvariable=view_height_value,
                          command=save_view_height, width = 3, wrap=True)
view_height.grid(row=159, column=0, sticky='e', padx=2, pady=5)
ttk.Label(settings_frame, text='VIEW text box height',
          foreground='blue' ).grid(column=1, row=159, sticky='w', padx=5, pady=1)




################# Contents of HELP tab #######################################
help_frame = ttk.Frame(help_tab)
help_frame.columnconfigure(0, weight=1)
help_frame.rowconfigure(0, weight=1) #######
help_frame.grid(sticky='ewns')
ttk.Label(help_frame, text='Pi2650   --  Version : '
          + VERSION).grid(sticky='e', padx=5, pady=5)
# help topic
topic_frame = ttk.Frame(help_frame)
topic_frame.columnconfigure(1, weight=1)
topic_var = tk.StringVar()

ttk.Label(
    topic_frame,
    text='Help topics: '
).grid(sticky=tk.E + tk.W, padx=5, pady=5)

help_var = tk.StringVar()
help_options = ['About', 'File organization', 'Assembler',
                'Dump', '2650 User Manual', 'Interton Coding Guide', 'Changelog']
help_topics = ttk.Combobox(topic_frame, 
                           value=help_options,
                           textvariable=help_var,
                           state='readonly'
                           )
help_topics.grid(row=0, column=1, sticky=tk.W, padx=5)
help_topics.current(0)
help_topics.bind("<<ComboboxSelected>>", get_and_display_help)

topic_frame.grid(sticky='w')

ttk.Separator(help_frame, orient=tk.HORIZONTAL).grid(sticky='ew')

help_message_frame = ttk.LabelFrame(help_frame, text='Help info')
help_message_frame.columnconfigure(0, weight=1)
help_message_frame.rowconfigure(3, weight=2)

help_message = tk.Text(help_message_frame, height=36)
# NOTE the tk.Text widget is not designed to resize itself to fill
# available space. It's height setting, in lines, has been chosen to maximise
# space in the text widget within the root dimensions, and with the current
# font size.
help_message.config(wrap=tk.WORD)
help_message.grid(sticky='nesw')

help_scrollbar = ttk.Scrollbar(help_message_frame)
help_scrollbar.grid(row=0, column=1, sticky='nes')
help_message_frame.grid(row=3, sticky='nesw') #########
help_scrollbar.configure(command=help_message.yview)
help_message.configure(yscrollcommand=help_scrollbar.set)

display_help_file("about")  # default file to show

############################################################################

root.mainloop()
