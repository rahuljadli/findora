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
# Custom white & orange theme
# ---------------------------------------------------------------------------
theme = gr.themes.Soft(
    primary_hue=gr.themes.colors.orange,
    secondary_hue=gr.themes.colors.orange,
    neutral_hue=gr.themes.colors.gray,
).set(
    body_background_fill="#ffffff",
    body_background_fill_dark="#ffffff",
    background_fill_primary="#ffffff",
    background_fill_secondary="#fff7f0",
    block_background_fill="#ffffff",
    block_border_color="#f3d9c4",
    button_primary_background_fill="#f97316",
    button_primary_background_fill_hover="#ea580c",
    button_primary_text_color="#ffffff",
    block_title_text_color="#ea580c",
    block_label_text_color="#ea580c",
)

CUSTOM_CSS = """
#findora-header {
    text-align: center;
    padding: 24px 12px 8px 12px;
}
#findora-header h1 {
    color: #ea580c;
    font-size: 2.4em;
    margin-bottom: 4px;
}
#findora-header p {
    color: #6b7280;
    font-size: 1.05em;
}
#examples-row button {
    border: 1px solid #f97316 !important;
    color: #ea580c !important;
    background: #fff7f0 !important;
}
#examples-row button:hover {
    background: #f97316 !important;
    color: #ffffff !important;
}
#run-btn {
    font-size: 1.05em !important;
}
"""

with gr.Blocks(title="Findora - AI Research Assistant", theme=theme, css=CUSTOM_CSS) as ui:
    gr.HTML(
        """
        <div id="findora-header">
            <h1>🔎 Findora</h1>
            <p>Your AI-powered research assistant — plans searches, scours the web,
            writes a polished report, and emails it straight to your inbox.</p>
        </div>
        """
    )

    with gr.Row():
        query_textbox = gr.Textbox(
            label="What would you like to research?",
            placeholder="e.g. Latest developments in autonomous AI agents",
            lines=2,
            scale=4,
        )

    gr.Markdown("**Try an example:**")
    with gr.Row(elem_id="examples-row"):
        example_buttons = [gr.Button(prompt, size="sm") for prompt in EXAMPLE_PROMPTS]

    run_button = gr.Button("🚀 Run Research", variant="primary", elem_id="run-btn")

    report_output = gr.Markdown(label="Research Progress & Report")

    run_button.click(fn=run_research, inputs=query_textbox, outputs=report_output)
    query_textbox.submit(fn=run_research, inputs=query_textbox, outputs=report_output)

    for btn, prompt in zip(example_buttons, EXAMPLE_PROMPTS):
        btn.click(fn=lambda p=prompt: p, inputs=None, outputs=query_textbox)


if __name__ == "__main__":
    ui.launch(inbrowser=True)
