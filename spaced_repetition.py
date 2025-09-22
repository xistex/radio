from datetime import datetime, timedelta
from src.models.user import db
from src.models.flashcard import Flashcard, FlashcardReview
from src.models.question import Question, UserAnswer
from src.models.priority import UserTopicPriority, get_user_topic_priority
import math
import random

class SpacedRepetitionService:
    """Serviço de repetição espaçada baseado no algoritmo SM-2 (SuperMemo)"""
    
    def __init__(self, user_id):
        self.user_id = user_id
        
        # Intervalos iniciais em dias (baseado na curva de esquecimento)
        self.initial_intervals = [1, 3, 7, 14, 30, 90, 180, 365]
        
        # Fatores de facilidade (ease factor)
        self.min_ease_factor = 1.3
        self.default_ease_factor = 2.5
        self.max_ease_factor = 4.0
    
    def generate_flashcards_from_questions(self, limit=50):
        """Gera flashcards automaticamente a partir de questões respondidas incorretamente"""
        try:
            # Buscar questões respondidas incorretamente pelo usuário
            incorrect_answers = db.session.query(UserAnswer, Question).join(
                Question
            ).filter(
                UserAnswer.user_id == self.user_id,
                UserAnswer.is_correct == False
            ).order_by(UserAnswer.answered_at.desc()).limit(limit).all()
            
            flashcards_created = 0
            
            for answer, question in incorrect_answers:
                # Verificar se já existe flashcard para esta questão
                existing_flashcard = Flashcard.query.filter_by(
                    user_id=self.user_id,
                    question_id=question.id
                ).first()
                
                if not existing_flashcard:
                    # Criar flashcard
                    flashcard = self.create_flashcard_from_question(question)
                    if flashcard:
                        flashcards_created += 1
            
            return flashcards_created, None
            
        except Exception as e:
            return 0, str(e)
    
    def create_flashcard_from_question(self, question):
        """Cria um flashcard a partir de uma questão"""
        try:
            # Extrair conceito principal da questão
            front_text = self.extract_concept_from_question(question)
            
            # Criar resposta baseada na explicação
            back_text = self.create_answer_from_explanation(question)
            
            flashcard = Flashcard(
                user_id=self.user_id,
                question_id=question.id,
                specialty=question.specialty,
                front_text=front_text,
                back_text=back_text,
                difficulty=question.difficulty,
                ease_factor=self.default_ease_factor,
                interval_days=1,
                next_review_date=datetime.utcnow() + timedelta(days=1)
            )
            
            db.session.add(flashcard)
            db.session.commit()
            
            return flashcard
            
        except Exception as e:
            db.session.rollback()
            return None
    
    def extract_concept_from_question(self, question):
        """Extrai o conceito principal de uma questão para criar a frente do flashcard"""
        # Simplificação: usar as primeiras palavras da questão
        # Em uma implementação mais avançada, usaríamos NLP para extrair conceitos
        
        question_text = question.question_text
        
        # Tentar identificar padrões comuns em questões médicas
        if "diagnóstico" in question_text.lower():
            return f"Qual o diagnóstico mais provável para: {question_text[:100]}..."
        elif "tratamento" in question_text.lower():
            return f"Qual o tratamento indicado para: {question_text[:100]}..."
        elif "exame" in question_text.lower():
            return f"Qual exame é indicado para: {question_text[:100]}..."
        else:
            # Usar a questão completa se for curta, ou resumir
            if len(question_text) <= 150:
                return question_text
            else:
                return f"{question_text[:150]}..."
    
    def create_answer_from_explanation(self, question):
        """Cria a resposta do flashcard baseada na explicação da questão"""
        explanation = question.explanation or ""
        correct_option = question.correct_option
        
        # Buscar a opção correta
        correct_answer_text = ""
        if question.options and correct_option in question.options:
            correct_answer_text = question.options[correct_option]
        
        # Combinar resposta correta com explicação
        back_text = f"**Resposta:** {correct_option}) {correct_answer_text}\n\n"
        
        if explanation:
            back_text += f"**Explicação:** {explanation}"
        
        return back_text
    
    def get_due_flashcards(self, limit=20):
        """Retorna flashcards que estão prontos para revisão"""
        try:
            now = datetime.utcnow()
            
            due_flashcards = Flashcard.query.filter(
                Flashcard.user_id == self.user_id,
                Flashcard.next_review_date <= now,
                Flashcard.is_active == True
            ).order_by(Flashcard.next_review_date.asc()).limit(limit).all()
            
            return due_flashcards, None
            
        except Exception as e:
            return [], str(e)
    
    def review_flashcard(self, flashcard_id, quality_rating):
        """
        Processa a revisão de um flashcard
        quality_rating: 0-5 (0=não lembrou, 5=lembrou perfeitamente)
        """
        try:
            flashcard = Flashcard.query.get(flashcard_id)
            
            if not flashcard or flashcard.user_id != self.user_id:
                return None, "Flashcard não encontrado"
            
            # Registrar a revisão
            review = FlashcardReview(
                flashcard_id=flashcard_id,
                user_id=self.user_id,
                quality_rating=quality_rating,
                previous_interval=flashcard.interval_days,
                previous_ease_factor=flashcard.ease_factor
            )
            db.session.add(review)
            
            # Atualizar flashcard usando algoritmo SM-2
            self.update_flashcard_schedule(flashcard, quality_rating)
            
            # Atualizar prioridade do tópico
            priority = get_user_topic_priority(self.user_id, flashcard.specialty)
            is_correct = quality_rating >= 3  # Considera correto se rating >= 3
            priority.update_performance(is_correct)
            
            db.session.commit()
            
            return {
                'flashcard': flashcard.to_dict(),
                'review': review.to_dict(),
                'next_review_date': flashcard.next_review_date.isoformat(),
                'interval_days': flashcard.interval_days
            }, None
            
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    def update_flashcard_schedule(self, flashcard, quality_rating):
        """Atualiza o cronograma do flashcard usando algoritmo SM-2 modificado"""
        
        # Incrementar contador de revisões
        flashcard.review_count += 1
        
        if quality_rating < 3:
            # Resposta incorreta - resetar intervalo
            flashcard.interval_days = 1
            flashcard.ease_factor = max(
                self.min_ease_factor,
                flashcard.ease_factor - 0.2
            )
        else:
            # Resposta correta - calcular próximo intervalo
            if flashcard.review_count == 1:
                flashcard.interval_days = 1
            elif flashcard.review_count == 2:
                flashcard.interval_days = 6
            else:
                # Usar fórmula SM-2
                flashcard.interval_days = int(
                    flashcard.interval_days * flashcard.ease_factor
                )
            
            # Ajustar ease factor baseado na qualidade
            ease_adjustment = 0.1 - (5 - quality_rating) * (0.08 + (5 - quality_rating) * 0.02)
            flashcard.ease_factor = max(
                self.min_ease_factor,
                min(self.max_ease_factor, flashcard.ease_factor + ease_adjustment)
            )
        
        # Calcular próxima data de revisão
        flashcard.next_review_date = datetime.utcnow() + timedelta(days=flashcard.interval_days)
        flashcard.last_reviewed = datetime.utcnow()
    
    def get_flashcard_stats(self):
        """Retorna estatísticas dos flashcards do usuário"""
        try:
            total_flashcards = Flashcard.query.filter_by(
                user_id=self.user_id,
                is_active=True
            ).count()
            
            # Flashcards por status
            now = datetime.utcnow()
            
            due_count = Flashcard.query.filter(
                Flashcard.user_id == self.user_id,
                Flashcard.next_review_date <= now,
                Flashcard.is_active == True
            ).count()
            
            learning_count = Flashcard.query.filter(
                Flashcard.user_id == self.user_id,
                Flashcard.review_count < 3,
                Flashcard.is_active == True
            ).count()
            
            mature_count = Flashcard.query.filter(
                Flashcard.user_id == self.user_id,
                Flashcard.review_count >= 3,
                Flashcard.interval_days >= 21,
                Flashcard.is_active == True
            ).count()
            
            # Estatísticas por especialidade
            specialty_stats = db.session.query(
                Flashcard.specialty,
                db.func.count(Flashcard.id).label('total'),
                db.func.avg(Flashcard.ease_factor).label('avg_ease'),
                db.func.avg(Flashcard.interval_days).label('avg_interval')
            ).filter(
                Flashcard.user_id == self.user_id,
                Flashcard.is_active == True
            ).group_by(Flashcard.specialty).all()
            
            specialty_data = []
            for stat in specialty_stats:
                specialty_data.append({
                    'specialty': stat.specialty,
                    'total_flashcards': stat.total,
                    'average_ease': round(stat.avg_ease, 2) if stat.avg_ease else 0,
                    'average_interval': round(stat.avg_interval, 1) if stat.avg_interval else 0
                })
            
            return {
                'total_flashcards': total_flashcards,
                'due_flashcards': due_count,
                'learning_flashcards': learning_count,
                'mature_flashcards': mature_count,
                'by_specialty': specialty_data
            }, None
            
        except Exception as e:
            return {}, str(e)
    
    def get_study_forecast(self, days=7):
        """Retorna previsão de flashcards para os próximos dias"""
        try:
            forecast = []
            base_date = datetime.utcnow().date()
            
            for i in range(days):
                target_date = base_date + timedelta(days=i)
                start_datetime = datetime.combine(target_date, datetime.min.time())
                end_datetime = datetime.combine(target_date, datetime.max.time())
                
                count = Flashcard.query.filter(
                    Flashcard.user_id == self.user_id,
                    Flashcard.next_review_date >= start_datetime,
                    Flashcard.next_review_date <= end_datetime,
                    Flashcard.is_active == True
                ).count()
                
                forecast.append({
                    'date': target_date.isoformat(),
                    'flashcards_due': count,
                    'is_today': i == 0
                })
            
            return forecast, None
            
        except Exception as e:
            return [], str(e)
    
    def create_custom_flashcard(self, front_text, back_text, specialty, difficulty='medium'):
        """Permite ao usuário criar flashcards personalizados"""
        try:
            flashcard = Flashcard(
                user_id=self.user_id,
                specialty=specialty,
                front_text=front_text,
                back_text=back_text,
                difficulty=difficulty,
                ease_factor=self.default_ease_factor,
                interval_days=1,
                next_review_date=datetime.utcnow() + timedelta(days=1),
                is_custom=True
            )
            
            db.session.add(flashcard)
            db.session.commit()
            
            return flashcard.to_dict(), None
            
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    def get_retention_rate(self, days=30):
        """Calcula taxa de retenção dos flashcards"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Reviews dos últimos X dias
            recent_reviews = FlashcardReview.query.filter(
                FlashcardReview.user_id == self.user_id,
                FlashcardReview.reviewed_at >= cutoff_date
            ).all()
            
            if not recent_reviews:
                return 0, None
            
            # Considerar correto se quality_rating >= 3
            correct_reviews = [r for r in recent_reviews if r.quality_rating >= 3]
            retention_rate = (len(correct_reviews) / len(recent_reviews)) * 100
            
            return round(retention_rate, 2), None
            
        except Exception as e:
            return 0, str(e)
    
    def optimize_study_session(self, available_time_minutes=15):
        """Otimiza uma sessão de estudo baseada no tempo disponível"""
        try:
            # Estimar tempo por flashcard (média de 30 segundos)
            estimated_time_per_card = 0.5  # minutos
            max_cards = int(available_time_minutes / estimated_time_per_card)
            
            # Buscar flashcards devido, priorizando os mais atrasados
            due_flashcards, error = self.get_due_flashcards(limit=max_cards)
            
            if error:
                return [], error
            
            # Se não há flashcards devido, buscar alguns para revisão antecipada
            if not due_flashcards:
                upcoming_flashcards = Flashcard.query.filter(
                    Flashcard.user_id == self.user_id,
                    Flashcard.next_review_date <= datetime.utcnow() + timedelta(days=1),
                    Flashcard.is_active == True
                ).order_by(Flashcard.next_review_date.asc()).limit(max_cards // 2).all()
                
                return upcoming_flashcards, None
            
            return due_flashcards, None
            
        except Exception as e:
            return [], str(e)

