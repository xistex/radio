from flask import Blueprint, request, jsonify
from src.models.user import db, User
from datetime import datetime
import jwt
import os

auth_bp = Blueprint('auth', __name__)

def token_required(f):
    """Decorator para rotas que requerem autenticação"""
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            
            data = jwt.decode(token, os.environ.get('SECRET_KEY', 'default-secret'), algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])
            
            if not current_user:
                return jsonify({'message': 'User not found'}), 401
                
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid'}), 401
        
        return f(current_user, *args, **kwargs)
    
    decorated.__name__ = f.__name__
    return decorated

@auth_bp.route('/register', methods=['POST'])
def register():
    """Registrar novo usuário"""
    try:
        data = request.get_json()
        
        # Validar dados obrigatórios
        required_fields = ['username', 'email', 'password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'{field} is required'}), 400
        
        # Verificar se usuário já existe
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'message': 'Email already registered'}), 400
        
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'message': 'Username already taken'}), 400
        
        # Criar novo usuário
        user = User(
            username=data['username'],
            email=data['email'],
            target_specialty=data.get('target_specialty'),
            daily_goal=data.get('daily_goal', 10)
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        # Gerar token
        token = user.generate_token()
        
        return jsonify({
            'message': 'User registered successfully',
            'token': token,
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Registration failed: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login do usuário"""
    try:
        data = request.get_json()
        
        # Validar dados obrigatórios
        if not data.get('email') or not data.get('password'):
            return jsonify({'message': 'Email and password are required'}), 400
        
        # Buscar usuário
        user = User.query.filter_by(email=data['email']).first()
        
        if not user or not user.check_password(data['password']):
            return jsonify({'message': 'Invalid email or password'}), 401
        
        # Atualizar último login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Gerar token
        token = user.generate_token()
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Login failed: {str(e)}'}), 500

@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user(current_user):
    """Obter dados do usuário atual"""
    return jsonify({
        'user': current_user.to_dict()
    }), 200

@auth_bp.route('/refresh', methods=['POST'])
@token_required
def refresh_token(current_user):
    """Renovar token de autenticação"""
    token = current_user.generate_token()
    return jsonify({
        'token': token,
        'user': current_user.to_dict()
    }), 200

@auth_bp.route('/update-profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    """Atualizar perfil do usuário"""
    try:
        data = request.get_json()
        
        # Campos que podem ser atualizados
        updatable_fields = ['username', 'target_specialty', 'daily_goal', 'avatar_url']
        
        for field in updatable_fields:
            if field in data:
                if field == 'username':
                    # Verificar se username já existe
                    existing_user = User.query.filter_by(username=data[field]).first()
                    if existing_user and existing_user.id != current_user.id:
                        return jsonify({'message': 'Username already taken'}), 400
                
                setattr(current_user, field, data[field])
        
        current_user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': current_user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Update failed: {str(e)}'}), 500

@auth_bp.route('/change-password', methods=['PUT'])
@token_required
def change_password(current_user):
    """Alterar senha do usuário"""
    try:
        data = request.get_json()
        
        if not data.get('current_password') or not data.get('new_password'):
            return jsonify({'message': 'Current password and new password are required'}), 400
        
        # Verificar senha atual
        if not current_user.check_password(data['current_password']):
            return jsonify({'message': 'Current password is incorrect'}), 400
        
        # Atualizar senha
        current_user.set_password(data['new_password'])
        current_user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'message': 'Password changed successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Password change failed: {str(e)}'}), 500

