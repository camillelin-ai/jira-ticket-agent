# Ticket Routing Logic — Obsidian Program

This file is read by the Jira ticket agent at runtime. Use it to reason about which project,
which epic parent, and which field values to assign when input is ambiguous.

---

## 1. Project Selection: EC vs AVP

### Primary Rule

| Work type | Project | Signal words |
|---|---|---|
| **AVP** | FMS product | "FMS", "Hive", "fleet management", "UI", "UX", "HMI", "frontend", "backend API", "fleet control", "tablet", "reporting", "shift", "site config", "deployment", "cluster", "customer-facing" |
| **EC** | Autonomy stack | "stack", "mission planner", "bedrock", "cloud supervisor", "behavior tree", "perception", "DbW", "localization", "SLAM", "map tooling", "simulation", "networking", "regression", "metrics", "bringup", "on-prem", "MQTT", "proto", "vehicle compute" |

### Ambiguous Cases — Resolve Explicitly

**Fuel Bay / Staging Points:**
- FMS commands, fuel level display in Hive, cycle state UI, FMS alerting → **AVP-57541**
- Mission planner behavior tree, stack-side cycle states (QueuedForFuel/Fueling), MQTT fuel level extraction, bedrock constants → **EC-16105**
- If the action item mentions both sides, split into two tickets.

**Dump Script:**
- Hive UI for authoring/editing/deleting dump scripts, FMS dispatch with dump config → **AVP-57421**
- Stack execution of dump sequences, DumpBedConfig proto, behavior tree, hopper/paddock autonomy logic, authority-gated spot selection → **EC-12454**
- If assignee is Walter Wang or an autonomy engineer → prefer EC. If Anisha Jain or Avi Agarwal → prefer AVP.

**HMI:**
- Manual haul truck fleet control UI → **AVP-58172**
- Onboard tablet (loader/dozer) → **AVP-43609**

**Ground Truth Network / Rajant:**
- On-prem network, mesh install, vehicle connectivity, network drop testing → **EC-15497**
- FMS-side network visualization → use closest AVP epic based on context

---

## 2. AVP Epic Map (children of AVP-34993)

Parent of all FMS/Obsidian V4 AVP work: **AVP-34993** (C^3: C-Cube: Fleet Management)

| Epic Key | Jira Summary | GDoc Deliverable Name | Notes |
|---|---|---|---|
| AVP-57421 | [Obsidian V4] Dump script page | Dump script creation page/modal | |
| AVP-57537 | [Obsidian V4] Dump zone configuration | Dump zone configuration | |
| AVP-57539 | [Obsidian V4] Mission Page | Mission page | |
| AVP-57541 | [Obsidian V4] Fuel Bay / Staging Points | Fuel Bay / Staging Points | |
| AVP-57543 | [Obsidian V4] Loader V2 | Loader V2 | |
| AVP-57546 | [Obsidian V4] Update FMS UI map dynamically | Updating FMS UI map dynamically | Dynamic map visualization (Three.js, drone imagery) is scope under this epic |
| AVP-58171 | Heidelberg Cluster - Prod | Heidelberg customer cluster | Production environment — see routing logic below |
| AVP-58173 | Heidelberg Cluster - Non-Prod | Heidelberg customer cluster | Non-production environment — see routing logic below |
| AVP-58172 | [Obsidian V4] Manual truck HMI | Manual haul trucks | |
| AVP-43609 | SDS - Mining Product HMI UI/UX | Tablet experience / Maps & HMI | |
| AVP-49321 | Report & Analytics for Mining | Non-Autonomy Deliverables | Reporting, analytics, shift/exception/variance reports |
| AVP-51568 | Site Configuration | Non-Autonomy Deliverables | Timezone, shift days, speed limits, unit settings |
| AVP-55510 | [C^3][FMS]: Shift Management | Non-Autonomy Deliverables | Shift scheduling, handover, shift definition |
| AVP-55524 | Time Governance | Non-Autonomy Deliverables | Equipment time classification and allocation |
| AVP-53044 | Fleet Management Productionization | Non-Autonomy Deliverables | FMS reliability, stability, tech debt |

### Heidelberg Cluster Routing (AVP-58171 vs AVP-58173)

Both epics map to the same "Heidelberg customer cluster" deliverable. Route based on the nature of the work:

- **AVP-58171 (Prod)**: Work that affects what customers and operators see and use in the live environment. Infrastructure that serves real operations. Anything that needs to be stable, release-gated, or approved before going live.
- **AVP-58173 (Non-Prod)**: Setup, validation, testing, and configuration work done before or in parallel with prod. Work that is iterative, experimental, or serves internal verification purposes.

Reason from the action item's intent — is this making something available to real users, or is it preparing/testing/verifying before that happens?

### Non-Autonomy Deliverables Routing

Action items may appear under a "Non-Autonomy Deliverables" section heading in the doc without naming the specific deliverable. In that case, match the action item to one of the five epics above based on what it's about:

- Analytics, reports, data exports, dashboards → **AVP-49321**
- Site-level settings, configuration pages, admin preferences → **AVP-51568**
- Shift definition, scheduling, handover → **AVP-55510**
- Time tracking, time categories, equipment time allocation → **AVP-55524**
- Anything about FMS reliability, uptime, tech debt, or productionization → **AVP-53044**

Do not prompt the reporter for clarification on these — reason from the action item text and pick the closest match.

---

## 3. EC Epic Map (children of EC-11955)

Parent of all Obsidian V4 EC/stack work: **EC-11955**

