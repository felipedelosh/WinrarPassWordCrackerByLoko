# CLAUDE.md — WinrarPassWordCrackerByLoko

> FelipedelosH · 2026
> Scope: repository-wide development instructions. This project is an educational, local RAR password-recovery tool for archives the operator owns or is authorized to access.

## 1. RED FLAGS — MUST FOLLOW

- NEVER change public method names, parameters, return types, `.env` keys, or dependency-dictionary keys without explicitly identifying affected callers and obtaining approval.
- NEVER bypass `Application` contracts by importing concrete `Infrastructure` services into application-facing code. Build concrete objects in `CORE/DependencyInjector.py`.
- NEVER replace the existing termite/colony design or sequential execution flow unless the task explicitly requests it.
- NEVER silently swallow exceptions (`except: pass`, `except Exception: return False`). Distinguish incorrect passwords from infrastructure failures.
- NEVER expose recovered passwords in logs, stack traces, debug output, or version-controlled files. Explicitly flag existing behavior that does so.
- NEVER execute a brute-force run, inspect private archive contents, or overwrite extracted files during a refactor unless explicitly authorized.
- NEVER introduce third-party libraries or change configuration formats without approval. Prefer the Python standard library and already-declared dependencies.
- ALWAYS inspect the relevant implementation, contract, and caller before editing. Preserve working behavior and make the smallest requested change.

## 2. PROJECT IDENTITY

- **Project:** WinrarPassWordCrackerByLoko.
- **Language:** Python; verify interpreter version and `requirements.txt` before using version-specific syntax.
- **Purpose:** Generate candidate passwords for authorized RAR recovery using `UnRAR.exe`.
- **Architecture goal:** Gradual hexagonal architecture with mirrored contracts and concrete implementations; migration is incremental, not a license to rewrite unrelated modules.
- **Current strategy:** Sequential brute force. `RANDOM` is a planned strategy; do not claim it exists until implemented.
- **Domain metaphor:** Each candidate may be represented as a physical `.txt` **termite**; a set of termites for a password length is a **colony**. Preserve the user's terminology.

## 3. DIRECTORY MAP

```text
main.py                       # Composition and startup
.env / characters.txt         # Local configuration and character source
INPUT/                       # RAR inputs
OUTPUT/files/                 # Extracted files
OUTPUT/log/                   # Execution logs
TEMP/                         # Temporary termite colonies
src/
  Application/services/CRACKER/IBruteForceService.py
  Infrastructure/services/CRACKER/SequentialBruteForceService.py
  Infrastructure/services/{TermiteService,WinrarService,PasswordCombinationGenerator,BeautifulPrinter}.py
  CORE/{Config,DependencyInjector,FolderController,Logger}.py
  Models/Enums/Attack.py
  controllers/Controller.py
```

The directory map is a guide to the currently discussed architecture; confirm on-disk paths before modifying imports or moving files.

## 4. ARCHITECTURE AND DEPENDENCY INJECTION

- `Application/` declares interfaces (use `ABC` and `@abstractmethod`); contracts describe behavior, not algorithm internals.
- `Infrastructure/` implements those contracts and handles external systems, files, processes, and presentation helpers.
- `CORE/DependencyInjector.py` is the composition root: load/resolve dependencies, instantiate concrete implementations, and return the dependency dictionary.
- `controllers/Controller.py` receives `path`, `config`, and `dependencies` through its constructor. It chooses/delegates strategy and should not instantiate concrete crackers.
- `main.py` constructs configuration, obtains dependencies through the injector, constructs Controller, runs it, and saves logs in `finally`.
- Use a general `IBruteForceService` for interchangeable implementations (e.g. sequential/random), rather than one interface per strategy unless different behavior genuinely requires it.
- Preserve the `execute()` contract for existing implementations until a coordinated interface change is requested.
- Keep one shared `Logger` instance across injected services and Controller; avoid independently constructing another logger in Controller.
- When adding a strategy: implement the general contract, wire it in the injector, and update selection through `Attack`/configuration without leaking a concrete type into Controller.

