"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { Button } from "@workspace/ui/components/button";
import Link from "next/link";
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

export default function LandingPage() {
  return (
    <div className="flex flex-col min-h-screen">
      <main className="flex-1">
        <section className="w-full py-12 md:py-24 lg:py-32 xl:py-48 bg-gray-50 dark:bg-gray-800/10">
          <div className="container px-4 md:px-6">
            <div className="flex flex-col items-center space-y-4 text-center">
              <h1 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl lg:text-6xl/none">
                The All-In-One Platform to Manage Your Padel Club
              </h1>
              <p className="mx-auto max-w-[700px] text-gray-500 md:text-xl dark:text-gray-400">
                Focus on your players, we'll handle the rest.
              </p>
              <Button asChild size="lg">
                <Link href="/register">Sign Up for Free</Link>
              </Button>
            </div>
          </div>
        </section>
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
      </main>
      <footer className="flex items-center justify-center w-full h-24 border-t">
        <p className="text-gray-500">© 2025 PadelGo. All rights reserved.</p>
      </footer>
    </div>
  );
} 