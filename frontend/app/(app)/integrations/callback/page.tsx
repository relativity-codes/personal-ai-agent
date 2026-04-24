"use client";

import { Suspense, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { exchangeGoogleCode } from "@/lib/integrations/api";

function CallbackContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [status, setStatus] = useState("Processing authorization...");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const code = searchParams.get("code");
    if (!code) {
      setError("No authorization code found in URL.");
      return;
    }

    const exchange = async () => {
      const redirectUri = `${window.location.origin}/integrations/callback`;
      const res = await exchangeGoogleCode(code, redirectUri);
      if (res.success) {
        setStatus("Authorization successful! Redirecting...");
        setTimeout(() => router.push("/integrations"), 1500);
      } else {
        setError(res.error);
      }
    };

    void exchange();
  }, [searchParams, router]);

  return (
    <div className="flex min-h-[400px] flex-col items-center justify-center p-4 text-center">
      {!error ? (
        <>
          <div className="mb-4 h-8 w-8 animate-spin rounded-full border-4 border-zinc-200 border-t-zinc-900" />
          <p className="text-zinc-600 dark:text-zinc-400">{status}</p>
        </>
      ) : (
        <div className="max-w-md rounded-2xl border border-red-200 bg-red-50 p-6 dark:border-red-900/50 dark:bg-red-950/30">
          <h1 className="text-lg font-semibold text-red-900 dark:text-red-100">
            Connection Failed
          </h1>
          <p className="mt-2 text-sm text-red-800 dark:text-red-200">{error}</p>
          <button
            onClick={() => router.push("/integrations")}
            className="mt-6 inline-flex h-10 items-center justify-center rounded-lg bg-red-900 px-4 text-sm font-semibold text-white transition hover:bg-red-800 dark:bg-red-800 dark:hover:bg-red-700"
          >
            Back to Integrations
          </button>
        </div>
      )}
    </div>
  );
}

export default function IntegrationCallbackPage() {
  return (
    <Suspense
      fallback={
        <div className="flex min-h-[400px] items-center justify-center">
          Loading...
        </div>
      }
    >
      <CallbackContent />
    </Suspense>
  );
}
