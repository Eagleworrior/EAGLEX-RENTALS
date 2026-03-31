from datetime import datetime
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, login_user, login_required,
    logout_user, current_user, UserMixin
)
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SECRET_KEY'] = 'change-this-secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rental.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
migrate = Migrate(app, db)

# ---------- MODELS ----------

class Landlord(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(50))
    password_hash = db.Column(db.String(200), nullable=False)
    buildings = db.relationship('Building', backref='landlord', cascade='all, delete-orphan')

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

class Building(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    landlord_id = db.Column(db.Integer, db.ForeignKey('landlord.id'), nullable=False)
    units = db.relationship('Unit', backref='building', cascade='all, delete-orphan')

class Unit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(50), nullable=False)
    rent_amount = db.Column(db.Float, default=0.0)
    building_id = db.Column(db.Integer, db.ForeignKey('building.id'), nullable=False)
    tenant = db.relationship('Tenant', uselist=False, backref='unit')

class Tenant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(50))
    id_number = db.Column(db.String(100))
    email = db.Column(db.String(120))
    amount_paid = db.Column(db.Float, default=0.0)
    paid = db.Column(db.Boolean, default=False)
    receipt_created_at = db.Column(db.DateTime)
    unit_id = db.Column(db.Integer, db.ForeignKey('unit.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def rent_amount(self):
        return self.unit.rent_amount if self.unit and self.unit.rent_amount else 0.0

    @property
    def balance(self):
        return self.rent_amount - (self.amount_paid or 0.0)

@login_manager.user_loader
def load_user(user_id):
    return Landlord.query.get(int(user_id))

# ---------- AUTH ----------

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        first_name = request.form['first_name'].strip()
        last_name = request.form['last_name'].strip()
        email = request.form['email'].strip().lower()
        phone = request.form.get('phone', '').strip()
        password = request.form['password']

        if not first_name or not last_name or not email or not password:
            flash("All required fields must be filled.", "error")
            return redirect(url_for('register'))

        if Landlord.query.filter_by(email=email).first():
            flash("Email already registered.", "error")
            return redirect(url_for('register'))

        user = Landlord(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        flash("Account created. Please log in.", "success")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password']
        user = Landlord.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash("Invalid credentials", "error")
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# ---------- DASHBOARD ----------

@app.route('/')
@login_required
def dashboard():
    buildings = Building.query.filter_by(landlord_id=current_user.id).all()
    return render_template('dashboard.html', buildings=buildings)

# ---------- BUILDINGS ----------

@app.route('/building/new', methods=['GET','POST'])
@login_required
def new_building():
    if request.method == 'POST':
        name = request.form['name'].strip()
        if not name:
            flash("Building name required", "error")
            return redirect(url_for('new_building'))
        b = Building(name=name, landlord_id=current_user.id)
        db.session.add(b)
        db.session.commit()
        return redirect(url_for('building_detail', bid=b.id))
    return render_template('building_form.html')

@app.route('/building/<int:bid>')
@login_required
def building_detail(bid):
    building = Building.query.filter_by(id=bid, landlord_id=current_user.id).first_or_404()
    return render_template('building_detail.html', building=building)

# ---------- UNITS ----------

@app.route('/building/<int:bid>/unit/new', methods=['GET','POST'])
@login_required
def new_unit(bid):
    building = Building.query.filter_by(id=bid, landlord_id=current_user.id).first_or_404()
    if request.method == 'POST':
        number = request.form['number'].strip()
        rent_amount = float(request.form.get('rent_amount') or 0)
        if not number:
            flash("House number required", "error")
            return redirect(url_for('new_unit', bid=bid))
        u = Unit(number=number, rent_amount=rent_amount, building_id=building.id)
        db.session.add(u)
        db.session.commit()
        return redirect(url_for('building_detail', bid=bid))
    return render_template('unit_form.html', building=building)

@app.route('/unit/<int:uid>')
@login_required
def unit_detail(uid):
    unit = Unit.query.join(Building).filter(
        Unit.id == uid,
        Building.landlord_id == current_user.id
    ).first_or_404()
    return render_template('unit_detail.html', unit=unit)

# ---------- TENANTS ----------

@app.route('/unit/<int:uid>/tenant/new', methods=['GET','POST'])
@login_required
def new_tenant(uid):
    unit = Unit.query.join(Building).filter(
        Unit.id == uid,
        Building.landlord_id == current_user.id
    ).first_or_404()
    if request.method == 'POST':
        tenant = Tenant(
            name=request.form['name'].strip(),
            phone=request.form.get('phone'),
            id_number=request.form.get('id_number'),
            email=request.form.get('email'),
            unit_id=unit.id
        )
        db.session.add(tenant)
        db.session.commit()
        return redirect(url_for('unit_detail', uid=unit.id))
    return render_template('tenant_form.html', unit=unit)

@app.route('/tenant/<int:tid>/pay', methods=['POST'])
@login_required
def record_payment(tid):
    tenant = Tenant.query.join(Unit).join(Building).filter(
        Tenant.id == tid,
        Building.landlord_id == current_user.id
    ).first_or_404()
    amount = float(request.form.get('amount') or 0)
    tenant.amount_paid += amount
    if tenant.amount_paid >= tenant.rent_amount:
        tenant.paid = True
        if not tenant.receipt_created_at:
            tenant.receipt_created_at = datetime.now()
    db.session.commit()
    flash(f"Payment of {amount} recorded for {tenant.name}", "success")
    return redirect(url_for('unit_detail', uid=tenant.unit_id))

# ---------- RECEIPT (SINGLE) ----------

@app.route('/tenant/<int:tid>/receipt')
@login_required
def receipt(tid):
    tenant = Tenant.query.join(Unit).join(Building).filter(
        Tenant.id == tid,
        Building.landlord_id == current_user.id
    ).first_or_404()
    date_value = tenant.receipt_created_at or tenant.created_at
    return render_template('receipt.html',
                           tenant=tenant,
                           landlord=current_user,
                           date=date_value)

# ---------- RECEIPTS DASHBOARD ----------

@app.route('/receipts')
@login_required
def receipts():
    tenants = Tenant.query.join(Unit).join(Building).filter(
        Building.landlord_id == current_user.id,
        Tenant.receipt_created_at.isnot(None)
    ).order_by(Tenant.receipt_created_at.desc()).all()

    grouped = {}
    for t in tenants:
        d = (t.receipt_created_at or t.created_at).date()
        grouped.setdefault(d, []).append(t)

    sorted_dates = sorted(grouped.keys(), reverse=True)
    return render_template('receipts.html',
                           grouped=grouped,
                           sorted_dates=sorted_dates)

# ---------- PAID / UNPAID ----------

@app.route('/tenants/paid')
@login_required
def paid_tenants():
    tenants = Tenant.query.join(Unit).join(Building).filter(
        Building.landlord_id == current_user.id,
        Tenant.paid == True
    ).all()
    return render_template('paid_tenants.html', tenants=tenants)

@app.route('/tenants/unpaid')
@login_required
def unpaid_tenants():
    tenants = Tenant.query.join(Unit).join(Building).filter(
        Building.landlord_id == current_user.id,
        Tenant.paid == False
    ).all()
    return render_template('unpaid_tenants.html', tenants=tenants)

# ---------- TENANT PORTAL (PUBLIC RECEIPT) ----------

@app.route('/portal/tenant/<int:tid>')
def tenant_portal(tid):
    tenant = Tenant.query.get_or_404(tid)
    date_value = tenant.receipt_created_at or tenant.created_at
    return render_template('receipt.html',
                           tenant=tenant,
                           landlord=None,
                           date=date_value)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

