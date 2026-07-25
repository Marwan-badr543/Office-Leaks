import React, { useEffect } from "react";
import { X, LogOut } from "lucide-react";

interface LogoutConfirmModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
}

export const LogoutConfirmModal: React.FC<LogoutConfirmModalProps> = ({
  isOpen,
  onClose,
  onConfirm,
}) => {
  useEffect(() => {
    if (!isOpen) return;

    document.body.style.overflow = "hidden";

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        onClose();
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => {
      document.body.style.overflow = "";
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white border border-slate-100 rounded-3xl shadow-2xl max-w-sm w-full overflow-hidden font-body animate-in fade-in zoom-in-95 duration-150 relative p-6 flex flex-col items-center">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-slate-400 hover:text-slate-650 p-1.5 rounded-xl transition-colors cursor-pointer"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Warning Icon Container */}
        <div className="w-14 h-14 bg-rose-50 text-rose-500 rounded-2xl flex items-center justify-center mb-4 shadow-sm">
          <LogOut className="w-7 h-7 stroke-[2.5]" />
        </div>

        {/* Text Details */}
        <h3 className="text-base font-extrabold text-slate-800 font-heading mb-2">
          Confirm Sign Out
        </h3>
        
        <p className="text-xs text-slate-500 text-center leading-relaxed font-body mb-6 px-2">
          Are you sure you want to end your secure session? You will need to log back in to access decrypted corporate leaks.
        </p>

        {/* Buttons Row */}
        <div className="flex gap-3 w-full font-heading">
          <button
            onClick={onClose}
            className="flex-1 bg-slate-50 hover:bg-slate-100 border border-slate-200 text-slate-650 font-bold py-3 px-4 rounded-xl text-xs transition-colors cursor-pointer text-center"
          >
            Keep Session
          </button>
          <button
            onClick={onConfirm}
            className="flex-1 bg-[#EF4444] hover:bg-[#DC2626] text-white font-extrabold py-3 px-4 rounded-xl text-xs shadow-sm shadow-red-100 hover:shadow-md transition-all cursor-pointer text-center"
          >
            Sign Out
          </button>
        </div>
      </div>
    </div>
  );
};
