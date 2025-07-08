"use client";

import { useState } from "react";
import { Upload, X } from "lucide-react";
import { Button } from "@workspace/ui/components/button";
import { toast } from "sonner";

interface ImageUploaderProps {
  onFileSelect: (file: File | null) => void;
  label?: string;
  maxSizeMB?: number;
}

export function ImageUploader({ 
  onFileSelect, 
  label = "Upload Image", 
  maxSizeMB = 5 
}: ImageUploaderProps) {
  const [preview, setPreview] = useState<string | null>(null);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) {
      onFileSelect(null);
      setPreview(null);
      return;
    }
    
    if (file.size > maxSizeMB * 1024 * 1024) {
      toast.error(`File too large. Maximum file size is ${maxSizeMB}MB`);
      onFileSelect(null);
      setPreview(null);
      return;
    }
    
    if (!file.type.startsWith('image/')) {
      toast.error("Invalid file type. Please upload an image file");
      onFileSelect(null);
      setPreview(null);
      return;
    }
    
    onFileSelect(file);
    setPreview(URL.createObjectURL(file));
  };
  
  const handleRemove = () => {
    onFileSelect(null);
    setPreview(null);
  };
  
  return (
    <div className="space-y-2">
      <p className="text-sm font-medium">{label}</p>
      
      {preview ? (
        <div className="relative w-full h-48 bg-muted rounded-md overflow-hidden">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img 
            src={preview} 
            alt="Uploaded image preview" 
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
          />
        </label>
      )}
    </div>
  );
} 