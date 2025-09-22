from datetime import datetime, timedelta
from src.models.user import db, User
from src.models.study_session import StudySession
from src.models.question import UserAnswer
from src.services.question_selector import IntelligentQuestionSelector
from src.services.gamification import GamificationService
import random

class MicroLearningService:
    """Serviço de micro-learning para sessões curtas e eficazes"""
    
    def __init__(self, user_id):
        self.user_id = user_id
        self.user = User.query.get(user_id)
        self.session_length = 10  # Sessões de 10 questões (micro-learning)
        self.max_session_time = 15  # Máximo 15 minutos por sessão
    
    def create_micro_session(self, specialty=None, difficulty=None, session_type='daily'):
        """Cria uma nova micro-sessão de aprendizagem"""
        try:
            # Usar seleção inteligente para escolher questões
            selector = IntelligentQuestionSelector(self.user_id)
            questions = selector.select_questions(
                limit=self.session_length,
                specialty=specialty,
                difficulty=difficulty
            )
            
            if not questions:
                return None, "Nenhuma questão disponível para esta sessão"
            
            # Criar sessão
            session = StudySession(
                user_id=self.user_id,
                session_type=session_type,
                total_questions=len(questions),
                questions_data=[q.id for q in questions],
                target_time=self.max_session_time * 60  # em segundos
            )
            db.session.add(session)
            db.session.commit()
            
            # Log da seleção
            selector._log_selections(questions, session.id)
            
            return session, None
            
        except Exception as e:
            return None, str(e)
    
    def get_session_questions(self, session_id):
        """Retorna as questões de uma sessão"""
        session = StudySession.query.get(session_id)
        
        if not session or session.user_id != self.user_id:
            return None, "Sessão não encontrada"
        
        if not session.questions_data:
            return None, "Sessão sem questões"
        
        # Buscar questões
        from src.models.question import Question
        questions = Question.query.filter(
            Question.id.in_(session.questions_data)
        ).all()
        
        # Ordenar na mesma ordem da sessão
        ordered_questions = []
        for q_id in session.questions_data:
            for q in questions:
                if q.id == q_id:
                    ordered_questions.append(q)
                    break
        
        return ordered_questions, None
    
    def submit_session_answer(self, session_id, question_id, selected_option, response_time=None):
        """Submete resposta de uma questão na sessão"""
        try:
            session = StudySession.query.get(session_id)
            
            if not session or session.user_id != self.user_id:
                return None, "Sessão não encontrada"
            
            # Verificar se a questão pertence à sessão
            if question_id not in session.questions_data:
                return None, "Questão não pertence a esta sessão"
            
            # Buscar questão
            from src.models.question import Question
            question = Question.query.get(question_id)
            
            if not question:
                return None, "Questão não encontrada"
            
            # Verificar se já foi respondida nesta sessão
            existing_answer = UserAnswer.query.filter_by(
                user_id=self.user_id,
                question_id=question_id,
                session_id=session_id
            ).first()
            
            if existing_answer:
                return None, "Questão já foi respondida nesta sessão"
            
            # Verificar resposta
            is_correct = selected_option == question.correct_option
            
            # Criar resposta
            answer = UserAnswer(
                user_id=self.user_id,
                question_id=question_id,
                selected_option=selected_option,
                is_correct=is_correct,
                response_time=response_time,
                session_id=session_id
            )
            db.session.add(answer)
            
            # Atualizar estatísticas da sessão
            session.questions_answered += 1
            if is_correct:
                session.correct_answers += 1
            
            # Calcular XP
            gamification = GamificationService(self.user_id)
            xp_earned = gamification.calculate_xp_for_answer(
                is_correct, question.difficulty, response_time
            )
            
            session.xp_earned += xp_earned
            self.user.xp += xp_earned
            
            # Atualizar sistema de priorização
            selector = IntelligentQuestionSelector(self.user_id)
            selector.update_user_performance(question_id, is_correct, response_time)
            
            # Verificar se a sessão foi completada
            session_completed = session.questions_answered >= session.total_questions
            
            if session_completed:
                self.complete_session(session_id)
            
            db.session.commit()
            
            return {
                'is_correct': is_correct,
                'correct_option': question.correct_option,
                'explanation': question.explanation,
                'xp_earned': xp_earned,
                'session_progress': {
                    'answered': session.questions_answered,
                    'total': session.total_questions,
                    'correct': session.correct_answers,
                    'accuracy': (session.correct_answers / session.questions_answered * 100) if session.questions_answered > 0 else 0
                },
                'session_completed': session_completed
            }, None
            
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    def complete_session(self, session_id):
        """Completa uma micro-sessão"""
        try:
            session = StudySession.query.get(session_id)
            
            if not session or session.user_id != self.user_id:
                return None, "Sessão não encontrada"
            
            if session.completed_at:
                return None, "Sessão já foi completada"
            
            # Marcar como completada
            session.completed_at = datetime.utcnow()
            
            # Calcular bonus de conclusão
            gamification = GamificationService(self.user_id)
            completion_bonus = gamification.calculate_session_bonus(session_id)
            
            session.xp_earned += completion_bonus
            self.user.xp += completion_bonus
            
            # Atualizar nível e streak
            level_up, levels_gained = gamification.update_user_level()
            new_streak = gamification.update_streak()
            
            # Verificar conquistas
            achievements = gamification.check_achievements()
            
            db.session.commit()
            
            return {
                'session_summary': {
                    'questions_answered': session.questions_answered,
                    'correct_answers': session.correct_answers,
                    'accuracy_rate': (session.correct_answers / session.questions_answered * 100) if session.questions_answered > 0 else 0,
                    'total_xp_earned': session.xp_earned,
                    'completion_bonus': completion_bonus,
                    'session_duration': (session.completed_at - session.created_at).total_seconds()
                },
                'user_progress': {
                    'level_up': level_up,
                    'levels_gained': levels_gained,
                    'new_level': self.user.level,
                    'total_xp': self.user.xp,
                    'streak': new_streak
                },
                'achievements_unlocked': achievements
            }, None
            
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    def get_session_summary(self, session_id):
        """Retorna resumo de uma sessão"""
        session = StudySession.query.get(session_id)
        
        if not session or session.user_id != self.user_id:
            return None, "Sessão não encontrada"
        
        # Buscar respostas da sessão
        answers = UserAnswer.query.filter_by(
            user_id=self.user_id,
            session_id=session_id
        ).all()
        
        # Estatísticas detalhadas
        correct_by_specialty = {}
        total_by_specialty = {}
        
        for answer in answers:
            specialty = answer.question.specialty
            
            if specialty not in total_by_specialty:
                total_by_specialty[specialty] = 0
                correct_by_specialty[specialty] = 0
            
            total_by_specialty[specialty] += 1
            if answer.is_correct:
                correct_by_specialty[specialty] += 1
        
        specialty_stats = []
        for specialty in total_by_specialty:
            accuracy = (correct_by_specialty[specialty] / total_by_specialty[specialty] * 100)
            specialty_stats.append({
                'specialty': specialty,
                'correct': correct_by_specialty[specialty],
                'total': total_by_specialty[specialty],
                'accuracy': round(accuracy, 2)
            })
        
        return {
            'session': session.to_dict(),
            'specialty_breakdown': specialty_stats,
            'answers': [answer.to_dict() for answer in answers]
        }, None
    
    def get_recommended_session_type(self):
        """Recomenda o tipo de sessão baseado no histórico do usuário"""
        # Verificar última atividade
        last_session = StudySession.query.filter_by(
            user_id=self.user_id
        ).order_by(StudySession.created_at.desc()).first()
        
        if not last_session:
            return 'introduction', "Primeira sessão - Vamos começar com questões variadas"
        
        # Verificar se estudou hoje
        today = datetime.utcnow().date()
        if last_session.created_at.date() < today:
            return 'daily', "Sessão diária - Mantenha sua sequência de estudos"
        
        # Verificar desempenho recente
        recent_sessions = StudySession.query.filter(
            StudySession.user_id == self.user_id,
            StudySession.created_at >= datetime.utcnow() - timedelta(days=7),
            StudySession.completed_at.isnot(None)
        ).all()
        
        if recent_sessions:
            avg_accuracy = sum(
                (s.correct_answers / s.questions_answered * 100) if s.questions_answered > 0 else 0
                for s in recent_sessions
            ) / len(recent_sessions)
            
            if avg_accuracy < 60:
                return 'review', "Sessão de revisão - Vamos reforçar os conceitos"
            elif avg_accuracy > 85:
                return 'challenge', "Sessão desafio - Teste seus conhecimentos avançados"
        
        return 'practice', "Sessão de prática - Continue aprimorando seus conhecimentos"
    
    def get_optimal_study_time(self):
        """Sugere o melhor horário para estudar baseado no histórico"""
        # Analisar horários de melhor desempenho
        sessions_with_good_performance = StudySession.query.filter(
            StudySession.user_id == self.user_id,
            StudySession.completed_at.isnot(None)
        ).all()
        
        if not sessions_with_good_performance:
            return "Qualquer horário é bom para começar!"
        
        # Agrupar por hora do dia
        hour_performance = {}
        for session in sessions_with_good_performance:
            hour = session.created_at.hour
            accuracy = (session.correct_answers / session.questions_answered * 100) if session.questions_answered > 0 else 0
            
            if hour not in hour_performance:
                hour_performance[hour] = []
            hour_performance[hour].append(accuracy)
        
        # Calcular média por hora
        hour_averages = {}
        for hour, accuracies in hour_performance.items():
            hour_averages[hour] = sum(accuracies) / len(accuracies)
        
        if hour_averages:
            best_hour = max(hour_averages, key=hour_averages.get)
            best_accuracy = hour_averages[best_hour]
            
            if best_accuracy > 70:
                return f"Seu melhor horário é às {best_hour}h (média de {best_accuracy:.1f}% de acerto)"
        
        return "Continue estudando em horários variados para encontrar seu melhor momento"
    
    def get_study_streak_info(self):
        """Retorna informações sobre a sequência de estudos"""
        gamification = GamificationService(self.user_id)
        daily_progress = gamification.get_daily_goal_progress()
        
        return {
            'current_streak': self.user.streak,
            'daily_progress': daily_progress,
            'next_milestone': self._get_next_streak_milestone(),
            'motivation_message': self._get_motivation_message()
        }
    
    def _get_next_streak_milestone(self):
        """Retorna a próxima meta de sequência"""
        current_streak = self.user.streak
        
        milestones = [3, 7, 14, 30, 50, 100]
        
        for milestone in milestones:
            if current_streak < milestone:
                return {
                    'days': milestone,
                    'remaining': milestone - current_streak,
                    'reward': f"{milestone * 2} XP bonus"
                }
        
        return {
            'days': current_streak + 50,
            'remaining': 50,
            'reward': "Conquista especial"
        }
    
    def _get_motivation_message(self):
        """Retorna mensagem motivacional baseada no progresso"""
        streak = self.user.streak
        
        if streak == 0:
            return "Comece sua jornada hoje! 🚀"
        elif streak < 3:
            return f"Você está no caminho certo! Continue por mais {3 - streak} dias. 💪"
        elif streak < 7:
            return f"Excelente! Faltam apenas {7 - streak} dias para completar uma semana. 🔥"
        elif streak < 30:
            return f"Impressionante! {streak} dias de dedicação. Continue assim! ⭐"
        else:
            return f"Incrível! {streak} dias consecutivos. Você é um exemplo de dedicação! 🏆"

