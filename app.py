from __future__ import annotations

import asyncio
import html
import json
import os

import streamlit as st
import streamlit.components.v1 as components

from proofloop.evaluator import parse_review_response, validate_inputs
from proofloop.llm_client import api_configuration, generate_review
from proofloop.mascot import render_global_robot
from proofloop.prompts import build_evaluation_prompt

st.set_page_config(
    page_title="ProofLoop — Annotation Guideline Checker",
    page_icon="🪐",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.session_state.setdefault("pl_theme", "Dark")
# One-time visual migration: an existing Codespace session may still hold the
# old Light default. Start v6 in the intended cosmic Dark appearance once, while
# preserving any later user choice between Light and Dark.
if st.session_state.get("pl_visual_version") != 7:
    st.session_state["pl_theme"] = "Dark"
    st.session_state["pl_visual_version"] = 7
st.session_state.setdefault("pl_show_loop", True)
st.session_state.setdefault("proofloop_mascot_status", "idle")

THEMES = {
    "Light": {
        "bg": "#F6F7FC", "surface": "#FFFFFF", "card": "#FFFFFF", "control": "#FFFFFF",
        "border": "#E0E3F5", "border_strong": "#A6A0F2", "ink": "#1A2142", "muted": "#535D7D",
        "subtle": "#737F9F", "accent": "#6556D9", "accent_hover": "#5144BD", "accent_soft": "#EFEDFF",
        "accent_border": "#D1CCFF", "on_accent": "#FFFFFF", "shadow": "0 14px 36px rgba(42,44,101,.10)",
        "color_scheme": "light", "panel": "#FAF9FF", "field": "#FFFFFF", "badge": "#F3F1FF",
        "hero_background": "radial-gradient(ellipse at 84% 10%,rgba(180,164,255,.24),transparent 35%),radial-gradient(ellipse at 48% 112%,rgba(88,203,202,.17),transparent 46%),linear-gradient(126deg,#FBFCFF 0%,#EFF2FF 52%,#F9F0FF 100%)",
        "hero_border": "rgba(133,126,207,.30)", "hero_shadow": "0 18px 45px rgba(72,75,139,.12),inset 0 1px 0 rgba(255,255,255,.88)",
        "hero_ink": "#222447", "hero_copy": "#535E7E", "hero_eyebrow": "#5143C2", "hero_shimmer": "rgba(255,255,255,.48)",
        "chip_bg": "rgba(112,95,220,.09)", "chip_border": "rgba(111,98,206,.24)", "chip_ink": "#38385F",
        "board_background": "radial-gradient(ellipse at 49% 86%,rgba(91,191,210,.20),transparent 42%),linear-gradient(145deg,#FFFFFF 0%,#F0F3FF 52%,#F8F0FF 100%)",
        "board_border": "rgba(139,129,211,.34)", "board_shadow": "inset 0 1px 0 rgba(255,255,255,.92),0 10px 28px rgba(72,79,138,.14),0 0 32px rgba(146,130,255,.10)",
        "scene_nebula": "radial-gradient(ellipse at 24% 28%,rgba(98,202,210,.25),transparent 38%),radial-gradient(ellipse at 78% 75%,rgba(143,126,255,.20),transparent 44%),linear-gradient(135deg,#F7FCFF,#EAF0FF 61%,#F5ECFF)",
        "scene_planet": "radial-gradient(ellipse at 70% 38%,rgba(111,132,255,.18),transparent 42%),linear-gradient(135deg,#F5FAFF,#E8F1FF 52%,#F2E9FF)",
        "scene_aurora": "radial-gradient(ellipse at 30% 15%,rgba(79,221,185,.18),transparent 38%),radial-gradient(ellipse at 78% 78%,rgba(171,126,255,.20),transparent 43%),linear-gradient(135deg,#F3FCFF,#EAF7FA 52%,#F2ECFF)",
        "star_dot_a": "rgba(105,119,201,.62)", "star_dot_b": "rgba(78,159,176,.60)", "orbit_color": "rgba(109,126,219,.50)",
        "scene_label_bg": "rgba(255,255,255,.76)", "scene_label_border": "rgba(125,121,196,.24)", "scene_label_ink": "#3D4269", "mascot_caption": "#56627F",
        "code_bg": "#ECEAFF", "code_ink": "#4B3BB0", "code_border": "#D4CEFF",
    },
    "Dark": {
        "bg": "#090E1B", "surface": "#11182B", "card": "#151E35", "control": "#0D1426",
        "border": "#293452", "border_strong": "#7776E8", "ink": "#F0F3FF", "muted": "#B7C1E0",
        "subtle": "#8F9BC2", "accent": "#79EDE3", "accent_hover": "#A0F7F0", "accent_soft": "#1C2D4B",
        "accent_border": "#38527F", "on_accent": "#071121", "shadow": "0 18px 42px rgba(0,0,0,.28)",
        "color_scheme": "dark", "panel": "#0E1629", "field": "#0B1325", "badge": "#182344",
        "hero_background": "radial-gradient(ellipse at 83% 14%,rgba(129,111,255,.23),transparent 34%),radial-gradient(ellipse at 52% 110%,rgba(64,224,215,.15),transparent 44%),linear-gradient(126deg,#090F25 0%,#11183A 52%,#19183E 100%)",
        "hero_border": "rgba(155,173,255,.25)", "hero_shadow": "0 18px 50px rgba(26,29,75,.22),inset 0 1px 0 rgba(227,235,255,.08)",
        "hero_ink": "#F5F6FF", "hero_copy": "#CAD3F0", "hero_eyebrow": "#8BF4E8", "hero_shimmer": "rgba(255,255,255,.12)",
        "chip_bg": "rgba(132,151,255,.11)", "chip_border": "rgba(164,180,255,.24)", "chip_ink": "#E4E9FF",
        "board_background": "radial-gradient(ellipse at 49% 86%,rgba(104,221,225,.13),transparent 38%),linear-gradient(145deg,#080D22 0%,#111637 55%,#17163D 100%)",
        "board_border": "rgba(160,177,255,.28)", "board_shadow": "inset 0 1px 0 rgba(255,255,255,.11),0 10px 28px rgba(2,5,22,.25),0 0 35px rgba(98,100,255,.08)",
        "scene_nebula": "radial-gradient(ellipse at 24% 28%,rgba(93,237,227,.26),transparent 38%),radial-gradient(ellipse at 78% 75%,rgba(143,126,255,.30),transparent 44%),linear-gradient(135deg,#081326,#131A42 61%,#17183B)",
        "scene_planet": "radial-gradient(ellipse at 70% 38%,rgba(111,132,255,.20),transparent 42%),linear-gradient(135deg,#09152B,#13244C 52%,#241B49)",
        "scene_aurora": "radial-gradient(ellipse at 30% 15%,rgba(79,221,185,.22),transparent 38%),radial-gradient(ellipse at 78% 78%,rgba(171,126,255,.26),transparent 43%),linear-gradient(135deg,#071322,#102844 52%,#201942)",
        "star_dot_a": "rgba(106,190,191,.72)", "star_dot_b": "rgba(255,255,255,.8)", "orbit_color": "rgba(126,238,230,.45)",
        "scene_label_bg": "rgba(8,14,36,.38)", "scene_label_border": "rgba(174,184,255,.18)", "scene_label_ink": "#D3DBFF", "mascot_caption": "#D7E8FF",
        "code_bg": "#1B2542", "code_ink": "#9FF5EC", "code_border": "#39466A",
    },
}
palette = THEMES[st.session_state["pl_theme"]]

# The native Streamlit toolbar is deliberately hidden: settings live in ProofLoop's
# own sidebar, not behind the framework's three-dot developer menu.
st.markdown(
    f"""
    <style>
      :root {{
        color-scheme: {palette['color_scheme']};
        --pl-bg:{palette['bg']}; --pl-surface:{palette['surface']}; --pl-card:{palette['card']};
        --pl-control:{palette['control']}; --pl-border:{palette['border']}; --pl-border-strong:{palette['border_strong']};
        --pl-ink:{palette['ink']}; --pl-muted:{palette['muted']}; --pl-subtle:{palette['subtle']};
        --pl-accent:{palette['accent']}; --pl-accent-hover:{palette['accent_hover']}; --pl-accent-soft:{palette['accent_soft']};
        --pl-accent-border:{palette['accent_border']}; --pl-on-accent:{palette['on_accent']}; --pl-shadow:{palette['shadow']};
        --pl-panel:{palette['panel']}; --pl-field:{palette['field']}; --pl-badge:{palette['badge']};
        --pl-hero-background:{palette['hero_background']}; --pl-hero-border:{palette['hero_border']}; --pl-hero-shadow:{palette['hero_shadow']};
        --pl-hero-ink:{palette['hero_ink']}; --pl-hero-copy:{palette['hero_copy']}; --pl-hero-eyebrow:{palette['hero_eyebrow']}; --pl-hero-shimmer:{palette['hero_shimmer']};
        --pl-chip-bg:{palette['chip_bg']}; --pl-chip-border:{palette['chip_border']}; --pl-chip-ink:{palette['chip_ink']};
        --pl-board-background:{palette['board_background']}; --pl-board-border:{palette['board_border']}; --pl-board-shadow:{palette['board_shadow']};
        --pl-scene-nebula:{palette['scene_nebula']}; --pl-scene-planet:{palette['scene_planet']}; --pl-scene-aurora:{palette['scene_aurora']};
        --pl-star-dot-a:{palette['star_dot_a']}; --pl-star-dot-b:{palette['star_dot_b']}; --pl-orbit-color:{palette['orbit_color']};
        --pl-scene-label-bg:{palette['scene_label_bg']}; --pl-scene-label-border:{palette['scene_label_border']}; --pl-scene-label-ink:{palette['scene_label_ink']}; --pl-mascot-caption:{palette['mascot_caption']};
        --pl-code-bg:{palette['code_bg']}; --pl-code-ink:{palette['code_ink']}; --pl-code-border:{palette['code_border']};
      }}
      [data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stStatusWidget"],
      #MainMenu, .stDeployButton, footer {{ display:none !important; visibility:hidden !important; height:0 !important; }}
      .stApp {{ background:var(--pl-bg) !important; color:var(--pl-ink) !important; font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif !important; }}
      .pl-brand, .pl-brand *, .pl-hero, .pl-hero *, .pl-step-card, .pl-step-card * {{ font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif !important; }}
      .block-container {{ max-width:1180px; padding:2rem clamp(.8rem,3vw,2rem) 3.2rem !important; }}
      section[data-testid="stSidebar"] {{ background:var(--pl-surface) !important; border-right:1px solid var(--pl-border); }}
      section[data-testid="stSidebar"] > div {{ padding-top:1rem; }}
      .stApp label, .stApp [data-testid="stWidgetLabel"] p,
      .stApp [data-testid="stRadio"] label p, .stApp [data-testid="stCheckbox"] label p {{ color:var(--pl-ink) !important; }}
      .stApp [data-testid="stCaptionContainer"] p {{ color:var(--pl-muted) !important; }}
      .stApp .pl-step-copy, .stApp .pl-muted,
      .stApp .pl-mascot-caption, .stApp .pl-sidebar-note {{ color:var(--pl-muted) !important; }}
      .pl-brand {{ display:flex; align-items:center; gap:.7rem; margin:0 0 1.15rem; }}
      .pl-logo {{ width:2.55rem; height:2.55rem; display:grid; place-items:center; flex:0 0 auto; border-radius:15px; background:linear-gradient(145deg,#18294D 0%,#24224F 52%,#173A50 100%); box-shadow:0 0 0 1px rgba(164,179,255,.38) inset,0 6px 18px rgba(74,78,180,.22); }}
      .pl-logo svg {{ width:2.2rem; height:2.2rem; display:block; filter:drop-shadow(0 0 5px rgba(111,232,235,.32)); }}
      .pl-brand-name {{ color:var(--pl-ink) !important; font-size:1.2rem; line-height:1.05; font-weight:850; letter-spacing:-.04em; }}
      .pl-brand-tag {{ color:var(--pl-muted) !important; font-size:.69rem; margin-top:.22rem; letter-spacing:.085em; text-transform:uppercase; }}
      .pl-hero {{ position:relative; isolation:isolate; display:grid; grid-template-columns:minmax(0,1.35fr) minmax(230px,.78fr); align-items:center; gap:clamp(1rem,2.6vw,1.8rem); overflow:hidden; border:1px solid var(--pl-hero-border); border-radius:26px; padding:clamp(1.2rem,3vw,2.05rem); background:var(--pl-hero-background); box-shadow:var(--pl-hero-shadow); margin-bottom:1.05rem; transition:background .35s ease,border-color .35s ease,box-shadow .35s ease; }}
      .pl-hero:before {{ content:""; position:absolute; z-index:-1; inset:0; pointer-events:none; opacity:.56; background-image:radial-gradient(circle,rgba(191,212,255,.85) .7px,transparent 1.4px),radial-gradient(circle,rgba(110,245,231,.7) .6px,transparent 1.3px); background-size:37px 37px,61px 61px; background-position:4px 7px,18px 21px; mask-image:linear-gradient(90deg,transparent 0%,#000 48%,#000 100%); }}
      .pl-hero:after {{ content:""; pointer-events:none; position:absolute; z-index:-1; inset:-1px; border-radius:inherit; background:linear-gradient(110deg,transparent 18%,var(--pl-hero-shimmer) 40%,transparent 58%); transform:translateX(-100%); animation:pl-shimmer 8s ease-in-out infinite; }}
      .pl-eyebrow {{ color:var(--pl-hero-eyebrow) !important; font-size:.69rem; font-weight:850; letter-spacing:.16em; text-transform:uppercase; margin-bottom:.72rem; }}
      .pl-hero h1 {{ color:var(--pl-hero-ink) !important; font-size:clamp(1.9rem,4.2vw,3.05rem); line-height:1.04; font-weight:850; letter-spacing:-.06em; margin:0; max-width:780px; text-shadow:0 2px 24px rgba(127,132,255,.11); }}
      .pl-hero-copy {{ color:var(--pl-hero-copy) !important; font-size:clamp(.96rem,1.6vw,1.06rem); line-height:1.65; margin:.85rem 0 1rem; max-width:730px; }}
      .pl-chips {{ display:flex; flex-wrap:wrap; gap:.45rem; }}
      .pl-chip {{ background:var(--pl-chip-bg); border:1px solid var(--pl-chip-border); border-radius:999px; padding:.38rem .64rem; color:var(--pl-chip-ink) !important; font-size:.72rem; font-weight:650; box-shadow:inset 0 1px 0 rgba(255,255,255,.035); transition:transform .2s ease,border-color .2s ease,background .2s ease; }}
      .pl-chip:hover {{ transform:translateY(-2px); border-color:rgba(128,242,231,.58); background:rgba(104,217,222,.13); }}
      .pl-hero-art {{ min-width:0; position:relative; }}
      .hero-mascot-slot {{ height:212px; width:100%; position:relative; isolation:isolate; overflow:hidden; border:1px solid var(--pl-board-border); border-radius:21px; background:var(--pl-board-background); box-shadow:var(--pl-board-shadow); transition:background .35s ease,border-color .35s ease,box-shadow .35s ease; }}
      .pl-space-scene {{ position:absolute; inset:0; opacity:0; pointer-events:none; animation:pl-scene-fade-a 27s linear infinite; }}
      .pl-space-scene.scene-nebula {{ opacity:1; background:var(--pl-scene-nebula); animation-delay:0s; }}
      .pl-space-scene.scene-planet {{ background:var(--pl-scene-planet); animation-delay:9s; }}
      .pl-space-scene.scene-aurora {{ background:var(--pl-scene-aurora); animation-delay:18s; }}
      .pl-space-scene.scene-nebula {{ animation-name:pl-scene-fade-a; }}
      .pl-space-scene.scene-planet {{ animation-name:pl-scene-fade-b; }}
      .pl-space-scene.scene-aurora {{ animation-name:pl-scene-fade-c; }}
      .pl-space-scene::before {{ content:""; position:absolute; inset:0; opacity:.62; background-image:radial-gradient(var(--pl-star-dot-a) .8px,transparent 1px),radial-gradient(var(--pl-star-dot-b) .7px,transparent 1px); background-size:23px 23px,37px 37px; background-position:0 0,11px 16px; animation:pl-starfield-drift 22s linear infinite; }}
      .pl-space-scene.scene-nebula::after {{ content:""; position:absolute; width:90px; height:54px; left:7%; top:17%; border:1px solid var(--pl-orbit-color); border-radius:50%; transform:rotate(-25deg); box-shadow:0 0 28px rgba(80,207,207,.11),inset 0 0 24px rgba(99,170,255,.08); animation:pl-nebula-breathe 8s ease-in-out infinite; }}
      .pl-space-scene.scene-planet::after {{ content:""; position:absolute; width:58px; height:58px; right:12%; top:20%; border-radius:50%; background:radial-gradient(circle at 32% 26%,#F9F0FF 0 3%,#BFB7FF 12%,#7A76CF 52%,#4A548F 78%,#23365F 100%); border:1px solid rgba(221,222,255,.55); box-shadow:0 0 30px rgba(135,140,255,.32),inset -10px -8px 15px rgba(10,18,44,.42); animation:pl-planet-drift 9s ease-in-out infinite; }}
      .pl-space-scene.scene-aurora::after {{ content:""; position:absolute; width:145%; height:62%; left:-22%; top:10%; border-radius:50%; background:linear-gradient(125deg,transparent 28%,rgba(69,235,191,.1) 39%,rgba(94,198,255,.23) 49%,rgba(174,125,255,.16) 58%,transparent 70%); filter:blur(8px); transform:rotate(-17deg); animation:pl-aurora-wave 7s ease-in-out infinite alternate; }}
      .hero-mascot-slot:before {{ content:""; position:absolute; z-index:1; width:108px; height:108px; border:1px dashed var(--pl-orbit-color); border-radius:50%; left:50%; top:46%; transform:translate(-50%,-50%); opacity:.55; animation:pl-orbit-spin 28s linear infinite; pointer-events:none; }}
      .hero-mascot-slot:after {{ content:""; position:absolute; z-index:4; inset:0; border-radius:inherit; pointer-events:none; opacity:.22; background-image:linear-gradient(110deg,transparent 18%,rgba(255,255,255,.28) 40%,transparent 58%); background-size:240% 100%; animation:pl-shimmer 9s ease-in-out infinite; }}
      .pl-orbit {{ position:absolute; z-index:1; left:50%; top:46%; width:132px; height:67px; transform:translate(-50%,-50%) rotate(-20deg); border:1px solid var(--pl-orbit-color); border-radius:50%; opacity:.7; pointer-events:none; }}
      .pl-star {{ position:absolute; z-index:2; color:var(--pl-hero-eyebrow); font-size:1.1rem; text-shadow:0 0 12px rgba(186,133,255,.7); animation:pl-twinkle 2.8s ease-in-out infinite; pointer-events:none; }}
      .pl-star.a {{ top:25px; left:24px; }} .pl-star.b {{ bottom:38px; right:25px; animation-delay:1.1s; }}
      .pl-platform {{ position:absolute; z-index:1; left:50%; bottom:34px; width:83px; height:10px; border-radius:50%; transform:translateX(-50%); background:linear-gradient(90deg,rgba(105,238,228,.12),rgba(137,130,255,.52),rgba(105,238,228,.12)); filter:blur(4px); box-shadow:0 0 18px rgba(119,149,255,.18); animation:pl-platform-pulse 3.2s ease-in-out infinite; pointer-events:none; }}
      .pl-scene-label {{ position:absolute; top:12px; right:13px; z-index:3; color:var(--pl-scene-label-ink) !important; font-size:.57rem; font-weight:800; letter-spacing:.10em; text-shadow:0 0 12px rgba(141,151,255,.20); text-transform:uppercase; background:var(--pl-scene-label-bg); border:1px solid var(--pl-scene-label-border); border-radius:999px; padding:.24rem .42rem; backdrop-filter:blur(8px); }}
      .pl-scene-label .scene-name {{ display:inline-block; opacity:0; }}
      .pl-mascot-caption {{ position:absolute; z-index:3; bottom:8px; left:0; right:0; color:var(--pl-mascot-caption) !important; text-align:center; font-size:.58rem; font-weight:850; letter-spacing:.13em; text-shadow:0 0 13px rgba(96,160,233,.22); pointer-events:none; }}
      @keyframes pl-scene-fade-a {{ 0%,29% {{ opacity:1; }} 33%,96% {{ opacity:0; }} 100% {{ opacity:1; }} }}
      @keyframes pl-scene-fade-b {{ 0%,29% {{ opacity:0; }} 33%,62% {{ opacity:1; }} 66%,100% {{ opacity:0; }} }}
      @keyframes pl-scene-fade-c {{ 0%,62% {{ opacity:0; }} 66%,96% {{ opacity:1; }} 100% {{ opacity:0; }} }}
      .pl-scene-label .scene-name {{ position:absolute; right:0; top:0; white-space:nowrap; opacity:0; animation:pl-scene-label 27s linear infinite; }}
      .pl-scene-label .scene-name:nth-child(1) {{ animation-delay:0s; }}
      .pl-scene-label .scene-name:nth-child(2) {{ animation-delay:9s; }}
      .pl-scene-label .scene-name:nth-child(3) {{ animation-delay:18s; }}
      @keyframes pl-scene-label {{ 0%,29% {{ opacity:1; }} 33%,96% {{ opacity:0; }} 100% {{ opacity:1; }} }}
      @keyframes pl-starfield-drift {{ from {{background-position:0 0,11px 16px}} to {{background-position:80px 55px,-37px 74px}} }}
      @keyframes pl-nebula-breathe {{ 0%,100% {{ transform:rotate(-25deg) scale(.96); opacity:.62 }} 50% {{ transform:rotate(-18deg) scale(1.08); opacity:1 }} }}
      @keyframes pl-planet-drift {{ 0%,100% {{ transform:translateY(0) rotate(-8deg) }} 50% {{ transform:translateY(-8px) rotate(5deg) }} }}
      @keyframes pl-aurora-wave {{ from {{ transform:translateX(-5%) rotate(-17deg); opacity:.55 }} to {{ transform:translateX(6%) rotate(-10deg); opacity:1 }} }}
      .pl-step-card {{ height:100%; min-height:112px; padding:1.05rem; border:1px solid var(--pl-border); border-radius:16px; background:var(--pl-surface); transition:transform .22s ease,border-color .22s ease,box-shadow .22s ease; }}
      .pl-step-card:hover {{ transform:translateY(-4px); border-color:var(--pl-border-strong); box-shadow:var(--pl-shadow),0 0 0 1px var(--pl-accent-border) inset; }}
      .pl-step-no {{ color:var(--pl-accent) !important; font-size:.68rem; font-weight:850; letter-spacing:.14em; text-transform:uppercase; }}
      .pl-step-title {{ color:var(--pl-ink) !important; font-weight:800; margin:.42rem 0 .28rem; }}
      .pl-step-copy {{ color:var(--pl-muted) !important; font-size:.81rem; line-height:1.55; }}
      .pl-section-title {{ color:var(--pl-ink) !important; font-size:1.27rem; font-weight:850; letter-spacing:-.03em; margin:1rem 0 .2rem; }}
      .pl-muted {{ color:var(--pl-muted) !important; font-size:.9rem; line-height:1.6; }}
      .pl-panel {{ padding:1rem 1.1rem; background:var(--pl-panel); border:1px solid var(--pl-border); border-radius:16px; margin:.8rem 0 1rem; }}
      .pl-panel-title {{ color:var(--pl-ink) !important; font-weight:800; font-size:.98rem; margin-bottom:.2rem; }}
      .pl-note {{ border:1px solid var(--pl-border); border-left:3px solid var(--pl-accent); border-radius:10px; background:var(--pl-panel); padding:.75rem .9rem; margin:.45rem 0 .8rem; color:var(--pl-muted) !important; font-size:.82rem; line-height:1.55; }}
      [data-testid="stTextArea"] label p, [data-testid="stTextInput"] label p, [data-testid="stWidgetLabel"] p {{ color:var(--pl-ink) !important; -webkit-text-fill-color:var(--pl-ink) !important; font-weight:750 !important; font-size:.91rem !important; }}
      [data-testid="stTextArea"] textarea, [data-testid="stTextInput"] input {{ background:var(--pl-field) !important; color:var(--pl-ink) !important; -webkit-text-fill-color:var(--pl-ink) !important; border:1px solid var(--pl-border) !important; border-radius:12px !important; font-size:.93rem !important; line-height:1.6 !important; padding:.85rem .9rem !important; }}
      [data-testid="stTextArea"] textarea::placeholder, [data-testid="stTextInput"] input::placeholder {{ color:var(--pl-subtle) !important; -webkit-text-fill-color:var(--pl-subtle) !important; opacity:1 !important; }}
      [data-testid="stTextArea"] textarea:focus, [data-testid="stTextInput"] input:focus {{ border-color:var(--pl-accent) !important; box-shadow:0 0 0 3px var(--pl-accent-soft) !important; }}
      [data-testid="stRadio"] > label p {{ color:var(--pl-ink) !important; -webkit-text-fill-color:var(--pl-ink) !important; font-weight:800 !important; }}
      [data-testid="stRadio"] [role="radiogroup"] {{ gap:.55rem !important; }}
      [data-testid="stRadio"] [role="radiogroup"] label {{ color:var(--pl-ink) !important; background:var(--pl-surface) !important; border:1px solid var(--pl-border) !important; border-radius:12px !important; padding:.65rem .85rem !important; transition:border-color .18s ease,background .18s ease,box-shadow .18s ease; }}
      [data-testid="stRadio"] [role="radiogroup"] label:hover {{ border-color:var(--pl-accent) !important; background:var(--pl-accent-soft) !important; }}
      [data-testid="stRadio"] [role="radiogroup"] label p, [data-testid="stRadio"] [role="radiogroup"] label span {{ color:var(--pl-ink) !important; -webkit-text-fill-color:var(--pl-ink) !important; }}
      /* Theme-safe result surfaces: Streamlit's default code blocks, expanders and secondary download buttons can otherwise stay dark in Light mode. */
      [data-testid="stCode"], .stCodeBlock, [data-testid="stCodeBlock"] {{ background:var(--pl-code-bg) !important; border:1px solid var(--pl-code-border) !important; border-radius:12px !important; color:var(--pl-code-ink) !important; }}
      [data-testid="stCode"] pre, [data-testid="stCode"] code, [data-testid="stCode"] span, .stCodeBlock pre, .stCodeBlock code, [data-testid="stCodeBlock"] pre, [data-testid="stCodeBlock"] code {{ background:transparent !important; color:var(--pl-code-ink) !important; -webkit-text-fill-color:var(--pl-code-ink) !important; white-space:pre-wrap !important; overflow-wrap:anywhere !important; }}
      /* Streamlit's built-in code-copy control was retaining its own dark button skin. Scope the fix to code blocks only. */
      [data-testid="stCode"] button,
      [data-testid="stCodeBlock"] button,
      [data-testid="stCodeCopyButton"],
      .stCodeBlock button {{
        background:var(--pl-code-bg) !important;
        background-color:var(--pl-code-bg) !important;
        color:var(--pl-code-ink) !important;
        -webkit-text-fill-color:var(--pl-code-ink) !important;
        border:1px solid var(--pl-code-border) !important;
        border-radius:9px !important;
        box-shadow:0 2px 8px color-mix(in srgb,var(--pl-accent) 10%,transparent) !important;
        opacity:1 !important;
        transition:background .18s ease,border-color .18s ease,box-shadow .18s ease,transform .18s ease !important;
      }}
      [data-testid="stCode"] button svg,
      [data-testid="stCodeBlock"] button svg,
      [data-testid="stCodeCopyButton"] svg,
      .stCodeBlock button svg {{ color:var(--pl-code-ink) !important; fill:var(--pl-code-ink) !important; stroke:var(--pl-code-ink) !important; }}
      [data-testid="stCode"] button:hover,
      [data-testid="stCodeBlock"] button:hover,
      [data-testid="stCodeCopyButton"]:hover,
      .stCodeBlock button:hover {{
        background:var(--pl-accent-soft) !important;
        background-color:var(--pl-accent-soft) !important;
        border-color:var(--pl-accent-border) !important;
        box-shadow:0 4px 14px color-mix(in srgb,var(--pl-accent) 20%,transparent) !important;
        transform:translateY(-1px);
      }}
      [data-testid="stCode"] button:focus-visible,
      [data-testid="stCodeBlock"] button:focus-visible,
      [data-testid="stCodeCopyButton"]:focus-visible,
      .stCodeBlock button:focus-visible {{ outline:2px solid var(--pl-accent) !important; outline-offset:2px !important; }}
      [data-testid="stCode"] button:active,
      [data-testid="stCodeBlock"] button:active,
      [data-testid="stCodeCopyButton"]:active,
      .stCodeBlock button:active {{ transform:scale(.96); }}
      [data-testid="stExpander"] {{ background:var(--pl-surface) !important; border:1px solid var(--pl-border) !important; border-radius:12px !important; overflow:hidden; }}
      [data-testid="stExpander"] details, [data-testid="stExpander"] summary, [data-testid="stExpander"] summary:hover {{ background:var(--pl-surface) !important; color:var(--pl-ink) !important; }}
      [data-testid="stExpander"] summary p, [data-testid="stExpander"] summary span, [data-testid="stExpander"] summary svg {{ color:var(--pl-ink) !important; -webkit-text-fill-color:var(--pl-ink) !important; fill:var(--pl-ink) !important; }}
      [data-testid="stExpander"] [data-testid="stMarkdownContainer"] p {{ color:var(--pl-ink) !important; -webkit-text-fill-color:var(--pl-ink) !important; }}
      .stDownloadButton > button {{ background:var(--pl-surface) !important; color:var(--pl-ink) !important; -webkit-text-fill-color:var(--pl-ink) !important; border:1px solid var(--pl-border) !important; }}
      .stDownloadButton > button p, .stDownloadButton > button span, .stDownloadButton > button svg {{ color:var(--pl-ink) !important; -webkit-text-fill-color:var(--pl-ink) !important; fill:var(--pl-ink) !important; }}
      .stDownloadButton > button:hover {{ background:var(--pl-accent-soft) !important; border-color:var(--pl-accent-border) !important; }}
      .stButton > button, .stDownloadButton > button {{ border-radius:11px !important; font-weight:800 !important; min-height:2.8rem; transition:transform .18s ease,box-shadow .18s ease,border-color .18s ease !important; }}
      .stButton > button:hover, .stDownloadButton > button:hover {{ transform:translateY(-1px); box-shadow:0 8px 20px rgba(8,127,112,.14) !important; }}
      .stButton > button[kind="primary"], [data-testid="stFormSubmitButton"] button {{ background:var(--pl-accent) !important; border:1px solid var(--pl-accent) !important; color:var(--pl-on-accent) !important; -webkit-text-fill-color:var(--pl-on-accent) !important; font-weight:800 !important; min-height:2.8rem; transition:transform .18s ease,box-shadow .18s ease,background .18s ease !important; }}
      .stButton > button[kind="primary"]:hover, [data-testid="stFormSubmitButton"] button:hover {{ background:var(--pl-accent-hover) !important; border-color:var(--pl-accent-hover) !important; transform:translateY(-2px); box-shadow:0 9px 24px color-mix(in srgb,var(--pl-accent) 25%,transparent) !important; }}
      [data-testid="stAlert"] {{ border-radius:13px !important; border:1px solid var(--pl-border) !important; background:var(--pl-panel) !important; }}
      [data-testid="stAlert"] p, [data-testid="stAlert"] span, [data-testid="stAlert"] li, [data-testid="stAlert"] div {{ color:var(--pl-ink) !important; -webkit-text-fill-color:var(--pl-ink) !important; }}
      [data-testid="stAlert"] svg {{ color:var(--pl-accent) !important; fill:var(--pl-accent) !important; }}
      [data-testid="stFormSubmitButton"] button {{ background:var(--pl-accent) !important; border:1px solid var(--pl-accent) !important; color:var(--pl-on-accent) !important; -webkit-text-fill-color:var(--pl-on-accent) !important; font-weight:850 !important; letter-spacing:.01em; box-shadow:0 5px 18px color-mix(in srgb,var(--pl-accent) 22%,transparent) !important; }}
      [data-testid="stFormSubmitButton"] button:hover {{ background:var(--pl-accent-hover) !important; border-color:var(--pl-accent-hover) !important; transform:translateY(-2px); box-shadow:0 10px 25px color-mix(in srgb,var(--pl-accent) 30%,transparent) !important; }}
      [data-testid="stFormSubmitButton"] button:focus-visible {{ outline:3px solid var(--pl-accent-border) !important; outline-offset:3px !important; }}
      .pl-api-key-notice {{ display:flex; gap:.75rem; align-items:flex-start; border:1px solid var(--pl-accent-border); border-left:4px solid var(--pl-accent); background:var(--pl-panel); border-radius:13px; padding:.9rem 1rem; margin:.8rem 0; color:var(--pl-ink) !important; }}
      .pl-api-key-icon {{ display:grid; place-items:center; width:2rem; height:2rem; flex:0 0 2rem; border-radius:10px; background:var(--pl-accent-soft); color:var(--pl-accent) !important; font-size:1.05rem; }}
      .pl-api-key-title {{ color:var(--pl-ink) !important; font-weight:850; margin:0 0 .2rem; }}
      .pl-api-key-copy {{ color:var(--pl-muted) !important; font-size:.84rem; line-height:1.55; margin:0; }}
      .pl-api-key-copy code {{ background:var(--pl-code-bg) !important; color:var(--pl-code-ink) !important; border:1px solid var(--pl-code-border) !important; border-radius:5px !important; padding:.10rem .34rem !important; font:650 .88em ui-monospace,SFMono-Regular,Consolas,monospace !important; }}
      [data-testid="stForm"] {{ border:1px solid var(--pl-border) !important; border-radius:18px !important; background:var(--pl-surface) !important; padding:clamp(.9rem,2.3vw,1.35rem) !important; box-shadow:0 4px 18px rgba(12,35,30,.025); }}
      [data-testid="stAlert"] {{ border-radius:12px !important; }}
      .pl-result-head {{ border:1px solid var(--pl-border); border-radius:16px; padding:1.1rem 1.2rem; background:var(--pl-surface); }}
      .pl-verdict {{ color:var(--pl-ink) !important; margin:.2rem 0 .45rem; font-size:1.25rem; font-weight:850; }}
      .pl-correction-text {{ margin:.75rem 0 .8rem; padding:1rem 1.1rem; border:1px solid var(--pl-code-border); border-radius:12px; background:var(--pl-code-bg); color:var(--pl-code-ink) !important; font:500 .92rem/1.6 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace; white-space:pre-wrap; overflow-wrap:anywhere; }}
      .pl-footer {{ border-top:1px solid var(--pl-border); margin-top:2rem; padding-top:1rem; color:var(--pl-subtle) !important; font-size:.76rem; line-height:1.6; }}
      .pl-sidebar-note {{ color:var(--pl-muted) !important; font-size:.78rem; line-height:1.55; }}
      @keyframes pl-shimmer {{ 0%,55% {{ transform:translateX(-115%); }} 78%,100% {{ transform:translateX(115%); }} }}
      @keyframes pl-twinkle {{ 0%,100% {{ opacity:.35; transform:scale(.85) rotate(0); }} 50% {{ opacity:1; transform:scale(1.1) rotate(12deg); }} }}
      .pl-comet {{ position:absolute; z-index:2; width:58px; height:2px; left:-72px; top:30%; border-radius:99px; pointer-events:none; background:linear-gradient(90deg,transparent,rgba(129,248,239,.94)); box-shadow:0 0 9px rgba(107,241,232,.45); transform:rotate(-27deg); animation:pl-comet-pass 10.5s ease-in-out infinite; animation-delay:2.5s; }}
      @keyframes pl-comet-pass {{ 0%,58%,100% {{ opacity:0; transform:translate(0,0) rotate(-27deg); }} 61% {{ opacity:1; }} 74% {{ opacity:0; transform:translate(460px,92px) rotate(-27deg); }} }}
      @keyframes pl-fade-up {{ from {{ opacity:0; transform:translateY(9px); }} to {{ opacity:1; transform:translateY(0); }} }}
      .block-container {{ animation:pl-fade-up .4s ease-out both; }}
      @media (max-width:820px) {{ .pl-hero {{ grid-template-columns:1fr; }} .pl-hero-art {{ max-width:440px; width:100%; margin:.2rem auto 0; }} .hero-mascot-slot {{ height:204px; }} .pl-hero h1 {{ font-size:clamp(1.8rem,7vw,2.6rem); }} }}
      @media (max-width:520px) {{ .block-container {{ padding-top:1.15rem !important; }} .pl-hero {{ padding:1.1rem; border-radius:18px; }} .pl-chip {{ font-size:.68rem; }} .hero-mascot-slot {{ height:184px; }} .pl-step-card {{ min-height:0; }} }}
      @media (max-width:560px) {{ .block-container {{ padding:.85rem .7rem 2rem !important; }} .pl-hero {{ border-radius:18px; padding:1.15rem; }} .pl-hero h1 {{ font-size:clamp(1.8rem,9vw,2.4rem); }} .pl-step-card {{ min-height:0; padding:.9rem; }} [data-testid="stForm"] {{ padding:.75rem !important; }} [data-testid="stTextArea"] textarea {{ font-size:16px !important; }} .pl-chip {{ font-size:.68rem; }} }}
      @media (prefers-reduced-motion:reduce) {{ *,*::before,*::after {{ animation-duration:.01ms !important; animation-iteration-count:1 !important; scroll-behavior:auto !important; transition-duration:.01ms !important; }} }}
    </style>
    """,
    unsafe_allow_html=True,
)

config = api_configuration()
key_ready = bool(config["api_key"])
model_name = config.get("model", "AI model")

with st.sidebar:
    st.markdown(
        '<div class="pl-brand"><div class="pl-logo" aria-hidden="true"><svg viewBox="0 0 44 44" role="presentation" focusable="false"><defs><linearGradient id="pl-brand-gradient" x1="4" y1="4" x2="40" y2="40" gradientUnits="userSpaceOnUse"><stop stop-color="#87F5EC"/><stop offset=".55" stop-color="#9C9AFF"/><stop offset="1" stop-color="#DDA8FF"/></linearGradient></defs><circle cx="22" cy="22" r="15.5" fill="none" stroke="url(#pl-brand-gradient)" stroke-width="2.3"/><ellipse cx="22" cy="22" rx="20" ry="8.5" transform="rotate(-34 22 22)" fill="none" stroke="url(#pl-brand-gradient)" stroke-width="1.5" opacity=".8"/><path d="M14.3 22.8l5.1 5.1 10.6-12" fill="none" stroke="#F5FFFF" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round"/><circle cx="35.2" cy="9.2" r="2.1" fill="#FFC8F2"/></svg></div><div><div class="pl-brand-name">ProofLoop</div><div class="pl-brand-tag">Annotation quality checker</div></div></div>',
        unsafe_allow_html=True,
    )
    st.markdown("### Workspace settings")
    st.checkbox("Show Loop mascot", key="pl_show_loop")
    st.markdown("---")
    st.markdown("**AI connection**")
    if key_ready:
        st.success("API key configured", icon="✅")
        st.caption(f"Model: {model_name}")
    else:
        st.warning("API key required for live reviews", icon="🔌")
        st.caption("Set BACKBOARD_API_KEY in Codespaces secrets, then restart the Codespace.")
    st.markdown("---")
    st.markdown(
        '<div class="pl-sidebar-note"><b>Loop controls</b><br>Click Loop to wave. Drag it to a workspace area and release it to see the reaction. Use the small × by Loop to return it home.</div>',
        unsafe_allow_html=True,
    )

# The theme selector updates session state during widget evaluation; refresh palette for this run.
palette = THEMES[st.session_state["pl_theme"]]

brand_col, appearance_col = st.columns([3.4, 1.35], gap="medium", vertical_alignment="center")
with brand_col:
    st.markdown(
        '<div class="pl-brand"><div class="pl-logo" aria-hidden="true"><svg viewBox="0 0 44 44" role="presentation" focusable="false"><defs><linearGradient id="pl-brand-gradient" x1="4" y1="4" x2="40" y2="40" gradientUnits="userSpaceOnUse"><stop stop-color="#87F5EC"/><stop offset=".55" stop-color="#9C9AFF"/><stop offset="1" stop-color="#DDA8FF"/></linearGradient></defs><circle cx="22" cy="22" r="15.5" fill="none" stroke="url(#pl-brand-gradient)" stroke-width="2.3"/><ellipse cx="22" cy="22" rx="20" ry="8.5" transform="rotate(-34 22 22)" fill="none" stroke="url(#pl-brand-gradient)" stroke-width="1.5" opacity=".8"/><path d="M14.3 22.8l5.1 5.1 10.6-12" fill="none" stroke="#F5FFFF" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round"/><circle cx="35.2" cy="9.2" r="2.1" fill="#FFC8F2"/></svg></div><div><div class="pl-brand-name">ProofLoop</div><div class="pl-brand-tag">Guideline-based annotation QA</div></div></div>',
        unsafe_allow_html=True,
    )
with appearance_col:
    st.radio("Appearance", ["Light", "Dark"], horizontal=True, key="pl_theme")

st.markdown(
    '''
    <section class="pl-hero">
      <div>
        <div class="pl-eyebrow">TEXT-ONLY ANNOTATION REVIEW</div>
        <h1>Make sure your answer follows the guidelines.</h1>
        <p class="pl-hero-copy">Paste the task instructions and your answer. ProofLoop checks your answer against those rules, explains specific mistakes, and suggests a corrected version you can copy into your workflow.</p>
        <div class="pl-chips"><span class="pl-chip">Guideline-based verdict</span><span class="pl-chip">Specific mistake explanations</span><span class="pl-chip">Copy-ready correction</span><span class="pl-chip">No image or video uploads</span></div>
      </div>
      <div class="pl-hero-art" aria-label="Loop's animated space home">
        <div class="hero-mascot-slot" id="pl-robot-home-slot" aria-label="Loop home scene. Drag Loop to a step card or the review button.">
          <div class="pl-space-scene scene-nebula"></div><div class="pl-space-scene scene-planet"></div><div class="pl-space-scene scene-aurora"></div>
          <div class="pl-orbit"></div><span class="pl-comet" aria-hidden="true"></span><span class="pl-scene-label"><span class="scene-name">NEBULA GARDEN · 01</span><span class="scene-name">ORBIT STATION · 02</span><span class="scene-name">AURORA DRIFT · 03</span></span>
          <span class="pl-star a">✦</span><span class="pl-star b">✧</span><div class="pl-platform"></div><div class="pl-mascot-caption">LOOP · YOUR REVIEW COMPANION</div>
        </div>
      </div>
    </section>
    ''',
    unsafe_allow_html=True,
)

steps = st.columns(3, gap="small")
step_data = [
    ("STEP 01", "Add your guidelines", "Paste the actual task rules and evaluation criteria."),
    ("STEP 02", "Paste the answer", "Add the caption, annotation, or written feedback to check."),
    ("STEP 03", "Review and correct", "See the verdict, exact issues, and a corrected answer."),
]
for col, (number, title, copy) in zip(steps, step_data):
    with col:
        st.markdown(
            f'<div class="pl-step-card" id="pl-step-{number[-2:]}"><div class="pl-step-no">{number}</div><div class="pl-step-title">{html.escape(title)}</div><div class="pl-step-copy">{html.escape(copy)}</div></div>',
            unsafe_allow_html=True,
        )

if st.session_state["pl_show_loop"]:
    render_global_robot(st.session_state.get("proofloop_mascot_status", "idle"), palette)
else:
    from proofloop.mascot import hide_global_robot
    hide_global_robot()

st.markdown('<div class="pl-section-title">Check your work</div>', unsafe_allow_html=True)
st.markdown('<div class="pl-muted">Choose the task type below. Everything starts empty so you can test with your real guidelines and answers.</div>', unsafe_allow_html=True)
mode_label = st.radio(
    "Choose your review type",
    options=["Single answer review", "Comparison / feedback review"],
    horizontal=False,
    key="review_mode_label",
    help="Single answer checks one response. Comparison / feedback checks a written judgment about two text outputs.",
)
mode = "comparison" if mode_label == "Comparison / feedback review" else "single"
if mode == "single":
    st.markdown('<div class="pl-note"><b>Single answer review:</b> use this for one caption, annotation, written response, or feedback statement that must follow the guidelines.</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="pl-note"><b>Comparison / feedback review:</b> paste both text outputs and the annotator\'s comparison. ProofLoop checks whether the feedback accurately follows the supplied rules.</div>', unsafe_allow_html=True)

with st.form("proofloop_review_form", clear_on_submit=False):
    guidelines = st.text_area(
        "1. Task guidelines *",
        placeholder="Paste the real instructions, rubric, and rules your answer must follow…",
        height=180,
        key="guidelines_input",
        help="Use the exact instructions from your annotation task. ProofLoop treats them as the primary review standard.",
    )
    answer = ""
    output_a = ""
    output_b = ""
    comparison_feedback = ""
    if mode == "single":
        answer = st.text_area(
            "2. Annotator's answer *",
            placeholder="Paste the exact caption, annotation, written response, or feedback you want checked…",
            height=180,
            key="single_answer_input",
            help="This is a text-only check. ProofLoop cannot validate claims that require source material it has not been given.",
        )
    else:
        output_a = st.text_area("2. Output A *", placeholder="Paste the first text output…", height=130, key="output_a_input")
        output_b = st.text_area("3. Output B *", placeholder="Paste the second text output…", height=130, key="output_b_input")
        comparison_feedback = st.text_area(
            "4. Annotator's comparison / feedback *",
            placeholder="Paste the annotator's judgment explaining which output is better and why…",
            height=170,
            key="comparison_feedback_input",
            help="ProofLoop checks the feedback against the guidelines and supplied outputs.",
        )
    st.caption("* Required. Your text is sent to the configured AI service only when you submit a review.")
    submit = st.form_submit_button("Check guideline alignment", type="primary", use_container_width=True)

if not key_ready:
    st.markdown(
        '<div class="pl-api-key-notice"><div class="pl-api-key-icon" aria-hidden="true">🔑</div><div><div class="pl-api-key-title">API key required for live reviews</div><p class="pl-api-key-copy">Configure <code>BACKBOARD_API_KEY</code> in Codespaces secrets, then restart the Codespace. ProofLoop will not invent a verdict while the AI connection is unavailable.</p></div></div>',
        unsafe_allow_html=True,
    )

if submit:
    st.session_state.pop("proofloop_last_review", None)
    st.session_state.pop("proofloop_last_inputs", None)
    errors = validate_inputs(
        mode=mode, guidelines=guidelines, answer=answer, output_a=output_a,
        output_b=output_b, comparison_feedback=comparison_feedback,
    )
    if errors:
        for error in errors:
            st.error(error)
        st.session_state["proofloop_mascot_status"] = "error"
    elif not key_ready:
        st.error("Review not run: configure the Backboard API key, then submit again.")
        st.session_state["proofloop_mascot_status"] = "error"
    else:
        st.session_state["proofloop_pending_review"] = {
            "mode": mode, "mode_label": mode_label, "guidelines": guidelines,
            "answer": answer, "output_a": output_a, "output_b": output_b,
            "comparison_feedback": comparison_feedback,
        }
        st.session_state["proofloop_mascot_status"] = "thinking"
        st.rerun()

pending = st.session_state.pop("proofloop_pending_review", None)
if pending:
    prompt = build_evaluation_prompt(
        guidelines=pending["guidelines"], mode=pending["mode"], answer=pending["answer"],
        output_a=pending["output_a"], output_b=pending["output_b"],
        comparison_feedback=pending["comparison_feedback"],
    )
    try:
        with st.spinner("Checking your answer against the supplied guidelines…"):
            raw_response = asyncio.run(generate_review(prompt))
        review = parse_review_response(raw_response)
        st.session_state["proofloop_last_review"] = review
        st.session_state["proofloop_last_inputs"] = pending
        st.session_state["proofloop_mascot_status"] = "success"
        st.rerun()
    except Exception as exc:
        config_now = api_configuration()
        message = str(exc).replace(config_now["api_key"], "[REDACTED]") if config_now["api_key"] else str(exc)
        st.session_state["proofloop_mascot_status"] = "error"
        st.error("The review could not be completed. Check your API configuration and try again.")
        st.caption(message[:600])

review = st.session_state.get("proofloop_last_review")
if review:
    st.markdown('<div class="pl-section-title">Review results</div>', unsafe_allow_html=True)
    verdict = review["verdict"]
    st.markdown(
        f'<div class="pl-result-head"><div class="pl-eyebrow">VERDICT</div><div class="pl-verdict">{html.escape(verdict)}</div><div class="pl-muted">{html.escape(review["summary"])}</div></div>',
        unsafe_allow_html=True,
    )
    if not review.get("parse_ok", True):
        st.warning("The response was not parsed into a reliable structured verdict. Inspect the raw response below before treating it as final.")
    issues = review.get("issues", [])
    st.markdown("### Issues to fix")
    if not issues:
        st.success("No specific guideline violations were identified in this structured review. This is an AI assessment, not a guarantee of correctness.")
    else:
        for index, issue in enumerate(issues, start=1):
            title = str(issue.get("title", f"Issue {index}"))
            severity = str(issue.get("severity", "Review"))
            with st.expander(f"{index}. {title} · {severity}", expanded=index == 1):
                if issue.get("guideline"):
                    st.markdown("**Relevant guideline**")
                    st.write(issue["guideline"])
                if issue.get("problem"):
                    st.markdown("**What is wrong**")
                    st.write(issue["problem"])
                if issue.get("reason"):
                    st.markdown("**Why it matters**")
                    st.write(issue["reason"])
                if issue.get("suggestion"):
                    st.markdown("**How to fix it**")
                    st.write(issue["suggestion"])
    if review.get("strengths"):
        st.markdown("### What is already working")
        for strength in review["strengths"]:
            st.markdown(f"- {strength}")
    correction = review.get("corrected_answer", "")
    st.markdown("### Suggested final answer")
    st.markdown('<div class="pl-muted">Copy the revised text into your annotation workflow, then verify it against your task policy.</div>', unsafe_allow_html=True)
    if correction:
        st.markdown(
            f'<div class="pl-correction-text" role="region" aria-label="Corrected answer">{html.escape(correction)}</div>',
            unsafe_allow_html=True,
        )
        copy_text_js = json.dumps(correction, ensure_ascii=False)
        is_dark = palette["color_scheme"] == "dark"
        correction_html = f"""
        <!doctype html>
        <html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
          * {{ box-sizing:border-box; }}
          html, body {{ margin:0; padding:0; background:transparent; color:{palette['ink']};
            font-family:Inter,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; }}
          .copy-dock {{ display:flex; align-items:center; justify-content:space-between; gap:14px;
            width:100%; min-height:68px; padding:11px 12px; border:1px solid {palette['border']};
            border-radius:13px; background:linear-gradient(115deg,{palette['surface']},{palette['card']});
            color:{palette['ink']}; }}
          .copy-main {{ display:flex; align-items:center; gap:10px; min-width:0; flex:1 1 auto; }}
          .copy-mark {{ display:grid; place-items:center; flex:0 0 38px; width:38px; height:38px;
            border:1px solid {palette['accent_border']}; border-radius:11px;
            background:{palette['accent_soft']}; color:{palette['accent']}; }}
          .copy-mark svg {{ width:18px; height:18px; display:block; }}
          .copy-copy {{ min-width:0; }}
          .copy-eyebrow {{ margin:0 0 3px; color:{palette['accent']}; font-size:9px;
            line-height:1.2; letter-spacing:.13em; font-weight:800; text-transform:uppercase; }}
          .copy-title {{ margin:0; color:{palette['ink']}; font-size:12.5px; line-height:1.35; font-weight:750; }}
          .copy-detail {{ margin:3px 0 0; color:{palette['muted']}; font-size:10.5px; line-height:1.35; }}
          .copy-btn {{ flex:0 0 auto; display:inline-flex; align-items:center; justify-content:center; gap:8px;
            min-height:40px; padding:0 15px; border:1px solid {palette['accent']}; border-radius:10px;
            background:{palette['accent']}; color:{palette['on_accent']};
            font:750 12px/1 Inter,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
            white-space:nowrap; cursor:pointer; user-select:none;
            box-shadow:0 5px 14px {('rgba(0,0,0,.24)' if is_dark else 'rgba(8,127,112,.15)')};
            transition:transform .16s ease,background .16s ease,border-color .16s ease,box-shadow .16s ease; }}
          .copy-btn svg {{ display:block; width:15px; height:15px; flex:0 0 15px; }}
          .copy-btn:hover {{ background:{palette['accent_hover']}; border-color:{palette['accent_hover']};
            transform:translateY(-1px); }}
          .copy-btn:active {{ transform:translateY(0) scale(.985); }}
          .copy-btn:focus-visible {{ outline:2px solid {palette['accent']}; outline-offset:3px; }}
          .copy-btn.is-copied {{ background:{palette['accent_soft']}; color:{palette['accent']};
            border-color:{palette['accent_border']}; box-shadow:none; }}
          .copy-feedback {{ min-height:15px; padding:4px 3px 0; color:{palette['muted']};
            font-size:10.5px; line-height:1.35; }}
          @media (max-width:540px) {{
            .copy-dock {{ gap:8px; padding:10px; min-height:62px; }}
            .copy-main {{ gap:8px; }} .copy-mark {{ flex-basis:34px; width:34px; height:34px; border-radius:10px; }}
            .copy-detail {{ display:none; }} .copy-eyebrow {{ font-size:8px; }}
            .copy-title {{ font-size:11.5px; }} .copy-btn {{ min-height:38px; padding:0 11px; gap:6px; font-size:11.5px; }}
          }}
        </style></head><body>
          <section class="copy-dock" aria-label="Copy suggested correction">
            <div class="copy-main">
              <div class="copy-mark" aria-hidden="true">
                <svg viewBox="0 0 24 24" fill="none"><rect x="8.5" y="8.5" width="11" height="12" rx="2" stroke="currentColor" stroke-width="1.7"/><path d="M15.5 8.5V6A2 2 0 0 0 13.5 4h-8A2 2 0 0 0 3.5 6v9a2 2 0 0 0 2 2h3" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/></svg>
              </div>
              <div class="copy-copy">
                <p class="copy-eyebrow">Ready to reuse</p>
                <p class="copy-title">Copy corrected answer</p>
                <p class="copy-detail">Copy it once, then paste it into your annotation workflow.</p>
              </div>
            </div>
            <button class="copy-btn" id="pl-copy-btn" type="button" aria-label="Copy corrected answer">
              <svg id="pl-copy-icon" viewBox="0 0 24 24" fill="none" aria-hidden="true"><rect x="8.5" y="8.5" width="11" height="12" rx="2" stroke="currentColor" stroke-width="1.7"/><path d="M15.5 8.5V6A2 2 0 0 0 13.5 4h-8A2 2 0 0 0 3.5 6v9a2 2 0 0 0 2 2h3" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/></svg>
              <span id="pl-copy-label">Copy correction</span>
            </button>
          </section>
          <div class="copy-feedback" id="pl-copy-feedback" role="status" aria-live="polite"></div>
          <script>
          (() => {{
            const btn = document.getElementById('pl-copy-btn');
            const label = document.getElementById('pl-copy-label');
            const icon = document.getElementById('pl-copy-icon');
            const feedback = document.getElementById('pl-copy-feedback');
            const correction = {copy_text_js};
            const copySvg = '<rect x="8.5" y="8.5" width="11" height="12" rx="2" stroke="currentColor" stroke-width="1.7"/><path d="M15.5 8.5V6A2 2 0 0 0 13.5 4h-8A2 2 0 0 0 3.5 6v9a2 2 0 0 0 2 2h3" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/>';
            const checkSvg = '<path d="m5 12.5 4.2 4.2L19.5 6.8" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>';
            let resetTimer;
            btn.addEventListener('click', async () => {{
              btn.disabled = true;
              let copied = false;
              try {{
                if (navigator.clipboard && window.isSecureContext) {{
                  await navigator.clipboard.writeText(correction);
                  copied = true;
                }}
              }} catch (error) {{
                copied = false;
              }}
              if (!copied) {{
                let area;
                try {{
                  area = document.createElement('textarea');
                  area.value = correction; area.setAttribute('readonly', '');
                  area.style.position = 'fixed'; area.style.top = '0'; area.style.left = '-9999px';
                  document.body.appendChild(area); area.focus(); area.select();
                  copied = document.execCommand('copy');
                }} catch (error) {{
                  copied = false;
                }} finally {{
                  if (area) area.remove();
                }}
              }}
              btn.disabled = false;
              if (copied) {{
                clearTimeout(resetTimer);
                btn.classList.add('is-copied');
                btn.setAttribute('aria-label', 'Answer copied to clipboard');
                icon.innerHTML = checkSvg;
                label.textContent = 'Copied!';
                feedback.textContent = 'Copied successfully — ready to paste.';
                resetTimer = window.setTimeout(() => {{
                  btn.classList.remove('is-copied');
                  btn.setAttribute('aria-label', 'Copy corrected answer');
                  icon.innerHTML = copySvg;
                  label.textContent = 'Copy correction';
                  feedback.textContent = '';
                }}, 2200);
              }} else {{
                feedback.textContent = 'Clipboard access was blocked. Select the correction above and copy it manually.';
              }}
            }});
          }})();
          </script>
        </body></html>
        """
        components.html(correction_html, height=100, scrolling=False)
        st.download_button("Download corrected answer (.txt)", data=correction, file_name="proofloop-corrected-answer.txt", mime="text/plain", use_container_width=True)
    else:
        st.info("No corrected answer was generated because the available information was insufficient for a safe rewrite.")
    meta_cols = st.columns(2)
    with meta_cols[0]:
        st.markdown("**Reviewer confidence**")
        st.write(review.get("confidence", "Low"))
    with meta_cols[1]:
        st.markdown("**Limitations / missing context**")
        st.write(review.get("limitations") or "No additional limitation was reported.")
    report_text = (
        f"ProofLoop guideline review\n\nVerdict: {verdict}\nSummary: {review.get('summary', '')}\n"
        f"Confidence: {review.get('confidence', 'Low')}\n\nIssues:\n"
        + ("\n".join(
            f"- {item.get('title', 'Issue')}: {item.get('problem', '')}\n  Guideline: {item.get('guideline', '')}\n  Reason: {item.get('reason', '')}\n  Suggestion: {item.get('suggestion', '')}"
            for item in issues
        ) or "No structured issues reported.")
        + f"\n\nSuggested final answer:\n{correction or '(Not provided)'}\n\nLimitations: {review.get('limitations', '')}\n"
    )
    st.download_button("Download full review (.txt)", data=report_text, file_name="proofloop-review.txt", mime="text/plain")
    with st.expander("View raw AI response"):
        st.text(review.get("raw_response", ""))

st.markdown(
    '<div class="pl-footer">ProofLoop checks text against the guidelines you provide. It does not inspect images or videos and cannot verify facts that depend on unseen source material. Use the result as a review aid and make the final decision using your task evidence and policy.</div>',
    unsafe_allow_html=True,
)
