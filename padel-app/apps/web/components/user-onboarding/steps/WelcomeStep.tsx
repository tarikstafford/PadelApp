"use client";

import React, { useState, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@workspace/ui/components/card';
import { Button } from '@workspace/ui/components/button';
import { useUserOnboarding } from '../UserOnboardingProvider';
import { useAuth } from '@/contexts/AuthContext';
import { Upload, Camera, User, Sparkles, ArrowRight, Clock } from 'lucide-react';
import { cn } from '@/lib/utils';

export function WelcomeStep() {
  const { userData, setProfilePicture, nextStep, skipStep } = useUserOnboarding();
  const { user } = useAuth();
  const [dragActive, setDragActive] = useState(false);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (file: File) => {
    if (file && file.type.startsWith('image/')) {
      if (file.size > 2 * 1024 * 1024) {
        alert('File is too large. Maximum size is 2MB.');
        return;
      }
      
      setProfilePicture(file);
      setPreviewUrl(URL.createObjectURL(file));
    } else {
      alert('Please select a valid image file.');
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
    
    const files = e.dataTransfer.files;
    if (files && files[0]) {
      handleFileSelect(files[0]);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files[0]) {
      handleFileSelect(files[0]);
    }
  };

  const openFileDialog = () => {
    fileInputRef.current?.click();
  };

  const getDisplayName = () => {
    if (user?.full_name) return user.full_name;
    if (user?.email) return user.email.split('@')[0];
    return 'there';
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Welcome Header */}
      <div className="text-center space-y-4">
        <div className="flex items-center justify-center gap-2 mb-2">
          <Sparkles className="h-8 w-8 text-primary" />
          <h1 className="text-3xl font-bold">Welcome to PadelGo, {getDisplayName()}!</h1>
        </div>
        <p className="text-lg text-muted-foreground">
          Let&apos;s set up your profile so you can start connecting with the padel community.
        </p>
      </div>

      {/* Profile Picture Upload */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Camera className="h-5 w-5" />
            Add Your Profile Picture
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Upload Area */}
          <div
            className={cn(
              "relative border-2 border-dashed rounded-lg p-8 text-center transition-all duration-200",
              dragActive 
                ? "border-primary bg-primary/5" 
                : "border-muted-foreground/25 hover:border-primary/50 hover:bg-muted/50",
              "cursor-pointer"
            )}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onClick={openFileDialog}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleFileInput}
              className="hidden"
            />
            
            {previewUrl ? (
              <div className="space-y-4">
                <div className="relative w-24 h-24 mx-auto">
                  <img
                    src={previewUrl}
                    alt="Profile preview"
                    className="w-full h-full object-cover rounded-full border-4 border-primary/20"
                  />
                  <div className="absolute -bottom-1 -right-1 w-8 h-8 bg-primary rounded-full flex items-center justify-center">
                    <Camera className="h-4 w-4 text-primary-foreground" />
                  </div>
                </div>
                <div>
                  <p className="font-medium">Great photo!</p>
                  <p className="text-sm text-muted-foreground">
                    Click to change or drag a new image here
                  </p>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="w-16 h-16 mx-auto bg-muted rounded-full flex items-center justify-center">
                  <Upload className="h-8 w-8 text-muted-foreground" />
                </div>
                <div>
                  <p className="font-medium">Upload your profile picture</p>
                  <p className="text-sm text-muted-foreground">
                    Drag and drop an image here, or click to browse
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">
                    PNG, JPG up to 2MB
                  </p>
                </div>
              </div>
            )}
          </div>

          {/* Benefits */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 dark:bg-blue-950 dark:border-blue-800">
            <h4 className="font-medium text-blue-900 dark:text-blue-100 mb-2">
              Why add a profile picture?
            </h4>
            <ul className="space-y-1 text-sm text-blue-700 dark:text-blue-200">
              <li className="flex items-center gap-2">
                <div className="w-1 h-1 bg-current rounded-full" />
                Help other players recognize you at games
              </li>
              <li className="flex items-center gap-2">
                <div className="w-1 h-1 bg-current rounded-full" />
                Build trust within the community
              </li>
              <li className="flex items-center gap-2">
                <div className="w-1 h-1 bg-current rounded-full" />
                Make your profile more engaging
              </li>
            </ul>
          </div>
        </CardContent>
      </Card>

      {/* App Introduction */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <User className="h-5 w-5" />
            What You Can Do with PadelGo
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <h4 className="font-medium flex items-center gap-2">
                🏟️ Find Courts & Games
              </h4>
              <p className="text-sm text-muted-foreground">
                Discover courts near you and join games with players of your skill level.
              </p>
            </div>
            
            <div className="space-y-2">
              <h4 className="font-medium flex items-center gap-2">
                🏆 Compete in Tournaments
              </h4>
              <p className="text-sm text-muted-foreground">
                Participate in tournaments and climb the leaderboards in your skill category.
              </p>
            </div>
            
            <div className="space-y-2">
              <h4 className="font-medium flex items-center gap-2">
                👥 Build Your Network
              </h4>
              <p className="text-sm text-muted-foreground">
                Connect with other players, form teams, and grow your padel community.
              </p>
            </div>
            
            <div className="space-y-2">
              <h4 className="font-medium flex items-center gap-2">
                📊 Track Your Progress
              </h4>
              <p className="text-sm text-muted-foreground">
                Monitor your ELO rating, game history, and improvement over time.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Setup Preview */}
      <Card className="bg-gradient-to-r from-primary/5 to-transparent border-primary/20">
        <CardContent className="pt-6">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 text-primary">
              <Clock className="h-5 w-5" />
              <span className="font-medium">Quick Setup</span>
            </div>
            <div className="flex-1 text-sm text-muted-foreground">
              Just a few more steps to complete your profile and start playing!
            </div>
          </div>
          
          <div className="mt-4 flex items-center gap-2 text-sm text-muted-foreground">
            <span>Next:</span>
            <span className="text-foreground">Choose your playing position</span>
            <ArrowRight className="h-4 w-4" />
          </div>
        </CardContent>
      </Card>

      {/* Navigation */}
      <div className="flex justify-between items-center pt-6">
        <Button variant="outline" onClick={skipStep}>
          Skip for Now
        </Button>
        <Button onClick={nextStep} size="lg">
          Continue Setup
        </Button>
      </div>
    </div>
  );
}