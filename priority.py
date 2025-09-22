from src.models.user import db
from datetime import datetime
import json

class TopicFrequency(db.Model):
    """Frequência de temas nas provas históricas"""
    id = db.Column(db.Integer, primary_key=True)
    specialty = db.Column(db.String(100), nullable=False, unique=True)
    exam_source = db.Column(db.String(50), nullable=False)  # SES-GO, PSU-GO, ALL
    
    # Estatísticas de frequência
    total_questions = db.Column(db.Integer, default=0)
    frequency_percentage = db.Column(db.Float, default=0.0)  # % de aparição nas provas
    importance_score = db.Column(db.Float, default=1.0)  # Score de importância (1-10)
    pareto_tier = db.Column(db.String(20), default='normal')  # top20, important, normal, rare
    
    # Metadados
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def calculate_pareto_tier(self):
        """Calcula o tier baseado na regra de Pareto"""
        if self.frequency_percentage >= 15.0:  # Top 20% dos temas
            self.pareto_tier = 'top20'
            self.importance_score = 10.0
        elif self.frequency_percentage >= 8.0:  # Importantes
            self.pareto_tier = 'important'
            self.importance_score = 7.0
        elif self.frequency_percentage >= 3.0:  # Normais
            self.pareto_tier = 'normal'
            self.importance_score = 4.0
        else:  # Raros
            self.pareto_tier = 'rare'
            self.importance_score = 1.0

    def to_dict(self):
        return {
            'id': self.id,
            'specialty': self.specialty,
            'exam_source': self.exam_source,
            'total_questions': self.total_questions,
            'frequency_percentage': self.frequency_percentage,
            'importance_score': self.importance_score,
            'pareto_tier': self.pareto_tier,
            'last_updated': self.last_updated.isoformat()
        }

class UserTopicPriority(db.Model):
    """Prioridade personalizada de temas para cada usuário"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    specialty = db.Column(db.String(100), nullable=False)
    
    # Estatísticas do usuário
    questions_answered = db.Column(db.Integer, default=0)
    correct_answers = db.Column(db.Integer, default=0)
    accuracy_rate = db.Column(db.Float, default=0.0)
    
    # Sistema de priorização
    base_priority = db.Column(db.Float, default=1.0)  # Prioridade base (frequência)
    performance_modifier = db.Column(db.Float, default=1.0)  # Modificador por desempenho
    final_priority = db.Column(db.Float, default=1.0)  # Prioridade final calculada
    
    # Controle de exposição
    last_seen = db.Column(db.DateTime)
    times_seen = db.Column(db.Integer, default=0)
    consecutive_correct = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    user = db.relationship('User', backref='topic_priorities')
    
    # Índice único
    __table_args__ = (db.UniqueConstraint('user_id', 'specialty', name='unique_user_specialty_priority'),)

    def update_performance(self, is_correct):
        """Atualiza o desempenho e recalcula prioridade"""
        self.questions_answered += 1
        
        if is_correct:
            self.correct_answers += 1
            self.consecutive_correct += 1
        else:
            self.consecutive_correct = 0
        
        # Recalcular taxa de acerto
        self.accuracy_rate = (self.correct_answers / self.questions_answered) * 100
        
        # Atualizar modificador de desempenho
        self.calculate_performance_modifier()
        
        # Recalcular prioridade final
        self.calculate_final_priority()
        
        # Atualizar timestamps
        self.last_seen = datetime.utcnow()
        self.times_seen += 1
        self.updated_at = datetime.utcnow()

    def calculate_performance_modifier(self):
        """Calcula modificador baseado no desempenho do usuário"""
        if self.questions_answered < 3:
            # Poucos dados, manter neutro
            self.performance_modifier = 1.0
            return
        
        # Modificador baseado na taxa de acerto
        if self.accuracy_rate < 50:
            # Baixo desempenho = maior prioridade
            self.performance_modifier = 2.0
        elif self.accuracy_rate < 70:
            # Desempenho médio = prioridade aumentada
            self.performance_modifier = 1.5
        elif self.accuracy_rate < 85:
            # Bom desempenho = prioridade normal
            self.performance_modifier = 1.0
        else:
            # Excelente desempenho = prioridade reduzida (mas não zero)
            self.performance_modifier = 0.5
        
        # Ajuste por sequência de acertos
        if self.consecutive_correct >= 5:
            # Muitos acertos consecutivos = reduzir prioridade
            self.performance_modifier *= 0.7
        elif self.consecutive_correct == 0 and self.questions_answered >= 3:
            # Erro recente = aumentar prioridade
            self.performance_modifier *= 1.3

    def calculate_final_priority(self):
        """Calcula a prioridade final combinando base + desempenho"""
        self.final_priority = self.base_priority * self.performance_modifier
        
        # Garantir que a prioridade não seja zero
        if self.final_priority < 0.1:
            self.final_priority = 0.1

    def to_dict(self):
        return {
            'id': self.id,
            'specialty': self.specialty,
            'questions_answered': self.questions_answered,
            'correct_answers': self.correct_answers,
            'accuracy_rate': round(self.accuracy_rate, 2),
            'base_priority': self.base_priority,
            'performance_modifier': self.performance_modifier,
            'final_priority': self.final_priority,
            'consecutive_correct': self.consecutive_correct,
            'times_seen': self.times_seen,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
            'updated_at': self.updated_at.isoformat()
        }

class QuestionSelectionLog(db.Model):
    """Log de seleção de questões para análise e otimização"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('study_session.id'))
    
    # Dados da seleção
    specialty = db.Column(db.String(100), nullable=False)
    selection_method = db.Column(db.String(50), nullable=False)  # pareto, performance, random
    priority_score = db.Column(db.Float)
    
    # Resultado
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    was_correct = db.Column(db.Boolean)
    response_time = db.Column(db.Integer)  # em segundos
    
    # Timestamp
    selected_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    user = db.relationship('User', backref='question_selections')
    question = db.relationship('Question', backref='selection_logs')

    def to_dict(self):
        return {
            'id': self.id,
            'specialty': self.specialty,
            'selection_method': self.selection_method,
            'priority_score': self.priority_score,
            'was_correct': self.was_correct,
            'response_time': self.response_time,
            'selected_at': self.selected_at.isoformat()
        }

