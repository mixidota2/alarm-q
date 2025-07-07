# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Flet** application called "alearm-q" - a Python-based cross-platform app framework built on top of Flutter. The app is currently a simple counter application that demonstrates Flet's basic functionality.

## Development Commands

### Running the Application

**Desktop app:**
```bash
uv run flet run
```

**Web app:**
```bash
uv run flet run --web
```

**Alternative with Poetry:**
```bash
poetry install
poetry run flet run          # Desktop
poetry run flet run --web    # Web
```

### Code Quality

**Type checking:**
```bash
uv run mypy src/
```

**Linting:**
```bash
uv run ruff check src/
```

**Formatting:**
```bash
uv run ruff format src/
```

### Building for Distribution

**Android:**
```bash
flet build apk -v
```

**iOS:**
```bash
flet build ipa -v
```

**Desktop platforms:**
```bash
flet build macos -v
flet build linux -v
flet build windows -v
```

## Project Structure

- `src/main.py` - Main application entry point and UI logic
- `src/assets/` - Static assets (icons, splash screens)
- `storage/` - Runtime storage directory (ignored by git)
- `pyproject.toml` - Project configuration with both uv and poetry support

## Architecture

The application follows Flet's event-driven architecture:

- **Main function** (`main(page: ft.Page)`) - Entry point that receives a Page object
- **UI components** - Built using Flet's widget system (Text, FloatingActionButton, Container, etc.)
- **Event handlers** - Functions that respond to user interactions
- **State management** - Currently uses component-level state (counter.data)

## Key Dependencies

- `flet==0.28.3` - Core framework
- `flet[all]==0.28.3` - Development version with all features
- `mypy>=1.16.1` - Type checking
- `ruff>=0.12.2` - Linting and formatting

## Package Management

The project supports both **uv** (preferred) and **poetry** as package managers. The uv.lock file suggests uv is the primary choice for dependency management.