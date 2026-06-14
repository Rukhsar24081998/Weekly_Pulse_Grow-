export type ArtifactFlags = Record<string, boolean>;

export type HealthResponse = {
  status: string;
  service: string;
  product: string;
  artifacts: ArtifactFlags;
};

export type PulseTheme = {
  rank: number;
  theme_id: string;
  label: string;
  summary: string;
  review_count: number;
  avg_rating: number;
};

export type PulseQuote = {
  theme_id: string;
  text: string;
  rating: number;
  store: string;
};

export type PulseAction = {
  theme_id: string;
  action: string;
  rationale: string;
};

export type PulsePayload = {
  product: string;
  week_ending: string;
  review_window_weeks: number;
  window_start: string;
  window_end: string;
  total_reviews: number;
  sample_size: number;
  top_themes: PulseTheme[];
  quotes: PulseQuote[];
  action_ideas: PulseAction[];
  word_count: number;
  validation_passed: boolean;
  markdown: string;
};

export type PulseLatestResponse = {
  pulse: PulsePayload;
  markdown: string;
  paths: { json: string; markdown: string | null };
  validation: { passed: boolean; errors: string[] };
};

export type StatusResponse = {
  product: string;
  artifacts: ArtifactFlags;
  phases_dir: string;
  reviews?: {
    total?: number;
    app_store?: number;
    play_store?: number;
    window?: { start?: string; end?: string };
  };
  pulse_summary?: {
    week_ending?: string;
    word_count?: number;
    validation_passed?: boolean;
  };
  last_publish?: {
    google_doc_url?: string;
    gmail_draft_id?: string;
    week_ending?: string;
  };
  doc?: {
    google_doc_url?: string;
    google_doc_id?: string;
  };
};
