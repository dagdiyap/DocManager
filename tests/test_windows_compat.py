#!/usr/bin/env python3
"""
Cross-platform compatibility tests for DocManager.
Validates that all code works correctly on both Windows and macOS.
Run with: python tests/test_windows_compat.py
"""

import os
import sys
import unittest
from pathlib import Path

# Ensure project root is on path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


class TestConfigCrossPlatform(unittest.TestCase):
    """Test configuration works on all platforms."""

    def test_find_project_root(self):
        from ca_desktop.backend.src.config import _find_project_root
        root = _find_project_root()
        self.assertTrue(root.exists(), f"Project root not found: {root}")
        # Should contain ca_desktop or .env
        has_marker = (root / 'ca_desktop').exists() or (root / '.env').exists()
        self.assertTrue(has_marker, f"Root {root} missing expected markers")

    def test_find_env_file(self):
        from ca_desktop.backend.src.config import _find_env_file
        env_path = _find_env_file()
        self.assertIsNotNone(env_path)
        # Should be a string path
        self.assertIsInstance(env_path, str)

    def test_auto_generate_secret_key(self):
        from ca_desktop.backend.src.config import _get_default_secret_key
        # Remove env vars temporarily
        old_sk = os.environ.pop('SECRET_KEY', None)
        old_ca_sk = os.environ.pop('CA_SECRET_KEY', None)
        try:
            key = _get_default_secret_key()
            self.assertIsInstance(key, str)
            self.assertGreaterEqual(len(key), 32, "Auto-generated key too short")
        finally:
            if old_sk:
                os.environ['SECRET_KEY'] = old_sk
            if old_ca_sk:
                os.environ['CA_SECRET_KEY'] = old_ca_sk

    def test_settings_loads_without_env_vars(self):
        """Settings should load even without SECRET_KEY in env (auto-generated)."""
        from ca_desktop.backend.src.config import Settings
        # This should NOT raise ValidationError
        settings = Settings()
        self.assertIsNotNone(settings.secret_key)
        self.assertGreaterEqual(len(settings.secret_key), 32)

    def test_host_is_localhost(self):
        """Host should be 127.0.0.1 to avoid Windows Firewall popups."""
        from ca_desktop.backend.src.config import Settings
        settings = Settings()
        self.assertEqual(settings.host, "127.0.0.1")

    def test_cors_includes_all_ports(self):
        """CORS should include all common frontend ports."""
        from ca_desktop.backend.src.config import Settings
        settings = Settings()
        required_origins = [
            "http://localhost:5173",
            "http://localhost:5174",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:5174",
        ]
        for origin in required_origins:
            self.assertIn(origin, settings.cors_origins,
                         f"Missing CORS origin: {origin}")


class TestFilenameSanitization(unittest.TestCase):
    """Test filename sanitization for Windows compatibility."""

    def test_basic_sanitization(self):
        from shared.utils.validators import sanitize_filename
        self.assertEqual(sanitize_filename("report.pdf"), "report.pdf")
        self.assertEqual(sanitize_filename("my file.txt"), "my file.txt")

    def test_windows_reserved_names(self):
        from shared.utils.validators import sanitize_filename
        # These must be prefixed with _ to avoid Windows crashes
        for name in ["CON", "PRN", "AUX", "NUL", "COM1", "LPT1"]:
            result = sanitize_filename(f"{name}.txt")
            self.assertTrue(result.startswith("_"),
                          f"Reserved name {name}.txt not prefixed: {result}")

    def test_windows_invalid_chars(self):
        from shared.utils.validators import sanitize_filename
        # Characters that crash on Windows: \ / : * ? " < > |
        result = sanitize_filename('file:name<test>?.txt')
        self.assertNotIn(":", result)
        self.assertNotIn("<", result)
        self.assertNotIn(">", result)
        self.assertNotIn("?", result)

    def test_leading_trailing_dots(self):
        from shared.utils.validators import sanitize_filename
        # Windows doesn't allow trailing dots
        result = sanitize_filename("...hidden...")
        self.assertFalse(result.startswith("."))
        self.assertFalse(result.endswith("."))

    def test_empty_after_sanitization(self):
        from shared.utils.validators import sanitize_filename
        result = sanitize_filename(":::")
        self.assertEqual(result, "file")


class TestPathNormalization(unittest.TestCase):
    """Test that all stored paths use forward slashes."""

    def test_path_normalize_on_join(self):
        """Simulate what documents.py does and verify forward slashes."""
        doc_root = Path("documents")
        save_path = doc_root / "9876543210" / "2024" / "report.pdf"
        normalized = str(save_path.relative_to(doc_root)).replace("\\", "/")
        self.assertNotIn("\\", normalized)
        self.assertEqual(normalized, "9876543210/2024/report.pdf")

    def test_path_traversal_protection(self):
        """is_relative_to should work on all platforms."""
        base = Path("/tmp/documents").resolve()
        good_path = (base / "client" / "file.pdf").resolve()
        # This is the cross-platform safe check
        self.assertTrue(good_path.is_relative_to(base))


