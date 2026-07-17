import { useEffect, useState } from "react";

export type AsyncResource<T> =
  | { status: "loading" }
  | { status: "ready"; data: T }
  | { status: "failed"; message: string };

export function useAsyncResource<T>(
  key: string,
  loader: (signal: AbortSignal) => Promise<T>,
): AsyncResource<T> {
  const [resource, setResource] = useState<AsyncResource<T>>({ status: "loading" });

  useEffect(() => {
    const controller = new AbortController();
    setResource({ status: "loading" });
    void loader(controller.signal)
      .then((data) => setResource({ status: "ready", data }))
      .catch((error: unknown) => {
        if (!controller.signal.aborted) {
          setResource({
            status: "failed",
            message: error instanceof Error ? error.message : "Resource failed to load",
          });
        }
      });
    return () => controller.abort();
  }, [key, loader]);

  return resource;
}
