import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent


class AccountLauncherTests(unittest.TestCase):
    def test_exported_wrappers_preserve_arguments_and_independent_auth(self):
        for profile in ("kuno", "rbx", "muu"):
            with self.subTest(profile=profile), tempfile.TemporaryDirectory() as directory:
                home = Path(directory)
                binary_dir = home / "bin"
                binary_dir.mkdir()
                for name in ("pi-account", "pi-extension-deps-patch", "pi-hermes-realpath-patch"):
                    destination = binary_dir / name
                    shutil.copyfile(ROOT / f"executable_{name}", destination)
                    destination.chmod(0o755)
                stub = binary_dir / "pi"
                stub.write_text(
                    '#!/usr/bin/env python3\n'
                    'import json, os, sys\n'
                    'from pathlib import Path\n'
                    'profile = Path(os.environ.get("PI_CODING_AGENT_DIR", str(Path.home() / ".pi/agent")))\n'
                    'print(json.dumps({"profile": str(profile), "args": sys.argv[1:], '
                    '"auth": (profile / "auth.json").read_text()}))\n'
                )
                stub.chmod(0o755)
                original = {}
                for name, folder in (("kuno", "agent"), ("rbx", "agent-rbx"), ("muu", "agent-muu")):
                    target = home / ".pi" / folder
                    target.mkdir(parents=True)
                    (target / "auth.json").write_text(f"synthetic-{name}\n")
                    original[target / "auth.json"] = (target / "auth.json").read_bytes()
                (home / ".pi/agent/settings.json").write_text("{}\n")
                environment = dict(os.environ, HOME=str(home), PATH=f"{binary_dir}:{os.environ['PATH']}")
                for key in ("PI_CODING_AGENT_DIR", "PI_CODING_AGENT_SESSION_DIR"):
                    environment.pop(key, None)
                result = subprocess.run(
                    ["sh", str(ROOT / f"executable_pi-{profile}"), "--offline", "argument with spaces"],
                    env=environment, capture_output=True, text=True, check=True,
                )
                folder = "agent" if profile == "kuno" else f"agent-{profile}"
                self.assertEqual(json.loads(result.stdout), {
                    "profile": str(home / ".pi" / folder),
                    "args": ["--offline", "argument with spaces"],
                    "auth": f"synthetic-{profile}\n",
                })
                self.assertEqual(result.stderr, "")
                for path, content in original.items():
                    self.assertEqual(path.read_bytes(), content)
                    self.assertFalse(path.is_symlink())

    def test_realpath_helper_operates_only_on_synthetic_home_and_is_idempotent(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            script = home / ".pi/agent/npm/node_modules/pi-hermes-memory/src/store/session-indexer.ts"
            script.parent.mkdir(parents=True)
            script.write_text('return { path: filePath, size: stat.size, mtimeMs: Math.trunc(stat.mtimeMs) };\n')
            environment = dict(os.environ, HOME=str(home))
            helper = ROOT / "executable_pi-hermes-realpath-patch"
            subprocess.run(["bash", str(helper)], env=environment, check=True)
            # Execute the transformed TypeScript-compatible expression, not source-text matching.
            fixture = home / "fixture"
            fixture.write_text("synthetic\n")
            link = home / "link"
            link.symlink_to(fixture)
            javascript = (
                'const fs = require("fs"); const filePath = process.argv[1]; '
                'const stat = fs.statSync(filePath); '
                'const result = (function() {' + script.read_text() + '})(); '
                'console.log(result.path);'
            )
            result = subprocess.run(["node", "-e", javascript, str(link)], capture_output=True, text=True, check=True)
            self.assertEqual(result.stdout.strip(), str(fixture.resolve()))
            content, modified = script.read_bytes(), script.stat().st_mtime_ns
            subprocess.run(["bash", str(helper)], env=environment, check=True)
            self.assertEqual((script.read_bytes(), script.stat().st_mtime_ns), (content, modified))


if __name__ == "__main__":
    unittest.main()
