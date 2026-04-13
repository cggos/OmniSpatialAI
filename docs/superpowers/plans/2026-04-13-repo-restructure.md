# Repo Restructure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Optimize top-level directory naming to all-lowercase, reorganize loose files in `control_system/` and `ros/`, consolidate `slam/slam_faq/` into docs, and remove committed build artifacts.

**Architecture:** Three independent work packages executed in sequence — D (build artifacts) first to keep git clean, then A (bulk renaming), then C (internal reorganization + doc consolidation). All file moves use `git mv` to preserve history. Documentation files (`README.md`, `GEMINI.md`, `CLAUDE.md`, `mkdocs.yml`) are updated in the final task.

**Tech Stack:** git mv, bash, Markdown

---

## Task 1: Remove build artifacts from git tracking

**Files:**
- Modify: `Planning/mapping/build/` (remove from git index)
- No new files needed; root `.gitignore` already contains `build/`

- [ ] **Step 1: Untrack the build directory**

```bash
cd /opt/user_data/code/OmniSpatialAI
git rm -r --cached Planning/mapping/build/
```

Expected output: lines like `rm 'Planning/mapping/build/CMakeCache.txt'` etc. for each file.

- [ ] **Step 2: Verify the build directory still exists on disk but is untracked**

```bash
ls Planning/mapping/build/
git status Planning/mapping/build/
```

Expected: files still present on disk; git status shows them as untracked (or not shown at all since `.gitignore` has `build/`).

- [ ] **Step 3: Commit**

```bash
git add -u
git commit -m "chore: remove committed build artifacts from tracking

build/ is already covered by .gitignore; removing from index.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

## Task 2: Rename top-level module directories to lowercase

**Files renamed (git mv):**
- `ControlSystem/` → `control_system/`
- `GIS/` → `gis/`
- `Planning/` → `planning/`
- `ROS/` → `ros/`
- `SLAM/` → `slam/`

- [ ] **Step 1: Rename all five top-level directories**

```bash
cd /opt/user_data/code/OmniSpatialAI
git mv ControlSystem control_system
git mv GIS gis
git mv Planning planning
git mv ROS ros
git mv SLAM slam
```

- [ ] **Step 2: Fix the slam_framworks typo**

```bash
git mv slam/slam_framworks slam/slam_frameworks
```

- [ ] **Step 3: Verify the renames are staged**

```bash
git status --short | grep "^R"
```

Expected: ~6 rename entries beginning with `R  ControlSystem/ -> control_system/` etc.

- [ ] **Step 4: Commit**

```bash
git commit -m "refactor: rename top-level module dirs to lowercase

ControlSystem->control_system, GIS->gis, Planning->planning,
ROS->ros, SLAM->slam; also fix slam_framworks typo->slam_frameworks.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

## Task 3: Move loose MATLAB files into control_system/basics/

**Files:**
- Create dir: `control_system/basics/`
- Move: `control_system/StepResponse.m` → `control_system/basics/StepResponse.m`
- Move: `control_system/TransferFunction.m` → `control_system/basics/TransferFunction.m`

- [ ] **Step 1: Create the basics/ directory and move files**

```bash
cd /opt/user_data/code/OmniSpatialAI
mkdir control_system/basics
git mv control_system/StepResponse.m control_system/basics/StepResponse.m
git mv control_system/TransferFunction.m control_system/basics/TransferFunction.m
```

- [ ] **Step 2: Verify**

```bash
git status --short | grep "^R.*StepResponse\|^R.*TransferFunction"
ls control_system/basics/
```

Expected: two renamed entries; directory lists both `.m` files.

- [ ] **Step 3: Commit**

```bash
git commit -m "refactor(control_system): move loose .m files into basics/

StepResponse.m and TransferFunction.m now live alongside
DigitalSignalProcessing/ and Simulink/ rather than at the root.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

## Task 4: Move non-catkin content in ros/ into ros/extras/

**Files:**
- Create dir: `ros/extras/`
- Move: `ros/ros_matlab/` → `ros/extras/ros_matlab/`
- Move: `ros/ros_video/` → `ros/extras/ros_video/`
- Move: `ros/scripts/` → `ros/extras/scripts/`

- [ ] **Step 1: Create extras/ and move the three directories**

```bash
cd /opt/user_data/code/OmniSpatialAI
mkdir ros/extras
git mv ros/ros_matlab  ros/extras/ros_matlab
git mv ros/ros_video   ros/extras/ros_video
git mv ros/scripts     ros/extras/scripts
```

- [ ] **Step 2: Verify**

```bash
ls ros/extras/
git status --short | grep extras
```

Expected: `ros_matlab  ros_video  scripts` listed; staged renames visible.

- [ ] **Step 3: Commit**

```bash
git commit -m "refactor(ros): move non-catkin content into extras/

ros_matlab/, ros_video/, and scripts/ are not catkin packages;
grouping them under extras/ separates them from buildable packages.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

## Task 5: Consolidate slam/slam_faq/ into docs/SLAM/slam_qa/

**Files:**
- Move: `slam/slam_faq/slam_faq.md` → `docs/SLAM/slam_qa/slam_faq.md`
- Move: `slam/slam_faq/slam_faq_company.md` → `docs/SLAM/slam_qa/slam_faq_company.md`
- Move: `slam/slam_faq/slam_faq_gx.md` → `docs/SLAM/slam_qa/slam_faq_gx.md`
- Move: `slam/slam_faq/MYNTAI-QA.md` → `docs/SLAM/slam_qa/myntai_qa.md` (normalize filename)
- Move: `slam/slam_faq/README.md` → `docs/SLAM/slam_qa/slam_faq_index.md`
- Delete: `slam/slam_faq/` directory

