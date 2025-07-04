"use client";

import React, { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@workspace/ui/components/dialog';
import { Button } from '@workspace/ui/components/button';
import { Input } from '@workspace/ui/components/input';
import { Label } from '@workspace/ui/components/label';
// Using custom tab implementation since tabs component is not available
import { useGameOnboarding } from './GameOnboardingProvider';
import { useAuth } from '@/contexts/AuthContext';
import { useForm } from 'react-hook-form';
import { toast } from 'sonner';
import { Loader2, GamepadIcon } from 'lucide-react';
import { cn } from '@/lib/utils';

interface LoginFormData {
  email: string;
  password: string;
}

interface RegisterFormData {
  full_name: string;
  email: string;
  password: string;
  confirmPassword: string;
}

export function AuthenticationModal() {
  const { 
    currentStep, 
    setCurrentStep, 
    authMode, 
    setAuthMode, 
    gameData, 
    handleAuthSuccess 
  } = useGameOnboarding();
  
  const { login, register } = useAuth();
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Login form
  const {
    register: registerLogin,
    handleSubmit: handleLoginSubmit,
    formState: { errors: loginErrors },
    reset: resetLogin
  } = useForm<LoginFormData>();

  // Register form
  const {
    register: registerRegister,
    handleSubmit: handleRegisterSubmit,
    formState: { errors: registerErrors },
    reset: resetRegister,
    watch
  } = useForm<RegisterFormData>();

  const isOpen = currentStep === 'auth';

  const onCloseModal = () => {
    setCurrentStep('preview');
    resetLogin();
    resetRegister();
  };

  const onLoginSubmit = async (data: LoginFormData) => {
    try {
      setIsSubmitting(true);
      
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/v1/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Login failed');
      }

      const authData = await response.json();
      login(authData.access_token, authData.refresh_token);
      
      toast.success('Successfully signed in!');
      await handleAuthSuccess();
    } catch (error) {
      console.error('Login error:', error);
      toast.error(error instanceof Error ? error.message : 'Login failed');
    } finally {
      setIsSubmitting(false);
    }
  };

  const onRegisterSubmit = async (data: RegisterFormData) => {
    if (data.password !== data.confirmPassword) {
      toast.error('Passwords do not match');
      return;
    }

    try {
      setIsSubmitting(true);
      
      await register(data.full_name, data.email, data.password);
      
      toast.success('Account created successfully!');
      await handleAuthSuccess();
    } catch (error) {
      console.error('Register error:', error);
      toast.error(error instanceof Error ? error.message : 'Registration failed');
    } finally {
      setIsSubmitting(false);
    }
  };

  const passwordValue = watch('password');

  return (
    <Dialog open={isOpen} onOpenChange={onCloseModal}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <GamepadIcon className="h-5 w-5" />
            Join {gameData?.game.booking.court.name}
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          {/* Game Context Reminder */}
          {gameData && (
            <div className="bg-muted/50 rounded-lg p-3 text-sm">
              <p className="font-medium">
                {gameData.game.booking.court.club?.name}
              </p>
              <p className="text-muted-foreground">
                {new Date(gameData.game.booking.start_time).toLocaleDateString()} at{' '}
                {new Date(gameData.game.booking.start_time).toLocaleTimeString([], {
                  hour: '2-digit',
                  minute: '2-digit'
                })}
              </p>
            </div>
          )}

          {/* Custom Tab Implementation */}
          <div className="w-full">
            <div className="flex border-b border-border">
              <button
                onClick={() => setAuthMode('login')}
                className={cn(
                  "flex-1 px-4 py-2 text-sm font-medium border-b-2 transition-colors",
                  authMode === 'login'
                    ? 'border-primary text-primary'
                    : 'border-transparent text-muted-foreground hover:text-foreground'
                )}
              >
                Sign In
              </button>
              <button
                onClick={() => setAuthMode('register')}
                className={cn(
                  "flex-1 px-4 py-2 text-sm font-medium border-b-2 transition-colors",
                  authMode === 'register'
                    ? 'border-primary text-primary'
                    : 'border-transparent text-muted-foreground hover:text-foreground'
                )}
              >
                Sign Up
              </button>
            </div>

            {/* Login Form */}
            {authMode === 'login' && (
              <div className="mt-4 space-y-4">
                <form onSubmit={handleLoginSubmit(onLoginSubmit)} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="login-email">Email</Label>
                    <Input
                      id="login-email"
                      type="email"
                      placeholder="Enter your email"
                      {...registerLogin('email', {
                        required: 'Email is required',
                        pattern: {
                          value: /^\S+@\S+$/i,
                          message: 'Invalid email address'
                        }
                      })}
                    />
                    {loginErrors.email && (
                      <p className="text-sm text-destructive">{loginErrors.email.message}</p>
                    )}
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="login-password">Password</Label>
                    <Input
                      id="login-password"
                      type="password"
                      placeholder="Enter your password"
                      {...registerLogin('password', {
                        required: 'Password is required'
                      })}
                    />
                    {loginErrors.password && (
                      <p className="text-sm text-destructive">{loginErrors.password.message}</p>
                    )}
                  </div>

                  <Button
                    type="submit"
                    className="w-full"
                    disabled={isSubmitting}
                  >
                    {isSubmitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                    Sign In & Join Game
                  </Button>
                </form>
              </div>
            )}

            {/* Register Form */}
            {authMode === 'register' && (
              <div className="mt-4 space-y-4">
                <form onSubmit={handleRegisterSubmit(onRegisterSubmit)} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="register-name">Full Name</Label>
                    <Input
                      id="register-name"
                      type="text"
                      placeholder="Enter your full name"
                      {...registerRegister('full_name', {
                        required: 'Full name is required'
                      })}
                    />
                    {registerErrors.full_name && (
                      <p className="text-sm text-destructive">{registerErrors.full_name.message}</p>
                    )}
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="register-email">Email</Label>
                    <Input
                      id="register-email"
                      type="email"
                      placeholder="Enter your email"
                      {...registerRegister('email', {
                        required: 'Email is required',
                        pattern: {
                          value: /^\S+@\S+$/i,
                          message: 'Invalid email address'
                        }
                      })}
                    />
                    {registerErrors.email && (
                      <p className="text-sm text-destructive">{registerErrors.email.message}</p>
                    )}
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="register-password">Password</Label>
                    <Input
                      id="register-password"
                      type="password"
                      placeholder="Choose a password"
                      {...registerRegister('password', {
                        required: 'Password is required',
                        minLength: {
                          value: 6,
                          message: 'Password must be at least 6 characters'
                        }
                      })}
                    />
                    {registerErrors.password && (
                      <p className="text-sm text-destructive">{registerErrors.password.message}</p>
                    )}
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="register-confirm-password">Confirm Password</Label>
                    <Input
                      id="register-confirm-password"
                      type="password"
                      placeholder="Confirm your password"
                      {...registerRegister('confirmPassword', {
                        required: 'Please confirm your password',
                        validate: (value) => 
                          value === passwordValue || 'Passwords do not match'
                      })}
                    />
                    {registerErrors.confirmPassword && (
                      <p className="text-sm text-destructive">{registerErrors.confirmPassword.message}</p>
                    )}
                  </div>

                  <Button
                    type="submit"
                    className="w-full"
                    disabled={isSubmitting}
                  >
                    {isSubmitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                    Create Account & Join Game
                  </Button>
                </form>
              </div>
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}