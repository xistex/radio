from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import os

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Gamificação
    xp = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=1)
    streak = db.Column(db.Integer, default=0)
    last_study_date = db.Column(db.Date)
    
    # Perfil
    avatar_url = db.Column(db.String(255))
    target_specialty = db.Column(db.String(100))
    daily_goal = db.Column(db.Integer, default=10)  # questões por dia
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relacionamentos
    answers = db.relationship('UserAnswer', backref='user', lazy=True)
    flashcard_reviews = db.relationship('FlashcardReview', backref='user', lazy=True)
    achievements = db.relationship('UserAchievement', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_token(self):
        payload = {
            'user_id': self.id,
            'exp': datetime.utcnow() + timedelta(days=7)
        }
        return jwt.encode(payload, os.environ.get('SECRET_KEY', 'default-secret'), algorithm='HS256')

    def add_xp(self, points):
        self.xp += points
        new_level = (self.xp // 100) + 1
        if new_level > self.level:
            self.level = new_level
            return True  # Level up!
        return False

    def update_streak(self):
        today = datetime.utcnow().date()
        if self.last_study_date:
            if self.last_study_date == today:
                return  # Já estudou hoje
            elif self.last_study_date == today - timedelta(days=1):
                self.streak += 1
            else:
                self.streak = 1
        else:
            self.streak = 1
        self.last_study_date = today

    def get_accuracy_rate(self):
        if not self.answers:
            return 0
        correct_answers = sum(1 for answer in self.answers if answer.is_correct)
        return (correct_answers / len(self.answers)) * 100

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'xp': self.xp,
            'level': self.level,
            'streak': self.streak,
            'avatar_url': self.avatar_url,
            'target_specialty': self.target_specialty,
            'daily_goal': self.daily_goal,
            'accuracy_rate': self.get_accuracy_rate(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
