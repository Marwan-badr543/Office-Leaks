import React, { useState, useEffect } from "react";
import { 
  Building, 
  Lock, 
  Briefcase, 
  FolderOpen, 
  Search, 
  Check, 
  User as UserIcon, 
  ShieldCheck
} from "lucide-react";
import type { Company, Review, User } from "../types";
import { companiesApi } from "../api/companiesApi";

// Stable empty array to avoid creating a new [] reference on every render
// which would cause useEffect dependency changes and infinite re-render loops
const EMPTY_COMPANIES: Company[] = [];

interface ComposerCardProps {
  companies?: Company[];
  currentUser: User | null;
  onOpenAuthModal: () => void;
  onPostCreated: (
    type: "text" | "review",
    content: string,
    companyId?: string,
    rating?: number,
    category?: Review["category"],
    tag?: string,
    isAnonymous?: boolean
  ) => void;
}

export const ComposerCard: React.FC<ComposerCardProps> = ({
  companies: fallbackCompanies = EMPTY_COMPANIES,
  currentUser,
  onOpenAuthModal,
  onPostCreated,
}) => {
  const [content, setContent] = useState("");
  const [selectedCompanyId, setSelectedCompanyId] = useState("");
  const [companyQuery, setCompanyQuery] = useState("");
  const [companySuggestions, setCompanySuggestions] = useState<Company[]>([]);
  const [showCompanyDropdown, setShowCompanyDropdown] = useState(false);
  const [category, setCategory] = useState<Review["category"]>("Workplace Culture");
  const [tag, setTag] = useState("");
  const [isAnonymous, setIsAnonymous] = useState(true);
  const [isExpanded, setIsExpanded] = useState(false);

  // Live Company Search API call as user types
  useEffect(() => {
    if (!companyQuery.trim()) {
      setCompanySuggestions((prev) => prev.length === 0 ? prev : []);
      return;
    }

    const timer = setTimeout(() => {
      companiesApi
        .searchCompanies(companyQuery)
        .then((res) => {
          if (res.length > 0) {
            setCompanySuggestions(res);
          } else {
            const localMatches = fallbackCompanies.filter((c) =>
              c.name.toLowerCase().includes(companyQuery.toLowerCase())
            );
            setCompanySuggestions(localMatches);
          }
        })
        .catch(() => {
          const localMatches = fallbackCompanies.filter((c) =>
            c.name.toLowerCase().includes(companyQuery.toLowerCase())
          );
          setCompanySuggestions(localMatches);
        });
    }, 250);

    return () => clearTimeout(timer);
  }, [companyQuery, fallbackCompanies]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!currentUser) {
      onOpenAuthModal();
      return;
    }
    if (!content.trim()) return;

    onPostCreated(
      "text",
      content,
      selectedCompanyId || undefined,
      undefined,
      category,
      tag,
      isAnonymous
    );

    // Reset composer state
    setContent("");
    setSelectedCompanyId("");
    setCompanyQuery("");
    setCompanySuggestions([]);
    setShowCompanyDropdown(false);
    setCategory("Workplace Culture");
    setTag("");
    setIsExpanded(false);
  };

  const handleSelectCompany = (comp: Company) => {
    setSelectedCompanyId(comp.id);
    setCompanyQuery(comp.name);
    setShowCompanyDropdown(false);
  };

  return (
    <div className="bg-white border border-slate-100 rounded-2xl p-5 mb-5 shadow-sm">
      <div className="flex gap-3 items-start">
        <div className="hidden sm:flex w-10 h-10 rounded-xl bg-slate-100 border border-slate-200 items-center justify-center text-slate-500 font-bold text-sm font-heading flex-shrink-0">
          {isAnonymous ? <Lock className="w-4 h-4 text-[#0EA5E9]" /> : <UserIcon className="w-4 h-4 text-slate-600" />}
        </div>

        <form onSubmit={handleSubmit} className="flex-1 min-w-0">
          <textarea
            placeholder="Share an anonymous office experience, leak, query, or thoughts with the network..."
            value={content}
            onChange={(e) => setContent(e.target.value)}
            onFocus={() => {
              if (!currentUser) {
                onOpenAuthModal();
              } else {
                setIsExpanded(true);
              }
            }}
            className="w-full text-sm font-body border-0 p-0 text-slate-700 placeholder-slate-400 focus:ring-0 focus:outline-none resize-none min-h-[50px]"
            rows={isExpanded ? 3 : 1}
          />

          {isExpanded && (
            <div className="mt-4 pt-4 border-t border-slate-100 space-y-4 transition-all duration-200">
              {/* Identity Mode Selector (Anonymous vs Public Profile) */}

              <div className="flex items-center justify-between bg-slate-50 p-2 rounded-xl">
                <span className="text-xs font-bold text-slate-700 font-heading flex items-center gap-1.5">
                  <ShieldCheck className="w-4 h-4 text-[#0EA5E9]" />
                  Posting Mode:
                </span>
                <div className="flex bg-white p-1 rounded-lg border border-slate-200/80 shadow-xs">
                  <button
                    type="button"
                    onClick={() => setIsAnonymous(true)}
                    className={`px-3 py-1 rounded-md text-xs font-bold font-heading flex items-center gap-1.5 transition-all cursor-pointer ${
                      isAnonymous
                        ? "bg-[#0F172A] text-white shadow-sm"
                        : "text-slate-500 hover:text-slate-800"
                    }`}
                  >
                    <Lock className="w-3 h-3 text-[#0EA5E9]" />
                    Anonymous 🔒
                  </button>
                  <button
                    type="button"
                    onClick={() => setIsAnonymous(false)}
                    className={`px-3 py-1 rounded-md text-xs font-bold font-heading flex items-center gap-1.5 transition-all cursor-pointer ${
                      !isAnonymous
                        ? "bg-[#0F172A] text-white shadow-sm"
                        : "text-slate-500 hover:text-slate-800"
                    }`}
                  >
                    <UserIcon className="w-3 h-3 text-slate-300" />
                    Public Profile 👤
                  </button>
                </div>
              </div>

              {/* Share Config Form */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5 text-xs">
                {/* Live Company Search Input */}
                <div className="flex flex-col gap-1 relative">
                  <label className="font-bold text-slate-600 flex items-center gap-1">
                    <Building className="w-3.5 h-3.5 text-slate-400" />
                    Tag Company (Optional)
                  </label>

                  <div className="relative">
                    <input
                      type="text"
                      placeholder="Type company name to search..."
                      value={companyQuery}
                      onChange={(e) => {
                        setCompanyQuery(e.target.value);
                        setSelectedCompanyId("");
                        setShowCompanyDropdown(true);
                      }}
                      onFocus={() => setShowCompanyDropdown(true)}
                      className="w-full bg-slate-50 border border-slate-200 rounded-xl pl-8 pr-3 py-1.5 text-slate-700 focus:outline-none focus:ring-1 focus:ring-[#0EA5E9] focus:border-[#0EA5E9]"
                    />
                    <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-1/2 -translate-y-1/2" />
                  </div>

                  {showCompanyDropdown && companyQuery.trim().length > 0 && (
                    <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-slate-200 rounded-xl shadow-lg z-50 max-h-48 overflow-y-auto">
                      {companySuggestions.length > 0 ? (
                        companySuggestions.map((comp) => (
                          <button
                            key={comp.id}
                            type="button"
                            onClick={() => handleSelectCompany(comp)}
                            className="w-full text-left px-3 py-2 text-xs hover:bg-slate-50 flex items-center justify-between font-medium border-b border-slate-100 last:border-0"
                          >
                            <span className="text-slate-800 font-bold">{comp.name}</span>
                            <span className="text-[10px] text-slate-400">{comp.industry}</span>
                          </button>
                        ))
                      ) : (
                        <div className="p-3 text-[11px] text-slate-400 text-center">
                          No matching company found.
                        </div>
                      )}
                    </div>
                  )}

                  {selectedCompanyId && (
                    <span className="text-[10px] font-bold text-[#22C55E] flex items-center gap-1 mt-0.5">
                      <Check className="w-3 h-3" /> Selected Company Tagged
                    </span>
                  )}
                </div>

                {/* Categories Selector */}
                <div className="flex flex-col gap-1">
                  <label className="font-bold text-slate-600 flex items-center gap-1">
                    <FolderOpen className="w-3.5 h-3.5 text-slate-400" />
                    Category
                  </label>
                  <select
                    value={category}
                    onChange={(e) => setCategory(e.target.value as Review["category"])}
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-1.5 text-slate-700 focus:outline-none focus:ring-1 focus:ring-[#0EA5E9] focus:border-[#0EA5E9]"
                  >
                    <option value="Workplace Culture">Workplace Culture</option>
                    <option value="Salary Data">Salary Data</option>
                    <option value="Misconduct">Misconduct</option>
                    <option value="Internal Policy">Internal Policy</option>
                    <option value="Management">Management</option>
                    <option value="Growth">Growth</option>
                    <option value="Interviews">Interviews</option>
                    <option value="Other">Other</option>
                  </select>
                </div>

              </div>

              {/* Security & Identity Status Badge */}
              <div className="flex items-center gap-2 bg-slate-50 border border-slate-200/60 p-2 rounded-xl text-[11px]">
                {isAnonymous ? (
                  <>
                    <Lock className="w-4 h-4 text-[#0EA5E9] flex-shrink-0" />
                    <span className="font-body text-slate-600">
                      <strong>Anonymous Mode:</strong> Your identity will be completely hidden from public feed displays.
                    </span>
                  </>
                ) : (
                  <>
                    <UserIcon className="w-4 h-4 text-slate-700 flex-shrink-0" />
                    <span className="font-body text-slate-600">
                      <strong>Public Mode:</strong> Posting as <strong>{currentUser?.name || "Guest"}</strong>.
                    </span>
                  </>
                )}
              </div>
            </div>
          )}

          {/* Footer Actions */}
          <div className="flex justify-between items-center mt-3">
            <div className="hidden sm:flex items-center gap-1.5 text-xs text-slate-400 font-medium">
              <span className="w-2 h-2 rounded-full bg-[#0EA5E9] animate-pulse" />
              <span className="whitespace-nowrap">{isAnonymous ? "Anonymous & Encrypted" : `Public as ${currentUser?.name || "Guest"}`}</span>
            </div>


            <div className="flex items-center gap-2 ml-auto sm:ml-0">
              {isExpanded && (
                <button
                  type="button"
                  onClick={() => setIsExpanded(false)}
                  className="px-4 py-2 text-xs font-bold text-slate-500 hover:bg-slate-50 rounded-xl transition-colors font-heading cursor-pointer whitespace-nowrap"
                >
                  Cancel
                </button>
              )}
              <button
                type="submit"
                disabled={!content.trim()}
                className={`px-5 py-2 text-xs font-bold text-white rounded-xl shadow-sm transition-all font-heading whitespace-nowrap ${
                  content.trim()
                    ? "bg-[#0EA5E9] hover:bg-[#0EA5E9]/90 active:scale-[0.98] cursor-pointer shadow-[#0EA5E9]/20"
                    : "bg-slate-200 text-slate-400 cursor-not-allowed"
                }`}
              >
                Post Leak
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};
