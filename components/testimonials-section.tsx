import { Star } from "lucide-react"

export function TestimonialsSection() {
  const testimonials = [
    {
      name: "Sarah Chen",
      role: "Sustainability Director",
      company: "GreenTech Industries",
      image: "/placeholder.svg?height=60&width=60",
      content:
        "Bioserde has transformed our waste management strategy. We've reduced disposal costs by 70% while generating clean energy for our facility.",
      rating: 5,
    },
    {
      name: "Michael Rodriguez",
      role: "Operations Manager",
      company: "Farm Fresh Co.",
      image: "/placeholder.svg?height=60&width=60",
      content:
        "The AI predictions are incredibly accurate. We can now optimize our biogas production and plan maintenance schedules with confidence.",
      rating: 5,
    },
    {
      name: "Emma Thompson",
      role: "Environmental Engineer",
      company: "EcoSolutions Ltd.",
      image: "/placeholder.svg?height=60&width=60",
      content:
        "Installation was seamless and the remote monitoring gives us complete control. It's the future of sustainable waste management.",
      rating: 5,
    },
  ]

  return (
    <section id="testimonials" className="py-20 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">What Our Customers Say</h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Join hundreds of satisfied customers who have transformed their waste into valuable energy.
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {testimonials.map((testimonial, index) => (
            <div key={index} className="bg-white rounded-xl p-6 shadow-sm">
              <div className="flex items-center mb-4">
                {[...Array(testimonial.rating)].map((_, i) => (
                  <Star key={i} className="h-5 w-5 text-yellow-400 fill-current" />
                ))}
              </div>
              <p className="text-gray-600 mb-6 italic">"{testimonial.content}"</p>
              <div className="flex items-center">
                <img
                  src={testimonial.image || "/placeholder.svg"}
                  alt={testimonial.name}
                  className="w-12 h-12 rounded-full mr-4"
                />
                <div>
                  <div className="font-semibold text-gray-900">{testimonial.name}</div>
                  <div className="text-sm text-gray-600">{testimonial.role}</div>
                  <div className="text-sm text-green-600">{testimonial.company}</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
