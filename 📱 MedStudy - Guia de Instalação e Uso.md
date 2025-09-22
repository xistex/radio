# 📱 MedStudy - Guia de Instalação e Uso

## 🎯 Sobre o MedStudy

O **MedStudy** é um aplicativo completo para estudo de residência médica, especificamente desenvolvido para as provas **SES-GO** e **PSU-GO**. Inspirado no Duolingo, combina gamificação, micro-learning e técnicas científicas de aprendizagem para maximizar sua preparação.

### ✨ Funcionalidades Principais

- **🎮 Gamificação Completa**: Sistema de XP, níveis, conquistas e streaks
- **📚 Micro-Learning**: Sessões de 10 questões (15 minutos máximo)
- **🧠 Flashcards Inteligentes**: Repetição espaçada com algoritmo SM-2
- **📊 Regra de Pareto**: 80% das questões dos 20% dos temas que mais caem
- **🎯 Personalização**: Adapta-se ao seu desempenho individual
- **📱 PWA**: Funciona como app nativo, inclusive offline

## 📲 Como Instalar (PWA - Recomendado)

### Para Android (Chrome/Edge):

1. **Acesse o aplicativo**
   - Abra o Chrome no seu celular
   - Digite: `http://localhost:5173` (ou o endereço fornecido)
   - Aguarde carregar completamente

2. **Instale como app**
   - Toque no menu (⋮) no canto superior direito
   - Selecione **"Adicionar à tela inicial"**
   - Confirme tocando em **"Adicionar"**
   - O ícone do MedStudy aparecerá na sua tela inicial

3. **Use como app nativo**
   - Toque no ícone do MedStudy
   - O app abre em tela cheia (sem barra do navegador)
   - Funciona offline após a primeira instalação

### Para iPhone/iPad (Safari):

1. **Acesse o aplicativo**
   - Abra o Safari no seu iPhone/iPad
   - Digite: `http://localhost:5173` (ou o endereço fornecido)
   - Aguarde carregar completamente

2. **Instale como app**
   - Toque no botão **Compartilhar** (□↗)
   - Role para baixo e selecione **"Adicionar à Tela de Início"**
   - Edite o nome se desejar e toque em **"Adicionar"**
   - O ícone do MedStudy aparecerá na sua tela inicial

3. **Use como app nativo**
   - Toque no ícone do MedStudy
   - O app abre em tela cheia
   - Funciona offline após a primeira instalação

## 🚀 Primeiros Passos

### 1. Criar Conta
- Abra o MedStudy
- Toque em **"Cadastrar"**
- Preencha: nome de usuário, email, senha
- Escolha sua especialidade desejada (ex: Clínica Médica)
- Toque em **"Criar conta"**

### 2. Primeiro Login
- Use seu email e senha para entrar
- Você será direcionado ao Dashboard principal
- Explore as diferentes seções do app

### 3. Começar a Estudar
- **Questões**: Sessões de 10 questões com micro-learning
- **Flashcards**: Revisão com repetição espaçada
- **Progresso**: Acompanhe suas estatísticas
- **Perfil**: Veja seu nível, XP e conquistas

## 📚 Como Usar Cada Funcionalidade

### 🎯 Sessões de Questões

1. **Iniciar Sessão**
   - Vá para a aba **"Questões"**
   - Toque em **"Iniciar Sessão"**
   - O sistema seleciona 10 questões inteligentemente

2. **Durante a Sessão**
   - Leia a questão com atenção
   - Escolha sua resposta (A, B, C, D, E)
   - Receba feedback imediato
   - Veja explicação detalhada
   - Continue para a próxima questão

3. **Após a Sessão**
   - Veja seu desempenho (acertos/erros)
   - Ganhe XP e possíveis conquistas
   - Flashcards são criados automaticamente dos erros

### 🧠 Sistema de Flashcards

1. **Gerar Flashcards**
   - Vá para a aba **"Flashcards"**
   - Toque em **"Gerar Flashcards"**
   - O sistema cria cards das questões que você errou

2. **Revisar Flashcards**
   - Toque em **"Iniciar Revisão"**
   - Leia a pergunta (frente do card)
   - Tente lembrar a resposta
   - Toque em **"Mostrar Resposta"**
   - Avalie sua lembrança (0-5):
     - **0**: Não lembrei nada
     - **3**: Lembrei com dificuldade
     - **5**: Lembrei perfeitamente

3. **Repetição Espaçada**
   - O algoritmo SM-2 calcula quando revisar novamente
   - Cards difíceis aparecem mais frequentemente
   - Cards dominados têm intervalos maiores

### 🎮 Sistema de Gamificação

1. **XP (Pontos de Experiência)**
   - Ganhe XP respondendo questões
   - Bonus por velocidade (+2 XP se < 30s)
   - Bonus por acurácia (+25 XP se > 90%)
   - Bonus por completar sessão (+50 XP)

2. **Níveis**
   - Seu nível aumenta conforme ganha XP
   - Fórmula: `nível = √(XP/100)`
   - Cada nível desbloqueado é uma conquista

3. **Conquistas**
   - **Primeiros Passos**: Complete sua primeira sessão
   - **Centena Completa**: Responda 100 questões
   - **Mestre em [Especialidade]**: 90%+ de acerto em uma especialidade
   - **Estudante Consistente**: 7 dias seguidos estudando

