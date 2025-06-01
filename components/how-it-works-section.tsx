import { ArrowRight, Trash2, Cog, Zap } from "lucide-react"

export function HowItWorksSection() {
  const steps = [
    {
      icon: Trash2,
      title: "Waste In",
      description: "Organic waste is fed into the Bioserde system through our automated input mechanism.",
    },
    {
      icon: Cog,
      title: "Biodegradation",
      description: "Advanced anaerobic digestion breaks down organic matter using optimized bacterial cultures.",
    },
    {
      icon: Zap,
      title: "Biogas Output",
      description: "Clean biogas is produced and can be used for heating, electricity, or fuel applications.",
    },
  ]

  return (
    <section id="how-it-works" className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">How It Works</h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Our simple three-step process transforms your organic waste into valuable clean energy with minimal effort
            and maximum efficiency.
          </p>
        </div>

        <div className="relative">
          {/* Desktop Layout */}
          <div className="hidden lg:flex items-center justify-between">
            {steps.map((step, index) => (
              <div key={index} className="flex items-center">
                <div className="text-center">
                  <div className="bg-green-100 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-4">
                    <step.icon className="h-10 w-10 text-green-600" />
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">{step.title}</h3>
                  <p className="text-gray-600 max-w-xs">{step.description}</p>
                </div>
                {index < steps.length - 1 && <ArrowRight className="h-8 w-8 text-green-600 mx-8" />}
              </div>
            ))}
          </div>

          {/* Mobile Layout */}
          <div className="lg:hidden space-y-8">
            {steps.map((step, index) => (
              <div key={index} className="text-center">
                <div className="bg-green-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                  <step.icon className="h-8 w-8 text-green-600" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">{step.title}</h3>
                <p className="text-gray-600">{step.description}</p>
                {index < steps.length - 1 && (
                  <div className="flex justify-center mt-6">
                    <ArrowRight className="h-6 w-6 text-green-600 rotate-90" />
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        <div className="mt-16 bg-green-50 rounded-2xl p-8 text-center">
          <h3 className="text-2xl font-bold text-gray-900 mb-4">Ready to See It in Action?</h3>
          <p className="text-gray-600 mb-6">Watch our Bioserde system transform waste into energy in real-time.</p>
          <button className="bg-green-600 hover:bg-green-700 text-white px-8 py-3 rounded-lg font-semibold transition-colors">
            Schedule Live Demo
          </button>
        </div>
      </div>
    </section>
  )
}
