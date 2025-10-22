import streamlit as st


CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&display=swap');
    
    /* Palette: requested solid colors (no gradients) */
    :root{
        --p1: #DBFE87; /* light lime */
        --p2: #FBDE6F; /* main yellow */
        --p3: #CEC288; /* ecru */
        --p4: #6F8695; /* slate gray */
        --p5: #1C448E; /* deep blue */
        --ink: #0F1724; /* dark text */
        --bg: #FFFFFF; /* page background */
        --card: #FFFFFF; /* card background */
    }

    .main { 
        background: var(--bg);
        font-family: 'Space Grotesk', sans-serif;
        color: var(--ink);
        padding: 24px;
    }
    
    h1 { 
        color: var(--p5);
        font-weight: 700;
        font-size: 2.4rem !important;
        margin: 0 0 8px 0;
    }

    /* Inputs */
    .stTextInput > div > div > input {
        border-radius: 12px;
        border: none;
        background: var(--card);
        color: var(--ink);
        padding: 14px 18px;
        transition: box-shadow 0.25s ease, transform 0.15s ease;
        box-shadow: 0 6px 18px rgba(11,22,36,0.06);
    }

    .stTextInput > div > div > input:focus {
        box-shadow: 0 8px 30px rgba(251,222,111,0.22);
        transform: translateY(-2px);
        outline: none;
    }

    /* Buttons */
    .stButton > button {
        background: var(--p5); /* deep blue */
        color: white;
        border-radius: 10px;
        padding: 10px 20px;
        font-weight: 700;
        letter-spacing: 0.02em;
        box-shadow: 0 6px 18px rgba(28,68,142,0.12);
        transition: transform 0.14s ease, box-shadow 0.14s ease;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 24px rgba(28,68,142,0.16);
    }

    /* Smooth loading animation */
    .loading-wrapper {
        display:flex;align-items:center;justify-content:center;
        padding:26px;border-radius:14px;background:var(--card);
        box-shadow: 0 10px 30px rgba(11,22,36,0.06);
    }

    .loader-dots{display:flex;gap:8px;align-items:flex-end}
    .loader-dots > div{width:12px;height:12px;border-radius:999px;opacity:0.95;transform:translateY(0);}

    .loader-dots > div:nth-child(1){background:var(--p1);animation: up 0.7s infinite ease-in-out 0s}
    .loader-dots > div:nth-child(2){background:var(--p2);animation: up 0.7s infinite ease-in-out 0.12s}
    .loader-dots > div:nth-child(3){background:var(--p5);animation: up 0.7s infinite ease-in-out 0.24s}

    @keyframes up{0%{transform:translateY(0);opacity:.8}50%{transform:translateY(-14px);opacity:1}100%{transform:translateY(0);opacity:.8}}

    .loading-text{font-weight:700;color:var(--ink);margin-left:14px}

    /* Progress bar */
    .stProgress > div > div > div{background:var(--p2);border-radius:8px}

    /* Cards */
    [data-testid="stDataFrame"]{background:var(--card) !important;border-radius:12px;box-shadow:0 8px 30px rgba(11,22,36,0.06)}

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: var(--p2) !important;
        color: var(--ink) !important;
        box-shadow: none;
    }
    [data-testid="stSidebar"] .css-1d391kg, [data-testid="stSidebar"] .css-1lcbmhc { color: var(--ink) !important; }
    [data-testid="stSidebar"] img { border-radius: 8px; }

    /* small helpers */
    .muted{color:rgba(15,23,36,0.6)}

</style>
"""


def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)


def loading_html(icon: str, text: str) -> str:
    # returns a small dot-loader + text block
    return f"""
    <div class="loading-wrapper">
        <div style="display:flex;align-items:center">
            <div class="loader-dots" aria-hidden="true">
                <div style="background:var(--p1)"></div>
                <div style="background:var(--p2)"></div>
                <div style="background:var(--p5)"></div>
            </div>
            <div class="loading-text">{text}</div>
        </div>
    </div>
    """
