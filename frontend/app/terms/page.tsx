import type { Metadata } from "next";
import { Footer } from "@/components/landing/Footer";
import { NavigationBar } from "@/components/landing/NavigationBar";

export const metadata: Metadata = {
  title: "Terms of Service | Personal AI Agent",
  description: "Terms governing use of Personal AI Agent.",
};

const LAST_UPDATED = "April 27, 2026";

export default function TermsPage() {
  return (
    <div className="min-h-screen bg-white text-zinc-900 dark:bg-zinc-950 dark:text-zinc-50">
      <NavigationBar />
      <main className="mx-auto max-w-4xl px-4 py-10 sm:px-6 sm:py-14">
        <h1 className="text-3xl font-bold tracking-tight sm:text-4xl">
          Terms of Service
        </h1>
        <p className="mt-3 text-sm text-zinc-600 dark:text-zinc-300">
          Last updated: {LAST_UPDATED}
        </p>

        <div className="mt-8 space-y-8 text-sm leading-7 text-zinc-700 dark:text-zinc-200">
          <section className="space-y-3">
            <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-50">
              1. Agreement to Terms
            </h2>
            <p>
              By using Personal AI Agent, you agree to these Terms of Service.
              If you do not agree, do not use the service.
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-50">
              2. Eligibility and Accounts
            </h2>
            <ul className="list-disc space-y-2 pl-5">
              <li>You must be legally able to enter into binding agreements.</li>
              <li>
                You are responsible for maintaining account credentials and all
                activity under your account.
              </li>
              <li>
                You must provide accurate information and keep it updated.
              </li>
            </ul>
          </section>

          <section className="space-y-3">
            <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-50">
              3. Service Description
            </h2>
            <p>
              Personal AI Agent helps users plan and execute workflows across
              connected services such as GitHub, Notion, Google Calendar, and
              Gmail. Features may evolve over time and can vary by account,
              plan, or region.
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-50">
              4. Acceptable Use
            </h2>
            <p>You agree not to:</p>
            <ul className="list-disc space-y-2 pl-5">
              <li>
                Use the service for unlawful, fraudulent, harmful, or abusive
                activities.
              </li>
              <li>
                Attempt unauthorized access, interfere with operations, or bypass
                security controls.
              </li>
              <li>
                Use the service to distribute malware, spam, or harmful code.
              </li>
              <li>
                Infringe intellectual property or privacy rights of others.
              </li>
            </ul>
          </section>

          <section className="space-y-3">
            <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-50">
              5. Integrations and Third-Party Services
            </h2>
            <p>
              When you connect third-party services, you authorize us to access
              and process data needed to perform requested actions. Third-party
              services are governed by their own terms and privacy policies, and
              we are not responsible for their availability or behavior.
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-50">
              6. AI Output and User Responsibility
            </h2>
            <p>
              AI-generated outputs may be incomplete or inaccurate. You are
              responsible for reviewing outputs and actions before relying on
              them in production, legal, medical, financial, or safety-critical
              contexts.
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-50">
              7. Intellectual Property
            </h2>
            <p>
              We retain rights to the service, software, and branding. You retain
              rights to content you submit, to the extent permitted by law and
              third-party terms. You grant us rights necessary to operate and
              improve the service.
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-50">
              8. Fees and Billing
            </h2>
            <p>
              Paid features, if offered, will be billed as described at purchase.
              Unless stated otherwise, fees are non-refundable except where
              required by law.
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-50">
              9. Suspension and Termination
            </h2>
            <p>
              We may suspend or terminate access if you violate these Terms,
              create risk, or as required by law. You may stop using the service
              at any time.
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-50">
              10. Disclaimers
            </h2>
            <p>
              The service is provided on an as-is and as-available basis
              without warranties of any kind, express or implied, to the maximum
              extent permitted by law.
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-50">
              11. Limitation of Liability
            </h2>
            <p>
              To the fullest extent permitted by law, we are not liable for
              indirect, incidental, special, consequential, or punitive damages,
              or for lost profits, data, use, or goodwill.
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-50">
              12. Indemnification
            </h2>
            <p>
              You agree to defend, indemnify, and hold harmless Personal AI
              Agent from claims arising out of your use of the service or
              violation of these Terms.
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-50">
              13. Governing Law
            </h2>
            <p>
              These Terms are governed by applicable laws of your service
              operator&apos;s jurisdiction, without regard to conflict-of-law
              principles, unless local law requires otherwise.
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-50">
              14. Changes to Terms
            </h2>
            <p>
              We may update these Terms from time to time. Continued use after
              updates become effective constitutes acceptance of the revised
              Terms.
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-50">
              15. Contact
            </h2>
            <p>
              For legal notices or questions about these Terms, contact{" "}
              <a
                href="mailto:legal@personalaiagent.app"
                className="underline underline-offset-4"
              >
                legal@personalaiagent.app
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
