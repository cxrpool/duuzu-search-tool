import tkinter as tk
from tkinter import ttk
from tkinter import font 
import webbrowser
import re
import os


titleResults = []

def get_enharmonic_equivalent(key):
    enharmonic_map = {                    
        "A#maj": "Bbmaj", "Bbmaj": "A#maj",
        "C#maj": "Dbmaj", "Dbmaj": "C#maj",
        "D#maj": "Ebmaj", "Ebmaj": "D#maj",
        "F#maj": "Gbmaj", "Gbmaj": "F#maj",
        "G#maj": "Abmaj", "Abmaj": "G#maj",
        "A#min": "Bbmin", "Bbmin": "A#min",
        "C#min": "Dbmin", "Dbmin": "C#min",
        "D#min": "Ebmin", "Ebmin": "D#min",
        "F#min": "Gbmin", "Gbmin": "F#min",
        "G#min": "Abmin", "Abmin": "G#min"
    }
    return enharmonic_map.get(key, key)

def search_songs(file_path, keywords): #searching song titles!
    with open(file_path, 'r', errors="ignore", encoding='utf-8') as file:
        lines = file.readlines()

        songs = []
        current_key = ""

        for line in lines:
            line = line.strip()
            if line.startswith("[") and line.endswith("]"): #if we're on a new key section
                current_key = line
            else: #if its not, it must be a song
                match = re.match(r'^(.*?)(~?\d+(?:\.\d+)?)\)$', line) #extract bpm from parantheses using regex
                if match:
                    bpm = match.group(2).replace('~', '') #get rid of the ~ symbol for live bpms
                    songs.append([line, current_key[1:-1], float(bpm)])  # put the song title and key into a list

    # Split the input string into individual keywords and convert them to lowercase
    keywords_lower = [keyword.lower() for keyword in keywords.split()]

    # Filter song titles that contain any of the keywords
    matching_songs = [song for song in songs if all(keyword in song[0].lower() for keyword in keywords_lower)]

    
    return matching_songs

    


def extract_songs_by_key(file_path, key, bpm, threshold):
    enharmonic_key = get_enharmonic_equivalent(key)
    keys_to_search = {f"[{key}]", f"[{enharmonic_key}]"} 

    try:
        with open(file_path, 'r', errors="ignore", encoding='utf-8') as file:
            lines = file.readlines()

        key_section = False
        songs = []

        for line in lines: #now we extract all the songs in that key
            if line.strip() in keys_to_search:
                key_section = True
            elif line.startswith('[') and key_section:
                break
            elif key_section:
                songs.append(line.strip())

        if songs:
            songs = parse_songs(songs)
            target_bpm = float(bpm)
            tolerance = int(threshold)
            similar_songs = find_similar_bpm(songs, target_bpm, tolerance)
            return similar_songs

    except FileNotFoundError:
        print("The specified file was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

def parse_songs(songs): #get each song title with a sanitized bpm for sorting
    goodSongs = []
    for song in songs:
        match = re.match(r'^(.*?)(~?\d+(?:\.\d+)?)\)$', song) #extract bpm from parantheses using regex
        if match:
            bpm = match.group(2).replace('~', '') #get rid of the ~ symbol for live bpms
            goodSongs.append((song, float(bpm)))
    return goodSongs

def find_similar_bpm(songs, target_bpm, tolerance):
    similar_songs = [(song[0], abs(target_bpm - song[1])) for song in songs if abs(song[1] - target_bpm) <= tolerance]
    similar_songs.sort(key=lambda x: x[1])  # sort by bpm
    return [title[0] for title in similar_songs] #return only titles cuz we dont need the sanitized bpms anymore

def on_double_click(event):
    index = results_listbox.curselection()[0]
    item_text = results_listbox.get(index)
    pattern = r'\([^()]*\)' #we're removing the last set of parantheses for our web search (should be bpm)
    matches = list(re.finditer(pattern, item_text)) 

    if matches:
        last_match = matches[-1]
        start, end = last_match.span()
        item_text = item_text[:start] + item_text[end:]
        item_text = item_text[1:]

    webbrowser.open(f"https://www.google.com/search?q={item_text}")

def set_placeholder(entry, placeholder):
    entry.insert(0, placeholder)
    

def clear_placeholder(event, entry, placeholder):
    if entry.get() == placeholder:
        entry.delete(0, tk.END)
        

def restore_placeholder(event, entry, placeholder):
    if entry.get() == '':
        set_placeholder(entry, placeholder)

def scroll_to_middle():
    middle_index = results_listbox.size() // 2
    results_listbox.see(middle_index)
    results_listbox.selection_set(middle_index)

def on_checkbox_click(var):
    if var == var1:
        var2.set(0)
    else:
        var1.set(0)

def search():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, 'database.txt')
    if key_checkbox_var.get(): #search for songs with key and bpm
        key = key_entry.get()
        bpm = bpm_entry.get()
        threshold = thresh_entry.get()
        if threshold == "" or threshold == "threshold (default: 5)" or not threshold.isnumeric():
            threshold = 5
        
        results = extract_songs_by_key(file_path, key, bpm, threshold)
        results_listbox.delete(0, tk.END)
        if results is None or len(results) == 0:
            results_listbox.insert(tk.END, "No results bruh!")
        else:
            for result in results:
                results_listbox.insert(tk.END, result)
    else: #search songs by title
        search = search_entry.get()
        global titleResults
        results = search_songs(file_path, search) 
        results_listbox.delete(0, tk.END)
        if results is None or len(results) == 0:
            results_listbox.insert(tk.END, "No results bruh!")
        else:
            for result in results:
                results_listbox.insert(tk.END, result[0])
            titleResults = results #whatever i guess we're doing a global variable now
        
