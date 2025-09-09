# app.py

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from functools import wraps
import os
from datetime import datetime

from modules import user_manager, auth_service, webauthn_helpers, typing_analyzer

app = Flask(__name__)
app.config.from_object('config.Config')

with app.app_context():
    os.makedirs(os.path.dirname(app.config['USER_DB_PATH']), exist_ok=True)

@app.context_processor
def inject_now():
    return {'now': datetime.utcnow}

# --- Decorators ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_authenticated'):
            flash('You must be logged in to view this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def registration_in_progress(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('registration_email'):
            flash('Please start the registration process first.', 'error')
            return redirect(url_for('register'))
        return f(*args, **kwargs)
    return decorated_function

# --- Main Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been successfully logged out.', 'success')
    return redirect(url_for('index'))

# --- Registration Flow ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        if not email:
            flash('Email is required.', 'error')
            return redirect(url_for('register'))
        if user_manager.get_user(email):
            flash('An account with this email already exists.', 'error')
            return redirect(url_for('register'))
        session['registration_email'] = email
        user_manager.create_user_profile(email)
        return redirect(url_for('register_fingerprint'))
    return render_template('register.html')

@app.route('/register/fingerprint')
@registration_in_progress
def register_fingerprint():
    email = session['registration_email']
    options = webauthn_helpers.get_registration_options(email)
    session['webauthn_challenge'] = options['challenge']
    return render_template('fingerprint_prompt.html', title="Step 1: Register Fingerprint",
                           instruction="Your browser will prompt you to scan your fingerprint.",
                           options=options, form_action_url=url_for('verify_fingerprint_registration'),
                           failure_redirect_url=None)

@app.route('/register/verify_fingerprint', methods=['POST'])
@registration_in_progress
def verify_fingerprint_registration():
    email = session['registration_email']
    challenge = session.get('webauthn_challenge')
    credential = request.get_json()
    if auth_service.verify_webauthn_registration(credential, challenge):
        user_manager.save_webauthn_credential(email, credential)
        session.pop('webauthn_challenge', None)
        return jsonify({'success': True, 'redirect_url': url_for('register_clicks')})
    else:
        return jsonify({'success': False, 'error': 'Fingerprint verification failed. Please try again.'}), 400

@app.route('/register/clicks')
@registration_in_progress
def register_clicks():
    return render_template('click_challenge.html', title="Step 2: Create Click Pattern",
                           instruction="Click on 3 distinct, memorable points on the image.",
                           form_action_url=url_for('save_click_profile'))

@app.route('/register/save_clicks', methods=['POST'])
@registration_in_progress
def save_click_profile():
    email = session['registration_email']
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'Invalid request format.'}), 400
    clicks = data.get('clicks')
    if isinstance(clicks, list) and len(clicks) == 3:
        user_manager.save_click_profile(email, clicks)
        return jsonify({'success': True, 'redirect_url': url_for('register_typing_baseline')})
    else:
        return jsonify({'success': False, 'error': 'You must select exactly 3 points. Please reset and try again.'}), 400

@app.route('/register/typing_baseline', methods=['GET'])
@registration_in_progress
def register_typing_baseline():
    challenge_sentence = "the quick brown fox jumps over the lazy dog"
    return render_template('typing_challenge.html',
                           title="Step 3: Create Typing Profile",
                           challenge_text=challenge_sentence)

@app.route('/register/save_typing_baseline', methods=['POST'])
@registration_in_progress
def save_typing_baseline():
    email = session['registration_email']
    durations = request.form.getlist('durations', type=float)
    if len(durations) == 4:
        user_manager._update_user_field(email, 'typing_samples', durations)
        average_speed = typing_analyzer.calculate_average(durations)
        if average_speed is not None:
            user_manager.save_typing_average(email, average_speed)
        passkey = auth_service.generate_and_save_passkey(email)
        session['passkey_to_show'] = passkey
        return redirect(url_for('register_complete'))
    else:
        flash('There was an error collecting typing samples. Please try again.', 'error')
        return redirect(url_for('register_typing_baseline'))

@app.route('/register/complete')
@registration_in_progress
def register_complete():
    passkey = session.get('passkey_to_show')
    if not passkey: return redirect(url_for('register'))
    session.pop('registration_email', None)
    session.pop('passkey_to_show', None)
    flash('Registration successful! You can now log in.', 'success')
    return render_template('registration_complete.html', passkey=passkey)

