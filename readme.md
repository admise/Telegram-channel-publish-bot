[🇷🇺 Русский](README.ru.md) | [🇬🇧 English](README.en.md)

# Telegram Bot: Управление контентом и модерация | Content Management and Moderation

Этот репозиторий содержит Telegram-бота, который упрощает процесс публикации пользовательского контента в Telegram-канале с возможностью модерации. Бот построен с использованием библиотеки `python-telegram-bot` и включает функции для публикации контента, управления интервалами между публикациями, блокировки/разблокировки пользователей и многое другое.  
This repository contains a Python-based Telegram bot designed to simplify the process of publishing user-generated content to a Telegram channel with moderation capabilities. The bot is built using the `python-telegram-bot` library and includes features for content posting, managing intervals between posts, banning/unbanning users, and more.

---

## Возможности | Features

1. **Публикация пользовательского контента | User Content Sharing:**
   - Пользователи могут отправлять сообщения с текстом, фотографиями, видео или документами и описанием для публикации в указанном Telegram-канале.  
     Users can send messages containing text, photos, videos, or documents with captions to be published on a designated Telegram channel.
   - Сообщения публикуются с кнопкой для читателей, позволяющей связаться с автором.  
     Messages are posted to the channel with a button allowing readers to contact the author.

2. **Инструменты модерации | Moderation Tools:**
   - Администраторы могут:  
     Admins can:
     - Блокировать или разблокировать пользователей.  
       Ban or unban users.
     - Отправлять ответы пользователям напрямую через бота.  
       Reply directly to users via the bot.
     - Удалять сообщения из канала.  
       Delete messages from the channel.
   - Команды доступны только администратору для обеспечения безопасности.  
     Admin-only commands ensure secure moderation.

3. **Управление интервалами | Interval Management:**
   - Пользователи должны ждать настраиваемый промежуток времени между публикациями.  
     Users must wait a configurable amount of time between posts.
   - По умолчанию интервал составляет 72 часа, но администратор может его изменить.  
     The default interval is 72 hours, but it can be adjusted by the admin.

4. **Статистика и режим обслуживания | Statistics and Maintenance Mode:**
   - Ведется подсчет общего количества пользователей и сообщений.  
     Tracks the total number of users and messages.
   - Администратор может включить или отключить режим обслуживания, чтобы приостановить взаимодействие с ботом.  
     Admins can enable or disable maintenance mode to pause user interactions.

5. **Проверка подписки на канал | Channel Subscription Validation:**
   - Проверяет, подписан ли пользователь на указанный канал, перед тем как разрешить публикацию.  
     Ensures users are subscribed to the designated channel before allowing them to post.

---

## Требования | Requirements

- Python 3.7+  
- Telegram bot API token  
- Переменные окружения для настройки  
  Environment variables for configuration

---

## Установка | Setup

1. **Клонирование репозитория | Clone the Repository:**

   ```bash
   git clone https://github.com/admise/Telegram-channel-publish-bot
   cd Telegram-channel-publish-bot
   ```

2. **Установка зависимостей | Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Настройка переменных окружения | Set Environment Variables:**
   Создайте файл `.env` в корневой папке проекта и укажите следующие переменные:  
   Create a `.env` file in the project root and define the following variables:

   ```env
   TELEGRAM_API_TOKEN=ваш-токен-бота | your-telegram-bot-token
   ADMIN_ID=ваш-id-администратора | your-admin-user-id
   CHANNEL_ID=@id-вашего-канала | @your-channel-id
   CHANNEL_NAME=@имя-вашего-канала | @your-channel-name
   POST_INTERVAL=72  # Интервал между публикациями в часах | Interval between posts in hours
   ```

4. **Запуск бота | Run the Bot:**

   ```bash
   python3 main.py
   ```

---

## Команды | Commands

### Команды для пользователей | User Commands

- **Начать | Start:** `/start`  
  Отображает приветственное сообщение с инструкциями.  
  Displays a welcome message with usage instructions.

### Команды для администратора | Admin Commands

- **Установить интервал между публикациями | Set Post Interval:** `/set_interval <часы | hours>`  
  Изменяет интервал между публикациями (только для администратора).  
  Updates the interval between user posts (admin-only).

- **Проверить текущий интервал | Get Current Interval:** `/get_interval`  
  Отображает текущий интервал между публикациями.  
  Shows the current post interval.

- **Заблокировать пользователя | Ban User:** `/ban <id_пользователя | user_id> <причина | reason>`  
  Блокирует пользователя от взаимодействия с ботом.  
  Bans a user from interacting with the bot.

- **Разблокировать пользователя | Unban User:** `/unban <id_пользователя | user_id>`  
  Удаляет пользователя из списка заблокированных.  
  Removes a user from the ban list.

- **Список заблокированных пользователей | View Banned Users:** `/banned_list`  
  Отображает список заблокированных пользователей.  
  Displays a list of banned users.

- **Ответ пользователю | Reply to User:** `/reply <id_пользователя | user_id> <сообщение | message>`  
  Отправляет прямой ответ пользователю.  
  Sends a direct reply to a user.

- **Включить/выключить режим обслуживания | Enable/Disable Maintenance Mode:** `/maintenance`  
  Переключает режим обслуживания.  
  Toggles maintenance mode on or off.

- **Посмотреть статистику | View Bot Statistics:** `/stats`  
  Отображает статистику использования бота.  
  Displays bot usage statistics.

---

## Структура файлов | File Structure

```plaintext
.
├── main.py               # Основной скрипт с логикой бота | Main script containing bot logic
├── web_app_routes.py     # Интеграция с веб-приложением Flask (если используется) | Flask web app integration (if applicable)
├── requirements.txt      # Зависимости Python | Python dependencies
├── .env                  # Переменные окружения (не включены в репозиторий) | Environment variables (not included in repo)
```

---

## Логирование | Logging

Бот использует модуль Python `logging` для записи важных событий и ошибок. Логи выводятся в консоль по умолчанию и содержат детали, такие как взаимодействия с пользователями, ошибки и действия администратора.  
The bot uses the Python `logging` module to log important events and errors. Logs are output to the console by default and include details like user interactions, errors, and admin actions.

---

## Развертывание | Deployment

### Локальное развертывание | Local Deployment

Запустите бота локально с помощью команды:  
Run the bot locally by executing:

```bash
python3 main.py
```

### Развертывание на серверах | Deployment on Servers

Вы можете развернуть бота на облачных сервисах, таких как AWS, Google Cloud или Heroku. Убедитесь, что файл `.env` правильно настроен, а зависимости установлены на сервере.  
You can deploy the bot on cloud services like AWS, Google Cloud, or Heroku. Ensure the `.env` file is properly configured and dependencies are installed on the server.

---

## Вклад в проект | Contributing

1. Форкните репозиторий.  
   Fork the repository.
2. Создайте новую ветку для своей функции.  
   Create a new feature branch.
3. Зафиксируйте изменения и откройте pull request.  
   Commit changes and open a pull request.

---

## Лицензия | License

Этот проект лицензирован под лицензией MIT. Подробности см. в файле `LICENSE`.  
This project is licensed under the MIT License. See the `LICENSE` file for details.

---

## Контакты | Contact

Если у вас есть вопросы или отзывы, свяжитесь с поддержкой по адресу sergei-700@mail.ru.  
For questions or feedback, contact the repository maintainer at sergei-700@mail.ru.

