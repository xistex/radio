# Design da Arquitetura e Funcionalidades do Aplicativo de Residência Médica

## Visão Geral do Aplicativo

O aplicativo "MedStudy" será uma plataforma de estudo gamificada para residência médica, especificamente focada nas provas SES-GO e PSU-GO. Inspirado no Duolingo, o app combinará micro-learning, gamificação, repetição espaçada e um vasto banco de questões de provas anteriores.

## Arquitetura Técnica

### Frontend (React Native)
- **Framework:** React Native para desenvolvimento multiplataforma (Android/iOS)
- **Navegação:** React Navigation para navegação entre telas
- **Estado Global:** Redux Toolkit para gerenciamento de estado
- **UI Components:** React Native Elements + componentes customizados
- **Animações:** React Native Reanimated para animações fluidas
- **Armazenamento Local:** AsyncStorage para dados offline

### Backend (Node.js + Express)
- **Framework:** Express.js com TypeScript
- **Banco de Dados:** PostgreSQL para dados estruturados
- **ORM:** Prisma para modelagem e queries do banco
- **Autenticação:** JWT (JSON Web Tokens)
- **Cache:** Redis para cache de sessões e dados frequentes
- **API:** RESTful API com documentação Swagger

### Infraestrutura
- **Hospedagem:** Heroku ou AWS para o backend
- **Banco de Dados:** PostgreSQL hospedado (Heroku Postgres ou AWS RDS)
- **CDN:** Cloudflare para entrega de conteúdo estático
- **Monitoramento:** Sentry para tracking de erros

## Funcionalidades Principais

### 1. Sistema de Autenticação e Perfil
- **Cadastro/Login:** Email, Google, Facebook
- **Perfil do Usuário:** Foto, nome, especialidade desejada, meta de estudo
- **Configurações:** Notificações, horários de estudo, preferências

### 2. Dashboard Principal
- **Progresso Diário:** Streak de dias consecutivos estudando
- **Estatísticas:** Questões respondidas, acertos, tempo de estudo
- **Metas:** Objetivos diários/semanais personalizáveis
- **Ranking:** Posição entre amigos e usuários globais

### 3. Sistema de Questões (Micro-learning)
- **Sessões de 10 Questões:** Duração de 10-15 minutos
- **Filtros Inteligentes:** Por especialidade, dificuldade, ano da prova
- **Feedback Imediato:** Explicação detalhada após cada resposta
- **Modo Prova:** Simulados completos das provas SES-GO e PSU-GO
- **Revisão de Erros:** Sistema para revisar questões erradas

### 4. Sistema de Flashcards
- **Criação Automática:** Flashcards gerados a partir das questões
- **Repetição Espaçada:** Algoritmo baseado no método Anki
- **Categorização:** Por especialidade e nível de dificuldade
- **Modo Offline:** Acesso aos flashcards sem internet

### 5. Gamificação
- **Sistema de XP:** Pontos por questões corretas e sessões completas
- **Níveis:** Progressão de "Estudante" a "Residente Expert"
- **Conquistas:** Badges por marcos específicos (100 questões, 7 dias seguidos, etc.)
- **Ligas:** Competição semanal entre usuários
- **Recompensas:** Desbloqueio de conteúdo premium e avatares

### 6. Análise de Performance
- **Relatórios Detalhados:** Performance por especialidade
- **Gráficos de Progresso:** Evolução temporal do desempenho
- **Pontos Fracos:** Identificação de áreas que precisam de mais estudo
- **Recomendações:** Sugestões personalizadas de estudo

### 7. Modo Offline
- **Download de Conteúdo:** Questões e flashcards para estudo offline
- **Sincronização:** Upload automático quando conectado
- **Cache Inteligente:** Priorização de conteúdo mais relevante

## Interface do Usuário (UI/UX)

