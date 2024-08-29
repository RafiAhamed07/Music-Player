import os
import threading
import time
from tkinter import *
from tkinter import filedialog, messagebox
from tkinter import ttk
from PIL import Image, ImageTk
from pygame import mixer

# Initialize the mixer for audio playback
mixer.init()

# Create the main application window
root = Tk()
root.title('Music Player App')
root.geometry('700x500')
root.resizable(False, False)

# Load and set the background image
bg_image = Image.open("bg.jpg")
bg_image = bg_image.resize((700, 500), Image.LANCZOS)
bg_photo = ImageTk.PhotoImage(bg_image)

# Create a Canvas widget to hold the background image
canvas = Canvas(root, width=700, height=500)
canvas.pack(fill="both", expand=True)
canvas.create_image(0, 0, image=bg_photo, anchor="nw")

# Set the directory for music files
music_dir = os.path.join(os.path.expanduser("~"), "Music")

# Define styles for various widgets
button_style = {
    'bg': '#282c34',  # Darker background for buttons
    'fg': '#61dafb',  # Light blue text color
    'font': ('Courier', 12, 'bold'),  # Primary font
    'relief': RAISED,
    'bd': 3
}
label_style = {
    'bg': '#282c34',  # Dark background
    'fg': '#61dafb',  # Light blue text color
    'font': ('Courier', 10, 'bold')  # Primary font
}
listbox_style = {
    'bg': '#1C1C1C',
    'fg': 'green',
    'font': ('Courier', 12),  # Primary font
    'selectbackground': '#696969',
    'selectforeground': 'black'
}

# Define custom styles for ttk.Button
style = ttk.Style()
style.configure("TButton",
                font=('Courier', 12, 'bold'),
                background='#282c34',  # Match the button bg to overall theme
                foreground='#61dafb',  # Text color
                borderwidth=3,
                relief='raised')
style.map("TButton",
          background=[('active', '#444b58')],
          foreground=[('active', '#61dafb')],
          relief=[('pressed', 'sunken'), ('!pressed', 'raised')])

style.configure("TScale",
                background="#282c34",  # Background for the slider
                troughcolor='#444b58',  # Darker trough for contrast
                sliderrelief='raised')

# Create the listbox frame with scrollbar
listbox_frame = Frame(canvas, bg="black", bd=2, relief=SUNKEN)
listbox_frame.place(relx=0.1, rely=0.15, relwidth=0.8, relheight=0.4)
scrollbar = Scrollbar(listbox_frame, orient=VERTICAL)
songs_list = Listbox(listbox_frame, selectmode=SINGLE, yscrollcommand=scrollbar.set, **listbox_style)
scrollbar.config(command=songs_list.yview)
scrollbar.pack(side=RIGHT, fill=Y)
songs_list.pack(side=LEFT, fill=BOTH, expand=True)


# Function to display developer information
def show_info():
    messagebox.showinfo("Developer Info", "Name: Rafi Ahamed\nEmail: fidaahamed15@gmail.com\nMusic Player App")


# Function to add songs to the playlist
def add_songs():
    temp_song = filedialog.askopenfilenames(initialdir=music_dir, title="Choose a song",
                                            filetypes=[("mp3 Files", "*.mp3")])
    for s in temp_song:
        if s not in songs_list.get(0, END):  # Avoid duplicate entries
            songs_list.insert(END, s)


# Function to delete the selected song from the playlist
def delete_song():
    try:
        selected_song_index = songs_list.curselection()[0]
        songs_list.delete(selected_song_index)
    except IndexError:
        messagebox.showerror("Error", "No song selected to delete!")


# Function to play the selected song
def play_song():
    try:
        selected_song = songs_list.get(ACTIVE)
        mixer.music.load(selected_song)
        mixer.music.play()
        update_song_details()
    except Exception as e:
        messagebox.showerror("Error", f"Unable to play the song: {e}")


# Function to control playback (pause, resume, stop)
def control_playback(action):
    if action == 'pause':
        mixer.music.pause()
    elif action == 'resume':
        mixer.music.unpause()
    elif action == 'stop':
        mixer.music.stop()
        reset_progress()


