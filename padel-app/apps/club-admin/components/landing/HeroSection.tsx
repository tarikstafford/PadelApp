"use client";

import { Button } from "@workspace/ui/components/button";
import Link from "next/link";

export default function HeroSection() {
  return (
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
  );
} 