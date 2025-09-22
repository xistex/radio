import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { 
  BookOpen, 
  CreditCard, 
  Target, 
  Flame, 
  Star, 
  Trophy, 
  TrendingUp,
  Calendar,
  Clock,
  Award
} from 'lucide-react'

const Dashboard = () => {
  const { user, apiCall } = useAuth()
  const [dashboardData, setDashboardData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      const data = await apiCall('/progress/dashboard')
      setDashboardData(data)
    } catch (error) {
      console.error('Error fetching dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  const stats = dashboardData?.user_stats || {}
  const todayActivity = dashboardData?.today_activity || {}
  const recentSessions = dashboardData?.recent_sessions || []
  const specialtyProgress = dashboardData?.specialty_progress || []
  const recentAchievements = dashboardData?.recent_achievements || []

  return (
    <div className="space-y-6">
      {/* Welcome Header */}
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold text-gray-900">
          Olá, {user?.username}! 👋
        </h1>
        <p className="text-gray-600">
          Pronto para mais um dia de estudos para a residência?
        </p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4 text-center">
            <div className="flex items-center justify-center space-x-2 mb-2">
              <Flame className="h-5 w-5 text-orange-500" />
              <span className="text-2xl font-bold text-orange-500">{stats.streak || 0}</span>
            </div>
            <p className="text-sm text-gray-600">Sequência</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4 text-center">
            <div className="flex items-center justify-center space-x-2 mb-2">
              <Star className="h-5 w-5 text-yellow-500" />
              <span className="text-2xl font-bold text-yellow-500">{stats.xp || 0}</span>
            </div>
            <p className="text-sm text-gray-600">XP Total</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4 text-center">
            <div className="flex items-center justify-center space-x-2 mb-2">
              <Trophy className="h-5 w-5 text-purple-500" />
              <span className="text-2xl font-bold text-purple-500">{stats.level || 1}</span>
            </div>
            <p className="text-sm text-gray-600">Nível</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4 text-center">
            <div className="flex items-center justify-center space-x-2 mb-2">
              <Target className="h-5 w-5 text-green-500" />
              <span className="text-2xl font-bold text-green-500">{stats.accuracy_rate || 0}%</span>
            </div>
            <p className="text-sm text-gray-600">Precisão</p>
          </CardContent>
        </Card>
      </div>

      {/* Today's Goal */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Calendar className="h-5 w-5" />
            <span>Meta de Hoje</span>
          </CardTitle>
          <CardDescription>
            {todayActivity.questions_answered || 0} de {user?.daily_goal || 10} questões respondidas
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Progress 
            value={todayActivity.goal_progress || 0} 
            className="w-full mb-4" 
          />
          <div className="flex justify-between text-sm text-gray-600">
            <span>Progresso: {Math.round(todayActivity.goal_progress || 0)}%</span>
            <span>{todayActivity.flashcards_due || 0} flashcards para revisar</span>
          </div>
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <div className="grid md:grid-cols-2 gap-6">
        <Card className="bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2 text-blue-700">
              <BookOpen className="h-6 w-6" />
              <span>Sessão de Questões</span>
            </CardTitle>
            <CardDescription>
              Responda 10 questões em uma sessão focada
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Link to="/questions">
              <Button className="w-full bg-blue-600 hover:bg-blue-700">
                Iniciar Sessão
              </Button>
            </Link>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-purple-50 to-purple-100 border-purple-200">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2 text-purple-700">
              <CreditCard className="h-6 w-6" />
              <span>Flashcards</span>
            </CardTitle>
            <CardDescription>
              Revise conceitos com repetição espaçada
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Link to="/flashcards">
              <Button className="w-full bg-purple-600 hover:bg-purple-700">
                Revisar Flashcards
              </Button>
            </Link>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity & Progress */}
      <div className="grid md:grid-cols-2 gap-6">
        {/* Recent Sessions */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Clock className="h-5 w-5" />
              <span>Sessões Recentes</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {recentSessions.length > 0 ? (
              <div className="space-y-3">
                {recentSessions.slice(0, 3).map((session, index) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div>
                      <p className="font-medium">{session.questions_answered} questões</p>
                      <p className="text-sm text-gray-600">
                        {session.accuracy_rate}% de acerto
                      </p>
                    </div>
                    <Badge variant="secondary">
                      +{session.xp_earned} XP
                    </Badge>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-4">
                Nenhuma sessão recente
              </p>
            )}
          </CardContent>
        </Card>

        {/* Recent Achievements */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Award className="h-5 w-5" />
              <span>Conquistas Recentes</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {recentAchievements.length > 0 ? (
              <div className="space-y-3">
                {recentAchievements.map((achievement, index) => (
                  <div key={index} className="flex items-center space-x-3 p-3 bg-yellow-50 rounded-lg">
                    <Trophy className="h-6 w-6 text-yellow-600" />
                    <div>
                      <p className="font-medium">{achievement.achievement?.name}</p>
                      <p className="text-sm text-gray-600">
                        {achievement.achievement?.description}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-4">
                Nenhuma conquista recente
              </p>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Specialty Progress */}
      {specialtyProgress.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <TrendingUp className="h-5 w-5" />
              <span>Progresso por Especialidade</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-2 gap-4">
              {specialtyProgress.slice(0, 4).map((progress, index) => (
                <div key={index} className="space-y-2">
                  <div className="flex justify-between">
                    <span className="font-medium">{progress.specialty}</span>
                    <span className="text-sm text-gray-600">
                      {progress.accuracy_rate}%
                    </span>
                  </div>
                  <Progress value={progress.accuracy_rate} className="h-2" />
                  <p className="text-xs text-gray-500">
                    {progress.correct_answers}/{progress.total_questions} questões
                  </p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

export default Dashboard