# Function to update song details, such as progress bar and time labels
def update_song_details():
    def update_thread():
        try:
            song_length = mixer.Sound(songs_list.get(ACTIVE)).get_length()
            progress_slider.config(to=song_length)
            total_time_label.config(text=f"Total Duration: {time.strftime('%M:%S', time.gmtime(song_length))}")

            while mixer.music.get_busy():
                if not progress_slider_clicked:  # Update only if the slider is not being dragged
                    current_time = mixer.music.get_pos() / 1000
                    progress_slider.set(current_time)
                    selected_time_label.config(
                        text=f"Selected Time: {time.strftime('%M:%S', time.gmtime(current_time))}")
                else:
                    # Update selected time label even if the slider is clicked
                    current_time = progress_slider.get()
                    selected_time_label.config(
                        text=f"Selected Time: {time.strftime('%M:%S', time.gmtime(current_time))}")
                time.sleep(0.5)  # Update every 0.5 seconds for smoother progress
        except Exception as e:
            print(f"Error: {e}")

    # Run the update in a separate thread to avoid blocking the main loop
    threading.Thread(target=update_thread, daemon=True).start()


# Function to reset the progress bar and time labels when the song stops
def reset_progress():
    progress_slider.set(0)
    selected_time_label.config(text="Selected Time: 00:00")
    total_time_label.config(text="Total Duration: 00:00")


# Function to handle the event when the progress slider is clicked and dragged
def on_progress_slider_change(event):
    if mixer.music.get_busy():
        seek_time = progress_slider.get()
        mixer.music.play(loops=0, start=seek_time)
        selected_time_label.config(text=f"Selected Time: {time.strftime('%M:%S', time.gmtime(seek_time))}")


# Function to handle the event when the progress slider is clicked and dragged
def on_progress_slider_click(event):
    global progress_slider_clicked
    progress_slider_clicked = True


def on_progress_slider_release(event):
    global progress_slider_clicked
    progress_slider_clicked = False
    seek_time = progress_slider.get()
    mixer.music.play(loops=0, start=seek_time)
    selected_time_label.config(text=f"Selected Time: {time.strftime('%M:%S', time.gmtime(seek_time))}")


# Adjusting the progress & volume bar style
style.configure("TScale",
                background="#282c34",
                troughcolor='#444b58',
                sliderrelief='raised',
                sliderthickness=5,
                sliderlength=25,
                sliderborderwidth=100, )
progress_slider = ttk.Scale(canvas, from_=0, to=100, orient=HORIZONTAL, style="TScale")
progress_slider.place(relx=0.1, rely=0.65, relwidth=0.8)
# Update the progress slider bindings
progress_slider.bind("<Button-1>", on_progress_slider_click)
progress_slider.bind("<ButtonRelease-1>", on_progress_slider_release)
progress_slider.bind("<B1-Motion>", on_progress_slider_change)  # Update while dragging

selected_time_label = Label(canvas, text="Selected Time: 00:00", **label_style)
selected_time_label.place(relx=0.1, rely=0.6)

total_time_label = Label(canvas, text="Total Duration: 00:00", **label_style)
total_time_label.place(relx=0.7, rely=0.6)

# Create control buttons for playing, pausing, resuming, and stopping music
buttons = [
    {'text': 'Play', 'command': play_song},
    {'text': 'Pause', 'command': lambda: control_playback('pause')},
    {'text': 'Resume', 'command': lambda: control_playback('resume')},
    {'text': 'Stop', 'command': lambda: control_playback('stop')}
]

# Buttons' positioning (adjust x values as needed)
for i, btn in enumerate(buttons):
    ttk.Button(canvas, text=btn['text'], command=btn['command'], style="TButton").place(x=160 + i * 110, y=380)

# Update progress bar placement if needed:
progress_slider.place(relx=0.1, rely=0.65, relwidth=0.8)

# Update labels:
selected_time_label.place(relx=0.1, rely=0.6)
total_time_label.place(relx=0.7, rely=0.6)

# Volume label and control slider
volume_label = Label(canvas, text="Volume", **label_style)
volume_label.place(relx=0.85, rely=0.85, anchor="center")

volume_slider = ttk.Scale(canvas, from_=0, to=1, orient=HORIZONTAL, style="TScale",
                          command=lambda v: mixer.music.set_volume(float(v)))
volume_slider.set(0.5)
volume_slider.place(relx=0.85, rely=0.9, anchor="center", relwidth=0.15)

# Create the menu for adding, deleting songs, and showing info
my_menu = Menu(root)
root.config(menu=my_menu)

add_song_menu = Menu(my_menu, tearoff=0)
my_menu.add_cascade(label="Menu", menu=add_song_menu)
add_song_menu.add_command(label="Add songs", command=add_songs)
add_song_menu.add_command(label="Delete song", command=delete_song)

info_menu = Menu(my_menu, tearoff=0)
my_menu.add_cascade(label="Info", menu=info_menu)
info_menu.add_command(label="About", command=show_info)


# Handle exit with confirmation
def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        root.destroy()


root.protocol("WM_DELETE_WINDOW", on_closing)
# Start the main event loop
root.mainloop()
