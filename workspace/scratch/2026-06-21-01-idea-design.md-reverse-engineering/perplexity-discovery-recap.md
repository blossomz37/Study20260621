# Recap from conversation with Perplexity about reverse engineering DESIGN.md



Here’s a concise recap you can paste into your local agent.

## Goal

We researched **DESIGN.md**, an open-source format from Google Labs/Stitch for describing a visual identity to AI coding agents. Its purpose is to give agents a persistent, structured understanding of a design system so they stop guessing colors, typography, spacing, and component behavior. 

## What DESIGN.md is

A `DESIGN.md` file combines:

- **YAML front matter** for machine-readable design tokens.
- **Markdown prose** for human-readable design rationale.

The tokens are the normative values; the prose explains why they exist and how they should be applied.

Typical token areas:

- Colors
- Typography
- Rounded/radius
- Spacing
- Components

Canonical prose sections usually include:

- Overview
- Colors
- Typography
- Layout
- Elevation
- Shapes
- Components
- Dos and Don’ts

## Intended use

DESIGN.md is meant to act as a bridge between:

- a brand/design system,
- AI coding agents,
- and downstream implementation formats.

It helps agents generate more consistent UI by giving them exact token values and design intent in a portable text file.

The CLI supports:

- `lint` — validate structure, references, and contrast
- `diff` — compare two versions of a design system
- `export` — convert to Tailwind/DTCG-related outputs
- `spec` — output the spec/reference

It also supports token references and component definitions.

## Project direction chosen

We selected **Option 1**:

**Reverse-engineer a live website into a DESIGN.md file.**

Core idea:
- Pick a real site or one of your own apps.
- Inspect the live UI.
- Infer the hidden design system.
- Reconstruct it as a clean `DESIGN.md`.
- Validate it.
- Export it.
- Demonstrate that the recovered system can reproduce the original look and feel.

## Why this option is strong

This was the strongest demo because it has a clean narrative:

1. Existing shipped UI
2. Reverse-engineered design rules
3. Formalized `DESIGN.md`
4. Validation with linting
5. Export to implementation format
6. Recreated or matched UI output

It clearly demonstrates the point of DESIGN.md as a contract between visual intent and AI-generated implementation.

## Suggested demo output

Final demo deliverables could include:

- Screenshot(s) of the original site
- A token audit table
- Your reconstructed `DESIGN.md`
- Lint results
- Exported Tailwind or DTCG output
- A recreated mini interface using the inferred design system
- A short explanation of what was inferred vs what had to be interpreted

## Recommended Mac stack

Suggested lightweight setup:

- **Node.js + npm**
- **VS Code**
- **Git**
- Optional small **Next.js**, **Svelte**, or **Astro** sandbox
- Browser devtools for inspecting styles
- Optional Playwright if you want scripted extraction

Reasoning:
- DESIGN.md itself is just Markdown + YAML.
- The main official dependency is the npm CLI.
- You do not need a heavy specialized reverse-engineering environment.

## Requirements and dependencies

Important notes:

- The format is still **alpha**, so the schema and CLI may evolve.
- The main dependency is the official npm package.
- You need normal npm registry access.
- If an agent is going to use the file automatically, it must be able to read local project files or be given the file directly.

You do **not** need:

- a database
- a browser extension
- an MCP server
- a proprietary SDK
- a large infrastructure setup

## Do you need the GitHub ZIP?

**Not required.**

You only really need:
- the spec/reference,
- the CLI,
- and your own `DESIGN.md` working file.

Downloading the repository as a ZIP is only useful if you want:

- local examples
- offline docs
- to inspect the source
- to browse the CLI/package structure
- to use the reference repo as teaching material

So: **helpful, but optional**.

## Practical workflow to hand to your local agent

Use this as the likely execution plan:

1. Choose a target website.
2. Capture screenshots of key pages/components.
3. Inspect CSS/design patterns with browser devtools.
4. Extract probable tokens:
- brand colors
- type scale
- font families
- spacing scale
- border radius
- button/input/card styles
5. Group repeated patterns into component definitions.
6. Write a first-pass `DESIGN.md`.
7. Run linting and fix issues.
8. Export to Tailwind or DTCG.
9. Build a small reproduction page.
10. Compare original vs recreated UI and document fidelity gaps.

## Suggested evaluation criteria

Have the local agent judge the reverse-engineered result on:

- Token consistency
- Component coverage
- Visual similarity
- Accessibility/contrast
- Ease of reuse by another agent
- Portability into a frontend stack

## Framing for your educational/demo mission

Good framing:
- “Can we infer a hidden design system from a shipped interface?”
- “Can DESIGN.md turn observed UI patterns into a reusable agent-readable contract?”
- “How much of brand identity can be reconstructed from production HTML/CSS alone?”

That makes the demo about both:
- reverse engineering,
- and agent interoperability.

## One-sentence handoff

We are building a demo that reverse-engineers a live website into a structured `DESIGN.md`, validates it, exports it, and uses it to recreate the site’s visual system as proof that DESIGN.md can capture and transfer design intent to AI coding agents.
