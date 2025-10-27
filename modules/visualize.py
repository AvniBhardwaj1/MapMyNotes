"""
modules/visualize.py
--------------------
🎯 Interactive D3 Mind Map for MapMyNotes

✅ Unlimited hierarchy (auto root detection)
✅ Smart text wrapping inside nodes
✅ Auto-resizing pastel nodes (no overflow)
✅ Hover tooltips, zoom & pan
✅ Download as PNG button
"""

import streamlit as st
import json
from modules.hover_tooltip import generate_tooltip_js


def visualize_graph(data, title="MapMyNotes – Mind Map", height=850, width=1400):
    """Render an interactive, zoomable, exportable D3 mind map."""
    if not data or "nodes" not in data or "edges" not in data:
        st.warning("⚠️ No mind map data available to visualize.")
        return

    graph_json = json.dumps(data)
    tooltip_js = generate_tooltip_js()

    html_code = fr"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <script src="https://d3js.org/d3.v7.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/save-svg-as-png@1.4.17/lib/saveSvgAsPng.min.js"></script>
        <style>
            body {{
                background: #f8f9fb;
                font-family: 'Inter', sans-serif;
                overflow: hidden;
            }}
            #mindmap-container {{
                position: relative;
                margin: auto;
                width: {width}px;
            }}
            #downloadBtn {{
                position: absolute;
                bottom: 15px;
                right: 20px;
                padding: 8px 14px;
                background: #2563eb;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                cursor: pointer;
                box-shadow: 0 2px 6px rgba(0,0,0,0.15);
            }}
            #downloadBtn:hover {{ background: #1d4ed8; }}
            #tooltip-box {{
                position: absolute;
                pointer-events: none;
                z-index: 10;
                visibility: hidden;
                font-size: 12px;
                background: #fff;
                border: 1px solid #d1d5db;
                border-radius: 8px;
                padding: 10px;
                color: #111827;
                box-shadow: 0 2px 8px rgba(0,0,0,0.15);
                max-width: 260px;
            }}
        </style>
    </head>

    <body>
        <h3 style="text-align:center; color:#1e293b;">{title}</h3>
        <div id="mindmap-container">
            <div id="mindmap"></div>
            <button id="downloadBtn">📸 Download Mind Map</button>
        </div>

        <script>
            const data = {graph_json};
            const width = {width};
            const height = {height};
            const margin = {{ top: 80, right: 220, bottom: 80, left: 220 }};

            // --- SVG setup ---
            const svg = d3.select("#mindmap")
                .append("svg")
                .attr("id", "mindmap-svg")
                .attr("width", width)
                .attr("height", height)
                .style("background", "#f8fafc")
                .style("border-radius", "16px")
                .style("box-shadow", "0 4px 18px rgba(0,0,0,0.08)");

            const g = svg.append("g");

            // --- Build hierarchy (detect true root) ---
            const nodeById = new Map();
            data.nodes.forEach(n => nodeById.set(n.id, {{...n, children: []}}));

            const targets = new Set();
            data.edges.forEach(e => {{
                const parent = nodeById.get(e.source);
                const child = nodeById.get(e.target);
                if (parent && child) parent.children.push(child);
                targets.add(e.target);
            }});

            let rootNode = null;
            for (const [id, node] of nodeById) {{
                if (!targets.has(id)) {{ rootNode = node; break; }}
            }}
            if (!rootNode) rootNode = nodeById.values().next().value;

            const hierarchy = d3.hierarchy(rootNode);
            const treeLayout = d3.tree().nodeSize([110, 240]);
            treeLayout(hierarchy);

            // --- Color palette ---
            const pastelColors = [
                "#a0c4ff", "#bdb2ff", "#ffc6ff", "#caffbf", "#ffd6a5",
                "#fdffb6", "#ffadad", "#9bf6ff", "#b9fbc0", "#ffb5a7",
                "#c8b6ff", "#fbc4ab", "#ffd7ba"
            ];
            const colorScale = d3.scaleOrdinal(pastelColors);

            // --- Draw links ---
            g.selectAll(".link")
                .data(hierarchy.links())
                .enter()
                .append("path")
                .attr("fill", "none")
                .attr("stroke", "#cbd5e1")
                .attr("stroke-width", 1.6)
                .attr("d", d3.linkHorizontal().x(d => d.y).y(d => d.x));

            // --- Draw nodes ---
            const node = g.selectAll(".node")
                .data(hierarchy.descendants())
                .enter()
                .append("g")
                .attr("class", "node")
                .attr("transform", d => `translate(${{d.y}},${{d.x}})`);

            // --- Draw dynamic rect background ---
            node.append("rect")
                .attr("x", -100)
                .attr("y", -28)
                .attr("rx", 16)
                .attr("ry", 16)
                .attr("width", 200)
                .attr("height", 60)
                .attr("fill", d => colorScale(d.depth))
                .attr("stroke", "#334155")
                .attr("stroke-width", 1.2)
                .style("filter", "drop-shadow(0 2px 4px rgba(0,0,0,0.1))");

            // --- Add wrapped title ---
            const wrapText = (text, width) => {{
                text.each(function() {{
                    const textEl = d3.select(this);
                    const words = textEl.text().split(/\s+/).reverse();
                    let line = [], lineNumber = 0;
                    const y = textEl.attr("y");
                    const dy = parseFloat(textEl.attr("dy")) || 0;
                    let tspan = textEl.text(null)
                        .append("tspan")
                        .attr("x", 0)
                        .attr("y", y)
                        .attr("dy", dy + "em");
                    let word;
                    while (word = words.pop()) {{
                        line.push(word);
                        tspan.text(line.join(" "));
                        if (tspan.node().getComputedTextLength() > width - 18) {{
                            line.pop();
                            tspan.text(line.join(" "));
                            line = [word];
                            tspan = textEl.append("tspan")
                                .attr("x", 0)
                                .attr("y", y)
                                .attr("dy", ++lineNumber * 1.1 + dy + "em")
                                .text(word);
                        }}
                    }}
                }});
            }};

            node.append("text")
                .attr("text-anchor", "middle")
                .attr("dy", "-0.2em")
                .style("font-weight", "600")
                .style("font-size", "13px")
                .style("font-family", "Inter, sans-serif")
                .style("fill", "#111827")
                .text(d => d.data.label || "")
                .call(wrapText, 180);

            // --- Add summary text ---
            node.append("text")
                .attr("text-anchor", "middle")
                .attr("dy", "1.5em")
                .style("font-size", "11px")
                .style("font-family", "Inter, sans-serif")
                .style("fill", "#374151")
                .text(d => {{
                    const s = d.data.summary || "";
                    return s.length > 65 ? s.slice(0, 65) + "..." : s;
                }});

            // --- Adjust node size based on content ---
            node.each(function(d) {{
                const titleBox = d3.select(this).select("text").node().getBBox();
                const totalHeight = Math.max(55, titleBox.height + 40);
                const width = Math.min(Math.max(titleBox.width + 60, 180), 280);
                d3.select(this).select("rect")
                    .attr("x", -width/2)
                    .attr("width", width)
                    .attr("y", -totalHeight/2)
                    .attr("height", totalHeight);
            }});

            // --- Zoom & pan ---
            const zoom = d3.zoom()
                .scaleExtent([0.4, 2])
                .on("zoom", (event) => g.attr("transform", event.transform));
            svg.call(zoom);

            // --- Centering ---
            const bbox = g.node().getBBox();
            const xOffset = (width - bbox.width) / 2 - bbox.x;
            const yOffset = (height - bbox.height) / 2 - bbox.y;
            g.attr("transform", `translate(${{xOffset}},${{yOffset}})`);

            // --- Tooltip logic ---
            {tooltip_js}

            // --- PNG download ---
            document.getElementById("downloadBtn").addEventListener("click", () => {{
                const svgNode = document.getElementById("mindmap-svg");
                saveSvgAsPng(svgNode, "MapMyNotes_MindMap.png", {{
                    backgroundColor: "#f8fafc",
                    scale: 2
                }});
            }});
        </script>
    </body>
    </html>
    """

    st.components.v1.html(html_code, height=height + 180, scrolling=True)
