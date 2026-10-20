"""
FelipedelosH
2026

Unit tests for work.json-based resume of SequentialBruteForceService and
Controller identity verification. Stdlib only (unittest + unittest.mock).
Subprocess and filesystem are mocked/temped; no real brute force is executed.
"""
import os
import sys
import io
import json
import shutil
import hashlib
import tempfile
import contextlib
import unittest
from unittest import mock

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.CORE.Logger import Logger
from src.Infrastructure.repositories.JsonWorkRepository import JsonWorkRepository
from src.Infrastructure.services.WinrarService import WinrarService
from src.Infrastructure.services.TermiteService import TermiteService
from src.Infrastructure.services.CRACKER.SequentialBruteForceService import (
    SequentialBruteForceService, TermiteCheckError
)
from src.Models.Entities.WorkState import WorkState
from src.Models.Enums.WorkStatus import WorkStatus
from src.Models.Enums.PasswordTestResult import PasswordTestResult
from src.controllers.Controller import Controller
from src.CORE.Config import Config

REAL_RAR = os.path.join(PROJECT_ROOT, "INPUT", "123.rar")
REAL_UNRAR = os.path.join(PROJECT_ROOT, "UnRAR.exe")


def silence_stdout():
    return contextlib.redirect_stdout(io.StringIO())


def real_charset():
    with open(os.path.join(PROJECT_ROOT, "characters.txt"), "r", encoding="utf-8") as f:
        content = f.read()
    charset = "".join(c for c in content if c not in ", \n\r\t")
    return "".join(dict.fromkeys(charset))


class TestWinrarService(unittest.TestCase):
    """Scenario 9 support: tryPassword distinguishes correct/incorrect/error."""

    @mock.patch("subprocess.run")
    def test_correct(self, mock_run):
        mock_run.return_value = mock.Mock(returncode=0)
        self.assertEqual(
            WinrarService.tryPassword(REAL_RAR, REAL_UNRAR, "x"),
            PasswordTestResult.CORRECT,
        )

    @mock.patch("subprocess.run")
    def test_incorrect(self, mock_run):
        mock_run.return_value = mock.Mock(returncode=7)
        self.assertEqual(
            WinrarService.tryPassword(REAL_RAR, REAL_UNRAR, "x"),
            PasswordTestResult.INCORRECT,
        )

    def test_timeout_is_error(self):
        import subprocess
        with mock.patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="x", timeout=10)):
            self.assertEqual(
                WinrarService.tryPassword(REAL_RAR, REAL_UNRAR, "x"),
                PasswordTestResult.ERROR,
            )

    @mock.patch("subprocess.run", side_effect=FileNotFoundError("no unrar"))
    def test_hard_error_propagates(self, mock_run):
        with self.assertRaises(FileNotFoundError):
            WinrarService.tryPassword(REAL_RAR, REAL_UNRAR, "x")

    def test_compute_sha256(self):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"hello")
            path = f.name
        try:
            expected = hashlib.sha256(b"hello").hexdigest()
            self.assertEqual(WinrarService.computeSha256(path), expected)
        finally:
            os.remove(path)

    def test_compute_sha256_missing(self):
        with self.assertRaises(FileNotFoundError):
            WinrarService.computeSha256(os.path.join(PROJECT_ROOT, "does_not_exist.rar"))


