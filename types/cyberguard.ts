export interface Alert {
  incident_id?: string;
  category?: string;
  incident_type?: string;
  title?: string;
  affected_system?: string;
  description?: string;
  severity?: string;
  [key: string]: unknown;
}

export type IncidentAlert = Alert;

export interface HistoricalMatch {
  incident_id: string;
  similarity: number;
  resolution: string;
}

export interface Recommendation {
  resolution_id: string;
  resolution: string;
  response_domain?: string;
  priority?: string;
  rationale?: string;
  response_steps?: string[];
  confidence: number;
  success_rate: number;
  times_used: number;
  successful_resolutions: number;
}

export interface InvestigationResult {
  is_cold_start?: boolean;
  historical_matches: HistoricalMatch[];
  recommendation: Recommendation;
}

export interface FeedbackSubmission {
  incident_id: string;
  resolution_id: string;
  outcome: 'success' | 'failed';
}

export interface FeedbackJsonPayload {
  event_type: 'SOC_ANALYST_FEEDBACK';
  timestamp: string;
  incident_id: string;
  resolution_id: string;
  feedback_outcome: 'success' | 'failed';
  segment_writeback_target: 'Hindsight_Memory_Worker';
}

export interface FeedbackResponse {
  memory_updated: boolean;
  metrics: Pick<Recommendation, 'times_used' | 'success_rate' | 'successful_resolutions'>;
  historical_matches?: HistoricalMatch[];
}