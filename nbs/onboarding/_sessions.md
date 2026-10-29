# Onboarding sessions

A log of the onboarding sessions with new MARIS team members. Each entry records what was covered, which parts of the guide were hard to follow, and how long it took. Use it to improve the onboarding pages and to plan the next session. Write about the material, not about the person.

## 2026-10-28 · Session 1 · 1 hour

**Covered:** Stage 1, step 1 (WSL with Ubuntu, Windows Terminal). Terminal basics with the cheatsheet: moving between folders, listing files. What Git and GitHub are. Cloning marisco.

**Challenging:** Command options and arguments (`ls -ah`, `cd my-new-dir`) were new. The idea of GitHub as a shared copy, with a full local copy for each person, was hard to explain without diagrams. Cloning over SSH failed because no SSH key was set up, so marisco was cloned over HTTPS instead.

**Guide changes:** Stage 1 reordered: VS Code and GitHub now come before uv and Rust. `gh auth login` now creates and uploads the SSH key. Added an explanation of Git and GitHub, of the VS Code WSL extension, and links to beginner shell and Git lessons (9a59156).

**Next:** VS Code with the WSL extension (step 2), connecting to GitHub with `gh auth login` and SSH (step 3), then uv and Rust (step 4).

## 2026-10-29 · Session 2 · 1 hour

**Covered:** Stage 1, steps 2 to 5. VS Code with the WSL extension, and opening `~/.bashrc` with `code`. Git name and email, VS Code as Git's editor, and `git config --list` to check the settings. `gh` installed, and `gh auth login` with a new SSH key. Removing the session 1 HTTPS clone and cloning marisco again over SSH. uv and Rust. Claude Code in WSL, signed in with a Pro account.

**Challenging:** The areas of the VS Code window, such as the terminal panel, needed an explanation. Removing the earlier clone needed `rm -rf`, so the difference between `rm -r` and `rm -rf`, and the danger of `rm -rf`, needed an explanation. What uv does was not clear without background: Python as a toolbox, packages as plugins or Lego bricks, marisco's dependencies in `pyproject.toml`, and one environment per project instead of one for the whole computer.

**Went well:** `gh auth login` created and uploaded the SSH key with no problems, and cloning over SSH worked.

**Guide changes:** Step 2 describes the areas of the VS Code window and links VS Code's user interface page and tutorial. Step 3 sets VS Code as Git's editor and checks the settings with `git config --list`. Step 4 explains packages, dependencies and environments before uv is installed, and why the workspace needs Rust. Step 6 opens with what aai-ws and aai-coding do. The cheatsheet adds `rm -r` and `rm -rf`, with a warning.

**Next:** Step 6 (aai-ws workspace), step 7 (add marisco), step 8 (open marisco in VS Code), then the setup check.
