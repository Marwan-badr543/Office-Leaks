import React, { useState, useEffect, useRef } from "react";
import { Search, Flame, TrendingUp, Star } from "lucide-react";
import type { Company } from "../types";
import { companiesApi } from "../api/companiesApi";

interface RightSidebarProps {
  onCompanyClick?: (companyId: string) => void;
  onSearchChange?: (search: string) => void;
  onCategoryClick?: (category: string) => void;
}

export const RightSidebar: React.FC<RightSidebarProps> = ({
  onCompanyClick,
  onSearchChange,
  onCategoryClick,
}) => {
  const [searchTerm, setSearchTerm] = useState("");
  const [topRated, setTopRated] = useState<Company[]>([]);
  const [trendingTopics, setTrendingTopics] = useState<{ category: string; count: number }[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchedTopRatedRef = useRef(false);

  useEffect(() => {
    if (fetchedTopRatedRef.current) return;
    fetchedTopRatedRef.current = true;
    let isSubscribed = true;
    const controller = new AbortController();

    companiesApi
      .getTopAndTrending()
      .then((res) => {
        if (!isSubscribed) return;
        setTopRated(res.topRated.slice(0, 5) || []);
        setTrendingTopics(res.trending || []);
      })
      .catch((err) => {
        if (err.name === 'AbortError') return;
        console.error("Failed to fetch top rated and trending data:", err);
      })
      .finally(() => {
        if (isSubscribed) setLoading(false);
      });

    return () => {
      isSubscribed = false;
      controller.abort();
      fetchedTopRatedRef.current = false;
    };
  }, []);

  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value;
    setSearchTerm(val);
    if (onSearchChange) onSearchChange(val);
  };

  return (
    <aside className="hidden lg:block lg:w-80 space-y-6 flex-shrink-0">
      {/* Search Bar */}
      <div className="relative">
        <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
        <input
          type="text"
          placeholder="Search companies, leaks..."
          value={searchTerm}
          onChange={handleSearch}
          className="w-full pl-10 pr-4 py-2.5 bg-white border border-slate-200 rounded-xl text-sm placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-[#0EA5E9]/55 focus:border-[#0EA5E9] transition-all font-body shadow-sm"
        />
      </div>

      {/* Top Rated Companies Widget */}
      <div className="bg-white rounded-2xl p-5 shadow-sm border border-slate-100">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-bold text-sm text-slate-800 font-heading">
            Top Rated Companies
          </h3>
          <TrendingUp className="w-4 h-4 text-slate-400" />
        </div>

        <div className="space-y-3.5">
          {loading ? (
            <p className="text-xs text-slate-400 italic text-center py-4">
              Loading rankings...
            </p>
          ) : (
            topRated.map((comp, idx) => (
              <div
                key={comp.id}
                onClick={() => onCompanyClick && onCompanyClick(comp.id)}
                className="flex items-center justify-between p-2 rounded-xl hover:bg-slate-50 cursor-pointer transition-all duration-205"
              >
                <div className="flex items-center gap-3">
                  <span className="text-xs font-bold text-slate-400 w-3">
                    {idx + 1}
                  </span>
                  <div className="w-8 h-8 rounded-lg bg-slate-900 flex items-center justify-center text-white font-extrabold text-[10px] overflow-hidden">
                    {comp.logo.startsWith("http") ? (
                      <img src={comp.logo} alt={comp.name} className="w-full h-full object-cover" />
                    ) : (
                      comp.logo
                    )}
                  </div>
                  <div>
                    <h4 className="text-xs font-bold text-slate-800 font-heading">
                      {comp.name}
                    </h4>
                    <span className="text-[10px] text-slate-400">
                      {comp.industry}
                    </span>
                  </div>
                </div>
                <div className="text-right">
                  <div className="flex items-center gap-0.5 justify-end">
                    <Star className="w-3 h-3 fill-amber-400 stroke-amber-400" />
                    <span className="text-xs font-bold text-slate-800 font-body">
                      {comp.rating.toFixed(1)}
                    </span>
                  </div>
                </div>
              </div>
            ))
          )}

          {!loading && topRated.length === 0 && (
            <p className="text-xs text-slate-400 italic text-center py-4">
              No companies rated yet.
            </p>
          )}
        </div>

        <button 
          onClick={() => onCompanyClick && onCompanyClick("view-all")}
          className="w-full text-center text-xs font-bold text-[#0EA5E9] hover:underline mt-4 block font-heading cursor-pointer"
        >
          View full rankings &rarr;
        </button>
      </div>

      {/* Trending Topics Widget */}
      <div className="bg-white rounded-2xl p-5 shadow-sm border border-slate-100">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-bold text-sm text-slate-800 font-heading">
            Trending Categories
          </h3>
          <Flame className="w-4 h-4 text-orange-500 fill-orange-500" />
        </div>

        <div className="space-y-3">
          {loading ? (
            <p className="text-xs text-slate-400 italic text-center py-4">
              Loading trends...
            </p>
          ) : (
            trendingTopics.map((topic, idx) => (
              <div
                key={idx}
                onClick={() => onCategoryClick && onCategoryClick(topic.category)}
                className="flex items-center justify-between p-2 rounded-xl bg-slate-50/50 hover:bg-slate-100 hover:scale-[1.01] active:scale-[0.99] transition-all duration-205 cursor-pointer"
              >
                <div className="flex items-center gap-2.5">
                  <span className="text-xs font-bold text-slate-400">
                    #{idx + 1}
                  </span>
                  <span className="text-xs font-bold text-slate-700 font-body">
                    {topic.category}
                  </span>
                </div>
                <span className="text-[10px] bg-slate-200/60 text-slate-650 font-bold px-2.5 py-0.5 rounded-full">
                  {topic.count} leaks
                </span>
              </div>
            ))
          )}

          {!loading && trendingTopics.length === 0 && (
            <p className="text-xs text-slate-400 italic text-center py-4">
              No recent trends.
            </p>
          )}
        </div>
      </div>

      {/* Security Info Card */}
      <div className="bg-[#0F172A] text-white rounded-2xl p-5 shadow-md border border-slate-800">
        <div className="flex items-center gap-2 mb-3">
          <Flame className="w-5 h-5 text-[#0EA5E9]" />
          <h3 className="font-bold text-sm tracking-wider uppercase font-heading text-white">
            Encrypted Network
          </h3>
        </div>
        <p className="text-xs font-body text-slate-300 leading-relaxed">
          Office Leaks operates on strict zero-trust principles. All company reviews, salary submissions, and anonymous posts are cryptographically hashed before storage.
        </p>
      </div>
    </aside>
  );
};
