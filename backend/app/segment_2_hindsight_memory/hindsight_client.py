"""
Segment 2: Hindsight Memory Client Service
Interacts with Hindsight Cloud SDK / Vector API to retrieve multi-memory context bundle.
"""
import os
import httpx
from typing import Dict, Any, List
from app.config import settings

# Pre-populated Operational Profiles for Zero-Downtime Fallback & Demo Stability
DEFAULT_RESOLUTION_PROFILES: Dict[str, Dict[str, Any]] = {
    'SSH Brute Force': {
        'resolution_id': 'RES-SSH-001',
        'resolution': 'Throttle SSH authentication attempts, block attacking IPs, and enforce MFA for impacted accounts.',
        'response_domain': 'Identity containment',
        'priority': 'High',
        'rationale': 'Rapid failed SSH logins often indicate automation against privileged access paths.',
        'response_steps': [
            'Rate-limit SSH auth attempts and block the offending source addresses.',
            'Require MFA and reset credentials for any account with repeated failures.',
            'Review successful login events and harden SSH access policy.'
        ],
        'confidence': 0.94,
        'times_used': 18,
        'successful_resolutions': 16,
        'historical_matches': [
            {'incident_id': 'INC-2026-0156', 'similarity': 0.97, 'resolution': 'Throttle login attempts and enforce MFA for impacted SSH accounts.', 'outcome': 'success'},
            {'incident_id': 'INC-2026-0042', 'similarity': 0.91, 'resolution': 'Rate-limit authentication attempts and rotate impacted credentials.', 'outcome': 'success'}
        ]
    },
    'Credential Stuffing': {
        'resolution_id': 'RES-CRED-002',
        'resolution': 'Distribute malicious login traffic with challenge throttling, IP blocking, and customer account verification.',
        'response_domain': 'Access defense',
        'priority': 'Critical',
        'rationale': 'Credential stuffing spreads password spray traffic across customer accounts and can lead to mass account takeover.',
        'response_steps': [
            'Block abusive IP ranges and enforce progressive delay for repeated login failures.',
            'Add step-up verification for suspicious customers and require password resets for high-risk accounts.',
            'Inspect authentication telemetry for a successful takeover pattern.'
        ],
        'confidence': 0.93,
        'times_used': 10,
        'successful_resolutions': 8,
        'historical_matches': [
            {'incident_id': 'INC-2026-0066', 'similarity': 0.96, 'resolution': 'Throttle customer authentication attempts and validate risky accounts.', 'outcome': 'success'},
            {'incident_id': 'INC-2026-0042', 'similarity': 0.90, 'resolution': 'Limit login attempts and reset suspicious credentials.', 'outcome': 'failed'}
        ]
    },
    'Prompt Injection': {
        'resolution_id': 'RES-AI-PI-011',
        'resolution': 'Enforce prompt boundary isolation, strip instruction override tags, and restrict agent tool privileges.',
        'response_domain': 'AI System Defense',
        'priority': 'Critical',
        'rationale': 'Direct or indirect prompt injections manipulate LLM instruction hierarchy to trigger unauthorized actions.',
        'response_steps': [
            'Isolate and sanitize untrusted user inputs with input guardrails.',
            'Revoke high-risk tool execution privileges for compromised agent sessions.',
            'Update system prompts with standard instruction delimiter boundaries.'
        ],
        'confidence': 0.96,
        'times_used': 14,
        'successful_resolutions': 13,
        'historical_matches': [
            {'incident_id': 'INC-2026-0912', 'similarity': 0.98, 'resolution': 'Applied strict input delimiters and disabled bash tool execution.', 'outcome': 'success'},
            {'incident_id': 'INC-2026-0881', 'similarity': 0.92, 'resolution': 'Sanitized incoming prompt payload.', 'outcome': 'success'}
        ]
    },
    'Generic Security Event': {
        'resolution_id': 'RES-ISOLATE-002',
        'resolution': 'Isolate affected assets, collect volatile forensic logs, and review access control policies.',
        'response_domain': 'General Containment',
        'priority': 'Medium',
        'rationale': 'Unclassified security anomalies require immediate host isolation and telemetry extraction.',
        'response_steps': [
            'Isolate the impacted host/endpoint from the network.',
            'Capture volatile memory and system log snapshots.',
            'Perform privilege escalation and access log review.'
        ],
        'confidence': 0.85,
        'times_used': 5,
        'successful_resolutions': 4,
        'historical_matches': [
            {'incident_id': 'INC-2026-0010', 'similarity': 0.88, 'resolution': 'Host isolation and volatile memory collection.', 'outcome': 'success'}
        ]
    }
}

class HindsightMemoryClient:
    def __init__(self):
        self.api_key = settings.HINDSIGHT_API_KEY
        self.base_url = settings.HINDSIGHT_BASE_URL
        self.profiles = DEFAULT_RESOLUTION_PROFILES

    async def query_memory(self, scenario: str, raw_input: Any) -> Dict[str, Any]:
        """
        Queries Hindsight Cloud API for historical matches & resolution stats.
        Falls back smoothly to local memory store if Hindsight API is unconfigured.
        """
        profile = self.profiles.get(scenario, self.profiles['Generic Security Event'])

        # If Hindsight Cloud API credentials are provided, attempt live cloud query
        if self.api_key:
            try:
                async with httpx.AsyncClient(timeout=3.0) as client:
                    response = await client.post(
                        f"{self.base_url}/query",
                        headers={"Authorization": f"Bearer {self.api_key}"},
                        json={"scenario": scenario, "query": str(raw_input)}
                    )
                    if response.status_code == 200:
                        return response.json()
            except Exception as e:
                print(f"[Hindsight Client Warning] Cloud query failed, falling back to local memory store: {e}")

        return profile

    def update_local_memory(self, resolution_id: str, outcome: str, incident_id: str) -> Dict[str, Any]:
        """
        Updates memory metrics locally when analyst submits feedback.
        """
        target_profile = None
        for key, prof in self.profiles.items():
            if prof['resolution_id'] == resolution_id:
                target_profile = prof
                break

        if not target_profile:
            # Fallback to SSH profile if id not found
            target_profile = self.profiles['SSH Brute Force']

        target_profile['times_used'] += 1
        if outcome == 'success':
            target_profile['successful_resolutions'] += 1

        new_match = {
            'incident_id': incident_id,
            'similarity': 1.0,
            'resolution': target_profile['resolution'],
            'outcome': outcome
        }
        target_profile['historical_matches'].insert(0, new_match)

        times_used = target_profile['times_used']
        successful = target_profile['successful_resolutions']
        success_rate = successful / times_used if times_used > 0 else 0.0

        return {
            "times_used": times_used,
            "successful_resolutions": successful,
            "success_rate": round(success_rate, 4),
            "historical_matches": target_profile['historical_matches']
        }

hindsight_service = HindsightMemoryClient()
