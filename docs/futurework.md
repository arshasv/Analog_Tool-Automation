# Future Work: AI Agent Integration & Next-Generation Features

## Status
**Draft** — May 2026

---

## Overview

xEDA's current architecture already provides:
- A **topology role system** (`app/services/topology.py`) with constraint-aware enumeration
- A **modular netlist synthesizer** (`app/services/architecture_synthesizer.py`) that assembles SPICE netlists from composable blocks
- A **brute-force architecture search** (`pipeline_executor.py:run_architecture_search()`) and **design memory** (`data/results/design_memory.jsonl`)

This document outlines how to evolve these foundations into an AI-guided design agent.

---

## 1. Natural Language → Netlist Generation

### Goal
Allow users to describe circuit requirements in natural language and have an LLM generate a syntactically correct, simulation-ready netlist.

### Proposed Implementation

| Component | File | Description |
|-----------|------|-------------|
| LLM Interface | `app/agents/llm_interface.py` | Wraps LLM API (GPT-4, Claude, CodeLlama), returns structured topology dict + parameter ranges |
| Generate Endpoint | `app/api/v1/generate` | Accepts NL spec, calls LLM, feeds result into `ArchitectureSynthesizer`, runs simulation, returns results |
| RAG over Design Memory | `app/agents/experience_buffer.py` | Retrieves past (spec → result) pairs from `.jsonl` as in-context examples for the LLM |

### Flow
```
User: "low-power two-stage opamp with 60dB gain"
  → POST /api/v1/generate
  → LLM returns {"topology": {"input": "diff_n", "gain": "two_stage", ...}, "params": {...}}
  → ArchitectureSynthesizer.generate_netlist_string(topology, params)
  → NgSpiceExecutor simulates
  → Results stored in design memory + returned to user
  → (Optional) LLM proposes fixes if metrics miss spec
```

### Key Considerations
- Constrain LLM output to the role enums defined in `topology.py` to guarantee synthesizable topologies
- Use `_check_constraints()` to validate before synthesis
- Design memory should grow into a vector-indexed RAG store (e.g. Chroma, FAISS) for fast similarity retrieval

---

## 2. Learned Architecture Search

### Current State
`run_architecture_search()` brute-forces `enumerate_valid_topologies()[:20]` with `n=3` random parameter samples — no learning across iterations.

### Proposed Upgrade

#### Phase 1 — Surrogate-Guided Search
Replace brute-force enumeration with a learned surrogate (e.g. Bayesian optimization, small GNN):

1. **Train on design memory**: Each entry in `.jsonl` is a (topology, params → metrics) training point
2. **Predict promising regions**: Surrogate scores unexplored topologies without simulation
3. **Acquire top candidates**: Simulate only the top-N predicted by the surrogate
4. **Update model**: Feed real simulation results back to improve predictions

#### Phase 2 — RL-Based Topology Exploration
- Treat topology selection + parameter suggestion as a reinforcement learning episode
- Reward = simulated performance score
- Policy network (small MLP or GNN) proposes next (topology, params) to try
- Experience replay buffer over design memory

### Implementation Sketch

| Component | File | Description |
|-----------|------|-------------|
| Surrogate Model | `app/agents/topology_predictor.py` | Lightweight regressor (XGBoost or 2-layer NN) over encoded topology + params |
| Acquisition Function | `app/agents/search_policy.py` | Expected Improvement or UCB over surrogate predictions |
| RL Agent | `app/agents/rl_agent.py` | Policy network + replay buffer for iterative topology exploration |

### Integration
```python
# Current (brute-force):
topologies = enumerate_valid_topologies()[:20]
for topo in topologies:
    for params in random_sample_params(topo, n=3):
        simulate(...)

# Future (learned):
agent = TopologyPredictor()
agent.load_design_memory("data/results/design_memory.jsonl")
candidates = agent.propose_candidates(specs, n=10)
for topo, params in candidates:
    result = simulate(topo, params)
    agent.ingest_result(topo, params, result.metrics)
```

---

## 3. Suggested Package Layout

```
app/
├── agents/                      # NEW — AI agent package
│   ├── __init__.py
│   ├── llm_interface.py         # NL → structured topology/params
│   ├── topology_predictor.py    # Surrogate model for architecture search
│   ├── search_policy.py         # Acquisition / exploration policy
│   ├── rl_agent.py              # Reinforcement learning agent
│   └── experience_buffer.py     # RAG / replay buffer over design memory
├── api/
│   └── v1_agent.py              # NEW — /generate, /architecture-search-stream
└── services/
    ├── architecture_synthesizer.py  # EXISTS — extend for LLM-generated topologies
    ├── pipeline_executor.py         # EXISTS — extend run_architecture_search
    └── topology.py                  # EXISTS — extend with learned scoring
```

### New API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/generate` | Natural language → netlist → simulate → return results |
| `POST` | `/api/v1/architecture-search` | Learned architecture search with streaming progress |
| `GET` | `/api/v1/design-memory` | Query past design points (RAG-ready) |

---

## 4. Infrastructure Changes

### Design Memory Evolution
| Phase | Storage | Query |
|-------|---------|-------|
| Current | `.jsonl` file | Sequential scan |
| Near | SQLite | Filter by topology, metrics range |
| Future | Vector DB (Chroma/FAISS) | Semantic similarity over NL specs + metrics |

### Configuration (`app/core/config.py`)
Add:
```python
LLM_MODEL: str = "gpt-4"           # or local model
LLM_API_KEY: str = ""               # from env
AGENT_LEARNING_RATE: float = 0.01
DESIGN_MEMORY_VECTOR_DB: str = "./data/design_memory.vectordb"
```

---

## 5. Open Questions

1. **LLM hallucination**: How to guarantee syntactically valid, manufacturable netlists from free-form NL output? Potential mitigation: structured output parsing + topology constraint validation as a hard filter.
2. **Simulation cost**: Each SPICE run is O(seconds). Can a fast analytical estimator (pre-sim) reduce the search space before invoking NGSpice?
3. **Cold start**: Design memory will be sparse initially. Use transfer learning from published analog design datasets (e.g. CircuitNet, open-source PDK benchmarks)?
4. **Frontend**: How should the NL interface and architecture search results be surfaced in the React UI? Consider a chat-style pane or a guided form that fills topology roles.

---

## 6. Roadmap

| Milestone | Effort | Dependencies |
|-----------|--------|--------------|
| LLM interface + `/generate` endpoint | 2-3 weeks | LLM API access, structured output parsing |
| Design memory → vector RAG store | 1 week | Embedding model, vector DB library |
| Surrogate model for search | 2-4 weeks | Training pipeline, feature encoding for topologies |
| RL agent + streaming search UI | 3-5 weeks | Surrogate model, frontend chat/candidate browser |
| End-to-end evaluation | Ongoing | User testing, metric correlation vs. manual design |

---

*This document is a living proposal. Update as the AI agent features are implemented and new research directions emerge.*
