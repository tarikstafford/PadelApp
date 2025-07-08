"use client";

import { useState } from 'react';
import { Input } from '@workspace/ui/components/input';
import { Label } from '@workspace/ui/components/label';
import { Button } from '@workspace/ui/components/button';
import { ImageIcon, X } from 'lucide-react';

interface ImageUploaderProps {
  onFileChange: (file: File | null) => void;
  defaultImageUrl?: string | null;
}

export default function ImageUploader({ onFileChange, defaultImageUrl }: ImageUploaderProps) {
  const [preview, setPreview] = useState<string | null>(defaultImageUrl || null);
  const [fileName, setFileName] = useState<string | null>(defaultImageUrl ? 'Current image' : null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setPreview(URL.createObjectURL(file));
      setFileName(file.name);
      onFileChange(file);
    } else {
      handleRemoveImage();
    }
  };

  const handleRemoveImage = () => {
    setPreview(null);
    setFileName(null);
    onFileChange(null);
    // Reset the file input
    const input = document.getElementById('image-upload') as HTMLInputElement;
    if (input) {
      input.value = '';
    }
  };

  return (
    <div className="space-y-4">
      <Label htmlFor="image-upload">Club Image</Label>
      <div className="flex items-center space-x-4">
        <div className="relative h-24 w-24 rounded-md bg-muted flex items-center justify-center">
          {preview ? (
            <>
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src={preview} alt="Club image preview" className="h-full w-full rounded-md object-cover" />
              <Button
                type="button"
                variant="destructive"
                size="icon"
                className="absolute -top-2 -right-2 h-6 w-6 rounded-full"
                onClick={handleRemoveImage}
              >
                <X className="h-4 w-4" />
              </Button>
            </>
          ) : (
            <ImageIcon className="h-10 w-10 text-muted-foreground" />
          )}
        </div>
        <div className="flex flex-col space-y-2">
          <Input id="image-upload" type="file" accept="image/*" onChange={handleFileChange} className="hidden" />
          <Label
            htmlFor="image-upload"
            className="cursor-pointer inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2"
          >
            {preview ? 'Change Image' : 'Upload Image'}
          </Label>
          {fileName && <span className="text-sm text-muted-foreground">{fileName}</span>}
        </div>
      </div>
    </div>
  );
} 