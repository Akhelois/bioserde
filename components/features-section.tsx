import { Monitor, Brain, Smartphone, Settings } from "lucide-react"

export function FeaturesSection() {
  const features = [
    {
      icon: Monitor,
      title: "Real-time Monitoring",
      description:
        "Track biogas production, temperature, and system performance with live dashboards and instant alerts.",
    },
    {
      icon: Brain,
      title: "AI Predictions",
      description:
        "Machine learning algorithms predict optimal production cycles and maintenance schedules for peak efficiency.",
    },
    {
      icon: Smartphone,
      title: "Remote Control & Access",
      description: "Control and monitor your Bioserde system from anywhere with our mobile app and web platform.",
    },
    {
      icon: Settings,
      title: "Easy Setup",
      description: "Plug-and-play installation with automated calibration. Get up and running in under 24 hours.",
    },
  ]

  return (
    <section id="features" className="py-20 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">Powerful Features</h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Advanced technology meets user-friendly design to deliver the most efficient biogas production system on the
            market.
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
          {features.map((feature, index) => (
            <div key={index} className="bg-white rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow">
              <div className="bg-green-100 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
                <feature.icon className="h-6 w-6 text-green-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">{feature.title}</h3>
              <p className="text-gray-600">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
