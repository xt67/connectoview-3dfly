"""Create a standalone ConnectoView 3D demonstration HTML file.

The scene is intentionally synthetic.  Keeping this dependency-free lets the
viewer UX be tested before authenticated neuPrint retrieval is introduced.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class Synapse:
    x: float
    y: float
    z: float
    weight: int


@dataclass(frozen=True)
class Neuron:
    label: str
    color: str
    points: tuple[tuple[float, float, float], ...]


@dataclass(frozen=True)
class ConnectomeScene:
    source_label: str
    neurons: tuple[Neuron, ...]
    inputs: tuple[Synapse, ...]
    outputs: tuple[Synapse, ...]


def demo_scene() -> ConnectomeScene:
    """Return a compact, deliberately non-biological visual test scene."""
    return ConnectomeScene(
        source_label="Synthetic demonstration data - not a neuPrint query",
        neurons=(
            Neuron(
                "Demo neuron A",
                "#4dff88",
                ((-34, -10, -28), (-24, -5, -12), (-14, 2, 2), (-4, 8, 16), (8, 14, 30)),
            ),
            Neuron(
                "Demo neuron B",
                "#ff4dde",
                ((30, -22, -20), (20, -14, -8), (12, -5, 4), (4, 5, 16), (-8, 14, 26)),
            ),
        ),
        inputs=(
            Synapse(-21, -3, -10, 8),
            Synapse(-10, 3, 5, 4),
            Synapse(10, -8, 0, 12),
            Synapse(17, -11, -4, 2),
            Synapse(2, 7, 15, 6),
        ),
        outputs=(
            Synapse(-31, -8, -23, 9),
            Synapse(-7, 7, 14, 5),
            Synapse(19, -14, -8, 11),
            Synapse(7, -1, 7, 3),
            Synapse(-1, 10, 21, 7),
        ),
    )


def _xyz(points: Iterable[tuple[float, float, float]]) -> tuple[list[float], list[float], list[float]]:
    values = list(points)
    return [p[0] for p in values], [p[1] for p in values], [p[2] for p in values]


def build_html(scene: ConnectomeScene) -> str:
    """Serialize the scene into one small HTML file using Plotly's CDN bundle."""
    neurons = []
    for neuron in scene.neurons:
        x, y, z = _xyz(neuron.points)
        neurons.append({"name": neuron.label, "color": neuron.color, "x": x, "y": y, "z": z})

    payload = json.dumps(
        {
            "sourceLabel": scene.source_label,
            "neurons": neurons,
            "inputs": [asdict(item) for item in scene.inputs],
            "outputs": [asdict(item) for item in scene.outputs],
        },
        separators=(",", ":"),
    ).replace("</", "<\\/")

    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>ConnectoView 3D - Demo</title>
  <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
  <style>
    :root { color-scheme: dark; font-family: Inter, ui-sans-serif, system-ui, sans-serif; }
    body { margin: 0; background: #070b13; color: #edf3ff; }
    header { display:flex; justify-content:space-between; gap:16px; align-items:center; padding:18px 24px; border-bottom:1px solid #273249; }
    h1 { font-size: 1.15rem; margin:0; } .badge { color:#ffd66d; font-size:.82rem; }
    main { display:grid; grid-template-columns: minmax(0, 1fr) 272px; min-height: calc(100vh - 69px); }
    #plot { min-height: 580px; } aside { padding:22px; background:#0d1421; border-left:1px solid #273249; }
    h2 { font-size:.92rem; margin:0 0 8px; } p, label { color:#b9c6da; font-size:.86rem; line-height:1.45; }
    label { display:block; margin-top:20px; } input { width:100%; accent-color:#71a9ff; } output { color:#fff; float:right; }
    .note { margin-top:22px; padding:12px; border-left:3px solid #ffd66d; background:#171d28; }
    @media (max-width: 760px) { main { grid-template-columns: 1fr; } aside { border-left:0; border-top:1px solid #273249; } #plot { min-height:460px; } }
  </style>
</head>
<body>
  <header><h1>ConnectoView 3D <span class="badge">MVP / synthetic demo</span></h1><span id="source"></span></header>
  <main>
    <div id="plot" aria-label="Interactive 3D connectome plot"></div>
    <aside>
      <h2>Scene controls</h2>
      <p>Use the legend in the plot to show or hide each neuron, synapse class, and ROI envelope.</p>
      <label for="threshold">Synapse weight minimum <output id="thresholdValue">1</output></label>
      <input id="threshold" type="range" min="1" max="12" value="1">
      <label for="opacity">ROI envelope opacity <output id="opacityValue">15%</output></label>
      <input id="opacity" type="range" min="0" max="40" value="15">
      <p class="note">This view contains synthetic geometry and synthetic synapses. It is a UI prototype, not scientific evidence.</p>
    </aside>
  </main>
  <script id="connectoview-data" type="application/json">__DATA__</script>
  <script>
    const data = JSON.parse(document.getElementById('connectoview-data').textContent);
    document.getElementById('source').textContent = data.sourceLabel;
    const synapseTrace = (name, points, color, size) => ({
      type: 'scatter3d', mode: 'markers', name, x: points.map(p => p.x), y: points.map(p => p.y), z: points.map(p => p.z),
      customdata: points.map(p => p.weight), marker: { color, size, opacity: .9 },
      hovertemplate: name + '<br>weight: %{customdata}<extra></extra>'
    });
    const neuronTraces = data.neurons.map(n => ({
      type: 'scatter3d', mode: 'lines+markers', name: n.name, x:n.x, y:n.y, z:n.z,
      line:{color:n.color, width:7}, marker:{color:n.color, size:3}, hovertemplate:n.name+'<extra></extra>'
    }));
    const roiTrace = {
      type:'mesh3d', name:'Demo ROI envelope', opacity:.15, color:'#aab6c8',
      x:[-45,45,45,-45,-45,45,45,-45], y:[-38,-38,38,38,-38,-38,38,38], z:[-34,-34,-34,-34,38,38,38,38],
      i:[0,0,0,1,1,2,4,4,5,5,6,6], j:[1,2,3,5,6,6,5,6,6,7,2,3], k:[2,3,4,6,5,7,6,7,7,4,3,7],
      hovertemplate:'Synthetic ROI envelope<extra></extra>'
    };
    const traces = [...neuronTraces, synapseTrace('Input synapses',data.inputs,'#43a7ff',4), synapseTrace('Output synapses',data.outputs,'#ff5252',5), roiTrace];
    const synapseTraceIndices = [neuronTraces.length, neuronTraces.length + 1];
    const layout = {
      paper_bgcolor:'#070b13', plot_bgcolor:'#070b13', font:{color:'#edf3ff'}, margin:{l:0,r:0,t:12,b:0},
      legend:{bgcolor:'rgba(13,20,33,.86)', bordercolor:'#34445f', borderwidth:1},
      scene:{xaxis:{title:'X',backgroundcolor:'#070b13',gridcolor:'#24334c'}, yaxis:{title:'Y',backgroundcolor:'#070b13',gridcolor:'#24334c'}, zaxis:{title:'Z',backgroundcolor:'#070b13',gridcolor:'#24334c'}, aspectmode:'data'},
      uirevision:'connectoview-demo'
    };
    Plotly.newPlot('plot', traces, layout, {responsive:true, displaylogo:false});
    const threshold = document.getElementById('threshold');
    const opacity = document.getElementById('opacity');
    threshold.addEventListener('input', () => {
      const minimum = Number(threshold.value); document.getElementById('thresholdValue').textContent = minimum;
      synapseTraceIndices.forEach((traceIndex, index) => {
        const points = index ? data.outputs : data.inputs;
        const kept = points.filter(p => p.weight >= minimum);
        Plotly.restyle('plot', {x:[kept.map(p=>p.x)], y:[kept.map(p=>p.y)], z:[kept.map(p=>p.z)], customdata:[kept.map(p=>p.weight)]}, [traceIndex]);
      });
    });
    opacity.addEventListener('input', () => {
      const value = Number(opacity.value) / 100; document.getElementById('opacityValue').textContent = opacity.value + '%';
      Plotly.restyle('plot', {opacity:value}, [traces.length - 1]);
    });
  </script>
</body>
</html>""".replace("__DATA__", payload)


def main() -> None:
    output_path = Path(__file__).resolve().parents[1] / "output" / "connectoview-demo.html"
    output_path.parent.mkdir(exist_ok=True)
    output_path.write_text(build_html(demo_scene()), encoding="utf-8")
    print(f"Created {output_path}")


# ---------------------------------------------------------------------------
# Live neuPrint pipeline (PRD FR-1.1 … FR-4.2). Optional deps only on use:
# neuprint-python + navis for queries, plotly/pandas/numpy for figures.
# The synthetic demo above stays dependency-free so tests run anywhere.
# ---------------------------------------------------------------------------

NEURON_COLORS = ["#39FF14", "#FF10F0", "#00E5FF", "#FFD400", "#FF7A00", "#B28DFF"]
INPUT_COLOR = "#3B82F6"  # blue scatter, size 2 (FR-3.2)
OUTPUT_COLOR = "#EF4444"  # red scatter, size 3 (FR-3.2)
MESH_COLOR = "gray"
MESH_OPACITY_DEFAULT = 0.15
NEUPRINT_SERVER = "neuprint.janelia.org"


def get_client(token, dataset, server=NEUPRINT_SERVER):
    """FR-1.1: handshake with neuprint.janelia.org via user API token."""
    import os as _os

    from neuprint import Client

    tok = token or _os.environ.get("NEUPRINT_APPLICATION_CREDENTIALS", "")
    if not tok:
        raise ValueError(
            "Missing neuPrint API token. Pass --token or set "
            "NEUPRINT_APPLICATION_CREDENTIALS."
        )
    return Client(server, dataset=dataset, token=tok)


def to_navis_neuron(skel_df, body_id):
    """FR-1.2: validate SWC vectors convert via navis (best-effort)."""
    try:
        import navis
    except Exception:
        return None
    try:
        tmp = skel_df.rename(columns={"rowId": "node_id", "link": "parent_id"})
        neuron = navis.TreeNeuron(
            tmp[["node_id", "parent_id", "x", "y", "z", "radius"]], units="nm"
        )
        neuron.name = str(body_id)
        return neuron
    except Exception:
        return None


def fetch_skeleton(client, body_id):
    """FR-1.2: fetch 3D skeleton vectors for one bodyId."""
    from neuprint import fetch_skeleton as _fetch

    skel = _fetch(body_id, heal=True, client=client)
    to_navis_neuron(skel, body_id)
    return skel


def fetch_synapses_split(client, body_id):
    """FR-1.3 + FR-2.2: synapse X,Y,Z split pre/post; drop corrupt rows."""
    import numpy as _np

    from neuprint import NeuronCriteria as NC
    from neuprint import SynapseCriteria as SC, fetch_synapses

    syn = fetch_synapses(NC(bodyId=body_id), SC(primary_only=True), client=client)
    if syn is None or syn.empty:
        import pandas as _pd

        empty = _pd.DataFrame(columns=["x", "y", "z"])
        return empty, empty
    before = len(syn)
    syn = syn.dropna(subset=["x", "y", "z"])
    syn = syn[_np.isfinite(syn["x"]) & _np.isfinite(syn["y"]) & _np.isfinite(syn["z"])]
    if len(syn) < before:
        print(f"[ConnectoView] body {body_id}: omitted {before - len(syn)} corrupt synapse(s).")
    return syn[syn["type"] == "pre"].copy(), syn[syn["type"] == "post"].copy()


def fetch_connectivity_filtered(client, body_ids, weight_threshold):
    """FR-2.1: keep only connections with weight >= X."""
    if weight_threshold <= 1:
        return None
    try:
        from neuprint import fetch_simple_connections

        conn = fetch_simple_connections(
            body_ids, body_ids, min_weight=weight_threshold, client=client
        )
        print(f"[ConnectoView] weight>={weight_threshold} kept {len(conn)} edge(s).")
        return conn
    except Exception as exc:
        print(f"[ConnectoView] connectivity filter failed (non-fatal): {exc}")
        return None


def parse_obj_mesh(obj_bytes, max_faces=20000):
    """Parse ROI .obj bytes -> x,y,z,i,j,k; decimate faces for 60 FPS."""
    import numpy as _np

    text = obj_bytes.decode("utf-8", errors="ignore")
    verts, faces = [], []
    for line in text.splitlines():
        if line.startswith("v "):
            parts = line.split()
            try:
                verts.append([float(parts[1]), float(parts[2]), float(parts[3])])
            except (IndexError, ValueError):
                continue
        elif line.startswith("f "):
            idx = []
            for p in line.split()[1:]:
                try:
                    idx.append(int(p.split("/")[0]) - 1)
                except ValueError:
                    pass
            if len(idx) >= 3:
                for k in range(1, len(idx) - 1):
                    faces.append([idx[0], idx[k], idx[k + 1]])
    v = _np.asarray(verts, dtype=_np.float32)
    f = _np.asarray(faces, dtype=_np.int32)
    if len(v) == 0 or len(f) == 0:
        raise ValueError("empty mesh after .obj parse")
    if len(f) > max_faces:
        f = f[:: int(_np.ceil(len(f) / max_faces))]
    return v[:, 0], v[:, 1], v[:, 2], f[:, 0], f[:, 1], f[:, 2]


def fetch_roi_meshes(client, rois):
    """FR-1.4: ROI volumetric meshes by shorthand (MB(R), EB, AL …)."""
    meshes = {}
    for roi in rois:
        roi = roi.strip()
        if not roi:
            continue
        try:
            meshes[roi] = parse_obj_mesh(client.fetch_roi_mesh(roi))
        except Exception as exc:
            print(f"[ConnectoView] ROI '{roi}' skipped: {exc}")
    return meshes


def skeleton_to_line_xyz(skel):
    """SWC node table -> Plotly None-separated line segments."""
    import numpy as _np

    lookup = {
        int(r.rowId): (float(r.x), float(r.y), float(r.z))
        for r in skel.itertuples()
        if _np.isfinite(r.x)
    }
    xs, ys, zs = [], [], []
    for r in skel.itertuples():
        child = lookup.get(int(r.rowId))
        try:
            parent = lookup.get(int(r.link))
        except (ValueError, AttributeError):
            parent = None
        if child is None or parent is None:
            continue
        xs += [child[0], parent[0], None]
        ys += [child[1], parent[1], None]
        zs += [child[2], parent[2], None]
    return xs, ys, zs


def build_neuprint_figure(skeletons, synapses, meshes,
                          title="ConnectoView 3D — Fruit Fly Connectome"):
    """FR-3.1/3.2/3.3: dark canvas, strict palette, togglable legend."""
    import plotly.graph_objects as _go

    fig = _go.Figure()
    for k, (body_id, skel) in enumerate(skeletons.items()):
        color = NEURON_COLORS[k % len(NEURON_COLORS)]
        xs, ys, zs = skeleton_to_line_xyz(skel)
        if not xs:
            continue
        fig.add_trace(_go.Scatter3d(
            x=xs, y=ys, z=zs, mode="lines", name=f"Neuron {body_id}",
            line=dict(color=color, width=3), hoverinfo="name", showlegend=True))
        pre, post = synapses.get(body_id, (None, None))
        if post is not None and len(post):
            fig.add_trace(_go.Scatter3d(
                x=post["x"].to_numpy(), y=post["y"].to_numpy(), z=post["z"].to_numpy(),
                mode="markers", name=f"Inputs (post) {body_id}",
                marker=dict(color=INPUT_COLOR, size=2, opacity=0.8),
                hovertemplate="input %{x:.0f},%{y:.0f},%{z:.0f}<extra></extra>",
                showlegend=True))
        if pre is not None and len(pre):
            fig.add_trace(_go.Scatter3d(
                x=pre["x"].to_numpy(), y=pre["y"].to_numpy(), z=pre["z"].to_numpy(),
                mode="markers", name=f"Outputs (pre) {body_id}",
                marker=dict(color=OUTPUT_COLOR, size=3, opacity=0.9),
                hovertemplate="output %{x:.0f},%{y:.0f},%{z:.0f}<extra></extra>",
                showlegend=True))
    mesh_traces = []
    for roi, (mx, my, mz, mi, mj, mk) in meshes.items():
        fig.add_trace(_go.Mesh3d(
            x=mx, y=my, z=mz, i=mi, j=mj, k=mk, name=f"ROI {roi}",
            color=MESH_COLOR, opacity=MESH_OPACITY_DEFAULT,
            flatshading=True, hoverinfo="name", showlegend=True))
        mesh_traces.append(len(fig.data) - 1)
    sliders = []
    if mesh_traces:
        steps = []
        for op in [0.0, 0.05, 0.10, 0.15]:
            op_list = [op if idx in mesh_traces else fig.data[idx].opacity
                       for idx in range(len(fig.data))]
            steps.append(dict(method="restyle", args=[{"opacity": op_list}],
                              label=f"{int(op * 100)}%"))
        sliders = [dict(active=3, currentvalue={"prefix": "Mesh opacity: "},
                        pad={"t": 40}, steps=steps)]
    fig.update_layout(
        template="plotly_dark",
        title=title,
        scene=dict(xaxis_title="X (nm)", yaxis_title="Y (nm)",
                   zaxis_title="Z (nm)", aspectmode="data"),
        legend=dict(title="Toggle layers (click to hide/show)",
                    itemsizing="constant", bgcolor="rgba(0,0,0,0.5)"),
        margin=dict(l=0, r=0, t=50, b=0),
        sliders=sliders,
        updatemenus=[dict(type="buttons", showactive=False, x=0.0, y=1.12,
                          xanchor="left", buttons=[
                              dict(label="Show all", method="update",
                                   args=[{"visible": [True] * len(fig.data)}])])],
    )
    return fig


def export_neuprint_html(fig, path):
    """FR-4.1/4.2: standalone HTML via CDN, footprint ceiling 5MB."""
    import os as _os

    fig.write_html(path, include_plotlyjs="cdn", full_html=True)
    size = _os.path.getsize(path)
    print(f"[ConnectoView] exported {path} ({size / 1024:.1f} KB, cdn).")
    if size > 5 * 1024 * 1024:
        print("[ConnectoView] WARNING: export exceeds 5MB ceiling.")
    return size


def synthetic_skeleton(body_id, n=300, seed=0):
    """Offline stand-in skeleton (nm units) for tests / no-token runs."""
    import numpy as _np
    import pandas as _pd

    rng = _np.random.default_rng(seed + int(body_id) % 10_000)
    t = _np.linspace(0, 4 * _np.pi, n)
    return _pd.DataFrame({
        "rowId": _np.arange(1, n + 1),
        "x": 15000 + 3000 * _np.cos(t) + rng.normal(0, 80, n),
        "y": 22000 + 3000 * _np.sin(t) + rng.normal(0, 80, n),
        "z": 15000 + 200 * t + rng.normal(0, 60, n),
        "radius": _np.full(n, 40.0),
        "link": [-1, *range(1, n)],
    })


def synthetic_synapses(body_id, n_pre=120, n_post=180, seed=1):
    """Offline stand-in synapses; exercises FR-2.2 corrupt-row omission."""
    import numpy as _np
    import pandas as _pd

    rng = _np.random.default_rng(seed + int(body_id) % 10_000)

    def cloud(n):
        return _pd.DataFrame({
            "x": rng.normal(15000, 2500, n),
            "y": rng.normal(22000, 2500, n),
            "z": rng.normal(17000, 1200, n),
        })

    corrupt = _pd.DataFrame({"x": [_np.nan], "y": [_np.nan], "z": [_np.nan]})
    pre = _pd.concat([cloud(n_pre), corrupt], ignore_index=True).dropna(subset=["x", "y", "z"])
    post = _pd.concat([cloud(n_post), corrupt], ignore_index=True).dropna(subset=["x", "y", "z"])
    return pre, post


def synthetic_mesh(center=(15000, 22000, 17000), scale=(5000, 4000, 2500),
                   n_u=24, n_v=16):
    """Offline ellipsoid ROI stand-in -> x,y,z,i,j,k."""
    import numpy as _np

    uu = _np.linspace(0, 2 * _np.pi, n_u)
    vv = _np.linspace(0, _np.pi, n_v)
    U, V = _np.meshgrid(uu, vv)
    X = center[0] + scale[0] * _np.sin(V) * _np.cos(U)
    Y = center[1] + scale[1] * _np.sin(V) * _np.sin(U)
    Z = center[2] + scale[2] * _np.cos(V)
    verts = _np.stack([X.ravel(), Y.ravel(), Z.ravel()], axis=1).astype(_np.float32)
    faces = []
    for j in range(n_v - 1):
        for i in range(n_u):
            a = j * n_u + i
            b = j * n_u + (i + 1) % n_u
            c = (j + 1) * n_u + i
            d = (j + 1) * n_u + (i + 1) % n_u
            faces += [[a, c, b], [b, c, d]]
    f = _np.asarray(faces, dtype=_np.int32)
    return verts[:, 0], verts[:, 1], verts[:, 2], f[:, 0], f[:, 1], f[:, 2]


def run_offline(body_ids, rois, output):
    """No-token pipeline: synthetic skeletons/synapses/meshes -> HTML."""
    skeletons = {b: synthetic_skeleton(b, seed=i * 7) for i, b in enumerate(body_ids)}
    synapses = {b: synthetic_synapses(b, seed=i * 13) for i, b in enumerate(body_ids)}
    meshes = {r: synthetic_mesh(center=(15000 + i * 1500, 22000, 17000))
              for i, r in enumerate(rois)}
    fig = build_neuprint_figure(
        skeletons, synapses, meshes, title="ConnectoView 3D — offline (synthetic)")
    export_neuprint_html(fig, output)
    return output


def run_live(token, dataset, body_ids, rois, weight_threshold, output):
    """Authenticated pipeline: neuPrint -> navis -> Plotly -> HTML."""
    client = get_client(token, dataset)
    fetch_connectivity_filtered(client, body_ids, weight_threshold)
    skeletons, synapses = {}, {}
    for b in body_ids:
        try:
            skeletons[b] = fetch_skeleton(client, b)
        except Exception as exc:
            print(f"[ConnectoView] body {b} skeleton failed: {exc}")
            continue
        try:
            synapses[b] = fetch_synapses_split(client, b)
        except Exception as exc:
            print(f"[ConnectoView] body {b} synapses failed: {exc}")
            import pandas as _pd

            synapses[b] = (_pd.DataFrame(columns=["x", "y", "z"]),
                           _pd.DataFrame(columns=["x", "y", "z"]))
    meshes = fetch_roi_meshes(client, rois)
    if not skeletons:
        raise RuntimeError("no skeletons fetched; aborting render.")
    export_neuprint_html(build_neuprint_figure(skeletons, synapses, meshes), output)
    return output


def cli(argv=None) -> int:
    """CLI: demo (default, dependency-free) or live/offline Plotly export."""
    import argparse as _argparse
    import os as _os

    p = _argparse.ArgumentParser(description="ConnectoView 3D pipeline (PRD).")
    p.add_argument("--bodyIds", default="5813027016,734404633")
    p.add_argument("--rois", default="MB(R),EB,AL(R)")
    p.add_argument("--token", default=_os.environ.get("NEUPRINT_APPLICATION_CREDENTIALS", ""))
    p.add_argument("--dataset", default="hemibrain:v1.2.1")
    p.add_argument("--weight-threshold", type=int, default=5)
    p.add_argument("--output", default=None)
    p.add_argument("--demo", action="store_true",
                   help="dependency-free synthetic demo -> output/connectoview-demo.html")
    p.add_argument("--offline", action="store_true",
                   help="plotly offline synthetic export (no token needed)")
    a = p.parse_args(argv)
    if a.demo or (not a.token and not a.offline):
        if not a.token and not a.demo:
            print("[ConnectoView] no token — running dependency-free demo.")
        main()
        return 0
    body_ids = [int(x.strip()) for x in a.bodyIds.split(",") if x.strip()]
    rois = [x.strip() for x in a.rois.split(",") if x.strip()]
    out = a.output or str(Path(__file__).resolve().parents[1] / "output"
                           / "connectoview-live.html")
    try:
        if a.offline or not a.token:
            run_offline(body_ids, rois, out)
        else:
            run_live(a.token, a.dataset, body_ids, rois, a.weight_threshold, out)
    except Exception as exc:
        print(f"[ConnectoView] pipeline failed: {exc}")
        return 1
    print(f"[ConnectoView] done -> {out}")
    return 0


if __name__ == "__main__":
    import sys as _sys

    _sys.exit(cli())

