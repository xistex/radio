import { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { 
  BookOpen, 
  Clock, 
  Target, 
  CheckCircle, 
  XCircle, 
  Trophy,
  Flame,
  Star,
  ArrowRight,
  RotateCcw
} from 'lucide-react'

const QuestionsPage = () => {
  const { apiCall } = useAuth()
  const [currentSession, setCurrentSession] = useState(null)
  const [questions, setQuestions] = useState([])
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0)
  const [selectedOption, setSelectedOption] = useState('')
  const [showResult, setShowResult] = useState(false)
  const [sessionResult, setSessionResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [sessionCompleted, setSessionCompleted] = useState(false)
  const [startTime, setStartTime] = useState(null)

  const startMicroSession = async () => {
    setLoading(true)
    try {
      const response = await apiCall('/microlearning/session', {
        method: 'POST',
        body: JSON.stringify({
          session_type: 'daily',
          use_intelligent_selection: true
        })
      })

      setCurrentSession(response.session)
      setQuestions(response.questions)
      setCurrentQuestionIndex(0)
      setSelectedOption('')
      setShowResult(false)
      setSessionCompleted(false)
      setStartTime(Date.now())
    } catch (error) {
      console.error('Erro ao iniciar sessão:', error)
    } finally {
      setLoading(false)
    }
  }

  const submitAnswer = async () => {
    if (!selectedOption || !currentSession) return

    const responseTime = Math.floor((Date.now() - startTime) / 1000)

    try {
      const response = await apiCall(`/microlearning/session/${currentSession.id}/answer`, {
        method: 'POST',
        body: JSON.stringify({
          question_id: questions[currentQuestionIndex].id,
          selected_option: selectedOption,
          response_time: responseTime
        })
      })

      setSessionResult(response)
      setShowResult(true)

      if (response.session_completed) {
        setSessionCompleted(true)
      }
    } catch (error) {
      console.error('Erro ao submeter resposta:', error)
    }
  }

  const nextQuestion = () => {
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1)
      setSelectedOption('')
      setShowResult(false)
      setStartTime(Date.now())
    }
  }

  const completeSession = async () => {
    try {
      const response = await apiCall(`/microlearning/session/${currentSession.id}/complete`, {
        method: 'POST'
      })
      
      setSessionResult(response)
      setSessionCompleted(true)
    } catch (error) {
      console.error('Erro ao completar sessão:', error)
    }
  }

  const resetSession = () => {
    setCurrentSession(null)
    setQuestions([])
    setCurrentQuestionIndex(0)
    setSelectedOption('')
    setShowResult(false)
    setSessionResult(null)
    setSessionCompleted(false)
    setStartTime(null)
  }

  if (sessionCompleted && sessionResult) {
    return (
      <div className="space-y-6">
        <div className="text-center">
          <Trophy className="h-16 w-16 text-yellow-500 mx-auto mb-4" />
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Sessão Completada!</h1>
          <p className="text-gray-600">Parabéns por completar mais uma micro-sessão</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Resumo da Sessão</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">
                  {sessionResult.session_summary?.questions_answered || 0}
                </div>
                <div className="text-sm text-gray-600">Questões</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {sessionResult.session_summary?.correct_answers || 0}
                </div>
                <div className="text-sm text-gray-600">Acertos</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">
                  {Math.round(sessionResult.session_summary?.accuracy_rate || 0)}%
                </div>
                <div className="text-sm text-gray-600">Precisão</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-yellow-600">
                  {sessionResult.session_summary?.total_xp_earned || 0}
                </div>
                <div className="text-sm text-gray-600">XP Ganho</div>
              </div>
            </div>

            {sessionResult.user_progress?.level_up && (
              <Alert>
                <Trophy className="h-4 w-4" />
                <AlertDescription>
                  🎉 Parabéns! Você subiu {sessionResult.user_progress.levels_gained} nível(is)! 
                  Agora você está no nível {sessionResult.user_progress.new_level}!
                </AlertDescription>
              </Alert>
            )}

            {sessionResult.achievements_unlocked?.length > 0 && (
              <div className="space-y-2">
                <h4 className="font-semibold">Conquistas Desbloqueadas:</h4>
                {sessionResult.achievements_unlocked.map((achievement, index) => (
                  <Badge key={index} variant="secondary" className="mr-2">
                    🏆 {achievement.achievement.name}
                  </Badge>
                ))}
              </div>
            )}

            <div className="flex space-x-4">
              <Button onClick={startMicroSession} className="flex-1">
                <RotateCcw className="h-4 w-4 mr-2" />
                Nova Sessão
              </Button>
              <Button variant="outline" onClick={resetSession} className="flex-1">
                Voltar ao Menu
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (!currentSession) {
    return (
      <div className="space-y-6">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Micro-Learning</h1>
          <p className="text-gray-600">Sessões curtas de 10 questões para aprendizagem eficaz</p>
        </div>

        <Card className="bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2 text-blue-700">
              <BookOpen className="h-6 w-6" />
              <span>Sessão Inteligente</span>
            </CardTitle>
            <CardDescription>
              Questões selecionadas com base na regra de Pareto e seu desempenho individual
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid md:grid-cols-3 gap-4 text-sm">
              <div className="flex items-center space-x-2">
                <Target className="h-4 w-4 text-blue-600" />
                <span>10 questões focadas</span>
              </div>
              <div className="flex items-center space-x-2">
                <Clock className="h-4 w-4 text-blue-600" />
                <span>15 minutos máximo</span>
              </div>
              <div className="flex items-center space-x-2">
                <Star className="h-4 w-4 text-blue-600" />
                <span>Seleção inteligente</span>
              </div>
            </div>
            
            <Button 
              onClick={startMicroSession} 
              disabled={loading}
              className="w-full bg-blue-600 hover:bg-blue-700"
            >
              {loading ? 'Preparando sessão...' : 'Iniciar Sessão'}
            </Button>
          </CardContent>
        </Card>

        <div className="grid md:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Como Funciona</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              <div className="flex items-start space-x-3">
                <div className="bg-blue-100 rounded-full p-1 mt-0.5">
                  <span className="text-blue-600 text-xs font-bold">1</span>
                </div>
                <div>
                  <strong>Seleção Inteligente:</strong> 80% das questões vêm dos temas que mais caem nas provas
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <div className="bg-blue-100 rounded-full p-1 mt-0.5">
                  <span className="text-blue-600 text-xs font-bold">2</span>
                </div>
                <div>
                  <strong>Personalização:</strong> 20% baseado no seu desempenho individual
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <div className="bg-blue-100 rounded-full p-1 mt-0.5">
                  <span className="text-blue-600 text-xs font-bold">3</span>
                </div>
                <div>
                  <strong>Micro-Learning:</strong> Sessões curtas para máxima retenção
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Benefícios</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              <div className="flex items-center space-x-2">
                <CheckCircle className="h-4 w-4 text-green-600" />
                <span>Foco nos temas mais importantes</span>
              </div>
              <div className="flex items-center space-x-2">
                <CheckCircle className="h-4 w-4 text-green-600" />
                <span>Adaptação ao seu nível</span>
              </div>
              <div className="flex items-center space-x-2">
                <CheckCircle className="h-4 w-4 text-green-600" />
                <span>Sessões que cabem na sua rotina</span>
              </div>
              <div className="flex items-center space-x-2">
                <CheckCircle className="h-4 w-4 text-green-600" />
                <span>Gamificação motivacional</span>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    )
  }

  const currentQuestion = questions[currentQuestionIndex]
  const progress = ((currentQuestionIndex + 1) / questions.length) * 100

  return (
    <div className="space-y-6">
      {/* Header da Sessão */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            Questão {currentQuestionIndex + 1} de {questions.length}
          </h1>
          <p className="text-gray-600">{currentQuestion?.specialty}</p>
        </div>
        <div className="flex items-center space-x-4">
          <Badge variant="outline">
            <Flame className="h-3 w-3 mr-1" />
            Sessão Ativa
          </Badge>
        </div>
      </div>

      {/* Barra de Progresso */}
      <div className="space-y-2">
        <Progress value={progress} className="h-2" />
        <div className="flex justify-between text-sm text-gray-600">
          <span>Progresso da Sessão</span>
          <span>{Math.round(progress)}%</span>
        </div>
      </div>

      {/* Questão */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <Badge variant="secondary">{currentQuestion?.difficulty}</Badge>
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <Clock className="h-4 w-4" />
              <span>Tempo livre</span>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="text-lg leading-relaxed">
            {currentQuestion?.question_text}
          </div>

          {/* Opções */}
          <div className="space-y-3">
            {currentQuestion?.options && Object.entries(currentQuestion.options).map(([key, value]) => (
              <button
                key={key}
                onClick={() => setSelectedOption(key)}
                disabled={showResult}
                className={`w-full p-4 text-left rounded-lg border transition-colors ${
                  selectedOption === key
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                } ${showResult ? 'cursor-not-allowed' : 'cursor-pointer'}`}
              >
                <div className="flex items-center space-x-3">
                  <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center ${
                    selectedOption === key ? 'border-blue-500 bg-blue-500' : 'border-gray-300'
                  }`}>
                    {selectedOption === key && (
                      <div className="w-2 h-2 bg-white rounded-full"></div>
                    )}
                  </div>
                  <span className="font-medium">{key.toUpperCase()})</span>
                  <span>{value}</span>
                </div>
              </button>
            ))}
          </div>

          {/* Resultado */}
          {showResult && sessionResult && (
            <Alert className={sessionResult.is_correct ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'}>
              <div className="flex items-center space-x-2">
                {sessionResult.is_correct ? (
                  <CheckCircle className="h-5 w-5 text-green-600" />
                ) : (
                  <XCircle className="h-5 w-5 text-red-600" />
                )}
                <span className="font-medium">
                  {sessionResult.is_correct ? 'Correto!' : 'Incorreto'}
                </span>
                {sessionResult.xp_earned > 0 && (
                  <Badge variant="secondary">+{sessionResult.xp_earned} XP</Badge>
                )}
              </div>
              {!sessionResult.is_correct && (
                <div className="mt-2">
                  <p className="text-sm">
                    <strong>Resposta correta:</strong> {sessionResult.correct_option}
                  </p>
                </div>
              )}
              {sessionResult.explanation && (
                <div className="mt-2">
                  <p className="text-sm">
                    <strong>Explicação:</strong> {sessionResult.explanation}
                  </p>
                </div>
              )}
            </Alert>
          )}

          {/* Botões de Ação */}
          <div className="flex space-x-4">
            {!showResult ? (
              <Button 
                onClick={submitAnswer}
                disabled={!selectedOption}
                className="flex-1"
              >
                Confirmar Resposta
              </Button>
            ) : (
              <>
                {currentQuestionIndex < questions.length - 1 ? (
                  <Button onClick={nextQuestion} className="flex-1">
                    Próxima Questão
                    <ArrowRight className="h-4 w-4 ml-2" />
                  </Button>
                ) : (
                  <Button onClick={completeSession} className="flex-1">
                    Finalizar Sessão
                    <Trophy className="h-4 w-4 ml-2" />
                  </Button>
                )}
              </>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default QuestionsPage

