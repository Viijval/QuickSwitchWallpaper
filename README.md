Quick Wallpaper Switch
Tired of digging through File Explorer every time you want to change your wallpaper? Yeah, same.
This is a lightweight Windows app that lets you build a gallery of wallpapers and switch between them instantly — either through the UI or a single keyboard shortcut, no window, no clicks.

Features

Import wallpapers and manage them in a visual gallery
Double-click any wallpaper in the gallery to set it instantly
Quick Switch — cycles through your wallpapers silently via a hotkey (no app window)
Per-wallpaper style settings (Fill, Fit, Stretch, Center, Tile)
Everything persists — your gallery and cycle position are saved across sessions


Setup
Run the app
Just double-click QuickWallpaper.exe. Import some wallpapers, pick your styles.
Set up the Quick Switch hotkey

Right-click QuickWallpaper.exe → Create shortcut
Right-click the shortcut → Properties
Set Target to:

   "C:\path\to\QuickWallpaper.exe" --quick-switch

Set a Shortcut key (e.g. Ctrl + Alt + W)
Apply → OK

Now that combo cycles your wallpapers in the background — no window, instant switch.

Build from source
bashpip install customtkinter pillow pyinstaller
pyinstaller --onefile --windowed --name QuickWallpaper wallpaper_switch.py
Exe will be in the dist folder.

Data
Your gallery is saved at %AppData%\QuickWallpaper\data.json. Wallpaper files themselves aren't moved or copied — just referenced by path, so don't delete or move them.

Built with Python, CustomTkinter, and mild frustration with the Windows Settings app.
