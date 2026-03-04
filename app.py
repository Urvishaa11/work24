from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.config.from_object('config.Config')
db = SQLAlchemy(app)

# Admin credentials (change these in production!)
ADMIN_CREDENTIALS = {
    'admin': 'admin123',
    'superadmin': 'super123'
}

# Database Models
class Worker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text, nullable=False)
    aadhar = db.Column(db.String(12), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    experience = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)
    portfolio_images = db.Column(db.Text)
    is_approved = db.Column(db.Boolean, default=None, nullable=True)
    rating = db.Column(db.Float, default=0.0)
    total_reviews = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def status(self):
        if self.is_approved is None:
            return 'pending'
        elif self.is_approved:
            return 'approved'
        else:
            return 'rejected'

class Seller(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    shop_name = db.Column(db.String(100), nullable=False)
    owner_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text, nullable=False)
    business_license = db.Column(db.String(50), nullable=False)
    gst_number = db.Column(db.String(15), nullable=False)
    categories = db.Column(db.Text, nullable=False)
    is_approved = db.Column(db.Boolean, default=None, nullable=True)
    rating = db.Column(db.Float, default=0.0)
    total_reviews = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def status(self):
        if self.is_approved is None:
            return 'pending'
        elif self.is_approved:
            return 'approved'
        else:
            return 'rejected'

