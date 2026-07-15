import {
  type AnchorHTMLAttributes,
  type MouseEvent,
  useSyncExternalStore,
} from "react";

export type AppRoute =
  | { kind: "atlas" }
  | { kind: "models" }
  | { kind: "model"; slug: string }
  | { kind: "relation"; relationId: string }
  | { kind: "learn" }
  | { kind: "journey"; journeyId: string }
  | { kind: "not-found" };

const LOCATION_CHANGE_EVENT = "lolla:navigation";

function subscribe(listener: () => void): () => void {
  window.addEventListener("popstate", listener);
  window.addEventListener(LOCATION_CHANGE_EVENT, listener);
  return () => {
    window.removeEventListener("popstate", listener);
    window.removeEventListener(LOCATION_CHANGE_EVENT, listener);
  };
}

function locationSnapshot(): string {
  return `${window.location.pathname}${window.location.search}${window.location.hash}`;
}

export function useLocation(): URL {
  const snapshot = useSyncExternalStore(
    subscribe,
    locationSnapshot,
    () => "/atlas",
  );
  return new URL(snapshot, window.location.origin);
}

export function navigate(to: string, options: { replace?: boolean } = {}): void {
  const next = new URL(to, window.location.href);
  const current = new URL(window.location.href);
  if (
    next.pathname === current.pathname &&
    next.search === current.search &&
    next.hash === current.hash
  ) {
    return;
  }
  const method = options.replace ? "replaceState" : "pushState";
  window.history[method](null, "", `${next.pathname}${next.search}${next.hash}`);
  window.dispatchEvent(new Event(LOCATION_CHANGE_EVENT));
}

export function parseRoute(pathname: string): AppRoute {
  const parts = pathname.split("/").filter(Boolean);
  if (parts.length === 0 || (parts.length === 1 && parts[0] === "atlas")) {
    return { kind: "atlas" };
  }
  if (parts.length === 1 && parts[0] === "models") {
    return { kind: "models" };
  }
  if (parts.length === 2 && parts[0] === "models") {
    return { kind: "model", slug: safeDecode(parts[1]) };
  }
  if (parts.length === 2 && parts[0] === "relations") {
    return { kind: "relation", relationId: safeDecode(parts[1]) };
  }
  if (parts.length === 1 && parts[0] === "learn") {
    return { kind: "learn" };
  }
  if (parts.length === 2 && parts[0] === "learn") {
    return { kind: "journey", journeyId: safeDecode(parts[1]) };
  }
  return { kind: "not-found" };
}

type AppLinkProps = AnchorHTMLAttributes<HTMLAnchorElement> & {
  href: string;
  replace?: boolean;
};

export function AppLink({ href, replace, onClick, ...props }: AppLinkProps) {
  function handleClick(event: MouseEvent<HTMLAnchorElement>): void {
    onClick?.(event);
    if (
      event.defaultPrevented ||
      event.button !== 0 ||
      event.metaKey ||
      event.ctrlKey ||
      event.shiftKey ||
      event.altKey ||
      props.target === "_blank"
    ) {
      return;
    }
    const target = new URL(href, window.location.href);
    if (target.origin !== window.location.origin) {
      return;
    }
    event.preventDefault();
    navigate(href, { replace });
  }

  return <a href={href} onClick={handleClick} {...props} />;
}

function safeDecode(value: string | undefined): string {
  if (!value) {
    return "";
  }
  try {
    return decodeURIComponent(value);
  } catch {
    return "";
  }
}