class TestJsonWorkRepository(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.work_path = os.path.join(self.tmp, "work.json")
        self.repo = JsonWorkRepository(self.work_path)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_round_trip(self):
        self.assertFalse(self.repo.exists())
        state = WorkState(rar_sha256="abc", charset="01", min_len=1, max_len=2,
                          status=WorkStatus.PAUSED, completed_colonies=[1],
                          current_colony=2, current_colony_index=5)
        self.repo.save(state)
        self.assertTrue(self.repo.exists())
        loaded = self.repo.load()
        self.assertEqual(loaded.status, WorkStatus.PAUSED)
        self.assertEqual(loaded.completed_colonies, [1])
        self.assertEqual(loaded.current_colony, 2)
        self.assertEqual(loaded.current_colony_index, 5)
        self.assertEqual(loaded.rar_sha256, "abc")

    def test_backup_corrupt_preserves_original(self):
        with open(self.work_path, "w", encoding="utf-8") as f:
            f.write("{not valid json")
        backup = self.repo.backupCorrupt()
        self.assertIsNotNone(backup)
        self.assertTrue(os.path.isfile(backup))
        self.assertFalse(self.repo.exists())


class ResumeTestBase(unittest.TestCase):
    """Base for service-level resume tests with mocked tryPassword/extractContent."""

    def _make_service(self, charset, min_len, max_len, flush_interval=100):
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp, True)
        temp_path = os.path.join(tmp, "TEMP")
        output_path = os.path.join(tmp, "OUTPUT")
        os.makedirs(temp_path, exist_ok=True)
        os.makedirs(output_path, exist_ok=True)
        work_path = os.path.join(temp_path, "work.json")
        repo = JsonWorkRepository(work_path)
        logger = Logger(False)
        service = SequentialBruteForceService(
            rar_path=REAL_RAR, unrar_path=REAL_UNRAR,
            charset=charset, min_len=min_len, max_len=max_len,
            temp_path=temp_path, output_path=output_path,
            work_repository=repo, logger=logger,
        )
        return service, repo

    def _save_work(self, repo, **kwargs):
        defaults = dict(
            version=1, rar_file="INPUT/123.rar", rar_sha256="testhash",
            rar_size_bytes=0, charset="x", min_len=1, max_len=1,
            attack_mode="SEQUENTIAL", status=WorkStatus.NEW,
            password_found=False, completed_colonies=[],
            current_colony=None, current_colony_index=-1,
            total_combinations_tried=0, total_colonies=1,
            total_combinations=1, created_at="2026-01-01T00:00:00",
            updated_at="2026-01-01T00:00:00", completed_at=None,
            flush_interval=100,
        )
        defaults.update(kwargs)
        state = WorkState(**defaults)
        repo.save(state)
        return state

    def _try_password_factory(self, correct=None, error_on=None, raise_kb_on=None):
        call_log = []

        def side_effect(rar_path, unrar_path, password, timeout=10):
            call_log.append(password)
            if raise_kb_on is not None and password == raise_kb_on:
                raise KeyboardInterrupt
            if error_on is not None and password == error_on:
                return PasswordTestResult.ERROR
            if correct is not None and password == correct:
                return PasswordTestResult.CORRECT
            return PasswordTestResult.INCORRECT

        return side_effect, call_log

    def _run(self, service):
        with silence_stdout():
            return service.execute()


