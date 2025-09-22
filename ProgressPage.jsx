import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { BarChart3 } from 'lucide-react'

const ProgressPage = () => {
  return (
    <div className="space-y-6">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Progresso</h1>
        <p className="text-gray-600">Acompanhe sua evolução nos estudos</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <BarChart3 className="h-6 w-6" />
            <span>Estatísticas</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gray-600">
            Funcionalidade em desenvolvimento...
          </p>
        </CardContent>
      </Card>
    </div>
  )
}

export default ProgressPage

