# ProofLoop — Annotation Guideline Checker

ProofLoop is a **text-only annotation quality checker**. Paste the actual task guidelines and an annotator's response; ProofLoop evaluates the response against the supplied rules, identifies specific issues, and suggests a corrected version. It does not accept image/video uploads or fill the form with sample data.

## Core workflow

1. Paste the task instructions and evaluation criteria.
2. Choose **Single answer review** for a caption, annotation, written response, or feedback statement; or **Comparison / feedback review** to supply Output A, Output B, and the annotator's comparison.
3. Submit for a structured verdict, specific issues, explanations, suggestions, confidence, limitations, and a copy-ready correction.
4. Copy or download the correction or full report.

When an API key is missing or the model cannot return a valid structured response, the app reports the problem rather than inventing a successful verdict.

## UI features

- Clear purpose statement and three-step workflow.
- Responsive desktop/tablet/mobile layout with explicit contrast on labels and input fields.
- In-app Light/Dark appearance setting; the Streamlit developer toolbar is hidden so users do not confuse its three-dot menu with product navigation.
- The animated **Loop** mascot is restored from the earlier ProofLoop version: click to wave, drag and drop it on supported page areas, see reactions/moods, and use its return-home control. The sidebar has a Show Loop mascot setting.
- Empty input fields, with no demo or sample-case data.

## Project structure

```text
app.py                     Streamlit UI, settings, input workflow, and result rendering
proofloop/prompts.py       Prompt composition from actual user-supplied text
proofloop/llm_client.py    Server-side Backboard/OpenRouter client wrapper
proofloop/evaluator.py     Input validation and structured-response parsing
proofloop/mascot.py        Restored interactive Loop mascot widget
tests/test_evaluator.py   Offline unit tests (no AI API calls)
requirements.txt           Python dependencies
.env.example               Configuration example only
```

## Run in GitHub Codespaces

Python 3.10+ is recommended. In the Codespaces terminal, run:

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python -m streamlit run app.py
```

Open the forwarded port `8501` in the browser.

## Configure live AI reviews

The app uses a Backboard client configured for OpenRouter by default. Create a Codespaces secret named `BACKBOARD_API_KEY`, grant it access to the repository, then restart the Codespace. Optional settings:

```text
LLM_PROVIDER=openrouter
MODEL_NAME=openai/gpt-4o-mini
```

Never commit API keys or `.streamlit/secrets.toml` to GitHub.

## Tests and limitations

The offline tests validate required inputs and response parsing; they do not make live AI calls. A valid Backboard API key and working configured model are required for a real review. The AI can only evaluate supplied text: it cannot verify details that depend on unseen source material. Treat results as review assistance, not an automatic guarantee of correctness.


## Mascot animation update

Loop is a 2D SVG/CSS/JavaScript character (not a real-time 3D rig). It has a boot-up thruster/smoke sequence, continuous hover, expressive face states, and timed idle actions such as curious head tilts, stretching, a happy bounce, a face scan, and a short hover drift. Drag Loop to the home scene, step cards, or review button to see its landing/reaction behavior. The home scene rotates between Nebula Garden, Orbit Station, and Aurora Drift. Reduced-motion preferences are respected.

The existing Backboard/OpenRouter configuration is unchanged. Live reviews still require `BACKBOARD_API_KEY` in the environment.



## UI refresh v6 — Cosmic Loop

- Compact Loop sizing: 98×118 px on desktop and 78×94 px on small screens.
- A shorter 212 px desktop home scene, responsive down to 184 px on narrow phones.
- An original orbital/check brand mark used in the app header and sidebar; the browser page icon is a planet.
- Consistent space palette: deep navy, nebula indigo, aurora cyan, lavender shell, luminous cyan eyes, and violet engine glow. The mascot home stays in the space theme in both Light and Dark content modes.
- Three clearly named rotating scenes: Nebula Garden, Orbit Station, and Aurora Drift, with star drift, a planet, orbit rings, an occasional comet, and a glowing landing platform.
- Eight home idle actions: curious tilt, stretch, scan, cheer, drift, goofy wobble, tiny dance, and antenna-propeller spin. These play at random after a short pause while Loop is docked at home.
- Existing dragging, perching, return-home, success/error reactions, and Backboard/OpenRouter model settings are preserved.

The idle motions are original 2D SVG/CSS animations, not a complete 3D rig. Reduced-motion preferences are respected.


## v8 appearance and mascot patch

- Both Light and Dark modes now theme the hero board, the embedded space scenes, badges, labels, and inline BACKBOARD_API_KEY token.
- The mascot receives the current theme on every Streamlit rerun: Light mode shifts its shell to pearl/ice tones and warms the eye lights; Dark mode retains the lunar-violet/cyan look.
- The original SVG character is preserved. A drop now includes a longer, readable face-first pancake/splat pose with animated impact dust and stars, then recovers.
- Backboard/OpenRouter endpoint and model configuration are unchanged.


## v8 fixes
- Theme-aware Streamlit code blocks, expander headers, and download buttons.
- Restored the earlier short mascot landing animation; removed the exaggerated splat overlay.
- Kept the current theme-aware robot appearance, idle actions, drag/perch interactions, and Backboard/OpenRouter configuration.
