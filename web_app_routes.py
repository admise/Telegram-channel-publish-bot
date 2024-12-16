from flask import jsonify, Flask, render_template, url_for, redirect, request, session
from jinja2 import TemplateNotFound
from utils import get_bot_username
import json
import urllib.parse

app = Flask(__name__)
import secrets
app.secret_key = secrets.token_hex(16)  # Generate a random secret key for Flask

@app.route('/')
def home():
    return render_template('index.html')

@app.errorhandler(TemplateNotFound)
def template_not_found(e):
    app.logger.error(f"Template not found: {e}")
    return "An error occurred while rendering the template.", 500

@app.route('/profile')
def profile():
    user_data = session.get('user', {})
    return render_template('profile.html', user_data=user_data)
        
@app.route('/telegram_identity', methods=['POST'])
def telegram_identity():
    init_data = request.json.get('tgWebAppData')
    if init_data:
        try:
            # Parse the init_data as a URL-encoded string
            parsed_data = urllib.parse.parse_qs(init_data)
            # Extract user data from the parsed dictionary
            user_data = json.loads(parsed_data.get('user', ['{}'])[0])
            
            # Check if the session already contains the same user data
            if session.get('user') == user_data:
                return jsonify({'success': True, 'status': 'already_logged_in'}), 200
            
            # Store all available user data in the session
            session['user'] = user_data
            return jsonify({'success': True, 'status': 'first_time_login'}), 200
        except json.JSONDecodeError as e:
            app.logger.error(f"Failed to parse user data JSON: {str(e)}")
            return jsonify({'success': False, 'error': f"Invalid JSON in user data: {str(e)}"}), 400
        except Exception as e:
            app.logger.error(f"Unexpected error processing Telegram init data: {str(e)}")
            return jsonify({'success': False, 'error': f"Unexpected error: {str(e)}"}), 500
    app.logger.warning("No init data received")
    return jsonify({'success': False, 'error': 'No init data received'}), 400

@app.route('/not_in_telegram')
def not_in_telegram():
    bot_username = get_bot_username()
    error = request.args.get('error', '')
    return render_template('not_in_telegram.html', bot_username=bot_username, error=error), 200
