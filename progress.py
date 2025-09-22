from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.achievement import UserProgress, Achievement, UserAchievement, Leaderboard
from src.models.question import UserAnswer, StudySession
from src.models.flashcard import FlashcardReview
from src.routes.auth import token_required
from datetime import datetime, timedelta, date
from sqlalchemy import func, desc

progress_bp = Blueprint('progress', __name__)

@progress_bp.route('/dashboard', methods=['GET'])
@token_required
def get_dashboard_data(current_user):
    """Obter dados do dashboard principal"""
    try:
        # Estatísticas gerais
        total_questions = UserAnswer.query.filter_by(user_id=current_user.id).count()
        correct_answers = UserAnswer.query.filter_by(user_id=current_user.id, is_correct=True).count()
        
        # Atividade hoje
        today = date.today()
        questions_today = UserAnswer.query.filter(
            UserAnswer.user_id == current_user.id,
            func.date(UserAnswer.answered_at) == today
        ).count()
        
        # Flashcards devido hoje
        flashcards_due = FlashcardReview.query.filter(
            FlashcardReview.user_id == current_user.id,
            FlashcardReview.next_review_date <= today
        ).count()
        
        # Sessões de estudo recentes
        recent_sessions = StudySession.query.filter_by(
            user_id=current_user.id
        ).filter(
            StudySession.completed_at.isnot(None)
        ).order_by(desc(StudySession.completed_at)).limit(5).all()
        
        # Progresso por especialidade
        specialty_progress = UserProgress.query.filter_by(user_id=current_user.id).all()
        
        # Conquistas recentes
        recent_achievements = UserAchievement.query.filter_by(
            user_id=current_user.id
        ).order_by(desc(UserAchievement.unlocked_at)).limit(3).all()
        
        return jsonify({
            'user_stats': {
                'xp': current_user.xp,
                'level': current_user.level,
                'streak': current_user.streak,
                'total_questions': total_questions,
                'correct_answers': correct_answers,
                'accuracy_rate': round((correct_answers / total_questions * 100) if total_questions > 0 else 0, 2)
            },
            'today_activity': {
                'questions_answered': questions_today,
                'goal_progress': round((questions_today / current_user.daily_goal * 100) if current_user.daily_goal > 0 else 0, 2),
                'flashcards_due': flashcards_due
            },
            'recent_sessions': [session.to_dict() for session in recent_sessions],
            'specialty_progress': [progress.to_dict() for progress in specialty_progress],
            'recent_achievements': [achievement.to_dict() for achievement in recent_achievements]
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to get dashboard data: {str(e)}'}), 500

@progress_bp.route('/detailed', methods=['GET'])
@token_required
def get_detailed_progress(current_user):
    """Obter progresso detalhado do usuário"""
    try:
        specialty = request.args.get('specialty')
        days = int(request.args.get('days', 30))
        
        # Data de início
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Progresso diário
        daily_progress = db.session.query(
            func.date(UserAnswer.answered_at).label('date'),
            func.count(UserAnswer.id).label('questions'),
            func.sum(func.case([(UserAnswer.is_correct == True, 1)], else_=0)).label('correct')
        ).filter(
            UserAnswer.user_id == current_user.id,
            UserAnswer.answered_at >= start_date
        ).group_by(func.date(UserAnswer.answered_at)).all()
        
        # Converter para formato de resposta
        daily_data = []
        for day in daily_progress:
            accuracy = (day.correct / day.questions * 100) if day.questions > 0 else 0
            daily_data.append({
                'date': day.date.isoformat(),
                'questions_answered': day.questions,
                'correct_answers': day.correct,
                'accuracy_rate': round(accuracy, 2)
            })
        
        # Progresso por especialidade (se especificado)
        specialty_data = None
        if specialty:
            specialty_progress = UserProgress.query.filter_by(
                user_id=current_user.id,
                specialty=specialty
            ).first()
            
            if specialty_progress:
                specialty_data = specialty_progress.to_dict()
        
        # Tempo de estudo por dia
        study_time = db.session.query(
            func.date(UserAnswer.answered_at).label('date'),
            func.sum(UserAnswer.time_spent).label('total_time')
        ).filter(
            UserAnswer.user_id == current_user.id,
            UserAnswer.answered_at >= start_date
        ).group_by(func.date(UserAnswer.answered_at)).all()
        
        time_data = []
        for day in study_time:
            time_data.append({
                'date': day.date.isoformat(),
                'study_time_minutes': round((day.total_time or 0) / 60, 2)
            })
        
        return jsonify({
            'daily_progress': daily_data,
            'specialty_detail': specialty_data,
            'study_time': time_data,
            'period_days': days
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to get detailed progress: {str(e)}'}), 500

@progress_bp.route('/achievements', methods=['GET'])
@token_required
def get_user_achievements(current_user):
    """Obter conquistas do usuário"""
    try:
        # Conquistas desbloqueadas
        unlocked = db.session.query(UserAchievement, Achievement).join(
            Achievement
        ).filter(
            UserAchievement.user_id == current_user.id
        ).order_by(desc(UserAchievement.unlocked_at)).all()
        
        # Todas as conquistas disponíveis
        all_achievements = Achievement.query.all()
        
        unlocked_ids = {ua.achievement_id for ua, a in unlocked}
        
        unlocked_data = []
        for user_achievement, achievement in unlocked:
            data = achievement.to_dict()
            data['unlocked_at'] = user_achievement.unlocked_at.isoformat()
            unlocked_data.append(data)
        
        available_data = []
        for achievement in all_achievements:
            if achievement.id not in unlocked_ids:
                data = achievement.to_dict()
                data['progress'] = calculate_achievement_progress(current_user, achievement)
                available_data.append(data)
        
        return jsonify({
            'unlocked': unlocked_data,
            'available': available_data,
            'total_unlocked': len(unlocked_data),
            'total_available': len(all_achievements)
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to get achievements: {str(e)}'}), 500

def calculate_achievement_progress(user, achievement):
    """Calcular progresso para uma conquista específica"""
    try:
        if achievement.criteria_type == 'questions_answered':
            current_value = UserAnswer.query.filter_by(user_id=user.id).count()
        elif achievement.criteria_type == 'streak':
            current_value = user.streak
        elif achievement.criteria_type == 'accuracy':
            total = UserAnswer.query.filter_by(user_id=user.id).count()
            correct = UserAnswer.query.filter_by(user_id=user.id, is_correct=True).count()
            current_value = (correct / total * 100) if total > 0 else 0
        elif achievement.criteria_type == 'xp':
            current_value = user.xp
        elif achievement.criteria_type == 'level':
            current_value = user.level
        else:
            current_value = 0
        
        progress_percentage = min(100, (current_value / achievement.criteria_value * 100))
        
        return {
            'current_value': current_value,
            'target_value': achievement.criteria_value,
            'percentage': round(progress_percentage, 2)
        }
    except:
        return {'current_value': 0, 'target_value': achievement.criteria_value, 'percentage': 0}

@progress_bp.route('/leaderboard', methods=['GET'])
@token_required
def get_leaderboard(current_user):
    """Obter ranking semanal"""
    try:
        # Calcular início da semana atual
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        
        # Buscar ou criar entrada do leaderboard para o usuário atual
        user_entry = Leaderboard.query.filter_by(
            user_id=current_user.id,
            week_start=week_start
        ).first()
        
        if not user_entry:
            user_entry = Leaderboard(
                user_id=current_user.id,
                week_start=week_start
            )
            db.session.add(user_entry)
        
        # Atualizar estatísticas da semana atual
        week_end = week_start + timedelta(days=7)
        
        # XP ganho esta semana (aproximação baseada em respostas)
        weekly_answers = UserAnswer.query.filter(
            UserAnswer.user_id == current_user.id,
            func.date(UserAnswer.answered_at) >= week_start,
            func.date(UserAnswer.answered_at) < week_end
        ).all()
        
        weekly_xp = sum(10 if answer.is_correct else 0 for answer in weekly_answers)
        user_entry.weekly_xp = weekly_xp
        user_entry.questions_answered = len(weekly_answers)
        
        # Sessões de estudo esta semana
        weekly_sessions = StudySession.query.filter(
            StudySession.user_id == current_user.id,
            func.date(StudySession.started_at) >= week_start,
            func.date(StudySession.started_at) < week_end,
            StudySession.completed_at.isnot(None)
        ).count()
        
        user_entry.study_sessions = weekly_sessions
        
        db.session.commit()
        
        # Buscar top 10 do ranking
        top_users = db.session.query(Leaderboard).filter_by(
            week_start=week_start
        ).order_by(desc(Leaderboard.weekly_xp)).limit(10).all()
        
        # Atualizar ranks
        for i, entry in enumerate(top_users, 1):
            entry.rank = i
        
        db.session.commit()
        
        # Buscar posição do usuário atual se não estiver no top 10
        user_rank = user_entry.rank
        if not user_rank:
            higher_ranked = Leaderboard.query.filter(
                Leaderboard.week_start == week_start,
                Leaderboard.weekly_xp > user_entry.weekly_xp
            ).count()
            user_rank = higher_ranked + 1
        
        leaderboard_data = [entry.to_dict() for entry in top_users]
        
        return jsonify({
            'leaderboard': leaderboard_data,
            'user_position': {
                'rank': user_rank,
                'weekly_xp': user_entry.weekly_xp,
                'questions_answered': user_entry.questions_answered,
                'study_sessions': user_entry.study_sessions
            },
            'week_start': week_start.isoformat()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to get leaderboard: {str(e)}'}), 500

@progress_bp.route('/study-streak', methods=['GET'])
@token_required
def get_study_streak(current_user):
    """Obter informações sobre sequência de estudos"""
    try:
        # Últimos 30 dias de atividade
        days = 30
        start_date = date.today() - timedelta(days=days-1)
        
        daily_activity = db.session.query(
            func.date(UserAnswer.answered_at).label('date'),
            func.count(UserAnswer.id).label('questions')
        ).filter(
            UserAnswer.user_id == current_user.id,
            func.date(UserAnswer.answered_at) >= start_date
        ).group_by(func.date(UserAnswer.answered_at)).all()
        
        # Criar mapa de atividade
        activity_map = {day.date: day.questions for day in daily_activity}
        
        # Gerar dados para os últimos 30 dias
        streak_data = []
        current_date = start_date
        
        while current_date <= date.today():
            questions_count = activity_map.get(current_date, 0)
            streak_data.append({
                'date': current_date.isoformat(),
                'questions_answered': questions_count,
                'goal_met': questions_count >= current_user.daily_goal
            })
            current_date += timedelta(days=1)
        
        # Calcular estatísticas da sequência
        consecutive_days = 0
        for day in reversed(streak_data):
            if day['goal_met']:
                consecutive_days += 1
            else:
                break
        
        days_with_activity = sum(1 for day in streak_data if day['questions_answered'] > 0)
        
        return jsonify({
            'current_streak': current_user.streak,
            'consecutive_goal_days': consecutive_days,
            'days_with_activity': days_with_activity,
            'daily_goal': current_user.daily_goal,
            'streak_calendar': streak_data
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to get study streak: {str(e)}'}), 500

@progress_bp.route('/summary', methods=['GET'])
@token_required
def get_progress_summary(current_user):
    """Obter resumo geral do progresso"""
    try:
        # Estatísticas gerais
        total_questions = UserAnswer.query.filter_by(user_id=current_user.id).count()
        correct_answers = UserAnswer.query.filter_by(user_id=current_user.id, is_correct=True).count()
        
        # Tempo total de estudo
        total_time = db.session.query(
            func.sum(UserAnswer.time_spent)
        ).filter_by(user_id=current_user.id).scalar() or 0
        
        # Sessões completadas
        completed_sessions = StudySession.query.filter(
            StudySession.user_id == current_user.id,
            StudySession.completed_at.isnot(None)
        ).count()
        
        # Flashcards revisados
        flashcards_reviewed = FlashcardReview.query.filter_by(user_id=current_user.id).count()
        
        # Conquistas desbloqueadas
        achievements_unlocked = UserAchievement.query.filter_by(user_id=current_user.id).count()
        
        # Progresso por especialidade
        specialty_progress = UserProgress.query.filter_by(user_id=current_user.id).all()
        
        return jsonify({
            'overall_stats': {
                'total_questions_answered': total_questions,
                'correct_answers': correct_answers,
                'accuracy_rate': round((correct_answers / total_questions * 100) if total_questions > 0 else 0, 2),
                'total_study_time_hours': round(total_time / 3600, 2),
                'completed_sessions': completed_sessions,
                'flashcards_reviewed': flashcards_reviewed,
                'achievements_unlocked': achievements_unlocked,
                'current_level': current_user.level,
                'total_xp': current_user.xp,
                'study_streak': current_user.streak
            },
            'specialty_breakdown': [progress.to_dict() for progress in specialty_progress]
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to get progress summary: {str(e)}'}), 500

