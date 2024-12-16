from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, Filters
import os
import apscheduler.jobstores.base
import logging
from datetime import timedelta

from telegram.ext import CallbackContext, ConversationHandler
from dotenv import load_dotenv

load_dotenv()
def handle_admin_reply(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    admin_id = int(os.environ.get('ADMIN_ID', 0))
    
    if query.from_user.id != admin_id:
        query.answer("У вас нет прав для выполнения этой команды.")
        return
    
    user_id = int(query.data.split('_')[1])
    context.user_data['replying_to'] = user_id
    query.answer()
    query.edit_message_text(f"Введите ваш ответ для пользователя {user_id}")
    return ConversationHandler.END
from flask import Flask, render_template, url_for, redirect
import os
import logging
import threading
import time
from datetime import datetime
from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext, Filters, CallbackQueryHandler
from web_app_routes import app

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Global variables
banned_users = set()
TELEGRAM_API_TOKEN = os.getenv('TELEGRAM_API_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')
CHANNEL_NAME = os.getenv('CHANNEL_NAME')
POST_INTERVAL = int(os.environ.get('POST_INTERVAL', 72)) * 3600  # Get interval from environment variable
MAINTENANCE_MODE = False  # Global variable to track maintenance mode

# Global variables for statistics
TOTAL_USERS = set()
TOTAL_MESSAGES = 0

def ban_user(update: Update, context: CallbackContext) -> None:
    admin_id = int(os.environ.get('ADMIN_ID', 0))
    if update.effective_user.id != admin_id:
        update.message.reply_text("У вас нет прав для выполнения этой команды.")
        return
    if context.args:
        try:
            user_id = int(context.args[0])
            reason = ' '.join(context.args[1:]) if len(context.args) > 1 else "Причина не указана"
            banned_users.add(user_id)
            ban_message = f"🚫 Пользователь {user_id} был заблокирован.\n📝 Причина: {reason}"
            update.message.reply_text(ban_message)
            logger.info(f"Администратор заблокировал пользователя {user_id}. Причина: {reason}")
            
            # Notify the banned user
            try:
                context.bot.send_message(chat_id=user_id, text=f"Вы были заблокированы администратором.\nПричина: {reason}")
            except telegram.error.Unauthorized:
                logger.warning(f"Не удалось отправить уведомление пользователю {user_id} о блокировке.")
        except ValueError:
            update.message.reply_text("Пожалуйста, укажите действительный ID пользователя.")
    else:
        update.message.reply_text("Пожалуйста, укажите ID пользователя для блокировки и, при желании, причину.")

def banned_list(update: Update, context: CallbackContext) -> None:
    admin_id = int(os.environ.get('ADMIN_ID', 0))
    if update.effective_user.id != admin_id:
        update.message.reply_text("У вас нет прав для выполнения этой команды.")
        return
    
    if not banned_users:
        update.message.reply_text("Список заблокированных пользователей пуст.")
    else:
        banned_list_text = "Список заблокированных пользователей:\n" + "\n".join(map(str, banned_users))
        update.message.reply_text(banned_list_text)

def unban_user(update: Update, context: CallbackContext) -> None:
    admin_id = int(os.environ.get('ADMIN_ID', 0))
    if update.effective_user.id != admin_id:
        update.message.reply_text("У вас нет прав для выполнения этой команды.")
        return
    if context.args:
        try:
            user_id = int(context.args[0])
            if user_id in banned_users:
                banned_users.remove(user_id)
                unban_message = f"✅ Пользователь {user_id} был разблокирован."
                update.message.reply_text(unban_message)
                logger.info(f"Администратор разблокировал пользователя {user_id}.")
                
                # Notify the unbanned user
                try:
                    context.bot.send_message(chat_id=user_id, text="Вы были разблокированы администратором. Теперь вы снова можете отправлять сообщения.")
                except telegram.error.Unauthorized:
                    logger.warning(f"Не удалось отправить уведомление пользователю {user_id} о разблокировке.")
            else:
                update.message.reply_text(f"❗️ Пользователь {user_id} не был заблокирован.")
        except ValueError:
            update.message.reply_text("Пожалуйста, укажите действительный ID пользователя.")
    else:
        update.message.reply_text("Пожалуйста, укажите ID пользователя для разблокировки.")

def reply_to_user(update: Update, context: CallbackContext) -> None:
    admin_id = int(os.environ.get('ADMIN_ID', 0))
    if update.effective_user.id != admin_id:
        update.message.reply_text("У вас нет прав для выполнения этой команды.")
        return
    
    # Check if this is a reply to a message
    if update.message.reply_to_message:
        reply_text = update.message.reply_to_message.text
        if reply_text.startswith("/reply"):
            try:
                user_id = int(reply_text.split()[1])
                message_text = update.message.text
            except (ValueError, IndexError):
                update.message.reply_text("Не удалось извлечь ID пользователя из оригинального сообщения.")
                return
        else:
            update.message.reply_text("Это сообщение не содержит команду /reply.")
            return
    else:
        # If it's a direct command
        if len(context.args) < 2:
            update.message.reply_text("Пожалуйста, укажите ID пользователя и текст сообщения.")
            return
        try:
            user_id = int(context.args[0])
            message_text = ' '.join(context.args[1:])
        except ValueError:
            update.message.reply_text("Пожалуйста, укажите действительный ID пользователя.")
            return
    
    try:
        admin_message = f"Сообщение от администратора:\n\n{message_text}"
        context.bot.send_message(chat_id=user_id, text=admin_message)
        update.message.reply_text(f"Сообщение успешно отправлено пользователю {user_id}.")
        logger.info(f"Администратор отправил сообщение пользователю {user_id}: {message_text}")
    except telegram.error.Unauthorized:
        update.message.reply_text(f"Не удалось отправить сообщение пользователю {user_id}. Возможно, пользователь заблокировал бота.")
    except Exception as e:
        update.message.reply_text(f"Произошла ошибка при отправке сообщения: {str(e)}")
        logger.error(f"Ошибка при отправке сообщения пользователю {user_id}: {str(e)}")

def handle_message(update: Update, context: CallbackContext) -> None:
    global TOTAL_USERS, TOTAL_MESSAGES
    if 'reminder_job' in context.user_data:
        try:
            context.user_data['reminder_job'].schedule_removal()
        except apscheduler.jobstores.base.JobLookupError:
            logger.warning(f"Job not found for user {update.effective_user.id if update.effective_user else 'Unknown'}")
    if update.effective_user is None:
        logger.error("Received update with no effective user")
        return
    
    user = update.effective_user
    TOTAL_USERS.add(user.id)
    
    if MAINTENANCE_MODE and user.id != int(os.environ.get('ADMIN_ID', 0)):
        update.message.reply_text("Извините, бот находится на техническом обслуживании. Пожалуйста, попробуйте позже.")
        return
    user_id = user.id
    
    if user_id in banned_users:
        update.message.reply_text("Вы были заблокированы и не можете отправлять сообщения.")
        return
    
    if update.message is None:
        logger.error(f"Received update with no message for user {user_id}")
        return
    
    message = update.message
    
    # Check if the message is empty (no text, photo, video, or document)
    if not message.text and not message.photo and not message.video and not message.document:
        # Silently ignore empty messages
        return
    
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Schedule reminder for the next possible post
    post_interval = int(os.environ.get('POST_INTERVAL', 72)) * 3600
    next_post_time = datetime.now() + timedelta(seconds=post_interval)
    context.user_data['reminder_job'] = context.job_queue.run_once(send_reminder, post_interval, context=user_id)
    logger.info(f"Scheduled reminder for user {user_id} at {next_post_time}")
    
    # Проверка подписки на канал
    try:
        chat_member = context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        if chat_member.status not in ['member', 'administrator', 'creator']:
            channel_name = os.getenv('CHANNEL_NAME', '')
            if channel_name:
                channel_name = channel_name.replace('@', '')
                keyboard = [[InlineKeyboardButton("🌟 Подписаться на канал 🌟", url=f"https://t.me/{channel_name}")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                update.message.reply_text(
                    f"👋 Привет, дорогой друг! 🤗\n\n"
                    f"🌈 Мы рады видеть тебя здесь! Чтобы полностью погрузиться в наше сообщество, тебе нужно подписаться на наш канал. 🚀✨\n\n"
                    f"🎉 Там тебя ждет:\n"
                    f"   🔹 Уникальный контент\n"
                    f"   🔹 Интересные обсуждения\n"
                    f"   🔹 Новые друзья и единомышленники\n\n"
                    f"🔥 Просто нажми на кнопку ниже и подпишись! 🌟\n\n"
                    f"Мы с нетерпением ждем тебя в нашей дружной семье! 🤗💖",
                    reply_markup=reply_markup
                )
            else:
                update.message.reply_text("Извините, но в данный момент невозможно проверить подписку на канал. Пожалуйста, попробуйте позже.")
            return
    except telegram.error.TelegramError as e:
        logger.error(f"Error checking channel subscription: {str(e)}")
        update.message.reply_text("Произошла ошибка при проверке подписки. Пожалуйста, попробуйте позже.")
        return
    
    if message.document:
        content_type = "документ"
    elif message.photo:
        content_type = "фото"
    elif message.video:
        content_type = "видео"
    else:
        content_type = "текстовое сообщение"
    
    log_message = f"📅 {current_time}\n👤 Пользователь {user.id} ({'@' + user.username if user.username else 'без имени пользователя'}) отправил {content_type}."
    
    if message.caption:
        log_message += f"\n📝 {message.caption}"
    elif message.text:
        log_message += f"\n📝 {message.text}"
    
    logger.info(log_message)
    
    admin_id = int(os.environ.get('ADMIN_ID', 0))
    if admin_id:
        user_info = f"{user.first_name} (@{user.username})" if user.username else user.first_name or "без имени пользователя"
        admin_message = (
            f"👤 Пользователь {user_info}\n"
            f"🆔 ID: {user.id}\n"
            f"📝 Сообщение:\n{message.text or message.caption}\n\n"
            f"Команды:\n"
            f"/reply {user.id}\n"
            f"/ban {user.id}\n"
            f"/unban {user.id}"
        )
        context.bot.send_message(chat_id=admin_id, text=admin_message)
    
    if message.document or message.photo or message.video:
        if message.caption:
            current_time = int(time.time())
            last_post_time = context.user_data.get('last_post_time', 0)
            
            if current_time - last_post_time < POST_INTERVAL:
                remaining_time = POST_INTERVAL - (current_time - last_post_time)
                hours, remainder = divmod(remaining_time, 3600)
                minutes, _ = divmod(remainder, 60)
                interval_hours = POST_INTERVAL // 3600
                cooldown_message = f"⏳ Ой-ой! Нужно немного подождать! 🕰️\n\nТы сможешь отправить новое сообщение через {int(hours)} часов и {int(minutes)} минут. Интервал между сообщениями составляет {interval_hours} часов. Используй это время, чтобы придумать что-нибудь супер-крутое! 🚀✨"
                update.message.reply_text(cooldown_message)
                
                if admin_id:
                    admin_message = f"🕒 Пользователь {user.id} (@{user.username if user.username else 'без имени пользователя'}) попытался отправить сообщение раньше времени.\n\nСледующее сообщение можно отправить через {int(hours)} часов и {int(minutes)} минут."
                    context.bot.send_message(chat_id=admin_id, text=admin_message)
                
                return
            
            try:
                if 'last_message' in context.user_data:
                    try:
                        context.bot.delete_message(chat_id=CHANNEL_ID, message_id=context.user_data['last_message'])
                    except Exception as e:
                        logger.warning(f"Не удалось удалить предыдущее сообщение: {str(e)}")

                button_text = f"Написать {user.first_name}" if user.first_name else f"Написать {user.username}" if user.username else "Написать автору"
                keyboard = [[InlineKeyboardButton(button_text, url=f"tg://user?id={user_id}")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                if message.document:
                    sent_message = context.bot.send_document(
                        chat_id=CHANNEL_ID,
                        document=message.document.file_id,
                        caption=message.caption,
                        reply_markup=reply_markup
                    )
                elif message.photo:
                    sent_message = context.bot.send_photo(
                        chat_id=CHANNEL_ID,
                        photo=message.photo[-1].file_id,
                        caption=message.caption,
                        reply_markup=reply_markup
                    )
                elif message.video:
                    sent_message = context.bot.send_video(
                        chat_id=CHANNEL_ID,
                        video=message.video.file_id,
                        caption=message.caption,
                        reply_markup=reply_markup
                    )
                
                context.user_data['last_message'] = sent_message.message_id
                context.user_data['last_post_time'] = current_time
                global TOTAL_MESSAGES
                TOTAL_MESSAGES += 1
                
                keyboard = [[InlineKeyboardButton("Удалить пост 🗑️", callback_data=f"delete_{sent_message.message_id}")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                interval_hours = POST_INTERVAL // 3600
                confirmation_message = update.message.reply_text(
                    f"🎉 Ура! Твой пост опубликован в канале! 🌟\n\n"
                    f"Предыдущий твой пост (если он был) удален. Следующий свой пост ты сможешь отправить через {interval_hours} часов. "
                    "Используй это время, чтобы создать что-то невероятное! 💡✨\n\n"
                    "Если хочешь удалить свой пост, нажми кнопку 'Удалить пост' ниже. "
                    "Кнопка будет активна в течение 5 минут после публикации. После этого она исчезнет автоматически.",
                    reply_markup=reply_markup
                )
                logger.info(f"Сообщение успешно отправлено в канал: {CHANNEL_ID}")
                # Schedule the button to be inactive after 5 minutes
                context.job_queue.run_once(remove_delete_button, 300, context={'chat_id': confirmation_message.chat_id, 'message_id': confirmation_message.message_id})
                logger.info(f"Scheduled removal of delete button for message {confirmation_message.message_id} in 5 minutes.")
            except Exception as e:
                error_message = f"Не удалось отправить сообщение: {str(e)}"
                logger.error(error_message)
                update.message.reply_text("😕 Ой, кажется, что-то пошло не так! Не удалось опубликовать твое сообщение. 🛠️\n\n"
                                         "Давай проверим настройки конфиденциальности в Telegram:\n\n"
                                         "1️⃣ Открой настройки Telegram\n"
                                         "2️⃣ Перейди в 'Конфиденциальность'\n"
                                         "3️⃣ Выбери 'Пересылка сообщений'\n"
                                         "4️⃣ Убедись, что опция 'Кто может добавлять ссылку на мой аккаунт при пересылке сообщений' установлена на 'Все'\n\n"
                                         "Если это не помогло, попробуй:\n"
                                         "🔄 Перезапустить Telegram\n"
                                         "🔁 Отправить сообщение еще раз\n\n"
                                         "Если проблема сохраняется, не расстраивайся! Свяжись с нашим администратором, и мы обязательно поможем! 🦸‍♂️")
        else:
            update.message.reply_text("📝 Ой! Кажется, ты забыл добавить описание к файлу. Добавь пару слов! ✨")
    else:
        update.message.reply_text("📸 Ой! Кажется, ты забыл прикрепить фото, видео или документ. Пожалуйста, добавь медиафайл с описанием, чтобы все могли увидеть твой пост на канале! 🌟")

def handle_callback_query(update: Update, context: CallbackContext) -> None:
    logger.debug("Начало выполнения функции handle_callback_query")
    query = update.callback_query
    
    callback_data = query.data.split("_")
    action = callback_data[0]
    message_id = int(callback_data[1]) if len(callback_data) > 1 else None
    
    logger.info(f"Получен callback_query: {action}")
    
    try:
        if action == "delete":
            logger.info(f"Попытка удаления сообщения {message_id}")
            try:
                # Пытаемся удалить сообщение напрямую
                context.bot.delete_message(chat_id=CHANNEL_ID, message_id=message_id)
                context.user_data.pop('last_message', None)
                context.user_data.pop('last_post_time', None)
                logger.info(f"Пользователь {update.effective_user.id} успешно удалил сообщение {message_id} из канала.")
                query.answer("Ваше сообщение успешно удалено из канала!")
                query.edit_message_text("Ваше сообщение было успешно удалено из канала.")
            except telegram.error.BadRequest as e:
                logger.error(f"Ошибка при удалении сообщения {message_id}: {str(e)}")
                query.answer("Не удалось удалить сообщение. Возможно, оно уже было удалено.")
                query.edit_message_text("Не удалось удалить сообщение. Возможно, оно уже было удалено.")
            except Exception as e:
                logger.error(f"Неожиданная ошибка при удалении сообщения {message_id}: {str(e)}", exc_info=True)
                query.answer("Произошла неожиданная ошибка. Пожалуйста, попробуйте позже.")
                query.edit_message_text("Произошла неожиданная ошибка. Пожалуйста, попробуйте позже.")
            # Schedule the button to be inactive after 5 minutes
            context.job_queue.run_once(remove_delete_button, 300, context={'chat_id': query.message.chat_id, 'message_id': message_id})
            logger.info(f"Scheduled removal of delete button for message {message_id} in 5 minutes.")
        elif action == "reply":
            logger.info(f"Обработка ответа для пользователя {message_id}")
            context.user_data['replying_to'] = message_id
            query.edit_message_text(f"Введите ваш ответ для пользователя {message_id}:")
            return ConversationHandler.END
        elif action == "ban":
            logger.info(f"Запрос на бан пользователя {message_id}")
            query.edit_message_text(f"Вы уверены, что хотите заблокировать пользователя {message_id}?",
                                    reply_markup=InlineKeyboardMarkup([[
                                        InlineKeyboardButton("Да", callback_data=f"confirm_ban_{message_id}"),
                                        InlineKeyboardButton("Нет", callback_data="cancel_ban")
                                    ]]))
        elif action == "confirm":
            logger.info(f"Подтверждение бана пользователя {message_id}")
            ban_user(update, context)
            query.edit_message_text(f"Пользователь {message_id} был заблокирован.")
        elif query.data == "cancel_ban":
            logger.info("Отмена бана пользователя")
            query.edit_message_text("Блокировка пользователя была отменена.")
        else:
            logger.warning(f"Получен неизвестный callback_query: {query.data}")
            query.answer("Неизвестная команда.")
    except Exception as e:
        logger.error(f"Ошибка при обработке callback_query: {str(e)}", exc_info=True)
        query.answer("Произошла ошибка при обработке вашего запроса.")
    
    logger.debug("Завершение выполнения функции handle_callback_query")
    
    if update.effective_message:
        if update.effective_message.document or update.effective_message.photo or update.effective_message.video:
            if update.effective_message.caption:
                current_time = int(time.time())
                last_post_time = context.user_data.get('last_post_time', 0)
                
                if current_time - last_post_time < POST_INTERVAL:
                    remaining_time = POST_INTERVAL - (current_time - last_post_time)
                    hours, remainder = divmod(remaining_time, 3600)
                    minutes, _ = divmod(remainder, 60)
                    cooldown_message = f"⏳ Ой-ой! Нужно немного подождать! 🕰️\n\nТы сможешь отправить новое сообщение через {int(hours)} часов и {int(minutes)} минут. Используй это время, чтобы придумать что-нибудь супер-крутое! 🚀✨"
                    update.effective_message.reply_text(cooldown_message)
                    
                    # Notify admin about the cooldown
                    admin_id = int(os.environ.get('ADMIN_ID', 0))
                    if admin_id:
                        admin_message = f"🕒 Пользователь {update.effective_user.id} (@{update.effective_user.username}) попытался отправить сообщение раньше времени.\n\n{cooldown_message}"
                        context.bot.send_message(chat_id=admin_id, text=admin_message)
                    
                    return
                
                try:
                    # Удаляем предыдущее сообщение пользователя
                    if 'last_message' in context.user_data:
                        try:
                            context.bot.delete_message(chat_id=CHANNEL_ID, message_id=context.user_data['last_message'])
                        except Exception as e:
                            logger.warning(f"Не удалось удалить предыдущее сообщение: {str(e)}")

                    # Создаем кнопку "Написать автору"
                    user_id = update.effective_user.id
                    keyboard = [[InlineKeyboardButton("Написать автору", url=f"tg://user?id={user_id}")]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    # Публикуем сообщение в канал
                    if update.effective_message.document:
                        sent_message = context.bot.send_document(
                            chat_id=CHANNEL_ID,
                            document=update.effective_message.document.file_id,
                            caption=update.effective_message.caption,
                            reply_markup=reply_markup
                        )
                    elif update.effective_message.photo:
                        sent_message = context.bot.send_photo(
                            chat_id=CHANNEL_ID,
                            photo=update.effective_message.photo[-1].file_id,
                            caption=update.effective_message.caption,
                            reply_markup=reply_markup
                        )
                    elif update.effective_message.video:
                        sent_message = context.bot.send_video(
                            chat_id=CHANNEL_ID,
                            video=update.effective_message.video.file_id,
                            caption=update.effective_message.caption,
                            reply_markup=reply_markup
                        )
                    
                    # Сохраняем информацию о новом сообщении и времени публикации
                    context.user_data['last_message'] = sent_message.message_id
                    context.user_data['last_post_time'] = current_time
                    
                    keyboard = [[InlineKeyboardButton("Удалить пост 🗑️", callback_data=f"delete_{sent_message.message_id}")]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    update.effective_message.reply_text(
                        "🎉 Ура! Твой пост опубликован в канале! 🌟\n\n"
                        "Предыдущий пост (если он было) удален. Следующий шедевр ты сможешь отправить через 72 часа. "
                        "Используй это время, чтобы создать что-то невероятное! 💡✨\n\n"
                        "Если хочешь удалить свой пост, нажми кнопку 'Удалить пост' ниже. "
                        "Кнопка будет активна в течение 5 минут после публикации.",
                        reply_markup=reply_markup
                    )
                    logger.info(f"Сообщение успешно отправлено в канал: {CHANNEL_ID}")
                except Exception as e:
                    error_message = f"Не удалось отправить сообщение: {str(e)}"
                    logger.error(error_message)
                    update.effective_message.reply_text("😕 Ой, кажется, что-то пошло не так! Не удалось опубликовать твое сообщение. 🛠️\n\n"
                                                        "Давай проверим настройки конфиденциальности в Telegram:\n\n"
                                                        "1️⃣ Открой настройки Telegram\n"
                                                        "2️⃣ Перейди в 'Конфиденциальность'\n"
                                                        "3️⃣ Выбери 'Пересылка сообщений'\n"
                                                        "4️⃣ Убедись, что опция 'Кто может добавлять ссылку на мой аккаунт при пересылке сообщений' установлена на 'Все'\n\n"
                                                        "Если это не помогло, попробуй:\n"
                                                        "🔄 Перезапустить Telegram\n"
                                                        "🔁 Отправить сообщение еще раз\n\n"
                                                        "Если проблема сохраняется, не расстраивайся! Свяжись с нашим супер-администратором, и мы обязательно поможем! 🦸‍♂️")
            else:
                update.effective_message.reply_text("📝 Ой! Кажется, ты забыл добавить описание к файлу. Добавь пару слов, чтобы все поняли, насколько он крутой! ✨")
        else:
            update.effective_message.reply_text("📸 Ой! Кажется, ты забыл прикрепить фото, видео или документ. Пожалуйста, добавь медиафайл с описанием, чтобы все могли насладиться твоим шедевром! 🌟")
    elif update.callback_query:
        query = update.callback_query
        if query.data.startswith("delete_"):
            message_id = int(query.data.split("_")[1])
            try:
                context.bot.delete_message(chat_id=CHANNEL_ID, message_id=message_id)
                query.answer("Сообщение удалено.")
            except Exception as e:
                logger.error(f"Ошибка при удалении сообщения: {str(e)}")
                query.answer("Не удалось удалить сообщение.")
        elif query.data.startswith("reply_"):
            user_id = int(query.data.split("_")[1])
            context.user_data['replying_to'] = user_id
            query.answer()
            query.edit_message_text(f"Введите ваш ответ для пользователя {user_id}:")

def setup_telegram_bot():
    if not TELEGRAM_API_TOKEN:
        logger.error("TELEGRAM_API_TOKEN is missing. Please set it in the Env Secrets tab.")
        print_setup_instructions()
        return False

    try:
        updater = Updater(TELEGRAM_API_TOKEN)
        dispatcher = updater.dispatcher
        
        # Add handlers here
        dispatcher.add_handler(CommandHandler("set_interval", set_interval))
        dispatcher.add_handler(CommandHandler("get_interval", get_interval))
        dispatcher.add_handler(MessageHandler(Filters.all & ~Filters.command, handle_message))
        dispatcher.add_handler(CommandHandler("ban", ban_user))
        dispatcher.add_handler(CommandHandler("banned_list", banned_list))
        dispatcher.add_handler(CommandHandler("unban", unban_user))
        dispatcher.add_handler(CommandHandler("reply", reply_to_user))
        dispatcher.add_handler(CommandHandler("start", start))
        dispatcher.add_handler(CommandHandler("maintenance", toggle_maintenance))
        dispatcher.add_handler(CommandHandler("stats", show_stats))
        dispatcher.add_handler(CallbackQueryHandler(handle_callback_query))
        return updater  # Return the updater object

    except Exception as e:
        logger.error(f"An error occurred while setting up the Telegram bot: {str(e)}")
        return False

def run_telegram_bot(updater):
    logger.info(f"Starting Telegram bot @{updater.bot.username}")
    # Start polling
    updater.start_polling()
    logger.info(f"Bot @{updater.bot.username} is now running.")
    print(f"🎉 Bot @{updater.bot.username} is now connected and ready to use! 🎉")
    print(f"🚀 Click here to start chatting: https://t.me/{updater.bot.username} 🚀")
    updater.idle()

def main():
    try:
        logging.info("Setting up Telegram bot")
        updater = setup_telegram_bot()
        if not updater:
            logging.error("Failed to set up Telegram bot. Exiting.")
            return
        
        logging.info("Starting Telegram bot")
        run_telegram_bot(updater)
    except Exception as e:
        logging.error(f"An error occurred while setting up or running the Telegram bot: {str(e)}")
        logging.debug("Exception details", exc_info=True)
    finally:
        logging.info("Bot has been stopped")

def start(update: Update, context: CallbackContext) -> None:
    interval_hours = POST_INTERVAL // 3600
    welcome_message = (
        "👋 Привет! Добро пожаловать в наш уникальный бот для обмена публичными сообщениями на канале! 🎨✨\n\n"
        "🤖 Я здесь, чтобы помочь вам поделиться вашими постами с нашим сообществом.\n\n"
        "🚀 Вот как это работает:\n"
        "1️⃣ Отправьте мне ваше сообщение с фото, видео или документом и кратким описанием.\n"
        "2️⃣ Я автоматически опубликую его в нашем канале, где все смогут увидеть ваше творчество!\n"
        "3️⃣ Другие участники смогут связаться с вами, если ваш пост заинтересует их.\n\n"
        f"⏳ Помните, вы можете отправлять новые сообщения каждые {interval_hours} часов. Используйте это время, чтобы создать что-то действительно особенное!\n\n"
        "🌟 Готовы начать? Отправьте ваше первое сообщение!\n\n"
    )
    update.message.reply_text(welcome_message)
def set_interval(update: Update, context: CallbackContext) -> None:
    admin_id = int(os.environ.get('ADMIN_ID', 0))
    if update.effective_user.id != admin_id:
        update.message.reply_text("У вас нет прав для выполнения этой команды.")
        return
    
    if not context.args or not context.args[0].isdigit():
        update.message.reply_text("Пожалуйста, укажите интервал в часах. Например: /set_interval 48")
        return
    
    new_interval = int(context.args[0])
    os.environ['POST_INTERVAL'] = str(new_interval)
    global POST_INTERVAL
    POST_INTERVAL = new_interval * 3600
    
    update.message.reply_text(f"Интервал между постами установлен на {new_interval} часов.")
    logger.info(f"Администратор изменил интервал между постами на {new_interval} часов.")

def get_interval(update: Update, context: CallbackContext) -> None:
    current_interval = int(os.environ.get('POST_INTERVAL', 72))
    update.message.reply_text(f"Текущий интервал между постами: {current_interval} часов.")

def send_reminder(context: CallbackContext):
    job = context.job
    user_id = job.context
    interval_hours = int(os.environ.get('POST_INTERVAL', 72))
    reminder_message = (
        f"🎉 Привет! Прошло {interval_hours} часов с вашего последнего поста. 🕒\n\n"
        "Теперь вы можете отправить новое сообщение в канал! 🚀\n"
        "Поделитесь своими новыми идеями, фото или видео. Мы с нетерпением ждем вашего нового контента! ✨\n\n"
        "Если у вас есть что-то интересное, просто отправьте это мне, и я опубликую в канале. 😊"
    )
    context.bot.send_message(chat_id=user_id, text=reminder_message)

def remove_delete_button(context: CallbackContext):
    job_data = context.job.context
    try:
        context.bot.edit_message_reply_markup(chat_id=job_data['chat_id'], message_id=job_data['message_id'], reply_markup=None)
        logger.info(f"Delete button removed for message {job_data['message_id']}.")
    except telegram.error.BadRequest as e:
        if "Message is not modified" in str(e):
            logger.info(f"Delete button was already removed for message {job_data['message_id']}.")
        else:
            logger.error(f"Failed to remove delete button for message {job_data['message_id']}: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error while removing delete button for message {job_data['message_id']}: {str(e)}")
def toggle_maintenance(update: Update, context: CallbackContext) -> None:
    global MAINTENANCE_MODE
    admin_id = int(os.environ.get('ADMIN_ID', 0))
    if update.effective_user.id != admin_id:
        update.message.reply_text("У вас нет прав для выполнения этой команды.")
        return
    
    MAINTENANCE_MODE = not MAINTENANCE_MODE
    status = "включен" if MAINTENANCE_MODE else "выключен"
    update.message.reply_text(f"Режим обслуживания {status}.")
    logger.info(f"Администратор {update.effective_user.id} {status} режим обслуживания.")

def show_stats(update: Update, context: CallbackContext) -> None:
    admin_id = int(os.environ.get('ADMIN_ID', 0))
    if update.effective_user.id != admin_id:
        update.message.reply_text("У вас нет прав для выполнения этой команды.")
        return
    
    stats_message = f"Статистика бота:\n\nВсего пользователей: {len(TOTAL_USERS)}\nВсего отправлено сообщений: {TOTAL_MESSAGES}"
    update.message.reply_text(stats_message)

if __name__ == "__main__":
    main()