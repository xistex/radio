from src.models.user import db
from datetime import datetime
import json

class Achievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    icon = db.Column(db.String(100))  # Nome do ícone ou URL
    category = db.Column(db.String(50), nullable=False)  # study, streak, accuracy, etc.
    
    # Critérios para desbloqueio
    criteria_type = db.Column(db.String(50), nullable=False)  # questions_answered, streak, accuracy, etc.
    criteria_value = db.Column(db.Integer, nullable=False)
    
    # Recompensas
    xp_reward = db.Column(db.Integer, default=0)
    
    # Raridade
    rarity = db.Column(db.String(20), default='common')  # common, rare, epic, legendary
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    user_achievements = db.relationship('UserAchievement', backref='achievement', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'category': self.category,
            'criteria_type': self.criteria_type,
            'criteria_value': self.criteria_value,
            'xp_reward': self.xp_reward,
            'rarity': self.rarity
        }

class UserAchievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievement.id'), nullable=False)
    unlocked_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Índice único para evitar conquistas duplicadas
    __table_args__ = (db.UniqueConstraint('user_id', 'achievement_id', name='unique_user_achievement'),)

    def to_dict(self):
        return {
            'id': self.id,
            'achievement_id': self.achievement_id,
            'achievement': self.achievement.to_dict() if self.achievement else None,
            'unlocked_at': self.unlocked_at.isoformat()
        }

class UserProgress(db.Model):
    """Progresso detalhado do usuário por especialidade"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    specialty = db.Column(db.String(100), nullable=False)
    
    # Estatísticas de questões
    total_questions = db.Column(db.Integer, default=0)
    correct_answers = db.Column(db.Integer, default=0)
    total_time_spent = db.Column(db.Integer, default=0)  # em segundos
    
    # Estatísticas por dificuldade
    easy_correct = db.Column(db.Integer, default=0)
    easy_total = db.Column(db.Integer, default=0)
    medium_correct = db.Column(db.Integer, default=0)
    medium_total = db.Column(db.Integer, default=0)
    hard_correct = db.Column(db.Integer, default=0)
    hard_total = db.Column(db.Integer, default=0)
    
    # Timestamps
    last_studied = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    user = db.relationship('User', backref='progress_by_specialty')
    
    # Índice único
    __table_args__ = (db.UniqueConstraint('user_id', 'specialty', name='unique_user_specialty'),)

    def get_accuracy_rate(self):
        if self.total_questions == 0:
            return 0
        return (self.correct_answers / self.total_questions) * 100

    def get_accuracy_by_difficulty(self, difficulty):
        if difficulty == 'easy':
            return (self.easy_correct / self.easy_total * 100) if self.easy_total > 0 else 0
        elif difficulty == 'medium':
            return (self.medium_correct / self.medium_total * 100) if self.medium_total > 0 else 0
        elif difficulty == 'hard':
            return (self.hard_correct / self.hard_total * 100) if self.hard_total > 0 else 0
        return 0

    def get_average_time_per_question(self):
        if self.total_questions == 0:
            return 0
        return self.total_time_spent / self.total_questions

    def update_stats(self, is_correct, difficulty, time_spent):
        """Atualiza as estatísticas com uma nova resposta"""
        self.total_questions += 1
        self.total_time_spent += time_spent
        self.last_studied = datetime.utcnow()
        
        if is_correct:
            self.correct_answers += 1
        
        # Atualiza estatísticas por dificuldade
        if difficulty == 'easy':
            self.easy_total += 1
            if is_correct:
                self.easy_correct += 1
        elif difficulty == 'medium':
            self.medium_total += 1
            if is_correct:
                self.medium_correct += 1
        elif difficulty == 'hard':
            self.hard_total += 1
            if is_correct:
                self.hard_correct += 1

    def to_dict(self):
        return {
            'id': self.id,
            'specialty': self.specialty,
            'total_questions': self.total_questions,
            'correct_answers': self.correct_answers,
            'accuracy_rate': self.get_accuracy_rate(),
            'average_time_per_question': self.get_average_time_per_question(),
            'difficulty_stats': {
                'easy': {
                    'total': self.easy_total,
                    'correct': self.easy_correct,
                    'accuracy': self.get_accuracy_by_difficulty('easy')
                },
                'medium': {
                    'total': self.medium_total,
                    'correct': self.medium_correct,
                    'accuracy': self.get_accuracy_by_difficulty('medium')
                },
                'hard': {
                    'total': self.hard_total,
                    'correct': self.hard_correct,
                    'accuracy': self.get_accuracy_by_difficulty('hard')
                }
            },
            'last_studied': self.last_studied.isoformat() if self.last_studied else None,
            'updated_at': self.updated_at.isoformat()
        }

class Leaderboard(db.Model):
    """Ranking semanal dos usuários"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    week_start = db.Column(db.Date, nullable=False)
    
    # Estatísticas da semana
    weekly_xp = db.Column(db.Integer, default=0)
    questions_answered = db.Column(db.Integer, default=0)
    study_sessions = db.Column(db.Integer, default=0)
    
    # Posição no ranking
    rank = db.Column(db.Integer)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    user = db.relationship('User', backref='leaderboard_entries')
    
    # Índice único
    __table_args__ = (db.UniqueConstraint('user_id', 'week_start', name='unique_user_week'),)

    def to_dict(self):
        return {
            'id': self.id,
            'user': {
                'id': self.user.id,
                'username': self.user.username,
                'level': self.user.level,
                'avatar_url': self.user.avatar_url
            },
            'weekly_xp': self.weekly_xp,
            'questions_answered': self.questions_answered,
            'study_sessions': self.study_sessions,
            'rank': self.rank,
            'week_start': self.week_start.isoformat()
        }

