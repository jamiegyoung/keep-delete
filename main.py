import tempfile
import shutil
from os import walk, path, listdir
from tkinter import *
from tkinter import filedialog, messagebox
from PIL import ImageTk, Image

def resizeImage(img, target_width, target_height):
  if img.width > target_width or img.height > target_height:
    new_width = int(round(img.width * 0.9))
    new_height = int(round(img.height * 0.9))
    img = img.resize((new_width, new_height), Image.ANTIALIAS)
    return resizeImage(img, target_width, target_height)

  return img

def get_image_files_in_dir(dir):
  if not path.isdir(dir): return []
  files = []

  for (dirpath, dirnames, filenames) in walk(dir):
    filtered_filenames = filter(lambda x: x[-4:].lower() == ".jpg" or x[-4:].lower() == ".png", filenames)
    files.extend(filtered_filenames)
    break

  return files

class App():
  def __init__(self):
    self.tmp_dir = tempfile.mkdtemp(prefix="keep_delete_")
    self.root = Tk()
    self.root.title("keep-delete")
    self.root.geometry("1000x800")
    self.root.configure(background='#1E1E24')
    self.past_actions = []
    self.root.bind("<Configure>", self.handle_resize)

    self.width = self.root.winfo_width()
    self.height = self.root.winfo_height()
    
    self.add_title()
    self.dir = filedialog.askdirectory()
    self.images = get_image_files_in_dir(self.dir)
    self.initial_length = len(self.images)
    self.buttons = self.add_buttons()
    self.counter_value = 0
    self.counter = self.add_counter()
    self.add_image()

    def on_closing():
      if messagebox.askokcancel("Quit", "After quitting you will not be able to recover deleted files\nDo you still wish to quit?"):
        self.root.destroy()

    # Handle closing of window
    self.root.protocol("WM_DELETE_WINDOW", on_closing)


  def add_counter(self):
    counter = Label(
      self.root,
      background="#1E1E24",
      text="{}/{}".format(self.counter_value, len(self.images)),
      justify=CENTER,
      padx=10,
      pady=20,
      foreground="White",
      font=("Whitney", 16)
    )
    counter.pack()

    return counter

  def handle_resize(self, e):
    if hasattr(self, 'current_image') and self.current_image:
      if not self.width == self.root.winfo_width() or not self.height == self.root.winfo_height():
        self.width = self.root.winfo_width()
        self.height = self.root.winfo_height()
        self.update_image()

  def add_title(self):
    title = Label(
      self.root,
      background="#1E1E24",
      text="keep-delete",
      justify=CENTER,
      padx=10,
      pady=20,
      foreground="White",
      font=("Whitney", 24)
    )
    title.pack()

  def update_image(self):
    img = Image.open(self.current_image)
    img = resizeImage(img, self.root.winfo_width() - 50, self.root.winfo_height() - 50)
    photo_image = image=ImageTk.PhotoImage(image=img)
    self.image_panel.configure(image=photo_image)
    self.image_panel.image = photo_image

  def change_image(self):
    self.buttons["keep_button"]["state"] = NORMAL
    self.buttons["delete_button"]["state"] = NORMAL
    if len(self.images) == 0:
      self.buttons["keep_button"]["state"] = DISABLED
      self.buttons["delete_button"]["state"] = DISABLED
      messagebox.showinfo("Finished!", "No more images remaining!")
      self.current_image = None
      return

    self.current_image = "{}/{}".format(self.dir, self.images[0])
    self.images.pop(0)
    self.counter_value += 1
    self.counter["text"] = "{}/{}".format(self.counter_value, self.initial_length)
    self.update_image()

  def keep_image(self):
    self.past_actions.insert(0, {"action": "keep", "img": self.current_image[self.current_image.rfind("/"):]})
    self.change_image()
    self.buttons["undo_button"]["state"] = NORMAL

  def delete_image(self):
    shutil.move(self.current_image, self.tmp_dir)
    self.past_actions.insert(0, {
      "action": "delete",
      "img": self.current_image[self.current_image.rfind("/"):]
    })
    self.change_image()
    self.buttons["undo_button"]["state"] = NORMAL

  def undo_action(self):
    last_action = self.past_actions[0]
    
    if last_action["action"] == "delete":
      shutil.move(self.tmp_dir + last_action["img"], self.dir)

    # Fixes last image duplication problem
    if not self.current_image == None:
      self.images.insert(0, self.current_image[self.current_image.rfind('/'):])
    self.images.insert(0, last_action["img"])
    self.counter_value -= 2
    self.change_image()
    self.past_actions.pop(0)
    if len(self.past_actions) == 0:
      self.buttons["undo_button"]["state"] = DISABLED
      return

  def add_image(self):
    mainframe = Frame(
      self.root,
      padx=5, pady=5,
      width=self.width,
      height=self.height,
      background="#424242"
    )
    
    self.image_panel = Label(mainframe, background="#424242")

    self.change_image()

    self.image_panel.pack(side="top")
    mainframe.pack()

  def add_buttons(self):
    button_frame = Frame(
      self.root,
      padx=10, pady=10,
      width=self.width,
      height=self.height,
      background="#1E1E24"
    )

    keep_button = HoverButton(
      button_frame,
      text="Keep",
      command=self.keep_image,
      padx=40,
      pady=20,
      font=("Whitney", 18),
      background="#282835",
      activebackground="#3d3d51",
      foreground="white",
      highlightthickness=0,
      bd=0
    )

    keep_button.grid(row=0, column=0, padx=10)

    delete_button = HoverButton(
      button_frame,
      text="Delete",
      command=self.delete_image,
      padx=40,
      pady=20,
      font=("Whitney", 18),
      background="#282835",
      activebackground="#3d3d51",
      foreground="white",
      highlightthickness=0,
      bd=0
    )

    delete_button.grid(row=0, column=2, padx=10)

    undo_button = HoverButton(
      button_frame,
      text="Undo",
      command=self.undo_action,
      padx=40,
      pady=20,
      font=("Whitney", 18),
      background="#92140C",
      activebackground="#ba1d12",
      foreground="white",
      highlightthickness=0,
      bd=0,
      state=DISABLED
    )

    undo_button.grid(row=0, column=3, padx=10)

    button_frame.pack(side=BOTTOM)
    return { "keep_button": keep_button, "delete_button": delete_button, "undo_button": undo_button }

class HoverButton(Button):
  def __init__(self, master=None, **kw):
    super().__init__(master=master, **kw)
    self.default_background = self["background"]
    self.bind("<Enter>", self.on_enter)
    self.bind("<Leave>", self.on_leave)
  
  def on_enter(self, e):
    self["background"] = self["activebackground"]

  def on_leave(self, e):
    self["background"] = self.default_background    

tmp = tempfile.gettempdir()
filtered_tmp = filter(lambda x: x[:12] == "keep_delete_", listdir(tmp))

# Clean previous tmp folders
for file in filtered_tmp:
  shutil.rmtree("{}\\{}".format(tmp, file))
  pass

app = App()
app.root.mainloop()

# Clean tmp folders
if path.exists(app.tmp_dir):
  shutil.rmtree(app.tmp_dir)
  if path.exists(app.tmp_dir):
    print("failed to delete dir {}".format(app.tmp_dir))
    pass