### Design System
- **Cores Primárias:** Azul médico (#2E86AB), Verde sucesso (#A8E6CF), Vermelho erro (#FF6B6B)
- **Tipografia:** Inter (títulos) e Open Sans (corpo do texto)
- **Iconografia:** Feather Icons + ícones médicos customizados
- **Componentes:** Design consistente inspirado no Material Design

### Telas Principais

#### 1. Tela de Login/Cadastro
- Design minimalista com logo do app
- Opções de login social (Google, Facebook)
- Formulário de cadastro com validação em tempo real

#### 2. Dashboard/Home
- Card de progresso diário com streak
- Botão principal "Iniciar Sessão de Estudo"
- Estatísticas rápidas (XP, nível, questões respondidas)
- Acesso rápido a flashcards e simulados

#### 3. Tela de Questões
- Interface limpa focada na questão
- Barra de progresso da sessão
- Botões de resposta com feedback visual
- Timer opcional para pressão de tempo real

#### 4. Tela de Flashcards
- Design de cartão com flip animation
- Botões de dificuldade (Fácil, Médio, Difícil)
- Contador de cards restantes
- Modo de revisão espaçada

#### 5. Tela de Estatísticas
- Gráficos interativos de performance
- Filtros por período e especialidade
- Comparação com outros usuários
- Recomendações de estudo

#### 6. Tela de Perfil
- Avatar personalizável
- Conquistas e badges
- Configurações de notificação
- Histórico de atividades

## Banco de Dados

### Principais Entidades

#### Users
- id, email, name, avatar, level, xp, streak
- created_at, updated_at, last_login
- study_preferences (JSON)

#### Questions
- id, content, options (JSON), correct_answer
- explanation, difficulty, specialty, exam_year
- source_exam (SES-GO, PSU-GO), created_at

#### UserAnswers
- id, user_id, question_id, selected_answer
- is_correct, answered_at, time_spent

#### Flashcards
- id, front_content, back_content, difficulty
- next_review_date, review_count, specialty

#### UserProgress
- id, user_id, specialty, correct_answers
- total_answers, accuracy_rate, last_studied

#### Achievements
- id, name, description, icon, criteria
- xp_reward, unlock_condition

## Algoritmos Principais

### 1. Repetição Espaçada (Flashcards)
```
Intervalo inicial: 1 dia
Se acertou: próximo_intervalo = intervalo_atual * 2.5
Se errou: próximo_intervalo = 1 dia
Máximo: 30 dias
```

### 2. Seleção Inteligente de Questões
- 70% questões não respondidas
- 20% questões erradas para revisão
- 10% questões acertadas para reforço

### 3. Sistema de XP e Níveis
- Questão correta: +10 XP
- Sessão completa: +50 XP bonus
- Streak diário: +20 XP
- Níveis: 100 XP * nível atual

### 4. Recomendação de Estudo
- Análise de performance por especialidade
- Identificação de pontos fracos
- Sugestão de tempo de estudo por área

## Funcionalidades Avançadas

### 1. Modo Competitivo
- Duelos entre amigos
- Torneios semanais
- Ranking global e por região

### 2. Estudo em Grupo
- Criação de grupos de estudo
- Compartilhamento de progresso
- Desafios em grupo

### 3. Análise Preditiva
- Estimativa de probabilidade de aprovação
- Recomendações baseadas em IA
- Identificação de padrões de estudo

### 4. Integração com Calendário
- Agendamento de sessões de estudo
- Lembretes inteligentes
- Sincronização com calendários externos

## Monetização

### Modelo Freemium
- **Gratuito:** 5 questões por dia, flashcards básicos
- **Premium:** Questões ilimitadas, análises avançadas, modo offline completo
- **Preço:** R$ 29,90/mês ou R$ 299,90/ano

### Funcionalidades Premium
- Acesso ilimitado a questões
- Simulados completos
- Análises detalhadas de performance
- Modo offline completo
- Suporte prioritário
- Conteúdo exclusivo

## Cronograma de Desenvolvimento

### Fase 1 (4 semanas): MVP
- Sistema de autenticação
- Banco básico de questões
- Interface principal
- Sistema de XP básico

### Fase 2 (3 semanas): Gamificação
- Sistema completo de níveis e conquistas
- Flashcards com repetição espaçada
- Análises de performance

### Fase 3 (3 semanas): Funcionalidades Avançadas
- Modo offline
- Sistema de recomendações
- Otimizações de performance

### Fase 4 (2 semanas): Polimento e Testes
- Testes de usabilidade
- Correção de bugs
- Preparação para lançamento

## Considerações de Segurança

### Proteção de Dados
- Criptografia de senhas (bcrypt)
- HTTPS obrigatório
- Validação de entrada em todas as APIs
- Rate limiting para prevenir abuso

### Privacidade
- Conformidade com LGPD
- Política de privacidade clara
- Opção de exclusão de dados
- Anonimização de dados analíticos

## Métricas de Sucesso

### Engajamento
- Tempo médio de sessão: >15 minutos
- Retenção D7: >40%
- Retenção D30: >20%
- Sessões por usuário/semana: >3

### Aprendizado
- Taxa de acerto média: >70%
- Melhoria de performance ao longo do tempo
- Feedback positivo dos usuários
- Taxa de aprovação em residências

Este design combina as melhores práticas de gamificação, micro-learning e repetição espaçada para criar uma experiência de estudo envolvente e eficaz para candidatos à residência médica.

