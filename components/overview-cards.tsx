import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Zap, TrendingUp, Leaf, AlertTriangle } from "lucide-react"

export function OverviewCards() {
  const cards = [
    {
      title: "Energy Generated",
      value: "142.5 kWh",
      change: "+12.3%",
      changeType: "increase" as const,
      icon: Zap,
      description: "Last 24 hours",
    },
    {
      title: "Biogas Production",
      value: "85.2 m³",
      change: "+8.7%",
      changeType: "increase" as const,
      icon: TrendingUp,
      description: "Current week",
    },
    {
      title: "CO₂ Reduced",
      value: "2.8 tons",
      change: "+15.2%",
      changeType: "increase" as const,
      icon: Leaf,
      description: "This month",
    },
    {
      title: "System Efficiency",
      value: "94.2%",
      change: "-2.1%",
      changeType: "decrease" as const,
      icon: AlertTriangle,
      description: "Current status",
    },
  ]

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 lg:gap-6">
      {cards.map((card, index) => (
        <Card key={index} className="bg-white">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">{card.title}</CardTitle>
            <div className="bg-green-100 p-2 rounded-lg">
              <card.icon className="h-4 w-4 text-green-600" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-gray-900">{card.value}</div>
            <div className="flex items-center space-x-2 mt-2">
              <span
                className={`text-sm font-medium ${card.changeType === "increase" ? "text-green-600" : "text-red-600"}`}
              >
                {card.change}
              </span>
              <span className="text-sm text-gray-600">{card.description}</span>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
