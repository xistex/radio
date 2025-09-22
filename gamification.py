from datetime import datetime, timedelta
from src.models.user import db, User
from src.models.achievement import Achievement, UserAchievement
from src.models.study_session import StudySession
from src.models.question import UserAnswer
from src.models.priority import UserTopicPriority
import math

class GamificationService:
    """Serviço de gamificação para o MedStudy"""
    
    def __init__(self, user_id):
        self.user_id = user_id
        self.user = User.query.get(user_id)
    
    def calculate_xp_for_answer(self, is_correct, difficulty='medium', response_time=None):
        """Calcula XP baseado na resposta"""
        if not is_correct:
            return 0
        
        # XP base por dificuldade
        base_xp = {
            'easy': 5,
            'medium': 10,
            'hard': 15
        }.get(difficulty, 10)
        
        # Bonus por velocidade (se respondeu em menos de 30 segundos)
        speed_bonus = 0
        if response_time and response_time < 30:
            speed_bonus = 2
        
        return base_xp + speed_bonus
    
    def calculate_session_bonus(self, session_id):
        """Calcula bonus de XP por completar sessão"""
        session = StudySession.query.get(session_id)
        if not session or session.user_id != self.user_id:
            return 0
        
        # Bonus base por completar sessão
        completion_bonus = 25
        
        # Bonus por acurácia
        if session.questions_answered > 0:
            accuracy = (session.correct_answers / session.questions_answered) * 100
            if accuracy >= 90:
                completion_bonus += 25  # Bonus por excelência
            elif accuracy >= 70:
                completion_bonus += 15  # Bonus por bom desempenho
        
        # Bonus por sequência (streak)
        if self.user.streak >= 7:
            completion_bonus += 20  # Bonus por semana completa
        elif self.user.streak >= 3:
            completion_bonus += 10  # Bonus por 3 dias seguidos
        
        return completion_bonus
    
    def update_user_level(self):
        """Atualiza o nível do usuário baseado no XP"""
        # Fórmula: level = sqrt(xp / 100)
        new_level = int(math.sqrt(self.user.xp / 100)) + 1
        old_level = self.user.level
        
        self.user.level = new_level
        
        # Verificar se subiu de nível
        if new_level > old_level:
            self.check_level_achievements(new_level)
            return True, new_level - old_level
        
        return False, 0
    
    def update_streak(self):
        """Atualiza a sequência de dias estudando"""
        today = datetime.utcnow().date()
        
        if self.user.last_activity_date:
            last_activity = self.user.last_activity_date.date()
            
            if last_activity == today:
                # Já estudou hoje, não alterar streak
                return self.user.streak
            elif last_activity == today - timedelta(days=1):
                # Estudou ontem, incrementar streak
                self.user.streak += 1
            else:
                # Quebrou a sequência
                self.user.streak = 1
        else:
            # Primeira atividade
            self.user.streak = 1
        
        self.user.last_activity_date = datetime.utcnow()
        
        # Verificar conquistas de streak
        self.check_streak_achievements()
        
        return self.user.streak
    
    def check_achievements(self, context=None):
        """Verifica e desbloqueia conquistas"""
        achievements_unlocked = []
        
        # Conquistas básicas
        achievements_unlocked.extend(self.check_basic_achievements())
        
        # Conquistas de especialidade
        achievements_unlocked.extend(self.check_specialty_achievements())
        
        # Conquistas de desempenho
        achievements_unlocked.extend(self.check_performance_achievements())
        
        # Conquistas de consistência
        achievements_unlocked.extend(self.check_consistency_achievements())
        
        return achievements_unlocked
    
    def check_basic_achievements(self):
        """Conquistas básicas de progresso"""
        achievements = []
        
        # Total de questões respondidas
        total_answered = UserAnswer.query.filter_by(user_id=self.user_id).count()
        
        milestones = [
            (10, "Primeiros Passos", "Respondeu 10 questões"),
            (50, "Estudante Dedicado", "Respondeu 50 questões"),
            (100, "Centena Completa", "Respondeu 100 questões"),
            (500, "Meio Milhar", "Respondeu 500 questões"),
            (1000, "Milhar Conquistado", "Respondeu 1000 questões")
        ]
        
        for count, name, description in milestones:
            if total_answered >= count:
                achievement = self.unlock_achievement(
                    name=name,
                    description=description,
                    category="progress",
                    xp_reward=count // 10
                )
                if achievement:
                    achievements.append(achievement)
        
        return achievements
    
    def check_specialty_achievements(self):
        """Conquistas por especialidade"""
        achievements = []
        
        # Verificar domínio de especialidades (>= 80% de acerto com pelo menos 20 questões)
        priorities = UserTopicPriority.query.filter_by(user_id=self.user_id).all()
        
        for priority in priorities:
            if priority.questions_answered >= 20 and priority.accuracy_rate >= 80:
                achievement = self.unlock_achievement(
                    name=f"Mestre em {priority.specialty}",
                    description=f"Alcançou 80% de acerto em {priority.specialty}",
                    category="specialty",
                    xp_reward=50
                )
                if achievement:
                    achievements.append(achievement)
        
        return achievements
    
    def check_performance_achievements(self):
        """Conquistas de desempenho"""
        achievements = []
        
        # Acurácia geral
        total_answered = UserAnswer.query.filter_by(user_id=self.user_id).count()
        correct_answers = UserAnswer.query.filter_by(user_id=self.user_id, is_correct=True).count()
        
        if total_answered >= 50:
            accuracy = (correct_answers / total_answered) * 100
            
            if accuracy >= 90:
                achievement = self.unlock_achievement(
                    name="Precisão Cirúrgica",
                    description="Manteve 90% de acerto com pelo menos 50 questões",
                    category="performance",
                    xp_reward=100
                )
                if achievement:
                    achievements.append(achievement)
            elif accuracy >= 80:
                achievement = self.unlock_achievement(
                    name="Alta Performance",
                    description="Manteve 80% de acerto com pelo menos 50 questões",
                    category="performance",
                    xp_reward=75
                )
                if achievement:
                    achievements.append(achievement)
        
        return achievements
    
    def check_streak_achievements(self):
        """Conquistas de sequência"""
        achievements = []
        
        streak_milestones = [
            (3, "Três Dias Seguidos", "Estudou por 3 dias consecutivos"),
            (7, "Uma Semana Completa", "Estudou por 7 dias consecutivos"),
            (14, "Duas Semanas", "Estudou por 14 dias consecutivos"),
            (30, "Um Mês Dedicado", "Estudou por 30 dias consecutivos"),
            (100, "Cem Dias de Foco", "Estudou por 100 dias consecutivos")
        ]
        
        for days, name, description in streak_milestones:
            if self.user.streak >= days:
                achievement = self.unlock_achievement(
                    name=name,
                    description=description,
                    category="consistency",
                    xp_reward=days * 2
                )
                if achievement:
                    achievements.append(achievement)
        
        return achievements
    
    def check_level_achievements(self, level):
        """Conquistas por nível alcançado"""
        achievements = []
        
        level_milestones = [
            (5, "Nível 5", "Alcançou o nível 5"),
            (10, "Nível 10", "Alcançou o nível 10"),
            (20, "Nível 20", "Alcançou o nível 20"),
            (50, "Nível 50", "Alcançou o nível 50")
        ]
        
        for target_level, name, description in level_milestones:
            if level >= target_level:
                achievement = self.unlock_achievement(
                    name=name,
                    description=description,
                    category="level",
                    xp_reward=target_level * 10
                )
                if achievement:
                    achievements.append(achievement)
        
        return achievements
    
    def check_consistency_achievements(self):
        """Conquistas de consistência de estudo"""
        achievements = []
        
        # Verificar sessões completadas nos últimos 7 dias
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_sessions = StudySession.query.filter(
            StudySession.user_id == self.user_id,
            StudySession.completed_at >= week_ago,
            StudySession.completed_at.isnot(None)
        ).count()
        
        if recent_sessions >= 7:
            achievement = self.unlock_achievement(
                name="Estudante Consistente",
                description="Completou pelo menos uma sessão por dia na última semana",
                category="consistency",
                xp_reward=100
            )
            if achievement:
                achievements.append(achievement)
        
        return achievements
    
    def unlock_achievement(self, name, description, category, xp_reward=0):
        """Desbloqueia uma conquista se ainda não foi obtida"""
        # Verificar se a conquista já existe
        achievement = Achievement.query.filter_by(name=name).first()
        
        if not achievement:
            # Criar nova conquista
            achievement = Achievement(
                name=name,
                description=description,
                category=category,
                xp_reward=xp_reward
            )
            db.session.add(achievement)
            db.session.commit()
        
        # Verificar se o usuário já tem esta conquista
        user_achievement = UserAchievement.query.filter_by(
            user_id=self.user_id,
            achievement_id=achievement.id
        ).first()
        
        if not user_achievement:
            # Desbloquear conquista para o usuário
            user_achievement = UserAchievement(
                user_id=self.user_id,
                achievement_id=achievement.id
            )
            db.session.add(user_achievement)
            
            # Adicionar XP da conquista
            if xp_reward > 0:
                self.user.xp += xp_reward
                self.update_user_level()
            
            db.session.commit()
            
            return {
                'achievement': achievement.to_dict(),
                'xp_reward': xp_reward,
                'unlocked_at': user_achievement.unlocked_at.isoformat()
            }
        
        return None
    
    def get_user_achievements(self):
        """Retorna todas as conquistas do usuário"""
        user_achievements = db.session.query(UserAchievement, Achievement).join(
            Achievement
        ).filter(UserAchievement.user_id == self.user_id).all()
        
        achievements = []
        for user_ach, achievement in user_achievements:
            achievements.append({
                'achievement': achievement.to_dict(),
                'unlocked_at': user_ach.unlocked_at.isoformat()
            })
        
        return achievements
    
    def get_available_achievements(self):
        """Retorna conquistas ainda não desbloqueadas"""
        unlocked_ids = db.session.query(UserAchievement.achievement_id).filter_by(
            user_id=self.user_id
        ).subquery()
        
        available = Achievement.query.filter(
            ~Achievement.id.in_(unlocked_ids)
        ).all()
        
        return [ach.to_dict() for ach in available]
    
    def get_daily_goal_progress(self):
        """Retorna progresso da meta diária"""
        today = datetime.utcnow().date()
        
        # Questões respondidas hoje
        today_answers = UserAnswer.query.filter(
            UserAnswer.user_id == self.user_id,
            db.func.date(UserAnswer.answered_at) == today
        ).count()
        
        daily_goal = self.user.daily_goal or 10
        progress_percentage = min((today_answers / daily_goal) * 100, 100)
        
        return {
            'answered_today': today_answers,
            'daily_goal': daily_goal,
            'progress_percentage': progress_percentage,
            'goal_completed': today_answers >= daily_goal
        }
    
    def get_weekly_summary(self):
        """Retorna resumo semanal de atividades"""
        week_ago = datetime.utcnow() - timedelta(days=7)
        
        # Questões da semana
        weekly_answers = UserAnswer.query.filter(
            UserAnswer.user_id == self.user_id,
            UserAnswer.answered_at >= week_ago
        ).count()
        
        # Sessões da semana
        weekly_sessions = StudySession.query.filter(
            StudySession.user_id == self.user_id,
            StudySession.created_at >= week_ago,
            StudySession.completed_at.isnot(None)
        ).count()
        
        # XP ganho na semana
        weekly_xp = db.session.query(db.func.sum(StudySession.xp_earned)).filter(
            StudySession.user_id == self.user_id,
            StudySession.created_at >= week_ago
        ).scalar() or 0
        
        return {
            'questions_answered': weekly_answers,
            'sessions_completed': weekly_sessions,
            'xp_earned': weekly_xp,
            'current_streak': self.user.streak,
            'days_studied': min(self.user.streak, 7)
        }

