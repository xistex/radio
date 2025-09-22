import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.user import db
from src.models.question import Question, UserAnswer, StudySession
from src.models.flashcard import Flashcard, FlashcardReview, UserFlashcardProgress
from src.models.achievement import Achievement, UserAchievement, UserProgress, Leaderboard
from src.models.priority import TopicFrequency, UserTopicPriority, QuestionSelectionLog

# Importar rotas
from src.routes.user import user_bp
from src.routes.auth import auth_bp
from src.routes.questions import questions_bp
from src.routes.flashcards import flashcards_bp
from src.routes.progress import progress_bp
from src.routes.gamification import gamification_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'medstudy-secret-key-2024'

# Habilitar CORS para todas as rotas
CORS(app, origins="*")

# Registrar blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(user_bp, url_prefix='/api/users')
app.register_blueprint(questions_bp, url_prefix='/api/questions')
app.register_blueprint(flashcards_bp, url_prefix='/api/flashcards')
app.register_blueprint(progress_bp, url_prefix='/api/progress')
app.register_blueprint(gamification_bp, url_prefix='/api')

# Configuração do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Criar todas as tabelas
with app.app_context():
    db.create_all()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

@app.route('/api/health')
def health_check():
    return {'status': 'ok', 'message': 'MedStudy API is running'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
