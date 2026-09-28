import type {
  Alert,
  FeedbackJsonPayload,
  FeedbackResponse,
  FeedbackSubmission,
  InvestigationResult,
} from '@/types/cyberguard';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000/api';

export async function investigateAlert(
  alert: Alert | string,
  source: 'PRESET_SELECTION' | 'RAW_SYSLOG_WEBHOOK' = 'PRESET_SELECTION'
): Promise<InvestigationResult> {
  const response = await fetch(`${API_BASE_URL}/investigate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ raw_input: alert, source }),
  });

  if (!response.ok) {
    throw new Error(`Investigation failed with status ${response.status}`);
  }

  return response.json();
}

export async function submitFeedback(submission: FeedbackSubmission): Promise<FeedbackResponse> {
  const payload: FeedbackJsonPayload = {
    event_type: 'SOC_ANALYST_FEEDBACK',
    timestamp: new Date().toISOString(),
    incident_id: submission.incident_id,
    resolution_id: submission.resolution_id,
    feedback_outcome: submission.outcome,
    segment_writeback_target: 'Hindsight_Memory_Worker',
  };

  const response = await fetch(`${API_BASE_URL}/feedback`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`Feedback submission failed with status ${response.status}`);
  }

  return response.json();
}