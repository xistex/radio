import random
import numpy as np
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_
from src.models.user import db
from src.models.question import Question, UserAnswer
from src.models.priority import TopicFrequency, UserTopicPriority, QuestionSelectionLog, get_user_topic_priority

class IntelligentQuestionSelector:
    """Seletor inteligente de questões baseado na regra de Pareto e desempenho individual"""
    
    def __init__(self, user_id):
        self.user_id = user_id
        self.pareto_weight = 0.8  # 80% das questões dos temas importantes
        self.performance_weight = 0.6  # Peso do desempenho individual
        
    def select_questions(self, limit=10, specialty=None, difficulty=None, session_id=None):
        """
        Seleciona questões usando algoritmo inteligente baseado em Pareto + desempenho
        """
        selected_questions = []
        selection_logs = []
        
        # Calcular quantas questões de cada tipo selecionar
        pareto_count = int(limit * self.pareto_weight)  # 80% dos temas importantes
        performance_count = limit - pareto_count  # 20% baseado em desempenho
        
        # 1. Selecionar questões dos temas importantes (Pareto)
        pareto_questions = self._select_pareto_questions(
            count=pareto_count,
            specialty=specialty,
            difficulty=difficulty
        )
        selected_questions.extend(pareto_questions)
        
        # 2. Selecionar questões baseadas no desempenho individual
        performance_questions = self._select_performance_questions(
            count=performance_count,
            specialty=specialty,
            difficulty=difficulty,
            exclude_ids=[q.id for q in pareto_questions]
        )
        selected_questions.extend(performance_questions)
        
        # 3. Se não temos questões suficientes, completar com seleção aleatória
        if len(selected_questions) < limit:
            remaining = limit - len(selected_questions)
            random_questions = self._select_random_questions(
                count=remaining,
                specialty=specialty,
                difficulty=difficulty,
                exclude_ids=[q.id for q in selected_questions]
            )
            selected_questions.extend(random_questions)
        
        # 4. Embaralhar a ordem final
        random.shuffle(selected_questions)
        
        # 5. Registrar logs de seleção
        self._log_selections(selected_questions, session_id)
        
        return selected_questions[:limit]
    
    def _select_pareto_questions(self, count, specialty=None, difficulty=None):
        """Seleciona questões dos temas que mais caem (top 20%)"""
        if count <= 0:
            return []
        
        # Buscar temas do top 20% (Pareto)
        top_topics = TopicFrequency.query.filter(
            TopicFrequency.pareto_tier.in_(['top20', 'important'])
        ).all()
        
        if not top_topics:
            return []
        
        # Criar distribuição de probabilidades baseada na importância
        topic_weights = []
        topic_names = []
        
        for topic in top_topics:
            if specialty and topic.specialty != specialty:
                continue
            topic_names.append(topic.specialty)
            topic_weights.append(topic.importance_score)
        
        if not topic_names:
            return []
        
        # Normalizar pesos
        total_weight = sum(topic_weights)
        probabilities = [w / total_weight for w in topic_weights]
        
        # Selecionar temas baseado nas probabilidades
        selected_topics = np.random.choice(
            topic_names,
            size=min(count, len(topic_names)),
            p=probabilities,
            replace=True
        )
        
        # Buscar questões dos temas selecionados
        questions = []
        for topic in selected_topics:
            question = self._get_random_question_from_topic(
                topic, difficulty, exclude_answered=True
            )
            if question:
                questions.append(question)
        
        return questions
    
    def _select_performance_questions(self, count, specialty=None, difficulty=None, exclude_ids=None):
        """Seleciona questões baseadas no desempenho individual do usuário"""
        if count <= 0:
            return []
        
        exclude_ids = exclude_ids or []
        
        # Buscar prioridades do usuário
        user_priorities = UserTopicPriority.query.filter_by(
            user_id=self.user_id
        ).all()
        
        if not user_priorities:
            return []
        
        # Filtrar por especialidade se especificado
        if specialty:
            user_priorities = [p for p in user_priorities if p.specialty == specialty]
        
        # Ordenar por prioridade final (maior = mais importante para o usuário)
        user_priorities.sort(key=lambda x: x.final_priority, reverse=True)
        
        # Selecionar questões dos temas prioritários
        questions = []
        for priority in user_priorities:
            if len(questions) >= count:
                break
            
            question = self._get_random_question_from_topic(
                priority.specialty, 
                difficulty, 
                exclude_answered=False,  # Permitir questões já respondidas para revisão
                exclude_ids=exclude_ids
            )
            
            if question:
                questions.append(question)
                exclude_ids.append(question.id)
        
        return questions
    
    def _select_random_questions(self, count, specialty=None, difficulty=None, exclude_ids=None):
        """Seleção aleatória para completar a quota"""
        if count <= 0:
            return []
        
        exclude_ids = exclude_ids or []
        
        query = Question.query
        
        if specialty:
            query = query.filter(Question.specialty == specialty)
        
        if difficulty:
            query = query.filter(Question.difficulty == difficulty)
        
        if exclude_ids:
            query = query.filter(~Question.id.in_(exclude_ids))
        
        # Excluir questões já respondidas pelo usuário (opcional)
        answered_ids = db.session.query(UserAnswer.question_id).filter_by(
            user_id=self.user_id
        ).subquery()
        
        query = query.filter(~Question.id.in_(answered_ids))
        
        questions = query.order_by(func.random()).limit(count).all()
        return questions
    
    def _get_random_question_from_topic(self, topic, difficulty=None, exclude_answered=True, exclude_ids=None):
        """Busca uma questão aleatória de um tópico específico"""
        exclude_ids = exclude_ids or []
        
        query = Question.query.filter(Question.specialty == topic)
        
        if difficulty:
            query = query.filter(Question.difficulty == difficulty)
        
        if exclude_ids:
            query = query.filter(~Question.id.in_(exclude_ids))
        
        if exclude_answered:
            # Excluir questões já respondidas
            answered_ids = db.session.query(UserAnswer.question_id).filter_by(
                user_id=self.user_id
            ).subquery()
            query = query.filter(~Question.id.in_(answered_ids))
        
        question = query.order_by(func.random()).first()
        return question
    
    def _log_selections(self, questions, session_id=None):
        """Registra as seleções para análise posterior"""
        for i, question in enumerate(questions):
            # Determinar método de seleção baseado na posição
            if i < int(len(questions) * self.pareto_weight):
                method = 'pareto'
            else:
                method = 'performance'
            
            # Buscar prioridade do usuário para este tópico
            priority = get_user_topic_priority(self.user_id, question.specialty)
            
            log = QuestionSelectionLog(
                user_id=self.user_id,
                session_id=session_id,
                specialty=question.specialty,
                selection_method=method,
                priority_score=priority.final_priority,
                question_id=question.id
            )
            db.session.add(log)
        
        db.session.commit()
    
    def update_user_performance(self, question_id, is_correct, response_time=None):
        """Atualiza o desempenho do usuário e recalcula prioridades"""
        question = Question.query.get(question_id)
        if not question:
            return
        
        # Atualizar prioridade do tópico
        priority = get_user_topic_priority(self.user_id, question.specialty)
        priority.update_performance(is_correct)
        
        # Atualizar log de seleção se existir
        log = QuestionSelectionLog.query.filter_by(
            user_id=self.user_id,
            question_id=question_id
        ).order_by(QuestionSelectionLog.selected_at.desc()).first()
        
        if log:
            log.was_correct = is_correct
            log.response_time = response_time
        
        db.session.commit()
    
    def get_user_priorities_summary(self):
        """Retorna resumo das prioridades do usuário"""
        priorities = UserTopicPriority.query.filter_by(
            user_id=self.user_id
        ).order_by(UserTopicPriority.final_priority.desc()).all()
        
        summary = {
            'total_topics': len(priorities),
            'priorities': [p.to_dict() for p in priorities],
            'needs_attention': [
                p.to_dict() for p in priorities 
                if p.accuracy_rate < 70 and p.questions_answered >= 3
            ],
            'mastered': [
                p.to_dict() for p in priorities 
                if p.accuracy_rate >= 85 and p.questions_answered >= 5
            ]
        }
        
        return summary
    
    def get_pareto_analysis(self):
        """Retorna análise dos temas baseada na regra de Pareto"""
        topic_frequencies = TopicFrequency.query.order_by(
            TopicFrequency.frequency_percentage.desc()
        ).all()
        
        total_frequency = sum(tf.frequency_percentage for tf in topic_frequencies)
        cumulative = 0
        pareto_analysis = []
        
        for tf in topic_frequencies:
            cumulative += tf.frequency_percentage
            cumulative_percentage = (cumulative / total_frequency) * 100
            
            pareto_analysis.append({
                'specialty': tf.specialty,
                'frequency_percentage': tf.frequency_percentage,
                'cumulative_percentage': cumulative_percentage,
                'pareto_tier': tf.pareto_tier,
                'importance_score': tf.importance_score,
                'is_top_20': cumulative_percentage <= 20
            })
        
        return {
            'analysis': pareto_analysis,
            'top_20_topics': [
                item for item in pareto_analysis 
                if item['is_top_20']
            ],
            'total_topics': len(topic_frequencies)
        }

