"use client";

import { Button } from "@workspace/ui/components/button";
import Link from "next/link";

export default function HeroSection() {
  return (
    <section className="w-full py-12 md:py-24 lg:py-32 xl:py-48 bg-gradient-to-br from-emerald-50 to-teal-100 dark:from-gray-900 dark:to-gray-800">
      <div className="container px-4 md:px-6">
        <div className="grid gap-6 lg:grid-cols-[1fr_500px] lg:gap-12 xl:grid-cols-[1fr_600px]">
          <div className="flex flex-col justify-center space-y-4">
            <div className="space-y-2">
              <h1 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl lg:text-6xl/none text-primary">
                Revolutionize Your Padel Club Management
              </h1>
              <p className="max-w-[600px] text-muted-foreground md:text-xl">
                Streamline operations, boost revenue, and create amazing experiences for your players with our comprehensive club management platform.
              </p>
            </div>
            <div className="flex flex-col gap-2 min-[400px]:flex-row">
              <Button asChild size="lg">
                <Link href="/register">Start Free Trial</Link>
              </Button>
              <Button asChild variant="outline" size="lg">
                <Link href="/login">Admin Login</Link>
              </Button>
            </div>
          </div>
          <div className="flex items-center justify-center">
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-emerald-400 to-teal-600 rounded-2xl blur opacity-20"></div>
              <div className="relative bg-white dark:bg-gray-800 rounded-2xl p-8 shadow-2xl">
                <div className="text-center space-y-4">
                  <div className="w-16 h-16 bg-gradient-to-r from-emerald-500 to-teal-600 rounded-full mx-auto flex items-center justify-center">
                    <span className="text-white font-bold text-xl">🏢</span>
                  </div>
                  <h3 className="text-2xl font-bold">Ready to Transform Your Club?</h3>
                  <p className="text-muted-foreground">Join hundreds of successful padel clubs already using PadelGo</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
} 