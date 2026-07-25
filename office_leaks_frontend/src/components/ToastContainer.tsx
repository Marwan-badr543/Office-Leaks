import React from "react";
import { AlertCircle, CheckCircle, Info, X } from "lucide-react";
import type { ToastMessage } from "../hooks/useToast";

interface ToastContainerProps {
  toasts: ToastMessage[];
  onDismiss: (id: string) => void;
}

export const ToastContainer: React.FC<ToastContainerProps> = ({ toasts, onDismiss }) => {
  if (toasts.length === 0) return null;

  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col gap-2.5 max-w-sm w-full pointer-events-none px-4 md:px-0">
      {toasts.map((toast) => {
        const isError = toast.type === "error";
        const isSuccess = toast.type === "success";

        return (
          <div
            key={toast.id}
            className={`pointer-events-auto flex items-center justify-between gap-3 p-3.5 rounded-xl shadow-lg border text-xs font-medium font-body animate-scale-pulse ${
              isError
                ? "bg-slate-900 text-white border-red-500/30"
                : isSuccess
                ? "bg-slate-900 text-white border-emerald-500/30"
                : "bg-slate-900 text-white border-slate-700"
            }`}
          >
            <div className="flex items-center gap-2.5 min-w-0">
              {isError && <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0" />}
              {isSuccess && <CheckCircle className="w-4 h-4 text-emerald-400 flex-shrink-0" />}
              {!isError && !isSuccess && <Info className="w-4 h-4 text-[#0EA5E9] flex-shrink-0" />}
              <span className="truncate">{toast.message}</span>
            </div>

            <div className="flex items-center gap-2 flex-shrink-0">
              {toast.actionText && (
                <button
                  onClick={() => {
                    if (toast.onAction) toast.onAction();
                    onDismiss(toast.id);
                  }}
                  className="text-xs font-bold text-[#0EA5E9] hover:underline cursor-pointer"
                >
                  {toast.actionText}
                </button>
              )}
              <button
                onClick={() => onDismiss(toast.id)}
                className="text-slate-400 hover:text-white transition-colors cursor-pointer p-0.5"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        );
      })}
    </div>
  );
};
