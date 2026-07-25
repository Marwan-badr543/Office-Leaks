import { useEffect } from "react";

export function useScrollMemory(contextKey: string, active: boolean = true) {
  const storageKey = `office_leaks_scroll_${contextKey}`;

  // Restore scroll position on mount/activation
  useEffect(() => {
    if (!active) return;

    try {
      const savedPosition = sessionStorage.getItem(storageKey);
      if (savedPosition !== null) {
        const y = parseInt(savedPosition, 10);
        if (!isNaN(y)) {
          requestAnimationFrame(() => {
            window.scrollTo({ top: y, behavior: "instant" as ScrollBehavior });
          });
        }
      }
    } catch (err) {
      console.warn("Failed to restore scroll position:", err);
    }
  }, [contextKey, active, storageKey]);

  // Save scroll position on scroll / unmount / context change
  useEffect(() => {
    if (!active) return;

    const handleScroll = () => {
      try {
        sessionStorage.setItem(storageKey, window.scrollY.toString());
      } catch (err) {
        console.warn("Failed to save scroll position:", err);
      }
    };

    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => {
      window.removeEventListener("scroll", handleScroll);
    };
  }, [contextKey, active, storageKey]);
}