def initialize_topic_frequencies():
    """Inicializa as frequências dos temas baseado em dados históricos"""
    
    # Dados baseados em análise das provas SES-GO e PSU-GO
    frequency_data = [
        # Top 20% - Temas que mais caem (regra de Pareto)
        {'specialty': 'Clínica Médica', 'frequency': 25.0, 'total': 150},
        {'specialty': 'Cirurgia Geral', 'frequency': 20.0, 'total': 120},
        {'specialty': 'Pediatria', 'frequency': 15.0, 'total': 90},
        {'specialty': 'Ginecologia e Obstetrícia', 'frequency': 12.0, 'total': 72},
        
        # Importantes - 20% seguintes
        {'specialty': 'Medicina Preventiva', 'frequency': 8.0, 'total': 48},
        {'specialty': 'Cardiologia', 'frequency': 6.0, 'total': 36},
        {'specialty': 'Infectologia', 'frequency': 5.0, 'total': 30},
        
        # Normais - Aparecem regularmente
        {'specialty': 'Neurologia', 'frequency': 3.0, 'total': 18},
        {'specialty': 'Pneumologia', 'frequency': 2.5, 'total': 15},
        {'specialty': 'Gastroenterologia', 'frequency': 2.0, 'total': 12},
        {'specialty': 'Endocrinologia', 'frequency': 1.5, 'total': 9},
        
        # Raros - Aparecem ocasionalmente
        {'specialty': 'Dermatologia', 'frequency': 1.0, 'total': 6},
        {'specialty': 'Oftalmologia', 'frequency': 0.8, 'total': 5},
        {'specialty': 'Otorrinolaringologia', 'frequency': 0.7, 'total': 4},
        {'specialty': 'Urologia', 'frequency': 0.5, 'total': 3}
    ]
    
    for data in frequency_data:
        # Verificar se já existe
        existing = TopicFrequency.query.filter_by(
            specialty=data['specialty'],
            exam_source='ALL'
        ).first()
        
        if not existing:
            topic_freq = TopicFrequency(
                specialty=data['specialty'],
                exam_source='ALL',
                total_questions=data['total'],
                frequency_percentage=data['frequency']
            )
            topic_freq.calculate_pareto_tier()
            db.session.add(topic_freq)
    
    db.session.commit()

def get_user_topic_priority(user_id, specialty):
    """Obtém ou cria prioridade de tópico para usuário"""
    priority = UserTopicPriority.query.filter_by(
        user_id=user_id,
        specialty=specialty
    ).first()
    
    if not priority:
        # Buscar frequência base do tópico
        topic_freq = TopicFrequency.query.filter_by(
            specialty=specialty,
            exam_source='ALL'
        ).first()
        
        base_priority = topic_freq.importance_score if topic_freq else 1.0
        
        priority = UserTopicPriority(
            user_id=user_id,
            specialty=specialty,
            base_priority=base_priority,
            final_priority=base_priority
        )
        db.session.add(priority)
        db.session.commit()
    
    return priority

