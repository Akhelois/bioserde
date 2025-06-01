import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { AlertTriangle, Info, CheckCircle, Clock } from "lucide-react"

export function RecentAlerts() {
  const alerts = [
    {
      id: 1,
      type: "warning",
      title: "Temperature Rising",
      description: "System temperature reached 40°C. Monitor closely.",
      time: "2 hours ago",
      status: "active",
    },
    {
      id: 2,
      type: "info",
      title: "Maintenance Scheduled",
      description: "Routine maintenance scheduled for tomorrow at 9:00 AM.",
      time: "4 hours ago",
      status: "scheduled",
    },
    {
      id: 3,
      type: "success",
      title: "Production Target Met",
      description: "Daily biogas production target of 80m³ achieved.",
      time: "6 hours ago",
      status: "resolved",
    },
    {
      id: 4,
      type: "warning",
      title: "Filter Status",
      description: "Primary filter efficiency dropped to 85%. Consider replacement.",
      time: "1 day ago",
      status: "acknowledged",
    },
  ]

  const getAlertIcon = (type: string) => {
    switch (type) {
      case "warning":
        return { icon: AlertTriangle, color: "text-orange-600 bg-orange-100" }
      case "info":
        return { icon: Info, color: "text-blue-600 bg-blue-100" }
      case "success":
        return { icon: CheckCircle, color: "text-green-600 bg-green-100" }
      default:
        return { icon: AlertTriangle, color: "text-gray-600 bg-gray-100" }
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active":
        return "bg-red-100 text-red-800"
      case "scheduled":
        return "bg-blue-100 text-blue-800"
      case "resolved":
        return "bg-green-100 text-green-800"
      case "acknowledged":
        return "bg-yellow-100 text-yellow-800"
      default:
        return "bg-gray-100 text-gray-800"
    }
  }

  return (
    <Card className="bg-white">
      <CardHeader>
        <CardTitle className="text-lg font-semibold text-gray-900">Recent Alerts</CardTitle>
        <p className="text-sm text-gray-600">System notifications and status updates</p>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {alerts.map((alert) => {
            const alertIcon = getAlertIcon(alert.type)
            return (
              <div key={alert.id} className="flex items-start space-x-3 p-3 border border-gray-200 rounded-lg">
                <div className={`p-2 rounded-lg ${alertIcon.color}`}>
                  <alertIcon.icon className="h-4 w-4" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-1">
                    <h4 className="text-sm font-semibold text-gray-900">{alert.title}</h4>
                    <Badge className={getStatusColor(alert.status)}>{alert.status}</Badge>
                  </div>
                  <p className="text-sm text-gray-600 mb-2">{alert.description}</p>
                  <div className="flex items-center space-x-1 text-xs text-gray-500">
                    <Clock className="h-3 w-3" />
                    <span>{alert.time}</span>
                  </div>
                </div>
              </div>
            )
          })}
        </div>

        <div className="mt-4 text-center">
          <button className="text-sm text-green-600 hover:text-green-700 font-medium">View All Alerts</button>
        </div>
      </CardContent>
    </Card>
  )
}
