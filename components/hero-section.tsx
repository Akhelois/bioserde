import { Button } from "@/components/ui/button"
import { ArrowRight, Play } from "lucide-react"

export function HeroSection() {
  return (
    <section className="bg-gradient-to-br from-green-50 to-emerald-50 py-20 lg:py-32">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          <div className="text-center lg:text-left">
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-gray-900 leading-tight">
              Transform Waste Into <span className="text-green-600">Clean Energy</span>
            </h1>
            <p className="mt-6 text-xl text-gray-600 leading-relaxed">
              Bioserde converts organic waste into clean biogas energy with cutting-edge technology. Reduce waste,
              generate power, and create a sustainable future.
            </p>
            <div className="mt-8 flex flex-col sm:flex-row gap-4 justify-center lg:justify-start">
              <Button size="lg" className="bg-green-600 hover:bg-green-700 text-white">
                Request Demo
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
              <Button size="lg" variant="outline" className="border-green-600 text-green-600 hover:bg-green-50">
                <Play className="mr-2 h-5 w-5" />
                Watch Video
              </Button>
            </div>
          </div>
          <div className="relative">
            <div className="bg-green-100 rounded-2xl p-8 lg:p-12">
              <img
                src="/placeholder.svg?height=400&width=500"
                alt="Bioserde Machine"
                className="w-full h-auto rounded-lg shadow-lg"
              />
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
