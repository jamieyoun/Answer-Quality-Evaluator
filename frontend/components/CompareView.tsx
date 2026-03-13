"use client";

import { useState } from "react";

type Citation = {
  doc_id: string;
  section: string;
  chunk_id: string;
};

type RetrievedChunk = {
  chunk_id: string;
  doc_id: string;
  section: string;
  score: number;
  text: string;
  metadata: Record<string, any>;
};

type PipelineResult = {
  pipeline_id: string;
  answer: string;
  citations: Citation[];
  retrieved: RetrievedChunk[];
};

type Scores = {
  accuracy: { score_0_2: number };
  completeness: { score_0_2: number };
  citation_quality: { score_0_2: number };
  total: number;
  tags: any[];
};

type Props = {
  data: any | null;
  scores?: Record<string, Scores> | null;
  onSelectEvidence: (chunks: RetrievedChunk[], highlightIds: string[]) => void;
};

export function CompareView({ data, scores, onSelectEvidence }: Props) {
  if (!data) {
    return (
      <div className="flex h-full items-center justify-center text-sm text-slate-500">
        Select a question and run a comparison.
      </div>
    );
  }

  const cols: { id: "pipeline_a" | "pipeline_b" | "pipeline_c"; label: string }[] =
    [
      { id: "pipeline_a", label: "Pipeline A" },
      { id: "pipeline_b", label: "Pipeline B" },
      { id: "pipeline_c", label: "Pipeline C" },
    ];

  const q = data.question as string;

  const renderCol = (key: "pipeline_a" | "pipeline_b" | "pipeline_c") => {
    const res: PipelineResult | undefined = data[key];
    if (!res) return null;
    const pid = res.pipeline_id?.[0] ?? key.toUpperCase();
    const s =
      scores?.[pid] ?? scores?.[pid.replace("_strict_citations_small_chunks", "A")];

    return (
      <div key={key} className="card flex flex-col gap-2">
        <div className="flex items-center justify-between gap-2">
          <div className="flex flex-col gap-0.5">
            <div className="text-xs font-semibold text-slate-200">{pid}</div>
            <div className="text-[10px] text-slate-500">
              top_k={data.top_k} {pid === "C" && "· hybrid α="}
              {pid === "C" && (data.alpha ?? "").toString()}
            </div>
          </div>
          <div className="flex items-center gap-2">
            {s && (
              <div className="flex gap-1 text-[10px] text-slate-400">
                <span className="chip bg-surface">
                  A:{s.accuracy.score_0_2}
                </span>
                <span className="chip bg-surface">
                  C:{s.completeness.score_0_2}
                </span>
                <span className="chip bg-surface">
                  CQ:{s.citation_quality.score_0_2}
                </span>
                <span className="chip bg-accent/30 text-slate-900">
                  Σ:{s.total}
                </span>
              </div>
            )}
            <button
              className="chip bg-surface text-[10px]"
              onClick={() =>
                navigator.clipboard.writeText(
                  `${res.answer}\n\nCitations:\n${(res.citations || [])
                    .map(
                      (c) =>
                        `- ${c.doc_id} — ${c.section} (${c.chunk_id})`,
                    )
                    .join("\n")}`,
                )
              }
            >
              Copy answer
            </button>
          </div>
        </div>
        <div className="prose prose-invert max-w-none text-xs text-slate-100">
          {res.answer || <span className="text-slate-500">No answer.</span>}
        </div>
        <div className="mt-1 flex flex-wrap gap-1">
          {res.citations?.map((c) => (
            <button
              key={c.chunk_id}
              className="chip hover:border hover:border-accent/60"
              onClick={() =>
                onSelectEvidence(
                  res.retrieved || [],
                  [c.chunk_id],
                )
              }
            >
              <span className="font-mono text-[10px] text-slate-300">
                {c.doc_id}
              </span>
              <span className="ml-1 text-[10px] text-slate-400">
                · {c.section}
              </span>
            </button>
          ))}
          <button
            className="chip border border-accent/40 text-accent"
            onClick={() =>
              onSelectEvidence(
                res.retrieved || [],
                (res.citations || []).map((c) => c.chunk_id),
              )
            }
          >
            View evidence ({res.retrieved?.length ?? 0})
          </button>
        </div>
      </div>
    );
  };

  return (
    <div className="flex h-full flex-col gap-2">
      <div className="card">
        <div className="text-[11px] font-semibold uppercase tracking-wide text-slate-400">
          Question
        </div>
        <div className="mt-1 text-sm text-slate-100">{q}</div>
      </div>
      <div className="grid flex-1 grid-cols-1 gap-2 md:grid-cols-3">
        {cols.map((c) => renderCol(c.id))}
      </div>
    </div>
  );
}

