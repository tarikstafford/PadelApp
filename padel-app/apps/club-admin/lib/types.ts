export type User = {
  id: number;
  email: string;
  name?: string;
  profile_picture_url?: string;
  is_active: boolean;
  is_admin: boolean;
  role: "PLAYER" | "CLUB_ADMIN";
};

export type Club = {
  id: number;
  name: string;
  address?: string;
  city?: string;
  postal_code?: string;
  phone?: string;
  email?: string;
  description?: string;
  opening_hours?: string;
  amenities?: string;
  image_url?: string;
  website?: string;
  operationalHours?: any;
  owner_id: number;
};

export type Court = {
  id: number;
  name: string;
  surface_type?: "Turf" | "Clay" | "Hard Court" | "Sand";
  is_indoor?: boolean;
  price_per_hour?: number;
  default_availability_status?: "Available" | "Unavailable" | "Maintenance";
  club_id: number;
};

export type Booking = {
  id: number;
  start_time: string;
  end_time: string;
  total_price: number;
  status: "CONFIRMED" | "PENDING" | "CANCELLED";
  notes?: string;
  court_id: number;
  user_id: number;
  court: Court;
  user: {
    id: number;
    name: string;
    email: string;
  }
}; 