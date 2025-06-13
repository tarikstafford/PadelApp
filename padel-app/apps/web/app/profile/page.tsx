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

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '';

function UserProfilePage() {
    const { user, isLoading, accessToken, fetchUser } = useAuth();
    const [isEditing, setIsEditing] = useState(false);
    const [formData, setFormData] = useState({ name: '', email: '' });

    useEffect(() => {
        if (user) {
            setFormData({ name: user.full_name || '', email: user.email || '' });
        }
    }, [user]);

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleSave = async () => {
        if (!accessToken) {
            toast.error("You are not authenticated.");
            return;
        }

        toast.loading("Saving your profile...");
        try {
            const response = await fetch(`${API_BASE_URL}/api/v1/users/me`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${accessToken}`
                },
                body: JSON.stringify({
                    full_name: formData.name,
                    email: formData.email,
                }),
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.detail || "Failed to update profile.");
            }

            toast.success("Profile updated successfully!");
            await fetchUser(); // Re-fetch user data to update the context
            setIsEditing(false); // Exit editing mode
        } catch (error: any) {
            toast.error(error.message || "An unexpected error occurred.");
        }
    };

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
                        <AvatarImage src={user.profile_picture_url || ''} alt={user.full_name || 'User'} />
                        <AvatarFallback>{formData.name?.charAt(0).toUpperCase() || 'U'}</AvatarFallback>
                    </Avatar>
                    {!isEditing ? (
                        <>
                            <CardTitle className="text-2xl">{user.full_name || 'Padel Player'}</CardTitle>
                            <CardDescription>{user.email}</CardDescription>
                        </>
                    ) : (
                        <div className="space-y-4 px-6 py-2">
                             <div className="space-y-2 text-left">
                                <Label htmlFor="name">Full Name</Label>
                                <Input id="name" name="name" value={formData.name} onChange={handleInputChange} />
                            </div>
                            <div className="space-y-2 text-left">
                                <Label htmlFor="email">Email</Label>
                                <Input id="email" name="email" type="email" value={formData.email} onChange={handleInputChange} />
                            </div>
                        </div>
                    )}
                </CardHeader>
                <CardContent className="space-y-6">
                    <div className="text-center">
                        {!isEditing ? (
                            <Button variant="outline" onClick={() => setIsEditing(true)}>Edit Profile</Button>
                        ) : (
                            <div className="flex justify-center gap-4">
                                <Button variant="secondary" onClick={() => setIsEditing(false)}>Cancel</Button>
                                <Button onClick={handleSave}>Save Changes</Button>
                            </div>
                        )}
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