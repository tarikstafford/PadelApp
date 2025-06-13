"use client";

import Link from 'next/link';
import { ThemeToggle } from './ThemeToggle';
import { useAuth } from '@/contexts/AuthContext';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
  Avatar,
  AvatarFallback,
  AvatarImage,
  Button,
} from '@workspace/ui/components';
import { Loader2 } from 'lucide-react';

export default function Header() {
  const { user, logout, isLoading } = useAuth();

  return (
    <header className="bg-background border-b sticky top-0 z-50">
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
            <nav className="hidden md:flex items-center space-x-6">
              <Link href="/discover" className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors">
                Discover
              </Link>
              <Link href="/bookings" className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors">
                My Bookings
              </Link>
              
              {/* Auth-dependent UI */}
              {isLoading ? (
                <Loader2 className="h-5 w-5 animate-spin" />
              ) : user ? (
                <DropdownMenu>
                  <DropdownMenuTrigger>
                    <Avatar className="h-8 w-8">
                      <AvatarImage src={user.profile_picture_url || ''} alt={user.full_name || 'User'} />
                      <AvatarFallback>{user.full_name?.charAt(0).toUpperCase() || 'U'}</AvatarFallback>
                    </Avatar>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuLabel>My Account</DropdownMenuLabel>
                    <DropdownMenuSeparator />
                    <Link href="/profile" passHref>
                      <DropdownMenuItem>Profile</DropdownMenuItem>
                    </Link>
                    <DropdownMenuItem disabled>Settings</DropdownMenuItem>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem onClick={logout}>
                      Logout
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              ) : (
                <>
                  <Link href="/auth/login" passHref>
                    <Button variant="ghost" className="text-sm font-medium">Login</Button>
                  </Link>
                  <Link href="/auth/register" passHref>
                    <Button className="text-sm font-medium">Sign Up</Button>
                  </Link>
                </>
              )}
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