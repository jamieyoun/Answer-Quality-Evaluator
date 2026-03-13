"use client";

type Props = {
  data: any | null;
};

export function Leaderboard({ data }: Props) {
  if (!data) {
    return (
      <div className="card mt-2 text-xs text-slate-500">
        Enter a run_id and load results to see aggregate scores.
      </div>
    );
  }

  const heuristic = data.heuristic ?? {};
  const judge = data.llm_judge ?? {};

  const pids = Array.from(
    new Set([...Object.keys(heuristic), ...Object.keys(judge)])
  ).sort();

  return (
    <div className="card mt-2 text-xs">
      <div className="mb-2 flex items-center justify-between">
        <div className="font-semibold text-slate-200">Run summary</div>
        <div className="text-[10px] text-slate-400">
          run_id: <span className="font-mono">{data.run_id}</span>
        </div>
      </div>
      <table className="w-full border-collapse text-[11px]">
        <thead>
          <tr className="border-b border-slate-800 text-slate-400">
            <th className="py-1 text-left">Pipeline</th>
            <th className="py-1 text-right">N</th>
            <th className="py-1 text-right">Acc</th>
            <th className="py-1 text-right">Comp</th>
            <th className="py-1 text-right">CQ</th>
            <th className="py-1 text-right">Total</th>
            <th className="py-1 text-right">LLM Acc</th>
            <th className="py-1 text-right">LLM Comp</th>
            <th className="py-1 text-right">LLM CQ</th>
          </tr>
        </thead>
        <tbody>
          {pids.map((pid) => {
            const h = heuristic[pid];
            const j = judge[pid];
            return (
              <tr key={pid} className="border-b border-slate-900">
                <td className="py-1 text-slate-200">{pid}</td>
                <td className="py-1 text-right text-slate-300">
                  {h?.count ?? j?.count ?? "-"}
                </td>
                <td className="py-1 text-right">
                  {h ? h.avg_accuracy.toFixed(2) : "-"}
                </td>
                <td className="py-1 text-right">
                  {h ? h.avg_completeness.toFixed(2) : "-"}
                </td>
                <td className="py-1 text-right">
                  {h ? h.avg_citation_quality.toFixed(2) : "-"}
                </td>
                <td className="py-1 text-right">
                  {h ? h.avg_total.toFixed(2) : "-"}
                </td>
                <td className="py-1 text-right text-slate-300">
                  {j ? j.avg_accuracy.toFixed(2) : "-"}
                </td>
                <td className="py-1 text-right text-slate-300">
                  {j ? j.avg_completeness.toFixed(2) : "-"}
                </td>
                <td className="py-1 text-right text-slate-300">
                  {j ? j.avg_citation_quality.toFixed(2) : "-"}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
      {Object.keys(heuristic).length > 0 && (
        <div className="mt-2 text-[10px] text-slate-500">
          Heuristic scores use deterministic rubric v1. LLM-judge scores (if
          present) are explicitly marked and should be interpreted as model
          opinions, not ground truth.
        </div>
      )}
    </div>
  );
}

