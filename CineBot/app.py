
import streamlit as st
import requests
import uuid
import os
import zipfile
import xml.etree.ElementTree as ET
from dotenv import load_dotenv
from tavily import TavilyClient

# Load private API settings from the project .env file
load_dotenv()
TAVILY_API_KEY = os.getenv('TAVILY_API_KEY')

# ==========================================
# 1. CINEBOT CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="CineBot AI",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

OLLAMA_URL = os.getenv("OLLAMA_URL", os.getenv("OLLAMA_PROXY_URL", "http://localhost:11434/api/chat")).rstrip("/")
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY", "")
OLLAMA_HEADERS = {"Authorization": f"Bearer {OLLAMA_API_KEY}"} if OLLAMA_API_KEY else {}
OLLAMA_TAGS_URL = os.getenv("OLLAMA_TAGS_URL", OLLAMA_URL.rsplit("/api/chat", 1)[0] + "/api/tags")
MODEL = "qwen2.5:1.5b"


# ==========================================
# 2. CINEBOT SYSTEM PROMPT
# ==========================================

SYSTEM_PROMPT = """
You are CineBot AI, a knowledgeable filmmaking and
screenwriting assistant.

YOUR EXPERTISE:
1. Film direction and visual storytelling.
2. Screenwriting and screenplay formatting.
3. Story structure, character development and dialogue.
4. Cinematography, camera movement and composition.
5. Lighting, lenses, exposure and camera techniques.
6. Film editing, sound design and continuity.
7. Pre-production, production and post-production.
8. Shot lists, storyboards and script breakdowns.
9. Film history, filmmakers and cinema analysis.

ACCURACY RULES:
- Give technically accurate filmmaking explanations.
- Never invent film scenes, shots, quotations or production facts.
- If you are uncertain, clearly say so.
- Separate verified facts from your own interpretation.
- Never present an imaginary example as a real movie scene.
- Correct misunderstandings politely.

EYELINE MATCH ACCURACY:
- An eyeline match connects a character looking in
  a particular direction with a following shot that
  shows what the character is looking at.
- Do not confuse eyeline match with reaction shots.
- A reaction shot shows another character's
  emotional response to an event or dialogue.
- Shot-reverse-shot alternates between shots of
  two characters, usually during a conversation.
- The 180-degree rule maintains consistent screen
  direction by keeping camera positions on the
  established side of the imaginary axis.
- Explain the difference between these techniques
  using separate practical examples.
- Never label a reaction shot as an eyeline match
  unless the editing establishes a matching gaze.

CAMERA AND EDITING KNOWLEDGE:
- The 180-degree rule establishes an imaginary axis
  between two characters, or along the direction of
  movement or action.
- Camera positions should generally remain on the
  same side of the established axis.
- Do not confuse the imaginary axis with a physical
  line that actors must stand on.
- Shot-reverse-shot is an editing technique that
  alternates between shots of two characters.
- Explain eyelines, screen direction, and continuity
  when discussing shot-reverse-shot.
- Do not describe camera movement as a requirement
  for shot-reverse-shot.
- Distinguish a camera crossing the axis from an
  actor crossing the axis.
- Explain camera techniques using practical examples.
- If a question is ambiguous, clarify the intended
  filmmaking concept before giving technical advice.

TEACHING STYLE:
- Use simple English when appropriate.
- Explain technical terms clearly.
- Give practical examples.
- Use real film examples only when confident.
- Explain how a technique affects the audience.
- Structure detailed answers with headings and steps.

FILMMAKING TECHNICAL PRECISION:
- Explain filmmaking concepts using technically
  correct definitions.
- Distinguish camera position, camera movement,
  framing, and editing.
- Never confuse the 180-degree rule with camera movement.
- For dialogue scenes, explain the imaginary axis
  between two characters.
- Explain that cameras generally remain on the same
  side of this axis to maintain screen direction.
- Explain that crossing the axis can reverse screen
  direction and confuse viewers.
- Clarify that crossing the axis is allowed when
  handled deliberately.
- Explain methods of crossing the axis, including a
  continuous camera move, a neutral shot, or a clear
  transition.
- Never invent specific movie scenes or claim that
  an imaginary example is from a real film.
- Use simple practical examples before advanced
  technical explanations.

CREATIVE RULES:
- Respect the filmmaker's original vision.
- Do not rewrite a story unless requested.
- Preserve the intended tone, characters and themes.
- Offer alternatives without forcing creative changes.

180-DEGREE RULE — STRICT TECHNICAL ACCURACY:

- In a two-character dialogue scene, the imaginary
  axis is generally the line connecting the two
  characters' positions.
- The camera should generally remain on one
  established side of this axis.
- Never say that the camera must be on the same
  side of the axis as the characters.
- Explain that maintaining camera positions on
  one side preserves consistent screen direction.
- Crossing the axis can reverse the characters'
  apparent screen positions and eyelines.
- A neutral shot is a shot that reduces directional
  bias, often filmed on or near the axis. It is not
  necessarily a wide shot.
- A continuous camera movement across the axis,
  a neutral shot, or a clear editorial transition
  can establish a new screen direction.
- These are alternative techniques, not mandatory
  consecutive steps.
- Never confuse an actor crossing the axis with
  the camera crossing the axis.
- Always use a clear practical example involving
  two characters and explain their screen positions.

IDENTITY:
You are CineBot AI, a filmmaking chatbot.
You are not an autonomous agent.
Respond directly to the user's requests.


SCREENWRITING SPECIALIST MODE

You are an expert screenwriting assistant. Your purpose is to help writers develop, write, analyse, format and rewrite screenplays.

1. STORY FUNDAMENTALS
Understand premise, concept, theme, logline, synopsis, story, plot, conflict and dramatic stakes. Explain their differences with examples.

2. STORY STRUCTURE
Understand three-act structure, five-act structure, nonlinear narratives, parallel storylines, flashbacks, flashforwards, inciting incidents, turning points, midpoint, climax and resolution. Do not force every story into a fixed structure.

3. CHARACTER DEVELOPMENT
Help create believable characters with goals, motivations, flaws, internal conflicts, external conflicts, relationships, backstories and character arcs. Ensure character decisions influence the story.

4. SCREENPLAY FORMATTING
Understand professional screenplay elements:
- Scene heading (INT./EXT., LOCATION, TIME)
- Action and description
- Character cues
- Dialogue
- Parentheticals
- Transitions
- Montage and intercut sequences

Use standard screenplay formatting when requested.

5. SCENE CONSTRUCTION
Help develop scenes using objectives, obstacles, conflict, tension, subtext, beats, entrances, exits and scene transitions. Every scene should have a dramatic purpose.

6. DIALOGUE WRITING
Write natural, character-specific dialogue. Avoid unnecessary exposition, repetitive conversations and unnatural explanations. Understand subtext, silence, interruptions and conversational rhythm.

7. SCREENPLAY ANALYSIS
Analyse scenes, characters, structure, themes, pacing and cinematic storytelling. Clearly distinguish interpretation from verified facts.

8. REWRITING AND STORY ADAPTATION
When rewriting a user's story:
- Preserve the original premise and intended meaning.
- Do not introduce major plot changes without permission.
- Maintain character consistency.
- Follow the format requested by the user.
- Explain important structural changes when useful.

9. PRACTICAL SCREENWRITING SUPPORT
Help create loglines, synopses, beat sheets, treatments, character profiles, scene outlines, screenplay drafts and script breakdowns.

10. TEACHING APPROACH
Teach screenwriting in simple English with practical examples. Explain why a technique works, not just what it means.

IMPORTANT:
Never invent quotations, screenplay excerpts, production facts or claims about existing films. Distinguish established screenwriting principles from individual creative preferences.

"""

