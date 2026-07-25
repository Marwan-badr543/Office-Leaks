import React from "react";
import { 
  Home, 
  Building2, 
  Users, 
  User as UserIcon, 
  ShieldAlert,
  LogOut,
  LogIn
} from "lucide-react";
import type { User } from "../types";

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  currentUser: User | null;
  onOpenAuthModal: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab,
  setActiveTab,
  currentUser,
  onOpenAuthModal,
}) => {
  const navItems = [
    { id: "feed", name: "Home Feed", icon: Home },
    { id: "companies", name: "Companies", icon: Building2 },
    { id: "users", name: "Peer Network", icon: Users },
    { id: "profile", name: "Profile", icon: UserIcon },
  ];

  return (
    <>
      {/* Desktop Left Sidebar */}
      <aside className="hidden md:flex md:w-64 lg:w-72 flex-col fixed inset-y-0 left-0 bg-[#0F172A] text-slate-100 z-30 shadow-xl border-r border-slate-800">
        {/* Brand / Logo */}
        <div className="p-6 border-b border-slate-800 flex items-center gap-3">
          <div className="bg-[#0EA5E9] p-2 rounded-lg text-[#0F172A] flex items-center justify-center">
            <ShieldAlert className="w-6 h-6 stroke-[2.5]" />
          </div>
          <div>
            <h1 className="text-lg font-extrabold tracking-tight text-white font-heading">
              Office Leaks
            </h1>
            <span className="text-[10px] uppercase font-bold tracking-widest text-[#0EA5E9]">
              Encrypted · Anonymous
            </span>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-4 py-6 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => {
                  if (item.id === "profile" && !currentUser) {
                    onOpenAuthModal();
                    return;
                  }
                  setActiveTab(item.id);
                }}
                className={`w-full flex items-center justify-between px-4 py-3 rounded-xl transition-all duration-200 group text-left ${
                  isActive
                    ? "bg-[#0EA5E9] text-[#0F172A] font-semibold shadow-md shadow-[#0EA5E9]/20 cursor-pointer"
                    : "text-slate-400 hover:bg-slate-800/60 hover:text-white cursor-pointer"
                }`}
              >
                <div className="flex items-center gap-3">
                  <Icon className={`w-5 h-5 transition-transform duration-200 group-hover:scale-105 ${
                    isActive ? "text-[#0F172A]" : "text-slate-400 group-hover:text-white"
                  }`} />
                  <span className="text-sm font-heading">{item.name}</span>
                </div>
              </button>
            );
          })}
        </nav>

        {/* User Profile Footer / Guest Auth Button */}
        <div className="p-4 border-t border-slate-800 bg-slate-900/40">
          {currentUser ? (
            <div className="flex items-center gap-3">
              <img
                src={currentUser.avatar}
                alt={currentUser.name}
                className="w-10 h-10 rounded-full border border-[#0EA5E9]/30 object-cover bg-white flex-shrink-0"
              />
              <div className="flex-1 min-w-0">
                <h2 className="text-sm font-bold text-white truncate font-heading">
                  {currentUser.name}
                </h2>
                <p className="text-xs text-slate-400 truncate">
                  @{currentUser.username}
                </p>
              </div>
            </div>
          ) : (
            <button
              onClick={onOpenAuthModal}
              className="w-full bg-[#0EA5E9] hover:bg-[#0EA5E9]/90 text-[#0F172A] font-extrabold py-2.5 px-4 rounded-xl text-xs font-heading flex items-center justify-center gap-2 shadow-sm shadow-[#0EA5E9]/20 transition-all cursor-pointer"
            >
              <LogIn className="w-4 h-4" />
              Sign In / Register
            </button>
          )}
        </div>
      </aside>

      {/* Mobile Bottom Navigation */}
      <nav className="md:hidden fixed bottom-0 left-0 right-0 bg-[#0F172A] text-slate-100 border-t border-slate-800 flex items-center justify-around py-2 z-50 shadow-2xl backdrop-blur-md bg-opacity-95">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => {
                if (item.id === "profile" && !currentUser) {
                  onOpenAuthModal();
                  return;
                }
                setActiveTab(item.id);
              }}
              className="flex flex-col items-center gap-0.5 py-1 px-3 relative min-w-[64px] cursor-pointer"
            >
              <div className="relative">
                <Icon className={`w-5 h-5 transition-colors duration-200 ${
                  isActive ? "text-[#0EA5E9]" : "text-slate-400"
                }`} />
              </div>
              <span className={`text-[9px] font-heading font-medium tracking-wide ${
                isActive ? "text-[#0EA5E9]" : "text-slate-400"
              }`}>
                {item.id === "feed" ? "Feed" : item.name.split(" ")[0]}
              </span>
              {isActive && (
                <div className="absolute top-0 w-8 h-[2px] bg-[#0EA5E9] rounded-full" />
              )}
            </button>
          );
        })}
      </nav>
    </>
  );
};
