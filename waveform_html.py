#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交互式 HTML 波形查看器
======================
为 AT24C02 PAT 测试向量生成交互式 HTML 波形图。

功能:
  - SVG 绘制 SCL/SDA/A0/WP 多通道数字波形
  - 鼠标滚轮缩放、拖拽平移
  - 悬停浮窗: 向量编号/状态符号/所属测试段/时间戳
  - 顶部测试段色块, 点击跳转并高亮
  - 双游标拖拽, 底部显示时间差和向量数
  - 播放动画: 逐向量高亮, 可调速
  - 深色主题
"""

import os
import json


def export_waveform_html(vectors, output_path, comments=None, pat_sections=None, period_ns=2500):
    """
    生成交互式 HTML 波形文件。

    Parameters
    ----------
    vectors : list[dict]
        向量列表, 每个 dict 的 key 为引脚名 (如 "SCL","SDA","A0","WP"),
        value 为状态字符串 ("0","1","H","L","X","Z").
    output_path : str
        输出 HTML 文件路径.
    comments : list[str] | None
        与 vectors 等长的注释列表.
    pat_sections : list[tuple] | None
        测试段列表, 每个元素 (name, desc, section_vectors, section_comments, section_labels).
    period_ns : int
        每个向量周期 (ns), 用于时间戳计算.
    """
    if not vectors:
        return

    # -- 确定要显示的通道 --
    display_pins = []
    for pin in ["SCL", "SDA", "A0", "WP"]:
        if pin in vectors[0]:
            display_pins.append(pin)
    if not display_pins:
        display_pins = list(vectors[0].keys())

    # -- 构建段索引 (每个向量属于哪个段) --
    segment_map = []  # 每个向量 -> {name, desc, color}
    section_index = []  # [{name, desc, color, start, end}, ...]

    segment_colors = [
        "#e74c3c", "#e67e22", "#f1c40f", "#2ecc71", "#1abc9c",
        "#3498db", "#9b59b6", "#e84393", "#00cec9", "#fd79a8",
        "#6c5ce7", "#fdcb6e", "#55efc4", "#74b9ff", "#a29bfe",
    ]

    if pat_sections:
        idx = 0
        for si, (name, desc, sv, sc, sl) in enumerate(pat_sections):
            color = segment_colors[si % len(segment_colors)]
            start = idx
            end = idx + len(sv) - 1
            section_index.append({
                "name": name, "desc": desc, "color": color,
                "start": start, "end": end
            })
            for _ in sv:
                segment_map.append({"name": name, "desc": desc, "color": color})
                idx += 1
        # 如果 pat_sections 覆盖不到全部 vectors, 补齐
        while len(segment_map) < len(vectors):
            segment_map.append({"name": "UNKNOWN", "desc": "Unknown", "color": "#7f8c8d"})
    else:
        for i in range(len(vectors)):
            segment_map.append({"name": "DATA", "desc": "Data", "color": "#3498db"})
        section_index.append({
            "name": "DATA", "desc": "Data", "color": "#3498db",
            "start": 0, "end": len(vectors) - 1
        })

    # -- 序列化向量数据为 JSON --
    vec_data = []
    for i, vec in enumerate(vectors):
        entry = {"i": i}
        for pin in display_pins:
            entry[pin] = vec.get(pin, "X")
        entry["comment"] = comments[i] if comments and i < len(comments) else ""
        entry["seg"] = segment_map[i]["name"] if i < len(segment_map) else ""
        entry["seg_color"] = segment_map[i]["color"] if i < len(segment_map) else "#7f8c8d"
        vec_data.append(entry)

    vectors_json = json.dumps(vec_data, ensure_ascii=False)
    sections_json = json.dumps(section_index, ensure_ascii=False)
    pins_json = json.dumps(display_pins, ensure_ascii=False)

    html = _build_html(vectors_json, sections_json, pins_json, period_ns, len(vectors))

    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)


def _build_html(vectors_json, sections_json, pins_json, period_ns, total_vectors):
    """构建完整 HTML 字符串."""
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AT24C02 Interactive Waveform Viewer</title>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ background:#1a1a2e; color:#e0e0e0; font-family:'Segoe UI','Consolas',monospace;
       overflow:hidden; height:100vh; display:flex; flex-direction:column; user-select:none; }}

/* === 顶部栏 === */
#topbar {{ background:#16213e; padding:8px 16px; display:flex; align-items:center; gap:12px;
           border-bottom:1px solid #0f3460; flex-shrink:0; }}
#topbar h1 {{ font-size:14px; color:#e94560; white-space:nowrap; }}
#topbar .info {{ font-size:11px; color:#8899aa; }}
.btn {{ background:#0f3460; color:#e0e0e0; border:1px solid #1a4080; border-radius:4px;
        padding:4px 12px; font-size:11px; cursor:pointer; white-space:nowrap; }}
.btn:hover {{ background:#1a4080; }}
.btn.active {{ background:#e94560; border-color:#e94560; }}
#speed-display {{ font-size:11px; color:#e94560; min-width:45px; text-align:center; }}

/* === 测试段色块栏 === */
#seg-bar {{ background:#16213e; padding:4px 16px; display:flex; gap:4px; flex-wrap:wrap;
            border-bottom:1px solid #0f3460; flex-shrink:0; }}
.seg-chip {{ padding:3px 10px; border-radius:3px; font-size:10px; cursor:pointer;
             opacity:0.75; transition:opacity 0.2s, transform 0.2s; }}
.seg-chip:hover {{ opacity:1; transform:scale(1.08); }}
.seg-chip.highlight {{ opacity:1; outline:2px solid #fff; outline-offset:1px; }}

/* === 波形区 === */
#waveform-container {{ flex:1; position:relative; overflow:hidden; background:#0f0f23; }}
#waveform-svg {{ position:absolute; top:0; left:0; }}
#pin-labels {{ position:absolute; left:0; top:0; width:60px; background:#16213e;
               z-index:10; border-right:1px solid #0f3460; }}
.pin-label {{ height:80px; display:flex; align-items:center; justify-content:center;
              font-size:12px; font-weight:bold; color:#e94560; }}

/* === 浮窗 === */
#tooltip {{ position:fixed; background:#1e2a4a; border:1px solid #e94560; border-radius:6px;
            padding:8px 12px; font-size:11px; line-height:1.6; pointer-events:none;
            display:none; z-index:100; box-shadow:0 4px 16px rgba(0,0,0,0.5);
            max-width:280px; }}
#tooltip .tt-label {{ color:#8899aa; }}
#tooltip .tt-value {{ color:#e0e0e0; font-weight:bold; }}
#tooltip .tt-seg {{ display:inline-block; padding:1px 6px; border-radius:3px;
                     font-size:10px; margin-top:2px; }}

/* === 游标 === */
.cursor-line {{ stroke-width:1.5; stroke-dasharray:4,3; cursor:ew-resize; }}
.cursor-label {{ font-size:10px; fill:#fff; pointer-events:none; }}
.cursor-handle {{ cursor:ew-resize; }}

/* === 底部信息栏 === */
#bottombar {{ background:#16213e; padding:6px 16px; display:flex; align-items:center; gap:20px;
              border-top:1px solid #0f3460; font-size:11px; flex-shrink:0; }}
#bottombar .label {{ color:#8899aa; }}
#bottombar .value {{ color:#e94560; font-weight:bold; }}

/* === 高亮段 overlay === */
.seg-highlight-rect {{ fill:rgba(233,69,96,0.08); pointer-events:none; }}

/* === 播放指示线 === */
#play-line {{ stroke:#e94560; stroke-width:2; display:none; }}
</style>
</head>
<body>

<!-- 顶部栏 -->
<div id="topbar">
  <h1>AT24C02 Waveform Viewer</h1>
  <span class="info" id="info-total">Vectors: {total_vectors} | Period: {period_ns}ns</span>
  <span class="info" id="info-view"></span>
  <div style="flex:1"></div>
  <button class="btn" id="btn-zoomfit" title="适应全部">Fit All</button>
  <button class="btn" id="btn-zoomin" title="放大">Zoom +</button>
  <button class="btn" id="btn-zoomout" title="缩小">Zoom -</button>
  <span style="width:1px;height:20px;background:#0f3460;"></span>
  <button class="btn" id="btn-cursor-toggle" title="显示/隐藏游标">Cursors</button>
  <span style="width:1px;height:20px;background:#0f3460;"></span>
  <button class="btn" id="btn-play" title="播放动画">&#9654; Play</button>
  <button class="btn" id="btn-slower" title="减速">-</button>
  <span id="speed-display">1x</span>
  <button class="btn" id="btn-faster" title="加速">+</button>
</div>

<!-- 测试段色块栏 -->
<div id="seg-bar"></div>

<!-- 波形主区域 -->
<div id="waveform-container">
  <div id="pin-labels"></div>
  <svg id="waveform-svg" xmlns="http://www.w3.org/2000/svg"></svg>
</div>

<!-- 浮窗 -->
<div id="tooltip"></div>

<!-- 底部信息栏 -->
<div id="bottombar">
  <span><span class="label">View: </span><span class="value" id="view-range">-</span></span>
  <span><span class="label">Cursor A: </span><span class="value" id="cur-a-info">-</span></span>
  <span><span class="label">Cursor B: </span><span class="value" id="cur-b-info">-</span></span>
  <span><span class="label">&Delta;: </span><span class="value" id="cur-delta">-</span></span>
  <div style="flex:1"></div>
  <span class="info">Scroll=Zoom | Drag=Pan | Hover=Info</span>
</div>

<script>
// ========== 数据 ==========
const VECTORS = {vectors_json};
const SECTIONS = {sections_json};
const PINS = {pins_json};
const PERIOD_NS = {period_ns};
const TOTAL = {total_vectors};

// ========== 状态 ==========
const PIN_COLORS = {{
    "SCL": "#3498db", "SDA": "#2ecc71", "A0": "#e67e22",
    "A1": "#9b59b6", "A2": "#1abc9c", "WP": "#e74c3c"
}};
const STATE_HIGH = new Set(["1", "H"]);
const STATE_LOW = new Set(["0", "L"]);
const STATE_TRI = new Set(["Z", "X"]);

const CH_HEIGHT = 80;
const WAVE_HIGH = 20;
const WAVE_LOW = 60;
const WAVE_MID = 40;
const PIN_LABEL_W = 60;
const TOP_PAD = 10;

let viewStart = 0;        // 当前视图左边起始向量 (浮点)
let viewCount = Math.min(200, TOTAL); // 当前视图可见向量数
let pixPerVec = 8;         // 每向量像素宽度

let containerW = 800;
let containerH = 400;

let cursorsVisible = false;
let cursorA = -1;
let cursorB = -1;
let draggingCursor = null; // "A" | "B" | null

let isDragging = false;
let dragStartX = 0;
let dragStartView = 0;

let playing = false;
let playIdx = 0;
let playSpeed = 1;       // vectors per frame
let playRAF = null;

let highlightedSeg = null;

// ========== DOM ==========
const container = document.getElementById("waveform-container");
const svg = document.getElementById("waveform-svg");
const tooltip = document.getElementById("tooltip");
const pinLabelsDiv = document.getElementById("pin-labels");
const segBar = document.getElementById("seg-bar");
const NS = "http://www.w3.org/2000/svg";

// ========== 初始化 ==========
function init() {{
    calcSize();
    buildPinLabels();
    buildSegBar();
    fitAll();
    render();
    bindEvents();
}}

function calcSize() {{
    const rect = container.getBoundingClientRect();
    containerW = rect.width - PIN_LABEL_W;
    containerH = rect.height;
}}

function buildPinLabels() {{
    pinLabelsDiv.innerHTML = "";
    pinLabelsDiv.style.paddingTop = TOP_PAD + "px";
    PINS.forEach(pin => {{
        const d = document.createElement("div");
        d.className = "pin-label";
        d.style.color = PIN_COLORS[pin] || "#e0e0e0";
        d.textContent = pin;
        pinLabelsDiv.appendChild(d);
    }});
    pinLabelsDiv.style.height = (TOP_PAD + PINS.length * CH_HEIGHT) + "px";
}}

function buildSegBar() {{
    segBar.innerHTML = "";
    SECTIONS.forEach((sec, i) => {{
        const chip = document.createElement("span");
        chip.className = "seg-chip";
        chip.style.background = sec.color;
        chip.style.color = "#fff";
        chip.textContent = sec.name + " (" + (sec.end - sec.start + 1) + ")";
        chip.title = sec.desc + "\\nVectors " + sec.start + "~" + sec.end;
        chip.addEventListener("click", () => jumpToSection(i));
        segBar.appendChild(chip);
    }});
}}

// ========== 渲染 ==========
function render() {{
    // 清空 SVG
    while (svg.firstChild) svg.removeChild(svg.firstChild);

    pixPerVec = containerW / viewCount;
    const svgW = containerW;
    const svgH = TOP_PAD + PINS.length * CH_HEIGHT;
    svg.setAttribute("width", svgW);
    svg.setAttribute("height", svgH);
    svg.style.left = PIN_LABEL_W + "px";

    const iStart = Math.max(0, Math.floor(viewStart));
    const iEnd = Math.min(TOTAL - 1, Math.ceil(viewStart + viewCount));

    // -- 段高亮背景 --
    if (highlightedSeg !== null) {{
        const sec = SECTIONS[highlightedSeg];
        if (sec) {{
            const x1 = (sec.start - viewStart) * pixPerVec;
            const x2 = (sec.end + 1 - viewStart) * pixPerVec;
            if (x2 > 0 && x1 < svgW) {{
                const rect = createSVG("rect", {{
                    x: Math.max(0, x1), y: 0,
                    width: Math.min(svgW, x2) - Math.max(0, x1), height: svgH,
                    class: "seg-highlight-rect"
                }});
                svg.appendChild(rect);
            }}
        }}
    }}

    // -- 段分界线 --
    SECTIONS.forEach(sec => {{
        const x = (sec.start - viewStart) * pixPerVec;
        if (x > 0 && x < svgW) {{
            svg.appendChild(createSVG("line", {{
                x1: x, y1: 0, x2: x, y2: svgH,
                stroke: sec.color, "stroke-width": 0.8, "stroke-dasharray": "3,3", opacity: 0.5
            }}));
            // 段名标注
            if (pixPerVec > 1) {{
                const label = createSVG("text", {{
                    x: x + 3, y: 10, fill: sec.color, "font-size": "9px", opacity: 0.7
                }});
                label.textContent = sec.name;
                svg.appendChild(label);
            }}
        }}
    }});

    // -- 每个通道波形 --
    PINS.forEach((pin, ch) => {{
        const yBase = TOP_PAD + ch * CH_HEIGHT;
        const color = PIN_COLORS[pin] || "#e0e0e0";

        // 通道分隔线
        svg.appendChild(createSVG("line", {{
            x1: 0, y1: yBase, x2: svgW, y2: yBase,
            stroke: "#1a2040", "stroke-width": 0.5
        }}));
        // 高/低参考线
        svg.appendChild(createSVG("line", {{
            x1: 0, y1: yBase + WAVE_HIGH, x2: svgW, y2: yBase + WAVE_HIGH,
            stroke: "#1a2040", "stroke-width": 0.3, "stroke-dasharray": "2,4"
        }}));
        svg.appendChild(createSVG("line", {{
            x1: 0, y1: yBase + WAVE_LOW, x2: svgW, y2: yBase + WAVE_LOW,
            stroke: "#1a2040", "stroke-width": 0.3, "stroke-dasharray": "2,4"
        }}));

        // 构建波形路径
        let pathD = "";
        let prevY = null;
        let triRects = [];

        for (let i = iStart; i <= iEnd; i++) {{
            const vec = VECTORS[i];
            if (!vec) continue;
            const state = vec[pin] || "X";
            const x = (i - viewStart) * pixPerVec;
            let y;
            if (STATE_HIGH.has(state)) y = yBase + WAVE_HIGH;
            else if (STATE_LOW.has(state)) y = yBase + WAVE_LOW;
            else {{ y = yBase + WAVE_MID; triRects.push({{ x, state }}); }}

            if (prevY === null) {{
                pathD += "M" + x.toFixed(2) + "," + y.toFixed(2);
            }} else {{
                // 阶跃: 先垂直再水平
                pathD += " L" + x.toFixed(2) + "," + prevY.toFixed(2);
                pathD += " L" + x.toFixed(2) + "," + y.toFixed(2);
            }}
            const xEnd = x + pixPerVec;
            pathD += " L" + xEnd.toFixed(2) + "," + y.toFixed(2);
            prevY = y;
        }}

        if (pathD) {{
            svg.appendChild(createSVG("path", {{
                d: pathD, fill: "none", stroke: color, "stroke-width": 1.5
            }}));
        }}

        // Z/X 填充
        triRects.forEach(r => {{
            svg.appendChild(createSVG("rect", {{
                x: r.x, y: yBase + WAVE_HIGH,
                width: Math.max(pixPerVec, 1), height: WAVE_LOW - WAVE_HIGH,
                fill: color, opacity: 0.12
            }}));
            if (pixPerVec > 12) {{
                const lbl = createSVG("text", {{
                    x: r.x + pixPerVec / 2, y: yBase + WAVE_MID + 4,
                    fill: color, "font-size": "9px", "text-anchor": "middle", opacity: 0.6
                }});
                lbl.textContent = r.state;
                svg.appendChild(lbl);
            }}
        }});

        // 状态符号标注 (缩放足够大时)
        if (pixPerVec > 30) {{
            for (let i = iStart; i <= iEnd; i++) {{
                const vec = VECTORS[i];
                if (!vec) continue;
                const state = vec[pin] || "X";
                if (STATE_HIGH.has(state) || STATE_LOW.has(state)) {{
                    const x = (i - viewStart) * pixPerVec + pixPerVec / 2;
                    const y = STATE_HIGH.has(state) ? yBase + WAVE_HIGH - 4 : yBase + WAVE_LOW + 12;
                    const lbl = createSVG("text", {{
                        x: x, y: y, fill: color, "font-size": "8px",
                        "text-anchor": "middle", opacity: 0.5
                    }});
                    lbl.textContent = state;
                    svg.appendChild(lbl);
                }}
            }}
        }}
    }});

    // -- 向量编号刻度 (缩放足够大时) --
    if (pixPerVec > 15) {{
        const step = Math.max(1, Math.ceil(40 / pixPerVec));
        for (let i = iStart; i <= iEnd; i += step) {{
            const x = (i - viewStart) * pixPerVec + pixPerVec / 2;
            if (x > 0 && x < svgW) {{
                const t = createSVG("text", {{
                    x: x, y: svgH - 2, fill: "#556", "font-size": "8px", "text-anchor": "middle"
                }});
                t.textContent = i;
                svg.appendChild(t);
            }}
        }}
    }}

    // -- 游标 --
    if (cursorsVisible) {{
        renderCursor("A", cursorA, "#ff6b6b");
        renderCursor("B", cursorB, "#54a0ff");
    }}

    // -- 播放线 --
    if (playing) {{
        const px = (playIdx - viewStart) * pixPerVec;
        if (px >= 0 && px <= svgW) {{
            svg.appendChild(createSVG("line", {{
                x1: px, y1: 0, x2: px, y2: svgH,
                stroke: "#e94560", "stroke-width": 2, id: "play-line-el"
            }}));
        }}
    }}

    // -- 透明交互层 --
    const interactRect = createSVG("rect", {{
        x: 0, y: 0, width: svgW, height: svgH,
        fill: "transparent", style: "cursor:crosshair;"
    }});
    interactRect.addEventListener("mousemove", onMouseMove);
    interactRect.addEventListener("mouseleave", () => {{ tooltip.style.display = "none"; }});
    interactRect.addEventListener("mousedown", onMouseDown);
    svg.appendChild(interactRect);

    updateInfoBar();
    updateCursorInfo();
}}

function renderCursor(label, vecIdx, color) {{
    if (vecIdx < 0) return;
    const svgH = TOP_PAD + PINS.length * CH_HEIGHT;
    const px = (vecIdx - viewStart) * pixPerVec;
    if (px < -20 || px > containerW + 20) return;

    svg.appendChild(createSVG("line", {{
        x1: px, y1: 0, x2: px, y2: svgH,
        stroke: color, class: "cursor-line"
    }}));

    // 顶部手柄
    const g = createSVG("g", {{ class: "cursor-handle", "data-cursor": label }});
    g.appendChild(createSVG("rect", {{
        x: px - 12, y: 0, width: 24, height: 16, rx: 3,
        fill: color, opacity: 0.9
    }}));
    const txt = createSVG("text", {{
        x: px, y: 12, fill: "#fff", "font-size": "10px",
        "text-anchor": "middle", "font-weight": "bold", style: "pointer-events:none;"
    }});
    txt.textContent = label;
    g.appendChild(txt);
    // 拖拽区 (更宽)
    const hitArea = createSVG("rect", {{
        x: px - 15, y: 0, width: 30, height: svgH,
        fill: "transparent", style: "cursor:ew-resize;"
    }});
    hitArea.addEventListener("mousedown", (e) => {{
        e.stopPropagation();
        draggingCursor = label;
    }});
    g.appendChild(hitArea);
    svg.appendChild(g);
}}

function createSVG(tag, attrs) {{
    const el = document.createElementNS(NS, tag);
    for (const [k, v] of Object.entries(attrs)) el.setAttribute(k, v);
    return el;
}}

// ========== 交互 ==========
function bindEvents() {{
    window.addEventListener("resize", () => {{ calcSize(); render(); }});

    container.addEventListener("wheel", (e) => {{
        e.preventDefault();
        const rect = container.getBoundingClientRect();
        const mouseX = e.clientX - rect.left - PIN_LABEL_W;
        const frac = mouseX / containerW;
        const zoomFactor = e.deltaY < 0 ? 0.8 : 1.25;

        const mouseVec = viewStart + frac * viewCount;
        let newCount = viewCount * zoomFactor;
        newCount = Math.max(10, Math.min(TOTAL, newCount));
        const newStart = mouseVec - frac * newCount;

        viewCount = newCount;
        viewStart = Math.max(0, Math.min(TOTAL - viewCount, newStart));
        render();
    }}, {{ passive: false }});

    document.addEventListener("mousemove", (e) => {{
        if (draggingCursor) {{
            const rect = container.getBoundingClientRect();
            const mouseX = e.clientX - rect.left - PIN_LABEL_W;
            const vecIdx = Math.round(viewStart + mouseX / pixPerVec);
            const clamped = Math.max(0, Math.min(TOTAL - 1, vecIdx));
            if (draggingCursor === "A") cursorA = clamped;
            else cursorB = clamped;
            render();
        }}
        if (isDragging && !draggingCursor) {{
            const dx = e.clientX - dragStartX;
            const dVec = -dx / pixPerVec;
            viewStart = Math.max(0, Math.min(TOTAL - viewCount, dragStartView + dVec));
            render();
        }}
    }});

    document.addEventListener("mouseup", () => {{
        draggingCursor = null;
        isDragging = false;
    }});

    // 按钮
    document.getElementById("btn-zoomfit").addEventListener("click", () => {{ fitAll(); render(); }});
    document.getElementById("btn-zoomin").addEventListener("click", () => {{
        const center = viewStart + viewCount / 2;
        viewCount = Math.max(10, viewCount * 0.6);
        viewStart = Math.max(0, Math.min(TOTAL - viewCount, center - viewCount / 2));
        render();
    }});
    document.getElementById("btn-zoomout").addEventListener("click", () => {{
        const center = viewStart + viewCount / 2;
        viewCount = Math.min(TOTAL, viewCount * 1.6);
        viewStart = Math.max(0, Math.min(TOTAL - viewCount, center - viewCount / 2));
        render();
    }});
    document.getElementById("btn-cursor-toggle").addEventListener("click", () => {{
        cursorsVisible = !cursorsVisible;
        document.getElementById("btn-cursor-toggle").classList.toggle("active", cursorsVisible);
        if (cursorsVisible && cursorA < 0) {{
            cursorA = Math.floor(viewStart + viewCount * 0.3);
            cursorB = Math.floor(viewStart + viewCount * 0.7);
        }}
        render();
    }});
    document.getElementById("btn-play").addEventListener("click", togglePlay);
    document.getElementById("btn-faster").addEventListener("click", () => {{
        playSpeed = Math.min(64, playSpeed * 2);
        document.getElementById("speed-display").textContent = playSpeed + "x";
    }});
    document.getElementById("btn-slower").addEventListener("click", () => {{
        playSpeed = Math.max(1, playSpeed / 2);
        document.getElementById("speed-display").textContent = playSpeed + "x";
    }});
}}

function onMouseDown(e) {{
    if (draggingCursor) return;
    isDragging = true;
    dragStartX = e.clientX;
    dragStartView = viewStart;
}}

function onMouseMove(e) {{
    if (isDragging || draggingCursor) return;
    const rect = svg.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;
    const vecIdx = Math.floor(viewStart + mouseX / pixPerVec);

    if (vecIdx < 0 || vecIdx >= TOTAL) {{
        tooltip.style.display = "none";
        return;
    }}

    const vec = VECTORS[vecIdx];
    if (!vec) {{ tooltip.style.display = "none"; return; }}

    const timeNs = vecIdx * PERIOD_NS;
    const timeStr = timeNs >= 1e6 ? (timeNs / 1e6).toFixed(2) + " ms"
                  : timeNs >= 1e3 ? (timeNs / 1e3).toFixed(1) + " \\u00B5s"
                  : timeNs + " ns";

    let html = '<div><span class="tt-label">Vector: </span><span class="tt-value">#' + vecIdx + '</span></div>';
    html += '<div><span class="tt-label">Time: </span><span class="tt-value">' + timeStr + '</span></div>';
    PINS.forEach(pin => {{
        const st = vec[pin] || "X";
        const clr = PIN_COLORS[pin] || "#e0e0e0";
        html += '<div><span class="tt-label">' + pin + ': </span>'
              + '<span class="tt-value" style="color:' + clr + '">' + st + '</span></div>';
    }});
    if (vec.seg) {{
        html += '<div style="margin-top:3px"><span class="tt-seg" style="background:'
              + vec.seg_color + '">' + vec.seg + '</span></div>';
    }}
    if (vec.comment) {{
        html += '<div style="margin-top:2px;color:#8899aa;font-size:10px">' + vec.comment + '</div>';
    }}

    tooltip.innerHTML = html;
    tooltip.style.display = "block";

    // 定位浮窗
    let tx = e.clientX + 15;
    let ty = e.clientY + 15;
    const tw = tooltip.offsetWidth;
    const th = tooltip.offsetHeight;
    if (tx + tw > window.innerWidth - 10) tx = e.clientX - tw - 10;
    if (ty + th > window.innerHeight - 10) ty = e.clientY - th - 10;
    tooltip.style.left = tx + "px";
    tooltip.style.top = ty + "px";
}}

// ========== 段跳转 ==========
function jumpToSection(idx) {{
    const sec = SECTIONS[idx];
    if (!sec) return;

    // 高亮段色块
    document.querySelectorAll(".seg-chip").forEach((el, i) => {{
        el.classList.toggle("highlight", i === idx);
    }});
    highlightedSeg = (highlightedSeg === idx) ? null : idx;

    if (highlightedSeg !== null) {{
        const margin = Math.max(10, viewCount * 0.05);
        const secLen = sec.end - sec.start + 1;
        viewCount = Math.max(Math.min(secLen + margin * 2, TOTAL), 10);
        viewStart = Math.max(0, sec.start - margin);
    }}
    render();
}}

// ========== 播放 ==========
function togglePlay() {{
    playing = !playing;
    const btn = document.getElementById("btn-play");
    if (playing) {{
        btn.textContent = "\\u23F8 Pause";
        btn.classList.add("active");
        playIdx = Math.floor(viewStart);
        animateStep();
    }} else {{
        btn.textContent = "\\u25B6 Play";
        btn.classList.remove("active");
        if (playRAF) cancelAnimationFrame(playRAF);
        playRAF = null;
        render();
    }}
}}

function animateStep() {{
    if (!playing) return;
    playIdx += playSpeed;
    if (playIdx >= TOTAL) {{
        playIdx = 0;
        viewStart = 0;
    }}
    // 自动滚动: 播放位置超出视图右侧80%时前进
    const px = (playIdx - viewStart) * pixPerVec;
    if (px > containerW * 0.85) {{
        viewStart = Math.min(TOTAL - viewCount, playIdx - viewCount * 0.15);
    }}
    if (px < 0) {{
        viewStart = Math.max(0, playIdx - viewCount * 0.1);
    }}
    render();
    playRAF = requestAnimationFrame(animateStep);
}}

// ========== 辅助 ==========
function fitAll() {{
    viewStart = 0;
    viewCount = TOTAL;
}}

function updateInfoBar() {{
    const s = Math.floor(viewStart);
    const e = Math.min(TOTAL - 1, Math.ceil(viewStart + viewCount));
    document.getElementById("view-range").textContent = s + " ~ " + e + " (" + (e - s + 1) + " vectors)";
}}

function updateCursorInfo() {{
    if (!cursorsVisible || cursorA < 0 || cursorB < 0) {{
        document.getElementById("cur-a-info").textContent = "-";
        document.getElementById("cur-b-info").textContent = "-";
        document.getElementById("cur-delta").textContent = "-";
        return;
    }}
    const fmt = (idx) => "#" + idx + " (" + fmtTime(idx * PERIOD_NS) + ")";
    document.getElementById("cur-a-info").textContent = fmt(cursorA);
    document.getElementById("cur-b-info").textContent = fmt(cursorB);
    const delta = Math.abs(cursorB - cursorA);
    const dt = delta * PERIOD_NS;
    document.getElementById("cur-delta").textContent = delta + " vec, " + fmtTime(dt);
}}

function fmtTime(ns) {{
    if (ns >= 1e6) return (ns / 1e6).toFixed(2) + " ms";
    if (ns >= 1e3) return (ns / 1e3).toFixed(1) + " \\u00B5s";
    return ns + " ns";
}}

// ========== 启动 ==========
window.addEventListener("DOMContentLoaded", init);
</script>
</body>
</html>"""