# ==========================================
# CINEBOT - NEBULA PREMIUM WORKSPACE
# ==========================================

# 1. DESIGN SYSTEM

st.markdown("""
<style>

/* Main background and atmospheric lighting */

.stApp {
    background:
        radial-gradient(
            ellipse 850px 550px at 48% -12%,
            rgba(100, 64, 190, 0.25),
            transparent 72%
        ),
        radial-gradient(
            ellipse 650px 450px at 100% 45%,
            rgba(35, 100, 180, 0.13),
            transparent 75%
        ),
        radial-gradient(
            ellipse 500px 350px at 0% 85%,
            rgba(111, 54, 155, 0.10),
            transparent 75%
        ),
        #0B0C12;

    color: #F3F1FA;
}

/* Header */

[data-testid="stHeader"] {
    background: rgba(11, 12, 18, 0.8);
}

/* Sidebar */

[data-testid="stSidebar"] {
    background: #11121B;
    border-right: 1px solid #282638;
}

[data-testid="stSidebar"] * {
    color: #E9E7F1;
}

/* Main content */

.block-container {
    max-width: 1100px;
    padding-top: 2rem;
    padding-bottom: 6rem;
}

/* Branding */

.cine-logo {
    font-size: 27px;
    font-weight: 750;
    letter-spacing: 3px;
    color: #E5D8FF;
}

.cine-logo span {
    color: #A98BFF;
}

.cine-tagline {
    font-size: 10px;
    letter-spacing: 2px;
    color: #9692AA;
}

/* Welcome section */

.hero {
    position: relative;
    overflow: hidden;
    background:
        radial-gradient(
            ellipse at 85% 5%,
            rgba(130, 86, 230, 0.25),
            transparent 55%
        ),
        linear-gradient(
            125deg,
            #191729,
            #11131E 65%,
            #17162B
        );

    border: 1px solid #38304E;
    border-radius: 18px;
    padding: 46px 42px;
    margin-top: 30px;
    margin-bottom: 30px;
}

.hero-label {
    color: #B49AFF;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 3px;
}

.hero-title {
    color: #F6F1FF;
    font-size: 43px;
    line-height: 1.2;
    font-weight: 650;
    margin-top: 20px;
}

.hero-title span {
    background: linear-gradient(
        90deg,
        #D6C1FF,
        #8F9CFF,
        #78C7F5
    );
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
}

.hero-description {
    color: #B7B4C8;
    font-size: 15px;
    line-height: 1.8;
    max-width: 650px;
    margin-top: 15px;
}

/* Section headings */

.section-heading {
    color: #EAE6F5;
    font-size: 17px;
    font-weight: 600;
    margin-bottom: 15px;
}

/* Image cards */

.card-title {
    color: #F1EDFA;
    font-size: 16px;
    font-weight: 600;
    margin-top: 8px;
}

.card-description {
    color: #AAA6BC;
    font-size: 12px;
    line-height: 1.6;
}

/* Images */

[data-testid="stImage"] img {
    border-radius: 12px;
    border: 1px solid #343047;
    filter: brightness(0.82) saturate(0.85);
    transition: all 0.3s ease;
}

[data-testid="stImage"] img:hover {
    filter: brightness(1) saturate(1);
}

/* Buttons */

.stButton > button {
    background: #1B1B2A;
    color: #E9E5F5;
    border: 1px solid #39364F;
    border-radius: 9px;
    min-height: 42px;
    transition: all 0.2s ease;
}

.stButton > button:hover {
    background: #302544;
    color: #FFFFFF;
    border-color: #9474E8;
}

/* Sidebar buttons */

[data-testid="stSidebar"] .stButton > button {
    background: transparent;
    border: 1px solid transparent;
    text-align: left;
}

[data-testid="stSidebar"] .stButton > button:hover {
    background: #252337;
    border-color: #39334F;
}

/* Chat messages */

[data-testid="stChatMessage"] {
    background: rgba(28, 28, 43, 0.85);
    border: 1px solid #343149;
    border-radius: 13px;
    padding: 16px;
    margin-bottom: 14px;
}

/* Chat composer */

[data-testid="stChatInput"] {
    background: #191A28;
    border: 1px solid #50466F;
    border-radius: 14px;
}

[data-testid="stChatInput"] textarea {
    color: #FFFFFF !important;
}

/* Readability */

.stMarkdown p,
.stMarkdown li,
.stMarkdown h1,
.stMarkdown h2,
.stMarkdown h3,
.stMarkdown h4 {
    color: #F0EDF7;
}

[data-testid="stCaptionContainer"] {
    color: #B4B0C3 !important;
}

hr {
    border-color: #343147;
}

/* Responsive adjustments */

@media (max-width: 700px) {
    .hero {
        padding: 28px 22px;
    }

    .hero-title {
        font-size: 31px;
    }
}

/* CineBot visible dark chat composer */

[data-testid="stBottom"] {
    background: transparent !important;
}

[data-testid="stChatInput"] {
    background: #171827 !important;
    border: 1px solid #8064C9 !important;
    border-radius: 16px !important;
    box-shadow: 0 0 20px rgba(130, 90, 220, 0.15) !important;
}

[data-testid="stChatInput"] textarea,
[data-testid="stChatInput"] textarea:focus {
    background: transparent !important;
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    caret-color: #B69AFF !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: #AAA6BC !important;
    -webkit-text-fill-color: #AAA6BC !important;
    opacity: 1 !important;
}

[data-testid="stChatInput"] button {
    color: #FFFFFF !important;
}

/* Creative workspace image consistency */
[data-testid="stImage"] {
    width: 100%;
}

[data-testid="stImage"] img {
    display: block;
    width: 100%;
    height: 190px;
    object-fit: cover;
    border-radius: 12px;
    border: 1px solid #343047;
    filter: brightness(0.88) saturate(0.92);
    transition: filter 0.25s ease, transform 0.25s ease;
}

[data-testid="stImage"] img:hover {
    filter: brightness(1) saturate(1);
}

.card-title {
    margin-top: 12px;
    margin-bottom: 5px;
}

.card-description {
    min-height: 38px;
    margin-bottom: 10px;
}

/* Keep the bottom composer visually integrated with the dark workspace */
[data-testid="stBottom"],
[data-testid="stBottom"] > div {
    background: transparent !important;
    border-top: none !important;
}

[data-testid="stChatInput"] {
    background: #151622 !important;
    border: 1px solid rgba(151, 113, 255, 0.35) !important;
    border-radius: 16px !important;
    box-shadow: 0 0 24px rgba(115, 75, 255, 0.10) !important;
}

[data-testid="stChatInput"] textarea {
    background: transparent !important;
    color: #f1efff !important;
    caret-color: #a78bfa !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: #85849b !important;
}

[data-testid="stChatInput"] button {
    color: #a78bfa !important;
}
/* Strong dark composer override */

[data-testid="stBottom"] {
    background: transparent !important;
}

[data-testid="stBottom"] [data-testid="stChatInput"],
[data-testid="stBottom"] [data-testid="stChatInput"] > div,
[data-testid="stBottom"] [data-testid="stChatInput"] textarea {
    background: #171827 !important;
}

[data-testid="stBottom"] [data-testid="stChatInput"] textarea {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    caret-color: #B69AFF !important;
}

[data-testid="stBottom"] [data-testid="stChatInput"] textarea::placeholder {
    color: #AAA6BC !important;
    -webkit-text-fill-color: #AAA6BC !important;
}
</style>
""", unsafe_allow_html=True)


