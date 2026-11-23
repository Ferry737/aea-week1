# 0001 — Scope lock (Week 1)

Direction: simulation-first economic/agent laboratory for B2B customers. The product is not a
GTA clone, GTA integration, generic NPC engine, trading platform, broker, or real-money trader.

## Implemented in Week 1

- Config, per-agent deterministic RNG, canonical events + hash chain, tick engine, rule-based
  agents, in-memory double-entry ledger, runner, three test files, CI config.

## Not implemented and not to be added this week

Postgres, pgvector, NATS JetStream, Redis, LiteLLM, MCP, gVisor, Firecracker, OpenTelemetry,
Prometheus, Grafana, Tempo, trading connectors, dashboards, real money, real wallets, exchange,
DeFi, blockchain ledger, GTA assets/name/logo, 3D engine, all-agent LLM cortex, unlimited context,
write-capable MCP, generated code outside sandbox, multi-currency/FX, derivatives, loans/interest,
shared economy between runs, PII, plugin marketplace, mobile app, GraphQL, memory retrieval,
learned policies, market order book beyond the minimum needed for the ledger test.

## Notes

The in-memory ledger is a deliberate Week-1 simplification. Its interface is designed so a
Postgres implementation can replace it without changing the reducer or event contracts.