def on_select(event):
    if search_checkbox_var.get():
        # get the selected index
        selected_index = results_listbox.curselection()
        if selected_index:
            selected_item = titleResults[selected_index[0]]
            # replace the key and bpm input with the key and bpm of the song
            key_var.set(selected_item[1])
            bpm_var.set(selected_item[2])
           
    

def toggle_entries():
    if key_checkbox_var.get():
        search_checkbox_var.set(False)
        key_entry.config(state='normal')
        bpm_entry.config(state='normal')
        thresh_entry.config(state='normal')
        search_entry.config(state='disabled')
        results_listbox.delete(0, tk.END)
    else:
        search_checkbox_var.set(True)
        key_entry.config(state='disabled')
        bpm_entry.config(state='disabled')
        thresh_entry.config(state='disabled')
        search_entry.config(state='normal')
        results_listbox.delete(0, tk.END)

def toggle_search():
    if search_checkbox_var.get():
        key_checkbox_var.set(False)
        key_entry.config(state='disabled')
        bpm_entry.config(state='disabled')
        thresh_entry.config(state='disabled')
        search_entry.config(state='normal')
        results_listbox.delete(0, tk.END)
    else:
        key_checkbox_var.set(True)
        key_entry.config(state='normal')
        bpm_entry.config(state='normal')
        thresh_entry.config(state='normal')
        search_entry.config(state='disabled')
        results_listbox.delete(0, tk.END)
# main window
root = tk.Tk()
root.title("duuzu search tool")
root.configure(bg='black')
root.geometry("600x600")
root.defaultFont = font.nametofont("TkDefaultFont")
root.defaultFont.configure(size=11)

#title frame
title_frame = tk.Frame(root, bg='black')
title_frame.pack(fill='x')
title_label = tk.Label(title_frame, text="duuzu search tool by cxrpool", bg='black', fg='white', font=('Arial', 14))
title_label.pack(pady=10)
title_label.pack(anchor='center')

# top frame to hold our buttons
top_frame = tk.Frame(root, bg='black')
top_frame.pack()

# checkboxes
key_checkbox_var = tk.BooleanVar()
key_checkbox = tk.Checkbutton(top_frame, variable=key_checkbox_var, command=toggle_entries, bg='black', fg='white', selectcolor='black')
key_checkbox.grid(row=0, column=0, padx=5)
key_checkbox_var.set(True) #turned on by default

search_checkbox_var = tk.BooleanVar()
search_checkbox = tk.Checkbutton(top_frame, variable=search_checkbox_var, command=toggle_search, bg='black', fg='white', selectcolor='black')
search_checkbox.grid(row=2, column=0, padx=5)

# dumb variables
key_var = tk.StringVar() #really gotta do this cuz you cant do .set() on an entry box
bpm_var = tk.StringVar()

# key box
key_entry = tk.Entry(top_frame, width=20, textvariable=key_var, font = "Arial 11")
key_entry.grid(row=0, column=1, padx=5)
set_placeholder(key_entry, "key (ex: Amaj)")
key_entry.bind("<FocusIn>", lambda event: clear_placeholder(event, key_entry, "key (ex: Amaj)"))
key_entry.bind("<FocusOut>", lambda event: restore_placeholder(event, key_entry, "key (ex: Amaj)"))

# bpm box
bpm_entry = tk.Entry(top_frame, width=20, textvariable=bpm_var, font = "Arial 11")
bpm_entry.grid(row=0, column=2, padx=5)
set_placeholder(bpm_entry, "bpm")
bpm_entry.bind("<FocusIn>", lambda event: clear_placeholder(event, bpm_entry, "bpm"))
bpm_entry.bind("<FocusOut>", lambda event: restore_placeholder(event, bpm_entry, "bpm"))

# threshold box
thresh_entry = tk.Entry(top_frame, width=20, font = "Arial 11")
thresh_entry.grid(row=1, column=1, padx=5)
set_placeholder(thresh_entry, "threshold (default: 5)")
thresh_entry.bind("<FocusIn>", lambda event: clear_placeholder(event, thresh_entry, "threshold (default: 5)"))
thresh_entry.bind("<FocusOut>", lambda event: restore_placeholder(event, thresh_entry, "threshold (default: 5)"))

# search bar
search_entry = tk.Entry(top_frame, width=45, font = "Arial 11")
search_entry.grid(row=2, column=1, columnspan=2, padx=10, pady=30, ipadx=0)
set_placeholder(search_entry, "search title")
search_entry.bind("<FocusIn>", lambda event: clear_placeholder(event, search_entry, "search title"))
search_entry.bind("<FocusOut>", lambda event: restore_placeholder(event, search_entry, "search title"))
search_entry.config(state='disabled')


# search button
search_button = tk.Button(top_frame, text="Search", command=search)
search_button.grid(row=0, column=3, padx=10, pady=10, ipadx=0)

# bottom frame to hold listbox
bottom_frame = tk.Frame(root, bg='black')
bottom_frame.pack(fill=tk.BOTH, expand=True, pady=10)

# listbox
results_listbox = tk.Listbox(bottom_frame, width=50, height=10)
results_listbox.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# scrollbar
scrollbar = ttk.Scrollbar(results_listbox, orient=tk.VERTICAL, command=results_listbox.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# put the scrollbar in our epic listbox
results_listbox.config(yscrollcommand=scrollbar.set)

# add the search functionality to the list results
results_listbox.bind("<Double-1>", on_double_click)
results_listbox.bind('<<ListboxSelect>>', on_select)


# run it
root.mainloop()
