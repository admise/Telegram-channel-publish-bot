# Telegram Bot: Content Management and Moderation

This repository contains a Python-based Telegram bot designed to facilitate public content sharing on a Telegram channel with moderation features. The bot is built using the `python-telegram-bot` library and includes functionality for posting user-generated content, managing intervals between posts, banning/unbanning users, and more.

---

## Features

1. **User Content Sharing:**
   - Users can send messages containing text, photos, videos, or documents with captions to be published on a designated Telegram channel.
   - Messages are posted to the channel with the option for readers to directly contact the author.

2. **Moderation Tools:**
   - Admins can:
     - Ban or unban users.
     - Reply to users directly from the bot.
     - Remove messages from the channel.
   - Admin-only commands ensure secure moderation.

3. **Interval Management:**
   - Users must wait a configurable amount of time between posts.
   - The default interval is 72 hours, but it can be adjusted by the admin.

4. **Statistics and Maintenance Mode:**
   - Tracks total users and messages.
   - Admins can enable/disable maintenance mode to pause user interactions.

5. **Channel Subscription Validation:**
   - Ensures users are subscribed to the designated channel before allowing them to post.

---

## Prerequisites

- Python 3.7+
- Telegram bot API token
- Environment variables for configuration

---

## Setup

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/admise/Telegram-channel-publish-bot
   cd Telegram-channel-publish-bot
   ```

2. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set Environment Variables:**
   Create a `.env` file in the project root and define the following variables:

   ```env
   TELEGRAM_API_TOKEN=your-telegram-bot-token
   ADMIN_ID=your-admin-user-id
   CHANNEL_ID=@your-channel-id
   CHANNEL_NAME=@your-channel-name
   POST_INTERVAL=72  # Interval between posts in hours
   ```

4. **Run the Bot:**

   ```bash
   python3 main.py
   ```

---

## Commands

### User Commands

- **Start:** `/start`  
  Displays a welcome message with usage instructions.

### Admin Commands

- **Set Post Interval:** `/set_interval <hours>`  
  Updates the interval between user posts (admin-only).

- **Get Current Interval:** `/get_interval`  
  Shows the current post interval.

- **Ban User:** `/ban <user_id> <reason>`  
  Bans a user from interacting with the bot.

- **Unban User:** `/unban <user_id>`  
  Removes a user from the ban list.

- **View Banned Users:** `/banned_list`  
  Displays a list of banned users.

- **Reply to User:** `/reply <user_id> <message>`  
  Sends a direct reply to a user.

- **Enable/Disable Maintenance Mode:** `/maintenance`  
  Toggles maintenance mode on or off.

- **View Bot Statistics:** `/stats`  
  Displays bot usage statistics.

---

## File Structure

```plaintext
.
├── main.py               # Main script containing bot logic
├── web_app_routes.py     # Flask web app integration (if applicable)
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables (not included in repo)
```

---

## Logging

The bot uses the Python `logging` module to log important events and errors. Logs are output to the console by default and include details like user interactions, errors, and admin actions.

---

## Deployment

### Local Deployment

Run the bot locally by executing:

```bash
python3 main.py
```

### Deployment on Servers

You can deploy the bot on cloud services like AWS, Google Cloud, or Heroku. Ensure the `.env` file is properly configured and dependencies are installed on the server.

---

## Contributing

1. Fork the repository.
2. Create a new feature branch.
3. Commit changes and open a pull request.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

## Contact

For questions or feedback, contact the repository maintainer at sergei-700@mail.ru.