class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15))
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Material(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('seller.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    image_path = db.Column(db.String(200))
    stock_quantity = db.Column(db.Integer, default=0)
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Admin decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# Load translations
def load_translations():
    translations = {}
    try:
        with open('translations/hindi.json', 'r', encoding='utf-8') as f:
            translations['hindi'] = json.load(f)
        with open('translations/gujarati.json', 'r', encoding='utf-8') as f:
            translations['gujarati'] = json.load(f)
    except FileNotFoundError:
        translations = {'hindi': {}, 'gujarati': {}}
    return translations

translations = load_translations()

# Helper function to get translated text
def get_text(key, lang='english'):
    if lang == 'english':
        return key
    return translations.get(lang, {}).get(key, key)

# Make get_text available in all templates
@app.context_processor
def inject_get_text():
    return dict(get_text=get_text)

# Public Routes
@app.route('/')
def index():
    lang = session.get('language', 'english')
    workers_count = Worker.query.filter_by(is_approved=True).count()
    sellers_count = Seller.query.filter_by(is_approved=True).count()
    
    return render_template('index.html', 
                         lang=lang, 
                         workers_count=workers_count,
                         sellers_count=sellers_count)

@app.route('/set_language/<language>')
def set_language(language):
    session['language'] = language
    return redirect(request.referrer or url_for('index'))

@app.route('/services')
def services():
    lang = session.get('language', 'english')
    category = request.args.get('category', '')
    
    if category:
        workers = Worker.query.filter_by(category=category, is_approved=True).all()
    else:
        workers = Worker.query.filter_by(is_approved=True).all()
    
    # Group workers by category
    categories = {}
    for worker in workers:
        if worker.category not in categories:
            categories[worker.category] = []
        categories[worker.category].append(worker)
    
    return render_template('services.html', 
                         lang=lang, 
                         categories=categories,
                         selected_category=category)

@app.route('/materials')
def materials():
    lang = session.get('language', 'english')
    category = request.args.get('category', '')
    
    if category:
        materials = Material.query.filter_by(category=category, is_available=True).all()
    else:
        materials = Material.query.filter_by(is_available=True).all()
    
    # Group materials by category
    categories = {}
    for material in materials:
        if material.category not in categories:
            categories[material.category] = []
        categories[material.category].append(material)
    
    return render_template('materials.html', 
                         lang=lang, 
                         categories=categories,
                         selected_category=category)

@app.route('/architect')
def architect():
    lang = session.get('language', 'english')
    return render_template('architect.html', lang=lang)

@app.route('/career')
def career():
    lang = session.get('language', 'english')
    return render_template('career.html', lang=lang)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    lang = session.get('language', 'english')
    
    print(f"")
    print(f"Method: {request.method}")
    
    if request.method == 'POST':
        print("")
        print(f"Form data: {dict(request.form)}")
        
        try:
            # Get form data with validation
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            phone = request.form.get('phone', '').strip()
            subject = request.form.get('subject', '').strip()
            message = request.form.get('message', '').strip()
            
            print(f"Parsed data - Name: {name}, Email: {email}, Subject: {subject}")
            
            # Validate required fields
            if not all([name, email, subject, message]):
                print("Validation failed - missing required fields")
                flash('Please fill in all required fields (Name, Email, Subject, Message).', 'error')
                return render_template('contact.html', lang=lang)
            
            # Create and save message
            contact_message = ContactMessage(
                name=name,
                email=email,
                phone=phone if phone else None,
                subject=subject,
                message=message,
                is_read=False,
                created_at=datetime.now()  # Fixed deprecation warning
            )
            
            print(f"Created ContactMessage object: {contact_message.name}")
            
            db.session.add(contact_message)
            db.session.commit()
            
            print("Message saved to database successfully!")
            
            flash('Message sent successfully! We will get back to you soon.', 'success')
            return redirect(url_for('contact'))
            
        except Exception as e:
            print(f"ERROR saving contact message: {str(e)}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            flash('Error sending message. Please try again.', 'error')
            return render_template('contact.html', lang=lang)
    
    print("Rendering contact form (GET request)")
    return render_template('contact.html', lang=lang)

@app.route('/admin/contacts/<int:message_id>')
@admin_required
def admin_contact_details(message_id):
    """Get contact message details"""
    message = ContactMessage.query.get_or_404(message_id)
    
    return jsonify({
        'success': True,
        'message': {
            'id': message.id,
            'name': message.name,
            'email': message.email,
            'phone': message.phone,
            'subject': message.subject,
            'message': message.message,
            'is_read': message.is_read,
            'created_at': message.created_at.isoformat()
        }
    })

@app.route('/admin/contacts/<int:message_id>/mark-read', methods=['POST'])
@admin_required
def admin_mark_message_read(message_id):
    """Mark contact message as read"""
    try:
        message = ContactMessage.query.get_or_404(message_id)
        message.is_read = True
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
 

@app.route('/admin/contacts/<int:message_id>/delete', methods=['POST'])
@admin_required
def admin_delete_message(message_id):
    """Delete contact message"""
    try:
        message = ContactMessage.query.get_or_404(message_id)
        db.session.delete(message)
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/debug/test-message')
def debug_test_message():
    try:
        # Create a test message directly
        test_message = ContactMessage(
            name="Debug Test",
            email="debug@test.com",
            subject="Test Subject",
            message="This is a test message created directly",
            is_read=False,
            created_at=datetime.utcnow()
        )
        
        db.session.add(test_message)
        db.session.commit()
        
        # Check if it was saved
        saved = ContactMessage.query.filter_by(email="debug@test.com").first()
        
        return jsonify({
            'status': 'success',
            'message': 'Test message created',
            'saved_message': {
                'id': saved.id,
                'name': saved.name,
                'email': saved.email,
                'subject': saved.subject
            } if saved else None
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        })


@app.route('/worker_registration', methods=['GET', 'POST'])
def worker_registration():
    lang = session.get('language', 'english')
    
    if request.method == 'POST':
        # Handle worker registration
        worker = Worker(
            name=request.form['name'],
            phone=request.form['phone'],
            email=request.form['email'],
            address=request.form['address'],
            aadhar=request.form['aadhar'],
            category=request.form['category'],
            experience=int(request.form['experience']),
            description=request.form.get('description', '')
        )
        
        db.session.add(worker)
        db.session.commit()
        
        flash('Registration submitted successfully! Wait for admin approval.', 'success')
        return redirect(url_for('career'))
    
    return render_template('worker_registration.html', lang=lang)

@app.route('/seller_registration', methods=['GET', 'POST'])
def seller_registration():
    lang = session.get('language', 'english')
    
    if request.method == 'POST':
        # Handle seller registration
        seller = Seller(
            shop_name=request.form['shop_name'],
            owner_name=request.form['owner_name'],
            phone=request.form['phone'],
            email=request.form['email'],
            address=request.form['address'],
            business_license=request.form['business_license'],
            gst_number=request.form['gst_number'],
            categories=request.form['categories']
        )
        
        db.session.add(seller)
        db.session.commit()
        
        flash('Registration submitted successfully! Wait for admin approval.', 'success')
        return redirect(url_for('career'))
    
    return render_template('seller_registration.html', lang=lang)

# Admin Routes
@app.route('/admin')
def admin_redirect():
    return redirect(url_for('admin_login'))

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if 'admin_logged_in' in session:
        return redirect(url_for('admin_dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in ADMIN_CREDENTIALS and ADMIN_CREDENTIALS[username] == password:
            session['admin_logged_in'] = True
            session['admin_username'] = username
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    session.pop('admin_username', None)
    flash('Logged out successfully', 'success')
    return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    # Calculate statistics
    stats = {
        'total_workers': Worker.query.count(),
        'total_sellers': Seller.query.count(),
        'pending_approvals': Worker.query.filter_by(is_approved=None).count() + Seller.query.filter_by(is_approved=None).count(),
        'total_messages': ContactMessage.query.filter_by(is_read=False).count()
    }
    
    # Get recent registrations (workers and sellers combined)
    recent_workers = Worker.query.order_by(Worker.created_at.desc()).limit(5).all()
    recent_sellers = Seller.query.order_by(Seller.created_at.desc()).limit(5).all()
    
    # Combine and sort by date
    recent_registrations = []
    
    for worker in recent_workers:
        recent_registrations.append({
            'id': worker.id,
            'name': worker.name,
            'type': 'worker',
            'phone': worker.phone,
            'date': worker.created_at,
            'status': worker.status
        })
    
    for seller in recent_sellers:
        recent_registrations.append({
            'id': seller.id,
            'name': seller.shop_name,
            'type': 'seller',
            'phone': seller.phone,
            'date': seller.created_at,
            'status': seller.status
        })
    
    # Sort by date (newest first)
    recent_registrations.sort(key=lambda x: x['date'], reverse=True)
    recent_registrations = recent_registrations[:10]  # Take top 10
    
    return render_template('admin/dashboard.html', stats=stats, recent_registrations=recent_registrations)

@app.route('/admin/workers')
@admin_required
def admin_workers():
    workers = Worker.query.order_by(Worker.created_at.desc()).all()
    return render_template('admin/workers.html', workers=workers)

@app.route('/admin/sellers')
@admin_required
def admin_sellers():
    sellers = Seller.query.order_by(Seller.created_at.desc()).all()
    return render_template('admin/sellers.html', sellers=sellers)

@app.route('/admin/contacts')
@admin_required
def admin_contacts():
    print("")
    
    messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    
    print(f"Total messages found: {len(messages)}")
    for msg in messages:
        print(f"Message {msg.id}: {msg.name} - {msg.subject} - Read: {msg.is_read}")
    
    return render_template('admin/contacts.html', messages=messages)

@app.route('/admin/settings')
@admin_required
def admin_settings():
    return render_template('admin/settings.html')

# Admin Action Routes
@app.route('/admin/fix-status')
@admin_required
def admin_fix_status():
    try:
        # Reset all existing workers and sellers to pending
        workers = Worker.query.all()
        for worker in workers:
            worker.is_approved = None
        
        sellers = Seller.query.all()
        for seller in sellers:
            seller.is_approved = None
        
        db.session.commit()
        flash('All registrations reset to pending status!', 'success')
        return redirect(url_for('admin_workers'))
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/mark-message-read/<int:message_id>', methods=['POST'])
@admin_required
def mark_message_read(message_id):
    message = ContactMessage.query.get_or_404(message_id)
    message.is_read = True
    db.session.commit()
    return jsonify({'success': True, 'message': 'Message marked as read!'})

# Worker Admin Actions
@app.route('/admin/approve-worker/<int:worker_id>', methods=['POST'])
@admin_required
def approve_worker(worker_id):
    worker = Worker.query.get_or_404(worker_id)
    worker.is_approved = True
    db.session.commit()
    return jsonify({'success': True, 'message': 'Worker approved successfully!'})

@app.route('/admin/reject-worker/<int:worker_id>', methods=['POST'])
@admin_required
def reject_worker(worker_id):
    worker = Worker.query.get_or_404(worker_id)
    worker.is_approved = False
    db.session.commit()
    return jsonify({'success': True, 'message': 'Worker rejected successfully!'})

# Seller Admin Actions
@app.route('/admin/approve-seller/<int:seller_id>', methods=['POST'])
@admin_required
def approve_seller(seller_id):
    seller = Seller.query.get_or_404(seller_id)
    seller.is_approved = True
    db.session.commit()
    return jsonify({'success': True, 'message': 'Seller approved successfully!'})

@app.route('/admin/reject-seller/<int:seller_id>', methods=['POST'])
@admin_required
def reject_seller(seller_id):
    seller = Seller.query.get_or_404(seller_id)
    seller.is_approved = False
    db.session.commit()
    return jsonify({'success': True, 'message': 'Seller rejected successfully!'})

# Generic Admin Actions (for dashboard quick actions)
@app.route('/admin/approve-registration/<registration_id>', methods=['POST'])
@admin_required
def approve_registration(registration_id):
    # Try to find worker first
    worker = Worker.query.filter_by(id=registration_id).first()
    if worker:
        worker.is_approved = True
        db.session.commit()
        return jsonify({'success': True, 'message': 'Worker approved successfully'})
    
    # Try to find seller
    seller = Seller.query.filter_by(id=registration_id).first()
    if seller:
        seller.is_approved = True
        db.session.commit()
        return jsonify({'success': True, 'message': 'Seller approved successfully'})
    
    return jsonify({'success': False, 'message': 'Registration not found'})

@app.route('/admin/reject-registration/<registration_id>', methods=['POST'])
@admin_required
def reject_registration(registration_id):
    # Try to find worker first
    worker = Worker.query.filter_by(id=registration_id).first()
    if worker:
        worker.is_approved = False
        db.session.commit()
        return jsonify({'success': True, 'message': 'Worker rejected successfully'})
    
    # Try to find seller
    seller = Seller.query.filter_by(id=registration_id).first()
    if seller:
        seller.is_approved = False
        db.session.commit()
        return jsonify({'success': True, 'message': 'Seller rejected successfully'})
    
    return jsonify({'success': False, 'message': 'Registration not found'})

# Public API Routes
@app.route('/api/search_workers')
def api_search_workers():
    category = request.args.get('category', '')
    location = request.args.get('location', '')
    
    query = Worker.query.filter_by(is_approved=True)
    
    if category:
        query = query.filter_by(category=category)
    
    workers = query.all()
    
    result = []
    for worker in workers:
        result.append({
            'id': worker.id,
            'name': worker.name,
            'category': worker.category,
            'experience': worker.experience,
            'rating': worker.rating,
            'total_reviews': worker.total_reviews,
            'phone': worker.phone
        })
    
    return jsonify(result)
@app.route('/debug/messages')
def debug_messages():
    """Temporary debug route to check messages in database"""
    messages = ContactMessage.query.all()
    result = []
    
    for msg in messages:
        result.append({
            'id': msg.id,
            'name': msg.name,
            'email': msg.email,
            'subject': msg.subject,
            'message': msg.message,
            'is_read': msg.is_read,
            'created_at': str(msg.created_at)
        })
    
    return jsonify({
        'total_messages': len(messages),
        'messages': result
    })
@app.route('/api/search_materials')
def api_search_materials():
    category = request.args.get('category', '')
    
    query = Material.query.filter_by(is_available=True)
    
    if category:
        query = query.filter_by(category=category)
    
    materials = query.all()
    
    result = []
    for material in materials:
        seller = Seller.query.get(material.seller_id)
        result.append({
            'id': material.id,
            'name': material.name,
            'category': material.category,
            'price': material.price,
            'seller_name': seller.shop_name if seller else 'Unknown',
            'stock_quantity': material.stock_quantity
        })
    
    return jsonify(result)

if __name__ == '__main__':
    app.run()