## 5. CODE STYLE

- Maintain existing project conventions: `UpperCamelCase` classes; existing `lowerCamelCase` public methods such as `bruteForce`, `saveLogs`, `spawnColony`; `I` prefix for interfaces; `UPPER_SNAKE_CASE` constants and environment keys.
- Prefer explicit constructor dependencies, type hints, small cohesive methods, and clear names.
- Use `snake_case` for new private helpers where not inconsistent with adjacent code; do not mass-rename existing APIs.
- For new/modified Python modules, keep a brief descriptive docstring; avoid redundant commentary and giant scaffolds.
- Use `os.path`/`pathlib` safely; resolve relative configured paths against the project root, and validate inputs before I/O.
- Do not mix logging, console progress, and business results unnecessarily. `BeautifulPrinter` owns progress display; `Logger` owns operational logs.

## 6. ERROR HANDLING, SECURITY, AND OBSERVABILITY

- Validate `.env` values, range boundaries (`min_len <= max_len`), empty character sets, paths, file types, and required executables at startup.
- Catch specific expected exceptions where possible; log actionable context and re-raise or return an explicit failure. Do not treat timeouts/process failures as wrong passwords.
- Never use `shell=True` to construct an UnRAR command from user-controlled inputs; use argument lists and sensible timeouts.
- Inspect archive entries and extraction destinations before allowing overwrite or traversal outside the intended output directory.
- Avoid logging passwords or unnecessarily printing complete extracted file contents; report outcomes and metadata instead.
- `INFO`: lifecycle and meaningful steps; `WARN`: recoverable problems; `ERROR`: failed operations; avoid excessively noisy per-candidate file logs.
- Protect existing output and temporary data during refactors; do not silently delete previous runs.

## 7. TESTING AND CHANGE WORKFLOW

- Prefer fast unit tests with mocked subprocess and filesystem behavior. Do not require real brute-force execution for architecture tests.
- Cover happy path, boundaries, and failure path for any modified behavior.
- Verify that concrete crackers are instances of `IBruteForceService`, and that Controller receives and calls the injected dependency.
- Check import consistency (`src.Application`, `src.Infrastructure`, `src.CORE`) with how `main.py` starts the package.
- Distinguish verification performed (syntax/unit tests) from tests not run (real RAR extraction, long brute force).
- Before editing: read the relevant files and summarize the minimal proposed change. When asked only to analyze, do not edit.

## 8. RESPONSE STYLE AND SAFE REFACTOR CHECKLIST

- Reply in Spanish unless the user requests otherwise. Code identifiers, comments, and file-level documentation may remain in English.
- Explain the exact file path and minimal edits; prefer complete copy-paste-ready code when requested.
- Do not claim a migration is finished while legacy imports, duplicate classes, or invalid paths remain.
- If a dependency's constructor or config key is unknown, inspect the source or state the uncertainty; do not invent it.

Before reporting completion, confirm:

- [ ] Public contracts and configuration keys are preserved or explicitly approved for change.
- [ ] Controller depends on the abstraction; concrete classes are assembled only by DependencyInjector.
- [ ] One logger instance is shared.
- [ ] No unrelated algorithm, colony persistence, or output behavior changed.
- [ ] Errors are not swallowed, and secrets are not logged.
- [ ] Relevant tests/checks are run and limitations are disclosed.

## 9. INTERNAL REFERENCES — READ ON DEMAND

- Dependency wiring: `@src/CORE/DependencyInjector.py`, `@src/controllers/Controller.py`, `@main.py`.
- Contract pattern: `@src/Application/services/CRACKER/IBruteForceService.py`.
- Sequential strategy: `@src/Infrastructure/services/CRACKER/SequentialBruteForceService.py`.
- Termite lifecycle: `@src/Infrastructure/services/TermiteService.py`.
- Configuration and logging: `@src/CORE/Config.py`, `@src/CORE/Logger.py`, `@.env` (never reproduce secret values).

Only load references relevant to the current task. If a referenced file is missing, locate its current path rather than creating a duplicate.
