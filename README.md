# ProofLoop — Evidence-first annotation QA

ProofLoop helps an annotation reviewer compare a proposed caption against supplied evidence and guidelines. It highlights claims that are supported, contradicted, or not evidenced; identifies omitted actions; and drafts a correction.

## What this MVP does

- Reviews text evidence, a caption, and the applicable guideline.
- Produces a claim-by-claim audit with evidence-based reasons.
- Suggests one concise corrected caption.
- Lets the user download the report as Markdown.
- Calls an open-weight Gemma model through Backboard's API.
- Can be deployed to Render with the included `render.yaml`.

**Important limitation:** this version does not process video. The reviewer provides the evidence text/timestamps, and ProofLoop checks the caption against that evidence. It must not be presented as if it independently watched or verified a video.

## Run locally in GitHub Codespaces

1. Open this repository in a Codespace.
2. In the terminal, install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Create an API key in the Backboard dashboard.
4. Set the key in the terminal (do not paste the actual key into source code):

   ```bash
   export BACKBOARD_API_KEY="paste-your-key-here"
   ```

5. Start the app:

   ```bash
   streamlit run app.py
   ```

6. Open the forwarded Streamlit port (usually 8501) when Codespaces offers it.

## Model selection

By default, the app requests `google/gemma-3-4b-it:free` through OpenRouter via Backboard. Free endpoints can be rate-limited and model availability may change. If this model is unavailable, choose an available Gemma/open-weight model in Backboard's model catalogue and set its exact provider/model identifier before starting the app, for example:

```bash
export MODEL_NAME="provider/model-id-from-the-catalogue"
```

Keep `BACKBOARD_API_KEY` private. Do not commit it to GitHub.

## Deploy to Render

1. Push this repository to GitHub.
2. In Render, choose **New → Blueprint** and select the repository, or create a Python web service manually.
3. If using the Blueprint, supply `BACKBOARD_API_KEY` when prompted. If creating a service manually, use:
   - Build command: `pip install -r requirements.txt`
   - Start command: `streamlit run app.py --server.address 0.0.0.0 --server.port $PORT --server.headless true`
4. Add `BACKBOARD_API_KEY` in Render's Environment settings. Keep the API key out of source control.
5. Deploy and test the public URL with the demo case.

## Suggested validation cases

1. **Unsupported action + missing action:** evidence says “picks up cup, then drinks”; caption says “makes coffee”. Expected: “makes coffee” is not evidenced and drinking is omitted.
2. **Supported caption:** evidence says “opens a door and walks through”; caption says the same. Expected: accurate, no missing action.
3. **Direct contradiction:** evidence says “the person sits down”; caption says “the person remains standing.” Expected: contradicted.
4. **Insufficient evidence:** evidence only says “a person is in a room”; caption says “a person opens a drawer.” Expected: cannot verify / not evidenced, not automatically contradicted.

## Honest demo claims

Good: “ProofLoop uses an open-weight Gemma model to audit captions against supplied evidence and annotation rules.”

Avoid claiming that it watches videos, guarantees correctness, is fully private, or has zero ongoing inference costs. Inputs are sent to Backboard and the selected model provider. Human reviewers make the final decision.