- [ ] **Step 1: Move all faq files into docs/SLAM/slam_qa/**

```bash
cd /opt/user_data/code/OmniSpatialAI
git mv slam/slam_faq/slam_faq.md          docs/SLAM/slam_qa/slam_faq.md
git mv slam/slam_faq/slam_faq_company.md  docs/SLAM/slam_qa/slam_faq_company.md
git mv slam/slam_faq/slam_faq_gx.md       docs/SLAM/slam_qa/slam_faq_gx.md
git mv slam/slam_faq/MYNTAI-QA.md         docs/SLAM/slam_qa/myntai_qa.md
git mv slam/slam_faq/README.md            docs/SLAM/slam_qa/slam_faq_index.md
```

- [ ] **Step 2: Remove now-empty slam_faq/ directory**

```bash
rmdir slam/slam_faq
git status --short | head -20
```

Expected: 5 rename entries (`R  slam/slam_faq/... -> docs/SLAM/slam_qa/...`); `slam/slam_faq/` no longer exists.

- [ ] **Step 3: Commit**

```bash
git commit -m "refactor(slam): consolidate slam_faq/ into docs/SLAM/slam_qa/

FAQ and interview Q&A content belongs in docs alongside
slam_run_tips.md rather than as loose Markdown in the source tree.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

## Task 6: Update all documentation to reflect new paths

**Files:**
- Modify: `README.md`
- Modify: `GEMINI.md`
- Modify: `CLAUDE.md`
- Modify: `mkdocs.yml`

- [ ] **Step 1: Update README.md**

Replace the Key Modules section links and the directory structure block:

Old:
```markdown
- **[Control System](./ControlSystem/):** ...
- **[SLAM](./SLAM/):** ...
- **[GIS](./GIS/):** ...
- **[Planning](./Planning/):** ...
- **[ROS](./ROS/):** ...
```
New:
```markdown
- **[Control System](./control_system/):** ...
- **[SLAM](./slam/):** ...
- **[GIS](./gis/):** ...
- **[Planning](./planning/):** ...
- **[ROS](./ros/):** ...
```

Old directory structure block:
```
├── ControlSystem/      # Control theory & DSP (MATLAB)
├── GIS/                # Geographic Information Systems (Python)
├── Planning/           # Path planning & Mapping (C++)
├── ROS/                # ROS packages, URDFs, Gazebo simulations
├── SLAM/               # Visual Odometry, Mapping, SLAM frameworks
```
New:
```
├── control_system/     # Control theory & DSP (MATLAB)
│   └── basics/         # Transfer function & step response scripts
├── gis/                # Geographic Information Systems (Python)
├── planning/           # Path planning & Mapping (C++)
├── ros/                # ROS packages, URDFs, Gazebo simulations
│   └── extras/         # Non-catkin utilities (ros_matlab, ros_video, scripts)
├── slam/               # Visual Odometry, Mapping, SLAM frameworks
```

Old catkin build command:
```bash
catkin_make --source <path_to_omnispatialai>/ROS/
```
New:
```bash
catkin_make --source <path_to_omnispatialai>/ros/
```

- [ ] **Step 2: Update GEMINI.md**

Replace all occurrences of old paths:
- `ControlSystem` → `control_system`
- `GIS` → `gis`
- `Planning` → `planning`
- `ROS/` → `ros/`
- `SLAM/` → `slam/`
- `slam_framworks` → `slam_frameworks`
- `slam_faq` references → `docs/SLAM/slam_qa/`
- Update the catkin build example path from `ROS/` to `ros/`

- [ ] **Step 3: Update CLAUDE.md**

Replace all occurrences of old paths (same substitutions as GEMINI.md):
- `SLAM/visual_odometry/` → `slam/visual_odometry/`
- `SLAM/mapping/` → `slam/mapping/`
- `SLAM/visual_vocabulary/dbow_demos/` → `slam/visual_vocabulary/dbow_demos/`
- `Planning/mapping/` → `planning/mapping/`
- `ROS/` → `ros/`
- `slam_framworks` → `slam_frameworks`

- [ ] **Step 4: Update mkdocs.yml**

Add the migrated FAQ files to the SLAM FAQs nav section.

Old:
```yaml
    - SLAM FAQs:
      - SLAM Run Tips: SLAM/slam_qa/slam_run_tips.md
```
New:
```yaml
    - SLAM FAQs:
      - Overview: SLAM/slam_qa/slam_faq_index.md
      - SLAM Run Tips: SLAM/slam_qa/slam_run_tips.md
      - SLAM FAQ: SLAM/slam_qa/slam_faq.md
      - Company Q&A: SLAM/slam_qa/slam_faq_company.md
      - FAQ by GaoXiang: SLAM/slam_qa/slam_faq_gx.md
      - MYNTAI Q&A: SLAM/slam_qa/myntai_qa.md
```

- [ ] **Step 5: Verify no stale references remain**

```bash
grep -rn "ControlSystem\|/GIS\b\|/Planning\|/ROS\b\|/SLAM\b\|slam_framworks\|slam_faq" \
  README.md GEMINI.md CLAUDE.md mkdocs.yml
```

Expected: no matches (zero lines output).

- [ ] **Step 6: Commit**

```bash
git add README.md GEMINI.md CLAUDE.md mkdocs.yml
git commit -m "docs: update all path references after repo restructure

Rename ControlSystem->control_system, GIS->gis, Planning->planning,
ROS->ros, SLAM->slam; add new FAQ entries to mkdocs nav.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```
