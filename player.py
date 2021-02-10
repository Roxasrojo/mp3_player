import pygame
from mutagen.mp3 import MP3
import backend
from tkinter import *
from tkinter import filedialog
from PIL import ImageTk,Image
import os
import time

#Initialize a state of program starting (outside of the loop)
start = False
# Initialize Tkinter.
window = Tk()
window.wm_title("MP3 Player")
window.geometry('380x360')
#Initialize the player.
pygame.mixer.init()
pygame.mixer.music.set_volume(0.7)

#Function to create a new database (playlist), and run it.
def clean_list():
    backend.delete_table()
    backend.create_table()
    try:
        viewlist()
    except:
        pass

clean_list()

#Select the directory where the music is, automatically will add the elements to the playlist.
def select_directory():
    folder_selected = filedialog.askdirectory()
    for root, dir, file_in in os.walk(folder_selected):
        for item in file_in:
            if '.mp3' in item:
                backend.insert(root, item)
            elif '.flac' in item:
                backend.insert(root, item)
            else:
                pass
    try:
        viewlist()
    except:
        pass

def select_file():
    global file_selected
    file_selected = filedialog.askopenfilenames()
    for item in file_selected:
        if '.mp3' in item:
            backend.insert(os.path.dirname(item), os.path.basename(item))
        elif '.flac' in item:
            backend.insert(os.path.dirname(item), os.path.basename(item))
        else:
            pass
    try:
        viewlist()
    except:
        pass



#Selected row to load the song.
def get_selected_song(event):
    try:
        global selected_tuple
        global current_song
        index=song_list.curselection()[0]+1
        selected_tuple=backend.search(index)[0]
        song_player.delete(0,END)
        song_player.insert(END, selected_tuple[2])
        try:
            if current_song != f"{selected_tuple[1]}/{selected_tuple[2]}":
                playReload.config(state = NORMAL)
            else:
                playReload.config(state = DISABLED)
        except:
            pass

    except IndexError:
        pass

#Define the database handlers.
def add_entry():
    backend.insert(song_player_value.get())
    song_list.delete(0,END)
    song_list.insert(END,(song_player_value.get()))

def searchlist():
    song_list.delete(0,END)
    for row in backend.search(song_player_value.get()):
        song_list.insert(END,row)

def viewlist():
    song_list.delete(0,END)
    for row in backend.view():
        song_list.insert(END, row)

def delete_entry():
    try:
        backend.delete_row(selected_tuple[0])
        backend.update_id(selected_tuple[0])
        #get_selected_song(e)
        song_list.delete(0,END)
        for row in backend.view():
            song_list.insert(END, row)
    except:
        pass


#Define the initial functionalities of the player.
def play_song():
    global current_song
    global start
    global state
    global change
    global mute
    state = False
    change = False
    mute = False
    try:
        current_song = f"{selected_tuple[1]}/{selected_tuple[2]}"
        pygame.mixer.music.load(current_song)
        pygame.mixer.music.play()
        if start == False:
            start = True
            states_slider()
        playReload.config(state = DISABLED)
    except:
        pass


    time_scale.set(0)


def pause_unpause():
    if start == False:
        return
    else:
        global state
        if state == False:
            pygame.mixer.music.pause()
            pauseUnpause.config(relief = SUNKEN)
            state = True
        elif state == True:
            pygame.mixer.music.unpause()
            pauseUnpause.config(relief = RAISED)
            state = False
            states_slider()


def states_slider():
    if not start:
        return
    if state:
        return

    try:
        selected_song = MP3(current_song)
        global song_l
        try:
            song_l = selected_song.info.length
        except:
            song_l = 0
    except:
        pass

    global elapsing_time
    global change
    try:
        if change == True:
            change = False
        else:
            elapsing_time = int(time_scale.get())
            if elapsing_time > song_l:
                elapsing_time = 0
                song_time(song_l)



    except:
        elapsing_time = int(pygame.mixer.music.get_pos()) / 1000


    #Define the time variables to convert from seconds to minutes:seconds
    current_song_time = time.strftime("%M:%S", time.gmtime(song_l))
    current_time = time.strftime("%M:%S", time.gmtime(elapsing_time))

    slider_time = Label(window, text = f'{current_time} / {current_song_time}')
    slider_time.grid(column = 3, row = 14)

    elapsing_time += 1

    time_scale.configure(to = int(song_l)+1)
    time_scale.bind("<Button-1>", position_change)
    time_scale.set(int(elapsing_time))

    time_scale.after(1000, states_slider)


