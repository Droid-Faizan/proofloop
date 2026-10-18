"""Interactive ProofLoop companion, restored from the previous working version.

Loop is injected as a single page-level widget so dragging and animation do not
interfere with Streamlit forms.
"""
from __future__ import annotations

import streamlit.components.v1 as components

def render_global_robot(mascot_status: str, palette: dict[str, str]) -> None:
    """Inject one lightweight, draggable 3/4-profile robot mascot into Streamlit's parent page."""
    status = mascot_status if mascot_status in {"idle", "thinking", "success", "error"} else "idle"
    tokens = {
        "__BG__": palette["bg"], "__SURFACE__": palette["surface"], "__CARD__": palette["card"],
        "__BORDER__": palette["border"], "__INK__": palette["ink"], "__MUTED__": palette["muted"],
        "__ACCENT__": palette["accent"], "__ACCENT_SOFT__": palette["accent_soft"],
        "__STATUS__": status,
        "__THEME__": "light" if palette.get("color_scheme") == "light" else "dark",
    }
    doc = r'''<!doctype html><html lang="en"><head><meta charset="utf-8"><style>
      html,body{margin:0;padding:0;background:transparent;overflow:hidden}
    </style></head><body><script>
    (() => {
      let pd;
      try { pd = window.parent.document; if (!pd || pd === document) return; }
      catch (_) { return; }

      // A Streamlit rerun (including a theme switch) recreates this iframe. Tear
      // down listeners, timers, and observers owned by the previous iframe, but
      // replace versioned markup/styles when the mascot implementation changes.
      try {
        const previousRuntime = pd.defaultView.__proofloopRobotController;
        if (previousRuntime && typeof previousRuntime.destroy === 'function') previousRuntime.destroy();
      } catch (_) {}

      // Clean up earlier iterations. Keep at most one current controller/root so
      // stale mascots from previous Streamlit reruns cannot remain visible.
      ['pl-live-companion','pl-live-companion-style','pl-live-robot-old','pl-live-robot-old-style',
       'pl-robot-root','pl-mascot-overlay','proofloop-mascot-root','proofloop-teddy-root'].forEach(id => {
        pd.querySelectorAll('#' + id).forEach(node => node.remove());
      });
      const robotRoots = [...pd.querySelectorAll('#pl-live-robot')];
      const keepRobot = robotRoots.find(node => node.dataset.plVersion === '19') || null;
      robotRoots.forEach(node => { if (node !== keepRobot) node.remove(); });
      const robotStyles = [...pd.querySelectorAll('#pl-live-robot-style')];
      const keepStyle = robotStyles.find(node => node.dataset.plVersion === '19') || null;
      robotStyles.forEach(node => { if (node !== keepStyle) node.remove(); });
      try {
        pd.querySelectorAll('iframe').forEach(frame => {
          try {
            const fd = frame.contentDocument;
            if (fd) {
              fd.querySelectorAll('#teddy, #plb-bear, .teddy, #pl-live-companion, #pl-live-robot-old').forEach(old => {
                const stage = old.closest('#stage,.mascot-stage');
                if (stage) stage.remove(); else old.remove();
              });
            }
          } catch (_) {}
        });
      } catch (_) {}

      const colors = { bg:'__BG__', surface:'__SURFACE__', card:'__CARD__', border:'__BORDER__', ink:'__INK__', muted:'__MUTED__', accent:'__ACCENT__', accentSoft:'__ACCENT_SOFT__' };
      const status = '__STATUS__';
      let root = pd.getElementById('pl-live-robot');
      if (!root) {
        const oldStyle = pd.getElementById('pl-live-robot-style'); if (oldStyle) oldStyle.remove();
        const style = pd.createElement('style'); style.id = 'pl-live-robot-style'; style.dataset.plVersion = '19';
        style.textContent = `
          #pl-live-robot{position:fixed;inset:0;z-index:999990;pointer-events:none;overflow:visible;font-family:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;color:var(--plr-ink)}
          #pl-live-robot .plr-character{position:fixed;left:calc(100vw - 114px);top:120px;width:98px;height:118px;pointer-events:auto;touch-action:none;user-select:none;-webkit-user-select:none;cursor:grab;filter:drop-shadow(0 6px 4px rgba(10,20,35,.16));transform-origin:50% 90%;animation:plr-stand 3.8s ease-in-out infinite;transition:filter .18s ease;outline:none}
          #pl-live-robot .plr-character:hover{filter:drop-shadow(0 9px 7px rgba(10,20,35,.22))}
          #pl-live-robot .plr-character:before{content:"";position:absolute;z-index:0;left:calc(50% - 11px);bottom:-10px;width:22px;height:20px;opacity:0;pointer-events:none;transform-origin:50% 0;background:radial-gradient(ellipse at 50% 0%,rgba(255,255,255,.9) 0 12%,rgba(129,238,236,.94) 20%,rgba(159,128,255,.5) 48%,transparent 76%);filter:blur(1px);border-radius:50% 50% 60% 60%;}
          #pl-live-robot .plr-character:after{content:"";position:absolute;z-index:0;left:calc(50% - 18px);bottom:-17px;width:36px;height:25px;opacity:0;pointer-events:none;background:radial-gradient(circle at 20% 40%,rgba(170,190,197,.38) 0 3px,transparent 4px),radial-gradient(circle at 70% 55%,rgba(170,190,197,.28) 0 4px,transparent 5px),radial-gradient(circle at 48% 80%,rgba(170,190,197,.24) 0 5px,transparent 6px);filter:blur(1.2px);}
          #pl-live-robot .plr-character.home-hover:before{opacity:.9;animation:plr-thruster .19s ease-in-out infinite alternate;}
          #pl-live-robot .plr-character.home-hover:after{opacity:.72;animation:plr-smoke 2.3s ease-out infinite;}
          /* Cinematic idle vignettes: short, authored motions separated by calm hover. */
          #pl-live-robot .plr-character.idle-curious .plr-head{animation:plr-head-curious 1.05s cubic-bezier(.2,.75,.25,1) both;}
          #pl-live-robot .plr-character.idle-curious .antenna-near{animation:plr-antenna  .38s ease-in-out 2 alternate;transform-box:fill-box;transform-origin:center;}
          #pl-live-robot .plr-character.idle-stretch .plr-art{animation:plr-stretch-body 1.2s cubic-bezier(.2,.75,.25,1) both;}
          #pl-live-robot .plr-character.idle-stretch .plr-arm-near{animation:plr-stretch-near 1.2s ease-in-out both;}
          #pl-live-robot .plr-character.idle-stretch .plr-arm-far{animation:plr-stretch-far 1.2s ease-in-out both;}
          #pl-live-robot .plr-character.idle-stretch .plr-legs{transform-box:view-box;transform-origin:55px 101px;animation:plr-stretch-legs 1.2s ease-in-out both;}
          #pl-live-robot .plr-character.idle-cheer .plr-art{animation:plr-cheer-body 1.12s cubic-bezier(.2,.8,.2,1) both;}
          #pl-live-robot .plr-character.idle-cheer .plr-arm-near{animation:plr-wave .42s ease-in-out 2;}
          #pl-live-robot .plr-character.idle-scan .plr-scan-line{opacity:.96;animation:plr-scan-line 1.35s ease-in-out 1 both;}
          #pl-live-robot .plr-character.idle-scan .antenna-far{animation:plr-antenna  .4s ease-in-out 2 alternate;transform-box:fill-box;transform-origin:center;}
          #pl-live-robot .plr-character.idle-drift .plr-art{animation:plr-high-hover 1.45s cubic-bezier(.25,.7,.25,1) both;}
          #pl-live-robot .plr-character.idle-drift .plr-shadow{animation:plr-shadow-pulse 1.4s ease-in-out both;}
          #pl-live-robot .plr-character.idle-cheer .plr-idle-sparkles{opacity:1;animation:plr-sparkle-burst 1s ease-out both;}
          #pl-live-robot .plr-scan-line{opacity:0;stroke:#87F5F0;stroke-width:1.45;stroke-linecap:round;filter:drop-shadow(0 0 2px #6BE8E1)}
          #pl-live-robot .plr-idle-sparkles{opacity:0;transform-box:view-box;transform-origin:center;pointer-events:none}
          #pl-live-robot .plr-character.booting{animation:plr-boot-wobble .16s ease-in-out 9,plr-stand 3.8s ease-in-out infinite;}
          #pl-live-robot .plr-character.booting:before{opacity:1;animation:plr-ignite .24s ease-in-out 7 alternate;}
          #pl-live-robot .plr-character.booting:after{opacity:.85;animation:plr-smoke .65s ease-out 3;}
          #pl-live-robot .plr-character.carried:before,#pl-live-robot .plr-character.carried:after,#pl-live-robot .plr-character.falling:before,#pl-live-robot .plr-character.falling:after{opacity:0!important;animation:none!important;}
          @keyframes plr-thruster{from{transform:scaleX(.72) scaleY(.78);filter:blur(1.5px);opacity:.65}to{transform:scaleX(1.08) scaleY(1.22);filter:blur(.5px);opacity:1}}
          @keyframes plr-ignite{0%{transform:translateY(-2px) scale(.45,.6);opacity:.25}55%{transform:translateY(1px) scale(1.25,1.45);opacity:1}100%{transform:translateY(0) scale(.8,1.1);opacity:.8}}
          @keyframes plr-smoke{0%{transform:translateY(0) scale(.55);opacity:.1}35%{opacity:.7}100%{transform:translateY(12px) scale(1.5);opacity:0}}
          @keyframes plr-boot-wobble{0%,100%{transform:translate(0,0) rotate(-1deg)}25%{transform:translate(-2px,1px) rotate(-4deg)}50%{transform:translate(2px,-1px) rotate(3deg)}75%{transform:translate(-1px,1px) rotate(-2deg)}}
          #pl-live-robot .plr-character:focus-visible{outline:2px solid var(--plr-accent);outline-offset:5px;border-radius:18px}
          #pl-live-robot .plr-character svg{display:block;position:relative;z-index:1;width:100%;height:100%;overflow:visible;pointer-events:none}
          #pl-live-robot .plr-character[data-dir="left"] svg{transform:scaleX(-1)}
          #pl-live-robot .plr-character .plr-arm-near{transform-box:view-box;transform-origin:75px 66px;transition:transform .2s ease}
          #pl-live-robot .plr-character.waving .plr-arm-near{animation:plr-wave .48s ease-in-out 3}
          #pl-live-robot .plr-character.cheer .plr-arm-near{animation:plr-wave .4s ease-in-out 4}
          #pl-live-robot .plr-character .plr-eye{transform-box:fill-box;transform-origin:center;animation:plr-blink 5.2s infinite}
          #pl-live-robot .plr-character .plr-body{transform-box:fill-box;transform-origin:center;animation:plr-breathe 4.8s ease-in-out infinite}
          #pl-live-robot .plr-character .plr-head{transform-box:view-box;transform-origin:55px 36px}
          #pl-live-robot .plr-character .face-delight,#pl-live-robot .plr-character .face-curious{display:none}
          #pl-live-robot .plr-character .face-bored,#pl-live-robot .plr-character .face-sleep,#pl-live-robot .plr-character .face-annoyed,#pl-live-robot .plr-character .face-confused{display:none}
          #pl-live-robot .plr-character.bored .face-normal,#pl-live-robot .plr-character.sleeping .face-normal,#pl-live-robot .plr-character.annoyed .face-normal,#pl-live-robot .plr-character.confused .face-normal{display:none}
          #pl-live-robot .plr-character.confused .face-annoyed{display:none}
          #pl-live-robot .plr-character.idle-cheer .face-normal,#pl-live-robot .plr-character.idle-curious .face-normal{display:none}
          #pl-live-robot .plr-character.idle-cheer .face-delight,#pl-live-robot .plr-character.idle-curious .face-curious{display:block}
          #pl-live-robot .plr-character.bored .face-bored,#pl-live-robot .plr-character.sleeping .face-sleep,#pl-live-robot .plr-character.annoyed .face-annoyed,#pl-live-robot .plr-character.confused .face-confused{display:block}
          #pl-live-robot .plr-character.bored{animation:plr-bored 2.3s ease-in-out infinite}
          #pl-live-robot .plr-character.sleeping{animation:plr-sleep 3.5s ease-in-out infinite}
          #pl-live-robot .plr-character.sleeping .plr-z{opacity:1;animation:plr-zzz 1.4s ease-in-out infinite}
          #pl-live-robot .plr-character.sleeping .plr-snore{opacity:1;animation:plr-snore 2.1s ease-in-out infinite}
          #pl-live-robot .plr-snore{opacity:0;transition:opacity .2s ease}
          #pl-live-robot .plr-character.sleeping .plr-eye-glint{opacity:.25}
          #pl-live-robot .plr-z{opacity:0;transition:opacity .25s ease}
          #pl-live-robot .plr-character.thinking{animation:plr-think .7s ease-in-out infinite alternate}
          #pl-live-robot .plr-character.thinking .antenna-near{animation:plr-antenna .45s ease-in-out infinite alternate;transform-box:fill-box;transform-origin:center}
          #pl-live-robot .plr-character.walking{animation:plr-walk .24s ease-in-out infinite alternate}
          #pl-live-robot .plr-character.carried{animation:none;cursor:grabbing;filter:drop-shadow(0 12px 9px rgba(10,20,35,.25));}
          #pl-live-robot .plr-character.carried svg{transform:rotate(-7deg)}
          #pl-live-robot .plr-character.carried .plr-arm-near{transform:rotate(-34deg) translateY(-2px)}
          #pl-live-robot .plr-character.carried .plr-arm-far{transform:rotate(24deg) translateY(-2px)}
          #pl-live-robot .plr-character.carried[data-dir="left"] svg{transform:scaleX(-1) rotate(-7deg)}
          #pl-live-robot .plr-character.falling{animation:plr-fall .62s cubic-bezier(.45,.05,.7,.35) both}
          #pl-live-robot .plr-character.impact{animation:plr-impact .25s ease-out both}
          #pl-live-robot .plr-character.sitting{animation:plr-sit .42s ease-out both}
          #pl-live-robot .plr-character.hover-land{animation:plr-hover-land .65s ease-out both}
          #pl-live-robot .plr-character.annoyed{animation:plr-annoyed .3s ease-in-out 2}
          #pl-live-robot .plr-character.annoyed .antenna-near{transform:rotate(-10deg)}
          #pl-live-robot .plr-speech{position:fixed;max-width:205px;min-width:112px;padding:8px 11px;border:1px solid var(--plr-border);border-radius:13px;background:var(--plr-surface);color:var(--plr-ink);font:700 12px/1.35 "Trebuchet MS","Segoe UI",sans-serif;letter-spacing:.005em;box-shadow:0 9px 26px rgba(5,16,30,.15);pointer-events:none;opacity:0;visibility:hidden;transform:translateY(5px) scale(.98);transform-origin:bottom center;transition:opacity .2s ease,transform .2s ease,visibility .2s;z-index:999992;white-space:normal;text-align:center}
          #pl-live-robot .plr-speech.show{opacity:1;visibility:visible;transform:translateY(0) scale(1)}
          #pl-live-robot .plr-speech:after{content:"";position:absolute;width:8px;height:8px;left:calc(50% - 4px);bottom:-5px;background:var(--plr-surface);border-right:1px solid var(--plr-border);border-bottom:1px solid var(--plr-border);transform:rotate(45deg)}
          #pl-live-robot .plr-hide{position:fixed;display:grid;place-items:center;width:22px;height:22px;border-radius:50%;border:1px solid var(--plr-border);background:var(--plr-surface);color:var(--plr-muted);font:14px/1 sans-serif;cursor:pointer;pointer-events:auto;opacity:0;z-index:999993;transition:opacity .18s ease,transform .18s ease;box-shadow:0 3px 12px rgba(5,16,30,.12)}
          #pl-live-robot .plr-character:hover ~ .plr-hide,#pl-live-robot .plr-character:focus-visible ~ .plr-hide,#pl-live-robot .plr-hide:hover,#pl-live-robot .plr-hide:focus-visible{opacity:.92} #pl-live-robot .plr-hide:hover{color:var(--plr-ink);border-color:var(--plr-accent);transform:scale(1.06)}
          @keyframes plr-stand{0%,100%{transform:translateY(0) rotate(-.7deg)}50%{transform:translateY(-3px) rotate(.8deg)}}
          @keyframes plr-blink{0%,42%,46%,100%{transform:scaleY(1)}44%{transform:scaleY(.12)}}
          @keyframes plr-wave{0%,100%{transform:rotate(0)}35%{transform:rotate(-28deg)}70%{transform:rotate(12deg)}}
          @keyframes plr-bored{0%,100%{transform:translateY(0) rotate(0)}50%{transform:translateY(1px) rotate(2deg)}}
          @keyframes plr-sleep{0%,100%{transform:translateY(2px) rotate(1deg)}50%{transform:translateY(5px) rotate(-1deg)}}
          @keyframes plr-think{from{transform:rotate(-2deg) translateY(0)}to{transform:rotate(2deg) translateY(-2px)}}
          @keyframes plr-antenna{from{transform:rotate(-5deg)}to{transform:rotate(5deg)}}
          @keyframes plr-walk{from{transform:translateY(0) rotate(-3deg)}to{transform:translateY(-3px) rotate(3deg)}}
          @keyframes plr-fall{0%{transform:translateY(-4px) rotate(-4deg)}68%{transform:translateY(8px) rotate(13deg)}100%{transform:translateY(0) rotate(-3deg)}}
          @keyframes plr-impact{0%{transform:scale(1,1)}35%{transform:scale(1.16,.82)}65%{transform:scale(.94,1.06)}100%{transform:scale(1,1)}}
          @keyframes plr-sit{0%{transform:translateY(-6px)}55%{transform:translateY(3px) scale(1.02,.96)}100%{transform:translateY(0) scale(1,.98)}}
          @keyframes plr-hover-land{0%{transform:translateY(-12px)}48%{transform:translateY(-2px)}75%{transform:translateY(-6px)}100%{transform:translateY(0)}}
          @keyframes plr-annoyed{0%,100%{transform:translateX(0) rotate(0)}30%{transform:translateX(-2px) rotate(-4deg)}70%{transform:translateX(2px) rotate(4deg)}}
          @keyframes plr-zzz{0%{transform:translateY(5px) scale(.85);opacity:.2}40%{opacity:1}100%{transform:translateY(-15px) scale(1.08);opacity:0}}
          @keyframes plr-snore{0%,100%{transform:translate(0,0) scale(.9);opacity:.25}35%{transform:translate(2px,-4px) scale(1.08);opacity:1}70%{transform:translate(5px,-10px) scale(.95);opacity:.6}}
          @media(max-width:640px){#pl-live-robot .plr-character{width:78px;height:94px}#pl-live-robot .plr-speech{max-width:164px;font-size:11px}}

          /* Pose rig v11: animate SVG parts independently; keep layout position separate from character pose. */
          #pl-live-robot .plr-character{animation:none;transform-origin:50% 88%;}
          #pl-live-robot .plr-character .plr-art{transform-box:view-box;transform-origin:55px 112px;animation:plr-idle-bob 3.6s ease-in-out infinite;}
          #pl-live-robot .plr-character .plr-shadow{transform-box:fill-box;transform-origin:center;animation:plr-shadow-pulse 3.6s ease-in-out infinite;}
          #pl-live-robot .plr-character .plr-head{transform-box:view-box;transform-origin:55px 43px;transform:rotate(-4deg);transition:transform .18s ease;}
          #pl-live-robot .plr-character .plr-body{transform-box:view-box;transform-origin:55px 84px;transition:transform .16s ease;}
          #pl-live-robot .plr-character .plr-arm-near{transform-box:view-box;transform-origin:72px 73px;transition:transform .16s ease;}
          #pl-live-robot .plr-character .plr-arm-far{transform-box:view-box;transform-origin:38px 73px;transition:transform .16s ease;}
          #pl-live-robot .plr-character .plr-legs{transform-box:view-box;transform-origin:55px 99px;transition:transform .16s ease;}
          #pl-live-robot .plr-character.bored .plr-art{animation:plr-bored-body 2.5s ease-in-out infinite;}
          #pl-live-robot .plr-character.sleeping .plr-art{animation:plr-sleep-body 3.4s ease-in-out infinite;}
          #pl-live-robot .plr-character.thinking .plr-art{animation:plr-thinking-body .7s ease-in-out infinite alternate;}
          #pl-live-robot .plr-character.walking .plr-art{animation:plr-walk-body .23s ease-in-out infinite alternate;}
          #pl-live-robot .plr-character.carried .plr-art{animation:none;transform:rotate(-7deg) translateY(-2px);}
          #pl-live-robot .plr-character.carried .plr-arm-near{transform:rotate(-42deg) translateY(-2px);animation:none;}
          #pl-live-robot .plr-character.carried .plr-arm-far{transform:rotate(34deg) translateY(-2px);animation:none;}
          #pl-live-robot .plr-character.falling{animation:none!important;}
          #pl-live-robot .plr-character.falling .plr-art{animation:plr-face-first-fall .72s cubic-bezier(.42,.05,.72,.32) forwards;}
          #pl-live-robot .plr-character.falling .plr-head{animation:plr-head-dive .68s ease-in forwards;}
          #pl-live-robot .plr-character.falling .plr-arm-near{animation:plr-reach-near .66s ease-in forwards;}
          #pl-live-robot .plr-character.falling .plr-arm-far{animation:plr-reach-far .66s ease-in forwards;}
          #pl-live-robot .plr-character.falling .plr-legs{animation:plr-feet-kick .55s ease-in forwards;}
          #pl-live-robot .plr-character.falling .plr-fall-sweat{opacity:1;animation:plr-sweat-pop .72s ease-out forwards;}
          #pl-live-robot .plr-character.impact{animation:none!important;}
          #pl-live-robot .plr-character.impact .plr-art{animation:plr-faceplant-squash .28s cubic-bezier(.2,.75,.3,1) forwards;}
          #pl-live-robot .plr-character.impact .plr-arm-near{animation:plr-impact-near .28s ease-out forwards;}
          #pl-live-robot .plr-character.impact .plr-arm-far{animation:plr-impact-far .28s ease-out forwards;}
          #pl-live-robot .plr-character.recovering{animation:none!important;}
          #pl-live-robot .plr-character.recovering .plr-art{animation:plr-pushup-rise .92s cubic-bezier(.2,.75,.22,1) forwards;}
          #pl-live-robot .plr-character.recovering .plr-body{animation:plr-body-pushup .92s ease-in-out forwards;}
          #pl-live-robot .plr-character.recovering .plr-head{animation:plr-head-recover .92s cubic-bezier(.2,.75,.22,1) forwards;}
          #pl-live-robot .plr-character.recovering .plr-arm-near{animation:plr-pushup-near .92s cubic-bezier(.25,.7,.2,1) forwards;}
          #pl-live-robot .plr-character.recovering .plr-arm-far{animation:plr-pushup-far .92s cubic-bezier(.25,.7,.2,1) forwards;}
          #pl-live-robot .plr-character.recovering .plr-legs{animation:plr-legs-recover .92s ease-out forwards;}
          #pl-live-robot .plr-character.annoyed{animation:none!important;}
          #pl-live-robot .plr-character.annoyed .plr-art{animation:plr-annoyed-shimmy .36s ease-in-out 3;}
          #pl-live-robot .plr-character.annoyed .plr-arm-near{animation:plr-angry-near .5s cubic-bezier(.2,.8,.2,1) both;}
          #pl-live-robot .plr-character.annoyed .plr-arm-far{animation:plr-angry-far .5s cubic-bezier(.2,.8,.2,1) both;}
          #pl-live-robot .plr-character.annoyed .plr-head{animation:plr-angry-head .35s ease-out both;}
          #pl-live-robot .plr-character.confused{animation:none!important;}
          #pl-live-robot .plr-character.confused .plr-art{animation:plr-confused-tilt .55s ease-in-out 2;}
          #pl-live-robot .plr-character.confused .plr-arm-near{animation:plr-angry-near .5s ease-out both;}
          #pl-live-robot .plr-character.confused .plr-arm-far{animation:plr-angry-far .5s ease-out both;}
          #pl-live-robot .plr-character.sitting{animation:none!important;}
          #pl-live-robot .plr-character.sitting .plr-legs{transform:translateY(2px) scaleY(.96);}
          #pl-live-robot .plr-character.hover-land{animation:none!important;}
          #pl-live-robot .plr-character.hover-land .plr-art{animation:plr-hover-soft .72s ease-out both;}
          #pl-live-robot .plr-character .plr-snore{opacity:0;}
          #pl-live-robot .plr-character.sleeping .plr-snore{opacity:1;animation:plr-snore 2.1s ease-in-out infinite;}
          @keyframes plr-idle-bob{0%,100%{transform:translateY(0) rotate(-1deg)}50%{transform:translateY(-3px) rotate(1deg)}}
          @keyframes plr-shadow-pulse{0%,100%{transform:scaleX(1);opacity:.17}50%{transform:scaleX(.84);opacity:.1}}
          @keyframes plr-bored-body{0%,100%{transform:translateY(0) rotate(0)}50%{transform:translateY(1px) rotate(2deg)}}
          @keyframes plr-sleep-body{0%,100%{transform:translateY(2px) rotate(2deg)}50%{transform:translateY(5px) rotate(-2deg)}}
          @keyframes plr-thinking-body{from{transform:rotate(-2deg) translateY(0)}to{transform:rotate(2deg) translateY(-2px)}}
          @keyframes plr-walk-body{from{transform:translateY(0) rotate(-3deg)}to{transform:translateY(-3px) rotate(3deg)}}
          @keyframes plr-face-first-fall{0%{transform:translateY(-2px) rotate(-4deg) scale(1,1)}48%{transform:translateY(7px) rotate(42deg) scale(.99,.98)}78%{transform:translateY(13px) rotate(76deg) scale(1.06,.88)}100%{transform:translateY(10px) rotate(68deg) scale(1.03,.94)}}
          @keyframes plr-head-dive{0%{transform:rotate(-4deg)}60%{transform:rotate(25deg)}100%{transform:rotate(30deg)}}
          @keyframes plr-reach-near{0%{transform:rotate(0)}72%{transform:rotate(-76deg)}100%{transform:rotate(-68deg)}}
          @keyframes plr-reach-far{0%{transform:rotate(0)}72%{transform:rotate(72deg)}100%{transform:rotate(64deg)}}
          @keyframes plr-feet-kick{0%{transform:rotate(0)}65%{transform:rotate(-20deg)}100%{transform:rotate(-9deg)}}
          @keyframes plr-sweat-pop{0%{opacity:0;transform:translateY(-2px)}45%{opacity:1}100%{opacity:0;transform:translateY(9px)}}
          @keyframes plr-faceplant-squash{0%{transform:translateY(10px) rotate(68deg) scale(1.03,.94)}40%{transform:translateY(15px) rotate(72deg) scale(1.15,.62)}68%{transform:translateY(9px) rotate(62deg) scale(.96,1.05)}100%{transform:translateY(10px) rotate(68deg) scale(1.02,.94)}}
          @keyframes plr-impact-near{0%{transform:rotate(-68deg)}100%{transform:rotate(-52deg)}}
          @keyframes plr-impact-far{0%{transform:rotate(64deg)}100%{transform:rotate(50deg)}}
          @keyframes plr-pushup-rise{0%{transform:translateY(10px) rotate(66deg) scale(1.02,.94)}25%{transform:translateY(8px) rotate(48deg) scale(1,.96)}55%{transform:translateY(-5px) rotate(12deg) scale(.98,1.02)}78%{transform:translateY(-2px) rotate(-5deg)}100%{transform:translateY(0) rotate(-1deg) scale(1,1)}}
          @keyframes plr-body-pushup{0%{transform:translateY(3px) scaleY(.9)}30%{transform:translateY(1px) scaleY(.96)}65%{transform:translateY(-2px) scaleY(1.03)}100%{transform:translateY(0) scaleY(1)}}
          @keyframes plr-head-recover{0%{transform:rotate(28deg)}50%{transform:rotate(-12deg)}100%{transform:rotate(-4deg)}}
          @keyframes plr-pushup-near{0%{transform:rotate(-52deg)}34%{transform:rotate(48deg)}67%{transform:rotate(33deg)}100%{transform:rotate(0)}}
          @keyframes plr-pushup-far{0%{transform:rotate(50deg)}34%{transform:rotate(-48deg)}67%{transform:rotate(-33deg)}100%{transform:rotate(0)}}
          @keyframes plr-legs-recover{0%{transform:translateY(2px) rotate(-14deg)}55%{transform:translateY(-1px) rotate(7deg)}100%{transform:translateY(0) rotate(0)}}
          @keyframes plr-angry-near{0%{transform:rotate(0)}65%{transform:rotate(-122deg)}100%{transform:rotate(-112deg)}}
          @keyframes plr-angry-far{0%{transform:rotate(0)}65%{transform:rotate(116deg)}100%{transform:rotate(108deg)}}
          @keyframes plr-angry-head{0%{transform:rotate(-4deg)}60%{transform:rotate(-10deg)}100%{transform:rotate(-7deg)}}
          @keyframes plr-annoyed-shimmy{0%,100%{transform:translateX(0) rotate(-1deg)}35%{transform:translateX(-2px) rotate(-3deg)}70%{transform:translateX(2px) rotate(2deg)}}
          @keyframes plr-confused-tilt{0%,100%{transform:rotate(-1deg)}50%{transform:rotate(7deg)}}
          @keyframes plr-hover-soft{0%{transform:translateY(-10px)}50%{transform:translateY(-2px)}100%{transform:translateY(0)}}
          @keyframes plr-breathe{0%,100%{transform:scale(1,1)}50%{transform:scale(1.018,.992)}}
          @keyframes plr-head-curious{0%,100%{transform:rotate(0)}25%{transform:rotate(-9deg) translate(-1px,1px)}55%{transform:rotate(5deg) translate(1px,0)}76%{transform:rotate(-3deg)}}
          @keyframes plr-stretch-body{0%,100%{transform:translateY(0) rotate(0)}25%{transform:translateY(-3px) rotate(-2deg)}55%{transform:translateY(-6px) rotate(1deg) scale(1.02,1.025)}78%{transform:translateY(-2px) rotate(-1deg)}}
          @keyframes plr-stretch-near{0%,100%{transform:rotate(0)}28%{transform:rotate(-28deg) translateY(-2px)}58%{transform:rotate(-48deg) translateY(-5px)}82%{transform:rotate(-18deg)}}
          @keyframes plr-stretch-far{0%,100%{transform:rotate(0)}28%{transform:rotate(26deg) translateY(-2px)}58%{transform:rotate(43deg) translateY(-4px)}82%{transform:rotate(14deg)}}
          @keyframes plr-stretch-legs{0%,100%{transform:translateY(0)}45%{transform:translateY(2px) scaleY(.97)}75%{transform:translateY(-1px)}}
          @keyframes plr-cheer-body{0%,100%{transform:translateY(0) rotate(0)}20%{transform:translateY(1px) scale(.98,1.02)}48%{transform:translateY(-7px) rotate(-3deg) scale(1.02,1.02)}72%{transform:translateY(-2px) rotate(2deg)}88%{transform:translateY(-3px)}}
          @keyframes plr-scan-line{0%{transform:translateY(-4px);opacity:0}15%{opacity:.95}80%{opacity:.95}100%{transform:translateY(17px);opacity:0}}
          @keyframes plr-high-hover{0%{transform:translateY(0) rotate(0)}28%{transform:translateY(-7px) rotate(-2deg)}58%{transform:translateY(-10px) rotate(1deg)}78%{transform:translateY(-5px) rotate(0)}100%{transform:translateY(0) rotate(0)}}
          @keyframes plr-sparkle-burst{0%{opacity:0;transform:scale(.55) rotate(-10deg)}25%{opacity:1;transform:scale(1.1) rotate(6deg)}65%{opacity:.86;transform:scale(1) rotate(-5deg)}100%{opacity:0;transform:scale(.82) rotate(10deg)}}

          /* ProofLoop v16: stronger, visible movement and twin-engine hover effects. */
          #pl-live-robot .plr-character{width:98px;height:118px;overflow:visible;}
          #pl-live-robot .plr-character .plr-art{animation:plr-home-float 2.8s cubic-bezier(.37,0,.63,1) infinite;}
          #pl-live-robot .plr-character.home-hover .plr-art{animation:plr-home-float 2.8s cubic-bezier(.37,0,.63,1) infinite;}
          #pl-live-robot .plr-character.booting .plr-art{animation:plr-boot-art 1.9s cubic-bezier(.2,.75,.22,1) both;}
          #pl-live-robot .plr-character.idle-drift .plr-art{animation:plr-high-hover 1.45s cubic-bezier(.25,.7,.25,1) both;}
          #pl-live-robot .plr-character.idle-scan .face-normal{display:none;}
          #pl-live-robot .plr-character.idle-scan .face-curious{display:block;}
          #pl-live-robot .plr-character.idle-stretch .plr-eye{animation:plr-eye-squint .7s ease-in-out 1;}
          #pl-live-robot .plr-engine{position:absolute;z-index:0;bottom:5px;width:13px;height:25px;border-radius:55% 55% 70% 70%;opacity:0;pointer-events:none;transform-origin:50% 0;background:linear-gradient(180deg,rgba(255,255,255,.98) 0%,#D5F8FF 15%,#78EDEB 38%,#8B85FF 70%,rgba(149,130,255,.1) 100%);filter:drop-shadow(0 0 5px rgba(133,137,255,.82));}
          #pl-live-robot .plr-engine-left{left:31%;}
          #pl-live-robot .plr-engine-right{right:31%;}
          #pl-live-robot .plr-character.home-hover .plr-engine{opacity:.92;animation:plr-engine-flare .26s ease-in-out infinite alternate;}
          #pl-live-robot .plr-character.booting .plr-engine{opacity:1;animation:plr-engine-ignite .23s ease-in-out 7 alternate;}
          #pl-live-robot .plr-smoke{position:absolute;z-index:2;bottom:0;width:9px;height:9px;border-radius:50%;opacity:0;pointer-events:none;background:radial-gradient(circle at 32% 30%,rgba(255,255,255,.8),rgba(195,199,235,.62) 38%,rgba(164,157,235,0) 75%);filter:blur(.25px);}
          #pl-live-robot .plr-smoke-left{left:29%;}
          #pl-live-robot .plr-smoke-mid{left:47%;width:7px;height:7px;animation-delay:.42s!important;}
          #pl-live-robot .plr-smoke-right{right:28%;width:11px;height:11px;animation-delay:.76s!important;}
          #pl-live-robot .plr-character.home-hover .plr-smoke{opacity:.4;animation:plr-smoke-lift 1.65s ease-out infinite;}
          #pl-live-robot .plr-character.booting .plr-smoke{opacity:.65;animation:plr-smoke-lift .64s ease-out 3;}
          #pl-live-robot .plr-character.carried .plr-engine,#pl-live-robot .plr-character.carried .plr-smoke,#pl-live-robot .plr-character.falling .plr-engine,#pl-live-robot .plr-character.falling .plr-smoke{opacity:0!important;animation:none!important;}
          #pl-live-robot .plr-character.sitting .plr-art{animation:plr-sit-art .42s ease-out forwards;transform-origin:55px 112px;}
          #pl-live-robot .plr-character.home-hover:before{left:calc(50% - 23px);bottom:-20px;width:46px;height:32px;opacity:.72;filter:blur(2px);}
          #pl-live-robot .plr-character.home-hover:after{left:calc(50% - 24px);bottom:-38px;width:48px;height:40px;opacity:.54;}
          @keyframes plr-home-float{0%,100%{transform:translateY(0) rotate(-1deg)}24%{transform:translateY(-5px) rotate(-1.6deg)}52%{transform:translateY(-10px) rotate(1.2deg)}78%{transform:translateY(-4px) rotate(.3deg)}}
          @keyframes plr-boot-art{0%{transform:translate(0,2px) rotate(-2deg) scale(.97)}12%{transform:translate(-3px,-1px) rotate(4deg) scale(1.01)}24%{transform:translate(3px,1px) rotate(-5deg)}36%{transform:translate(-2px,-2px) rotate(3deg)}50%{transform:translate(2px,0) rotate(-2deg)}66%{transform:translate(-1px,-5px) rotate(1deg)}82%{transform:translateY(-7px) rotate(-.8deg)}100%{transform:translateY(-5px) rotate(-1deg)}}
          @keyframes plr-engine-flare{from{transform:scaleY(.68) scaleX(.8);filter:drop-shadow(0 0 3px rgba(133,137,255,.66));}to{transform:scaleY(1.22) scaleX(1.05);filter:drop-shadow(0 0 8px rgba(157,156,255,1));}}
          @keyframes plr-engine-ignite{0%{transform:scaleY(.4) scaleX(.62);opacity:.3}55%{transform:scaleY(1.6) scaleX(1.2);opacity:1}100%{transform:scaleY(.82) scaleX(.82);opacity:.9}}
          @keyframes plr-smoke-lift{0%{transform:translateY(0) translateX(0) scale(.42);opacity:0}20%{opacity:.7}65%{transform:translateY(18px) translateX(3px) scale(1.1);opacity:.34}100%{transform:translateY(27px) translateX(-2px) scale(1.55);opacity:0}}
          @keyframes plr-eye-squint{0%,100%{transform:scaleY(1)}50%{transform:scaleY(.2)}}
          @keyframes plr-sit-art{0%{transform:translateY(-4px) scale(1)}55%{transform:translateY(2px) scale(.94,.9)}100%{transform:translateY(2px) scale(.92,.9)}}
          @media(max-width:640px){#pl-live-robot .plr-character{width:78px;height:94px}}

          /* v17: smaller companion scale + playful idle personality beats. */
          #pl-live-robot .plr-character{width:98px;height:118px;filter:drop-shadow(0 9px 8px rgba(5,8,31,.28)) drop-shadow(0 0 9px rgba(120,126,255,.10));}
          #pl-live-robot .plr-character:hover{filter:drop-shadow(0 10px 8px rgba(5,8,31,.3)) drop-shadow(0 0 15px rgba(117,234,240,.25));}
          #pl-live-robot .plr-character svg{filter:drop-shadow(0 0 2px rgba(180,193,255,.13));}
          #pl-live-robot .plr-character .plr-eye{filter:drop-shadow(0 0 2px rgba(119,244,255,.7));}
          #pl-live-robot .plr-character.idle-goofy{animation:plr-goofy-wrapper 1.55s cubic-bezier(.24,.72,.2,1) both;}
          #pl-live-robot .plr-character.idle-goofy .plr-art{animation:plr-goofy-bounce 1.55s cubic-bezier(.2,.75,.25,1) both;transform-origin:55px 78px;}
          #pl-live-robot .plr-character.idle-goofy .plr-arm-near{animation:plr-goofy-arm .28s ease-in-out 4 alternate;}
          #pl-live-robot .plr-character.idle-goofy .plr-head{animation:plr-head-curious .95s ease-in-out both;}
          #pl-live-robot .plr-character.idle-goofy .face-normal,#pl-live-robot .plr-character.idle-dance .face-normal{display:none;}
          #pl-live-robot .plr-character.idle-goofy .face-delight,#pl-live-robot .plr-character.idle-dance .face-delight{display:block;}
          #pl-live-robot .plr-character.idle-goofy .plr-idle-sparkles,#pl-live-robot .plr-character.idle-dance .plr-idle-sparkles{opacity:1;animation:plr-sparkle-burst 1.4s ease-out both;}
          #pl-live-robot .plr-character.idle-dance{animation:plr-dance-wrapper 1.62s ease-in-out both;}
          #pl-live-robot .plr-character.idle-dance .plr-art{animation:plr-dance-bob 1.35s cubic-bezier(.2,.75,.25,1) both;transform-origin:55px 86px;}
          #pl-live-robot .plr-character.idle-dance .plr-arm-near{animation:plr-dance-arm .34s ease-in-out 4 alternate;}
          #pl-live-robot .plr-character.idle-dance .plr-arm-far{animation:plr-dance-arm-reverse .34s ease-in-out 4 alternate;}
          #pl-live-robot .plr-character.idle-dance .plr-legs{animation:plr-dance-feet .34s ease-in-out 4 alternate;}
          #pl-live-robot .plr-character.idle-propeller .antenna-near{transform-box:fill-box;transform-origin:center;animation:plr-propeller  .24s linear 6;}
          #pl-live-robot .plr-character.idle-propeller .plr-art{animation:plr-propeller-bob 1.55s ease-out both;}
          #pl-live-robot .plr-character.idle-propeller .plr-engine{opacity:1;animation:plr-engine-ignite .20s ease-in-out 5 alternate;}
          #pl-live-robot .plr-character.idle-propeller .plr-smoke{opacity:.6;animation:plr-smoke-lift .72s ease-out 3;}
          #pl-live-robot .plr-character.idle-propeller .face-normal{display:none;}
          #pl-live-robot .plr-character.idle-propeller .face-confused{display:block;}
          #pl-live-robot .plr-engine{background:linear-gradient(180deg,#FFF 0%,#C7FBFF 17%,#7DEDE8 42%,#9690FF 73%,rgba(149,130,255,.03) 100%);filter:drop-shadow(0 0 6px rgba(132,142,255,.75));}
          #pl-live-robot .plr-character.home-hover .plr-engine{opacity:.9;animation:plr-engine-flare .33s ease-in-out infinite alternate;}
          #pl-live-robot .plr-character.booting .plr-engine{opacity:1;animation:plr-engine-ignite .23s ease-in-out 7 alternate;}
          #pl-live-robot .plr-speech{background:linear-gradient(145deg,var(--plr-surface),var(--plr-card))!important;color:var(--plr-ink)!important;border-color:var(--plr-border)!important;box-shadow:0 12px 28px rgba(30,34,82,.16),0 0 16px rgba(119,144,255,.10);}
          #pl-live-robot .plr-speech:after{background:var(--plr-surface)!important;border-color:var(--plr-border)!important;}
          #pl-live-robot .plr-hide{background:var(--plr-surface)!important;color:var(--plr-ink)!important;border-color:var(--plr-border)!important;}
          #pl-live-robot[data-theme="light"] .plr-character{filter:drop-shadow(0 7px 6px rgba(68,76,144,.23)) drop-shadow(0 0 10px rgba(114,126,232,.20));}
          #pl-live-robot[data-theme="light"] #plr-shell stop:nth-child(1){stop-color:#FFFFFF!important;}
          #pl-live-robot[data-theme="light"] #plr-shell stop:nth-child(2){stop-color:#DDE2FF!important;}
          #pl-live-robot[data-theme="light"] #plr-shell stop:nth-child(3){stop-color:#929BE0!important;}
          #pl-live-robot[data-theme="light"] #plr-teal stop:nth-child(1){stop-color:#B8FFF2!important;}
          #pl-live-robot[data-theme="light"] #plr-teal stop:nth-child(2){stop-color:#A3BBFF!important;}
          #pl-live-robot[data-theme="light"] #plr-teal stop:nth-child(3){stop-color:#7E87D7!important;}
          #pl-live-robot[data-theme="light"] #plr-screen stop:nth-child(1){stop-color:#1B3152!important;}
          #pl-live-robot[data-theme="light"] #plr-screen stop:nth-child(2){stop-color:#31587D!important;}
          #pl-live-robot[data-theme="light"] .plr-eye{fill:#FFD68A!important;filter:drop-shadow(0 0 3px rgba(255,205,117,.72));}
          @keyframes plr-goofy-wrapper{0%,100%{transform:rotate(0)}12%{transform:rotate(-12deg) translateY(-2px)}26%{transform:rotate(15deg) translateY(-5px)}40%{transform:rotate(-16deg) translateY(-3px)}55%{transform:rotate(12deg) translateY(-8px)}70%{transform:rotate(-7deg) translateY(-2px)}84%{transform:rotate(4deg)} }
          @keyframes plr-goofy-bounce{0%,100%{transform:translateY(0) rotate(0)}20%{transform:translateY(-5px) rotate(-7deg)}40%{transform:translateY(-1px) rotate(8deg)}62%{transform:translateY(-8px) rotate(-6deg)}80%{transform:translateY(-2px) rotate(3deg)} }
          @keyframes plr-goofy-arm{from{transform:rotate(-18deg)}to{transform:rotate(42deg) translateY(-2px)}}
          @keyframes plr-dance-wrapper{0%,100%{transform:rotate(0) translateY(0)}18%{transform:rotate(-8deg) translateY(-2px)}36%{transform:rotate(9deg) translateY(-4px)}54%{transform:rotate(-8deg) translateY(-1px)}72%{transform:rotate(7deg) translateY(-5px)}90%{transform:rotate(-2deg)} }
          @keyframes plr-dance-bob{0%,100%{transform:translateY(0) scale(1)}20%{transform:translateY(-5px) scale(1.02,.98)}40%{transform:translateY(1px) scale(.98,1.02)}60%{transform:translateY(-7px) scale(1.02,.98)}80%{transform:translateY(0) scale(.99,1.01)} }
          @keyframes plr-dance-arm{from{transform:rotate(-36deg)}to{transform:rotate(28deg)}}
          @keyframes plr-dance-arm-reverse{from{transform:rotate(30deg)}to{transform:rotate(-34deg)}}
          @keyframes plr-dance-feet{from{transform:translateY(0) rotate(-5deg)}to{transform:translateY(-2px) rotate(7deg)}}
          @keyframes plr-propeller{from{transform:rotate(-38deg)}to{transform:rotate(38deg)}}
          @keyframes plr-propeller-bob{0%,100%{transform:translateY(0) rotate(0)}22%{transform:translateY(-8px) rotate(-4deg)}44%{transform:translateY(-3px) rotate(5deg)}62%{transform:translateY(-12px) rotate(-4deg)}78%{transform:translateY(-1px) rotate(4deg)} }
          @media(max-width:640px){#pl-live-robot .plr-character{width:78px;height:94px}#pl-live-robot .plr-speech{max-width:164px;font-size:11px}}
          @media(prefers-reduced-motion:reduce){#pl-live-robot *,#pl-live-robot *:before,#pl-live-robot *:after{animation-duration:.01ms!important;animation-iteration-count:1!important;transition-duration:.01ms!important}}
        `;
        pd.head.appendChild(style);
        root = pd.createElement('div'); root.id = 'pl-live-robot'; root.dataset.plVersion = '19';
        root.innerHTML = `
          <div class="plr-character" id="plr-character" role="button" tabindex="0" aria-label="Interactive ProofLoop robot. Drag me to supported landing areas. I fall face-first, push myself up, and react when dropped. Click to wave.">
            <span class="plr-engine plr-engine-left" aria-hidden="true"></span><span class="plr-engine plr-engine-right" aria-hidden="true"></span>
            <span class="plr-smoke plr-smoke-left" aria-hidden="true"></span><span class="plr-smoke plr-smoke-mid" aria-hidden="true"></span><span class="plr-smoke plr-smoke-right" aria-hidden="true"></span>
            <svg viewBox="0 0 110 132" aria-hidden="true" xmlns="http://www.w3.org/2000/svg">
              <defs>
                <linearGradient id="plr-shell" x1="25" y1="12" x2="82" y2="103" gradientUnits="userSpaceOnUse"><stop stop-color="#F4F0FF"/><stop offset=".52" stop-color="#B6B9F6"/><stop offset="1" stop-color="#686AB9"/></linearGradient>
                <linearGradient id="plr-teal" x1="27" y1="25" x2="83" y2="103" gradientUnits="userSpaceOnUse"><stop stop-color="#86F4E8"/><stop offset=".52" stop-color="#9B9BFF"/><stop offset="1" stop-color="#6265C4"/></linearGradient>
                <linearGradient id="plr-screen" x1="38" y1="16" x2="78" y2="53" gradientUnits="userSpaceOnUse"><stop stop-color="#14152F"/><stop offset="1" stop-color="#292950"/></linearGradient>
                <linearGradient id="plr-cheek" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#FFB6BD"/><stop offset="1" stop-color="#FF8F9C"/></linearGradient>
              </defs>
              <g class="plr-art">
                <ellipse class="plr-shadow" cx="55" cy="123" rx="26" ry="4.6" fill="#06121B" opacity=".17"/>
                <g class="plr-legs">
                  <path d="M39 96Q29 103 32 113Q34 120 45 119L54 112L50 98Z" fill="url(#plr-shell)" stroke="#4D4F88" stroke-width="1.2"/>
                  <path d="M59 97Q54 107 61 116Q67 121 77 116Q83 112 76 102L69 96Z" fill="url(#plr-shell)" stroke="#4D4F88" stroke-width="1.2"/>
                  <path d="M35 112Q41 116 49 112L48 117Q40 121 34 117Z" fill="url(#plr-teal)"/>
                  <path d="M63 112Q71 117 78 111L80 116Q71 122 63 117Z" fill="url(#plr-teal)"/>
                </g>
                <g class="plr-arm-far">
                  <path d="M38 70Q28 72 25 82L28 92Q32 96 36 89L44 79Z" fill="url(#plr-shell)" stroke="#4D4F88" stroke-width="1.2" stroke-linejoin="round"/>
                  <path d="M28 89Q22 90 23 96Q25 102 32 100Q37 97 34 92Z" fill="url(#plr-teal)" stroke="#4D4F88" stroke-width=".9"/>
                  <path d="M25 95l4 2" stroke="#E7FFFC" stroke-width="1.4" stroke-linecap="round"/>
                </g>
                <g class="plr-body">
                  <path d="M34 65Q46 59 66 66Q79 70 80 88L74 106Q56 117 38 106L29 91Q27 77 34 65Z" fill="url(#plr-shell)" stroke="#4D4F88" stroke-width="1.3" stroke-linejoin="round"/>
                  <path d="M39 77Q54 71 70 78L69 99Q56 108 42 99Z" fill="url(#plr-teal)" stroke="var(--plr-accent)" stroke-width="1.1"/>
                  <path d="M43 79L55 87L64 79" fill="none" stroke="#ECFFFC" stroke-width="2.1" stroke-linecap="round" stroke-linejoin="round" opacity=".92"/>
                  <circle cx="56" cy="94" r="2.1" fill="#E4FFFB" opacity=".86"/>
                  <path d="M45 104Q56 109 66 103" fill="none" stroke="#93B6BB" stroke-width="1" opacity=".55"/>
                </g>
                <g class="plr-arm-near">
                  <path d="M70 70Q81 71 85 82L83 92Q79 96 75 89L67 80Z" fill="url(#plr-shell)" stroke="#4D4F88" stroke-width="1.2" stroke-linejoin="round"/>
                  <path d="M78 89Q85 88 87 94Q87 101 80 101Q74 99 76 93Z" fill="url(#plr-teal)" stroke="#4D4F88" stroke-width=".9"/>
                  <path d="M79 94l4 1" stroke="#E7FFFC" stroke-width="1.4" stroke-linecap="round"/>
                </g>
                <g class="plr-head">
                  <g class="antenna-far"><path d="M69 17L74 5Q77 1 81 4L86 14L82 23Z" fill="url(#plr-shell)" stroke="#4D4F88" stroke-width="1.2"/><path d="M77 13L81 8L83 15L80 20Z" fill="url(#plr-teal)"/></g>
                  <g class="antenna-near"><path d="M29 34L21 19Q19 14 23 11Q27 9 30 14L38 29Z" fill="url(#plr-shell)" stroke="#4D4F88" stroke-width="1.2"/><path d="M23 17Q27 16 30 23L34 29L29 31Z" fill="url(#plr-teal)"/></g>
                  <path d="M31 20Q39 10 56 11L73 15Q84 21 83 34L79 48Q75 57 62 59L43 56Q30 52 28 41Q26 29 31 20Z" fill="url(#plr-shell)" stroke="#4D4F88" stroke-width="1.4" stroke-linejoin="round"/>
                  <path d="M37 23Q48 16 63 18L74 22Q79 27 76 37L72 45Q67 51 55 49L42 46Q34 43 34 34Q33 27 37 23Z" fill="url(#plr-screen)" stroke="var(--plr-accent)" stroke-width="1.9"/>
                  <g class="face-normal">
                    <ellipse class="plr-eye" cx="48" cy="31" rx="5.25" ry="6.65" fill="#87F2FF"/>
                    <ellipse class="plr-eye" cx="64" cy="29.5" rx="4.1" ry="5.5" fill="#87F2FF"/>
                    <circle class="plr-eye-glint" cx="46.4" cy="28.6" r="1.75" fill="#FFFFFF"/><circle class="plr-eye-glint" cx="62.8" cy="27.2" r="1.45" fill="#FFFFFF"/>
                    <path d="M52.5 40Q58 44 63.5 39.5" fill="none" stroke="#FF827B" stroke-width="3.2" stroke-linecap="round"/>
                    <ellipse cx="40.5" cy="39.5" rx="3.2" ry="2" fill="url(#plr-cheek)" opacity=".92"/>
                    <ellipse cx="68.5" cy="38" rx="2.6" ry="1.7" fill="url(#plr-cheek)" opacity=".85"/>
                  </g>
                  <g class="face-bored">
                    <path d="M43 32Q48 35 52 31M60 30Q64 33 68 29" fill="none" stroke="#87F2FF" stroke-width="3.5" stroke-linecap="round"/>
                    <path d="M54 41L62 40" stroke="#FF8F84" stroke-width="2.8" stroke-linecap="round"/>
                    <ellipse cx="41" cy="39" rx="3" ry="1.7" fill="url(#plr-cheek)"/>
                  </g>
                  <g class="face-sleep">
                    <path d="M43 32Q48 37 52 32M60 30Q64 35 68 30" fill="none" stroke="#87F2FF" stroke-width="3" stroke-linecap="round"/>
                    <path d="M54 41q4 3 7 0" fill="none" stroke="#FF8F84" stroke-width="2.5" stroke-linecap="round"/>
                    <ellipse cx="41" cy="39" rx="3.3" ry="1.8" fill="url(#plr-cheek)"/>
                  </g>
                  <g class="face-annoyed">
                    <path d="M42 25L52 29M61 27L69 22" fill="none" stroke="#87F2FF" stroke-width="2.9" stroke-linecap="round"/>
                    <ellipse cx="48.5" cy="32" rx="4.1" ry="4.6" fill="#87F2FF"/><ellipse cx="64" cy="30.3" rx="3.2" ry="3.8" fill="#87F2FF"/>
                    <circle cx="47.2" cy="30.5" r="1.2" fill="#FFFFFF"/><circle cx="63" cy="29" r="1" fill="#FFFFFF"/>
                    <path d="M53 42Q58 38 64 42" fill="none" stroke="#FF8F84" stroke-width="3.1" stroke-linecap="round"/>
                    <ellipse cx="40.5" cy="39" rx="3.8" ry="2.2" fill="url(#plr-cheek)"/><ellipse cx="69" cy="37.5" rx="3.2" ry="2" fill="url(#plr-cheek)"/>
                    <path d="M37 21l-3-3M72 18l3-4" stroke="#FFB4BB" stroke-width="1.5" stroke-linecap="round"/>
                  </g>
                  <g class="face-confused">
                    <ellipse cx="48" cy="31" rx="4.4" ry="5.6" fill="#87F2FF"/><circle cx="47" cy="29" r="1.4" fill="#FFFFFF"/>
                    <path d="M60 28q4-5 8-1" fill="none" stroke="#87F2FF" stroke-width="3" stroke-linecap="round"/>
                    <path d="M54 42q4-4 8 0" fill="none" stroke="#FF8F84" stroke-width="2.7" stroke-linecap="round"/>
                    <ellipse cx="41" cy="39" rx="3" ry="1.7" fill="url(#plr-cheek)"/>
                  </g>
                  <g class="face-delight">
                    <path d="M42.5 32Q47.5 25 52 32" fill="none" stroke="#9CF6FF" stroke-width="3.4" stroke-linecap="round"/>
                    <path d="M59 30Q63.5 23 68 30" fill="none" stroke="#9CF6FF" stroke-width="3.4" stroke-linecap="round"/>
                    <path d="M50.5 38Q58.5 48 66 38" fill="none" stroke="#A0F5E8" stroke-width="3.1" stroke-linecap="round"/>
                    <ellipse cx="40.5" cy="39" rx="4" ry="2.5" fill="url(#plr-cheek)"/><ellipse cx="69" cy="37.5" rx="3.5" ry="2.2" fill="url(#plr-cheek)"/>
                    <path d="M38 26l-3-3M72 24l3-3" stroke="#8BF3EF" stroke-width="1.4" stroke-linecap="round"/>
                  </g>
                  <g class="face-curious">
                    <ellipse cx="48" cy="31" rx="5.4" ry="6.2" fill="#86ECF2"/><circle cx="49.2" cy="29.5" r="1.8" fill="#FFFFFF"/>
                    <ellipse cx="64" cy="30" rx="3.8" ry="4.6" fill="#86ECF2"/><circle cx="64.8" cy="28.5" r="1.2" fill="#FFFFFF"/>
                    <path d="M43 23l8-1M61 24l7 1" stroke="#9AF2F0" stroke-width="1.6" stroke-linecap="round"/>
                    <ellipse cx="58" cy="41.5" rx="2.2" ry="2.7" fill="#FF9A9A"/>
                    <ellipse cx="40.5" cy="39" rx="3.2" ry="1.8" fill="url(#plr-cheek)"/>
                  </g>
                </g>
                <g class="plr-fall-sweat" fill="#7FE8ED" opacity="0"><path d="M88 34Q82 42 86 45Q91 44 88 34Z"/><path d="M20 39Q15 46 19 48Q24 46 20 39Z"/></g>
                <g class="plr-z" fill="var(--plr-accent)" font-family="Trebuchet MS,sans-serif" font-size="12" font-weight="800"><text x="82" y="13">z</text><text x="89" y="7" font-size="9">z</text></g>
                <g class="plr-snore" fill="#F59ECA" font-family="Trebuchet MS,sans-serif" font-size="8" font-weight="800"><text x="5" y="58">hmm…</text><text x="8" y="48" font-size="6">snrr</text></g>
                <path class="plr-scan-line" d="M38 26H73" fill="none"/>
                <g class="plr-idle-sparkles" fill="#C9C5FF" stroke="#F8F7FF" stroke-width=".45">
                  <path d="M15 47l2.4 6.1 6.1 2.4-6.1 2.4-2.4 6.1-2.4-6.1-6.1-2.4 6.1-2.4Z"/>
                  <path d="M92 61l1.7 4.3 4.3 1.7-4.3 1.7-1.7 4.3-1.7-4.3-4.3-1.7 4.3-1.7Z"/>
                  <path d="M88 19l1.4 3.2 3.2 1.4-3.2 1.4-1.4 3.2-1.4-3.2-3.2-1.4 3.2-1.4Z"/>
                </g>
              </g>
            </svg>
          </div>
          <div class="plr-speech" id="plr-speech" role="status" aria-live="polite"></div>
          <button class="plr-hide" id="plr-hide" type="button" title="Return Loop to home" aria-label="Return Loop to its home position">×</button>`;
        pd.body.appendChild(root);
      }

      root.style.display = 'block';
      root.style.setProperty('--plr-bg', colors.bg);
      root.style.setProperty('--plr-surface', colors.surface);
      root.style.setProperty('--plr-card', colors.card);
      root.style.setProperty('--plr-border', colors.border);
      root.style.setProperty('--plr-ink', colors.ink);
      root.style.setProperty('--plr-muted', colors.muted);
      root.style.setProperty('--plr-accent', colors.accent);
      root.style.setProperty('--plr-accent-soft', colors.accentSoft);
      const robot = root.querySelector('#plr-character');
      const speech = root.querySelector('#plr-speech');
      const previousStatus = root.dataset.status || '';
      const statusChanged = previousStatus !== status;
      root.dataset.status = status;

      // New iframe execution gets a fresh, fully wired controller. AbortController
      // reliably removes listeners from the parent document when another rerun occurs.
      const lifecycle = new pd.defaultView.AbortController();
      const runtimeTimers = new Set();
      let anchorObserver = null;
      let runtimeDisposed = false;
      function later(fn, delay) {
        const timerId = pd.defaultView.setTimeout(() => {
          runtimeTimers.delete(timerId);
          if (!runtimeDisposed && !lifecycle.signal.aborted) fn();
        }, delay);
        runtimeTimers.add(timerId);
        return timerId;
      }
      function cancelTimer(timerId) {
        if (timerId !== undefined && timerId !== null) {
          pd.defaultView.clearTimeout(timerId);
          runtimeTimers.delete(timerId);
        }
      }
      function destroyRuntime() {
        if (runtimeDisposed) return;
        runtimeDisposed = true;
        try { lifecycle.abort(); } catch (_) {}
        if (anchorObserver) { try { anchorObserver.disconnect(); } catch (_) {} }
        runtimeTimers.forEach(timerId => pd.defaultView.clearTimeout(timerId));
        runtimeTimers.clear();
        // If a theme change happens mid-drag, cancel the drag cleanly rather than
        // leaving the robot permanently in the carried state.
        if (root._plrDragging) {
          root._plrDragging = false;
          if (robot) robot.classList.remove('carried');
          const originKey = root.dataset.plrDragOriginKey || '';
          if (originKey) {
            root.dataset.plrAnchorKey = originKey;
            root.dataset.plrAnchorOffsetX = root.dataset.plrDragOriginX || '0';
            root.dataset.plrAnchorOffsetY = root.dataset.plrDragOriginY || '0';
          } else {
            delete root.dataset.plrAnchorKey;
            delete root.dataset.plrAnchorOffsetX;
            delete root.dataset.plrAnchorOffsetY;
          }
          delete root.dataset.plrDragOriginKey;
          delete root.dataset.plrDragOriginX;
          delete root.dataset.plrDragOriginY;
        }
      }
      pd.defaultView.__proofloopRobotController = { destroy: destroyRuntime, version: 19 };

      function say(message, duration=2600) {
        if (!speech) return;
        speech.textContent = message; speech.classList.add('show'); placeSpeech();
        cancelTimer(root._plrSpeechTimer);
        root._plrSpeechTimer = later(() => speech.classList.remove('show'), duration);
      }
      function placeSpeech() {
        if (!robot) return;
        const q = robot.getBoundingClientRect();
        // Keep the reset control aligned with Loop even when the speech bubble is closed.
        const hide = root.querySelector('#plr-hide');
        if (hide) {
          hide.style.left = Math.max(3, Math.min(pd.documentElement.clientWidth - 24, q.right - 7)) + 'px';
          hide.style.top = Math.max(3, Math.min(pd.documentElement.clientHeight - 24, q.top - 5)) + 'px';
        }
        if (!speech || !speech.classList.contains('show')) return;
        const sw = speech.offsetWidth || 150, sh = speech.offsetHeight || 36;
        let left = q.left + q.width/2 - sw/2;
        left = Math.max(8, Math.min(pd.documentElement.clientWidth - sw - 8, left));
        let top = q.top - sh - 8;
        if (top < 6) top = q.bottom + 8;
        speech.style.left = left + 'px';
        speech.style.top = Math.max(4, Math.min(pd.documentElement.clientHeight - sh - 6, top)) + 'px';
      }
      function setPos(x,y,animate=true) {
        if (!robot) return;
        const w = robot.getBoundingClientRect().width || 98, h = robot.getBoundingClientRect().height || 118;
        const maxX = Math.max(4, pd.documentElement.clientWidth - w - 4);
        const maxY = Math.max(4, pd.documentElement.clientHeight - h - 4);
        robot.style.transition = animate ? 'left .46s cubic-bezier(.2,.75,.25,1), top .46s cubic-bezier(.2,.75,.25,1), filter .2s ease' : 'none';
        robot.style.left = Math.max(4, Math.min(maxX, x)) + 'px';
        robot.style.top = Math.max(4, Math.min(maxY, y)) + 'px';
        placeSpeech();
      }
      // Only a small whitelist may accept Loop. These are the only elements the
      // character can attach to; ordinary inputs, cards, borders and sidebars are excluded.
      const LANDING_SELECTOR = '#pl-robot-home-slot,.pl-step-card,[data-testid="stFormSubmitButton"] button,.sample-bar,.audit-table-wrap,.correction-box';
      let attachedKey = root.dataset.plrAnchorKey || null;
      let attached = attachedKey ? resolveTarget(attachedKey) : null;
      let anchorOffsetX = Number.parseFloat(root.dataset.plrAnchorOffsetX || '0') || 0;
      let anchorOffsetY = Number.parseFloat(root.dataset.plrAnchorOffsetY || '0') || 0;

      function clearAnchor() {
        attached = null; attachedKey = null; anchorOffsetX = 0; anchorOffsetY = 0;
        delete root.dataset.plrAnchorKey;
        delete root.dataset.plrAnchorOffsetX;
        delete root.dataset.plrAnchorOffsetY;
      }

      function findReviewButton() {
        return [...pd.querySelectorAll('button,[role="button"]')].find(el => {
          const label = (el.innerText || el.getAttribute('aria-label') || '').replace(/\s+/g,' ').trim();
          return /check guideline alignment|review caption/i.test(label) && !root.contains(el);
        }) || null;
      }
      function targetKeyFor(el) {
        if (!el) return null;
        if (el.id === 'pl-robot-home-slot') return 'home';
        if (el.matches('.sample-bar')) return 'sample';
        if (el.matches('.audit-table-wrap')) return 'audit';
        if (el.matches('.correction-box')) return 'correction';
        if (el.matches('.pl-step-card')) { const step = (el.querySelector('.pl-step-no')?.innerText || '').match(/0?([1-3])/); return step ? 'step-' + step[1] : null; }
        const label = (el.innerText || el.getAttribute('aria-label') || '').replace(/\s+/g,' ').trim();
        if (/check guideline alignment|review caption/i.test(label)) return 'review-button';
        return null;
      }
      function resolveTarget(key) {
        if (key === 'home') return pd.querySelector('#pl-robot-home-slot');
        if (key && key.startsWith('step-')) { const n = key.slice(5); return [...pd.querySelectorAll('.pl-step-card')].find(el => (el.querySelector('.pl-step-no')?.innerText || '').includes(n.padStart(2,'0'))) || [...pd.querySelectorAll('.pl-step-card')][Number(n)-1] || null; }
        if (key === 'sample') return pd.querySelector('.sample-bar');
        if (key === 'audit') return pd.querySelector('.audit-table-wrap');
        if (key === 'correction') return pd.querySelector('.correction-box');
        if (key === 'review-button') return findReviewButton();
        return null;
      }
      function syncAnchor() {
        if (!attachedKey || !robot) return;
        if (!attached || !attached.isConnected) attached = resolveTarget(attachedKey);
        if (!attached) return; // keep the prior coordinates while Streamlit replaces its nodes
        const q = attached.getBoundingClientRect();
        robot.style.transition = 'none';
        // Do not clamp to the viewport: the robot must travel away with its page element
        // when scrolling, then return with that exact element when scrolling back.
        robot.style.left = (q.left + anchorOffsetX) + 'px';
        robot.style.top = (q.top + anchorOffsetY) + 'px';
        placeSpeech();
      }
      function anchorByOffset(targetKey, xOffset, yOffset) {
        const target = resolveTarget(targetKey);
        if (!target) return false;
        attached = target;
        attachedKey = targetKey;
        anchorOffsetX = xOffset;
        anchorOffsetY = yOffset;
        root.dataset.plrAnchorKey = targetKey;
        root.dataset.plrAnchorOffsetX = String(xOffset);
        root.dataset.plrAnchorOffsetY = String(yOffset);
        root.dataset.plrPositioned = 'true';
        syncAnchor();
        return true;
      }
      function anchorByCoordinates(target, left, top) {
        const key = targetKeyFor(target);
        if (!key) return false;
        const q = target.getBoundingClientRect();
        return anchorByOffset(key, left - q.left, top - q.top);
      }
      function positionAtHome() {
        const home = resolveTarget('home');
        if (!home) {
          clearAnchor();
          setPos(pd.documentElement.clientWidth - 104, 120, true);
          return;
        }
        const q = home.getBoundingClientRect();
        const w = robot.getBoundingClientRect().width || 98;
        const h = robot.getBoundingClientRect().height || 118;
        // Center Loop in the home stage so the mascot reads as the main character,
        // rather than a small decoration pushed against the right edge.
        const left = q.left + Math.max(8, (q.width - w) / 2);
        const top = q.top + Math.max(8, (q.height - h) / 2 - 8);
        anchorByCoordinates(home, left, top);
      }
      function goHome(announce=true) {
        clearAnchor();
        const home = resolveTarget('home');
        if (!home) {
          positionAtHome();
          return;
        }
        const q = home.getBoundingClientRect();
        const viewH = pd.defaultView.innerHeight || pd.documentElement.clientHeight;
        const needsScroll = q.bottom < 12 || q.top > viewH - 12;
        const finish = () => {
          positionAtHome();
          robot.classList.remove('carried','falling','impact','recovering','annoyed','confused','sleeping','bored','sitting','walking','hover-land','thinking','home-hover');
          robot.classList.add('booting','waving');
          if (announce) say('Docking sequence engaged.', 1900);
          later(() => { if (robot && robot.isConnected) { robot.classList.remove('waving','booting'); robot.classList.add('home-hover'); } }, 1900);
          scheduleMood();
        };
        if (needsScroll) {
          home.scrollIntoView({ behavior: 'smooth', block: 'center' });
          later(finish, 520);
        } else finish();
      }
      function candidates() {
        const fixedTargets = [...pd.querySelectorAll(LANDING_SELECTOR)];
        const review = findReviewButton();
        if (review && !fixedTargets.includes(review)) fixedTargets.push(review);
        return fixedTargets.filter(el =>
          !root.contains(el) && el.getClientRects().length &&
          getComputedStyle(el).visibility !== 'hidden' && getComputedStyle(el).display !== 'none'
        );
      }
      function targetAt(robotRect) {
        const centerX = robotRect.left + robotRect.width / 2;
        const centerY = robotRect.top + robotRect.height / 2;
        let best = null, bestScore = Infinity;
        candidates().forEach(el => {
          const q = el.getBoundingClientRect();
          if (q.width < 70 || q.height < 18) return;
          const inside = centerX >= q.left + 2 && centerX <= q.right - 2 &&
                         centerY >= q.top + 2 && centerY <= q.bottom - 2;
          const onTop = centerX >= q.left + 2 && centerX <= q.right - 2 &&
                        Math.abs(robotRect.bottom - q.top) <= 26 && robotRect.top < q.top + 10;
          if (inside || onTop) {
            const score = inside ? 0 : Math.abs(robotRect.bottom - q.top) + 1;
            if (score < bestScore) { best = el; bestScore = score; }
          }
        });
        return best;
      }
      const HOME_IDLE_CLASSES = ['idle-curious','idle-stretch','idle-scan','idle-cheer','idle-drift','idle-goofy','idle-dance','idle-propeller'];
      function clearHomeIdle() { if (robot) robot.classList.remove(...HOME_IDLE_CLASSES); }
      function moodClear() {
        if (!robot) return;
        robot.classList.remove('bored','sleeping','thinking','cheer','annoyed','confused','waving','walking','falling','impact','hover-land','sitting','standing',...HOME_IDLE_CLASSES);
      }
      function playHomeIdle() {
        if (!robot || !robot.isConnected || root.dataset.hidden === 'true' || root.dataset.status !== 'idle' || root._plrDragging || attachedKey !== 'home') return;
        clearHomeIdle();
        robot.classList.add('home-hover');
        const action = HOME_IDLE_CLASSES[Math.floor(Math.random() * HOME_IDLE_CLASSES.length)];
        robot.classList.add(action);
        // Short, characterful beats with long calm intervals keep the animation readable.
        const duration = ['idle-stretch','idle-goofy','idle-dance','idle-propeller'].includes(action) ? 1650 : (action === 'idle-drift' || action === 'idle-scan') ? 1500 : 1250;
        if (action === 'idle-scan' && Math.random() < .44) say('Tiny scan beam… bzzzt!', 1550);
        else if (action === 'idle-cheer' && Math.random() < .45) say('Achievement unlocked: being adorable.', 1700);
        else if (action === 'idle-goofy' && Math.random() < .72) say('I meant to do that. Probably.', 1700);
        else if (action === 'idle-dance' && Math.random() < .58) say('♪ micro dance break ♪', 1700);
        else if (action === 'idle-propeller' && Math.random() < .5) say('Wheeeee— recalibrating!', 1700);
        cancelTimer(root._plrHomeActionTimer);
        root._plrHomeActionTimer = later(() => {
          clearHomeIdle();
          if (robot && robot.isConnected && attachedKey === 'home' && root.dataset.status === 'idle' && !root._plrDragging) robot.classList.add('home-hover');
        }, duration);
      }
      function scheduleMood() {
        cancelTimer(root._plrMoodTimer);
        root._plrMoodTimer = later(() => {
          if (!robot || !robot.isConnected || root.dataset.hidden === 'true' || root.dataset.status !== 'idle' || root._plrDragging) return;
          if (attachedKey === 'home') {
            robot.classList.remove('bored','sleeping','walking','sitting','standing');
            robot.classList.add('home-hover');
            playHomeIdle();
            scheduleMood();
            return;
          }
          clearHomeIdle();
          moodClear(); robot.classList.add('bored');
          if (Math.random() < .35) say('Any captions to check?', 1900);
          root._plrSleepTimer = later(() => {
            if (root.dataset.hidden === 'true' || root.dataset.status !== 'idle' || root._plrDragging) return;
            moodClear(); robot.classList.add('sleeping');
            root._plrWakeTimer = later(() => { if (robot && robot.isConnected && !root._plrDragging && root.dataset.status === 'idle') { moodClear(); robot.classList.add('standing'); } scheduleMood(); }, 4200);
          }, 2800);
        }, 5100 + Math.random()*3900);
      }
      function scheduleWander() {
        // Animation only, never autonomous relocation. Loop remains on its chosen element.
        cancelTimer(root._plrWanderTimer);
        root._plrWanderTimer = later(() => {
          if (!robot || !robot.isConnected || root.dataset.hidden === 'true' || root.dataset.status !== 'idle' || root._plrDragging) { scheduleWander(); return; }
          if (attachedKey === 'home') { robot.classList.add('home-hover'); scheduleWander(); return; }
          if (robot.classList.contains('sleeping')) { scheduleWander(); return; }
          if (Math.random() < .5) {
            robot.classList.remove('standing','bored','sitting');
            robot.classList.add('walking');
            later(() => { if (!root._plrDragging && robot && robot.isConnected) { robot.classList.remove('walking'); robot.classList.add('sitting'); } }, 900);
          } else {
            robot.classList.remove('standing','bored','sitting');
            robot.classList.add('hover-land');
            later(() => { if (!root._plrDragging && robot && robot.isConnected) { robot.classList.remove('hover-land'); robot.classList.add('sitting'); } }, 850);
          }
          scheduleWander();
        }, 22000 + Math.random()*14000);
      }
      function landAt(x,y,pointerX,pointerY) {
        const w=robot.getBoundingClientRect().width||72, h=robot.getBoundingClientRect().height||92;
        const draggedRect=robot.getBoundingClientRect();
        const target=targetAt(draggedRect);
        let destX, destY, pendingAnchor=null;
        if (target) {
          const q=target.getBoundingClientRect();
          const key=targetKeyFor(target);
          destX = q.width >= w + 8
            ? Math.max(q.left+4, Math.min(draggedRect.left,q.right-w-4))
            : q.left + (q.width-w)/2;
          const droppedInside = draggedRect.left + draggedRect.width/2 >= q.left &&
                                draggedRect.left + draggedRect.width/2 <= q.right &&
                                draggedRect.top + draggedRect.height/2 >= q.top &&
                                draggedRect.top + draggedRect.height/2 <= q.bottom;
          if (key === 'home') {
            // Dropping into the home scene always docks Loop in the visual center.
            destX = q.left + (q.width - w) / 2;
            destY = q.top + (q.height - h) / 2 - 6;
          } else if (key === 'review-button' || (key && key.startsWith('step-'))) {
            // These compact UI targets are perches: keep Loop's feet on their top edge,
            // instead of covering the label/button text with the robot's body.
            destY = q.top - h + 10;
          } else if (droppedInside) {
            destY = q.height < h * .76 ? q.top - (h-q.height)/2 : Math.max(q.top+2, Math.min(draggedRect.top, q.bottom-h-2));
          } else {
            destY = q.top-h+10;
          }
          pendingAnchor = { key, x: destX-q.left, y: destY-q.top };
        } else {
          clearAnchor();
          destX=Math.max(4,Math.min(pd.documentElement.clientWidth-w-4,pointerX-w/2));
          destY=pd.documentElement.clientHeight-h-8;
          say('Oops—missed the landing spot!', 1500);
        }
        destX=Math.max(4,Math.min(pd.documentElement.clientWidth-w-4,destX));
        destY=Math.max(4,Math.min(pd.documentElement.clientHeight-h-4,destY));
        // Recalculate the stored local offset from the final visible landing position.
        if (pendingAnchor) {
          const q=target.getBoundingClientRect();
          pendingAnchor.x=destX-q.left; pendingAnchor.y=destY-q.top;
        }
        robot.classList.remove('carried','walking','sitting','bored','sleeping','hover-land','impact','recovering','annoyed','confused','standing','falling','thinking');
        robot.style.transition='none';
        robot.style.left=destX+'px';
        robot.style.top=Math.max(4,Math.min(pd.documentElement.clientHeight-h-4,destY-105))+'px';
        void robot.offsetWidth;
        robot.classList.add('falling');
        robot.style.transition='top .62s cubic-bezier(.45,.05,.7,.35), left .22s ease-out';
        requestAnimationFrame(()=>{ robot.style.top=destY+'px'; robot.style.left=destX+'px'; });
        later(()=>{
          robot.classList.remove('falling');
          robot.classList.add('impact');
          // A visible squash, then a separate hand-supported push-up.
          later(()=>{
            robot.classList.remove('impact');
            robot.classList.add('recovering');
            if (pendingAnchor && pendingAnchor.key) {
              anchorByOffset(pendingAnchor.key, pendingAnchor.x, pendingAnchor.y);
            } else {
              clearAnchor();
            }
            later(()=>{
              robot.classList.remove('recovering');
              const reaction = Math.random() < .78 ? 'annoyed' : 'confused';
              robot.classList.add(reaction);
              say(reaction === 'annoyed' ? 'HEY! A little warning next time.' : 'Wait… what just happened?', 2300);
              later(()=>{
                robot.classList.remove('annoyed','confused');
                if (attachedKey === 'home') robot.classList.add('home-hover');
                else if (root.dataset.status === 'idle') robot.classList.add('sitting');
                scheduleMood();
              }, 2150);
            }, 920);
          }, 280);
        }, 720);
        root._plrLastDrop=Date.now();
        scheduleWander(); scheduleMood();
      }
      function setup() {
        if (!robot) return;
        root.dataset.initialized='true';
        let dragging=false, moved=false, startX=0, startY=0, originX=0, originY=0, pointerId=null;
        robot.addEventListener('pointerdown', e => {
          if (e.button !== undefined && e.button !== 0) return;
          dragging=true; moved=false; pointerId=e.pointerId; startX=e.clientX; startY=e.clientY;
          const rect=robot.getBoundingClientRect(); originX=rect.left; originY=rect.top;
          root.dataset.plrDragOriginKey = attachedKey || '';
          root.dataset.plrDragOriginX = String(anchorOffsetX || 0);
          root.dataset.plrDragOriginY = String(anchorOffsetY || 0);
          root._plrDragging=true; robot.classList.remove('bored','sleeping','sitting','standing','walking','annoyed','confused','waving','recovering','impact','falling','home-hover','booting'); robot.classList.add('carried');
          if (root.dataset.status === 'idle') say('Carry me somewhere?', 1100);
          try { robot.setPointerCapture(e.pointerId); } catch (_) {}
          e.preventDefault();
        }, {signal:lifecycle.signal});
        pd.addEventListener('pointermove', e => {
          if (!dragging || (pointerId!==null && e.pointerId!==pointerId)) return;
          const dx=e.clientX-startX, dy=e.clientY-startY;
          if (Math.abs(dx)+Math.abs(dy)>4) moved=true;
          if (!moved) return;
          clearAnchor();
          robot.classList.remove('falling','sitting','hover-land');
          robot.dataset.dir=dx < -2 ? 'left' : (dx > 2 ? 'right' : robot.dataset.dir || 'right');
          setPos(originX+dx,originY+dy,false); e.preventDefault();
        }, {passive:false, signal:lifecycle.signal});
        function release(e) {
          if (!dragging || (pointerId!==null && e.pointerId!==pointerId)) return;
          dragging=false; pointerId=null; root._plrDragging=false;
          delete root.dataset.plrDragOriginKey;
          delete root.dataset.plrDragOriginX;
          delete root.dataset.plrDragOriginY;
          try { robot.releasePointerCapture(e.pointerId); } catch (_) {}
          if (!moved) {
            robot.classList.remove('carried','bored','sleeping','annoyed','confused'); robot.classList.add('waving');
            say('Hey! I’m Loop. Ready to review?', 2700);
            later(()=>robot.classList.remove('waving'),1450);
            scheduleMood(); return;
          }
          const rect=robot.getBoundingClientRect(); landAt(rect.left,rect.top,e.clientX,e.clientY);
        }
        pd.addEventListener('pointerup',release,{signal:lifecycle.signal});
        pd.addEventListener('pointercancel',release,{signal:lifecycle.signal});
        robot.addEventListener('keydown', e => {
          if (e.key==='Enter' || e.key===' ') { e.preventDefault(); robot.classList.remove('bored','sleeping','annoyed','confused'); robot.classList.add('waving'); say('Hey! I’m Loop. Ready to review?',2700); later(()=>robot.classList.remove('waving'),1450); }
        }, {signal:lifecycle.signal});
        const hide = root.querySelector('#plr-hide');
        if (hide) {
          hide.addEventListener('click', (e) => {
            e.preventDefault(); e.stopPropagation();
            goHome(true);
          }, {signal:lifecycle.signal});
        }
        const syncOnScroll = () => {
          if (attachedKey) syncAnchor();
          placeSpeech();
        };
        // Capture scroll events from the document and nested Streamlit scroll containers.
        pd.addEventListener('scroll', syncOnScroll, {passive:true, capture:true, signal:lifecycle.signal});
        pd.defaultView.addEventListener('scroll', syncOnScroll, {passive:true, signal:lifecycle.signal});
        pd.defaultView.addEventListener('resize', () => {
          if (attachedKey) syncAnchor();
          else { const q=robot.getBoundingClientRect(); setPos(q.left,q.top,false); }
        }, {signal:lifecycle.signal});
        // Streamlit recreates DOM nodes on rerun; reconnect the anchor to the replacement.
        anchorObserver = new pd.defaultView.MutationObserver(() => {
          if (!attachedKey || root._plrAnchorRebindPending) return;
          if (!attached || !attached.isConnected) {
            root._plrAnchorRebindPending = true;
            const key = attachedKey;
            later(() => {
              root._plrAnchorRebindPending = false;
              if (!root.isConnected || !attachedKey) return;
              const replacement = resolveTarget(key);
              if (replacement) { attached = replacement; syncAnchor(); }
              else {
                clearAnchor();
                positionAtHome();
              }
            }, 120);
          }
        });
        anchorObserver.observe(pd.body, {childList:true, subtree:true});
        root._plrAnchorObserver = anchorObserver;

        // The default home is the mascot slot inside the hero, not an arbitrary viewport corner.
        later(() => {
          if (!robot.isConnected || root.dataset.hidden==='true') return;
          if (attachedKey) syncAnchor();
          else if (root.dataset.plrPositioned !== 'true') positionAtHome();
          root.dataset.plrPositioned='true';
          if (!root.dataset.greeted) {
            root.dataset.greeted='true'; robot.classList.add('booting','waving'); say('Booting thrusters… ready to review!',3200);
            later(()=>{ robot.classList.remove('waving','booting'); if (attachedKey === 'home') robot.classList.add('home-hover'); },2200);
          } else if (attachedKey === 'home' && !robot.classList.contains('booting')) {
            robot.classList.add('home-hover');
          }
          scheduleMood(); scheduleWander();
        },320);
      }

      root.hidden = false;
      root.dataset.hidden = 'false';
      root.style.display='block';
      root.style.visibility='visible';
      root.style.opacity='1';
      root.dataset.theme = '__THEME__';
      root.style.setProperty('--plr-bg',colors.bg);
      root.style.setProperty('--plr-surface',colors.surface);
      root.style.setProperty('--plr-card',colors.card);
      root.style.setProperty('--plr-border',colors.border);
      root.style.setProperty('--plr-ink',colors.ink);
      root.style.setProperty('--plr-muted',colors.muted);
      root.style.setProperty('--plr-accent',colors.accent);
      root.style.setProperty('--plr-accent-soft',colors.accentSoft);
      setup();
      if (statusChanged && root.dataset.initialized==='true') {
        if (status==='thinking') { root.querySelector('#plr-character').classList.remove('bored','sleeping','annoyed','confused'); root.querySelector('#plr-character').classList.add('thinking'); say('Checking the evidence…',2600); }
        else if (status==='success') { const r=root.querySelector('#plr-character'); r.classList.remove('thinking','bored','sleeping','annoyed','confused'); r.classList.add('cheer','waving'); say('Review ready! Nice work.',2800); later(()=>r.classList.remove('cheer','waving'),1600); scheduleMood(); }
        else if (status==='error') { const r=root.querySelector('#plr-character'); r.classList.remove('thinking','bored','sleeping','confused'); r.classList.add('annoyed'); say('Hmm. Something needs a second look.',3000); scheduleMood(); }
        else if (status==='idle') { const r=root.querySelector('#plr-character'); r.classList.remove('thinking','cheer','annoyed','confused'); r.classList.add('standing'); scheduleMood(); scheduleWander(); }
      }
    })();
    </script></body></html>'''
    for token, value in tokens.items():
        doc = doc.replace(token, value)
    components.html(doc, height=1, scrolling=False)


def hide_global_robot() -> None:
    """Hide the persistent page-level mascot when the user disables it."""
    doc = r'''<!doctype html><html><body><script>
    (() => {
      try {
        const pd = window.parent.document;
        const root = pd && pd.getElementById('pl-live-robot');
        if (root) root.style.display = 'none';
      } catch (_) {}
    })();
    </script></body></html>'''
    components.html(doc, height=1, scrolling=False)