# --- Login Flow ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        if not user_manager.get_user(email):
            flash('No account found with that email. Please register first.', 'error')
            return redirect(url_for('login'))
        session['login_email'] = email
        session['login_failures'] = 0
        return redirect(url_for('login_with_fingerprint'))
    return render_template('login.html')

@app.route('/login/fingerprint')
def login_with_fingerprint():
    email = session.get('login_email')
    if not email: return redirect(url_for('login'))
    user_credential = user_manager.get_webauthn_credential(email)
    if not isinstance(user_credential, dict):
        flash('No fingerprint registered. Proceeding to step-up challenge.', 'error')
        return redirect(url_for('login_with_clicks'))
    options = webauthn_helpers.get_authentication_options(user_credential)
    session['webauthn_challenge'] = options['challenge']
    return render_template('fingerprint_prompt.html', 
                           title="Login: Verify Fingerprint",
                           instruction="Please use your fingerprint scanner to log in.",
                           options=options,
                           form_action_url=url_for('verify_fingerprint_login'),
                           failure_redirect_url=url_for('login_with_clicks'))

@app.route('/login/verify_fingerprint', methods=['POST'])
def verify_fingerprint_login():
    email = session.get('login_email')
    challenge = session.get('webauthn_challenge')
    login_credential = request.get_json()
    if auth_service.verify_webauthn_authentication(email, login_credential, challenge):
        session['is_authenticated'] = True
        session.permanent = True
        session['login_email'] = email
        session.pop('webauthn_challenge', None)
        return jsonify({'success': True, 'redirect_url': url_for('dashboard')})
    else:
        return jsonify({'success': False, 'redirect_url': url_for('login_with_clicks')})

@app.route('/login/clicks')
def login_with_clicks():
    if not session.get('login_email'): return redirect(url_for('login'))
    return render_template('click_challenge.html', title="Step-Up Challenge: Image Clicks",
                           instruction="Fingerprint failed. Please click your 3 secret points.",
                           form_action_url=url_for('verify_click_login'))

@app.route('/login/verify_clicks', methods=['POST'])
def verify_click_login():
    email = session.get('login_email')
    if not email: return jsonify({'success': False, 'error': 'Session expired.'}), 400
    clicks = request.get_json().get('clicks')
    if auth_service.verify_clicks(email, clicks):
        session['is_authenticated'] = True
        session.permanent = True
        session['login_email'] = email
        return jsonify({'success': True, 'redirect_url': url_for('dashboard')})
    else:
        # --- THIS IS THE CHANGE ---
        # Instead of just redirecting, we now also increment the failure counter
        session['login_failures'] = session.get('login_failures', 0) + 1
        return jsonify({'success': False, 'redirect_url': url_for('login_step_up')})

@app.route('/login/step_up', methods=['GET', 'POST'])
def login_step_up():
    email = session.get('login_email')
    if not email: return redirect(url_for('login'))
    
    # Check for lockout BEFORE processing the form
    if session.get('login_failures', 0) >= 2:
        session.pop('login_email', None)
        return redirect(url_for('locked_out'))

    if request.method == 'POST':
        passkey = request.form.get('passkey')
        typing_duration = float(request.form.get('typing_duration', '0'))
        
        passkey_ok = auth_service.verify_passkey(email, passkey)
        typing_ok = typing_analyzer.verify_typing_speed(email, typing_duration)
        
        if passkey_ok and typing_ok:
            session['is_authenticated'] = True
            session.permanent = True
            session['login_email'] = email
            session.pop('login_failures', None)
            flash('Recovery successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            session['login_failures'] = session.get('login_failures', 0) + 1
            if session['login_failures'] >= 2:
                session.pop('login_email', None)
                return redirect(url_for('locked_out'))
            
            flash('Recovery information was incorrect. Please try again.', 'error')
            return redirect(url_for('login_step_up'))

    # Calculate attempts left to display on the page
    attempts_left = 2 - session.get('login_failures', 0)
    return render_template('step_up_challenge.html',
                           challenge_text="the quick brown fox jumps over the lazy dog",
                           attempts_left=attempts_left)

@app.route('/locked_out')
def locked_out():
    return render_template('locked_out.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8501, debug=True)