# ==========================================
# 2. CONVERSATION MANAGEMENT
# ==========================================

if "conversations" not in st.session_state:

    first_id = str(uuid.uuid4())

    st.session_state.conversations = {
        first_id: {
            "title": "New conversation",
            "messages": []
        }
    }

    st.session_state.active_conversation = first_id


def create_new_chat():

    chat_id = str(uuid.uuid4())

    st.session_state.conversations[chat_id] = {
        "title": "New conversation",
        "messages": []
    }

    st.session_state.active_conversation = chat_id


current_id = st.session_state.active_conversation

current_chat = st.session_state.conversations[current_id]

messages = current_chat["messages"]


# ==========================================
# 3. SIDEBAR
# ==========================================

with st.sidebar:

    st.markdown(
        '<div class="cine-logo">CINE<span>BOT</span></div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="cine-tagline">'
        'AI FILMMAKING WORKSPACE'
        '</div>',
        unsafe_allow_html=True
    )

    st.write("")

    if st.button(
        "+  New conversation",
        use_container_width=True
    ):

        create_new_chat()
        st.rerun()

    st.divider()

    st.markdown("##### RECENT CONVERSATIONS")

    for chat_id, chat in reversed(
        list(st.session_state.conversations.items())
    ):

        if st.button(
            chat["title"],
            key="history_" + chat_id,
            use_container_width=True
        ):

            st.session_state.active_conversation = chat_id
            st.rerun()

    st.divider()

    st.markdown("##### MODEL")

    st.markdown("**Qwen 2.5 · 1.5B**")

    st.caption("Local language model")

    st.markdown("##### CONNECTION")

    try:

        connection = requests.get(
            "http://localhost:11434/api/tags",
            timeout=2
        )

        if connection.status_code == 200:

            installed_models = [
                model["name"]
                for model in connection.json().get("models", [])
            ]

            if MODEL in installed_models:
                st.success("Ollama connected")
                st.success("Model available")
            else:
                st.warning("Configured model not found")

        else:
            st.error("Ollama unavailable")

    except requests.exceptions.RequestException:
        st.error("Ollama offline")

    if TAVILY_API_KEY:
        st.success("Internet research ready")
    else:
        st.warning("Tavily API key not found in .env")

    st.divider()

    if st.button(
        "Clear current conversation",
        use_container_width=True
    ):

        current_chat["messages"] = []
        current_chat["title"] = "New conversation"
        st.rerun()

    st.caption("CINEBOT AI · LOCAL EDITION")


