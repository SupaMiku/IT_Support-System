"""Knowledge Base routes – /api/kb"""
from flask import Blueprint, request, jsonify, session
from database import db
from models import KnowledgeBaseArticle, User

kb_bp = Blueprint('kb', __name__)

def current_user():
    uid = session.get('user_id')
    return User.query.get(uid) if uid else None

@kb_bp.route('/', methods=['GET'])
def list_articles():
    q = KnowledgeBaseArticle.query
    user = current_user()
    # non-staff only sees published
    if not user or user.role.name not in ('admin', 'it_staff'):
        q = q.filter_by(is_published=True)
    if request.args.get('category'): q = q.filter_by(category=request.args['category'])
    if request.args.get('search'):
        term = f"%{request.args['search']}%"
        q = q.filter(KnowledgeBaseArticle.title.ilike(term) | KnowledgeBaseArticle.content.ilike(term))
    return jsonify([a.to_dict() for a in q.order_by(KnowledgeBaseArticle.views.desc()).all()]), 200

@kb_bp.route('/<int:article_id>', methods=['GET'])
def get_article(article_id):
    article = KnowledgeBaseArticle.query.get_or_404(article_id)
    user = current_user()
    # Non-staff users can only read published articles
    if not user or user.role.name not in ('admin', 'it_staff'):
        if not article.is_published:
            return jsonify({'error': 'Access denied'}), 403
    article.views += 1
    db.session.commit()
    return jsonify(article.to_dict()), 200

@kb_bp.route('/', methods=['POST'])
def create_article():
    user = current_user()
    if not user or user.role.name not in ('admin', 'it_staff'):
        return jsonify({'error': 'Insufficient permissions'}), 403
    data = request.get_json()
    a = KnowledgeBaseArticle(
        title=data['title'], content=data['content'],
        category=data.get('category','general'),
        author_id=user.id, is_published=data.get('is_published', False)
    )
    db.session.add(a)
    db.session.commit()
    return jsonify(a.to_dict()), 201

@kb_bp.route('/<int:article_id>', methods=['PUT'])
def update_article(article_id):
    user = current_user()
    if not user or user.role.name not in ('admin', 'it_staff'):
        return jsonify({'error': 'Insufficient permissions'}), 403
    article = KnowledgeBaseArticle.query.get_or_404(article_id)
    data = request.get_json()
    for f in ['title','content','category','is_published']:
        if f in data: setattr(article, f, data[f])
    db.session.commit()
    return jsonify(article.to_dict()), 200

@kb_bp.route('/<int:article_id>', methods=['DELETE'])
def delete_article(article_id):
    user = current_user()
    if not user or user.role.name != 'admin':
        return jsonify({'error': 'Admin only'}), 403
    article = KnowledgeBaseArticle.query.get_or_404(article_id)
    db.session.delete(article)
    db.session.commit()
    return jsonify({'message': 'Article deleted'}), 200
