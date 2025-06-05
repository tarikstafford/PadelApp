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

function ProfilePage() { // Changed to a named function for HOC
  const { user, accessToken, fetchAndUpdateUser } = useAuth(); // Added accessToken
  const [isEditing, setIsEditing] = useState(false);
  const [name, setName] = useState(user?.name || "");
  const [email, setEmail] = useState(user?.email || "");
  const [formError, setFormError] = useState(""); // Renamed from error to avoid conflict with toast.error
  const [isSaving, setIsSaving] = useState(false); // For save operation loading state

  // Effect to update form fields if user context changes (e.g., after initial load)
  useEffect(() => {
    if (user) {
      setName(user.name || "");
      setEmail(user.email || "");
    }
  }, [user]);

  // Display loading or placeholder if user data isn't available yet
  // The withAuth HOC already handles the main loading and redirect, 
  // but user might be null briefly after redirect if context is still settling.
  if (!user) {
    return <p>Loading profile...</p>; // Or a more sophisticated loading state
  }

  const handleEditToggle = () => {
    setIsEditing(!isEditing);
    // Reset form fields to current user data when entering edit mode or cancelling
    if (!isEditing) {
      setName(user.name || "");
      setEmail(user.email || "");
    }
    setFormError(""); // Clear errors when toggling edit mode
  };

  const handleSaveChanges = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setFormError("");
    if (!name.trim() || !email.trim()) {
      setFormError("Name and email cannot be empty.");
      return;
    }
    // Basic email validation regex
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      setFormError("Please enter a valid email address.");
      return;
    }
    setIsSaving(true);
    try {
      const response = await fetch("/api/v1/auth/users/me", {
        method: "PUT",
        headers: { 
          "Content-Type": "application/json",
          "Authorization": `Bearer ${accessToken}` 
        },
        body: JSON.stringify({ name, email }),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Failed to update profile.");
      }
      await fetchAndUpdateUser(); // Refresh user data from context
      setIsEditing(false);
      toast.success("Profile updated successfully!"); // Use toast for success
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : "An unexpected error occurred.";
      console.error("Error updating profile:", error);
      setFormError(message);
      toast.error(message);
    } finally {
      setIsSaving(false);
    }
  };

  const handleProfilePictureUploadSuccess = (newImageUrl: string) => {
    console.log("Profile picture upload succeeded, new URL reported by component:", newImageUrl);
    fetchAndUpdateUser(); // Refresh user data from context
  };

  // Profile picture URL (can be expanded in Subtask 5.4)
  // const profilePictureDisplayUrl = user.profile_picture_url || `https://avatar.vercel.sh/${user.email}?s=96`; // REMOVED as it's unused

  return (
    <div className="space-y-8 max-w-2xl mx-auto">
      <header className="mb-6 flex justify-between items-center">
        <h1 className="text-3xl font-bold tracking-tight">My Profile</h1>
        {!isEditing && (
          <Button variant="outline" onClick={handleEditToggle} disabled={isSaving}>Edit Profile</Button>
        )}
      </header>
      
      <Card>
        <CardHeader className="pb-4">
          <div className="flex flex-col md:flex-row items-center gap-6">
            <ProfilePictureUpload onUploadSuccess={handleProfilePictureUploadSuccess} />
            {/* Display Name and Email next to picture or below, depending on screen size */}
            <div className="text-center md:text-left">
              <CardTitle className="text-2xl">{isEditing ? name : user.name || "User Name"}</CardTitle>
              <CardDescription>{isEditing ? email : user.email}</CardDescription>
            </div>
          </div>
        </CardHeader>
        
        <form onSubmit={handleSaveChanges}>
          <CardContent className="space-y-6 pt-4">
            {isEditing ? (
              <>
                <div className="space-y-2">
                  <CardTitle className="text-xl mb-4">Edit Details</CardTitle>
                  <Label htmlFor="name">Name</Label>
                  <Input 
                    id="name" 
                    value={name} 
                    onChange={(e) => setName(e.target.value)} 
                    required 
                    disabled={isSaving}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="email">Email</Label>
                  <Input 
                    id="email" 
                    type="email" 
                    value={email} 
                    onChange={(e) => setEmail(e.target.value)} 
                    required 
                    disabled={isSaving}
                  />
                </div>
                {formError && <p className="text-sm text-destructive mt-2">{formError}</p>}
              </>
            ) : (
              <div className="space-y-2 mt-4">
                <h3 className="text-lg font-medium">Personal Information</h3>
                <div className="grid gap-2 border p-4 rounded-md">
                  <div>
                    <Label className="text-sm font-normal text-muted-foreground">Name</Label>
                    <p className="font-medium">{user.name || "Not set"}</p> 
                  </div>
                  <div>
                    <Label className="text-sm font-normal text-muted-foreground">Email</Label>
                    <p className="font-medium">{user.email}</p>
                  </div>
                </div>
              </div>
            )}
          </CardContent>
          {isEditing && (
            <CardFooter className="border-t pt-6 flex justify-end gap-2">
              <Button variant="outline" type="button" onClick={handleEditToggle} disabled={isSaving}>Cancel</Button> 
              <Button type="submit" disabled={isSaving}>{isSaving ? "Saving..." : "Save Changes"}</Button> 
            </CardFooter>
          )}
        </form>
      </Card>

      {/* Additional sections like "My Activity", "Linked Accounts" could go here as separate Cards */}
    </div>
  );
}

export default withAuth(ProfilePage); // Wrap ProfilePage with withAuth HOC 