# ---------- IMPORTS ----------
import sys
import json
import ctypes
import winreg
import os

# ---------- HEADLESS QUICK SWITCH (before any GUI import) ----------
# Must run before customtkinter/tkinter are imported — importing CTk
# initialises a Tk root on some PyInstaller builds, causing a window flash.

APP_DATA_DIR = os.path.join(os.getenv("APPDATA"), "QuickWallpaper")
STORAGE_FILE = os.path.join(APP_DATA_DIR, "data.json")

os.makedirs(APP_DATA_DIR, exist_ok=True)

def _load_data_headless():
    if os.path.exists(STORAGE_FILE):
        try:
            with open(STORAGE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"images": [], "cycle_index": 0, "styles": {}}

def _set_wallpaper_style_headless(style):
    key = winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        r"Control Panel\Desktop",
        0,
        winreg.KEY_SET_VALUE
    )
    styles = {
        "Fill":    ("10", "0"),
        "Fit":     ("6",  "0"),
        "Stretch": ("2",  "0"),
        "Center":  ("0",  "0"),
        "Tile":    ("0",  "1")
    }
    wallpaper_style, tile = styles.get(style, ("10", "0"))
    winreg.SetValueEx(key, "WallpaperStyle", 0, winreg.REG_SZ, wallpaper_style)
    winreg.SetValueEx(key, "TileWallpaper",  0, winreg.REG_SZ, tile)
    winreg.CloseKey(key)

if "--quick-switch" in sys.argv:
    _data        = _load_data_headless()
    _images      = _data.get("images", [])
    _cycle_index = _data.get("cycle_index", 0)
    _styles      = _data.get("styles", {})

    _valid = [p for p in _images if os.path.exists(p)]

    if _valid:
        _cycle_index = _cycle_index % len(_valid)
        _path        = _valid[_cycle_index]
        _style       = _styles.get(_path, "Fill")

        _set_wallpaper_style_headless(_style)
        ctypes.windll.user32.SystemParametersInfoW(20, 0, _path, 3)

        _cycle_index = (_cycle_index + 1) % len(_valid)
        _data["cycle_index"] = _cycle_index

        with open(STORAGE_FILE, "w") as _f:
            json.dump(_data, _f, indent=2)

    sys.exit(0)

# ---------- GUI IMPORTS (only reached in normal launch) ----------
import customtkinter as ctk
from tkinter import filedialog
from PIL import Image

# ---------- APP SETTINGS ----------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

def load_data():
    if os.path.exists(STORAGE_FILE):
        try:
            with open(STORAGE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"images": [], "cycle_index": 0, "styles": {}}

def save_data():
    with open(STORAGE_FILE, "w") as f:
        json.dump({
            "images":      images,
            "cycle_index": cycle_index,
            "styles":      image_styles    # path -> style string
        }, f, indent=2)

# ---------- GLOBALS ----------
_data        = load_data()
images       = _data.get("images", [])
cycle_index  = _data.get("cycle_index", 0)
image_styles = _data.get("styles", {})    # persists each wallpaper's chosen style
image_count  = 0

# ---------- WALLPAPER STYLE ----------
def set_wallpaper_style(style):

    key = winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        r"Control Panel\Desktop",
        0,
        winreg.KEY_SET_VALUE
    )

    styles = {
        "Fill":    ("10", "0"),
        "Fit":     ("6",  "0"),
        "Stretch": ("2",  "0"),
        "Center":  ("0",  "0"),
        "Tile":    ("0",  "1")
    }

    wallpaper_style, tile = styles[style]

    winreg.SetValueEx(key, "WallpaperStyle", 0, winreg.REG_SZ, wallpaper_style)
    winreg.SetValueEx(key, "TileWallpaper",  0, winreg.REG_SZ, tile)

    winreg.CloseKey(key)

# ---------- GET CURRENT WALLPAPER ----------
def get_current_wallpaper():

    buffer = ctypes.create_unicode_buffer(512)

    ctypes.windll.user32.SystemParametersInfoW(
        0x0073,
        512,
        buffer,
        0
    )

    return buffer.value

# ---------- QUICK SWITCH (no GUI) ----------
def quick_switch():
    """Called when exe is launched with --quick-switch flag.
    Cycles through imported wallpapers in FCFS order and exits."""

    global cycle_index

    # filter to only existing files
    valid = [p for p in images if os.path.exists(p)]

    if not valid:
        sys.exit(0)

    # clamp index in case list shrank since last run
    cycle_index = cycle_index % len(valid)

    path  = valid[cycle_index]
    style = image_styles.get(path, "Fill")

    set_wallpaper_style(style)

    ctypes.windll.user32.SystemParametersInfoW(
        20,
        0,
        path,
        3
    )

    # advance index — next quick-switch will apply the following wallpaper
    cycle_index = (cycle_index + 1) % len(valid)

    save_data()

    sys.exit(0)

# ---------- ROOT ----------
root = ctk.CTk()

root.title("Quick Wallpaper Switch")
root.geometry("1200x800")
root.minsize(800, 600)

# ---------- RESPONSIVE GRID ----------
root.grid_rowconfigure(0, weight=0)   # current wallpaper section — fixed
root.grid_rowconfigure(1, weight=0)   # gallery title — fixed
root.grid_rowconfigure(2, weight=1)   # gallery — expands
root.grid_rowconfigure(3, weight=0)   # import button — fixed
root.grid_columnconfigure(0, weight=1)

# ---------- SAVE ON CLOSE ----------
root.protocol("WM_DELETE_WINDOW", lambda: [save_data(), root.destroy()])

