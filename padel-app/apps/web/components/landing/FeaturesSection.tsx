"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@workspace/ui/components/card";

const features = [
  {
    title: "🏟️ Club Discovery",
    description: "Browse and discover padel clubs in your area. Find the perfect venue for your next game.",
    icon: "🏟️"
  },
  {
    title: "📅 Court Booking",
    description: "Book courts with real-time availability. Reserve your spot and get on the court faster.",
    icon: "📅"
  },
  {
    title: "🎮 Game Management",
    description: "Create private games or join public matches. Connect with other players and organize games effortlessly.",
    icon: "🎮"
  },
  {
    title: "👥 Team Formation",
    description: "Create and manage competitive teams. Build your dream team and compete together.",
    icon: "👥"
  },
  {
    title: "🏆 Tournament Participation",
    description: "Join tournaments with ELO-based skill categories. Compete at your level and climb the rankings.",
    icon: "🏆"
  },
  {
    title: "📊 Performance Tracking",
    description: "Monitor your ELO rating and view personal statistics. Track your progress and improvement over time.",
    icon: "📊"
  },
  {
    title: "🏅 Achievement System",
    description: "Earn trophies and badges for tournament victories. Showcase your accomplishments and celebrate wins.",
    icon: "🏅"
  },
  {
    title: "📱 Social Features",
    description: "Invite friends and build your padel community. Connect with other players and expand your network.",
    icon: "📱"
  }
];

export default function FeaturesSection() {
  return (
    <section id="features" className="w-full py-12 md:py-24 lg:py-32 bg-gray-50 dark:bg-gray-900/50">
      <div className="container mx-auto px-4 md:px-6 max-w-7xl">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl">
            Everything You Need to Excel at Padel
          </h2>
          <p className="mx-auto max-w-[700px] text-muted-foreground md:text-xl mt-4">
            From finding courts to tracking your progress, PadelGo provides all the tools you need to take your padel game to the next level.
          </p>
        </div>
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {features.map((feature) => (
            <Card key={feature.title} className="border-0 shadow-lg hover:shadow-xl transition-shadow duration-300">
              <CardHeader className="pb-3">
                <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center mb-3">
                  <span className="text-white text-xl">{feature.icon}</span>
                </div>
                <CardTitle className="text-lg font-semibold">
                  {feature.title.replace(/^[^a-zA-Z]*/, '')}
                </CardTitle>
              </CardHeader>
              <CardContent className="pt-0">
                <p className="text-muted-foreground text-sm">{feature.description}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
}