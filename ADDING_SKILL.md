# Adding the pyResToolbox Skill to Claude Code

This guide explains how to install the `pyRestToolbox` skill so that Claude Code
automatically loads the right tool-calling knowledge whenever you work on reservoir
engineering tasks.

---

## What is a skill?

A Claude Code skill is a Markdown file with a YAML front-matter header. When you
ask Claude a question that matches the skill's trigger description, it loads the
skill's content as additional context — telling Claude exactly how to call the
tools, which parameter names to use, which enum values are valid, and what
workflows make sense.

The skill in this repo (`SKILL.md`) covers all 108 tools in the pyResToolbox MCP
Server: PVT, inflow, nodal analysis, simulation support, DCA, material balance,
brine/CO2, heterogeneity, and geomechanics.

---

## Installation

### Step 1 — Find your Claude skills directory

Skills live in `~/.claude/skills/` (created automatically by Claude Code).

```bash
mkdir -p ~/.claude/skills
```

### Step 2 — Copy the skill file

From the root of this repository:

```bash
cp SKILL.md ~/.claude/skills/pyrestoolbox-mcp.md
```

Or with a direct path:

```bash
cp /path/to/pyrestoolbox-mcp/SKILL.md ~/.claude/skills/pyrestoolbox-mcp.md
```

### Step 3 — Copy the tools reference (optional but recommended)

The skill references `references/tools-reference.md` for complete parameter
details. Place it where the skill can find it, or simply keep it in the repo and
note its path for manual lookup:

```bash
mkdir -p ~/.claude/skills/references
cp guide/tools-reference.md ~/.claude/skills/references/tools-reference.md
```

### Step 4 — Verify

Open a new Claude Code session and ask:

```
What tools does pyResToolbox provide?
```

Claude should describe the 108 tools and their categories without you needing to
explain anything.

---

## Skill file structure

```
SKILL.md                          ← the skill (copy to ~/.claude/skills/)
guide/
  tools-reference.md              ← full parameter reference for all 108 tools
  pyRestToolbox_MCP_Formula_Reference.pdf  ← formula reference PDF
```

---

## What the skill teaches Claude

- **Parameter naming conventions** — `psd` vs `pwf`, `sg` vs `sg_g`, `method` vs
  `zmethod`, `z_method` vs `zmethod`
- **Valid enum values** — exact strings for all Literal fields (e.g. `"VALMC"`,
  `"DAK"`, `"SWOF"`, `"COR"`)
- **Tool signatures** — required vs optional parameters for all 108 tools
- **Validation constraints** — API range, gas SG range, Poisson's ratio bounds, etc.
- **Common workflows** — PVT analysis, well performance, simulation input
  generation, DCA, geomechanics drilling window
- **Error handling** — how to recover from the most common validation errors

---

## MCP server connection

The skill assumes the pyResToolbox MCP Server is running and connected to Claude.
There are two ways to run it:

### Option A — STDIO (recommended for Claude Code)

Add to your Claude Code MCP configuration (`~/.claude/mcp.json` or via
`claude mcp add`):

```json
{
  "pyrestoolbox": {
    "command": "uv",
    "args": [
      "run",
      "--directory", "/path/to/pyrestoolbox-mcp",
      "fastmcp",
      "run",
      "--no-banner",
      "server.py"
    ]
  }
}
```

### Option B — Docker / SSE (for shared or remote use)

```bash
cd pyrestoolbox-mcp
docker-compose up -d
```

Server runs at `http://localhost:8000/sse`.

---

## Updating the skill

When new tools are added to the server, update the skill:

1. Edit `SKILL.md` in this repo to add the new tool signatures and any new enum
   values.
2. Update `guide/tools-reference.md` with the full parameter details.
3. Copy the updated file to `~/.claude/skills/pyrestoolbox-mcp.md`.
4. Push the changes to the repo so other users get the update.

---

## Reference

- `SKILL.md` — skill file with YAML front-matter trigger conditions
- `guide/tools-reference.md` — complete parameter reference for all 108 tools
- `guide/pyRestToolbox_MCP_Formula_Reference.pdf` — formula derivation reference
- `test_new_geomech_tools.py` — direct MCP test for the 12 new geomechanics tools
