# Changelog

All notable changes to OrionAgent are documented in this file.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [1.0.0] — 2024-04-19 — *Professional Release*

### Added
- Rebranded from KwaiAgents → **OrionAgent** with production-grade structure
- New modular package layout: `orionagent/` with clear submodule separation
- `configs/default_config.yaml` — centralized YAML-based runtime configuration
- `.env.example` — secure API key management template
- `docs/quickstart.py` — beginner-friendly onboarding examples
- `scripts/` directory consolidating all inference and evaluation runners
- `tests/` directory scaffolded for future unit & integration tests
- CLI alias `orionagent` (legacy `kagentsys` preserved for compatibility)
- `CHANGELOG.md` — version history tracking

### Changed
- `requirements.txt` upgraded: `openai>=1.0.0`, grouped with comments
- `setup.py` modernized: Python 3.10+ requirement, PyPI classifiers, project URLs
- `.gitignore` expanded: covers model weights, JSONL outputs, local config overrides

### Fixed
- N/A (initial professional release)

---

## [0.0.1] — 2023-11-17 — *Initial Open-Source Release (KwaiAgents)*

### Added
- Initial open-source release of KAgentSys-Lite
- Qwen-7B-MAT and Baichuan2-13B-MAT model weights on HuggingFace
- KAgentInstruct: 200K+ agent fine-tuning dataset
- KAgentBench: 3,000+ automated evaluation samples
- Tools: web search, browser, weather, calendar, time utilities
- vLLM + FastChat GPU deployment support
- llama.cpp CPU inference support via GGUF quantized model
