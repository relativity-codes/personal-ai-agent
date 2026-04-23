"use client";

import { GoogleLogin, GoogleOAuthProvider } from "@react-oauth/google";
import { useRouter } from "next/navigation";
import { useState } from "react";

const SignIn = () => {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);

  const handleSuccess = async (credentialResponse: any) => {
    const idToken = credentialResponse.credential;
    if (!idToken) {
      setError("Failed to get ID token from Google.");
      return;
    }

    try {
      const response = await fetch("/api/v1/auth/google", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ id_token: idToken }),
      });

      if (response.ok) {
        // The backend sets a cookie, so we can just redirect.
        router.push("/dashboard"); // Redirect to the home page
      } else {
        const errorData = await response.json();
        setError(errorData.detail || "Login failed. Please try again.");
      }
    } catch (err) {
      setError("An error occurred during login.");
      console.error(err);
    }
  };

  const handleError = () => {
    setError("Login with Google failed. Please try again.");
  };

  return (
    <GoogleOAuthProvider clientId={process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID || ""}>
      <div className="flex flex-col items-center gap-4">
        <GoogleLogin onSuccess={handleSuccess} onError={handleError} useOneTap />
        {error && <p className="text-red-500">{error}</p>}
      </div>
    </GoogleOAuthProvider>
  );
};

export default SignIn;
