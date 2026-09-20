# ConnectoView 3D — Fruit Fly Connectome Web Visualizer

Lightweight Python pipeline: **neuPrint → navis → Plotly WebGL → standalone HTML**.
Implements PRD `FR-1.1 … FR-4.2`. End-user dashboard is zero-footprint
(single `.html`, CDN Plotly, no backend).

## Layout

| Path | Purpose |
|---|---|
| `src/connectoview.py` | Canonical pipeline (demo scene + live neuPrint pipeline + CLI) |
| `connectoview.py` | Thin shim forwarding to `src.connectoview.cli` |
| `tests/test_connectoview.py` | Demo-scene tests (dependency-free) |
| `tests/test_live_pipeline.py` | Live-pipeline offline tests (synthetic data, no token) |
| `output/connectoview-demo.html` | Dependency-free synthetic demo (regenerate: `--demo`) |
| `output/connectoview-offline.html` | Plotly offline synthetic export (regenerate: `--offline`) |
| `.env.example` | `NEUPRINT_APPLICATION_CREDENTIALS=<token>` template |

## Quickstart

```bash
pip install -r requirements.txt
# demo + tests need only the stdlib
python -m src.connectoview --demo
python -m unittest discover -s tests -v
```

Token source: https://neuprint.janelia.org/ user menu after login.

```bash
cp .env.example .env  # set NEUPRINT_APPLICATION_CREDENTIALS
python -m src.connectoview --bodyIds 5813027016,734404633 \
  --rois "MB(R),EB,AL(R)" --dataset hemibrain:v1.2.1 \
  --weight-threshold 5 --output output/connectoview-live.html
```

Offline Plotly export (no token/server; exercises the full figure builder):

```bash
python -m src.connectoview --offline --output output/connectoview-offline.html
```

Open any `output/*.html` in Chrome/Firefox/Safari/Edge — no install, no backend (NFR).

## PRD mapping (`src/connectoview.py`)

| PRD | Implementation |
|---|---|
| FR-1.1 handshake | `get_client()` → `neuprint.Client(server, dataset, token)` |
| FR-1.2 skeletons | `fetch_skeleton()` → `fetch_skeleton(body, heal=True)` + `to_navis_neuron()` (`navis.TreeNeuron`) |
| FR-1.3 synapses X,Y,Z pre/post | `fetch_synapses_split()` → `fetch_synapses(NC(bodyId), SC(primary_only=True))`, split `type==pre/post` |
| FR-1.4 ROI meshes | `fetch_roi_meshes()` → `Client.fetch_roi_mesh(roi)` + `parse_obj_mesh()` (`.obj`, fan-triangulation, decimation); e.g. `MB(R), EB, AL` |
| FR-2.1 weight gate `>=X` | `fetch_connectivity_filtered()` → `fetch_simple_connections(..., min_weight=X)`; demo adds a client-side weight slider (1–12) |
| FR-2.2 corrupt hygiene | `dropna(subset=[x,y,z])` + finite filter; corrupt rows logged and omitted, render continues |
| FR-3.1 dark canvas | live: `template="plotly_dark"`; demo: dark CSS + dark Plotly layout |
| FR-3.2 palette | neurons `#39FF14/#FF10F0/...`, inputs `#3B82F6` size 2, outputs `#EF4444` size 3, mesh `gray` opacity `0.15` + 0–15% slider |
| FR-3.3 toggle legend | `showlegend=True` + "Toggle layers" legend + "Show all" button (single-click hide/show) |
| FR-4.1 standalone | `export_neuprint_html()` → `fig.write_html(full_html=True)` / demo `build_html()` single file |
| FR-4.2 CDN <5MB | `include_plotlyjs="cdn"` (live) / `cdn.plot.ly` script tag (demo); warns if `>5MB` (offline output ~160KB) |
| Perf 60 FPS | one `Scatter3d(lines)` per neuron (None-separated), mesh `max_faces=20000` decimation, native WebGL |

## Notes

- `neuprint-python` / `navis` / `plotly` / `pandas` are required only for live/offline
  mode. Demo + tests run on the stdlib.
- ROI meshes are visualization-only (per neuPrint docs), decimated for iGPU frame rate.
- Cross-browser: pure client-side HTML + CDN Plotly, no extensions.
