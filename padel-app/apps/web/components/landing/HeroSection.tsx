"use client";

import { Button } from "@workspace/ui/components/button";
import Link from "next/link";

export default function HeroSection() {
  return (
    <section className="w-full min-h-[80vh] flex items-center py-12 md:py-24 lg:py-32 xl:py-48 bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto px-4 md:px-6 max-w-7xl">
        <div className="grid gap-6 lg:grid-cols-[1fr_500px] lg:gap-12 xl:grid-cols-[1fr_600px]">
          <div className="flex flex-col justify-center space-y-4">
            <div className="space-y-2">
              <h1 className="text-3xl font-bold tracking-tighter sm:text-5xl xl:text-6xl/none text-primary">
                Your Ultimate Padel Experience Starts Here
              </h1>
              <p className="max-w-[600px] text-muted-foreground md:text-xl">
                Discover courts, join tournaments, track your progress, and connect with the padel community. Everything you need to elevate your game.
              </p>
            </div>
            <div className="flex flex-col gap-2 min-[400px]:flex-row">
              <Button asChild size="lg">
                <Link href="/discover">Find Courts</Link>
              </Button>
              <Button asChild variant="outline" size="lg">
                <Link href="/tournaments">Join Tournaments</Link>
              </Button>
            </div>
          </div>
          <div className="flex items-center justify-center">
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-blue-400 to-indigo-600 rounded-2xl blur opacity-20"></div>
              <div className="relative bg-white dark:bg-gray-800 rounded-2xl p-8 shadow-2xl">
                <div className="text-center space-y-4">
                  <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full mx-auto flex items-center justify-center">
                    <span className="text-white font-bold text-xl">🏓</span>
                  </div>
                  <h3 className="text-2xl font-bold">Ready to Play?</h3>
                  <p className="text-muted-foreground">Join thousands of players already using PadelGo</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}