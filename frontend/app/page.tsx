'use client';

import { useState } from 'react';
import { PRESET_ALERTS, ATTACK_CATEGORIES } from '@/lib/mockData';
import {
  investigateAlert,
  submitFeedback,
} from '@/lib/api';
import { InvestigationResult, Alert } from '@/types/cyberguard';

export default function Home() {
  const [theme, setTheme] = useState<'dark' | 'light'>('dark');
  const [loading, setLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState<string>('');
  const [result, setResult] = useState<InvestigationResult | null>(null);
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false);

  const [selectedAttack, setSelectedAttack] = useState<string>('SSH Brute Force');
  const [rawInput, setRawInput] = useState('');

  const toggleTheme = () => {
    setTheme((prev) => (prev === 'dark' ? 'light' : 'dark'));
  };

  const runPipeline = async (
    rawInputData: Alert | string,
    source: 'PRESET_SELECTION' | 'RAW_SYSLOG_WEBHOOK'
  ) => {
    setLoading(true);
    setFeedbackSubmitted(false);
    setLoadingStep('Ingesting threat telemetry and evaluating playbook...');

    try {
      const data = await investigateAlert(rawInputData, source);
      setResult(data);
    } catch (err) {
      console.error('Telemetry processing error:', err);
    } finally {
      setLoading(false);
      setLoadingStep('');
    }
  };

  const handleDropdownSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedAttack) return;
    const alertData = PRESET_ALERTS[selectedAttack];
    if (alertData) {
      runPipeline(alertData, 'PRESET_SELECTION');
    }
  };

  const handleRawInputSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!rawInput.trim()) return;
    runPipeline(rawInput, 'RAW_SYSLOG_WEBHOOK');
  };

  const handleFeedback = async (outcome: 'success' | 'failed') => {
    if (!result) return;

    const incidentId = 'INC-2026-0042';
    const resolutionId = result.recommendation.resolution_id;

    try {
      const res = await submitFeedback({
        incident_id: incidentId,
        resolution_id: resolutionId,
        outcome,
      });

      if (res.memory_updated) {
        setFeedbackSubmitted(true);
        setResult((prev) =>
          prev
            ? {
                ...prev,
                recommendation: {
                  ...prev.recommendation,
                  times_used: res.metrics.times_used,
                  success_rate: res.metrics.success_rate,
                  successful_resolutions: res.metrics.successful_resolutions,
                },
              }
            : null
        );
      }
    } catch (err) {
      console.error('Feedback submission error:', err);
    }
  };

  return (
    <div className={theme}>
      <main className="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 p-8 font-sans transition-colors duration-200">
        <header className="mb-8 border-b border-slate-200 dark:border-slate-800 pb-4 flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white flex items-center gap-2">
              CYBERGUARD <span className="text-xs px-2 py-0.5 rounded bg-purple-100 dark:bg-purple-950 text-purple-700 dark:text-purple-300 font-mono font-normal">v2.4 Enterprise</span>
            </h1>
            <p className="text-xs text-slate-500 dark:text-slate-400 font-mono">
              Autonomous Threat Detection & Security Orchestration Platform
            </p>
          </div>

          <div className="flex items-center gap-4 text-xs font-mono">
            {loading ? (
              <span className="text-amber-500 dark:text-amber-400 font-semibold flex items-center gap-1.5">
                <span className="h-2 w-2 rounded-full bg-amber-500 animate-ping"></span>
                ANALYZING TELEMETRY...
              </span>
            ) : result ? (
              <span className="text-emerald-600 dark:text-emerald-400 font-semibold flex items-center gap-1.5">
                <span className="h-2 w-2 rounded-full bg-emerald-500"></span>
                ACTIVE INCIDENT ANALYSIS
              </span>
            ) : (
              <span className="text-slate-500 dark:text-slate-400 font-semibold flex items-center gap-1.5">
                <span className="h-2 w-2 rounded-full bg-emerald-500"></span>
                SYSTEM READY
              </span>
            )}

            <button
              onClick={toggleTheme}
              className="ml-2 px-3 py-1.5 rounded-md border text-xs font-semibold font-mono transition cursor-pointer bg-slate-200 dark:bg-slate-800 text-slate-800 dark:text-slate-200 border-slate-300 dark:border-slate-700 hover:bg-slate-300 dark:hover:bg-slate-700"
            >
              {theme === 'dark' ? '☀️ Light Mode' : '🌙 Dark Mode'}
            </button>
          </div>
        </header>

        <section className="mb-8 grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="p-4 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg shadow-sm flex flex-col justify-between">
            <div>
              <h2 className="text-xs font-mono text-slate-500 dark:text-slate-400 uppercase mb-3 font-semibold">
                Threat Scenario Selector
              </h2>
              <form onSubmit={handleDropdownSubmit} className="flex flex-col gap-3">
                <label className="text-xs font-medium text-slate-700 dark:text-slate-300">
                  Select Attack Vector:
                </label>
                <select
                  value={selectedAttack}
                  onChange={(e) => setSelectedAttack(e.target.value)}
                  className="w-full p-2.5 bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded text-xs font-mono text-slate-900 dark:text-slate-100 focus:outline-none focus:border-purple-500 cursor-pointer"
                >
                  <optgroup label="🔒 Network & System Threats">
                    {ATTACK_CATEGORIES.TRADITIONAL.map((attack) => (
                      <option key={attack} value={attack}>
                        {attack}
                      </option>
                    ))}
                  </optgroup>
                  <optgroup label="🤖 AI & LLM Infrastructure Threats">
                    {ATTACK_CATEGORIES.AI_SECURITY.map((attack) => (
                      <option key={attack} value={attack}>
                        {attack}
                      </option>
                    ))}
                  </optgroup>
                </select>
                <button
                  type="submit"
                  className="mt-2 w-full py-2 bg-purple-600 hover:bg-purple-500 text-white rounded text-xs font-semibold cursor-pointer transition"
                >
                  Execute Incident Analysis
                </button>
              </form>
            </div>
          </div>

          <div className="p-4 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg shadow-sm">
            <h2 className="text-xs font-mono text-slate-500 dark:text-slate-400 uppercase mb-2 font-semibold">
              Telemetry & Syslog Ingestion
            </h2>
            <form onSubmit={handleRawInputSubmit} className="flex flex-col gap-2">
              <textarea
                rows={4}
                value={rawInput}
                onChange={(e) => setRawInput(e.target.value)}
                placeholder='Paste raw syslog stream or security alert payload...'
                className="w-full p-2 bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-800 rounded text-xs font-mono text-slate-900 dark:text-slate-200 focus:outline-none focus:border-purple-500"
              />
              <button
                type="submit"
                className="self-end px-4 py-1.5 bg-slate-800 dark:bg-slate-700 hover:bg-slate-700 dark:hover:bg-slate-600 text-white rounded text-xs font-semibold cursor-pointer transition"
              >
                Ingest Raw Payload
              </button>
            </form>
          </div>
        </section>

        {loading && (
          <div className="p-6 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg font-mono text-sm text-purple-600 dark:text-purple-400 animate-pulse shadow-sm">
            <p className="text-xs text-slate-400 dark:text-slate-500 mb-1">
              AUTOMATED INVESTIGATION IN PROGRESS
            </p>
            <p className="font-bold">{loadingStep}</p>
          </div>
        )}

        {!loading && result && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="p-6 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg shadow-sm">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <span className="text-xs font-mono text-purple-600 dark:text-purple-400 uppercase font-semibold">
                    Recommended Playbook
                  </span>
                  <h2 className="text-xl font-bold text-slate-900 dark:text-white mt-1">
                    {result.recommendation.resolution}
                  </h2>
                </div>
                <span className="px-2.5 py-1 text-xs font-mono bg-purple-100 dark:bg-purple-950 text-purple-700 dark:text-purple-300 border border-purple-300 dark:border-purple-800 rounded">
                  Confidence: {(result.recommendation.confidence * 100).toFixed(0)}%
                </span>
              </div>

              <div className="grid grid-cols-3 gap-4 my-6 p-4 bg-slate-50 dark:bg-slate-950 rounded border border-slate-200 dark:border-slate-800 text-center">
                <div>
                  <p className="text-xs text-slate-500 font-mono">Success Rate</p>
                  <p className="text-lg font-bold text-emerald-600 dark:text-emerald-400">
                    {(result.recommendation.success_rate * 100).toFixed(1)}%
                  </p>
                </div>
                <div>
                  <p className="text-xs text-slate-500 font-mono">Times Deployed</p>
                  <p className="text-lg font-bold text-slate-900 dark:text-white">
                    {result.recommendation.times_used}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-slate-500 font-mono">Successful</p>
                  <p className="text-lg font-bold text-slate-900 dark:text-white">
                    {result.recommendation.successful_resolutions}
                  </p>
                </div>
              </div>

              <div className="mt-6 border-t border-slate-200 dark:border-slate-800 pt-4">
                <p className="text-xs text-slate-500 dark:text-slate-400 mb-3 font-mono">
                  Analyst Incident Resolution Outcome
                </p>
                <div className="flex gap-3">
                  <button
                    onClick={() => handleFeedback('success')}
                    className="flex-1 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded text-sm font-semibold transition cursor-pointer"
                  >
                    [ ✓ RESOLVED ]
                  </button>
                  <button
                    onClick={() => handleFeedback('failed')}
                    className="flex-1 py-2 bg-rose-600 hover:bg-rose-500 text-white rounded text-sm font-semibold transition cursor-pointer"
                  >
                    [ ✕ ESCALATE ]
                  </button>
                </div>

                {feedbackSubmitted && (
                  <div className="mt-4 p-2.5 bg-emerald-50 dark:bg-emerald-950/50 border border-emerald-200 dark:border-emerald-800 rounded text-xs text-emerald-800 dark:text-emerald-200 font-mono">
                    ✓ Resolution Outcome Recorded & Playbook Metrics Updated.
                  </div>
                )}
              </div>
            </div>

            <div className="p-6 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg shadow-sm">
              <h3 className="text-xs font-mono text-slate-500 dark:text-slate-400 uppercase mb-4 font-semibold">
                Historical Incident Intelligence
              </h3>
              {result.historical_matches.length === 0 ? (
                <p className="text-sm text-slate-500 font-mono">
                  No prior similar incidents recorded in knowledge base.
                </p>
              ) : (
                <ul className="space-y-3">
                  {result.historical_matches.map((match, index) => (
                    <li
                      key={`${match.incident_id}-${match.resolution}-${index}`}
                      className="p-3 bg-slate-50 dark:bg-slate-950 rounded border border-slate-200 dark:border-slate-800 text-sm"
                    >
                      <div className="flex justify-between items-center mb-1">
                        <span className="font-mono text-purple-600 dark:text-purple-400 text-xs font-semibold">
                          {match.incident_id}
                        </span>
                        <span className="text-xs font-mono text-emerald-600 dark:text-emerald-400 font-semibold">
                          {(match.similarity * 100).toFixed(0)}% Similarity
                        </span>
                      </div>
                      <p className="text-slate-700 dark:text-slate-300">{match.resolution}</p>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
