from src.models.user import db
from datetime import datetime, timedelta
import json

class Flashcard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    front_content = db.Column(db.Text, nullable=False)
    back_content = db.Column(db.Text, nullable=False)
    
    # Categorização
    specialty = db.Column(db.String(100), nullable=False)
    difficulty = db.Column(db.String(20), default='medium')
    tags = db.Column(db.Text)  # JSON array de tags
    
    # Relacionamento com questão (opcional)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    reviews = db.relationship('FlashcardReview', backref='flashcard', lazy=True)
    question = db.relationship('Question', backref='flashcards')

    def get_tags_list(self):
        """Retorna as tags como lista"""
        if self.tags:
            return json.loads(self.tags)
        return []

    def set_tags_list(self, tags_list):
        """Define as tags a partir de uma lista"""
        self.tags = json.dumps(tags_list)

    def to_dict(self):
        return {
            'id': self.id,
            'front_content': self.front_content,
            'back_content': self.back_content,
            'specialty': self.specialty,
            'difficulty': self.difficulty,
            'tags': self.get_tags_list(),
            'question_id': self.question_id,
            'created_at': self.created_at.isoformat()
        }

class FlashcardReview(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    flashcard_id = db.Column(db.Integer, db.ForeignKey('flashcard.id'), nullable=False)
    
    # Sistema de repetição espaçada
    ease_factor = db.Column(db.Float, default=2.5)  # Fator de facilidade (Anki algorithm)
    interval = db.Column(db.Integer, default=1)  # Intervalo em dias
    repetitions = db.Column(db.Integer, default=0)  # Número de repetições
    next_review_date = db.Column(db.Date, default=datetime.utcnow().date)
    
    # Última revisão
    last_review_date = db.Column(db.Date)
    last_quality = db.Column(db.Integer)  # 0-5 (0=blackout, 5=perfect)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def update_spaced_repetition(self, quality):
        """
        Atualiza o algoritmo de repetição espaçada baseado na qualidade da resposta
        Quality: 0-5 (0=não lembrou, 1=difícil, 2=hesitou, 3=fácil, 4=muito fácil, 5=perfeito)
        """
        self.last_review_date = datetime.utcnow().date()
        self.last_quality = quality
        
        if quality < 3:
            # Resposta incorreta ou difícil - reinicia o processo
            self.repetitions = 0
            self.interval = 1
        else:
            # Resposta correta
            if self.repetitions == 0:
                self.interval = 1
            elif self.repetitions == 1:
                self.interval = 6
            else:
                self.interval = int(self.interval * self.ease_factor)
            
            self.repetitions += 1
        
        # Atualiza o fator de facilidade
        self.ease_factor = max(1.3, self.ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)))
        
        # Define a próxima data de revisão
        self.next_review_date = datetime.utcnow().date() + timedelta(days=self.interval)

    def is_due_for_review(self):
        """Verifica se o flashcard está pronto para revisão"""
        return datetime.utcnow().date() >= self.next_review_date

    def to_dict(self):
        return {
            'id': self.id,
            'flashcard_id': self.flashcard_id,
            'ease_factor': self.ease_factor,
            'interval': self.interval,
            'repetitions': self.repetitions,
            'next_review_date': self.next_review_date.isoformat(),
            'last_review_date': self.last_review_date.isoformat() if self.last_review_date else None,
            'last_quality': self.last_quality,
            'is_due': self.is_due_for_review()
        }

class UserFlashcardProgress(db.Model):
    """Progresso do usuário por especialidade em flashcards"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    specialty = db.Column(db.String(100), nullable=False)
    
    # Estatísticas
    total_flashcards = db.Column(db.Integer, default=0)
    reviewed_flashcards = db.Column(db.Integer, default=0)
    mastered_flashcards = db.Column(db.Integer, default=0)  # repetitions >= 3
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    user = db.relationship('User', backref='flashcard_progress')
    
    # Índice único
    __table_args__ = (db.UniqueConstraint('user_id', 'specialty', name='unique_user_specialty_flashcard'),)

    def get_completion_rate(self):
        if self.total_flashcards == 0:
            return 0
        return (self.reviewed_flashcards / self.total_flashcards) * 100

    def get_mastery_rate(self):
        if self.total_flashcards == 0:
            return 0
        return (self.mastered_flashcards / self.total_flashcards) * 100

    def to_dict(self):
        return {
            'id': self.id,
            'specialty': self.specialty,
            'total_flashcards': self.total_flashcards,
            'reviewed_flashcards': self.reviewed_flashcards,
            'mastered_flashcards': self.mastered_flashcards,
            'completion_rate': self.get_completion_rate(),
            'mastery_rate': self.get_mastery_rate(),
            'updated_at': self.updated_at.isoformat()
        }

