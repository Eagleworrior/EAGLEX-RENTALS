from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db, Building, Unit, Tenant   # import your existing models from app.py

# Blueprint for landlord actions
landlord_bp = Blueprint('landlord', __name__, url_prefix='/landlord')

# Edit building name
@landlord_bp.route('/building/<int:id>/edit', methods=['GET', 'POST'])
def edit_building(id):
    building = Building.query.get_or_404(id)
    if request.method == 'POST':
        building.name = request.form['name']
        db.session.commit()
        flash('Building name updated successfully!')
        return redirect(url_for('landlord.edit_building', id=id))
    return render_template('edit_building.html', building=building)

# Edit unit details
@landlord_bp.route('/unit/<int:id>/edit', methods=['GET', 'POST'])
def edit_unit(id):
    unit = Unit.query.get_or_404(id)
    if request.method == 'POST':
        unit.name = request.form['name']
        unit.rent = request.form['rent']
        db.session.commit()
        flash('Unit updated successfully!')
        return redirect(url_for('landlord.edit_unit', id=id))
    return render_template('edit_unit.html', unit=unit)

# Edit tenant details
@landlord_bp.route('/tenant/<int:id>/edit', methods=['GET', 'POST'])
def edit_tenant(id):
    tenant = Tenant.query.get_or_404(id)
    if request.method == 'POST':
        tenant.name = request.form['name']
        tenant.phone = request.form['phone']
        db.session.commit()
        flash('Tenant updated successfully!')
        return redirect(url_for('landlord.edit_tenant', id=id))
    return render_template('edit_tenant.html', tenant=tenant)

# Delete tenant when they move out
@landlord_bp.route('/tenant/<int:id>/delete', methods=['POST'])
def delete_tenant(id):
    tenant = Tenant.query.get_or_404(id)
    db.session.delete(tenant)
    db.session.commit()
    flash('Tenant removed successfully!')
    return redirect(url_for('landlord.edit_tenant', id=id))
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db, Building, Unit, Tenant   # import your existing models from app.py

# Blueprint for landlord actions
landlord_bp = Blueprint('landlord', __name__, url_prefix='/landlord')

# Edit building name
@landlord_bp.route('/building/<int:id>/edit', methods=['GET', 'POST'])
def edit_building(id):
    building = Building.query.get_or_404(id)
    if request.method == 'POST':
        building.name = request.form['name']
        db.session.commit()
        flash('Building name updated successfully!')
        return redirect(url_for('landlord.edit_building', id=id))
    return render_template('edit_building.html', building=building)

# Edit unit details
@landlord_bp.route('/unit/<int:id>/edit', methods=['GET', 'POST'])
def edit_unit(id):
    unit = Unit.query.get_or_404(id)
    if request.method == 'POST':
        unit.name = request.form['name']
        unit.rent = request.form['rent']
        db.session.commit()
        flash('Unit updated successfully!')
        return redirect(url_for('landlord.edit_unit', id=id))
    return render_template('edit_unit.html', unit=unit)

# Edit tenant details
@landlord_bp.route('/tenant/<int:id>/edit', methods=['GET', 'POST'])
def edit_tenant(id):
    tenant = Tenant.query.get_or_404(id)
    if request.method == 'POST':
        tenant.name = request.form['name']
        tenant.phone = request.form['phone']
        db.session.commit()
        flash('Tenant updated successfully!')
        return redirect(url_for('landlord.edit_tenant', id=id))
    return render_template('edit_tenant.html', tenant=tenant)

# Delete tenant when they move out
@landlord_bp.route('/tenant/<int:id>/delete', methods=['POST'])
def delete_tenant(id):
    tenant = Tenant.query.get_or_404(id)
    db.session.delete(tenant)
    db.session.commit()
    flash('Tenant removed successfully!')
    return redirect(url_for('landlord.edit_tenant', id=id))

