import Link from 'next/link';
import { ThemeToggle } from './ThemeToggle';

export default function Header() {
  return (
    <header className="bg-background border-b">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Site Title/Logo */}
          <div className="flex-shrink-0">
            <Link href="/" className="text-2xl font-bold text-primary">
              PadelGo
            </Link>
          </div>

          {/* Right section: Navigation & Theme Toggle */}
          <div className="flex items-center space-x-4">
            {/* Navigation Links */}
            <nav className="hidden md:flex space-x-6">
              <Link href="/discover" className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors">
                Discover
              </Link>
              <Link href="/bookings" className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors">
                My Bookings
              </Link>
              <Link href="/profile" className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors">
                Profile
              </Link>
              <Link href="/auth/login" className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors">
                Login
              </Link>
            </nav>

            {/* Theme Toggle */}
            <ThemeToggle />

            {/* Mobile Menu Button - Placeholder */}
            <div className="md:hidden">
              {/* Icon for mobile menu, e.g., Hamburger icon */}
              <button className="text-foreground p-2 rounded-md hover:bg-accent hover:text-accent-foreground">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
} 