| Epic Key | Jira Summary | GDoc Name | Notes |
|---|---|---|---|
| EC-12454 | Obsidian V4 Capability: Managed and Unmanaged Dumping Operations | Hopper Dumping | GDoc uses "Hopper Dumping"; also covers Paddock Dumping action items (feature mostly complete) |
| EC-16103 | Obsidian V4 Capability: Wheel Loader Loading | Wheel Loader | |
| EC-16104 | Obsidian V4 Capability: Bench Loading | Bench Loading | |
| EC-16105 | Obsidian V4 Capability: Fuel Bay | Fuel Bay (stack/mission planner) | |
| EC-16107 | Obsidian V4 Capability: Mixed Operation | Mixed Operation | |
| EC-16122 | Obsidian V4 Capability: Triple Leader Follower | Triple Leader Follower | |
| EC-16134 | Obsidian V4 Subsystem: Map Workflow | Map Improvements | |
| EC-16183 | Obsidian V4 Development: Multi-Ego Simulation | Multi-Ego Simulation | Full name in GDoc; do not match to generic "simulation" references |
| EC-16190 | Obsidian V4 Development: Stability, Robustness, Performance Metrics | Stability, Robustness, Performance Metrics | |
| EC-16410 | Obsidian V4 Development: Uncertainty Framework | Uncertainty Framework | |
| EC-15497 | Obsidian V4 Development: On-prem network ground truth | On-prem network ground truth integration | |
| EC-16174 | Obsidian V4 Operations: Rockwell Buildout | Rockwell Buildout | Jira category is "Operations" but appears under "Development" section in meeting notes |

---

## 4. Epic Selection Logic

1. **Explicit Jira key in the doc line** (e.g., "[EC-16104]") → use that directly.
2. **Section context** — the meeting heading or parent requirement doc heading is strong signal. Action item under a "Bench Loading" section → EC-16104. Action item under "Non-Autonomy Deliverables" → apply routing rules in Section 2.
3. **Keyword and semantic match** — match action item text against GDoc Name, Jira Summary, and Notes columns above.
4. **Assignee** — cross-reference team_context.md for who is currently working on what area.
5. **If still ambiguous** — pick the closest match, show uncertainty in the preview, and prompt the reporter to confirm. Bias toward action: a ticket in the slightly wrong epic is better than no ticket.

---

## 5. Team Context

See `team_context.md` for the current person → feature area mapping. That file is updated after each approved ticket batch and is the primary source for assignee inference when no assignee is specified in the doc.

Static fallback table (use only when team_context.md has no signal):

| Person | Primary Area | Default Epic(s) |
|---|---|---|
| Walter Wang | Mission Planner / Dumping | EC-12454, EC-16105 |
| Avi Agarwal | FMS backend / Dump Zone / Mission | AVP-57537, AVP-57539, AVP-57421 |
| Anisha Jain | FMS frontend / UI | AVP-57421, AVP-57537, AVP-57543 |
| Kamil Nocon | Fuel Bay, Sim, Map | EC-16105, EC-16183, AVP-57541, AVP-57546 |
| Wenkai Ren / Li Jin | Bench Loading | EC-16104 |
| Zeyuan Jin | Wheel Loader | EC-16103 |
| Peter Redman | Mixed Operation | EC-16107 |
| Abhijit Chilukuri | Triple LF | EC-16122 |
| Jensen Solar | Metrics | EC-16190 |
| Tom Jennings | Rockwell, Network | EC-16174, EC-15497 |
| Camille Lin | Network, Connectivity | EC-15497 |
| Pankaj Saini | Reporting, Cluster | AVP-49321, AVP-58171 |
| Shreya Vemuri | Mission Page, Shift | AVP-57539, AVP-55510 |
| Naveen Kumar Aproop | Uncertainty | EC-16410 |
| Huaiqian Shou | Slope Handling | EC-16503, EC-16500, EC-16668 |

---

## 6. Carryover Task Detection

The doc is the primary source — no revision history API needed.

1. Before creating a ticket for an action item, scan all previous sprint sections (`## MMM DD, YYYY` headers earlier in the same doc) for semantically similar text by the same assignee.
2. Found in a prior section **with a linked ticket key inline** → state = **carryover, already ticketed** → propose linking, not creating.
3. Found in a prior section **without a linked ticket key** → state = **carryover, no ticket** → create, but flag in preview.
4. Found in 2+ prior sections → **recurring carry-over** — flag explicitly.

---

## 7. Field Inference Rules

### Priority
- Default: **P1**
- P0: blocking, safety, demo-critical, customer milestone, production down — should also be stated inline in the doc
- P2: nice to have, post-V4, stretch goal — should also be stated inline in the doc
- If the doc doesn't signal P0 or P2, use P1

### Sprint
- Sprint name should appear in the meeting section title (e.g., "Sprint 2026.17")
- If not present, defer sprint assignment — reference the sprint automation bot for fallback logic

### Due Date (EC only)
- Set only if explicitly mentioned in the action item or section context
- Format: YYYY-MM-DD

### Parent
- Always set to a specific epic from Sections 2 or 3 above
- If no match found → show as unresolved in preview and prompt reporter to confirm before creating

### Acceptance Criteria (AVP only)
- Required before backlog → To Do transition
- Use "Done when..." format, 2-5 bullets, based on task description
- Last-resort fallback if no description is available: "Added to Obsidian sprint plan"

### Assignee
- Use `[Name](mailto:...)` from the action item directly when present
- If name only (no mailto), look up in team_context.md first, then fall back to static table above
- If no assignee can be inferred, leave unset and flag in preview

### Components
- Derive from matched epic (e.g., FMS, Mission Planner, Networking, Simulation)
