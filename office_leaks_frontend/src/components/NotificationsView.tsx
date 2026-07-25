import React, { useState } from "react";
import { Bell, Check, Heart, MessageSquare, Shield } from "lucide-react";
import type { Notification } from "../types";

interface NotificationsViewProps {
  notifications: Notification[];
  onMarkRead: (id: string) => void;
  onMarkAllRead: () => void;
}

export const NotificationsView: React.FC<NotificationsViewProps> = ({
  notifications,
  onMarkRead,
  onMarkAllRead,
}) => {
  const [filter, setFilter] = useState<"all" | "unread">("all");

  const displayedNotifications = notifications.filter((n) => {
    if (filter === "unread") return !n.isRead;
    return true;
  });

  const getIcon = (type: Notification["type"]) => {
    switch (type) {
      case "like":
        return <Heart className="w-4 h-4 text-red-500 fill-red-500" />;
      case "comment":
        return <MessageSquare className="w-4 h-4 text-sky-500 fill-sky-500" />;
      case "system":
        return <Shield className="w-4 h-4 text-[#0EA5E9]" />;
      default:
        return <Bell className="w-4 h-4 text-slate-400" />;
    }
  };

  return (
    <div className="bg-white border border-slate-100 rounded-2xl overflow-hidden shadow-sm max-w-2xl mx-auto w-full">
      {/* Header */}
      <div className="p-4 border-b border-slate-100 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Bell className="w-5 h-5 text-slate-700" />
          <h2 className="text-sm font-bold text-slate-800 font-heading">
            Notifications Center
          </h2>
        </div>

        <button
          onClick={onMarkAllRead}
          className="text-xs font-bold text-[#0EA5E9] hover:underline flex items-center gap-1 cursor-pointer"
        >
          <Check className="w-3.5 h-3.5" />
          Mark all as read
        </button>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-slate-100 px-4">
        <button
          onClick={() => setFilter("all")}
          className={`py-3 px-3 font-heading text-xs font-bold border-b-2 transition-all cursor-pointer ${
            filter === "all"
              ? "border-[#0EA5E9] text-[#0EA5E9]"
              : "border-transparent text-slate-400 hover:text-slate-700"
          }`}
        >
          All
        </button>
        <button
          onClick={() => setFilter("unread")}
          className={`py-3 px-3 font-heading text-xs font-bold border-b-2 transition-all cursor-pointer ${
            filter === "unread"
              ? "border-[#0EA5E9] text-[#0EA5E9]"
              : "border-transparent text-slate-400 hover:text-slate-700"
          }`}
        >
          Unread ({notifications.filter((n) => !n.isRead).length})
        </button>
      </div>

      {/* List */}
      <div className="divide-y divide-slate-100 overflow-y-auto max-h-[60vh]">
        {displayedNotifications.map((notif) => (
          <div
            key={notif.id}
            onClick={() => onMarkRead(notif.id)}
            className={`p-4 flex items-start gap-3 cursor-pointer hover:bg-slate-50 transition-colors ${
              !notif.isRead ? "bg-[#0EA5E9]/5" : "bg-white"
            }`}
          >
            <div className="mt-0.5 p-2 bg-slate-50 rounded-xl border border-slate-100">
              {getIcon(notif.type)}
            </div>

            <div className="flex-1 min-w-0">
              <p className="text-xs text-slate-700 font-body leading-normal">
                <strong className="text-slate-800 font-semibold font-heading">
                  {notif.senderName}
                </strong>{" "}
                {notif.content}
              </p>
              <span className="text-[10px] text-slate-400 mt-1 block">
                {notif.createdAt}
              </span>
            </div>

            {!notif.isRead && (
              <span className="w-2 h-2 rounded-full bg-[#0EA5E9] mt-2 self-start flex-shrink-0" />
            )}
          </div>
        ))}

        {displayedNotifications.length === 0 && (
          <div className="text-center py-12 text-slate-400 italic text-xs font-body">
            No notifications to display.
          </div>
        )}
      </div>
    </div>
  );
};
