import os

import gradio as gr
from research_manager import ResearchManager


async def run_research(query: str):
    """
    Run the ResearchManager for the given query, streaming intermediate
    status updates and the final markdown report back to the Gradio UI.

    Args:
        query: The research question/topic entered by the user.
    """
    if not query or not query.strip():
        yield "Please enter a query to research."
        return

    manager = ResearchManager()
    output = ""
    async for chunk in manager.run(query):
        output += f"{chunk}\n\n"
        yield output


EXAMPLE_PROMPTS = [
    "Latest developments in autonomous AI agents",
    "Top places to visit in Dehradun",
    "Best practices for building scalable REST APIs",
    "How is quantum computing impacting cryptography?",
    "Emerging trends in renewable energy storage",
]

# ---------------------------------------------------------------------------
# Warm, editorial-style research workspace
# ---------------------------------------------------------------------------
theme = gr.themes.Soft(
    primary_hue=gr.themes.colors.orange,
    secondary_hue=gr.themes.colors.orange,
    neutral_hue=gr.themes.colors.stone,
).set(
    body_background_fill="#faf8f5",
    body_background_fill_dark="#171513",
    background_fill_primary="#ffffff",
    background_fill_secondary="#fff7ed",
    block_background_fill="#ffffff",
    block_border_color="#eee7df",
    button_primary_background_fill="#ea580c",
    button_primary_background_fill_hover="#c2410c",
    button_primary_text_color="#ffffff",
    block_title_text_color="#292524",
    block_label_text_color="#57534e",
)

CUSTOM_CSS = """
body { background: #faf8f5 !important; }
.gradio-container { max-width: 1080px !important; margin: 0 auto !important; }
#findora-header { text-align: center; padding: 54px 20px 28px; }
#findora-header .eyebrow {
    display: inline-flex; align-items: center; gap: 8px; padding: 7px 12px;
    border: 1px solid #fed7aa; border-radius: 999px; background: #fff7ed;
    color: #c2410c; font-size: 12px; font-weight: 700; letter-spacing: .08em;
    text-transform: uppercase;
}
#findora-header h1 {
    margin: 18px 0 10px; color: #1c1917; font-size: clamp(42px, 7vw, 68px);
    line-height: 1; letter-spacing: -.055em; font-weight: 800;
}
#findora-header h1 span { color: #ea580c; }
#findora-header p {
    max-width: 610px; margin: 0 auto; color: #78716c;
    font-size: 17px; line-height: 1.7;
}
#workflow-strip {
    display: flex; justify-content: center; gap: 10px; flex-wrap: wrap;
    margin: 0 auto 28px; color: #78716c; font-size: 13px;
}
#workflow-strip span {
    padding: 8px 12px; border: 1px solid #eee7df; border-radius: 999px;
    background: rgba(255,255,255,.8);
}
#research-panel {
    padding: 24px; border: 1px solid #eee7df; border-radius: 20px;
    background: #fff; box-shadow: 0 14px 40px rgba(41, 37, 36, .06);
}
#research-panel textarea { font-size: 16px !important; line-height: 1.6 !important; }
#prompt-heading { margin: 18px 0 8px; color: #78716c; font-size: 12px; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; }
#examples-row { gap: 8px; flex-wrap: wrap; }
#examples-row button {
    flex: 1 1 180px; min-height: 42px; border: 1px solid #f3e8dc !important;
    border-radius: 12px !important; background: #fffaf5 !important;
    color: #57534e !important; transition: all .18s ease !important;
}
#examples-row button:hover {
    transform: translateY(-2px); border-color: #fdba74 !important;
    background: #fff1e6 !important; color: #c2410c !important;
}
#run-btn { min-height: 52px; border-radius: 13px !important; font-size: 16px !important; font-weight: 700 !important; }
#results-heading { margin: 30px 0 12px; color: #292524; font-size: 19px; font-weight: 750; }
#report-output {
    min-height: 150px; padding: 22px; border: 1px solid #eee7df;
    border-radius: 18px; background: #fff; box-shadow: 0 8px 28px rgba(41,37,36,.035);
}
#footer-note { padding: 22px 10px 38px; color: #a8a29e; text-align: center; font-size: 12px; }
@media (max-width: 640px) {
    #findora-header { padding-top: 36px; }
    #research-panel { padding: 16px; }
    #examples-row button { flex-basis: 100%; }
}
"""

with gr.Blocks(title="Findora — Research, made clear") as ui:
    gr.HTML(
        """
        <header id="findora-header">
            <div class="eyebrow">✦ Your research copilot</div>
            <h1>Findora<span>.</span></h1>
            <p>Turn a big question into a clear, sourced report. Tell Findora what
            you're curious about and let the research unfold.</p>
        </header>
        <div id="workflow-strip">
            <span>01 &nbsp; Plan the research</span><span>02 &nbsp; Explore the web</span>
            <span>03 &nbsp; Get your report</span>
        </div>
        """
    )

    with gr.Group(elem_id="research-panel"):
        query_textbox = gr.Textbox(
            label="What are you curious about?",
            placeholder="Ask a focused question or describe a topic to explore…",
            lines=3,
            max_lines=6,
            autofocus=True,
        )

        gr.HTML('<div id="prompt-heading">Need a starting point? Try one of these</div>')
        with gr.Row(elem_id="examples-row"):
            example_buttons = [gr.Button(prompt, size="sm") for prompt in EXAMPLE_PROMPTS]

        run_button = gr.Button("✦  Start researching", variant="primary", elem_id="run-btn")

    gr.HTML('<div id="results-heading">Your research brief</div>')
    report_output = gr.Markdown(
        value="Your research progress and final report will appear here.",
        elem_id="report-output",
    )
    gr.HTML('<div id="footer-note">Thoughtful research, one question at a time.</div>')

    run_button.click(fn=run_research, inputs=query_textbox, outputs=report_output)
    query_textbox.submit(fn=run_research, inputs=query_textbox, outputs=report_output)

    for btn, prompt in zip(example_buttons, EXAMPLE_PROMPTS):
        btn.click(fn=lambda p=prompt: p, inputs=None, outputs=query_textbox)


if __name__ == "__main__":
    ui.launch(
        server_name="0.0.0.0",
        server_port=int(os.environ.get("PORT", "7860")),
        inbrowser=False,
        theme=theme,
        css=CUSTOM_CSS,
    )
