# Quick Wallpaper Switch

A lightweight Windows app to add and manage wallpapers with a quick Hotkey 

---

## What it does

- Build a personal wallpaper gallery by importing images
- Double-click any wallpaper in the gallery to set it immediately
- Set a wallpaper style per image including: Fill, Fit, Stretch, Center, or Tile
- **Quick Switch mode**  cycles through your gallery in the background with a hotkey, no window opens
- Your gallery, styles, and cycle position all persist between sessions

---

## Getting Started

Download `QuickWallpaper.exe` from [Releases](https://github.com/Viijval/QuickSwitchWallpaper/releases) and run it. No install needed.

**First time setup**
1. Open the app and import a few wallpapers using the **＋ Import Wallpaper** button
2. Set the style for each one using the dropdown on the card
3. Double-click any card to set it as your wallpaper

**Setting up the Quick Switch hotkey**
1. Right-click `QuickWallpaper.exe` → **Create shortcut**
2. Right-click the shortcut → **Properties**
3. Set the Target field to: (IMPORTANT)
   ```
   "C:\path\to\QuickWallpaper.exe" --quick-switch
   ```
4. Click the **Shortcut key** field and press your combo (e.g. `Ctrl + Alt + W`)
5. Hit **Apply → OK**

That's it. The hotkey will now silently cycle to the next wallpaper every time you press it.
or just double click.
If you want to get into the app again, open the .exe file instead of the shortcut and you can customize the wallpapers as you wish.
Right click to delete, double click to set as wallpaper inside the app.
---

## Build from Source

```bash
pip install customtkinter pillow pyinstaller
pyinstaller --onefile --windowed --name QuickWallpaper main.py
```

Output will be in the `dist/` folder.

---

## Notes

- Wallpaper files are referenced by path, not copied — don't move or delete them after importing
- Gallery data is stored at `%AppData%\QuickWallpaper\data.json`
- Windows only

---

Built with Python + CustomTkinter.