def position_change(event):
    if not start:
        return
    global change
    change = True
    song_time(time_scale.get())


def next_song(next):
    if not start:
        return
    global current_song
    global state
    global change
    current_song = next
    pygame.mixer.music.load(next)
    pygame.mixer.music.play()
    time_scale.set(0)
    state = False
    change = False

def next_bind():
    if not start:
        return
    next = backend.curr_song(os.path.basename(current_song))
    try:
        next_index = backend.search(next[0][0]+1)[0]
        song_list.selection_clear(0, END)
        song_list.selection_set(next_index[0]-1, last=None)

    except:
        next_index = backend.search(1)[0]
        song_list.selection_clear(0, END)
        song_list.selection_set(next_index[0]-1, last=None)

    play_next = f'{next_index[1]}/{next_index[2]}'

    #Change selection at the ListBox
    next_song(play_next)
    get_selected_song(next_index)

def previous_song():
    if not start:
        return
    previous = backend.curr_song(os.path.basename(current_song))
    try:
        if selected_tuple[0] == 1:
            previous_index = backend.search(len(backend.view()))[0]
        else:
            previous_index = backend.search(previous[0][0]-1)[0]

    except:
        previous_index = backend.search(1)[0]
    play_previous = f'{previous_index[1]}/{previous_index[2]}'

    #Change selection at the ListBox
    song_list.selection_clear(0, END)
    song_list.selection_set(previous_index[0]-1, last=None)
    next_song(play_previous)
    get_selected_song(previous_index)


def song_time(t):
    if not start:
        return
    global change
    if float(t) == float(song_l):
        next = backend.curr_song(os.path.basename(current_song))
        try:
            next_index = backend.search(next[0][0]+1)[0]
        except:
            next_index = backend.search(1)[0]
        play_next = r''+next_index[1]+r'/'+next_index[2]

        #Change selection at the ListBox
        song_list.selection_clear(0, END)
        song_list.selection_set(next_index[0]-1, last=None)
        get_selected_song(next_index)
        next_song(play_next)
    elif change:
        pygame.mixer.music.set_pos(float(t))
        global elapsing_time
        elapsing_time = float(t)

def volume_selector(volume):
    global mute_set
    global volume_set
    global mute
    mute = False
    pygame.mixer.music.set_volume(int(volume)/100)
    if int(volume) > 0:
        volume_icon.config(image = volume_set)
    else:
        volume_icon.config(image = mute_set)
        mute = True

def mute_unmute():
    global mute
    current_volume = volume_scale.get()
    if mute == False:
        volume_selector(0)
        mute = True
    elif current_volume == 0 and mute == True:
        volume_scale.set(70)
        volume_selector(70)
        mute = False
    else:
        volume_selector(current_volume)
        mute = False

def repeat():
    try:
        pygame.mixer.music.play()
        global state
        global change
        global mute
        state = False
        change = False
        mute = False

        time_scale.set(0)

    except:
        pass


"""The next lines of text define the icons used in the program
All icons are taken from The Noun Project by different sources: 365; Viktor Vorobyev; Fantastic,IN"""
volume_set = Image.open('./images/volume_img.png')
volume_set = volume_set.resize((20, 20), Image.ANTIALIAS)
volume_set = ImageTk.PhotoImage(volume_set)

mute_set = Image.open('./images/no_volume_img.png')
mute_set = mute_set.resize((20, 20), Image.ANTIALIAS)
mute_set = ImageTk.PhotoImage(mute_set)

play_set = Image.open('./images/play_img.png')
play_set = play_set.resize((30, 30), Image.ANTIALIAS)
play_set= ImageTk.PhotoImage(play_set)

pause_set = Image.open('./images/pause_img.png')
pause_set = pause_set.resize((30, 30), Image.ANTIALIAS)
pause_set= ImageTk.PhotoImage(pause_set)

