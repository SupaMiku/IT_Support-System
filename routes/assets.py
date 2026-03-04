"""Assets routes – /api/assets"""
from flask import Blueprint, request, jsonify, session
from database import db
from models import Asset, AssetMaintenance, User, AuditLog
from datetime import date

assets_bp = Blueprint('assets', __name__)

def current_user():
    uid = session.get('user_id')
    return User.query.get(uid) if uid else None

@assets_bp.route('/', methods=['GET'])
def list_assets():
    q = Asset.query
    if request.args.get('status'):   q = q.filter(Asset.status   == request.args['status'])
    if request.args.get('category'): q = q.filter(Asset.category == request.args['category'])
    if request.args.get('location'): q = q.filter(Asset.location.ilike(f"%{request.args['location']}%"))
    return jsonify([a.to_dict() for a in q.order_by(Asset.asset_tag).all()]), 200

@assets_bp.route('/', methods=['POST'])
def create_asset():
    user = current_user()
    if not user or user.role.name not in ('admin', 'it_staff'):
        return jsonify({'error': 'Insufficient permissions'}), 403
    data = request.get_json()
    if not data.get('asset_tag') or not data.get('name'):
        return jsonify({'error': 'asset_tag and name are required'}), 400
    
    # Handle date fields safely
    purchase_date = None
    if data.get('purchase_date') and data['purchase_date'].strip():
        try:
            purchase_date = date.fromisoformat(data['purchase_date'])
        except:
            pass
    
    warranty_expiry = None
    if data.get('warranty_expiry') and data['warranty_expiry'].strip():
        try:
            warranty_expiry = date.fromisoformat(data['warranty_expiry'])
        except:
            pass
    
    # Handle purchase_cost as float
    purchase_cost = None
    try:
        purchase_cost = float(data.get('purchase_cost')) if data.get('purchase_cost') else None
    except:
        pass
    
    asset = Asset(
        asset_tag=data['asset_tag'], name=data['name'],
        category=data.get('category','other'), brand=data.get('brand'),
        model=data.get('model'), serial_number=data.get('serial_number'),
        specifications=data.get('specifications'), status=data.get('status','active'),
        location=data.get('location'), assigned_to_id=data.get('assigned_to_id'),
        purchase_date=purchase_date,
        purchase_cost=purchase_cost,
        warranty_expiry=warranty_expiry,
        notes=data.get('notes')
    )
    db.session.add(asset)
    db.session.add(AuditLog(user_id=user.id, action='asset.create', target_type='Asset',
                            details=data['asset_tag'], ip_address=request.remote_addr))
    db.session.commit()
    return jsonify(asset.to_dict()), 201

@assets_bp.route('/<int:asset_id>', methods=['GET'])
def get_asset(asset_id):
    asset = Asset.query.get_or_404(asset_id)
    data  = asset.to_dict()
    data['maintenance_history'] = [m.to_dict() for m in asset.maintenance.order_by(AssetMaintenance.created_at.desc()).all()]
    return jsonify(data), 200

@assets_bp.route('/<int:asset_id>', methods=['PUT'])
def update_asset(asset_id):
    user = current_user()
    if not user or user.role.name not in ('admin', 'it_staff'):
        return jsonify({'error': 'Insufficient permissions'}), 403
    asset = Asset.query.get_or_404(asset_id)
    data  = request.get_json()
    
    # Update string fields
    for f in ['name','category','brand','model','serial_number','specifications',
              'status','location','notes']:
        if f in data:
            setattr(asset, f, data[f])
    
    # Handle assigned_to_id as integer
    if 'assigned_to_id' in data:
        asset.assigned_to_id = int(data['assigned_to_id']) if data['assigned_to_id'] else None
    
    # Handle purchase_cost as float
    if 'purchase_cost' in data:
        try:
            asset.purchase_cost = float(data['purchase_cost']) if data['purchase_cost'] else None
        except:
            pass
    
    # Handle date fields safely
    if data.get('purchase_date') and data['purchase_date'].strip():
        try:
            asset.purchase_date = date.fromisoformat(data['purchase_date'])
        except:
            pass
    
    if data.get('warranty_expiry') and data['warranty_expiry'].strip():
        try:
            asset.warranty_expiry = date.fromisoformat(data['warranty_expiry'])
        except:
            pass
    
    db.session.commit()
    return jsonify(asset.to_dict()), 200

@assets_bp.route('/<int:asset_id>', methods=['DELETE'])
def delete_asset(asset_id):
    user = current_user()
    if not user or user.role.name != 'admin':
        return jsonify({'error': 'Admin only'}), 403
    asset = Asset.query.get_or_404(asset_id)
    db.session.delete(asset)
    db.session.commit()
    return jsonify({'message': 'Asset deleted'}), 200

@assets_bp.route('/<int:asset_id>/maintenance', methods=['POST'])
def add_maintenance(asset_id):
    user = current_user()
    if not user or user.role.name not in ('admin', 'it_staff'):
        return jsonify({'error': 'Insufficient permissions'}), 403
    asset = Asset.query.get_or_404(asset_id)
    data  = request.get_json()
    
    # Handle date fields safely
    scheduled_date = None
    if data.get('scheduled_date') and data['scheduled_date'].strip():
        try:
            scheduled_date = date.fromisoformat(data['scheduled_date'])
        except:
            pass
    
    completed_date = None
    if data.get('completed_date') and data['completed_date'].strip():
        try:
            completed_date = date.fromisoformat(data['completed_date'])
        except:
            pass
    
    # Handle cost as float
    cost = 0
    try:
        cost = float(data.get('cost', 0)) if data.get('cost') else 0
    except:
        pass
    
    m = AssetMaintenance(
        asset_id=asset_id, performed_by_id=user.id,
        maintenance_type=data.get('maintenance_type','repair'),
        description=data.get('description'), cost=cost,
        scheduled_date=scheduled_date,
        completed_date=completed_date,
        status=data.get('status','scheduled')
    )
    if m.status == 'in_progress' and asset.status == 'active':
        asset.status = 'maintenance'
    if m.status == 'completed' and asset.status == 'maintenance':
        asset.status = 'active'
    db.session.add(m)
    db.session.commit()
    return jsonify(m.to_dict()), 201