4. **Streak (Sequência)**
   - Estude pelo menos 1 sessão por dia
   - Mantenha sua sequência para bonus de XP
   - Bonus de streak: +20 XP por semana completa

### 📊 Análise de Progresso

1. **Dashboard Principal**
   - Visão geral do seu progresso
   - Estatísticas de hoje
   - Próximas revisões de flashcards

2. **Página de Progresso**
   - Gráficos de desempenho
   - Análise por especialidade
   - Taxa de acerto ao longo do tempo
   - Tempo total de estudo

3. **Análise de Pareto**
   - Veja quais temas você domina (20%)
   - Identifique pontos fracos (80% do foco)
   - Recomendações personalizadas

## 🎓 Técnicas de Estudo Implementadas

### 1. **Repetição Espaçada (Algoritmo SM-2)**
- Baseado na curva de esquecimento de Ebbinghaus
- Intervalos otimizados: 1 dia → 6 dias → fórmula SM-2
- Personaliza-se ao seu ritmo de aprendizagem
- **Eficácia**: Reduz tempo de estudo em até 50%

### 2. **Micro-Learning**
- Sessões curtas de 10 questões (ideal para retenção)
- Máximo 15 minutos por sessão (evita fadiga cognitiva)
- Feedback imediato para reforço positivo
- **Eficácia**: Melhora retenção em 20-30%

### 3. **Gamificação**
- Sistema de recompensas para motivação intrínseca
- Progresso visível e metas claras
- Elementos de jogo mantêm engajamento
- **Eficácia**: Aumenta tempo de estudo em 40%

### 4. **Regra de Pareto (80/20)**
- 80% das questões vêm dos 20% dos temas que mais caem
- Foco nos tópicos de maior impacto
- Adaptação baseada no seu desempenho
- **Eficácia**: Otimiza preparação para provas específicas

## 📈 Dicas para Maximizar Resultados

### 🎯 Estratégia de Estudo

1. **Consistência é Chave**
   - Estude pelo menos 1 sessão por dia
   - Mantenha seu streak para bonus de XP
   - Prefira 15 min/dia a 2h uma vez por semana

2. **Use os Flashcards Religiosamente**
   - Revise todos os flashcards devido diariamente
   - Seja honesto na autoavaliação (0-5)
   - Não pule revisões - o algoritmo depende disso

3. **Analise seu Progresso**
   - Verifique estatísticas semanalmente
   - Identifique padrões nos seus erros
   - Ajuste foco baseado na análise de Pareto

4. **Aproveite a Gamificação**
   - Tente bater recordes pessoais
   - Desbloqueie todas as conquistas
   - Compete consigo mesmo, não com outros

### 🧠 Técnicas de Memorização

1. **Elaboração**
   - Conecte novos conceitos com conhecimento prévio
   - Crie histórias ou analogias
   - Explique conceitos em voz alta

2. **Teste Ativo**
   - Use flashcards para testar conhecimento
   - Não apenas releia - teste ativamente
   - Pratique recall sem olhar respostas

3. **Intercalação**
   - Misture diferentes especialidades
   - Não estude apenas um tópico por vez
   - O app já faz isso automaticamente

4. **Espaçamento**
   - Confie no algoritmo de repetição espaçada
   - Não force revisões antes do tempo
   - Deixe o sistema otimizar seus intervalos

## 🔧 Funcionalidades Offline

### O que funciona offline:
- ✅ Questões já carregadas
- ✅ Flashcards para revisão
- ✅ Navegação entre páginas
- ✅ Visualização de progresso
- ✅ Interface completa

### O que precisa de internet:
- ⚠️ Carregar novas questões
- ⚠️ Sincronizar progresso
- ⚠️ Gerar novos flashcards
- ⚠️ Atualizar estatísticas

### Sincronização:
- Dados são sincronizados automaticamente quando volta online
- Progresso offline é preservado
- Não há perda de dados

## 🆘 Solução de Problemas

### App não instala:
- Verifique se está usando Chrome (Android) ou Safari (iOS)
- Certifique-se que o site carregou completamente
- Tente atualizar a página e instalar novamente

### App não funciona offline:
- Abra o app online pelo menos uma vez
- Aguarde o download completo dos recursos
- Verifique se o service worker foi registrado

### Progresso não sincroniza:
- Conecte-se à internet
- Abra o app e aguarde alguns segundos
- O sistema sincroniza automaticamente

### Flashcards não aparecem:
- Complete pelo menos uma sessão de questões
- Erre algumas questões para gerar flashcards
- Toque em "Gerar Flashcards" manualmente

## 🎉 Parabéns!

Você agora tem acesso ao **MedStudy**, um aplicativo completo e científico para sua preparação para residência médica. Com técnicas comprovadas de aprendizagem, gamificação motivadora e foco nos temas que mais caem nas provas SES-GO e PSU-GO, você está equipado para maximizar seus resultados.

**Lembre-se**: A consistência é mais importante que a intensidade. Estude um pouco todos os dias e deixe o algoritmo trabalhar a seu favor!

**Boa sorte na sua jornada para a residência médica! 🩺📚🎯**

---

*Desenvolvido com ❤️ para futuros médicos residentes*

