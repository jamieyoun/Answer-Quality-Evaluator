"use client";

type RetrievedChunk = {
  chunk_id: string;
  doc_id: string;
  section: string;
  score: number;
  text: string;
  metadata: Record<string, any>;
};

type Props = {
  chunks: RetrievedChunk[];
  highlightedIds?: string[];
};

export function EvidenceDrawer({ chunks, highlightedIds = [] }: Props) {
  return (
    <aside className="flex h-full w-96 flex-col border-l border-slate-800 bg-surfaceMuted">
      <div className="border-b border-slate-800 px-4 py-2 text-xs font-semibold uppercase tracking-wide text-slate-400">
        Evidence
      </div>
      <div className="flex-1 overflow-y-auto px-3 py-3 space-y-2">
        {chunks.length === 0 && (
          <div className="text-xs text-slate-500">
            Select a pipeline and click “View evidence” to inspect retrieved
            chunks.
          </div>
        )}
        {chunks.map((c) => {
          const highlighted = highlightedIds.includes(c.chunk_id);
          return (
            <details
              key={c.chunk_id}
              className={`group rounded-md border bg-surface p-2 text-xs ${
                highlighted
                  ? "border-accent/70 shadow-[0_0_0_1px_rgba(56,189,248,0.6)]"
                  : "border-slate-800"
              }`}
            >
              <summary className="flex cursor-pointer items-center justify-between gap-2">
                <div>
                  <div className="font-mono text-[10px] text-slate-400">
                    {c.doc_id} · {c.section}
                  </div>
                  <div className="mt-0.5 line-clamp-2 text-[11px] text-slate-200">
                    {c.text.slice(0, 160)}
                    {c.text.length > 160 ? "…" : ""}
                  </div>
                </div>
                <div className="ml-2 text-[10px] text-accent">
                  {c.score.toFixed(3)}
                </div>
              </summary>
              <div className="mt-2 border-t border-slate-800 pt-2 text-[11px] leading-relaxed text-slate-100">
                {c.text}
              </div>
            </details>
          );
        })}
      </div>
    </aside>
  );
}

