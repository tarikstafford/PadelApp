"use client";

import { Badge } from "@workspace/ui/components/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@workspace/ui/components/card";

const features = [
  {
    title: "Effortless Booking Management",
    description: "View your entire court schedule at a glance. Our intuitive interface makes managing and tracking bookings simple and efficient.",
  },
  {
    title: "Unified Player Directory",
    description: "Keep all your member information organized in one place. Easily view player details and manage your community.",
  },
  {
    title: "Streamlined Payments",
    description: "Soon, you'll be able to accept online payments for bookings and memberships directly through the portal. Less hassle, more play.",
    comingSoon: true,
  },
];

export default function FeaturesSection() {
  return (
    <section id="features" className="w-full py-12 md:py-24 lg:py-32">
      <div className="container px-4 md:px-6">
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {features.map((feature) => (
            <Card key={feature.title}>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  {feature.title}
                  {feature.comingSoon && <Badge>Coming Soon</Badge>}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p>{feature.description}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
} 