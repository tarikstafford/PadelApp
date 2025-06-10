"use client";

import { useState } from "react";
import { Upload, X } from "lucide-react";
import { Button } from "@workspace/ui/components/button";
import { toast } from "sonner";
import { getCookie } from "cookies-next";

interface ImageUploaderProps {
  value: string | null | undefined;
  onChange: (url: string | null) => void;
  label?: string;
  maxSizeMB?: number;
}

export function ImageUploader({ 
  value, 
  onChange, 
  label = "Upload Image", 
  maxSizeMB = 5,
}: ImageUploaderProps) {
  const [isUploading, setIsUploading] = useState(false);
  
  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    
    if (file.size > maxSizeMB * 1024 * 1024) {
      toast.error(`File too large. Maximum file size is ${maxSizeMB}MB`);
      return;
    }
    
    if (!file.type.startsWith('image/')) {
      toast.error("Invalid file type. Please upload an image file");
      return;
    }

    const token = getCookie("token");
    if (!token) {
      toast.error("Authentication token not found. Please log in again.");
      return;
    }
    
    setIsUploading(true);
    
    const formData = new FormData();
    formData.append("file", file);

    try {
      const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
      const response = await fetch(`${apiBaseUrl}/api/v1/admin/my-club/profile-picture`, {
        method: "POST",
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Upload failed.");
      }
      
      // The backend returns the full club schema, which includes the new image_url
      onChange(data.image_url);
      toast.success("Image uploaded successfully");
    } catch (error: any) {
      console.error('Upload error:', error);
      toast.error(error.message || "Upload failed. There was an error uploading your image");
    } finally {
      setIsUploading(false);
    }
  };
  
  const handleRemove = () => {
    onChange(null);
  };
  
  return (
    <div className="space-y-2">
      <p className="text-sm font-medium">{label}</p>
      
      {value ? (
        <div className="relative w-full h-48 bg-muted rounded-md overflow-hidden">
          <img 
            src={value} 
            alt="Uploaded image" 
            className="w-full h-full object-cover"
          />
          <Button
            variant="destructive"
            size="icon"
            className="absolute top-2 right-2"
            onClick={handleRemove}
          >
            <X className="h-4 w-4" />
          </Button>
        </div>
      ) : (
        <label className="flex flex-col items-center justify-center w-full h-32 bg-muted hover:bg-muted/80 rounded-md border-2 border-dashed border-muted-foreground/50 cursor-pointer">
          <div className="flex flex-col items-center justify-center pt-5 pb-6">
            <Upload className="w-8 h-8 mb-2 text-muted-foreground" />
            <p className="mb-2 text-sm text-muted-foreground">
              <span className="font-semibold">Click to upload</span> or drag and drop
            </p>
            <p className="text-xs text-muted-foreground">
              PNG, JPG or WEBP (max. {maxSizeMB}MB)
            </p>
          </div>
          <input
            type="file"
            className="hidden"
            accept="image/*"
            onChange={handleFileChange}
            disabled={isUploading}
          />
        </label>
      )}
      
      {isUploading && (
        <div className="w-full bg-muted rounded-full h-2.5">
          <div className="bg-primary h-2.5 rounded-full animate-pulse w-full"></div>
        </div>
      )}
    </div>
  );
} 