# ---------- UPDATE CURRENT PREVIEW ----------
def current_wallpaper():

    wallpaper_path = get_current_wallpaper()

    if not wallpaper_path:
        return

    img = Image.open(wallpaper_path)

    # fixed preview size — doesn't grow with window
    img.thumbnail((480, 240))

    ctk_img = ctk.CTkImage(
        light_image=img,
        dark_image=img,
        size=img.size
    )

    current_wallpaper_label.configure(
        image=ctk_img,
        text=""
    )

    current_wallpaper_label.image = ctk_img

# ---------- SWITCH WALLPAPER ----------
def switch_wallpaper(path, style):

    old_wallpaper = get_current_wallpaper()

    # set style first
    set_wallpaper_style(style)

    # set wallpaper
    ctypes.windll.user32.SystemParametersInfoW(
        20,
        0,
        path,
        3
    )

    # persist chosen style for this wallpaper (used by quick-switch)
    image_styles[path] = style

    # add previous wallpaper to gallery
    if old_wallpaper and old_wallpaper not in images:

        images.append(old_wallpaper)

        imported_images(old_wallpaper)

    save_data()

    current_wallpaper()

# ---------- DELETE WALLPAPER ----------
def delete_wallpaper(path, widget):

    if path in images:
        images.remove(path)

    if path in image_styles:
        del image_styles[path]

    widget.destroy()

    save_data()

# ---------- IMPORT IMAGE ----------
def imported_images(path):

    global image_count

    if not os.path.exists(path):
        return

    img = Image.open(path)

    img.thumbnail((200, 110))

    ctk_img = ctk.CTkImage(
        light_image=img,
        dark_image=img,
        size=img.size
    )

    # ---------- CARD FRAME ----------
    card = ctk.CTkFrame(gallery_frame, corner_radius=10)

    row = image_count // 4
    col = image_count % 4

    card.grid(
        row=row,
        column=col,
        padx=10,
        pady=10,
        sticky="nsew"
    )

    # ---------- STYLE DROPDOWN ----------
    saved_style = image_styles.get(path, "Fill")
    style_var   = ctk.StringVar(value=saved_style)

    style_menu = ctk.CTkOptionMenu(
        card,
        values=["Fill", "Fit", "Stretch", "Center", "Tile"],
        variable=style_var,
        width=180,
        command=lambda s, p=path: image_styles.update({p: s}) or save_data()
    )

    style_menu.pack(pady=(8, 4), padx=10)

    # ---------- IMAGE BUTTON ----------
    image_button = ctk.CTkButton(
        card,
        image=ctk_img,
        text="",
        width=210,
        height=115,
        corner_radius=8,
        fg_color="transparent",
        hover_color=("gray80", "gray25")
    )

    image_button.pack(padx=10, pady=(4, 4))

    # ---------- HINT LABEL ----------
    hint_label = ctk.CTkLabel(
        card,
        text="⬡ double-click to set  ·  right-click to remove",
        font=("Arial", 9),
        text_color=("gray50", "gray55")
    )

    hint_label.pack(pady=(0, 8))

    # ---------- DOUBLE CLICK TO SWITCH ----------
    image_button.bind(
        "<Double-Button-1>",
        lambda event, p=path, s=style_var:
        switch_wallpaper(p, s.get())
    )

    # ---------- RIGHT CLICK DELETE ----------
    image_button.bind(
        "<Button-3>",
        lambda event, p=path, w=card:
        delete_wallpaper(p, w)
    )

    image_button.image = ctk_img

    image_count += 1

# ---------- IMPORT BUTTON ----------
def button_callback():

    file_path = filedialog.askopenfilename(
        filetypes=[("Images", "*.png *.jpg *.jpeg")]
    )

    if not file_path:
        return

    if file_path not in images:

        images.append(file_path)

        imported_images(file_path)

        save_data()

# ---------- CURRENT WALLPAPER FRAME ----------
current_frame = ctk.CTkFrame(root, corner_radius=12)

current_frame.grid(
    row=0,
    column=0,
    padx=20,
    pady=(20, 8),
    sticky="ew"
)

current_title = ctk.CTkLabel(
    current_frame,
    text="Current Wallpaper",
    font=("Arial", 20, "bold")
)

current_title.pack(pady=(10, 4))

current_wallpaper_label = ctk.CTkLabel(
    current_frame,
    text=""
)

current_wallpaper_label.pack(pady=(0, 10))

# ---------- GALLERY TITLE ----------
gallery_title = ctk.CTkLabel(
    root,
    text="Imported Wallpapers",
    font=("Arial", 20, "bold")
)

gallery_title.grid(
    row=1,
    column=0,
    pady=(4, 4),
    sticky="w",
    padx=24
)

# ---------- GALLERY FRAME ----------
gallery_frame = ctk.CTkScrollableFrame(
    root,
    corner_radius=12
)

gallery_frame.grid(
    row=2,
    column=0,
    padx=20,
    pady=(0, 8),
    sticky="nsew"
)

# ---------- IMPORT BUTTON ----------
import_button = ctk.CTkButton(
    root,
    text="＋  Import Wallpaper",
    command=button_callback,
    height=44,
    width=220,
    corner_radius=10,
    font=("Arial", 14, "bold")
)

import_button.grid(
    row=3,
    column=0,
    pady=(4, 16)
)

# ---------- RESTORE SAVED GALLERY ----------
for saved_path in images[:]:
    if os.path.exists(saved_path):
        imported_images(saved_path)
    else:
        images.remove(saved_path)   # prune missing files

# ---------- INITIAL LOAD ----------
current_wallpaper()

# ---------- RUN ----------
root.mainloop()