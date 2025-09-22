from src.models.user import db
from datetime import datetime
import json

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    options = db.Column(db.Text, nullable=False)  # JSON string com as opções
    correct_answer = db.Column(db.String(1), nullable=False)  # A, B, C, D
    explanation = db.Column(db.Text)
    
    # Categorização
    specialty = db.Column(db.String(100), nullable=False)  # Clínica Médica, Cirurgia, etc.
    difficulty = db.Column(db.String(20), default='medium')  # easy, medium, hard
    exam_source = db.Column(db.String(50), nullable=False)  # SES-GO, PSU-GO
    exam_year = db.Column(db.Integer)
    
    # Estatísticas
    times_answered = db.Column(db.Integer, default=0)
    times_correct = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    answers = db.relationship('UserAnswer', backref='question', lazy=True)

    def get_options_dict(self):
        """Retorna as opções como dicionário"""
        return json.loads(self.options)

    def set_options_dict(self, options_dict):
        """Define as opções a partir de um dicionário"""
        self.options = json.dumps(options_dict)

    def get_accuracy_rate(self):
        """Calcula a taxa de acerto da questão"""
        if self.times_answered == 0:
            return 0
        return (self.times_correct / self.times_answered) * 100

    def update_stats(self, is_correct):
        """Atualiza as estatísticas da questão"""
        self.times_answered += 1
        if is_correct:
            self.times_correct += 1

    def to_dict(self, include_answer=False):
        result = {
            'id': self.id,
            'content': self.content,
            'options': self.get_options_dict(),
            'specialty': self.specialty,
            'difficulty': self.difficulty,
            'exam_source': self.exam_source,
            'exam_year': self.exam_year,
            'accuracy_rate': self.get_accuracy_rate(),
            'times_answered': self.times_answered
        }
        
        if include_answer:
            result['correct_answer'] = self.correct_answer
            result['explanation'] = self.explanation
            
        return result

class UserAnswer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    selected_answer = db.Column(db.String(1), nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False)
    time_spent = db.Column(db.Integer)  # tempo em segundos
    answered_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Índice único para evitar respostas duplicadas
    __table_args__ = (db.UniqueConstraint('user_id', 'question_id', name='unique_user_question'),)

    def to_dict(self):
        return {
            'id': self.id,
            'question_id': self.question_id,
            'selected_answer': self.selected_answer,
            'is_correct': self.is_correct,
            'time_spent': self.time_spent,
            'answered_at': self.answered_at.isoformat()
        }

class StudySession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    questions_answered = db.Column(db.Integer, default=0)
    correct_answers = db.Column(db.Integer, default=0)
    xp_earned = db.Column(db.Integer, default=0)
    session_type = db.Column(db.String(50), default='practice')  # practice, exam, review
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    user = db.relationship('User', backref='study_sessions')

    def get_accuracy_rate(self):
        if self.questions_answered == 0:
            return 0
        return (self.correct_answers / self.questions_answered) * 100

    def to_dict(self):
        return {
            'id': self.id,
            'questions_answered': self.questions_answered,
            'correct_answers': self.correct_answers,
            'accuracy_rate': self.get_accuracy_rate(),
            'xp_earned': self.xp_earned,
            'session_type': self.session_type,
            'started_at': self.started_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

