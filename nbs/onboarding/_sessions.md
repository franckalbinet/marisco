# Onboarding sessions

A log of the onboarding sessions with new MARIS team members. Each entry records what was covered, which parts of the guide were hard to follow, and how long it took. Use it to improve the onboarding pages and to plan the next session. Write about the material, not about the person.

## 2026-10-28 · Session 1 · 1 hour

**Covered:** Stage 1, step 1 (WSL with Ubuntu, Windows Terminal). Terminal basics with the cheatsheet: moving between folders, listing files. What Git and GitHub are. Cloning marisco.

**Challenging:** Command options and arguments (`ls -ah`, `cd my-new-dir`) were new. The idea of GitHub as a shared copy, with a full local copy for each person, was hard to explain without diagrams. Cloning over SSH failed because no SSH key was set up, so marisco was cloned over HTTPS instead.

**Guide changes:** Stage 1 reordered: VS Code and GitHub now come before uv and Rust. `gh auth login` now creates and uploads the SSH key. Added an explanation of Git and GitHub, of the VS Code WSL extension, and links to beginner shell and Git lessons (9a59156).

**Next:** VS Code with the WSL extension (step 2), connecting to GitHub with `gh auth login` and SSH (step 3), then uv and Rust (step 4).
