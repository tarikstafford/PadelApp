import HeroSection from "@/components/landing/HeroSection";
import FeaturesSection from "@/components/landing/FeaturesSection";
import EloSystemSection from "@/components/landing/EloSystemSection";
import CTASection from "@/components/landing/CTASection";
import Footer from "@/components/landing/Footer";

export default function HomePage() {
  return (
    <div className="flex flex-col min-h-screen w-full">
      <main className="flex-1 w-full">
        <HeroSection />
        <FeaturesSection />
        <EloSystemSection />
        <CTASection />
      </main>
      <Footer />
    </div>
  );
}