delete_set = Image.open('./images/delete_img.png')
delete_set = delete_set.resize((30, 30), Image.ANTIALIAS)
delete_set= ImageTk.PhotoImage(delete_set)

repeat_set = Image.open('./images/repeat_img.png')
repeat_set = repeat_set.resize((20, 20), Image.ANTIALIAS)
repeat_set= ImageTk.PhotoImage(repeat_set)

next_set = Image.open('./images/next_img.png')
next_set = next_set.resize((20, 20), Image.ANTIALIAS)
next_set= ImageTk.PhotoImage(next_set)

previous_set = Image.open('./images/previous_img.png')
previous_set = previous_set.resize((20, 20), Image.ANTIALIAS)
previous_set= ImageTk.PhotoImage(previous_set)

cancel_set = Image.open('./images/cancel_img.png')
cancel_set = cancel_set.resize((30, 30), Image.ANTIALIAS)
cancel_set= ImageTk.PhotoImage(cancel_set)



"""THE NEXT LINES OF TEXT DEFINE THE INTERFACE OF THE PROGRAM"""
#Define a variable to store what it's being received by the database. (Top Side)
song_player_value=StringVar()
song_player=Entry(window, textvariable=song_player_value, width = 30)
song_player.grid(row=1,column=1)
song_player_label=Label(window, text="Song")
song_player_label.grid(row=1,column=0)

#Define the tool bar. (Top Side)
mp3_menu = Menu(window)
window.config(menu = mp3_menu)
file_menu = Menu(mp3_menu)
mp3_menu.add_cascade(label = 'File', menu = file_menu)
file_menu.add_command(label = "Directory/Folder", command = select_directory)
file_menu.add_command(label = 'Select File', command = select_file)
file_menu.add_command(label = 'Clear Playlist', command = clean_list)
file_menu.add_separator()
file_menu.add_command(label = "Exit", command = window.quit)

#The section of the program to view the playlist. (Left Side)
song_list = Listbox(window, height = 12, width = 45)
song_list.grid(row = 3, column = 0, rowspan = 10, columnspan = 2)

sb_song_list = Scrollbar(window)
sb_song_list.grid(row = 3, column = 2, columnspan = 1, rowspan = 6)

song_list.configure(yscroll = sb_song_list.set)
sb_song_list.configure(command = song_list.yview)

song_list.bind('<<ListboxSelect>>', get_selected_song)

#Create the buttons to run the different functionalities. (Right Side)

playReload = Button(window,text = "Play/Reload", image = play_set, command = play_song)
playReload.grid(row = 4,column = 3)

pauseUnpause = Button(window,text = "Pause/Unpause", image = pause_set, command = pause_unpause)
pauseUnpause.grid(row = 5,column = 3)

deleteSong = Button(window,text = "Delete Song", image = delete_set, command = delete_entry)
deleteSong.grid(row = 6,column = 3)

close_button = Button(window,text = "Close", image = cancel_set, command = window.destroy)
close_button.grid(row = 7,column = 3)

#Create variables for volume selection (Right Side)
set_volume = DoubleVar()
set_volume.set(70)
volume_scale = Scale(window, variable = set_volume, from_ = 100, to = 0, width = 20, command = volume_selector)
volume_scale.grid(row = 8, column = 3)
volume_icon = Button(window, image=volume_set, command = mute_unmute)
volume_icon.grid(row = 8, column = 2)


#Slider for time selection (Bottom)
time_scale = Scale(window, from_=0, to=100, orient='horizontal', length = 230, showvalue = False)
time_scale.configure(background="black", foreground="white", sliderrelief="flat", troughcolor="white",
                      command = song_time, activebackground="grey", highlightthickness=5, sliderlength=30)
time_scale.grid(row = 13, column = 1)

slider_time = Label(window, text = '00:00 / 00:00')
slider_time.grid(row = 14, column = 3)

repeat_button = Button(window,text = "repeat", image = repeat_set, command = repeat)
repeat_button.grid(row = 13,column = 3)

next_button = Button(window,text = "next", image = next_set, command = next_bind)
next_button.grid(row = 13,column = 2)

previous_button = Button(window,text = "previous", image = previous_set, command = previous_song)
previous_button.grid(row = 13,column = 0)


window.mainloop()
