# Client Portal Hosting from CA Desktop - Architecture Analysis

## Problem Statement
When a CA's client accesses the client portal via the web, the request must reach the CA's desktop/laptop running the backend. This involves DNS resolution, networking, CORS, resource constraints, and security.

## Analysis Tasks
- [x] Review current backend config (host, port, CORS)
- [x] Review networking constraints (127.0.0.1 binding)
- [x] Review file streaming and document access
- [x] Review rate limiting and resource usage
- [x] Identify all blocking issues for external client access
- [ ] Document architecture options and recommendation

## Key Findings
See STATE.md for detailed analysis.
