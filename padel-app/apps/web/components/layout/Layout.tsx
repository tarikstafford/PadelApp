'use client';

import React from 'react';
import { usePathname } from 'next/navigation';
import Header from './Header';
import Footer from './Footer';

interface LayoutProps {
  children: React.ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const pathname = usePathname();
  const isLandingPage = pathname === '/';

  return (
    <div className="flex flex-col min-h-screen">
      <Header />
      <main className={isLandingPage 
        ? "flex-grow w-full" 
        : "flex-grow container mx-auto px-4 sm:px-6 lg:px-8 py-8"
      }>
        {children}
      </main>
      {!isLandingPage && <Footer />}
    </div>
  );
} 