import Link from "next/link";
import { Button } from "@workspace/ui/components/button";

export default function HomePage() {
  return (
    <section className="py-12 md:py-24 lg:py-32 xl:py-40">
      <div className="container px-4 md:px-6">
        <div className="grid gap-6 lg:grid-cols-[1fr_400px] lg:gap-12 xl:grid-cols-[1fr_600px]">
          <div className="flex flex-col justify-center space-y-4">
            <div className="space-y-2">
              <h1 className="text-3xl font-bold tracking-tighter sm:text-5xl xl:text-6xl/none text-primary">
                Book Your Padel Court with Ease
              </h1>
              <p className="max-w-[600px] text-muted-foreground md:text-xl">
                Discover and reserve Padel courts in your area!! Invite friends, join games, and get on the court faster with PadelGo.
              </p>
            </div>
            <div className="flex flex-col gap-2 min-[400px]:flex-row">
              <Link href="/discover">
                <Button size="lg">Find a Court</Button>
              </Link>
              {/* <Link href="/auth/register">
                <Button variant="outline" size="lg">Sign Up</Button>
              </Link> */}
            </div>
          </div>
          {/* Optional: Placeholder for an image or illustration */}
          {/* <img
            alt="Hero Padel Image"
            className="mx-auto aspect-video overflow-hidden rounded-xl object-cover sm:w-full lg:order-last lg:aspect-square"
            height="550"
            src="/placeholder.svg" // Replace with an actual image path
            width="550"
          /> */}
        </div>
      </div>
    </section>
  );
}
