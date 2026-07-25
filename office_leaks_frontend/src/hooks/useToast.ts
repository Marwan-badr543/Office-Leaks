import { useState, useCallback } from "react";

export interface ToastMessage {
  id: string;
  message: string;
  type: "error" | "info" | "success";
  actionText?: string;
  onAction?: () => void;
}

export function useToast() {
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  const addToast = useCallback(
    (
      message: string,
      type: "error" | "info" | "success" = "info",
      actionText?: string,
      onAction?: () => void,
      duration: number = 4000
    ) => {
      const id = Math.random().toString(36).substring(2, 9);
      const newToast: ToastMessage = { id, message, type, actionText, onAction };

      setToasts((prev) => [...prev, newToast]);

      if (duration > 0) {
        setTimeout(() => {
          setToasts((prev) => prev.filter((t) => t.id !== id));
        }, duration);
      }
    },
    []
  );

  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  return { toasts, addToast, removeToast };
}
