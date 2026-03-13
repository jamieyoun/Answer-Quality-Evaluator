"use client";

type Props = {
  pipelines: { A: boolean; B: boolean; C: boolean };
  onPipelinesChange: (v: { A: boolean; B: boolean; C: boolean }) => void;
  topK: number;
  onTopKChange: (v: number) => void;
  alpha: number;
  onAlphaChange: (v: number) => void;
  maxChars: number;
  onMaxCharsChange: (v: number) => void;
  disabled?: boolean;
  onRun: () => void;
};

export function RunControls({
  pipelines,
  onPipelinesChange,
  topK,
  onTopKChange,
  alpha,
  onAlphaChange,
  maxChars,
  onMaxCharsChange,
  disabled,
  onRun,
}: Props) {
  return (
    <div className="card mb-2 flex items-center justify-between gap-4">
      <div className="flex items-center gap-3">
        <div className="text-xs font-semibold text-slate-300">
          Pipelines
        </div>
        {(["A", "B", "C"] as const).map((p) => (
          <label key={p} className="flex items-center gap-1 text-xs text-slate-300">
            <input
              type="checkbox"
              className="h-3 w-3 rounded border-slate-600 bg-surfaceMuted"
              checked={pipelines[p]}
              onChange={(e) =>
                onPipelinesChange({ ...pipelines, [p]: e.target.checked })
              }
            />
            <span>{p}</span>
          </label>
        ))}
      </div>
      <div className="flex items-center gap-4">
        <label className="flex items-center gap-2 text-xs text-slate-300">
          <span>top_k</span>
          <input
            type="number"
            min={1}
            max={16}
            value={topK}
            onChange={(e) => onTopKChange(Number(e.target.value) || 1)}
            className="w-16 rounded border border-slate-700 bg-surface px-2 py-1 text-xs"
          />
        </label>
        <label className="flex items-center gap-2 text-xs text-slate-300">
          <span>alpha (C)</span>
          <input
            type="number"
            min={0}
            max={1}
            step={0.1}
            value={alpha}
            onChange={(e) =>
              onAlphaChange(Math.min(1, Math.max(0, Number(e.target.value))))
            }
            className="w-20 rounded border border-slate-700 bg-surface px-2 py-1 text-xs"
          />
        </label>
        <label className="flex items-center gap-2 text-xs text-slate-300">
          <span>max_chars</span>
          <input
            type="number"
            min={200}
            max={4000}
            step={100}
            value={maxChars}
            onChange={(e) =>
              onMaxCharsChange(Math.max(200, Number(e.target.value) || 1200))
            }
            className="w-20 rounded border border-slate-700 bg-surface px-2 py-1 text-xs"
          />
        </label>
      </div>
      <button
        onClick={onRun}
        disabled={disabled}
        className="rounded-md bg-accent px-3 py-1.5 text-xs font-semibold text-slate-900 disabled:opacity-40"
      >
        {disabled ? "Running..." : "Run compare"}
      </button>
    </div>
  );
}

