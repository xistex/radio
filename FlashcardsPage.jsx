import { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { 
  Brain, 
  Clock, 
  RotateCcw, 
  CheckCircle, 
  XCircle, 
  Star,
  Calendar,
  TrendingUp,
  BookOpen,
  Plus,
  Eye,
  EyeOff
} from 'lucide-react'

const FlashcardsPage = () => {
  const { apiCall } = useAuth()
  const [dueFlashcards, setDueFlashcards] = useState([])
  const [currentCardIndex, setCurrentCardIndex] = useState(0)
  const [showAnswer, setShowAnswer] = useState(false)
  const [stats, setStats] = useState(null)
  const [forecast, setForecast] = useState([])
  const [loading, setLoading] = useState(false)
  const [sessionActive, setSessionActive] = useState(false)
  const [retentionRate, setRetentionRate] = useState(null)

  useEffect(() => {
    loadFlashcardData()
  }, [])

  const loadFlashcardData = async () => {
    setLoading(true)
    try {
      // Carregar flashcards devido
      const dueResponse = await apiCall('/flashcards/due?limit=20')
      setDueFlashcards(dueResponse.flashcards || [])

      // Carregar estatísticas
      const statsResponse = await apiCall('/flashcards/stats')
      setStats(statsResponse)

      // Carregar previsão
      const forecastResponse = await apiCall('/flashcards/forecast?days=7')
      setForecast(forecastResponse.forecast || [])

      // Carregar taxa de retenção
      const retentionResponse = await apiCall('/flashcards/retention-rate?days=30')
      setRetentionRate(retentionResponse)

    } catch (error) {
      console.error('Erro ao carregar dados dos flashcards:', error)
    } finally {
      setLoading(false)
    }
  }

  const generateFlashcards = async () => {
    setLoading(true)
    try {
      const response = await apiCall('/flashcards/generate', {
        method: 'POST',
        body: JSON.stringify({ limit: 50 })
      })
      
      alert(`${response.flashcards_created} flashcards foram criados automaticamente!`)
      loadFlashcardData()
    } catch (error) {
      console.error('Erro ao gerar flashcards:', error)
    } finally {
      setLoading(false)
    }
  }

  const startSession = () => {
    if (dueFlashcards.length > 0) {
      setSessionActive(true)
      setCurrentCardIndex(0)
      setShowAnswer(false)
    }
  }

  const reviewFlashcard = async (qualityRating) => {
    if (!sessionActive || !dueFlashcards[currentCardIndex]) return

    try {
      const flashcard = dueFlashcards[currentCardIndex]
      await apiCall(`/flashcards/${flashcard.id}/review`, {
        method: 'POST',
        body: JSON.stringify({ quality_rating: qualityRating })
      })

      // Próximo flashcard ou finalizar sessão
      if (currentCardIndex < dueFlashcards.length - 1) {
        setCurrentCardIndex(currentCardIndex + 1)
        setShowAnswer(false)
      } else {
        setSessionActive(false)
        loadFlashcardData() // Recarregar dados
      }
    } catch (error) {
      console.error('Erro ao revisar flashcard:', error)
    }
  }

  const getQualityLabel = (rating) => {
    const labels = {
      0: 'Não lembrei',
      1: 'Muito difícil',
      2: 'Difícil',
      3: 'Médio',
      4: 'Fácil',
      5: 'Muito fácil'
    }
    return labels[rating] || ''
  }

  const getRetentionColor = (rate) => {
    if (rate >= 90) return 'text-green-600'
    if (rate >= 80) return 'text-blue-600'
    if (rate >= 70) return 'text-yellow-600'
    return 'text-red-600'
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <Brain className="h-8 w-8 animate-spin mx-auto mb-2" />
          <p>Carregando flashcards...</p>
        </div>
      </div>
    )
  }

  if (sessionActive && dueFlashcards.length > 0) {
    const currentCard = dueFlashcards[currentCardIndex]
    const progress = ((currentCardIndex + 1) / dueFlashcards.length) * 100

    return (
      <div className="space-y-6">
        {/* Header da Sessão */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              Flashcard {currentCardIndex + 1} de {dueFlashcards.length}
            </h1>
            <p className="text-gray-600">{currentCard.specialty}</p>
          </div>
          <Badge variant="outline">
            <Brain className="h-3 w-3 mr-1" />
            Repetição Espaçada
          </Badge>
        </div>

        {/* Barra de Progresso */}
        <div className="space-y-2">
          <Progress value={progress} className="h-2" />
          <div className="flex justify-between text-sm text-gray-600">
            <span>Progresso da Sessão</span>
            <span>{Math.round(progress)}%</span>
          </div>
        </div>

        {/* Flashcard */}
        <Card className="min-h-[400px]">
          <CardHeader>
            <div className="flex items-center justify-between">
              <Badge variant="secondary">{currentCard.difficulty}</Badge>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowAnswer(!showAnswer)}
              >
                {showAnswer ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                {showAnswer ? 'Ocultar' : 'Mostrar'} Resposta
              </Button>
            </div>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Frente do Card */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-700">Pergunta:</h3>
              <div className="p-4 bg-blue-50 rounded-lg border-l-4 border-blue-500">
                <p className="text-lg leading-relaxed">{currentCard.front_text}</p>
              </div>
            </div>

            {/* Verso do Card */}
            {showAnswer && (
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-gray-700">Resposta:</h3>
                <div className="p-4 bg-green-50 rounded-lg border-l-4 border-green-500">
                  <div className="prose prose-sm max-w-none">
                    {currentCard.back_text.split('\n').map((line, index) => (
                      <p key={index} className="mb-2">{line}</p>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Botões de Avaliação */}
            {showAnswer && (
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-gray-700">Como foi sua lembrança?</h3>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                  {[0, 1, 2, 3, 4, 5].map((rating) => (
                    <Button
                      key={rating}
                      variant={rating <= 2 ? 'destructive' : rating <= 3 ? 'outline' : 'default'}
                      onClick={() => reviewFlashcard(rating)}
                      className="flex flex-col p-4 h-auto"
                    >
                      <span className="text-lg font-bold">{rating}</span>
                      <span className="text-xs">{getQualityLabel(rating)}</span>
                    </Button>
                  ))}
                </div>
                <p className="text-sm text-gray-600 text-center">
                  0 = Não lembrei nada | 3 = Lembrei com dificuldade | 5 = Lembrei perfeitamente
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Flashcards</h1>
        <p className="text-gray-600">Sistema de repetição espaçada para memorização eficaz</p>
      </div>

      {/* Estatísticas Principais */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-4 text-center">
              <div className="text-2xl font-bold text-blue-600">{stats.total_flashcards}</div>
              <div className="text-sm text-gray-600">Total</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4 text-center">
              <div className="text-2xl font-bold text-orange-600">{stats.due_flashcards}</div>
              <div className="text-sm text-gray-600">Para Revisar</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4 text-center">
              <div className="text-2xl font-bold text-green-600">{stats.mature_flashcards}</div>
              <div className="text-sm text-gray-600">Dominados</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4 text-center">
              <div className="text-2xl font-bold text-purple-600">{stats.learning_flashcards}</div>
              <div className="text-sm text-gray-600">Aprendendo</div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Taxa de Retenção */}
      {retentionRate && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <TrendingUp className="h-5 w-5" />
              <span>Taxa de Retenção (30 dias)</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center space-x-4">
              <div className={`text-3xl font-bold ${getRetentionColor(retentionRate.retention_rate)}`}>
                {retentionRate.retention_rate}%
              </div>
              <div className="text-sm text-gray-600">
                {retentionRate.interpretation.excellent && "Excelente! Sua memória está muito bem treinada."}
                {retentionRate.interpretation.good && "Bom desempenho! Continue praticando regularmente."}
                {retentionRate.interpretation.fair && "Razoável. Considere revisar com mais frequência."}
                {retentionRate.interpretation.needs_improvement && "Precisa melhorar. Aumente a frequência de revisões."}
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Ações Principais */}
      <div className="grid md:grid-cols-2 gap-6">
        <Card className="bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2 text-blue-700">
              <Brain className="h-6 w-6" />
              <span>Sessão de Revisão</span>
            </CardTitle>
            <CardDescription>
              {dueFlashcards.length > 0 
                ? `${dueFlashcards.length} flashcards prontos para revisão`
                : 'Nenhum flashcard devido no momento'
              }
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button 
              onClick={startSession}
              disabled={dueFlashcards.length === 0}
              className="w-full bg-blue-600 hover:bg-blue-700"
            >
              {dueFlashcards.length > 0 ? 'Iniciar Revisão' : 'Nada para revisar'}
            </Button>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-green-50 to-green-100 border-green-200">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2 text-green-700">
              <Plus className="h-6 w-6" />
              <span>Gerar Flashcards</span>
            </CardTitle>
            <CardDescription>
              Criar flashcards automaticamente das questões que você errou
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button 
              onClick={generateFlashcards}
              disabled={loading}
              className="w-full bg-green-600 hover:bg-green-700"
            >
              {loading ? 'Gerando...' : 'Gerar Flashcards'}
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Previsão Semanal */}
      {forecast.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Calendar className="h-5 w-5" />
              <span>Previsão dos Próximos 7 Dias</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-7 gap-2">
              {forecast.map((day, index) => (
                <div 
                  key={index}
                  className={`text-center p-3 rounded-lg border ${
                    day.is_today ? 'bg-blue-50 border-blue-200' : 'bg-gray-50 border-gray-200'
                  }`}
                >
                  <div className="text-xs text-gray-600 mb-1">
                    {new Date(day.date).toLocaleDateString('pt-BR', { weekday: 'short' })}
                  </div>
                  <div className="text-lg font-bold text-gray-900">
                    {day.flashcards_due}
                  </div>
                  <div className="text-xs text-gray-600">
                    {day.is_today ? 'Hoje' : 'cards'}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Estatísticas por Especialidade */}
      {stats?.by_specialty && stats.by_specialty.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Progresso por Especialidade</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {stats.by_specialty.map((specialty, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <div className="font-medium">{specialty.specialty}</div>
                    <div className="text-sm text-gray-600">
                      {specialty.total_flashcards} flashcards
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-medium">
                      Facilidade: {specialty.average_ease}
                    </div>
                    <div className="text-sm text-gray-600">
                      Intervalo: {specialty.average_interval} dias
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Informações sobre Repetição Espaçada */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Como Funciona a Repetição Espaçada</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-sm">
          <div className="flex items-start space-x-3">
            <div className="bg-blue-100 rounded-full p-1 mt-0.5">
              <span className="text-blue-600 text-xs font-bold">1</span>
            </div>
            <div>
              <strong>Algoritmo SM-2:</strong> Baseado na curva de esquecimento de Ebbinghaus
            </div>
          </div>
          <div className="flex items-start space-x-3">
            <div className="bg-blue-100 rounded-full p-1 mt-0.5">
              <span className="text-blue-600 text-xs font-bold">2</span>
            </div>
            <div>
              <strong>Intervalos Adaptativos:</strong> Aumentam conforme você domina o conteúdo
            </div>
          </div>
          <div className="flex items-start space-x-3">
            <div className="bg-blue-100 rounded-full p-1 mt-0.5">
              <span className="text-blue-600 text-xs font-bold">3</span>
            </div>
            <div>
              <strong>Geração Automática:</strong> Flashcards criados das questões que você erra
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default FlashcardsPage