# ==========================================
# 4. MAIN WORKSPACE
# ==========================================

header_left, header_right = st.columns([4, 1])

with header_left:

    st.markdown(
        '<div class="cine-tagline">'
        'YOUR PERSONAL FILMMAKING ASSISTANT'
        '</div>',
        unsafe_allow_html=True
    )

with header_right:

    st.markdown(
        '<div style="text-align:right;color:#A99AE2;'
        'font-size:11px;">LOCAL AI</div>',
        unsafe_allow_html=True
    )

st.divider()


# ==========================================
# WORKSPACE STATE AND DOCUMENT READING
# ==========================================

WORKSPACES = {
    "Screenwriting": {
        "description": "Develop, analyse and rewrite stories and screenplays.",
        "tasks": [
            "Analyse my screenplay",
            "Improve dialogue",
            "Rewrite a scene",
            "Develop characters",
            "Check story structure",
            "Find plot holes",
            "Improve screenplay formatting",
            "Develop a story idea into a screenplay",
            "Other / custom request",
        ],
        "file_help": "Upload a screenplay or writing document (TXT, MD, DOCX, or PDF).",
        "system": """SCREENWRITING WORKSPACE:
Act as a careful screenwriting collaborator. Analyse premise, theme, logline,
structure, character goals and arcs, conflict, scenes, beats, dialogue, subtext,
pacing and screenplay format as relevant to the user's task. Be specific and
refer to the supplied pages/scenes when possible. Do not invent missing pages
or claim a problem exists without evidence. Preserve the writer's premise,
voice, tone and intended meaning. Do not rewrite more than requested. When
suggesting changes, explain why and distinguish diagnosis from optional ideas.
Use standard screenplay formatting when asked.""",
    },
    "Cinematography": {
        "description": "Plan visual language, camera, lenses, lighting and exposure.",
        "tasks": [
            "Analyse a shot description",
            "Plan camera framing and composition",
            "Choose camera movement",
            "Recommend lens and focal length",
            "Plan lighting",
            "Explain exposure settings",
            "Create a shot list",
            "Develop a visual look",
            "Other / custom request",
        ],
        "file_help": "Upload supporting notes or shot documents (TXT, MD, DOCX, or PDF).",
        "system": """CINEMATOGRAPHY WORKSPACE:
Act as a technically precise cinematography assistant. Help with shot size,
camera position, lens and focal length, perspective, composition, movement,
lighting, exposure, frame rate, shutter angle, colour and visual continuity.
Separate creative choices from technical facts. State assumptions such as
sensor format, frame rate, available light and intended look. Show calculations
when useful and check units. Do not claim to have visually inspected an image:
the configured Qwen 2.5 1.5B model is text-only. Analyse written shot descriptions
and reference notes supplied by the user.""",
    },
    "Film Direction": {
        "description": "Shape performances, blocking, staging and visual storytelling.",
        "tasks": [
            "Break down a scene for direction",
            "Plan actor blocking",
            "Direct an emotional performance",
            "Plan visual storytelling",
            "Create a shot-by-shot approach",
            "Analyse subtext and character objectives",
            "Prepare rehearsal notes",
            "Other / custom request",
        ],
        "file_help": "Upload a scene, director's notes or reference document (TXT, MD, DOCX, or PDF).",
        "system": """FILM DIRECTION WORKSPACE:
Act as a practical film-directing collaborator. Help translate the scene's
dramatic intention into actor objectives, beats, blocking, staging, camera
coverage and visual storytelling. Discuss what each character wants, what
changes during the scene, and how performance and staging communicate meaning.
Offer alternatives without presenting one directing style as mandatory.
Preserve the writer's intent and distinguish textual evidence from interpretation.""",
    },
    "Film Production": {
        "description": "Break down scripts and plan the practical filmmaking process.",
        "tasks": [
            "Break down a screenplay",
            "Create a shooting schedule",
            "Prepare a production plan",
            "Create a budget outline",
            "Prepare a call sheet draft",
            "List cast, props, costumes and locations",
            "Plan post-production",
            "Other / custom request",
        ],
        "file_help": "Upload a screenplay or production document (TXT, MD, DOCX, or PDF).",
        "system": """FILM PRODUCTION WORKSPACE:
Act as a practical production coordinator. Help with script breakdowns, scenes,
cast, extras, locations, props, costumes, set dressing, equipment, schedules,
call-sheet drafts, budget categories, crew needs, logistics, risks and
post-production workflows. Clearly label estimates and assumptions. Do not
invent confirmed availability, prices, crew commitments or schedule details.
Use structured tables or checklists when useful, and flag missing information
needed to make a production plan reliable.""",
    },
}

