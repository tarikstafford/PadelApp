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
import { apiClient } from "@/lib/api";
import { EloAdjustmentRequest } from "@/lib/types";
import { EloAdjustmentRequestModal } from "@/components/profile/EloAdjustmentRequestModal";
import { EloRatingDisplay } from "@/components/profile/EloRatingDisplay";
import { PreferredPositionSelection } from "@/components/profile/PreferredPositionSelection";
import { EloAdjustmentRequestHistory } from "@/components/profile/EloAdjustmentRequestHistory";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '';

function UserProfilePage() {
    const { user, isLoading, accessToken, fetchUser } = useAuth();
    const [isEditing, setIsEditing] = useState(false);
    const [formData, setFormData] = useState({ name: '', email: '' });
    const [requests, setRequests] = useState<EloAdjustmentRequest[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (user && accessToken) {
            setFormData({ name: user.full_name || '', email: user.email || '' });
            apiClient
                .get<EloAdjustmentRequest[]>("/users/me/elo-adjustment-requests", undefined, accessToken)
                .then((data) => {
                    setRequests(data);
                })
                .catch((error) => {
                    console.error("Failed to fetch ELO adjustment requests", error);
                })
                .finally(() => {
                    setLoading(false);
                });
        }
    }, [user, accessToken]);

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

    const handleUploadSuccess = () => {
        toast.success("Profile picture updated!");
        fetchUser();
    };

    const canMakeRequest = () => {
        if (requests.some(req => req.status === 'pending')) {
            return false;
        }
        const thirtyDaysAgo = new Date();
        thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
        const recentRequest = requests.find(req => new Date(req.created_at) > thirtyDaysAgo);
        return !recentRequest;
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
        <div className="container mx-auto p-4">
            <div className="flex items-center space-x-4 mb-8">
                <ProfilePictureUpload onUploadSuccess={handleUploadSuccess} />
                <div>
                    <h1 className="text-3xl font-bold">{user.full_name}</h1>
                    <p className="text-gray-500">{user.email}</p>
                </div>
            </div>

            <div className="space-y-8">
                <div>
                    <h2 className="text-xl font-bold mb-4">Padel Details</h2>
                    <div className="space-y-4">
                        <EloRatingDisplay eloRating={user.elo_rating} />
                        <div>
                            <h3 className="text-lg font-bold">Preferred Position</h3>
                            <PreferredPositionSelection />
                        </div>
                        <EloAdjustmentRequestModal canMakeRequest={canMakeRequest()} />
                    </div>
                </div>
                <EloAdjustmentRequestHistory requests={requests} loading={loading} />
            </div>
        </div>
    );
}

export default withAuth(UserProfilePage); 