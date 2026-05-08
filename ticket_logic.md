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
- On-prem network, mesh install, vehicle connectivity, network drop testing → **EC-15497** (epic)
- FMS-side network visualization → use closest AVP epic based on context; no dedicated AVP epic confirmed

---

## 2. AVP Epic Map (children of AVP-34993)

Parent of all FMS/Obsidian V4 AVP work: **AVP-34993** (C^3: C-Cube: Fleet Management)

| Epic Key | Jira Summary | Doc Deliverable Name | Keywords |
|---|---|---|---|
| AVP-57421 | [Obsidian V4] Dump script page | Dump script creation page/modal | dump script, authoring scripts, create script, configure dump steps, raise/wait/forward |
| AVP-57537 | [Obsidian V4] Dump zone configuration | Dump zone configuration | dump zone, zone configuration, LHD assignment, hopper zone, paddock zone, map panel zone |
| AVP-57539 | [Obsidian V4] Mission Page | Mission page | mission, create mission, load zone, dump zone, assign haul truck, haul route |
| AVP-57541 | [Obsidian V4] Fuel Bay / Staging Points | Fuel Bay / Staging Points | fuel bay, staging point, send to fuel, fuel level, cycle state display, FMS fuel alert |
| AVP-57543 | [Obsidian V4] Loader V2 | Loader V2 | loader V2, wheel loader UI, bench loader UI, load path UI |
| AVP-57546 | [Obsidian V4] Update FMS UI map dynamically | Updating FMS UI map dynamically | dynamic map, FMS map update, bench shape update, stack map sync, Three.js, drone imagery |
| AVP-58171 | Heidelberg Cluster - Prod | Heidelberg customer cluster | Heidelberg, AU cluster, Australian region, production cluster |
| AVP-58172 | [Obsidian V4] Manual truck HMI | Manual haul trucks | manual truck, manual haul, manual HMI, manual vehicle fleet |
| AVP-43609 | SDS - Mining Product HMI UI/UX | Tablet experience / Maps & HMI | tablet, HMI tablet, onboard HMI, tablet productionization, maps tablet |
| AVP-49321 | Report & Analytics for Mining | Reporting page | reporting, analytics, shift report, exception report, variance report, performance report |
| AVP-51568 | Site Configuration | Site configuration | site config, timezone, shift days, speed limit, units, metrics units |
| AVP-55510 | [C^3][FMS]: Shift Management | Shift management | shift management, shift scheduling, shift handover |
| AVP-55524 | Time Governance | Time governance | time governance, equipment time, time classification, time allocation |
| AVP-53044 | Fleet Management Productionization | Fleet Management Productionization | fleet productionization, FMS stability, FMS tech debt |

---

## 3. EC Epic Map (children of EC-11955)

Parent of all Obsidian V4 EC/stack work: **EC-11955**

| Epic Key | Jira Summary | Doc Deliverable Name | Keywords |
|---|---|---|---|
| EC-12454 | Obsidian V4 Capability: Managed and Unmanaged Dumping Operations | Dumping | dump behavior, hopper dump, paddock dump, managed dump, unmanaged dump, dump mission planner |
| EC-16103 | Obsidian V4 Capability: Wheel Loader Loading | Wheel Loader | wheel loader, WL autonomy, wheel loader stack, WL loading |
| EC-16104 | Obsidian V4 Capability: Bench Loading | Bench Loading | bench loading, bench loader, load path, occupancy-based stopping, VARIABLE path, bench occupancy |
| EC-16105 | Obsidian V4 Capability: Fuel Bay | Fuel Bay (stack/mission planner) | fuel bay stack, mission planner fuel, QueuedForFuel, Fueling state, fuel behavior tree, fuel MQTT |
| EC-16107 | Obsidian V4 Capability: Mixed Operation | Mixed Operation | mixed operation, V2V, X2V, multi-vehicle, distributed mapping, VehicleMetadata, BedrockVehicleManager, x2v detections |
| EC-16122 | Obsidian V4 Capability: Triple Leader Follower | Triple Leader Follower | triple LF, triple leader follower, 3-vehicle LHD, ADT-201, RAP-107, KOM-101 multi |
| EC-16134 | Obsidian V4 Subsystem: Map Workflow | Map Improvements | map improvement, map toolset, SLAM data, drone imagery, map workflow, map validation, on-site cluster map |
| EC-16174 | Obsidian V4 Operations: Rockwell Buildout | Rockwell Buildout | Rockwell, site bringup, hopper construction, slope bringup, wheel loader sourcing, HIL bench |
| EC-16183 | Obsidian V4 Development: Multi-Ego Simulation | Simulation | multi-ego sim, AxionSim, Isaac-Sim, multi-vehicle sim, bedrock multi-ego |
| EC-16190 | Obsidian V4 Development: Stability, Robustness, Performance Metrics | Stability, Robustness, Performance Metrics | metrics, stability, robustness, pass/fail criteria, regression metrics, performance metrics |
| EC-16410 | Obsidian V4 Development: Uncertainty Framework | Uncertainty Framework | uncertainty, BedrockStreaming uncertainty, uncertainty ellipse, Hive viz uncertainty |
| EC-15497 | Obsidian V4 Development: On-prem network ground truth | On-prem network ground truth integration | on-prem network, Rajant, mesh network, ground truth, network integration |

---

## 4. Epic Selection Logic

When matching an action item to an epic:

1. **Explicit Jira key in the doc line** (e.g., "[EC-16104]") → use that directly.
2. **Section context** — the meeting heading or parent requirement doc heading is strong signal. Action item under a "Bench Loading" section → EC-16104.
3. **Keyword match** — match action item text against the Keywords column above.
4. **Assignee** — cross-reference team_context.md for who is currently working on what area.
5. **If still ambiguous** — show uncertainty in the preview and prompt the reporter to confirm the parent before creating. Do not silently guess and do not fall back to the program-level parent (EC-11955 / AVP-34993).

---

## 5. Team Context

See `team_context.md` for the current person → feature area mapping. That file is updated after each approved ticket batch and is the primary source for assignee inference.

Use this static table only as a fallback when team_context.md has no signal:

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
| Jensen Solar | Metrics, Uptime | EC-16190 |
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
- P0: "blocking", "blocked", "safety", "demo", "customer milestone", "production down" — should also be stated inline in the doc
- P2: "nice to have", "post-V4", "stretch goal" — should also be stated inline in the doc
- If the doc doesn't signal P0 or P2, use P1

### Sprint
- Sprint name should appear in the meeting section title (e.g., "Sprint 2026.17")
- If not present, defer sprint assignment and leave a TODO — reference the sprint automation bot for fallback logic

### Due Date (EC only)
- Set only if explicitly mentioned in the action item or section context
- Format: YYYY-MM-DD

### Parent
- Always set to a specific epic from Sections 2 or 3 above
- If no match found → show in preview as unresolved and prompt reporter to confirm before creating

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
