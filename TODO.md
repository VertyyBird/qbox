# Production Readiness TODO

Qbox has a functional browser-based Q&A MVP. The work below is prioritized to
make it safe and reliable for real users, beginning with a controlled public
beta and progressing toward a broader launch.

## P0: Correctness and Moderation

- [ ] Fix answer-report resolution so grouped reports use the correct report or
  answer identifier and resolving a group closes every intended report.
- [ ] Add explicit admin actions to hide, restore, or remove reported answers.
- [ ] Ensure hidden or removed content is excluded consistently from feeds,
  profiles, permalinks, and search or sharing surfaces.
- [ ] Allow authorized admins to moderate content without being the question
  receiver, while retaining receiver-only controls for ordinary users.
- [ ] Fix offset-naive versus offset-aware datetime handling for expiring
  blocks, and test expiration after database records are reloaded.
- [ ] Define and enforce what user and IP blocks prevent across questions,
  answers, reports, registration, and login.
- [ ] Add regression tests for every moderation and block action, including
  authorization failures and multiple reports against one answer.

## P0: Production Runtime and Security

- [ ] Disable Flask debug mode outside local development.
- [ ] Run the application with a production WSGI server behind a configured,
  trusted reverse proxy.
- [ ] Validate required environment variables at startup and fail closed when
  production secrets or host settings are missing.
- [ ] Configure secure session cookies (`Secure`, `HttpOnly`, and an appropriate
  `SameSite` policy) and require HTTPS.
- [ ] Add HSTS, Content Security Policy, and other appropriate response security
  headers.
- [ ] Configure proxy-header trust for the exact deployment topology so client
  IP addresses cannot be spoofed through forwarded headers.
- [ ] Avoid returning raw exception details to users; log a request or incident
  identifier instead.
- [ ] Change logout to a CSRF-protected state-changing request.

## P0: Abuse Resistance and Input Validation

- [ ] Add shared, atomic rate limiting for registration, login, question
  submission, answer reporting, and other write-heavy public endpoints.
- [ ] Prevent duplicate or automated report flooding by the same account or IP.
- [ ] Add server-side length and format validation matching every database
  constraint, including usernames, email addresses, passwords, questions,
  bios, avatar URLs, block reasons, and report reasons.
- [ ] Establish password-strength requirements and login-attempt throttling.
- [ ] Add challenge-based bot protection when abuse levels justify it.
- [ ] Review avatar URL fetching for redirect, DNS, content-type, download-size,
  and server-side request-forgery protections.

## P1: Database and Data Safety

- [ ] Use PostgreSQL for a concurrent public deployment; retain SQLite only for
  development and small single-process installations.
- [ ] Add explicit foreign-key deletion behavior and database integrity
  constraints for users, questions, answers, reports, and blocks.
- [ ] Add or verify indexes for feed ordering, unanswered-question lookup,
  report queues, block lookup, and rate-limit queries.
- [ ] Test migrations against populated databases and PostgreSQL, not only a
  fresh SQLite database.
- [ ] Automate `flask db upgrade` as a controlled deployment step.
- [ ] Define backup retention and perform a documented restoration test.

## P1: Tests, Dependencies, and CI

- [ ] Add `pytest` and other development tools to a reproducible development
  dependency file.
- [ ] Pin production dependencies and establish a regular update process.
- [ ] Add tests for authorization, ownership, anonymous-sender privacy, CSRF,
  rate-limit boundaries, moderation, reporting, blocks, and block expiration.
- [ ] Add browser-level tests for registration, asking, answering, sharing, and
  admin moderation workflows.
- [ ] Add CI checks for tests, migration consistency, formatting, static
  analysis, dependency auditing, and clean rendered templates.

## P1: Operations and Observability

- [ ] Add lightweight liveness and readiness endpoints.
- [ ] Emit structured application and audit logs without exposing secrets or
  unnecessary personal data.
- [ ] Add error reporting, uptime checks, resource monitoring, and actionable
  alerts.
- [ ] Document deployment, rollback, migration, backup, and incident-response
  procedures.
- [ ] Add a safe CLI workflow for creating and managing administrators.

## P2: Account and Product Readiness

- [ ] Add email verification, password reset, session revocation, and account
  deletion workflows.
- [ ] Supply every referenced Open Graph image and generate absolute canonical
  and social-sharing URLs.
- [ ] Improve modal accessibility, keyboard and focus behavior, responsive feed
  layout, and empty and error states.
- [ ] Add notifications for new questions when the delivery and privacy model is
  defined.
- [ ] Publish terms of service, privacy, community, and moderation policies.
- [ ] Explain clearly that anonymous sender information and IP addresses may be
  retained for moderation, including retention and access rules.

## Launch Gates

A controlled public beta is ready only when all P0 items are complete and:

- [ ] The complete automated test suite passes in CI.
- [ ] Migrations succeed against a production-like database containing data.
- [ ] Moderators can report, inspect, hide, restore, resolve, and block through
  tested end-to-end flows.
- [ ] Backup restoration and rollback procedures have been exercised.
- [ ] No production process exposes Flask debug mode or an untrusted proxy
  configuration.

A broader launch additionally requires the P1 operational, database, and CI
work plus published user-facing privacy and moderation policies.
