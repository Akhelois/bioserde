import { Button } from "@/components/ui/button"
import { ArrowRight, Phone, Mail } from "lucide-react"

export function CTASection() {
  return (
    <section className="py-20 bg-gradient-to-r from-green-600 to-emerald-600">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-white mb-6">
          Ready to Transform Your Waste Into Energy?
        </h2>
        <p className="text-xl text-green-100 mb-8 max-w-3xl mx-auto">
          Join the sustainable energy revolution today. Get a personalized demo and see how Bioserde can reduce your
          waste costs while generating clean energy.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
          <Button size="lg" className="bg-white text-green-600 hover:bg-gray-100">
            <Phone className="mr-2 h-5 w-5" />
            Request Demo
            <ArrowRight className="ml-2 h-5 w-5" />
          </Button>
          <Button size="lg" variant="outline" className="border-white text-white hover:bg-white hover:text-green-600">
            <Mail className="mr-2 h-5 w-5" />
            Contact Sales
          </Button>
        </div>

        <div className="grid md:grid-cols-3 gap-8 text-white">
          <div>
            <div className="text-3xl font-bold mb-2">24/7</div>
            <div className="text-green-100">Expert Support</div>
          </div>
          <div>
            <div className="text-3xl font-bold mb-2">30-Day</div>
            <div className="text-green-100">Money-Back Guarantee</div>
          </div>
          <div>
            <div className="text-3xl font-bold mb-2">Free</div>
            <div className="text-green-100">Installation & Training</div>
          </div>
        </div>
      </div>
    </section>
  )
}