if "active_workspace" not in st.session_state:
    st.session_state.active_workspace = None

def extract_uploaded_text(uploaded_file):
    """Extract text from supported document formats without altering the source."""
    name = uploaded_file.name.lower()
    raw = uploaded_file.getvalue()

    if name.endswith((".txt", ".md")):
        return raw.decode("utf-8", errors="replace")

    if name.endswith(".docx"):
        try:
            with zipfile.ZipFile(__import__("io").BytesIO(raw)) as archive:
                document_xml = archive.read("word/document.xml")
            root = ET.fromstring(document_xml)
            ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
            paragraphs = []
            for paragraph in root.findall(".//w:p", ns):
                text = "".join(node.text or "" for node in paragraph.findall(".//w:t", ns))
                if text.strip():
                    paragraphs.append(text)
            return "\n".join(paragraphs)
        except Exception as error:
            raise ValueError(f"Could not read this DOCX file: {error}")

    if name.endswith(".pdf"):
        try:
            from pypdf import PdfReader
            reader = PdfReader(__import__("io").BytesIO(raw))
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        except ImportError:
            raise ValueError("PDF reading needs the pypdf package. In the VS Code terminal run: python -m pip install pypdf")
        except Exception as error:
            raise ValueError(f"Could not extract text from this PDF: {error}")

    raise ValueError("Supported formats are TXT, MD, DOCX and PDF.")

