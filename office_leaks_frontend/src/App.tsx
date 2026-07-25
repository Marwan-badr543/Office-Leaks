import { useState, useCallback, useEffect } from "react";
import { 
  Lock, 
  ShieldAlert, 
  ListFilter
} from "lucide-react";
import { Sidebar } from "./components/Sidebar";
import { RightSidebar } from "./components/RightSidebar";
import { ComposerCard } from "./components/ComposerCard";
import { PostList } from "./components/PostList";
import { CompaniesView } from "./components/CompaniesView";
import { PeersView } from "./components/PeersView";
import { AuthPage } from "./components/AuthModal";
import { LogoutConfirmModal } from "./components/LogoutConfirmModal";
import { ToastContainer } from "./components/ToastContainer";
import { useFeed } from "./hooks/useFeed";
import { useToast } from "./hooks/useToast";
import { useScrollMemory } from "./hooks/useScrollMemory";
import { useKeyboardNavigation } from "./hooks/useKeyboardNavigation";
import type { User } from "./types";

function App() {
  const { toasts, addToast, removeToast } = useToast();

  // Tab persistence across page reloads & shallow URL sync
  const [activeTab, setActiveTabState] = useState<string>(() => {
    try {
      const urlParams = new URLSearchParams(window.location.search);
      const tabParam = urlParams.get("tab");
      if (tabParam) return tabParam;
      return localStorage.getItem("office_leaks_active_tab") || "feed";
    } catch {
      return "feed";
    }
  });

  useScrollMemory("feed", activeTab === "feed");

  const setActiveTab = useCallback((tab: string) => {
    try {
      localStorage.setItem("office_leaks_active_tab", tab);
      const url = new URL(window.location.href);
      url.searchParams.set("tab", tab);
      window.history.pushState({}, "", url.toString());
    } catch {}
    setActiveTabState(tab);
  }, []);

  // Sync back/forward browser navigation
  useEffect(() => {
    const handlePopState = () => {
      const urlParams = new URLSearchParams(window.location.search);
      const tabParam = urlParams.get("tab") || "feed";
      setActiveTabState(tabParam);
    };

    window.addEventListener("popstate", handlePopState);
    return () => {
      window.removeEventListener("popstate", handlePopState);
    };
  }, []);

  // Auth state: initial user loaded from localStorage or null (Guest)
  const [currentUser, setCurrentUser] = useState<User | null>(() => {
    try {
      const saved = localStorage.getItem("office_leaks_user");
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });

  const [showAuthModal, setShowAuthModal] = useState(false);
  const [showLogoutConfirm, setShowLogoutConfirm] = useState(false);

  const handleOpenAuthModal = useCallback(() => {
    setShowAuthModal(true);
  }, []);

  const handleRequestSignOut = useCallback(() => {
    setShowLogoutConfirm(true);
  }, []);

  const handleNavigateToUser = useCallback((userId: string) => {
    const url = new URL(window.location.href);
    url.searchParams.set("tab", "users");
    url.searchParams.set("user", userId);
    window.history.pushState({}, "", url.toString());
    setActiveTab("users");
  }, []);

  const handleErrorToast = useCallback((msg: string, actionText?: string, onAction?: () => void) => {
    addToast(msg, "error", actionText, onAction, 4000);
  }, [addToast]);

  // Custom hook for Feed state management (pure API driven)
  const {
    posts,
    hasMore,
    loading,
    activeCategory,
    setActiveCategory,
    feedType,
    setFeedType,
    sortBy,
    setSortBy,
    loadMorePosts,
    handleLikePost,
    handleSavePost,
    handleAddPost,
  } = useFeed({
    currentUser,
    onOpenAuthModal: handleOpenAuthModal,
    onErrorToast: handleErrorToast,
    enabled: activeTab === "feed",
  });

  // Highlight post from URL query parameter when feed loads
  useEffect(() => {
    if (activeTab === "feed" && posts.length > 0) {
      const urlParams = new URLSearchParams(window.location.search);
      const highlightPostId = urlParams.get("highlight");
      if (highlightPostId) {
        setTimeout(() => {
          const element = document.getElementById(`post-${highlightPostId}`);
          if (element) {
            element.scrollIntoView({ behavior: "smooth", block: "center" });
            element.classList.add("ring-2", "ring-[#0EA5E9]", "ring-offset-2");
            setTimeout(() => {
              element.classList.remove("ring-2", "ring-[#0EA5E9]", "ring-offset-2");
            }, 2000);
            
            const url = new URL(window.location.href);
            url.searchParams.delete("highlight");
            window.history.replaceState({}, "", url.toString());
          }
        }, 500);
      }
    }
  }, [activeTab, posts]);

  // Hotkey keyboard navigation (J, K, L, C, M)
  const handleKeyboardLike = useCallback((index: number) => {
    if (posts[index]) {
      handleLikePost(posts[index].id);
    }
  }, [posts, handleLikePost]);

  const { selectedIndex } = useKeyboardNavigation({
    itemCount: posts.length,
    onLike: handleKeyboardLike,
    enabled: activeTab === "feed",
  });



  // Jump from Right Sidebar to specific company page
  const [selectedCompanyIdExternal, setSelectedCompanyIdExternal] = useState<string | null>(null);

  const handleCompanyClick = useCallback((companyId: string) => {
    setSelectedCompanyIdExternal(companyId);
    setActiveTab("companies");
  }, [setActiveTab]);

  const handleCategoryClick = useCallback((rawCategory: string) => {
    const norm = rawCategory.toUpperCase();
    let mapped = "All Leaks";
    
    if (norm === "CULTURE") mapped = "Workplace Culture";
    else if (norm === "SALARIES") mapped = "Salary Data";
    else if (norm === "MISCONDUCT") mapped = "Misconduct";
    else if (norm === "POLICY") mapped = "Internal Policy";
    else if (norm === "MANAGEMENT") mapped = "Management";
    else if (norm === "GROWTH") mapped = "Growth";
    else if (norm === "INTERVIEWS") mapped = "Interviews";
    else if (norm === "OTHER") mapped = "Other";
    else {
      const matched = [
        "Workplace Culture",
        "Salary Data",
        "Misconduct",
        "Internal Policy",
        "Management",
        "Growth",
        "Interviews",
        "Other"
      ].find(cat => cat.toUpperCase() === norm);
      if (matched) mapped = matched;
    }

    setActiveCategory(mapped);
    setActiveTab("feed");
    window.scrollTo({ top: 0, behavior: "smooth" });
  }, [setActiveCategory, setActiveTab]);

  const handleClearExternalCompany = useCallback(() => {
    setSelectedCompanyIdExternal(null);
  }, []);

  const handleAuthSuccess = useCallback((user: User) => {
    setCurrentUser(user);
    setShowAuthModal(false);
    window.location.reload();
  }, []);

  const handleSignOut = useCallback(() => {
    localStorage.removeItem("office_leaks_user");
    localStorage.removeItem("office_leaks_token");
    localStorage.removeItem("office_leaks_refresh_token");
    localStorage.removeItem("office_leaks_active_tab");
    
    // Clear url parameters if any to return cleanly to feed
    const url = new URL(window.location.href);
    url.searchParams.delete("tab");
    window.history.replaceState({}, "", url.toString());

    window.location.reload();
  }, []);

  // Handle session expiration
  useEffect(() => {
    const handleAuthExpired = () => {
      handleSignOut();
      handleOpenAuthModal();
      addToast("Session expired. Please sign in again.", "info");
    };

    window.addEventListener("auth-expired", handleAuthExpired);
    return () => {
      window.removeEventListener("auth-expired", handleAuthExpired);
    };
  }, [handleSignOut, handleOpenAuthModal, addToast]);

  // Category filter list
  const categoryFilters = [
    "All Leaks",
    "Workplace Culture",
    "Salary Data",
    "Misconduct",
    "Internal Policy",
    "Management",
    "Growth",
    "Interviews",
    "Other",
  ];

  if (showAuthModal) {
    return (
      <div className="min-h-screen bg-[#F8FAFC]">
        <AuthPage
          onAuthSuccess={handleAuthSuccess}
          onClose={() => setShowAuthModal(false)}
        />
        <ToastContainer toasts={toasts} onDismiss={removeToast} />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#F8FAFC] flex font-body text-[#0F172A]">
      {/* Sidebar Navigation */}
      <Sidebar 
        activeTab={activeTab} 
        setActiveTab={setActiveTab} 
        currentUser={currentUser} 
        onOpenAuthModal={handleOpenAuthModal}
      />

      {/* Main Workspace Frame */}
      <div className="flex-1 md:pl-64 lg:pl-72 flex flex-col min-w-0">
        
        {/* Mobile Header Bar */}
        <header className="md:hidden sticky top-0 bg-[#0F172A] text-white py-3.5 px-4 flex items-center justify-between z-40 border-b border-slate-800 shadow-md">
          <div className="flex items-center gap-2">
            <div className="bg-[#0EA5E9] p-1.5 rounded-lg text-[#0F172A] flex items-center justify-center">
              <ShieldAlert className="w-5 h-5 stroke-[2.5]" />
            </div>
            <div>
              <h1 className="text-sm font-extrabold font-heading text-white tracking-tight leading-none">
                Office Leaks
              </h1>
              <span className="text-[8px] uppercase tracking-widest text-[#0EA5E9] font-bold leading-none block mt-0.5">
                Encrypted · Hashed
              </span>
            </div>
          </div>
          <div className="flex items-center gap-1 bg-slate-800 px-2 py-1 rounded-lg border border-slate-700">
            <Lock className="w-3 h-3 text-[#0EA5E9]" />
            <span className="text-[9px] font-bold text-slate-300 uppercase tracking-wider">
              Protected
            </span>
          </div>
        </header>

        {/* Content Wrapper */}
        <main className="flex-grow p-4 md:p-6 lg:p-8 max-w-7xl w-full mx-auto pb-24 md:pb-8 flex gap-6 min-h-[calc(100vh-60px)] md:min-h-screen">
          
          {/* MIDDLE COLUMN */}
          <div className="flex-1 min-w-0 space-y-6">
            
            {/* 1. HOME FEED TAB VIEW */}
            {activeTab === "feed" && (
              <>
                {/* Header Filter Panel */}
                <div className="bg-white border border-slate-100 rounded-2xl p-4 md:p-5 shadow-sm space-y-4">
                  <div className="flex items-center justify-between flex-wrap gap-3">
                    <h2 className="text-lg md:text-xl font-extrabold tracking-tight text-slate-800 font-heading">
                      Global Leak Feed
                    </h2>
                    
                    {/* Sort selector */}
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-slate-400 font-medium font-body flex items-center gap-1">
                        <ListFilter className="w-3.5 h-3.5" />
                        Sort:
                      </span>
                      <select
                        value={sortBy}
                        onChange={(e) => setSortBy(e.target.value as "recent" | "popular")}
                        className="bg-slate-50 border border-slate-200 rounded-xl px-3 py-1.5 text-xs text-slate-700 font-bold focus:outline-none focus:ring-1 focus:ring-[#0EA5E9]"
                      >
                        <option value="recent">Most Recent</option>
                        <option value="popular">Most Popular</option>
                      </select>
                    </div>
                  </div>

                  {/* Filter category chips */}
                  <div className="flex items-center gap-2 overflow-x-auto pb-1.5 scrollbar-none -mx-4 px-4 md:mx-0 md:px-0">
                    {categoryFilters.map((cat) => {
                      const isActive = activeCategory === cat;
                      return (
                        <button
                          key={cat}
                          onClick={() => setActiveCategory(cat)}
                          className={`text-xs font-bold px-3.5 py-1.5 rounded-xl border transition-all flex-shrink-0 cursor-pointer ${
                            isActive
                              ? "bg-[#0F172A] border-[#0F172A] text-white shadow-sm"
                              : "bg-slate-50 border-slate-200/80 text-slate-500 hover:bg-slate-100 hover:text-slate-700"
                          }`}
                        >
                          {cat}
                        </button>
                      );
                    })}
                  </div>
                </div>

                {/* Sub-counter tag */}
                <div className="flex items-center justify-center">
                  <div className="flex items-center gap-2 text-[10px] font-extrabold tracking-widest text-slate-400 uppercase">
                    <span className="w-1.5 h-1.5 rounded-full bg-[#0EA5E9] animate-pulse" />
                    {posts.length} leaks &bull; encrypted &bull; anonymous
                  </div>
                </div>

                {/* Composer card */}
                <ComposerCard 
                  currentUser={currentUser}
                  onOpenAuthModal={handleOpenAuthModal}
                  onPostCreated={handleAddPost}
                />


                {/* Virtual Feed Thread */}
                <PostList
                  posts={posts}
                  loading={loading}
                  hasMore={hasMore}
                  currentUser={currentUser}
                  onOpenAuthModal={handleOpenAuthModal}
                  loadMorePosts={loadMorePosts}
                  onLike={handleLikePost}
                  onSave={handleSavePost}
                  selectedIndex={selectedIndex}
                  onNavigateToUser={handleNavigateToUser}
                  onCompanyClick={handleCompanyClick}
                />
              </>
            )}

            {/* 2. COMPANIES DIRECTORY & DETAILS VIEW */}
            {activeTab === "companies" && (
              <CompaniesView
                currentUser={currentUser}
                onOpenAuthModal={handleOpenAuthModal}
                selectedCompanyIdExternal={selectedCompanyIdExternal}
                onClearExternalCompany={handleClearExternalCompany}
                onNavigateToUser={handleNavigateToUser}
              />
            )}

            {/* 3. PEER NETWORK & USER PROFILES VIEW */}
            {activeTab === "users" && (
              <PeersView
                currentUser={currentUser || undefined}
                mode="directory"
                onOpenAuthModal={handleOpenAuthModal}
                onCompanyClick={handleCompanyClick}
              />
            )}



            {/* 5. CURRENT USER PROFILE TAB */}
            {activeTab === "profile" && (
              <PeersView
                currentUser={currentUser || undefined}
                mode="profile"
                onOpenAuthModal={handleOpenAuthModal}
                onCompanyClick={handleCompanyClick}
              />
            )}

          </div>

          {/* RIGHT COLUMN */}
          {activeTab === "feed" && (
            <RightSidebar 
              onCompanyClick={handleCompanyClick} 
              onCategoryClick={handleCategoryClick}
            />
          )}

        </main>
      </div>



      {/* Logout Confirmation Modal */}
      <LogoutConfirmModal
        isOpen={showLogoutConfirm}
        onClose={() => setShowLogoutConfirm(false)}
        onConfirm={() => {
          setShowLogoutConfirm(false);
          handleSignOut();
        }}
      />

      {/* Non-intrusive Toast Container */}
      <ToastContainer toasts={toasts} onDismiss={removeToast} />
    </div>
  );
}

export default App;

