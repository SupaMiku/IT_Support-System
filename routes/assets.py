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
    asset = Asset(
        asset_tag=data['asset_tag'], name=data['name'],
        category=data.get('category','other'), brand=data.get('brand'),
        model=data.get('model'), serial_number=data.get('serial_number'),
        specifications=data.get('specifications'), status=data.get('status','active'),
        location=data.get('location'), assigned_to_id=data.get('assigned_to_id'),
        purchase_date=date.fromisoformat(data['purchase_date']) if data.get('purchase_date') else None,
        purchase_cost=data.get('purchase_cost'),
        warranty_expiry=date.fromisoformat(data['warranty_expiry']) if data.get('warranty_expiry') else None,
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
    for f in ['name','category','brand','model','serial_number','specifications',
              'status','location','assigned_to_id','purchase_cost','notes']:
        if f in data:
            setattr(asset, f, data[f])
    if data.get('purchase_date'):   asset.purchase_date   = date.fromisoformat(data['purchase_date'])
    if data.get('warranty_expiry'): asset.warranty_expiry = date.fromisoformat(data['warranty_expiry'])
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
    m = AssetMaintenance(
        asset_id=asset_id, performed_by_id=user.id,
        maintenance_type=data.get('maintenance_type','repair'),
        description=data.get('description'), cost=data.get('cost',0),
        scheduled_date=date.fromisoformat(data['scheduled_date']) if data.get('scheduled_date') else None,
        completed_date=date.fromisoformat(data['completed_date']) if data.get('completed_date') else None,
        status=data.get('status','scheduled')
    )
    if m.status == 'in_progress' and asset.status == 'active':
        asset.status = 'maintenance'
    if m.status == 'completed' and asset.status == 'maintenance':
        asset.status = 'active'
    db.session.add(m)
    db.session.commit()
    return jsonify(m.to_dict()), 201
