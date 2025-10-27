# modules/hover_tooltip.py
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = genai.GenerativeModel("models/gemini-2.5-flash")


def explain_node_in_layman(text: str) -> str:
    """
    Generate a layman-friendly yet technically sound explanation for a node.
    """
    prompt = f"""
    You are an educational AI assistant. Explain the following topic clearly:
    "{text}"
    
    Requirements:
    - Start with a simple layman’s explanation (2–3 lines)
    - Follow with a short technical explanation (2–3 lines)
    - End with a quick learning tip or analogy.
    Make it easy to understand but still informative.
    """
    try:
        response = MODEL.generate_content(prompt)
        return response.text.strip()
    except Exception:
        return "Detailed explanation unavailable for now."


def generate_tooltip_js():
    """
    Returns JavaScript for hover tooltip that shows precomputed AI explanations
    from node metadata (d.data.ai_explanation).
    """
    js_code = """
    const tooltip = d3.select("#mindmap").append("div")
        .attr("id", "tooltip-box")
        .style("position", "absolute")
        .style("background", "#ffffffee")
        .style("border", "1px solid #d1d5db")
        .style("border-radius", "10px")
        .style("padding", "10px 14px")
        .style("box-shadow", "0 4px 16px rgba(0,0,0,0.15)")
        .style("visibility", "hidden")
        .style("max-width", "340px")
        .style("font-family", "Inter, sans-serif");

    node.on("mouseover", (event, d) => {
        const explanation = d.data.ai_explanation || "No explanation available.";

        tooltip.html(`
            <div style='font-weight:600;font-size:14px;color:#111827;margin-bottom:4px;'>${d.data.label}</div>
            <div style='font-size:13px;color:#374151;line-height:1.5;'>${explanation}</div>
        `);

        tooltip.style("top", (event.pageY - 50) + "px")
               .style("left", (event.pageX + 20) + "px")
               .style("visibility", "visible");
    });

    node.on("mouseout", () => tooltip.style("visibility", "hidden"));
    """
    return js_code
