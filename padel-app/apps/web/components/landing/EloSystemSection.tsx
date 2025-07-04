"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@workspace/ui/components/card";
import { Badge } from "@workspace/ui/components/badge";

const eloCategories = [
  {
    name: "Bronze",
    range: "0-1200",
    color: "bg-amber-600",
    description: "Perfect for beginners starting their padel journey"
  },
  {
    name: "Silver",
    range: "1200-1600",
    color: "bg-gray-500",
    description: "Intermediate players developing their skills"
  },
  {
    name: "Gold",
    range: "1600-2000",
    color: "bg-yellow-500",
    description: "Advanced players with strong technique"
  },
  {
    name: "Platinum",
    range: "2000+",
    color: "bg-blue-600",
    description: "Elite players competing at the highest level"
  }
];

export default function EloSystemSection() {
  return (
    <section className="w-full py-12 md:py-24 lg:py-32">
      <div className="container mx-auto px-4 md:px-6 max-w-7xl">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl">
            Fair Play with ELO Rating System
          </h2>
          <p className="mx-auto max-w-[700px] text-muted-foreground md:text-xl mt-4">
            Our advanced ELO rating system ensures you're matched with players of similar skill levels. Compete fairly and track your improvement over time.
          </p>
        </div>
        
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4 mb-12">
          {eloCategories.map((category) => (
            <Card key={category.name} className="text-center">
              <CardHeader className="pb-3">
                <div className={`w-16 h-16 ${category.color} rounded-full mx-auto flex items-center justify-center mb-3`}>
                  <span className="text-white font-bold text-xl">{category.name[0]}</span>
                </div>
                <CardTitle className="text-xl">{category.name}</CardTitle>
                <Badge variant="outline" className="mx-auto">{category.range}</Badge>
              </CardHeader>
              <CardContent className="pt-0">
                <p className="text-muted-foreground text-sm">{category.description}</p>
              </CardContent>
            </Card>
          ))}
        </div>

        <div className="bg-gradient-to-r from-blue-50 to-indigo-100 dark:from-gray-800 dark:to-gray-700 rounded-2xl p-8 text-center">
          <h3 className="text-2xl font-bold mb-4">How It Works</h3>
          <div className="grid gap-4 md:grid-cols-3">
            <div className="space-y-2">
              <div className="w-12 h-12 bg-blue-500 rounded-full mx-auto flex items-center justify-center">
                <span className="text-white font-bold">1</span>
              </div>
              <h4 className="font-semibold">Play Matches</h4>
              <p className="text-sm text-muted-foreground">Compete in games and tournaments</p>
            </div>
            <div className="space-y-2">
              <div className="w-12 h-12 bg-indigo-500 rounded-full mx-auto flex items-center justify-center">
                <span className="text-white font-bold">2</span>
              </div>
              <h4 className="font-semibold">Rating Updates</h4>
              <p className="text-sm text-muted-foreground">Your ELO adjusts based on results</p>
            </div>
            <div className="space-y-2">
              <div className="w-12 h-12 bg-purple-500 rounded-full mx-auto flex items-center justify-center">
                <span className="text-white font-bold">3</span>
              </div>
              <h4 className="font-semibold">Fair Matches</h4>
              <p className="text-sm text-muted-foreground">Get matched with similar skill levels</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}