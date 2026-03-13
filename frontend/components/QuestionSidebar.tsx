"use client";

import { useMemo, useState } from "react";

type Question = {
  question_id: string;
  question: string;
  category?: string;
  difficulty?: string;
};

type Props = {
  questions: Question[];
  selectedId?: string;
  onSelect: (q: Question) => void;
};

export function QuestionSidebar({ questions, selectedId, onSelect }: Props) {
  const [query, setQuery] = useState("");
  const [categoryFilter, setCategoryFilter] = useState<string | "all">("all");

  const categories = useMemo(() => {
    const set = new Set<string>();
    questions.forEach((q) => {
      if (q.category) set.add(q.category);
    });
    return Array.from(set).sort();
  }, [questions]);

  const filtered = useMemo(() => {
    return questions.filter((q) => {
      const matchesCategory =
        categoryFilter === "all" || q.category === categoryFilter;
      const text = `${q.question_id} ${q.question}`.toLowerCase();
      const matchesQuery = !query || text.includes(query.toLowerCase());
      return matchesCategory && matchesQuery;
    });
  }, [questions, query, categoryFilter]);

  return (
    <aside className="flex h-full w-80 flex-col border-r border-slate-800 bg-surfaceMuted">
      <div className="border-b border-slate-800 px-4 py-2 text-xs font-semibold uppercase tracking-wide text-slate-400">
        Questions
      </div>
      <div className="border-b border-slate-800 px-3 py-2 space-y-2">
        <input
          type="search"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search questions..."
          className="w-full rounded-md border border-slate-700 bg-surface px-2 py-1 text-[11px] text-slate-100 placeholder:text-slate-500"
        />
        <div className="flex flex-wrap items-center gap-1 text-[10px]">
          <span className="text-slate-400">Category:</span>
          <button
            className={`chip px-2 ${
              categoryFilter === "all"
                ? "bg-accent/30 text-slate-900"
                : "bg-surface text-slate-300"
            }`}
            onClick={() => setCategoryFilter("all")}
          >
            All
          </button>
          {categories.map((c) => (
            <button
              key={c}
              className={`chip px-2 ${
                categoryFilter === c
                  ? "bg-accent/30 text-slate-900"
                  : "bg-surface text-slate-300"
              }`}
              onClick={() => setCategoryFilter(c)}
            >
              {c}
            </button>
          ))}
        </div>
      </div>
      <div className="flex-1 overflow-y-auto px-2 py-2 space-y-1">
        {filtered.length === 0 && (
          <div className="px-2 py-2 text-[11px] text-slate-500">
            No questions match this filter. Try clearing search or filters.
          </div>
        )}
        {filtered.map((q) => {
          const active = q.question_id === selectedId;
          return (
            <button
              key={q.question_id}
              onClick={() => onSelect(q)}
              className={`w-full rounded-md px-3 py-2 text-left text-xs ${
                active
                  ? "bg-accent/20 text-slate-50"
                  : "text-slate-300 hover:bg-slate-800/60"
              }`}
            >
              <div className="flex items-center justify-between gap-2">
                <div className="font-mono text-[10px] text-slate-400">
                  {q.question_id}
                </div>
                {q.difficulty && (
                  <span className="chip bg-surface px-1.5 py-0 text-[9px] capitalize text-slate-400">
                    {q.difficulty}
                  </span>
                )}
              </div>
              <div className="mt-0.5 line-clamp-2 text-[11px]">
                {q.question}
              </div>
            </button>
          );
        })}
      </div>
    </aside>
  );
}


