# Makefile for Architecture Governance Toolkit

.PHONY: help build-analysis-image run-analysis adr-new artifacts-dir

ANALYSIS_IMAGE=analysis:local
ARTIFACTS_DIR=artifacts

help:
	@echo "Architecture Governance Toolkit - Available Commands:"
	@echo ""
	@echo "  make artifacts-dir          - Create artifacts directory"
	@echo "  make build-analysis-image   - Build Docker analysis image"
	@echo "  make run-analysis           - Run analysis in Docker"
	@echo "  make adr-new TITLE='...'    - Create new ADR"
	@echo "  make clean                  - Remove artifacts directory"
	@echo ""

artifacts-dir:
	mkdir -p $(ARTIFACTS_DIR)/sbom $(ARTIFACTS_DIR)/timeseries

build-analysis-image:
	docker build -t $(ANALYSIS_IMAGE) -f Dockerfile.analysis .

run-analysis: artifacts-dir
	docker run --rm -v $(PWD):/workspace -w /workspace $(ANALYSIS_IMAGE) \
		bash -lc "bash scripts/gen_sbom.sh --out artifacts/sbom --ref \$$(git rev-parse HEAD)"

adr-new:
	@if [ -z "$(TITLE)" ]; then \
		echo "Error: TITLE is required. Usage: make adr-new TITLE='Decision Title'"; \
		exit 1; \
	fi
	bash scripts/adr_new.sh "$(TITLE)"

clean:
	rm -rf $(ARTIFACTS_DIR)

# Analysis pipeline targets (require Python and tools installed locally)
sbom:
	bash scripts/gen_sbom.sh --out artifacts/sbom --ref $$(git rev-parse HEAD)

hotspots: artifacts-dir
	@echo "Generating complexity metrics..."
	@mkdir -p artifacts
	@# Placeholder - replace with actual complexity tool
	@echo '{}' > artifacts/complexity.json
	@echo "Generating churn metrics..."
	@git log --since=90.days --name-only --pretty=format: 2>/dev/null | sort | grep -v '^$$' | uniq -c > artifacts/churn.txt || echo "" > artifacts/churn.txt
	@echo "Merging hotspots..."
	@python3 scripts/hotspot_merge.py --churn artifacts/churn.txt --complexity artifacts/complexity.json --out artifacts/hotspots.json 2>/dev/null || echo "[WARN] hotspot_merge.py requires adjustments"

ownership: artifacts-dir
	python3 scripts/ownership_diff.py --out artifacts/ownership.json

drift: artifacts-dir
	@# Requires current_graph.json and previous_graph.json
	@echo '{"nodes":[],"edges":[],"meta":{"ref":"'$$(git rev-parse HEAD)'"}}' > artifacts/current_graph.json
	@if [ ! -f artifacts/previous_graph.json ]; then cp artifacts/current_graph.json artifacts/previous_graph.json; fi
	python3 scripts/scan_drift.py --current artifacts/current_graph.json --previous artifacts/previous_graph.json --out artifacts/drift_report.json || true

risk: artifacts-dir
	python3 scripts/risk_update.py \
		--hotspots artifacts/hotspots.json \
		--drift artifacts/drift_report.json \
		--ownership artifacts/ownership.json \
		--out artifacts/consolidated_risk.json

full-analysis: hotspots ownership drift risk
	@echo "Full analysis complete. Check artifacts/ directory."
