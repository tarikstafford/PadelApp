export enum UserRole {
  PLAYER = "player",
  ADMIN = "admin",
  SUPER_ADMIN = "super-admin",
}

export type User = {
  id: number;
  email: string;
  full_name?: string;
  profile_picture_url?: string;
  is_active: boolean;
  role: UserRole;
  elo_rating: number;
  preferred_position?: "LEFT" | "RIGHT";
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
  club?: Club;
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
  game?: Game;
  user: {
    id: number;
    name: string;
    email: string;
  }
};

export type DashboardSummary = {
  total_bookings_today: number;
  occupancy_rate_percent: number;
  recent_activity: {
    game_id: number;
    player_count: number;
    created_at: string;
  }[];
};

export type GamePlayer = {
  id: number;
  status: string;
  user: User;
  elo_rating: number;
};

export type GameTeam = {
  id: number;
  name: string;
  players: GamePlayer[];
};

export type Game = {
  id: number;
  created_at: string;
  players: GamePlayer[];
  team1?: GameTeam;
  team2?: GameTeam;
  winning_team_id?: number;
  result_submitted?: boolean;
  game_type: "PRIVATE" | "PUBLIC" | "FRIENDLY" | "COMPETITIVE";
  booking: Booking;
  skill_level?: string;
};

export type BookingDetails = {
  booking: Booking;
  game?: Game;
};

export type AdminRegistrationData = {
  full_name: string;
  email: string;
  password: string;
};

export type AuthResponse = {
  access_token: string;
  refresh_token: string;
  token_type: string;
  role: string;
};

export type ClubData = {
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
};

export type CourtData = {
  name: string;
  surface_type?: string;
  is_indoor?: boolean;
  price_per_hour?: number;
  club_id: number;
};

export type EloAdjustmentRequest = {
  id: number;
  user_id: number;
  requested_rating: number;
  reason: string;
  status: "pending" | "approved" | "rejected";
  created_at: string;
}; 