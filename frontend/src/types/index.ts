export interface Athlete {
  id: string;
  user_id: string | null;
  first_name: string;
  last_name: string;
  display_name: string;
  date_of_birth: string | null;
  gender: string;
  country: string | null;
  country_code: string | null;
  city: string | null;
  photo_url: string | null;
  bio: string | null;
  sport_id: string | null;
  weight_class_id: string | null;
  belt_rank_id: string | null;
  years_training: number | null;
  gym_id: string | null;
  elo_rating: number;
  peak_rating: number;
  gi_rating: number;
  nogi_rating: number;
  total_matches: number;
  wins: number;
  losses: number;
  draws: number;
  submissions: number;
  competitor_points: number;
  is_active: boolean;
  is_verified: boolean;
  is_claimed: boolean;
  created_at: string;
}

export interface AthleteListItem {
  id: string;
  display_name: string;
  country: string | null;
  country_code: string | null;
  gender: string;
  elo_rating: number;
  total_matches: number;
  wins: number;
  losses: number;
  photo_url: string | null;
  is_verified: boolean;
}

export interface LeaderboardEntry {
  rank: number;
  athlete_id: string;
  display_name: string;
  country: string | null;
  country_code: string | null;
  gender: string;
  elo_rating: number;
  total_matches: number;
  wins: number;
  losses: number;
  win_rate: number;
  photo_url: string | null;
  gym_name: string | null;
  belt_rank: string | null;
  rating_change_7d: number | null;
  rating_change_30d: number | null;
}

export interface LeaderboardResponse {
  entries: LeaderboardEntry[];
  total_count: number;
  page: number;
  page_size: number;
  filters_applied: Record<string, string>;
}

export interface Event {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  sport_id: string | null;
  organizer: string | null;
  tier: string;
  event_date: string;
  end_date: string | null;
  venue: string | null;
  city: string | null;
  country: string | null;
  country_code: string | null;
  is_gi: boolean;
  is_nogi: boolean;
  cp_multiplier: number;
  k_factor_multiplier: number;
  source: string | null;
  is_published: boolean;
  matches_imported: boolean;
  created_at: string;
}

export interface Gym {
  id: string;
  owner_id: string | null;
  name: string;
  slug: string;
  description: string | null;
  logo_url: string | null;
  website: string | null;
  address: string | null;
  city: string | null;
  state: string | null;
  country: string | null;
  country_code: string | null;
  member_count: number;
  avg_rating: number;
  is_verified: boolean;
  is_active: boolean;
  created_at: string;
}

export interface Post {
  id: string;
  author_id: string;
  author_name: string | null;
  author_avatar: string | null;
  post_type: string;
  content: string;
  media_urls: string[] | null;
  hashtags: string[] | null;
  event_id: string | null;
  match_id: string | null;
  like_count: number;
  comment_count: number;
  is_liked: boolean;
  created_at: string;
  updated_at: string;
}

export interface Match {
  id: string;
  event_id: string;
  winner_id: string;
  loser_id: string;
  outcome: string;
  is_draw: boolean;
  submission_type: string | null;
  winner_score: number | null;
  loser_score: number | null;
  is_gi: boolean;
  round_name: string | null;
  winner_elo_before: number | null;
  winner_elo_after: number | null;
  loser_elo_before: number | null;
  loser_elo_after: number | null;
  elo_change: number | null;
  created_at: string;
}

export interface RatingPoint {
  rating_before: number;
  rating_after: number;
  rating_change: number;
  recorded_at: string;
}

export interface DashboardStats {
  total_athletes: number;
  total_gyms: number;
  total_events: number;
  total_matches: number;
  total_users: number;
  total_posts: number;
}
