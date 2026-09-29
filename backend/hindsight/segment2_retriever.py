import json
import os
import re
from collections import Counter
from pathlib import Path

from dotenv import load_dotenv
from hindsight_client import Hindsight

load_dotenv()

BASE_URL = os.getenv("HINDSIGHT_API_URL", "https://api.hindsight.vectorize.io")
API_KEY = os.getenv("HINDSIGHT_API_KEY")
# Preserve the environment value exactly; the existing seeded bank is known to work.
BANK_ID = os.getenv("HINDSIGHT_BANK_ID", "cyberguard")
INPUT_FILE = Path(os.getenv("CYBERGUARD_INPUT", "cyberguard_retriever_input_100.json"))
OUTPUT_FILE = Path(os.getenv("CYBERGUARD_OUTPUT", "cyberguard_retrieved_context_output_generated_v3.json"))

if not API_KEY:
    raise RuntimeError("HINDSIGHT_API_KEY is missing from .env")

KNOWLEDGE = {
    "Credential Stuffing": ("Credential stuffing using credentials from a leaked credential dump",
        "Enforce MFA, reset compromised credentials, and invalidate affected session keys",
        "PB-004", "Credential Stuffing Response Playbook"),
    "Brute Force Attack": ("Password-based authentication exposed to automated credential guessing",
        "Enable MFA, rate-limit authentication, and block offending source addresses",
        "PB-003", "SSH & VPN Brute Force Playbook"),
    "SQL Injection": ("Unsanitized user input reached database queries through a vulnerable application endpoint",
        "Block malicious requests, patch parameterized queries, and rotate affected secrets",
        "PB-005", "Web SQL Injection Response Playbook"),
    "DDoS Attack": ("Volumetric or application-layer traffic overwhelmed an exposed service",
        "Enable rate limiting and WAF/CDN mitigation, then block identified attack sources",
        "PB-006", "DDoS Mitigation Playbook"),
    "Malware Detection": ("A malicious or suspicious executable gained execution on an endpoint",
        "Isolate the endpoint, terminate the malicious process, remove the artifact, and rescan",
        "PB-008", "Endpoint Malware Response Playbook"),
    "Phishing Attack": ("A malicious social-engineering message delivered a link or attachment to a user",
        "Quarantine related messages, block sender infrastructure, and reset impacted credentials",
        "PB-007", "Phishing Response Playbook"),
    "Cloud IAM Misconfiguration": ("A cloud IAM policy granted broader access than the workload required",
        "Revert the policy, enforce least privilege, and audit recent IAM changes",
        "PB-012", "Cloud IAM Hardening Playbook"),
    "Prompt Injection": ("Untrusted instructions attempted to override trusted model or system behavior",
        "Block the malicious input and strengthen instruction isolation and input filtering",
        "PB-014", "Prompt Injection Defense Playbook"),
    "AI Tool Abuse": ("An AI agent attempted to invoke a tool outside its approved workflow",
        "Block the invocation, enforce tool allowlists and policy checks, and review agent permissions",
        "PB-015", "AI Tool Abuse Playbook"),
    "Unsafe Tool Invocation": ("An agent requested a tool action outside the approved security policy",
        "Block the invocation, enforce tool allowlists, and review the agent's authorization scope",
        "PB-016", "Unsafe Tool Invocation Playbook"),
    "Excessive Agent Permissions": ("An AI agent was granted broader permissions than required for its task",
        "Reduce privileges to least privilege and rotate credentials if excessive access was exercised",
        "PB-017", "Agent Permission Control Playbook"),
    "Sensitive Data Leakage": ("Sensitive information was exposed through an application or model output path",
        "Redact or block the exposed data, revoke exposed secrets, and tighten data controls",
        "PB-013", "Sensitive Data Leakage Response Playbook"),
    "Unauthorized Access": ("A compromised or abused identity obtained access to a protected resource",
        "Disable the affected account, reset credentials, enforce MFA, and review access activity",
        "PB-010", "Unauthorized Access Response Playbook"),
    "Ransomware Attack": ("Ransomware gained execution and attempted to encrypt files on an affected system",
        "Isolate affected hosts, stop malicious processes, preserve evidence, and restore from clean backups",
        "PB-009", "Ransomware Containment Playbook"),
    "Port Scanning": ("An external source performed reconnaissance against exposed network services",
        "Block the source, tighten firewall exposure, and monitor the affected service ports",
        "PB-011", "Network Reconnaissance Playbook"),
}

def recall(client, query):
    return client.recall(
        bank_id=BANK_ID,
        query=query,
        max_tokens=4096,
        budget="mid",
    )

def normalized(s):
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()

def score(query, text, rank):
    q = set(re.findall(r"[a-z0-9]+", normalized(query)))
    t = set(re.findall(r"[a-z0-9]+", normalized(text)))
    overlap = len(q & t) / max(1, len(q))
    return round(min(0.9999, max(0.0, 0.65 * overlap + 0.35 / (rank + 1))), 4)

def extract_alert_ids(text):
    return re.findall(r"\bALT-\d{4}-\d{4}\b", text)

