import React from 'react';
import { render, fireEvent, waitFor, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { EditClubForm } from './EditClubForm';
import { Club } from '@/lib/types';
import { apiClient } from '@/lib/api';
import { getCookie } from 'cookies-next';

// Mocks
jest.mock('@/lib/api', () => ({
  apiClient: {
    put: jest.fn(),
  },
}));
jest.mock('cookies-next', () => ({
  getCookie: jest.fn(),
}));
jest.mock('next/navigation', () => ({
    useRouter: () => ({
      refresh: jest.fn(),
    }),
  }));
global.fetch = jest.fn();

const mockClub: Club = {
  id: 1,
  name: 'Test Club',
  description: 'A club for testing',
  address: '123 Test St',
  city: 'Testville',
  postal_code: '12345',
  phone: '555-555-5555',
  email: 'test@club.com',
  website: 'https://testclub.com',
  image_url: '/images/test.jpg',
  operationalHours: {},
  owner_id: 1,
};

describe('EditClubForm', () => {
  const mockGetCookie = getCookie as jest.Mock;
  const mockFetch = global.fetch as jest.Mock;

  beforeEach(() => {
    mockGetCookie.mockReturnValue('fake-token');
    mockFetch.mockClear();
    jest.clearAllMocks();
  });

  it('renders correctly with club data', () => {
    render(<EditClubForm club={mockClub} />);
    expect(screen.getByLabelText('Club Name*')).toHaveValue(mockClub.name);
    expect(screen.getByLabelText('Description')).toHaveValue(mockClub.description);
  });

  it('handles image upload successfully', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ success: true }),
    });
    
    render(<EditClubForm club={mockClub} />);

    const file = new File(['(⌐□_□)'], 'new-image.png', { type: 'image/png' });
    const uploader = screen.getByLabelText('Upload New Image');
    const input = uploader.querySelector('input[type="file"]') as HTMLInputElement;

    fireEvent.change(input, { target: { files: [file] } });

    await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledTimes(1);
    });
  });
}); 