class TestPathTraversalSafety(unittest.TestCase):
    """Test path traversal protection in file streamer."""

    def test_is_safe_path(self):
        from shared.utils.validators import is_safe_path
        base = Path("/tmp/test_docs")
        # Safe path
        self.assertTrue(is_safe_path(base, base / "client" / "file.pdf"))
        # Unsafe path (traversal)
        self.assertFalse(is_safe_path(base, base / ".." / "etc" / "passwd"))


class TestFingerprintCrossPlatform(unittest.TestCase):
    """Test device fingerprinting works on current platform."""

    def test_get_device_info(self):
        from shared.crypto.fingerprint import get_device_info
        info = get_device_info()
        self.assertIsNotNone(info.cpu_id)
        self.assertIsNotNone(info.mac_address)
        self.assertIsNotNone(info.hostname)
        self.assertIsNotNone(info.os_info)

    def test_generate_fingerprint(self):
        from shared.crypto.fingerprint import generate_device_fingerprint
        fp = generate_device_fingerprint()
        self.assertIsInstance(fp, str)
        self.assertEqual(len(fp), 64)  # SHA256 hex digest

    def test_subprocess_kwargs_platform(self):
        """On Windows, _SUBPROCESS_KWARGS should have creationflags."""
        from shared.crypto import fingerprint
        if sys.platform == 'win32':
            self.assertIn('creationflags', fingerprint._SUBPROCESS_KWARGS)
        else:
            self.assertEqual(fingerprint._SUBPROCESS_KWARGS, {})


class TestConfigProdCrossPlatform(unittest.TestCase):
    """Test production config works on all platforms."""

    def test_get_data_dir(self):
        from ca_desktop.backend.src.config_prod import get_data_dir
        data_dir = get_data_dir()
        self.assertIsInstance(data_dir, Path)
        # Should be a real path
        self.assertTrue(data_dir.exists() or data_dir.parent.exists())

    def test_secret_key_not_hardcoded(self):
        from ca_desktop.backend.src.config_prod import ProductionSettings
        settings = ProductionSettings()
        self.assertNotEqual(settings.secret_key,
                          "CHANGE_THIS_IN_PRODUCTION_VIA_ENV_FILE")
        self.assertGreaterEqual(len(settings.secret_key), 32)


class TestSetupDatabaseCrossPlatform(unittest.TestCase):
    """Test setup_database.py path resolution."""

    def test_script_dir_resolution(self):
        """Scripts should resolve paths relative to their own location."""
        script_path = project_root / 'scripts' / 'setup_database.py'
        self.assertTrue(script_path.exists(),
                       f"setup_database.py not found at {script_path}")


class TestStartScripts(unittest.TestCase):
    """Test startup scripts exist for all platforms."""

    def test_start_sh_exists(self):
        self.assertTrue((project_root / 'start.sh').exists())

    def test_start_bat_exists(self):
        self.assertTrue((project_root / 'start.bat').exists())

    def test_start_sh_no_hardcoded_paths(self):
        """start.sh should not contain hardcoded user paths."""
        content = (project_root / 'start.sh').read_text()
        self.assertNotIn("/Users/pdagdiya", content,
                        "start.sh contains hardcoded Mac-specific path!")

    def test_start_sh_uses_127(self):
        """start.sh should bind to 127.0.0.1, not 0.0.0.0."""
        content = (project_root / 'start.sh').read_text()
        self.assertIn("127.0.0.1", content)
        self.assertNotIn("0.0.0.0", content)


def main():
    print("=" * 60)
    print("  DocManager - Cross-Platform Compatibility Tests")
    print("=" * 60)
    print(f"  Platform: {sys.platform}")
    print(f"  Python:   {sys.version.split()[0]}")
    print(f"  CWD:      {os.getcwd()}")
    print("=" * 60)
    print()

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestConfigCrossPlatform))
    suite.addTests(loader.loadTestsFromTestCase(TestFilenameSanitization))
    suite.addTests(loader.loadTestsFromTestCase(TestPathNormalization))
    suite.addTests(loader.loadTestsFromTestCase(TestPathTraversalSafety))
    suite.addTests(loader.loadTestsFromTestCase(TestFingerprintCrossPlatform))
    suite.addTests(loader.loadTestsFromTestCase(TestConfigProdCrossPlatform))
    suite.addTests(loader.loadTestsFromTestCase(TestSetupDatabaseCrossPlatform))
    suite.addTests(loader.loadTestsFromTestCase(TestStartScripts))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print()
    if result.wasSuccessful():
        print("✅ ALL CROSS-PLATFORM TESTS PASSED!")
    else:
        print("❌ SOME TESTS FAILED — fix before deploying to Windows")

    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