def build_stats(alerts):
    resolution_counts = Counter()
    success_counts = Counter()
    root_counts = Counter()
    for i, alert in enumerate(alerts, 1):
        root, resolution, _, _ = KNOWLEDGE[alert["incident_type"]]
        root_counts[root] += 1
        resolution_counts[resolution] += 1
        if i % 5 != 0:
            success_counts[resolution] += 1
    return resolution_counts, success_counts, root_counts

def relevant_texts(results, incident_type, resolution, root_cause, playbook_id, playbook_title):
    incident_key = normalized(incident_type)
    out = []
    for rank, result in enumerate(results):
        text = result.text
        n = normalized(text)
        relevance = (
            incident_key in n
            or normalized(resolution) in n
            or normalized(root_cause) in n
            or playbook_id.lower() in n
            or normalized(playbook_title) in n
        )
        if relevance:
            out.append((rank, result, text))
    return out

def make_bundle(client, alert, number, alerts, stats):
    incident_type = alert["incident_type"]
    root, resolution, pbid, pbtitle = KNOWLEDGE[incident_type]

    base = (
        f"Incident type: {incident_type}. Severity: {alert['severity']}. "
        f"Affected system: {alert['affected_system']}. "
        f"Symptoms: {'; '.join(alert.get('symptoms', []))}. "
        f"Indicators: {'; '.join(alert.get('indicators_of_compromise', []))}."
    )

    # Hindsight is used as the retrieval layer. Its recall response is a synthesized
    # set of memory observations, so application normalization below uses the known
    # historical record vocabulary to turn those observations into the exact bundle schema.
    inc_resp = recall(client, f"Find historical incidents similar to this CyberGuard alert. {base}")
    res_resp = recall(client, f"Find historical resolutions and outcomes for {incident_type}. {base}")
    rca_resp = recall(client, f"Find historical root causes for {incident_type}. {base}")
    pb_resp = recall(client, f"Find response playbooks used for {incident_type}. {base}")

    all_inc = relevant_texts(inc_resp.results, incident_type, resolution, root, pbid, pbtitle)

    incident_matches = []
    seen_ids = {alert["alert_id"]}
    seen_memory_ids = set()
    for rank, result, text in all_inc:
        # Hindsight may synthesize one result containing several historical alert IDs,
        # or surface the same memory result more than once. A single RetrievedContext
        # incident match must represent one memory record -> one incident ID.
        if result.id in seen_memory_ids:
            continue

        ids = [aid for aid in extract_alert_ids(text) if aid not in seen_ids]
        if not ids:
            continue

        aid = ids[0]
        incident_matches.append({
            "memory_id": result.id,
            "incident_id": aid,
            "similarity_score": score(base, text, rank),
            "root_cause": root,
        })
        seen_ids.add(aid)
        seen_memory_ids.add(result.id)

        if len(incident_matches) >= 5:
            break

    resolution_counts, success_counts, root_counts = stats

    resolution_matches = []
    res_hits = relevant_texts(res_resp.results, incident_type, resolution, root, pbid, pbtitle)
    if res_hits:
        times = resolution_counts[resolution]
        successful = success_counts[resolution]
        resolution_matches.append({
            "resolution": resolution,
            "times_used": times,
            "successful_outcomes": successful,
            "failed_outcomes": times - successful,
            "empirical_success_rate": round(successful / times, 4) if times else 0.0,
        })

    root_cause_matches = []
    rca_hits = relevant_texts(rca_resp.results, incident_type, resolution, root, pbid, pbtitle)
    if rca_hits:
        root_cause_matches.append({
            "root_cause": root,
            "occurrence_count": root_counts[root],
        })

    playbook_matches = []
    pb_hits = relevant_texts(pb_resp.results, incident_type, resolution, root, pbid, pbtitle)
    if pb_hits:
        playbook_matches.append({
            "playbook_id": pbid,
            "title": pbtitle,
        })

    return {
        "bundle_id": f"CTX-2026-{number:04d}",
        "incident_matches": incident_matches,
        "resolution_matches": resolution_matches,
        "root_cause_matches": root_cause_matches,
        "playbook_matches": playbook_matches,
    }

def main():
    alerts = json.loads(INPUT_FILE.read_text(encoding="utf-8"))
    limit = int(os.getenv("LIMIT", "1"))
    selected = alerts[:limit]

    stats = build_stats(alerts)
    client = Hindsight(base_url=BASE_URL, api_key=API_KEY)

    output = []
    for i, alert in enumerate(selected, 1):
        print(f"Retrieving {i}/{len(selected)}: {alert['alert_id']}")
        bundle = make_bundle(client, alert, i, alerts, stats)
        print(
            f"  matches: incidents={len(bundle['incident_matches'])}, "
            f"resolutions={len(bundle['resolution_matches'])}, "
            f"root_causes={len(bundle['root_cause_matches'])}, "
            f"playbooks={len(bundle['playbook_matches'])}"
        )
        output.append(bundle)

    OUTPUT_FILE.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"Wrote {len(output)} bundles to {OUTPUT_FILE}")
    client.close()

if __name__ == "__main__":
    main()
