"use client"; // ProfilePage likely needs to be a client component if it uses hooks or interactivity later

import React, { useState, useEffect } from 'react'; // Added useState, useEffect
import { Button } from "@workspace/ui/components/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@workspace/ui/components/card";
import { Input } from "@workspace/ui/components/input"; // Keep for potential future edit form
import { Label } from "@workspace/ui/components/label";
import withAuth from "@/components/auth/withAuth"; // Import the withAuth HOC
import { useAuth } from "@/contexts/AuthContext"; // Import useAuth to access user data
import ProfilePictureUpload from '@/components/profile/ProfilePictureUpload'; // Import the new component
import { toast } from "sonner"; // Import toast
import Image from 'next/image';
import { Avatar, AvatarFallback, AvatarImage } from "@workspace/ui/components/avatar";
import { Loader2 } from 'lucide-react';

function UserProfilePage() {
    const { user, isLoading } = useAuth();

    if (isLoading) {
        return <div className="flex justify-center items-center h-screen"><Loader2 className="h-16 w-16 animate-spin" /></div>;
    }

    if (!user) {
        return (
            <div className="flex justify-center items-center h-screen">
                <p>Could not load user profile. Please try logging in again.</p>
            </div>
        );
    }

    return (
        <div className="max-w-2xl mx-auto py-10 px-4">
            <Card>
                <CardHeader className="text-center">
                    <Avatar className="w-24 h-24 mx-auto mb-4">
                        <AvatarImage src={user.profile_picture_url || ''} alt={user.name || 'User'} />
                        <AvatarFallback>{user.name?.charAt(0).toUpperCase() || 'U'}</AvatarFallback>
                    </Avatar>
                    <CardTitle className="text-2xl">{user.name || 'Padel Player'}</CardTitle>
                    <CardDescription>{user.email}</CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                    <div className="text-center">
                        <Button variant="outline">Edit Profile</Button>
                    </div>
                    <div>
                        <h3 className="text-lg font-semibold mb-2">My Bookings</h3>
                        <div className="p-4 border rounded-lg text-center text-muted-foreground">
                            <p>Upcoming bookings will be displayed here.</p>
                        </div>
                    </div>
                    <div>
                        <h3 className="text-lg font-semibold mb-2">My Games</h3>
                        <div className="p-4 border rounded-lg text-center text-muted-foreground">
                            <p>Recent and upcoming games will be shown here.</p>
                        </div>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}

export default withAuth(UserProfilePage); 