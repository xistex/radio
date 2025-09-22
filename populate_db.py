#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.models.user import db
from src.models.question import Question
from src.models.flashcard import Flashcard
from src.models.achievement import Achievement
from src.main import app

def populate_database():
    """Popular o banco de dados com dados de exemplo"""
    
    with app.app_context():
        # Criar questões de exemplo baseadas nas provas reais
        sample_questions = [
            {
                'content': 'Paciente de 38 anos, sexo masculino, com quadro de dor aguda no membro inferior direito iniciada há 2 horas. Nega doenças prévias. Tabagista 30 anos-maço e etilista social. Ao exame físico apresenta frialdade e palidez no membro inferior direito e ausência de pulsos tibiais. Diante do quadro clínico apresentado, qual é o diagnóstico?',
                'options': '{"A": "Trombose venosa profunda do membro inferior direito", "B": "Phlegmasia Alba Dolens", "C": "Doença de Buerger", "D": "Doença de Cockett"}',
                'correct_answer': 'C',
                'explanation': 'A doença de Buerger (tromboangeíte obliterante) é uma vasculite que afeta artérias e veias de pequeno e médio calibre, principalmente em extremidades. É fortemente associada ao tabagismo e apresenta-se com dor, frialdade, palidez e ausência de pulsos.',
                'specialty': 'Cirurgia Geral',
                'difficulty': 'medium',
                'exam_source': 'SES-GO',
                'exam_year': 2024
            },
            {
                'content': 'Na conduta relacionada à hemorragia digestiva alta de etiologia varicosa, é importante:',
                'options': '{"A": "a realização da profilaxia de infecções, considerando os seguintes antibióticos: a cefadroxila, cefazolina e cefoxitina", "B": "o uso da terlipressina, por ser um constritor esplâncnico, é uma das opções medicamentosas", "C": "o uso do balão de Sengstaken – Blackmore, mantido por no máximo 48 horas", "D": "a utilização do TIPS, com o objetivo de embolizar ramos portais, nos casos refratários à terapêutica endoscópica adequada"}',
                'correct_answer': 'B',
                'explanation': 'A terlipressina é um vasoconstritor esplâncnico usado no tratamento da hemorragia digestiva alta por varizes esofágicas, reduzindo o fluxo sanguíneo portal e controlando o sangramento.',
                'specialty': 'Clínica Médica',
                'difficulty': 'medium',
                'exam_source': 'SES-GO',
                'exam_year': 2024
            },
            {
                'content': 'A patologia cirúrgica mais comum relacionada às vias biliares é a colelitíase. Uma complicação temida dela é a coledocolitíase, que pode levar à colangite e que é representada clinicamente pela tríade de Charcot. Os componentes da tríade de Charcot são:',
                'options': '{"A": "dor abdominal difusa, icterícia e leucocitose", "B": "dor abdominal em quadrante superior direito, febre e leucocitose", "C": "dor abdominal em quadrante superior direito, icterícia e febre", "D": "dor abdominal em faixa, leucocitose e icterícia"}',
                'correct_answer': 'C',
                'explanation': 'A tríade de Charcot consiste em: dor abdominal em quadrante superior direito, icterícia e febre. É característica da colangite aguda.',
                'specialty': 'Cirurgia Geral',
                'difficulty': 'easy',
                'exam_source': 'SES-GO',
                'exam_year': 2024
            },
            {
                'content': 'Nos pacientes com infecção por Doença de Chagas, quando evoluem para a fase crônica, qual a forma de apresentação mais comum?',
                'options': '{"A": "Forma cardíaca", "B": "Forma digestiva (esofagopatia ou colopatia)", "C": "Forma mista (cardíaca e digestiva)", "D": "Forma indeterminada (sem evidência de acometimento cardíaco ou digestivo)"}',
                'correct_answer': 'D',
                'explanation': 'A forma indeterminada é a mais comum na fase crônica da doença de Chagas, caracterizada pela ausência de manifestações clínicas, radiológicas ou eletrocardiográficas de acometimento cardíaco ou digestivo.',
                'specialty': 'Clínica Médica',
                'difficulty': 'medium',
                'exam_source': 'SES-GO',
                'exam_year': 2024
            },
            {
                'content': 'Para qual destas situações há indicação CLASSE I de implante de marcapasso definitivo?',
                'options': '{"A": "Doença do nó sinusal em pacientes em uso de amiodarona", "B": "Bloqueio atrioventricular de segundo grau Mobitz I (Wenckebach) durante o sono", "C": "Síncope recorrente, > 40 anos de idade e documentação de pausa sintomática espontânea maior que 6 segundos", "D": "Pacientes com miocardiopatia hipertrófica forma obstrutiva, mesmo com gradiente de via de saída de ventrículo esquerdo baixo"}',
                'correct_answer': 'C',
                'explanation': 'Síncope recorrente com documentação de pausa sintomática > 3 segundos (especialmente > 6 segundos) é indicação Classe I para marcapasso definitivo.',
                'specialty': 'Clínica Médica',
                'difficulty': 'hard',
                'exam_source': 'SES-GO',
                'exam_year': 2024
            }
        ]
        
        # Adicionar questões
        for q_data in sample_questions:
            question = Question(**q_data)
            db.session.add(question)
        
        # Criar flashcards de exemplo
        sample_flashcards = [
            {
                'front_content': 'Tríade de Charcot',
                'back_content': 'Dor abdominal em QSD + Icterícia + Febre\n(Característica da colangite aguda)',
                'specialty': 'Cirurgia Geral',
                'difficulty': 'easy'
            },
            {
                'front_content': 'Doença de Buerger',
                'back_content': 'Tromboangeíte obliterante\n- Vasculite de pequenos vasos\n- Fortemente associada ao tabagismo\n- Dor, frialdade, palidez em extremidades',
                'specialty': 'Cirurgia Geral',
                'difficulty': 'medium'
            },
            {
                'front_content': 'Forma mais comum da Doença de Chagas crônica',
                'back_content': 'Forma INDETERMINADA\n- Sem manifestações clínicas\n- Sem alterações no ECG\n- Sem acometimento digestivo',
                'specialty': 'Clínica Médica',
                'difficulty': 'medium'
            },
            {
                'front_content': 'Terlipressina',
                'back_content': 'Vasoconstritor esplâncnico\n- Usado na hemorragia digestiva alta varicosa\n- Reduz fluxo sanguíneo portal\n- Controla sangramento de varizes',
                'specialty': 'Clínica Médica',
                'difficulty': 'medium'
            }
        ]
        
        # Adicionar flashcards
        for f_data in sample_flashcards:
            flashcard = Flashcard(**f_data)
            db.session.add(flashcard)
        
        # Criar conquistas de exemplo
        sample_achievements = [
            {
                'name': 'Primeiro Passo',
                'description': 'Responda sua primeira questão',
                'icon': 'first_step',
                'category': 'study',
                'criteria_type': 'questions_answered',
                'criteria_value': 1,
                'xp_reward': 50,
                'rarity': 'common'
            },
            {
                'name': 'Estudante Dedicado',
                'description': 'Responda 100 questões',
                'icon': 'dedicated_student',
                'category': 'study',
                'criteria_type': 'questions_answered',
                'criteria_value': 100,
                'xp_reward': 200,
                'rarity': 'rare'
            },
            {
                'name': 'Sequência de Fogo',
                'description': 'Mantenha uma sequência de 7 dias estudando',
                'icon': 'fire_streak',
                'category': 'streak',
                'criteria_type': 'streak',
                'criteria_value': 7,
                'xp_reward': 150,
                'rarity': 'rare'
            },
            {
                'name': 'Mestre da Precisão',
                'description': 'Alcance 90% de acerto',
                'icon': 'precision_master',
                'category': 'accuracy',
                'criteria_type': 'accuracy',
                'criteria_value': 90,
                'xp_reward': 300,
                'rarity': 'epic'
            },
            {
                'name': 'Residente Expert',
                'description': 'Alcance o nível 10',
                'icon': 'expert_resident',
                'category': 'level',
                'criteria_type': 'level',
                'criteria_value': 10,
                'xp_reward': 500,
                'rarity': 'legendary'
            }
        ]
        
        # Adicionar conquistas
        for a_data in sample_achievements:
            achievement = Achievement(**a_data)
            db.session.add(achievement)
        
        # Salvar todas as mudanças
        db.session.commit()
        print("✅ Banco de dados populado com sucesso!")
        print(f"📚 {len(sample_questions)} questões adicionadas")
        print(f"🎴 {len(sample_flashcards)} flashcards adicionados")
        print(f"🏆 {len(sample_achievements)} conquistas adicionadas")

if __name__ == '__main__':
    populate_database()

