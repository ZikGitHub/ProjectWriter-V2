"""
run_tests.py -- Sequential test runner for ProjectWriter-V2.

Loads each test file directly from its path to avoid module-name
resolution issues, then runs them one at a time so live Ollama tests
don't collide with each other.

Usage (from project root, with venv activated):
    python tests/run_tests.py
"""
import sys
import os
import unittest
import importlib.util
import traceback

# Resolve paths relative to THIS file so the script works from any cwd
TESTS_DIR = os.path.abspath(os.path.dirname(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(TESTS_DIR, '../backend'))

# Make sure both dirs are importable BEFORE loading any test module
for p in (TESTS_DIR, BACKEND_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

# Ordered list: pure unit tests first, then live Ollama integration tests
TEST_FILES = [
    "test_state_manager",
    "test_dispatcher",
    "test_reducer",
    "test_planner",    # live -- llama3.2:1b
    "test_coder",      # live -- qwen2.5-coder:1.5b
    "test_orchestrator",  # live -- both models
]


def load_module(module_name: str):
    """
    Load a test module by file path, not by module-system lookup.
    Returns (module, error_string). On success error_string is None.
    """
    file_path = os.path.join(TESTS_DIR, f"{module_name}.py")
    if not os.path.exists(file_path):
        return None, f"File not found: {file_path}"
    try:
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        # Register in sys.modules so relative imports inside the test file work
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module, None
    except Exception:
        return None, traceback.format_exc()


def run_module(module_name: str) -> unittest.TestResult:
    print("\n" + "=" * 60)
    print(f"  RUNNING: {module_name}")
    print("=" * 60)

    module, err = load_module(module_name)
    if err:
        print(f"  [IMPORT ERROR] Could not load {module_name}:\n{err}")
        # Return a fake failing result so the summary reflects the error
        result = unittest.TestResult()
        result.errors.append((module_name, err))
        return result

    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(module)

    count = suite.countTestCases()
    if count == 0:
        print(f"  [WARNING] No test cases found in {module_name}")

    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    return runner.run(suite)


def main():
    overall_pass = True
    summary = []

    for module in TEST_FILES:
        result = run_module(module)
        passed = result.wasSuccessful()
        overall_pass &= passed
        label = "PASS" if passed else "FAIL"
        summary.append((
            module, label,
            result.testsRun,
            len(result.failures),
            len(result.errors),
            getattr(result, 'skipped', []),
        ))

    print("\n\n" + "=" * 60)
    print("  FINAL SUMMARY")
    print("=" * 60)
    print(f"  {'Module':<30} {'Result':<6}  {'Ran':>3}  {'Fail':>4}  {'Err':>4}  {'Skip':>4}")
    print("  " + "-" * 55)
    for module, label, ran, fails, errors, skipped in summary:
        flag = "[OK]  " if label == "PASS" else "[FAIL]"
        print(f"  {flag}  {module:<28} {label:<6}  {ran:>3}  {fails:>4}  {errors:>4}  {len(skipped):>4}")

    print("=" * 60)
    if overall_pass:
        print("  ALL TESTS PASSED")
    else:
        print("  SOME TESTS FAILED -- see details above")
    print("=" * 60)

    sys.exit(0 if overall_pass else 1)


if __name__ == "__main__":
    main()
