"use client";

import useSWR from "swr";
import { useEffect, useState } from "react";
import { QuestionSidebar } from "../components/QuestionSidebar";
import { RunControls } from "../components/RunControls";
import { CompareView } from "../components/CompareView";
import { EvidenceDrawer } from "../components/EvidenceDrawer";
import { Leaderboard } from "../components/Leaderboard";
import { fetchCompare, fetchEvalResults } from "../lib/api";

const fetcher = (url: string) => fetch(url).then((r) => r.json());

export default function HomePage() {
  const { data: qData, error: qError } = useSWR("/api/questions", fetcher);
  const [selectedQuestion, setSelectedQuestion] = useState<any | null>(null);
  const [pipelines, setPipelines] = useState({ A: true, B: true, C: true });
  const [topK, setTopK] = useState(6);
  const [alpha, setAlpha] = useState(0.5);
  const [maxChars, setMaxChars] = useState(1200);
  const [compareResult, setCompareResult] = useState<any | null>(null);
  const [compareLoading, setCompareLoading] = useState(false);
  const [compareError, setCompareError] = useState<string | null>(null);
  const [evidenceChunks, setEvidenceChunks] = useState<any[]>([]);
  const [highlightedChunkIds, setHighlightedChunkIds] = useState<string[]>([]);

  const [runId, setRunId] = useState("");
  const [resultsData, setResultsData] = useState<any | null>(null);
  const [resultsLoading, setResultsLoading] = useState(false);
  const [resultsError, setResultsError] = useState<string | null>(null);

  useEffect(() => {
    if (qData?.questions && qData.questions.length > 0 && !selectedQuestion) {
      setSelectedQuestion(qData.questions[0]);
    }
  }, [qData, selectedQuestion]);

  const handleRunCompare = async () => {
    if (!selectedQuestion) return;
    setCompareLoading(true);
    setCompareError(null);
    setCompareResult(null);
    setEvidenceChunks([]);
    setHighlightedChunkIds([]);
    try {
      const res = await fetchCompare({
        q: selectedQuestion.question,
        top_k: topK,
        include_c: pipelines.C,
        alpha,
      });
      setCompareResult(res);
    } catch (e: any) {
      setCompareError(e?.message ?? "Failed to run comparison");
    } finally {
      setCompareLoading(false);
    }
  };

  const handleLoadResults = async () => {
    if (!runId.trim()) return;
    setResultsLoading(true);
    setResultsError(null);
    setResultsData(null);
    try {
      const data = await fetchEvalResults(runId.trim());
      setResultsData(data);
    } catch (e: any) {
      setResultsError(e?.message ?? "Failed to load eval results");
    } finally {
      setResultsLoading(false);
    }
  };

  const questions = qData?.questions ?? [];

  return (
    <div className="flex h-full">
      <QuestionSidebar
        questions={questions}
        selectedId={selectedQuestion?.question_id}
        onSelect={(q) => setSelectedQuestion(q)}
      />
      <div className="flex min-w-0 flex-1 flex-col gap-2 p-3">
        <RunControls
          pipelines={pipelines}
          onPipelinesChange={setPipelines}
          topK={topK}
          onTopKChange={setTopK}
          alpha={alpha}
          onAlphaChange={setAlpha}
          maxChars={maxChars}
          onMaxCharsChange={setMaxChars}
          disabled={compareLoading}
          onRun={handleRunCompare}
        />
        {qError && (
          <div className="card mb-2 text-xs text-red-400">
            Failed to load questions from backend.
            <div className="mt-1 text-[11px] text-red-300">
              Check that the backend repo is present and{" "}
              <code>data/evalset/questions.jsonl</code> exists, then reload.
            </div>
          </div>
        )}
        {compareError && (
          <div className="card mb-2 text-xs text-red-400">
            {compareError}
          </div>
        )}
        <div className="flex min-h-0 flex-1 gap-2">
          <div className="flex min-w-0 flex-1 flex-col">
            {compareLoading && (
              <div className="card mb-2 space-y-2 text-xs text-slate-400">
                <div>Running comparison…</div>
                <div className="flex gap-2">
                  <div className="h-16 flex-1 animate-pulse rounded-md bg-slate-800/60" />
                  <div className="h-16 flex-1 animate-pulse rounded-md bg-slate-800/60" />
                  <div className="hidden h-16 flex-1 animate-pulse rounded-md bg-slate-800/60 md:block" />
                </div>
              </div>
            )}
            <CompareView
              data={compareResult}
              scores={resultsData?.heuristic ?? null}
              onSelectEvidence={(chunks, ids) => {
                setEvidenceChunks(chunks);
                setHighlightedChunkIds(ids);
              }}
            />
            <div className="mt-2 flex items-center gap-2">
              <input
                value={runId}
                onChange={(e) => setRunId(e.target.value)}
                placeholder="run_id (optional, for scores)"
                className="w-64 rounded-md border border-slate-700 bg-surface px-2 py-1 text-xs text-slate-100 placeholder:text-slate-500"
              />
              <button
                onClick={handleLoadResults}
                disabled={resultsLoading}
                className="rounded-md border border-slate-700 px-2 py-1 text-xs text-slate-200 disabled:opacity-40"
              >
                {resultsLoading ? "Loading…" : "Load results"}
              </button>
              {resultsError && (
                <span className="text-xs text-red-400">{resultsError}</span>
              )}
            </div>
            <Leaderboard data={resultsData} />
          </div>
          <EvidenceDrawer
            chunks={evidenceChunks}
            highlightedIds={highlightedChunkIds}
          />
        </div>
      </div>
    </div>
  );
}

