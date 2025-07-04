import React from 'react';
import { render, fireEvent, waitFor, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import ProfilePictureUpload from './ProfilePictureUpload';
import { useAuth } from '@/contexts/AuthContext';
import { toast } from 'sonner';

// Mock the useAuth hook
jest.mock('@/contexts/AuthContext', () => ({
  useAuth: jest.fn(),
}));

// Mock sonner
jest.mock('sonner', () => ({
  toast: {
    success: jest.fn(),
    error: jest.fn(),
  },
}));

global.fetch = jest.fn() as jest.MockedFunction<typeof fetch>;

describe('ProfilePictureUpload', () => {
  const mockUseAuth = useAuth as jest.Mock;
  const mockFetch = global.fetch as jest.MockedFunction<typeof fetch>;

  beforeEach(() => {
    // Reset mocks before each test
    mockUseAuth.mockReturnValue({
      user: { email: 'test@example.com', profile_picture_url: '' },
      accessToken: 'fake-token',
    });
    mockFetch.mockClear();
    jest.clearAllMocks();
  });

  it('renders correctly', () => {
    render(<ProfilePictureUpload />);
    expect(screen.getByText('Profile Picture')).toBeInTheDocument();
    expect(screen.getByText('Select Image')).toBeInTheDocument();
  });

  it('allows a user to select a file', () => {
    render(<ProfilePictureUpload />);
    const selectButton = screen.getByText('Select Image');
    const fileInput = selectButton.parentElement?.querySelector('input[type="file"]') as HTMLInputElement;
    const file = new File(['(⌐□_□)'], 'chucknorris.png', { type: 'image/png' });

    fireEvent.change(fileInput, { target: { files: [file] } });

    expect(screen.getByText('Selected: chucknorris.png')).toBeInTheDocument();
  });

  it('shows an error for invalid file type', () => {
    render(<ProfilePictureUpload />);
    const selectButton = screen.getByText('Select Image');
    const fileInput = selectButton.parentElement?.querySelector('input[type="file"]') as HTMLInputElement;
    const file = new File(['just text'], 'test.txt', { type: 'text/plain' });

    fireEvent.change(fileInput, { target: { files: [file] } });

    expect(screen.getByText('Invalid file type. Please select an image.')).toBeInTheDocument();
  });

  it('handles successful upload', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ profile_picture_url: 'http://new-image.jpg' }),
    } as Response);

    const mockOnUploadSuccess = jest.fn();
    render(<ProfilePictureUpload onUploadSuccess={mockOnUploadSuccess} />);
    
    const selectButton = screen.getByText('Select Image');
    const fileInput = selectButton.parentElement?.querySelector('input[type="file"]') as HTMLInputElement;
    const file = new File(['(⌐□_□)'], 'chucknorris.png', { type: 'image/png' });
    fireEvent.change(fileInput, { target: { files: [file] } });

    fireEvent.click(screen.getByText('Upload New Picture'));

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledTimes(1);
      expect(mockOnUploadSuccess).toHaveBeenCalledWith('http://new-image.jpg');
      expect(toast.success).toHaveBeenCalledWith('Profile picture updated successfully!');
    });
  });

  it('handles failed upload', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      json: () => Promise.resolve({ detail: 'Upload failed' }),
    } as Response);

    render(<ProfilePictureUpload />);
    
    const selectButton = screen.getByText('Select Image');
    const fileInput = selectButton.parentElement?.querySelector('input[type="file"]') as HTMLInputElement;
    const file = new File(['(⌐□_□)'], 'chucknorris.png', { type: 'image/png' });
    fireEvent.change(fileInput, { target: { files: [file] } });

    fireEvent.click(screen.getByText('Upload New Picture'));

    await waitFor(() => {
      expect(screen.getByText('Upload failed')).toBeInTheDocument();
      expect(toast.error).toHaveBeenCalledWith('Upload failed');
    });
  });
}); 