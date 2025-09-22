from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import db
from src.models.flashcard import Flashcard, FlashcardReview
from src.services.spaced_repetition import SpacedRepetitionService
from datetime import datetime

flashcards_bp = Blueprint('flashcards', __name__)

@flashcards_bp.route('/flashcards/generate', methods=['POST'])
@jwt_required()
def generate_flashcards():
    """Gera flashcards automaticamente a partir de questões incorretas"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        limit = data.get('limit', 50)
        
        spaced_rep = SpacedRepetitionService(user_id)
        cards_created, error = spaced_rep.generate_flashcards_from_questions(limit)
        
        if error:
            return jsonify({'message': error}), 400
        
        return jsonify({
            'flashcards_created': cards_created,
            'message': f'{cards_created} flashcards foram criados automaticamente'
        })
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@flashcards_bp.route('/flashcards/due', methods=['GET'])
@jwt_required()
def get_due_flashcards():
    """Retorna flashcards prontos para revisão"""
    try:
        user_id = get_jwt_identity()
        limit = int(request.args.get('limit', 20))
        
        spaced_rep = SpacedRepetitionService(user_id)
        flashcards, error = spaced_rep.get_due_flashcards(limit)
        
        if error:
            return jsonify({'message': error}), 400
        
        return jsonify({
            'flashcards': [card.to_dict() for card in flashcards],
            'total_due': len(flashcards)
        })
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@flashcards_bp.route('/flashcards/<int:flashcard_id>/review', methods=['POST'])
@jwt_required()
def review_flashcard(flashcard_id):
    """Processa a revisão de um flashcard"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        quality_rating = data.get('quality_rating')
        
        if quality_rating is None or not (0 <= quality_rating <= 5):
            return jsonify({'message': 'quality_rating deve ser um número entre 0 e 5'}), 400
        
        spaced_rep = SpacedRepetitionService(user_id)
        result, error = spaced_rep.review_flashcard(flashcard_id, quality_rating)
        
        if error:
            return jsonify({'message': error}), 400
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@flashcards_bp.route('/flashcards/stats', methods=['GET'])
@jwt_required()
def get_flashcard_stats():
    """Retorna estatísticas dos flashcards"""
    try:
        user_id = get_jwt_identity()
        
        spaced_rep = SpacedRepetitionService(user_id)
        stats, error = spaced_rep.get_flashcard_stats()
        
        if error:
            return jsonify({'message': error}), 400
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@flashcards_bp.route('/flashcards/forecast', methods=['GET'])
@jwt_required()
def get_study_forecast():
    """Retorna previsão de flashcards para os próximos dias"""
    try:
        user_id = get_jwt_identity()
        days = int(request.args.get('days', 7))
        
        spaced_rep = SpacedRepetitionService(user_id)
        forecast, error = spaced_rep.get_study_forecast(days)
        
        if error:
            return jsonify({'message': error}), 400
        
        return jsonify({
            'forecast': forecast,
            'days': days
        })
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@flashcards_bp.route('/flashcards/create', methods=['POST'])
@jwt_required()
def create_custom_flashcard():
    """Cria um flashcard personalizado"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        front_text = data.get('front_text')
        back_text = data.get('back_text')
        specialty = data.get('specialty')
        difficulty = data.get('difficulty', 'medium')
        
        if not front_text or not back_text or not specialty:
            return jsonify({'message': 'front_text, back_text e specialty são obrigatórios'}), 400
        
        spaced_rep = SpacedRepetitionService(user_id)
        flashcard, error = spaced_rep.create_custom_flashcard(
            front_text, back_text, specialty, difficulty
        )
        
        if error:
            return jsonify({'message': error}), 400
        
        return jsonify({
            'flashcard': flashcard,
            'message': 'Flashcard criado com sucesso'
        })
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@flashcards_bp.route('/flashcards/retention-rate', methods=['GET'])
@jwt_required()
def get_retention_rate():
    """Retorna taxa de retenção dos flashcards"""
    try:
        user_id = get_jwt_identity()
        days = int(request.args.get('days', 30))
        
        spaced_rep = SpacedRepetitionService(user_id)
        retention_rate, error = spaced_rep.get_retention_rate(days)
        
        if error:
            return jsonify({'message': error}), 400
        
        return jsonify({
            'retention_rate': retention_rate,
            'period_days': days,
            'interpretation': {
                'excellent': retention_rate >= 90,
                'good': 80 <= retention_rate < 90,
                'fair': 70 <= retention_rate < 80,
                'needs_improvement': retention_rate < 70
            }
        })
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@flashcards_bp.route('/flashcards/optimize-session', methods=['GET'])
@jwt_required()
def optimize_study_session():
    """Otimiza uma sessão de estudo baseada no tempo disponível"""
    try:
        user_id = get_jwt_identity()
        available_time = int(request.args.get('time_minutes', 15))
        
        spaced_rep = SpacedRepetitionService(user_id)
        flashcards, error = spaced_rep.optimize_study_session(available_time)
        
        if error:
            return jsonify({'message': error}), 400
        
        return jsonify({
            'recommended_flashcards': [card.to_dict() for card in flashcards],
            'estimated_time_minutes': len(flashcards) * 0.5,
            'available_time_minutes': available_time,
            'optimization_note': f'Selecionados {len(flashcards)} flashcards para {available_time} minutos'
        })
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@flashcards_bp.route('/flashcards/all', methods=['GET'])
@jwt_required()
def get_all_flashcards():
    """Retorna todos os flashcards do usuário"""
    try:
        user_id = get_jwt_identity()
        specialty = request.args.get('specialty')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        query = Flashcard.query.filter_by(user_id=user_id, is_active=True)
        
        if specialty:
            query = query.filter_by(specialty=specialty)
        
        flashcards = query.order_by(Flashcard.next_review_date.asc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'flashcards': [card.to_dict() for card in flashcards.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': flashcards.total,
                'pages': flashcards.pages,
                'has_next': flashcards.has_next,
                'has_prev': flashcards.has_prev
            }
        })
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@flashcards_bp.route('/flashcards/<int:flashcard_id>', methods=['DELETE'])
@jwt_required()
def delete_flashcard(flashcard_id):
    """Desativa um flashcard"""
    try:
        user_id = get_jwt_identity()
        
        flashcard = Flashcard.query.filter_by(
            id=flashcard_id,
            user_id=user_id
        ).first()
        
        if not flashcard:
            return jsonify({'message': 'Flashcard não encontrado'}), 404
        
        flashcard.is_active = False
        db.session.commit()
        
        return jsonify({'message': 'Flashcard removido com sucesso'})
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@flashcards_bp.route('/flashcards/<int:flashcard_id>/edit', methods=['PUT'])
@jwt_required()
def edit_flashcard(flashcard_id):
    """Edita um flashcard personalizado"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        flashcard = Flashcard.query.filter_by(
            id=flashcard_id,
            user_id=user_id,
            is_custom=True
        ).first()
        
        if not flashcard:
            return jsonify({'message': 'Flashcard não encontrado ou não é editável'}), 404
        
        # Atualizar campos permitidos
        if 'front_text' in data:
            flashcard.front_text = data['front_text']
        if 'back_text' in data:
            flashcard.back_text = data['back_text']
        if 'specialty' in data:
            flashcard.specialty = data['specialty']
        if 'difficulty' in data:
            flashcard.difficulty = data['difficulty']
        
        flashcard.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'flashcard': flashcard.to_dict(),
            'message': 'Flashcard atualizado com sucesso'
        })
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

