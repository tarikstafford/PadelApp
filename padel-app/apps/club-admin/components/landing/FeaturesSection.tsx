"use client";

import { Badge } from "@workspace/ui/components/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@workspace/ui/components/card";

const features = [
  {
    title: "🏢 Complete Club Management",
    description: "Manage your club profile, facilities, and operational details all in one place. Create a professional presence that attracts players.",
    icon: "🏢"
  },
  {
    title: "🎾 Court Administration",
    description: "Add, edit, and manage court availability with ease. Control scheduling, pricing, and maintenance schedules efficiently.",
    icon: "🎾"
  },
  {
    title: "📋 Booking Overview",
    description: "View and manage all club bookings with a comprehensive dashboard. Track occupancy, revenue, and player activity.",
    icon: "📋"
  },
  {
    title: "🏆 Tournament Creation",
    description: "Organize tournaments with automated bracket generation. Create engaging competitions that keep players coming back.",
    icon: "🏆"
  },
  {
    title: "📈 Analytics Dashboard",
    description: "Track club performance, revenue, and user engagement with detailed analytics. Make data-driven decisions for your business.",
    icon: "📈"
  },
  {
    title: "⚙️ Schedule Management",
    description: "Manage court schedules and operational hours with flexible scheduling tools. Optimize your court utilization.",
    icon: "⚙️"
  },
  {
    title: "👨‍💼 Multi-Admin Support",
    description: "Collaborate with other club administrators. Assign roles and permissions to manage your team effectively.",
    icon: "👨‍💼"
  },
  {
    title: "💳 Payment Processing",
    description: "Accept online payments for bookings and memberships directly through the portal. Streamline your revenue collection.",
    icon: "💳",
    comingSoon: true
  }
];

export default function FeaturesSection() {
  return (
    <section id="features" className="w-full py-12 md:py-24 lg:py-32 bg-gray-50 dark:bg-gray-900/50">
      <div className="container px-4 md:px-6">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl">
            Everything You Need to Run a Successful Padel Club
          </h2>
          <p className="mx-auto max-w-[700px] text-muted-foreground md:text-xl mt-4">
            From booking management to tournament organization, our platform provides all the tools you need to grow your business and delight your players.
          </p>
        </div>
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {features.map((feature) => (
            <Card key={feature.title} className="border-0 shadow-lg hover:shadow-xl transition-shadow duration-300">
              <CardHeader className="pb-3">
                <div className="w-12 h-12 bg-gradient-to-r from-emerald-500 to-teal-600 rounded-lg flex items-center justify-center mb-3">
                  <span className="text-white text-xl">{feature.icon}</span>
                </div>
                <CardTitle className="text-lg font-semibold flex items-center justify-between">
                  <span>{feature.title.replace(/^[^a-zA-Z]*/, '')}</span>
                  {feature.comingSoon && <Badge variant="secondary">Coming Soon</Badge>}
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