from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

class UIAssetTests(unittest.TestCase):
    def test_three_space_scenes_exist(self):
        app = (ROOT / "app.py").read_text()
        for name in ("scene-nebula", "scene-planet", "scene-aurora"):
            self.assertIn(name, app)
        self.assertIn("@keyframes pl-scene-fade-a", app)
        self.assertIn("@keyframes pl-scene-fade-b", app)
        self.assertIn("@keyframes pl-scene-fade-c", app)

    def test_api_key_notice_is_explicit_and_styled(self):
        app = (ROOT / "app.py").read_text()
        self.assertIn("API key required for live reviews", app)
        self.assertIn(".pl-api-key-notice", app)

    def test_mascot_has_idle_actions_and_centered_home(self):
        mascot = (ROOT / "proofloop" / "mascot.py").read_text()
        self.assertIn("positionAtHome()", mascot)
        self.assertIn("idle-stretch", mascot)
        self.assertIn("idle-scan", mascot)
        self.assertIn("idle-cheer", mascot)
        self.assertIn("idle-drift", mascot)
        self.assertIn("dataset.plVersion = '19'", mascot)
        self.assertIn('plr-engine-left', mascot)
        self.assertIn('plr-smoke-lift', mascot)
        self.assertIn('plr-boot-art', mascot)
        self.assertIn("key === 'review-button'", mascot)
        self.assertIn("robot.classList.add('sitting')", mascot)
        self.assertIn('plr-sit-art', mascot)

    def test_mascot_uses_lunar_shell_and_cyan_face(self):
        mascot = (ROOT / "proofloop" / "mascot.py").read_text()
        self.assertIn("#B6B9F6", mascot)
        self.assertIn("#87F2FF", mascot)

    def test_cosmic_hero_and_proper_orbital_brand(self):
        app = (ROOT / "app.py").read_text()
        self.assertIn("linear-gradient(126deg,#090F25", app)
        self.assertIn("pl-brand-gradient", app)
        self.assertIn("font-family:Inter,ui-sans-serif,system-ui", app)
        self.assertIn("pl-comet", app)
        self.assertIn("height:212px", app)
        self.assertIn('page_icon="🪐"', app)
        self.assertIn("pl_visual_version", app)
        self.assertIn('st.session_state["pl_theme"] = "Dark"', app)

    def test_mascot_is_compact_and_has_playful_idle_actions(self):
        mascot = (ROOT / "proofloop" / "mascot.py").read_text()
        self.assertIn("width:98px;height:118px", mascot)
        self.assertIn("idle-goofy", mascot)
        self.assertIn("idle-dance", mascot)
        self.assertIn("idle-propeller", mascot)
        self.assertIn("plr-goofy-wrapper", mascot)
        self.assertIn("plr-dance-wrapper", mascot)
        self.assertIn("dataset.plVersion = '19'", mascot)


    def test_theme_switch_updates_hero_board_api_chip_and_robot(self):
        app = (ROOT / "app.py").read_text()
        mascot = (ROOT / "proofloop" / "mascot.py").read_text()
        self.assertIn("--pl-hero-background", app)
        self.assertIn("--pl-board-background", app)
        self.assertIn("--pl-scene-nebula", app)
        self.assertIn(".pl-api-key-copy code", app)
        self.assertIn("--pl-code-bg", app)
        self.assertIn("root.dataset.theme = '__THEME__';", mascot)
        self.assertIn('#pl-live-robot[data-theme="light"] #plr-shell', mascot)
        self.assertIn('#pl-live-robot[data-theme="light"] .plr-eye', mascot)

    def test_previous_fall_animation_is_restored(self):
        mascot = (ROOT / "proofloop" / "mascot.py").read_text()
        self.assertIn("plr-faceplant-squash .28s", mascot)
        self.assertIn("rotate(72deg) scale(1.15,.62)", mascot)
        self.assertNotIn("plr-impact-splat", mascot)

    def test_native_code_copy_button_follows_active_theme(self):
        app = (ROOT / "app.py").read_text()
        self.assertIn('[data-testid="stCodeCopyButton"]', app)
        self.assertIn('[data-testid="stCode"] button', app)
        self.assertIn('background-color:var(--pl-code-bg) !important', app)
        self.assertIn('color:var(--pl-code-ink) !important', app)
        self.assertIn('border-color:var(--pl-accent-border) !important', app)
        self.assertIn(':focus-visible', app)

    def test_result_widgets_follow_active_theme(self):
        app = (ROOT / "app.py").read_text()
        self.assertIn('[data-testid="stCode"]', app)
        self.assertIn('[data-testid="stExpander"] summary', app)
        self.assertIn('.stDownloadButton > button', app)
        self.assertIn('background:var(--pl-code-bg)', app)
        self.assertIn('color:var(--pl-ink)', app)

if __name__ == "__main__":
    unittest.main()