# ==========================================
# 5. HOME SCREEN AND FOUR WORKSPACES
# ==========================================

quick_prompt = None
workspace_system_prompt = ""
workspace_user_input = None

if st.session_state.active_workspace is None and not messages:
    st.html("""
    <div class="hero">
        <div class="hero-label">WELCOME TO CINEBOT</div>
        <div class="hero-title">Where ideas become<br><span>cinematic stories.</span></div>
        <div class="hero-description">
            Your personal filmmaking assistant. Choose a dedicated workspace
            for screenwriting, cinematography, film direction or film production.
        </div>
    </div>
    """)
    st.markdown(
        '<div class="section-heading">Explore your creative workspace</div>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2, gap="large")
    cards = [
        ("Screenwriting", "Develop stories, characters and dialogue.",
         "https://images.unsplash.com/photo-1455390582262-044cdead277a?w=1000&auto=format&fit=crop&q=85"),
        ("Cinematography", "Explore cameras, lenses, lighting and composition.",
         "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=1000&auto=format&fit=crop&q=85"),
        ("Film Direction", "Understand blocking and visual storytelling.",
         "https://images.unsplash.com/photo-1478720568477-152d9b164e26?w=1000&auto=format&fit=crop&q=85"),
        ("Film Production", "Plan shoots, breakdowns and production workflows.",
         "https://images.unsplash.com/photo-1492619375914-88005aa9e8fb?w=1000&auto=format&fit=crop&q=85"),
    ]
    for index, (name, description, image_url) in enumerate(cards):
        column = col1 if index % 2 == 0 else col2
        with column:
            st.image(image_url, use_container_width=True)
            st.markdown(f'<div class="card-title">{name}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="card-description">{description}</div>', unsafe_allow_html=True)
            if st.button(f"Open {name}", key=f"open_{name}", use_container_width=True):
                st.session_state.active_workspace = name
                st.rerun()

elif st.session_state.active_workspace is not None:
    workspace_name = st.session_state.active_workspace
    workspace = WORKSPACES[workspace_name]

    top_left, top_right = st.columns([4, 1])
    with top_left:
        st.markdown(f"## {workspace_name} Studio")
        st.caption(workspace["description"])
    with top_right:
        if st.button("← All workspaces", use_container_width=True):
            st.session_state.active_workspace = None
            st.rerun()

    st.info("Use this workspace to provide your material and instructions. CineBot will work on the specific task you choose.")

    with st.form(f"workspace_form_{workspace_name}", clear_on_submit=False):
        task = st.selectbox("What would you like CineBot to do?", workspace["tasks"])
        uploaded_file = st.file_uploader(
            workspace["file_help"],
            type=["txt", "md", "docx", "pdf"],
            key=f"upload_{workspace_name}"
        )
        supplied_text = st.text_area(
            "Paste your screenplay, scene, shot description or production notes",
            height=220,
            placeholder="Paste your material here... You can upload a document above instead."
        )
        extra_instructions = st.text_area(
            "Additional instructions (optional)",
            height=100,
            placeholder="Tell CineBot what to focus on, what to preserve, and what you want changed..."
        )
        submitted = st.form_submit_button("✦ Work with CineBot", use_container_width=True)

    if submitted:
        document_text = ""
        if uploaded_file is not None:
            try:
                document_text = extract_uploaded_text(uploaded_file)
            except ValueError as error:
                st.error(str(error))
        if uploaded_file is None or document_text or supplied_text.strip():
            material = supplied_text.strip()
            if document_text:
                material = (material + "\n\n" if material else "") + (
                    f"UPLOADED DOCUMENT: {uploaded_file.name}\n\n{document_text[:40000]}"
                )
            if not material:
                st.warning("Please upload a document or paste some material before submitting.")
            else:
                workspace_user_input = (
                    f"WORKSPACE: {workspace_name}\n"
                    f"TASK: {task}\n"
                    f"ADDITIONAL INSTRUCTIONS: {extra_instructions.strip() or 'None provided'}\n\n"
                    f"USER MATERIAL:\n{material}"
                )
                workspace_system_prompt = workspace["system"]
                st.session_state.pending_workspace_prompt = workspace_user_input
                st.session_state.pending_workspace_system = workspace_system_prompt
                st.rerun()

elif messages:
    st.markdown("### Conversation")
    if st.session_state.active_workspace:
        st.caption(f"Workspace: {st.session_state.active_workspace}")

# ==========================================
# 6. DISPLAY CHAT HISTORY
# ==========================================

for message in messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])


