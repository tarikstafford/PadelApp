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
  club_id?: number;
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
  opening_time: string | null;
  closing_time: string | null;
  amenities?: string;
  image_url?: string;
  website?: string;
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
  status: "invited" | "accepted";
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

// Tournament types
export enum TournamentType {
  SINGLE_ELIMINATION = "SINGLE_ELIMINATION",
  DOUBLE_ELIMINATION = "DOUBLE_ELIMINATION",
  AMERICANO = "AMERICANO",
  FIXED_AMERICANO = "FIXED_AMERICANO",
}

export enum TournamentStatus {
  DRAFT = "DRAFT",
  REGISTRATION_OPEN = "REGISTRATION_OPEN",
  REGISTRATION_CLOSED = "REGISTRATION_CLOSED",
  IN_PROGRESS = "IN_PROGRESS",
  COMPLETED = "COMPLETED",
  CANCELLED = "CANCELLED",
}

export enum TournamentCategory {
  BRONZE = "BRONZE",
  SILVER = "SILVER",
  GOLD = "GOLD",
  PLATINUM = "PLATINUM",
}

export enum RecurrencePattern {
  DAILY = "DAILY",
  WEEKLY = "WEEKLY",
  MONTHLY = "MONTHLY",
}

export enum MatchStatus {
  PENDING = "PENDING",
  IN_PROGRESS = "IN_PROGRESS",
  COMPLETED = "COMPLETED",
  CANCELLED = "CANCELLED",
  POSTPONED = "POSTPONED",
}

export type TournamentCategoryTemplate = {
  id: number;
  category: TournamentCategory;
  max_participants: number;
  min_elo: number;
  max_elo: number;
};

export type TournamentCategoryResponse = {
  id: number;
  category: TournamentCategory;
  max_participants: number;
  min_elo: number;
  max_elo: number;
  current_participants: number;
  current_teams: number;
  current_individuals: number;
};

export type Tournament = {
  id: number;
  club_id: number;
  name: string;
  description?: string;
  tournament_type: TournamentType;
  start_date: string;
  end_date: string;
  registration_deadline: string;
  status: TournamentStatus;
  max_participants: number;
  entry_fee: number;
  created_at: string;
  updated_at: string;
  categories: TournamentCategoryResponse[];
  total_registered_teams: number;
  total_registered_participants: number;
  requires_teams: boolean;
};

export type RecurringTournament = {
  id: number;
  club_id: number;
  series_name: string;
  description?: string;
  recurrence_pattern: RecurrencePattern;
  interval_value: number;
  days_of_week?: number[];
  day_of_month?: number;
  series_start_date: string;
  series_end_date?: string;
  tournament_type: TournamentType;
  duration_hours: number;
  registration_deadline_hours: number;
  max_participants: number;
  entry_fee: number;
  advance_generation_days: number;
  auto_generation_enabled: boolean;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  category_templates: TournamentCategoryTemplate[];
  total_instances: number;
  upcoming_instances: number;
};

export type TournamentRegistration = {
  id: number;
  tournament_id: number;
  category: TournamentCategory;
  team_id?: number;
  user_id?: number;
  seed?: number;
  registration_date: string;
  is_active: boolean;
};

export type TournamentMatch = {
  id: number;
  tournament_id: number;
  category: TournamentCategory;
  team1_id?: number;
  team2_id?: number;
  team1_name?: string;
  team2_name?: string;
  round_number: number;
  match_number: number;
  scheduled_time?: string;
  court_id?: number;
  court_name?: string;
  status: MatchStatus;
  winning_team_id?: number;
  team1_score?: number;
  team2_score?: number;
  winner_advances_to_match_id?: number;
  loser_advances_to_match_id?: number;
};

export type HourlyTimeSlot = {
  start_time: string;
  end_time: string;
  day_of_week: number;
  hour: number;
};

export type TournamentScheduleRequest = {
  tournament_id: number;
  time_slots: HourlyTimeSlot[];
  court_ids: number[];
  auto_schedule?: boolean;
};

export type TournamentCreateData = {
  name: string;
  description?: string;
  tournament_type: TournamentType;
  start_date: string;
  end_date: string;
  registration_deadline: string;
  entry_fee: number;
  categories: {
    category: TournamentCategory;
    max_participants: number;
  }[];
  court_ids: number[];
};

export type RecurringTournamentCreateData = {
  series_name: string;
  description?: string;
  recurrence_pattern: RecurrencePattern;
  interval_value: number;
  days_of_week?: number[];
  day_of_month?: number;
  series_start_date: string;
  series_end_date?: string;
  tournament_type: TournamentType;
  duration_hours: number;
  registration_deadline_hours: number;
  max_participants: number;
  entry_fee: number;
  advance_generation_days: number;
  auto_generation_enabled: boolean;
  category_templates: {
    category: TournamentCategory;
    max_participants: number;
    min_elo: number;
    max_elo: number;
  }[];
};

export type TournamentTeam = {
  id: number;
  team_id: number;
  team_name: string;
  category: TournamentCategory;
  seed?: number;
  average_elo: number;
  registration_date: string;
  is_active: boolean;
  players: User[];
};

export type TournamentParticipant = {
  id: number;
  user_id: number;
  user_name: string;
  user_email: string;
  category: TournamentCategory;
  seed?: number;
  elo_rating: number;
  registration_date: string;
  is_active: boolean;
  match_teams?: any; // Temporary team assignments for Americano
}; 