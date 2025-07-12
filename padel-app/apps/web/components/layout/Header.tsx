"use client";

import Link from 'next/link';
import { useState } from 'react';
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
import { Loader2, X, Menu } from 'lucide-react';
import { NotificationCenter } from '@/components/notifications/notification-center';

export default function Header() {
  const { user, logout, isLoading } = useAuth();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

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
              <Link href="/tournaments" className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors">
                Tournaments
              </Link>
              <Link href="/teams" className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors">
                Teams
              </Link>
              <Link href="/leaderboard" className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors">
                Leaderboard
              </Link>
              <Link href="/bookings" className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors">
                My Bookings
              </Link>
              
              {/* Auth-dependent UI */}
              {isLoading ? (
                <Loader2 className="h-5 w-5 animate-spin" />
              ) : user ? (
                <>
                  <NotificationCenter />
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
                    <Link href="/teams" passHref>
                      <DropdownMenuItem>My Teams</DropdownMenuItem>
                    </Link>
                    <Link href="/profile/notifications" passHref>
                      <DropdownMenuItem>Notification Settings</DropdownMenuItem>
                    </Link>
                    <DropdownMenuItem disabled>Settings</DropdownMenuItem>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem onClick={logout}>
                      Logout
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
                </>
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

            {/* Mobile Menu Button */}
            <div className="md:hidden">
              <button 
                onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                className="text-foreground p-2 rounded-md hover:bg-accent hover:text-accent-foreground"
                aria-label="Toggle menu"
                aria-expanded={isMobileMenuOpen}
              >
                {isMobileMenuOpen ? (
                  <X className="h-6 w-6" />
                ) : (
                  <Menu className="h-6 w-6" />
                )}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Mobile Menu */}
      {isMobileMenuOpen && (
        <div className="md:hidden">
          <div className="px-2 pt-2 pb-3 space-y-1 bg-background border-b">
            <Link 
              href="/discover" 
              className="block px-3 py-2 rounded-md text-base font-medium text-muted-foreground hover:text-primary hover:bg-accent transition-colors"
              onClick={() => setIsMobileMenuOpen(false)}
            >
              Discover
            </Link>
            <Link 
              href="/tournaments" 
              className="block px-3 py-2 rounded-md text-base font-medium text-muted-foreground hover:text-primary hover:bg-accent transition-colors"
              onClick={() => setIsMobileMenuOpen(false)}
            >
              Tournaments
            </Link>
            <Link 
              href="/teams" 
              className="block px-3 py-2 rounded-md text-base font-medium text-muted-foreground hover:text-primary hover:bg-accent transition-colors"
              onClick={() => setIsMobileMenuOpen(false)}
            >
              Teams
            </Link>
            <Link 
              href="/leaderboard" 
              className="block px-3 py-2 rounded-md text-base font-medium text-muted-foreground hover:text-primary hover:bg-accent transition-colors"
              onClick={() => setIsMobileMenuOpen(false)}
            >
              Leaderboard
            </Link>
            <Link 
              href="/bookings" 
              className="block px-3 py-2 rounded-md text-base font-medium text-muted-foreground hover:text-primary hover:bg-accent transition-colors"
              onClick={() => setIsMobileMenuOpen(false)}
            >
              My Bookings
            </Link>
            
            {/* Auth section for mobile */}
            <div className="pt-4 border-t border-accent">
              {isLoading ? (
                <div className="px-3 py-2">
                  <Loader2 className="h-5 w-5 animate-spin" />
                </div>
              ) : user ? (
                <>
                  <div className="px-3 py-2 flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <Avatar className="h-8 w-8">
                        <AvatarImage src={user.profile_picture_url || ''} alt={user.full_name || 'User'} />
                        <AvatarFallback>{user.full_name?.charAt(0).toUpperCase() || 'U'}</AvatarFallback>
                      </Avatar>
                      <span className="text-sm font-medium">{user.full_name || 'User'}</span>
                    </div>
                    <NotificationCenter />
                  </div>
                  <Link 
                    href="/profile" 
                    className="block px-3 py-2 rounded-md text-base font-medium text-muted-foreground hover:text-primary hover:bg-accent transition-colors"
                    onClick={() => setIsMobileMenuOpen(false)}
                  >
                    Profile
                  </Link>
                  <Link 
                    href="/teams" 
                    className="block px-3 py-2 rounded-md text-base font-medium text-muted-foreground hover:text-primary hover:bg-accent transition-colors"
                    onClick={() => setIsMobileMenuOpen(false)}
                  >
                    My Teams
                  </Link>
                  <Link 
                    href="/profile/notifications" 
                    className="block px-3 py-2 rounded-md text-base font-medium text-muted-foreground hover:text-primary hover:bg-accent transition-colors"
                    onClick={() => setIsMobileMenuOpen(false)}
                  >
                    Notification Settings
                  </Link>
                  <button 
                    onClick={() => {
                      logout();
                      setIsMobileMenuOpen(false);
                    }}
                    className="block w-full text-left px-3 py-2 rounded-md text-base font-medium text-muted-foreground hover:text-primary hover:bg-accent transition-colors"
                  >
                    Logout
                  </button>
                </>
              ) : (
                <div className="space-y-2 px-3">
                  <Link href="/auth/login" passHref>
                    <Button 
                      variant="ghost" 
                      className="w-full justify-start text-base font-medium"
                      onClick={() => setIsMobileMenuOpen(false)}
                    >
                      Login
                    </Button>
                  </Link>
                  <Link href="/auth/register" passHref>
                    <Button 
                      className="w-full justify-start text-base font-medium"
                      onClick={() => setIsMobileMenuOpen(false)}
                    >
                      Sign Up
                    </Button>
                  </Link>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </header>
  );
} 