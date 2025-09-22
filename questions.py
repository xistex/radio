from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import db
from src.models.question import Question, UserAnswer
from src.models.study_session import StudySession
from src.models.priority import initialize_topic_frequencies
from src.services.question_selector import IntelligentQuestionSelector
from datetime import datetime
import random

questions_bp = Blueprint('questions', __name__)

@questions_bp.route('/questions/session', methods=['POST'])
@jwt_required()
def start_question_session():
    """Inicia uma nova sessão de questões com seleção inteligente"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        specialty = data.get('specialty')
        difficulty = data.get('difficulty')
        question_count = data.get('question_count', 10)
        use_intelligent_selection = data.get('use_intelligent_selection', True)
        
        # Inicializar frequências de tópicos se necessário
        initialize_topic_frequencies()
        
        if use_intelligent_selection:
            # Usar seleção inteligente baseada em Pareto + desempenho
            selector = IntelligentQuestionSelector(user_id)
            questions = selector.select_questions(
                limit=question_count,
                specialty=specialty,
                difficulty=difficulty
            )
        else:
            # Seleção tradicional aleatória
            query = Question.query
            
            if specialty:
                query = query.filter(Question.specialty == specialty)
            
            if difficulty:
                query = query.filter(Question.difficulty == difficulty)
            
            # Excluir questões já respondidas pelo usuário
            answered_questions = db.session.query(UserAnswer.question_id).filter_by(user_id=user_id)
            query = query.filter(~Question.id.in_(answered_questions))
            
            questions = query.order_by(db.func.random()).limit(question_count).all()
        
        if not questions:
            return jsonify({'message': 'Nenhuma questão encontrada'}), 404
        
        # Criar sessão de estudo
        session = StudySession(
            user_id=user_id,
            session_type='questions',
            total_questions=len(questions),
            questions_data=[q.id for q in questions]
        )
        db.session.add(session)
        db.session.commit()
        
        # Atualizar selector com session_id se usando seleção inteligente
        if use_intelligent_selection:
            selector = IntelligentQuestionSelector(user_id)
            selector._log_selections(questions, session.id)
        
        return jsonify({
            'session_id': session.id,
            'questions': [q.to_dict() for q in questions],
            'total_questions': len(questions),
            'selection_method': 'intelligent' if use_intelligent_selection else 'random'
        })
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@questions_bp.route('/questions/<int:question_id>/answer', methods=['POST'])
@jwt_required()
def answer_question():
    """Responde uma questão e atualiza sistema de priorização"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        selected_option = data.get('selected_option')
        session_id = data.get('session_id')
        response_time = data.get('response_time')
        
        question = Question.query.get(question_id)
        if not question:
            return jsonify({'message': 'Questão não encontrada'}), 404
        
        # Verificar se já foi respondida
        existing_answer = UserAnswer.query.filter_by(
            user_id=user_id,
            question_id=question_id
        ).first()
        
        is_correct = selected_option == question.correct_option
        
        if existing_answer:
            # Atualizar resposta existente
            existing_answer.selected_option = selected_option
            existing_answer.is_correct = is_correct
            existing_answer.response_time = response_time
            existing_answer.answered_at = datetime.utcnow()
        else:
            # Criar nova resposta
            answer = UserAnswer(
                user_id=user_id,
                question_id=question_id,
                selected_option=selected_option,
                is_correct=is_correct,
                response_time=response_time,
                session_id=session_id
            )
            db.session.add(answer)
        
        # Atualizar sistema de priorização inteligente
        selector = IntelligentQuestionSelector(user_id)
        selector.update_user_performance(question_id, is_correct, response_time)
        
        db.session.commit()
        
        return jsonify({
            'is_correct': is_correct,
            'correct_option': question.correct_option,
            'explanation': question.explanation,
            'specialty': question.specialty
        })
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@questions_bp.route('/questions/stats', methods=['GET'])
@jwt_required()
def get_question_stats():
    """Retorna estatísticas de questões do usuário"""
    try:
        user_id = get_jwt_identity()
        
        # Estatísticas gerais
        total_answered = UserAnswer.query.filter_by(user_id=user_id).count()
        correct_answers = UserAnswer.query.filter_by(user_id=user_id, is_correct=True).count()
        
        accuracy_rate = (correct_answers / total_answered * 100) if total_answered > 0 else 0
        
        # Estatísticas por especialidade
        specialty_stats = db.session.query(
            Question.specialty,
            db.func.count(UserAnswer.id).label('total'),
            db.func.sum(db.case([(UserAnswer.is_correct == True, 1)], else_=0)).label('correct')
        ).join(UserAnswer).filter(UserAnswer.user_id == user_id).group_by(Question.specialty).all()
        
        specialty_data = []
        for stat in specialty_stats:
            specialty_accuracy = (stat.correct / stat.total * 100) if stat.total > 0 else 0
            specialty_data.append({
                'specialty': stat.specialty,
                'total_questions': stat.total,
                'correct_answers': stat.correct,
                'accuracy_rate': round(specialty_accuracy, 2)
            })
        
        return jsonify({
            'total_answered': total_answered,
            'correct_answers': correct_answers,
            'accuracy_rate': round(accuracy_rate, 2),
            'specialty_stats': specialty_data
        })
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@questions_bp.route('/questions/priorities', methods=['GET'])
@jwt_required()
def get_user_priorities():
    """Retorna prioridades personalizadas do usuário"""
    try:
        user_id = get_jwt_identity()
        
        selector = IntelligentQuestionSelector(user_id)
        priorities_summary = selector.get_user_priorities_summary()
        
        return jsonify(priorities_summary)
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@questions_bp.route('/questions/pareto-analysis', methods=['GET'])
@jwt_required()
def get_pareto_analysis():
    """Retorna análise dos temas baseada na regra de Pareto"""
    try:
        user_id = get_jwt_identity()
        
        selector = IntelligentQuestionSelector(user_id)
        pareto_analysis = selector.get_pareto_analysis()
        
        return jsonify(pareto_analysis)
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@questions_bp.route('/questions/next-recommendation', methods=['GET'])
@jwt_required()
def get_next_recommendation():
    """Retorna recomendação do próximo tópico para estudar"""
    try:
        user_id = get_jwt_identity()
        
        selector = IntelligentQuestionSelector(user_id)
        
        # Simular seleção de uma questão para ver qual tópico seria escolhido
        questions = selector.select_questions(limit=1)
        
        if questions:
            question = questions[0]
            priorities_summary = selector.get_user_priorities_summary()
            
            # Encontrar prioridade do tópico recomendado
            topic_priority = None
            for priority in priorities_summary['priorities']:
                if priority['specialty'] == question.specialty:
                    topic_priority = priority
                    break
            
            return jsonify({
                'recommended_topic': question.specialty,
                'reason': 'Baseado na regra de Pareto e seu desempenho individual',
                'topic_priority': topic_priority,
                'sample_question': question.to_dict()
            })
        else:
            return jsonify({
                'message': 'Nenhuma recomendação disponível no momento'
            }), 404
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@questions_bp.route('/questions/specialties', methods=['GET'])
def get_specialties():
    """Retorna lista de especialidades disponíveis"""
    try:
        specialties = db.session.query(Question.specialty).distinct().all()
        specialty_list = [s[0] for s in specialties if s[0]]
        
        return jsonify({
            'specialties': specialty_list
        })
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