# ==========================================
# 7. CHAT INPUT
# ==========================================

typed_input = None
if st.session_state.active_workspace is None:
    typed_input = st.chat_input("Message CineBot...")

user_input = typed_input or st.session_state.pop("pending_workspace_prompt", None)
if user_input:
    workspace_system_prompt = st.session_state.pop("pending_workspace_system", "")


# ==========================================
# 8. INTERNET RESEARCH + OLLAMA AI RESPONSE
# ==========================================

if user_input:

    messages.append({
        "role": "user",
        "content": user_input
    })

    if len(messages) == 1:
        current_chat["title"] = user_input[:35]

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Researching the web and preparing your answer..."):

            research_results = []
            research_context = ""

            # Search the internet with Tavily before asking the local model.
            if TAVILY_API_KEY:
                try:
                    tavily = TavilyClient(api_key=TAVILY_API_KEY)
                    search_response = tavily.search(
                        query=user_input,
                        search_depth="advanced",
                        max_results=5
                    )

                    research_results = search_response.get("results", [])

                    if research_results:
                        research_context = (
                            "INTERNET RESEARCH RESULTS FROM TAVILY. "
                            "Use these sources when relevant. "
                            "Do not claim that a source says something unless "
                            "its provided content supports that claim. "
                            "Cite researched claims in the answer using [1], [2], etc. "
                            "If the sources disagree or are insufficient, say so. "
                            "Do not invent facts, quotes, titles, or URLs.\n\n"
                        )

                        for index, item in enumerate(research_results, start=1):
                            title = item.get("title", "Untitled source")
                            url = item.get("url", "")
                            content = item.get("content", "")
                            research_context += (
                                f"[{index}] {title}\n"
                                f"URL: {url}\n"
                                f"Relevant content: {content[:1200]}\n\n"
                            )
                    else:
                        research_context = (
                            "Tavily returned no relevant search results. "
                            "Answer using your existing knowledge, and clearly "
                            "state when current verification is unavailable."
                        )

                except Exception as error:
                    research_context = (
                        "Internet research could not be completed during this "
                        f"request ({type(error).__name__}). Answer using your "
                        "existing knowledge, and do not pretend that web research "
                        "was performed."
                    )
            else:
                research_context = (
                    "Tavily is not configured because TAVILY_API_KEY was not found "
                    "in the .env file. Answer using your existing knowledge and "
                    "do not claim to have searched the internet."
                )

            ollama_messages = [
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
            ]
            if workspace_system_prompt:
                ollama_messages.append({
                    "role": "system",
                    "content": workspace_system_prompt
                })
            ollama_messages.append({
                "role": "system",
                "content": research_context
            })
            ollama_messages += messages

            try:
                response = requests.post(
    OLLAMA_URL,
    json={
        "model": MODEL,
        "messages": ollama_messages,
        "stream": False
    },
    headers=OLLAMA_HEADERS,
    timeout=240
)
                    },
                    timeout=180
                )

                response.raise_for_status()
                answer = response.json()["message"]["content"]

            except requests.exceptions.RequestException as error:
                answer = (
                    "CineBot could not connect to Ollama.\n\n"
                    "Please check whether Ollama is running.\n\n"
                    f"Technical details: {error}"
                )

            # Add verifiable source links to the answer and conversation history.
            if research_results:
                answer += "\n\n### Internet sources\n"
                for index, item in enumerate(research_results, start=1):
                    title = item.get("title", "Source")
                    url = item.get("url", "")
                    if url:
                        answer += f"{index}. [{title}]({url})\n"

            st.markdown(answer)

    messages.append({
        "role": "assistant",
        "content": answer
    })

    st.rerun()
