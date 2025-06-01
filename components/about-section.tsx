import { Leaf, Recycle, Zap } from "lucide-react"

export function AboutSection() {
  return (
    <section id="about" className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">About Bioserde</h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            We're revolutionizing waste management with innovative biogas technology that transforms organic waste into
            clean, renewable energy while reducing environmental impact.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8 mb-16">
          <div className="text-center">
            <div className="bg-green-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <Leaf className="h-8 w-8 text-green-600" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Environmental Impact</h3>
            <p className="text-gray-600">
              Reduce methane emissions by 90% while converting waste into valuable energy resources.
            </p>
          </div>
          <div className="text-center">
            <div className="bg-green-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <Recycle className="h-8 w-8 text-green-600" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Circular Economy</h3>
            <p className="text-gray-600">
              Transform waste streams into energy sources, creating a sustainable circular economy model.
            </p>
          </div>
          <div className="text-center">
            <div className="bg-green-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <Zap className="h-8 w-8 text-green-600" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Innovation</h3>
            <p className="text-gray-600">
              Cutting-edge AI and IoT technology optimizes biogas production for maximum efficiency.
            </p>
          </div>
        </div>

        <div className="bg-green-50 rounded-2xl p-8 lg:p-12">
          <div className="grid lg:grid-cols-2 gap-8 items-center">
            <div>
              <h3 className="text-2xl font-bold text-gray-900 mb-4">Leading the Green Energy Revolution</h3>
              <p className="text-gray-600 mb-6">
                Our patented biogas technology processes organic waste 3x faster than traditional methods, producing
                clean energy while eliminating harmful emissions. Join thousands of businesses already making a positive
                environmental impact.
              </p>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="text-3xl font-bold text-green-600">90%</div>
                  <div className="text-sm text-gray-600">Emission Reduction</div>
                </div>
                <div>
                  <div className="text-3xl font-bold text-green-600">3x</div>
                  <div className="text-sm text-gray-600">Faster Processing</div>
                </div>
              </div>
            </div>
            <div>
              <img
                src="/placeholder.svg?height=300&width=400"
                alt="Environmental Impact"
                className="w-full h-auto rounded-lg"
              />
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