class TestSequentialBruteForceResume(ResumeTestBase):
    # Scenario 2: restart with a completed colony -> skip, no spawn
    def test_skip_completed_colony(self):
        service, repo = self._make_service("ab", 1, 2)
        self._save_work(repo, charset="ab", min_len=1, max_len=2,
                        status=WorkStatus.PAUSED, completed_colonies=[1],
                        current_colony=None, current_colony_index=-1,
                        total_colonies=2, total_combinations=6)
        side_effect, _ = self._try_password_factory()
        with mock.patch.object(WinrarService, "tryPassword", side_effect=side_effect), \
             mock.patch.object(WinrarService, "extractContent", return_value="/tmp"), \
             mock.patch.object(TermiteService, "spawnColony", wraps=TermiteService.spawnColony) as spawn_mock:
            self._run(service)
        spawned_lengths = [call.args[2] for call in spawn_mock.call_args_list]
        self.assertNotIn(1, spawned_lengths)
        self.assertIn(2, spawned_lengths)
        work = repo.load()
        self.assertEqual(work.status, WorkStatus.COMPLETED)
        self.assertEqual(sorted(work.completed_colonies), [1, 2])

    # Scenario 3: resume partially processed colony from index+1 deterministically
    def test_resume_partial_colony(self):
        service, repo = self._make_service("abc", 1, 1)
        self._save_work(repo, charset="abc", min_len=1, max_len=1,
                        status=WorkStatus.PAUSED, current_colony=1,
                        current_colony_index=0, total_colonies=1,
                        total_combinations=3)
        side_effect, call_log = self._try_password_factory(correct="c")
        with mock.patch.object(WinrarService, "tryPassword", side_effect=side_effect), \
             mock.patch.object(WinrarService, "extractContent", return_value="/tmp"):
            result = self._run(service)
        self.assertTrue(result)
        self.assertNotIn("a", call_log)   # index 0 skipped
        self.assertIn("b", call_log)      # index 1 tried
        self.assertIn("c", call_log)      # index 2 tried (winner)
        work = repo.load()
        self.assertEqual(work.status, WorkStatus.FOUND)
        self.assertTrue(work.password_found)

    # Scenario 4: Ctrl+C -> PAUSED persisted on disk
    def test_ctrl_c_pauses(self):
        service, repo = self._make_service("abcde", 1, 1)
        self._save_work(repo, charset="abcde", min_len=1, max_len=1,
                        status=WorkStatus.NEW, total_colonies=1,
                        total_combinations=5)
        side_effect, _ = self._try_password_factory(raise_kb_on="c")
        with mock.patch.object(WinrarService, "tryPassword", side_effect=side_effect), \
             mock.patch.object(WinrarService, "extractContent", return_value="/tmp"):
            self._run(service)
        work = repo.load()
        self.assertEqual(work.status, WorkStatus.PAUSED)
        self.assertEqual(work.current_colony, 1)
        self.assertEqual(work.current_colony_index, 1)  # a,b confirmed; c interrupted

    # Scenario 5: abrupt close after checkpoint -> resume from last flush, never skip
    def test_resume_after_abrupt_close(self):
        service, repo = self._make_service("abcde", 1, 1, flush_interval=2)
        # Simulate a crash: last checkpoint saved index 1, status still RUNNING
        self._save_work(repo, charset="abcde", min_len=1, max_len=1,
                        status=WorkStatus.RUNNING, current_colony=1,
                        current_colony_index=1, flush_interval=2,
                        total_colonies=1, total_combinations=5)
        side_effect, call_log = self._try_password_factory()
        with mock.patch.object(WinrarService, "tryPassword", side_effect=side_effect), \
             mock.patch.object(WinrarService, "extractContent", return_value="/tmp"):
            self._run(service)
        self.assertNotIn("a", call_log)
        self.assertNotIn("b", call_log)
        self.assertIn("c", call_log)
        self.assertIn("d", call_log)
        self.assertIn("e", call_log)
        work = repo.load()
        self.assertEqual(work.status, WorkStatus.COMPLETED)

    # Scenario 6: all colonies completed -> COMPLETED, no work done
    def test_all_completed(self):
        service, repo = self._make_service("ab", 1, 2)
        self._save_work(repo, charset="ab", min_len=1, max_len=2,
                        status=WorkStatus.PAUSED, completed_colonies=[1, 2],
                        total_colonies=2, total_combinations=6)
        side_effect, call_log = self._try_password_factory()
        with mock.patch.object(WinrarService, "tryPassword", side_effect=side_effect), \
             mock.patch.object(WinrarService, "extractContent", return_value="/tmp"), \
             mock.patch.object(TermiteService, "spawnColony", wraps=TermiteService.spawnColony) as spawn_mock:
            self._run(service)
        self.assertEqual(spawn_mock.call_count, 0)
        self.assertEqual(call_log, [])
        work = repo.load()
        self.assertEqual(work.status, WorkStatus.COMPLETED)

    # Scenario 7: password found -> FOUND, password_found=True, no password in work.json
    def test_password_found(self):
        service, repo = self._make_service("abc", 1, 1)
        self._save_work(repo, charset="abc", min_len=1, max_len=1,
                        status=WorkStatus.NEW, total_colonies=1,
                        total_combinations=3)
        side_effect, _ = self._try_password_factory(correct="b")
        with mock.patch.object(WinrarService, "tryPassword", side_effect=side_effect), \
             mock.patch.object(WinrarService, "extractContent", return_value="/tmp"):
            result = self._run(service)
        self.assertTrue(result)
        work = repo.load()
        self.assertEqual(work.status, WorkStatus.FOUND)
        self.assertTrue(work.password_found)
        with open(repo.work_path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        self.assertNotIn("password", raw)

    # Scenario 9: transient technical error -> PAUSED, progress not advanced
    def test_technical_error_pauses_without_advancing(self):
        service, repo = self._make_service("abc", 1, 1)
        self._save_work(repo, charset="abc", min_len=1, max_len=1,
                        status=WorkStatus.NEW, total_colonies=1,
                        total_combinations=3)
        side_effect, _ = self._try_password_factory(error_on="b")
        with mock.patch.object(WinrarService, "tryPassword", side_effect=side_effect), \
             mock.patch.object(WinrarService, "extractContent", return_value="/tmp"):
            self._run(service)
        work = repo.load()
        self.assertEqual(work.status, WorkStatus.PAUSED)
        self.assertEqual(work.current_colony_index, 0)  # a confirmed; b errored, not advanced


class TestControllerIdentity(unittest.TestCase):
    """Scenarios 1, 8, 10: identity verification at the Controller level."""

    def _make_controller(self, work_path):
        config = Config()
        logger = Logger(False)
        repo = JsonWorkRepository(work_path)
        deps = {"logger": logger, "work_repository": repo}
        controller = Controller(PROJECT_ROOT, config, deps)
        return controller, repo

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.work_path = os.path.join(self.tmp, "work.json")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    # Scenario 1: first execution without work.json
    def test_first_run_creates_new_work(self):
        self.assertFalse(os.path.isfile(self.work_path))
        controller, repo = self._make_controller(self.work_path)
        self.assertTrue(repo.exists())
        work = repo.load()
        self.assertEqual(work.status, WorkStatus.NEW)
        self.assertTrue(work.rar_sha256)  # hash computed, non-empty
        self.assertEqual(work.charset, real_charset())

    # Scenario 8: RAR/config change -> archive previous (preserved) + create new
    def test_identity_mismatch_archives_and_creates_new(self):
        charset = real_charset()
        config = Config()
        min_len = int(config.getConfig("GEN_CONFIG_LEN_MIN_SIZE_CHAR_SELECT_TO_CRACK"))
        max_len = int(config.getConfig("GEN_CONFIG_LEN_MAX_SIZE_CHAR_SELECT_TO_CRACK"))
        attack_mode = config.getConfig("GEN_CONFIG_ATTACK_MODE")
        # Pre-save a work with a fake (different) RAR hash
        pre = WorkState(
            rar_file="INPUT/123.rar", rar_sha256="f" * 64, rar_size_bytes=0,
            charset=charset, min_len=min_len, max_len=max_len, attack_mode=attack_mode,
            status=WorkStatus.PAUSED, completed_colonies=[2],
            current_colony=3, current_colony_index=456,
            total_colonies=max_len - min_len + 1, total_combinations=1000,
            created_at="2026-01-01T00:00:00", updated_at="2026-01-01T00:00:00",
        )
        JsonWorkRepository(self.work_path).save(pre)
        controller, repo = self._make_controller(self.work_path)
        # Original preserved as archived
        archived = [f for f in os.listdir(self.tmp) if f.startswith("work.archived.")]
        self.assertEqual(len(archived), 1)
        # New work created with the real hash
        work = repo.load()
        self.assertNotEqual(work.rar_sha256, "f" * 64)
        self.assertTrue(work.rar_sha256)
        self.assertEqual(work.status, WorkStatus.NEW)
        self.assertEqual(work.completed_colonies, [])

    # Scenario 10: corrupt work.json -> backup (preserved) + create new
    def test_corrupt_work_backed_up_and_new_created(self):
        with open(self.work_path, "w", encoding="utf-8") as f:
            f.write("{this is not valid json")
        controller, repo = self._make_controller(self.work_path)
        backup = [f for f in os.listdir(self.tmp) if f.startswith("work.corrupt.")]
        self.assertEqual(len(backup), 1)
        work = repo.load()
        self.assertEqual(work.status, WorkStatus.NEW)


if __name__ == "__main__":
    unittest.main(verbosity=2)
