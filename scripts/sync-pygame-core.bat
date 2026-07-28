@echo off
REM Fetch latest pygame_core from origin/main (.gitmodules pins branch=main, update=merge)
REM and stage the new submodule pointer. Run 'git commit && git push' afterward to publish.
cd /d "%~dp0.."
git submodule update --remote --merge src/pygame_core
git add src/pygame_core
pause

REM ---------------------------------------------------------------------------
REM Workflow for pushing a NEW pygame_core change from this project's submodule:
REM   1. cd src/pygame_core
REM   2. git add . && git commit -m "..."   - capture the code change in pygame_core
REM   3. git push origin main               - publish to all consumers
REM   4. cd ../..                           - back to project root
REM   5. git add src/pygame_core            - bump the submodule gitlink
REM   6. git commit -m "Bump pygame_core"   - record the bump in the project
REM   7. git push                           - publish project's pointer bump
REM ---------------------------------------------------------------------------
