import { useState, useEffect, useCallback } from "react";

interface UseKeyboardNavigationOptions {
  itemCount: number;
  onLike?: (index: number) => void;
  onComment?: (index: number) => void;
  enabled?: boolean;
}

export function useKeyboardNavigation({
  itemCount,
  onLike,
  onComment,
  enabled = true,
}: UseKeyboardNavigationOptions) {
  const [selectedIndex, setSelectedIndex] = useState<number>(-1);

  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (!enabled || itemCount === 0) return;

      // Ignore key events when user is typing in form inputs
      const target = e.target as HTMLElement;
      if (
        target.tagName === "INPUT" ||
        target.tagName === "TEXTAREA" ||
        target.tagName === "SELECT" ||
        target.isContentEditable
      ) {
        return;
      }

      const key = e.key.toLowerCase();

      if (key === "j") {
        e.preventDefault();
        setSelectedIndex((prev) => {
          const next = Math.min(prev + 1, itemCount - 1);
          return next;
        });
      } else if (key === "k") {
        e.preventDefault();
        setSelectedIndex((prev) => {
          const next = Math.max(prev - 1, 0);
          return next;
        });
      } else if (key === "l") {
        if (selectedIndex >= 0 && selectedIndex < itemCount && onLike) {
          e.preventDefault();
          onLike(selectedIndex);
        }
      } else if (key === "c" || key === "m") {
        if (selectedIndex >= 0 && selectedIndex < itemCount && onComment) {
          e.preventDefault();
          onComment(selectedIndex);
        }
      }
    },
    [enabled, itemCount, selectedIndex, onLike, onComment]
  );

  useEffect(() => {
    window.addEventListener("keydown", handleKeyDown);
    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [handleKeyDown]);

  // Reset index if itemCount changes below current index
  useEffect(() => {
    if (selectedIndex >= itemCount && selectedIndex !== -1) {
      setSelectedIndex(itemCount > 0 ? 0 : -1);
    }
  }, [itemCount, selectedIndex]);

  return { selectedIndex, setSelectedIndex };
}
