"use client";

import { Button } from "@workspace/ui/components/button";
import Link from "next/link";

export default function CTASection() {
  return (
    <section className="w-full py-12 md:py-24 lg:py-32 bg-gradient-to-r from-blue-600 to-indigo-700">
      <div className="container mx-auto px-4 md:px-6 max-w-7xl">
        <div className="text-center space-y-4">
          <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl text-white">
            Ready to Elevate Your Padel Game?
          </h2>
          <p className="mx-auto max-w-[600px] text-blue-100 md:text-xl">
            Join thousands of players who are already using PadelGo to find courts, compete in tournaments, and track their progress.
          </p>
          <div className="flex flex-col gap-4 min-[400px]:flex-row min-[400px]:justify-center mt-8">
            <Button asChild size="lg" className="bg-white text-blue-600 hover:bg-blue-50">
              <Link href="/auth/register">Get Started Free</Link>
            </Button>
            <Button asChild variant="outline" size="lg" className="border-white text-white hover:bg-white hover:text-blue-600">
              <Link href="/discover">Explore Courts</Link>
            </Button>
          </div>
        </div>
      </div>
    </section>
  );
}