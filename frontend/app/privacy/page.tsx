import type { Metadata } from "next";
import { Footer } from "@/components/landing/Footer";
import { NavigationBar } from "@/components/landing/NavigationBar";

export const metadata: Metadata = {
  title: "Privacy Policy | Personal AI Agent",
  description:
    "How Personal AI Agent collects, uses, stores, and protects your data.",
};

const LAST_UPDATED = "April 27, 2026";

export default function PrivacyPage() {
  return (
    <div className="min-h-screen bg-white text-zinc-900 dark:bg-zinc-950 dark:text-zinc-50">
      <NavigationBar />
      <main className="mx-auto max-w-4xl px-4 py-10 sm:px-6 sm:py-14">
        <h1 className="text-3xl font-bold tracking-tight sm:text-4xl">
          Privacy Policy
        </h1>
        <p className="mt-3 text-sm text-zinc-600 dark:text-zinc-300">
          Last updated: {LAST_UPDATED}
        </p>

        <div className="mt-8 space-y-8 text-sm leading-7 text-zinc-700 dark:text-zinc-200">
          <section className="space-y-3">
            <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-50">
              1. Scope
            </h2>
            <p>
              This Privacy Policy explains how Personal AI Agent collects, uses,
              and shares information when you use our website and services. By
              using the service, you agree to the practices described here.
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-50">
              2. Information We Collect
            </h2>
            <ul className="list-disc space-y-2 pl-5">
              <li>
                <strong>Account data:</strong> name, email address, and profile
                metadata from sign-in providers.
              </li>
              <li>
                <strong>Connected integration data:</strong> tokens and metadata
                required to connect services like GitHub, Notion, Calendar, and
                Gmail.
              </li>
              <li>
                <strong>Usage data:</strong> prompts, plan execution logs, tool
                invocation details, and error logs used to operate and improve
                the service.
              </li>
              <li>
                <strong>Technical data:</strong> IP address, user agent,
                browser/device information, and request diagnostics.
              </li>
            </ul>
          </section>

          <section className="space-y-3">
            <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-50">
              3. How We Use Information
            </h2>
            <ul className="list-disc space-y-2 pl-5">
              <li>Provide authentication, account access, and integrations.</li>
              <li>Execute requested tasks and multi-tool workflows.</li>
              <li>Maintain system reliability, security, and abuse prevention.</li>
              <li>Diagnose bugs, monitor performance, and improve product quality.</li>
              <li>Comply with legal obligations and enforce our Terms.</li>
            </ul>
          </section>

          <section className="space-y-3">
            <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-50">
              4. Legal Bases for Processing
            </h2>
            <p>
              We process personal data based on one or more of the following:
              contractual necessity (to provide the service), legitimate
              interests (security and product improvement), consent (where
              required), and legal obligations.
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-50">
              5. Cookies and Session Storage
            </h2>
            <p>
              We use cookies and similar technologies for authentication, session
              management, security controls, and preference persistence. You can
              manage cookies in your browser settings, but disabling essential
              cookies may prevent core functionality.
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-50">
              6. Data Sharing
            </h2>
            <p>We do not sell personal data. We may share data with:</p>
            <ul className="list-disc space-y-2 pl-5">
              <li>
                Infrastructure and hosting providers required to run the
                service.
              </li>
              <li>
                Integration providers at your direction (for example, API calls
                to connected accounts).
              </li>
              <li>
                Professional advisors or authorities when legally required.
              </li>
            </ul>
          </section>

          <section className="space-y-3">
            <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-50">
              7. Data Retention
            </h2>
            <p>
              We retain information only as long as necessary for service
              operation, security, legal compliance, and dispute resolution.
              Retention periods may vary based on data type and applicable law.
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-50">
              8. Security
            </h2>
            <p>
              We apply administrative, technical, and organizational safeguards
              designed to protect your data. No system is perfectly secure, and
              we cannot guarantee absolute security.
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-50">
              9. International Data Transfers
            </h2>
            <p>
              Your information may be processed in countries other than your own.
              Where required, we use safeguards intended to protect transferred
              personal information.
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-50">
              10. Your Rights
            </h2>
            <p>
              Depending on your jurisdiction, you may have rights to access,
              correct, delete, restrict, or object to certain processing. You
              may also have rights related to portability and consent withdrawal.
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-50">
              11. Children&apos;s Privacy
            </h2>
            <p>
              The service is not intended for children under 13 (or the minimum
              age required by local law). We do not knowingly collect personal
              information from children.
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-50">
              12. Changes to This Policy
            </h2>
            <p>
              We may update this Privacy Policy from time to time. The updated
              version will be posted on this page with a revised last-updated
              date shown at the top of this policy.
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-50">
              13. Contact
            </h2>
            <p>
              For privacy requests or questions, contact us at{" "}
              <a
                href="mailto:privacy@personalaiagent.app"
                className="underline underline-offset-4"
              >
                privacy@personalaiagent.app
              </a>
              .
            </p>
          </section>
        </div>
      </main>
      <Footer />
    </div>
  );
}
