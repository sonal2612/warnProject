import os
import uuid
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from datetime import datetime
from werkzeug.utils import secure_filename
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_socketio import SocketIO
from google.cloud import vision

# --- App Configuration ---
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SECRET_KEY'] = 'a-very-secret-key-you-should-change'

# --- Database Configuration ---
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///' + os.path.join(basedir, 'instance/reports.db'))
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# --- File Upload Configuration ---
app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'static/uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# --- Email Configuration ---
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_MAX_EMAILS'] = None
app.config['MAIL_ASCII_ATTACHMENTS'] = False

# --- Initializations ---
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
mail = Mail(app)
socketio = SocketIO(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'


# --- Database Models ---
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='responder')
    reports = db.relationship('Report', backref='responder', lazy=True)


class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    animal_type = db.Column(db.String(50), nullable=False)
    condition = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    reporter_email = db.Column(db.String(120), nullable=False)
    image_filename = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(20), nullable=False, default='New')
    responder_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    ai_species_suggestion = db.Column(db.String(50), nullable=True)
    resolution_notes = db.Column(db.String(500), nullable=True)
    resolution_image = db.Column(db.String(100), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


# --- Admin Panel Configuration ---
class AdminModelView(ModelView):
    can_export = True
    can_view_details = True
    page_size = 50
    
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == 'admin'

    def inaccessible_callback(self, name, **kwargs):
        flash('You must be an admin to access this page.', 'danger')
        return redirect(url_for('login'))

class UserAdmin(AdminModelView):
    column_list = ['id', 'username', 'email', 'role']
    column_searchable_list = ['username', 'email']
    column_filters = ['role']
    column_labels = {'id': 'ID', 'username': 'Username', 'email': 'Email Address', 'role': 'User Role'}
    form_excluded_columns = ['password_hash', 'reports']
    column_formatters = {
        'role': lambda v, c, m, p: f'<span class="badge bg-{"danger" if m.role == "admin" else "primary" if m.role == "responder" else "secondary"}">{m.role.upper()}</span>'
    }
    list_template = 'admin/model/custom_list.html'

class ReportAdmin(AdminModelView):
    column_list = ['id', 'timestamp', 'animal_type', 'condition', 'status', 'reporter_email', 'responder']
    column_searchable_list = ['animal_type', 'reporter_email', 'description']
    column_filters = ['status', 'animal_type', 'condition', 'timestamp']
    column_labels = {
        'id': 'Report ID',
        'timestamp': 'Date & Time',
        'animal_type': 'Animal Type',
        'condition': 'Condition',
        'status': 'Status',
        'reporter_email': 'Reporter Email',
        'responder': 'Assigned Responder'
    }
    column_formatters = {
        'status': lambda v, c, m, p: f'<span class="badge bg-{"danger" if m.status == "New" else "warning text-dark" if m.status == "Acknowledged" else "success"}">{m.status}</span>',
        'timestamp': lambda v, c, m, p: m.timestamp.strftime('%Y-%m-%d %H:%M')
    }
    column_default_sort = ('timestamp', True)
    list_template = 'admin/model/custom_list.html'

class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if not current_user.is_authenticated or current_user.role != 'admin':
            return redirect(url_for('login'))
        
        total_users = User.query.count()
        total_reports = Report.query.count()
        new_reports = Report.query.filter_by(status='New').count()
        resolved_reports = Report.query.filter_by(status='Resolved').count()
        
        return self.render('admin/custom_index.html',
                         total_users=total_users,
                         total_reports=total_reports,
                         new_reports=new_reports,
                         resolved_reports=resolved_reports)

admin = Admin(app, name='WARRN Admin', template_mode='bootstrap4', url='/admin', index_view=MyAdminIndexView())
admin.add_view(UserAdmin(User, db.session, name='Users', endpoint='user'))
admin.add_view(ReportAdmin(Report, db.session, name='Reports', endpoint='report'))


# --- Helper Functions ---
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def identify_animal_from_image(image_path):
    try:
        client = vision.ImageAnnotatorClient()
        with open(image_path, "rb") as image_file:
            content = image_file.read()
        image = vision.Image(content=content)
        response = client.label_detection(image=image)
        labels = response.label_annotations
        known_animals = ["dog", "cat", "cattle", "cow", "monkey", "deer", "canine", "feline", "bird"]
        for label in labels:
            if label.description.lower() in known_animals:
                return label.description.capitalize()
        return None
    except Exception as e:
        print(f"Error calling Vision API: {e}")
        return None


# --- Routes ---
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/report', methods=['POST'])
def submit_report():
    image_filename = None
    ai_suggestion = None

    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename != '' and allowed_file(file.filename):
            ext = file.filename.rsplit('.', 1)[1].lower()
            unique_id = uuid.uuid4().hex
            filename = secure_filename(f"{unique_id}.{ext}")
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(image_path)
            image_filename = filename
            ai_suggestion = identify_animal_from_image(image_path)

    new_report = Report(latitude=request.form['latitude'], longitude=request.form['longitude'],
                        animal_type=request.form['animal_type'], condition=request.form['condition'],
                        description=request.form['description'], reporter_email=request.form['reporter_email'],
                        image_filename=image_filename, ai_species_suggestion=ai_suggestion)
    db.session.add(new_report)
    db.session.commit()

    image_url = url_for('static',
                        filename=f'uploads/{new_report.image_filename}') if new_report.image_filename else None
    report_data = {'id': new_report.id, 'lat': new_report.latitude, 'lon': new_report.longitude,
                   'animal': new_report.animal_type, 'condition': new_report.condition, 'desc': new_report.description,
                   'time': new_report.timestamp.strftime('%Y-%m-%d %H:%M'), 'status': new_report.status,
                   'responder': None, 'image_url': image_url, 'ai_suggestion': new_report.ai_species_suggestion,
                   'claim_url': url_for('claim_report', report_id=new_report.id)}
    socketio.emit('new_report', report_data)

    # Send email notifications
    if app.config['MAIL_USERNAME'] and app.config['MAIL_PASSWORD']:
        try:
            map_link = f"https://www.google.com/maps?q={new_report.latitude},{new_report.longitude}"
            
            # Send confirmation to reporter
            reporter_msg = Message(
                subject='✅ Report Received - WARRN',
                sender=app.config['MAIL_USERNAME'],
                recipients=[new_report.reporter_email]
            )
            reporter_msg.body = f"""Thank you for reporting an animal incident!

Your Report Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 Report ID: #{new_report.id}
🐾 Animal Type: {new_report.animal_type}
⚠️  Condition: {new_report.condition}
📍 Location: {map_link}
🕐 Time: {new_report.timestamp.strftime('%Y-%m-%d %H:%M')}
{f'📝 Description: {new_report.description}' if new_report.description else ''}

Your report has been received and our responders have been notified.
You will receive updates when the report is claimed and resolved.

Thank you for helping animals! 🐾
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WARRN - Wildlife Animal Rescue & Response Network
"""
            mail.send(reporter_msg)
            
            # Send notification to responders
            responders = User.query.filter_by(role='responder').all()
            responder_emails = [user.email for user in responders]
            if responder_emails:
                responder_msg = Message(
                    subject='🚨 New Animal Incident Reported!',
                    sender=app.config['MAIL_USERNAME'],
                    recipients=responder_emails
                )
                responder_msg.body = f"""A new animal incident has been reported on WARRN.

Incident Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 Report ID: #{new_report.id}
🐾 Animal Type: {new_report.animal_type}
⚠️  Condition: {new_report.condition}
📍 Location: {map_link}
🕐 Time: {new_report.timestamp.strftime('%Y-%m-%d %H:%M')}
{f'📝 Description: {new_report.description}' if new_report.description else ''}

Please log in to the WARRN dashboard to claim and respond to this incident.

Thank you for your service! 🙏
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WARRN - Wildlife Animal Rescue & Response Network
"""
                mail.send(responder_msg)
            flash('Report submitted! Confirmation email sent to you and responders notified.', 'success')
        except Exception as e:
            print(f"Email Error: {e}")
            flash('Report submitted, but email notification failed.', 'warning')
    else:
        flash('Report submitted successfully!', 'info')

    return redirect(url_for('index'))


@app.route('/api/reports')
def get_reports():
    reports_list = []
    reports = Report.query.order_by(Report.timestamp.desc()).all()
    for report in reports:
        image_url = url_for('static', filename=f'uploads/{report.image_filename}') if report.image_filename else None
        reports_list.append({'lat': report.latitude, 'lon': report.longitude, 'animal': report.animal_type,
                             'condition': report.condition, 'desc': report.description,
                             'time': report.timestamp.strftime('%Y-%m-%d %H:%M'), 'image_url': image_url,
                             'status': report.status, 'ai_suggestion': report.ai_species_suggestion})
    return jsonify(reports_list)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated: return redirect(url_for('dashboard'))
    if request.method == 'POST':
        if User.query.count() == 0:
            user_role = 'admin'
        else:
            user_role = request.form.get('role', 'responder')
        hashed_password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        new_user = User(username=request.form['username'], email=request.form['email'], 
                       password_hash=hashed_password, role=user_role)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated: return redirect(url_for('dashboard'))
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and bcrypt.check_password_hash(user.password_hash, request.form['password']):
            login_user(user, remember=True)
            flash(f'Welcome back, {user.username}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Login unsuccessful. Please check username and password.', 'danger')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    reports = Report.query.order_by(Report.timestamp.desc()).all()
    return render_template('dashboard.html', reports=reports)


@app.route('/report/<int:report_id>/claim', methods=['POST'])
@login_required
def claim_report(report_id):
    report = Report.query.get_or_404(report_id)
    if report.status == 'New':
        report.responder_id = current_user.id
        report.status = 'Acknowledged'
        db.session.commit()
        
        # Send email to reporter
        if app.config['MAIL_USERNAME'] and app.config['MAIL_PASSWORD']:
            try:
                map_link = f"https://www.google.com/maps?q={report.latitude},{report.longitude}"
                msg = Message(
                    subject='👍 Report Claimed - WARRN',
                    sender=app.config['MAIL_USERNAME'],
                    recipients=[report.reporter_email]
                )
                msg.body = f"""Good news! Your report has been claimed by a responder.

Report Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 Report ID: #{report.id}
🐾 Animal Type: {report.animal_type}
⚠️  Condition: {report.condition}
📍 Location: {map_link}
👤 Responder: {current_user.username}
✅ Status: Acknowledged

A responder is now working on this incident.
You will be notified when it is resolved.

Thank you for your patience! 🙏
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WARRN - Wildlife Animal Rescue & Response Network
"""
                mail.send(msg)
            except Exception as e:
                print(f"Email Error: {e}")
        
        flash('You have claimed this report.', 'success')
    else:
        flash('This report has already been claimed.', 'warning')
    return redirect(url_for('dashboard'))


@app.route('/report/<int:report_id>/resolve', methods=['GET', 'POST'])
@login_required
def resolve_report(report_id):
    report = Report.query.get_or_404(report_id)
    
    if request.method == 'GET':
        if report.responder_id == current_user.id:
            return render_template('resolve_report.html', report=report)
        else:
            flash('You cannot resolve a report you have not claimed.', 'danger')
            return redirect(url_for('dashboard'))
    
    if report.responder_id == current_user.id:
        report.status = 'Resolved'
        report.resolution_notes = request.form.get('resolution_notes', '')
        
        # Handle resolution image
        if 'resolution_image' in request.files:
            file = request.files['resolution_image']
            if file and file.filename != '' and allowed_file(file.filename):
                ext = file.filename.rsplit('.', 1)[1].lower()
                unique_id = uuid.uuid4().hex
                filename = secure_filename(f"resolved_{unique_id}.{ext}")
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(image_path)
                report.resolution_image = filename
        
        db.session.commit()
        
        # Send email to reporter with resolution details
        if app.config['MAIL_USERNAME'] and app.config['MAIL_PASSWORD']:
            try:
                map_link = f"https://www.google.com/maps?q={report.latitude},{report.longitude}"
                msg = Message(
                    subject='✅ Report Resolved - WARRN',
                    sender=app.config['MAIL_USERNAME'],
                    recipients=[report.reporter_email]
                )
                resolution_text = f'📝 Resolution Notes:\n{report.resolution_notes}\n\n' if report.resolution_notes else ''
                msg.body = f"""Great news! Your report has been resolved.

Report Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 Report ID: #{report.id}
🐾 Animal Type: {report.animal_type}
⚠️  Condition: {report.condition}
📍 Location: {map_link}
👤 Responder: {current_user.username}
✅ Status: *** RESOLVED ***

{resolution_text}The incident has been successfully handled.
Thank you for reporting and helping save an animal's life!

Your compassion makes a difference. ❤️
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WARRN - Wildlife Animal Rescue & Response Network
"""
                # Attach resolution image if exists
                if report.resolution_image:
                    image_path = os.path.join(app.config['UPLOAD_FOLDER'], report.resolution_image)
                    if os.path.exists(image_path):
                        with open(image_path, 'rb') as img:
                            msg.attach(report.resolution_image, 'image/jpeg', img.read())
                
                mail.send(msg)
            except Exception as e:
                print(f"Email Error: {e}")
        
        flash('Report has been marked as resolved and reporter notified.', 'success')
    else:
        flash('You cannot resolve a report you have not claimed.', 'danger')
    return redirect(url_for('dashboard'))


@app.route('/analytics')
@login_required
def analytics():
    if current_user.role != 'admin':
        flash('You must be an admin to access this page.', 'danger')
        return redirect(url_for('dashboard'))

    total_reports = Report.query.count()
    reports_by_status = db.session.query(Report.status, func.count(Report.status)).group_by(Report.status).all()
    status_counts = {status: count for status, count in reports_by_status}
    reports_by_animal = db.session.query(Report.animal_type, func.count(Report.animal_type)).group_by(
        Report.animal_type).order_by(func.count(Report.animal_type).desc()).all()
    animal_labels = [item[0] for item in reports_by_animal]
    animal_data = [item[1] for item in reports_by_animal]

    return render_template('analytics.html', total_reports=total_reports, status_counts=status_counts,
                           animal_labels=animal_labels, animal_data=animal_data)


# --- Main Execution ---
if __name__ == '__main__':
    with app.app_context():
        instance_path = os.path.join(basedir, 'instance')
        os.makedirs(instance_path, exist_ok=True)
        db.create_all()
    socketio.run(app, debug=True)