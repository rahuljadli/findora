import os
import smtplib
import markdown
from dotenv import load_dotenv
from agents import Agent, ModelSettings,  function_tool, OpenAIChatCompletionsModel
from openai import AsyncOpenAI
from email.message import EmailMessage

load_dotenv(override=True)

# ---------------------------------------------------------------------------
# Model setup - using Gemini (free tier) via the OpenAI-compatible endpoint.
# ---------------------------------------------------------------------------
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
google_api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")

gemini_client = AsyncOpenAI(
    base_url=GEMINI_BASE_URL,
    api_key=google_api_key,
    timeout=60.0,
    max_retries=5,
)

search_model = OpenAIChatCompletionsModel(
    model="gemini-3.5-flash-lite",
    openai_client=gemini_client,
)

EMAIL_ADDRESS = os.environ.get("EMAIL_ADDRESS")
EMAIL_APP_PASSWORD = os.environ.get("EMAIL_APP_PASSWORD")
EMAIL_SMTP_SERVER = os.environ.get("EMAIL_SMTP_SERVER", "smtp.gmail.com")

def send_message(subject, text_body, html_body):
    msg = EmailMessage()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = EMAIL_ADDRESS
    msg["Subject"] = subject
    msg.set_content(text_body)
    msg.add_alternative(html_body, subtype="html")

    with smtplib.SMTP(EMAIL_SMTP_SERVER, 587) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_APP_PASSWORD)
        server.send_message(msg)

@function_tool 
def send_email(to: str, subject: str, body: str) -> str:
    """
    Send an email using the provided parameters.
    Params:
        to: Recipient email address.
        subject: Subject of the email.
        body: Body content of the email (markdown is supported and will be
            converted to HTML for the rendered email view).
    """
    try:
        html_body = markdown.markdown(
            body, extensions=["extra", "sane_lists", "nl2br"]
        )
        send_message(subject, body, html_body)
        return f"Email sent to {to} with subject '{subject}'."
    except Exception:
        return "Email could not be sent."


settings = ModelSettings(tool_choice="required")

instrunctions = "You are an Email Agent." \
"You are to send the email using the send_email function tool and return a confirmation message that the email has been sent successfully."
"Create appropriate subject line and body for the email based on the given information."

email_agent = Agent(
    name="EmailAgent",
    model=search_model,
    instructions=instrunctions,
    tools=[send_email],
    model_settings=settings,
)