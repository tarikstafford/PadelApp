"use client";

import { Button } from "@workspace/ui/components/button";
import Link from "next/link";

export default function CTASection() {
  return (
    <section className="w-full py-12 md:py-24 lg:py-32 bg-gradient-to-r from-emerald-600 to-teal-700">
      <div className="container px-4 md:px-6">
        <div className="text-center space-y-4">
          <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl text-white">
            Ready to Transform Your Club Management?
          </h2>
          <p className="mx-auto max-w-[600px] text-emerald-100 md:text-xl">
            Join hundreds of successful padel clubs that are already using PadelGo to streamline operations, increase revenue, and create better player experiences.
          </p>
          <div className="flex flex-col gap-4 min-[400px]:flex-row min-[400px]:justify-center mt-8">
            <Button asChild size="lg" className="bg-white text-emerald-600 hover:bg-emerald-50">
              <Link href="/register">Start Your Free Trial</Link>
            </Button>
            <Button asChild variant="outline" size="lg" className="border-white text-white hover:bg-white hover:text-emerald-600">
              <Link href="/login">Admin Login</Link>
            </Button>
          </div>
          <div className="mt-8 text-center">
            <p className="text-emerald-100 text-sm">
              No credit card required • Free 14-day trial • Cancel anytime
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}