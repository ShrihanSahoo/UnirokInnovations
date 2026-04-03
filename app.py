from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'unirok-innovations-super-secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///unirok.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- Database Models ---

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    brand_color = db.Column(db.String(20), default='#D4AF37') # Default Gold
    
    products = db.relationship('Product', backref='company', lazy=True, cascade="all, delete-orphan")

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(255), nullable=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)

# --- CLI Command to Seed Data ---
@app.cli.command('seed-db')
def seed_db():
    db.create_all()
    if not Company.query.first():
        c1 = Company(name='Myk Laticrete', slug='myk-laticrete', description='Premium adhesives, grouts, and waterproofing solutions.', brand_color='#E53935') # Red
        c2 = Company(name='Godrej', slug='godrej', description='Leading security solutions and premium locks.', brand_color='#1E88E5') # Blue
        c3 = Company(name='UltraTech', slug='ultratech', description='The engineer\'s choice. High quality cement and building materials.', brand_color='#D4AF37') # Gold
        
        db.session.add_all([c1, c2, c3])
        db.session.commit()
        
        p1 = Product(name='Laticrete Grout', company_id=c1.id)
        p2 = Product(name='Laticrete Adhesive', company_id=c1.id)
        p3 = Product(name='Godrej Nav-Tal Padlock', company_id=c2.id)
        p4 = Product(name='UltraTech Premium Cement', company_id=c3.id)
        
        db.session.add_all([p1, p2, p3, p4])
        db.session.commit()
        print("Database seeded successfully with initial dummy data.")
    else:
        print("Database already contains data.")

# --- Public Routes ---

@app.route('/')
def index():
    companies = Company.query.all()
    return render_template('index.html', companies=companies)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/companies/<slug>')
def company(slug):
    company = Company.query.filter_by(slug=slug).first_or_404()
    return render_template('company.html', company=company)

@app.route('/contact')
def contact():
    # Provide the external link here or redirect to it
    google_form_url = "#dummy-google-form-link"
    return render_template('contact.html', google_form_url=google_form_url)

# --- Admin / CMS Routes ---

ADMIN_PASSWORD = "admin" # Simple dummy password for now

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form['password'] == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid password', 'error')
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('index'))

@app.route('/admin')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    companies = Company.query.all()
    return render_template('admin_dashboard.html', companies=companies)

@app.route('/admin/company/add', methods=['POST'])
def admin_add_company():
    if not session.get('admin_logged_in'): return redirect(url_for('admin_login'))
    
    name = request.form['name']
    slug = name.lower().replace(' ', '-')
    desc = request.form.get('description', '')
    color = request.form.get('brand_color', '#D4AF37')
    
    new_company = Company(name=name, slug=slug, description=desc, brand_color=color)
    db.session.add(new_company)
    db.session.commit()
    flash('Company added successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/company/delete/<int:id>', methods=['POST'])
def admin_delete_company(id):
    if not session.get('admin_logged_in'): return redirect(url_for('admin_login'))
    
    company = Company.query.get_or_404(id)
    db.session.delete(company)
    db.session.commit()
    flash('Company deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/product/add', methods=['POST'])
def admin_add_product():
    if not session.get('admin_logged_in'): return redirect(url_for('admin_login'))
    
    name = request.form['name']
    company_id = request.form['company_id']
    
    new_product = Product(name=name, company_id=company_id)
    db.session.add(new_product)
    db.session.commit()
    flash('Product added successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
