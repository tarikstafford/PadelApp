"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@workspace/ui/components/card";

const benefits = [
  {
    title: "Increase Revenue",
    description: "Maximize court utilization and revenue with smart scheduling and pricing tools. Track financial performance in real-time.",
    icon: "💰",
    stat: "25% average revenue increase"
  },
  {
    title: "Save Time",
    description: "Automate routine tasks like booking confirmations, tournament brackets, and player communications. Focus on what matters most.",
    icon: "⏱️",
    stat: "10+ hours saved per week"
  },
  {
    title: "Improve Player Experience",
    description: "Provide seamless booking experiences and organized tournaments. Happy players become loyal members.",
    icon: "😊",
    stat: "90% customer satisfaction"
  },
  {
    title: "Scale Your Business",
    description: "Grow from a single court to multiple locations with our scalable platform. Manage everything from one dashboard.",
    icon: "📈",
    stat: "Support for unlimited courts"
  }
];

export default function BusinessBenefitsSection() {
  return (
    <section className="w-full py-12 md:py-24 lg:py-32">
      <div className="container px-4 md:px-6">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl">
            Grow Your Padel Business with Confidence
          </h2>
          <p className="mx-auto max-w-[700px] text-muted-foreground md:text-xl mt-4">
            Join successful club owners who have transformed their operations and increased profitability with PadelGo.
          </p>
        </div>
        
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          {benefits.map((benefit) => (
            <Card key={benefit.title} className="text-center border-0 shadow-lg">
              <CardHeader className="pb-3">
                <div className="w-16 h-16 bg-gradient-to-r from-emerald-500 to-teal-600 rounded-full mx-auto flex items-center justify-center mb-3">
                  <span className="text-white text-2xl">{benefit.icon}</span>
                </div>
                <CardTitle className="text-xl">{benefit.title}</CardTitle>
              </CardHeader>
              <CardContent className="pt-0 space-y-3">
                <p className="text-muted-foreground text-sm">{benefit.description}</p>
                <div className="bg-emerald-50 dark:bg-emerald-900/20 rounded-lg p-3">
                  <p className="text-sm font-semibold text-emerald-700 dark:text-emerald-300">{benefit.stat}</p>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        <div className="mt-16 bg-gradient-to-r from-emerald-50 to-teal-100 dark:from-gray-800 dark:to-gray-700 rounded-2xl p-8">
          <div className="text-center space-y-4">
            <h3 className="text-2xl font-bold">Why Club Owners Choose PadelGo</h3>
            <div className="grid gap-4 md:grid-cols-3 mt-8">
              <div className="space-y-2">
                <div className="text-3xl font-bold text-emerald-600">500+</div>
                <p className="text-sm text-muted-foreground">Happy Club Owners</p>
              </div>
              <div className="space-y-2">
                <div className="text-3xl font-bold text-emerald-600">98%</div>
                <p className="text-sm text-muted-foreground">Uptime Guarantee</p>
              </div>
              <div className="space-y-2">
                <div className="text-3xl font-bold text-emerald-600">24/7</div>
                <p className="text-sm text-muted-foreground">Support Available</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}