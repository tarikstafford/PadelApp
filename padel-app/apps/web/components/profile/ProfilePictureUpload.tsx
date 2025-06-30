"use client";

import React, { useState, useRef } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@workspace/ui/components/button';
// import { Input } from '@workspace/ui/components/input'; // For file input styling if needed, or just use native
import { Label } from '@workspace/ui/components/label';
import { toast } from 'sonner'; // Import toast

interface ProfilePictureUploadProps {
  onUploadSuccess?: (newImageUrl: string) => void; // Callback for when upload is successful (in future)
}

export default function ProfilePictureUpload({ onUploadSuccess }: ProfilePictureUploadProps) {
  const { user, accessToken } = useAuth();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const currentProfilePic = user?.profile_picture_url || `https://avatar.vercel.sh/${user?.email || 'default'}?s=96`;

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setError(null);
    const file = event.target.files?.[0];
    if (file) {
      if (!file.type.startsWith('image/')) {
        setError("Invalid file type. Please select an image.");
        setSelectedFile(null);
        setPreviewUrl(null);
        return;
      }
      // Limit file size (e.g., 2MB)
      if (file.size > 2 * 1024 * 1024) {
        setError("File is too large. Maximum size is 2MB.");
        setSelectedFile(null);
        setPreviewUrl(null);
        return;
      }
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setError("No file selected to upload.");
      return;
    }
    if (!accessToken) {
      toast.error("Authentication token not found. Please log in again.");
      setError("Authentication token not found. Please log in again.");
      return;
    }

    setIsLoading(true);
    setError(null);
    
    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiBaseUrl}/api/v1/users/me/profile-picture`, {
        method: "POST",
        headers: { 'Authorization': `Bearer ${accessToken}` }, // No Content-Type for FormData, browser sets it
        body: formData,
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || "Profile picture upload failed.");
      }
      
      console.log("Upload successful:", data);
      toast.success("Profile picture updated successfully!");
      if (onUploadSuccess && data.profile_picture_url) {
        onUploadSuccess(data.profile_picture_url);
      }
      setSelectedFile(null);
      setPreviewUrl(null);
      // TODO: Add success toast notification here
      alert("Profile picture updated!"); // Placeholder

    } catch (err: any) {
      console.error("Profile picture upload error:", err);
      toast.error(err.message || "An error occurred during upload.");
      setError(err.message || "An error occurred during upload.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-4 flex flex-col items-center text-center">
      <Label>Profile Picture</Label>
      <div className="flex flex-col items-center space-y-2">
        <img 
          src={previewUrl || currentProfilePic} 
          alt="Profile" 
          className="w-24 h-24 rounded-full border object-cover bg-muted"
        />
        <Button 
          type="button" 
          variant="outline" 
          onClick={() => fileInputRef.current?.click()}
          disabled={isLoading}
        >
          {selectedFile ? "Change Image" : "Select Image"}
        </Button>
        <input 
          type="file" 
          accept="image/*" 
          ref={fileInputRef} 
          onChange={handleFileChange} 
          className="hidden" 
        />
      </div>
      {selectedFile && previewUrl && (
        <div className="space-y-2 mt-2">
          <p className="text-sm text-muted-foreground">Selected: {selectedFile.name}</p>
          <Button 
            type="button" 
            onClick={handleUpload} 
            disabled={isLoading || !selectedFile}
          >
            {isLoading ? "Uploading..." : "Upload New Picture"}
          </Button>
        </div>
      )}
      {error && <p className="text-sm text-destructive mt-1">{error}</p>}
    </div>
  );
} 