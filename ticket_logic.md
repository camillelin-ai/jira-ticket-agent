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
- If the work involves **FMS commands, fuel level display in Hive, cycle state UI, FMS alerting** → **AVP-57541**
- If the work involves **mission planner behavior tree, stack-side cycle states (QueuedForFuel/Fueling), MQTT fuel level extraction, bedrock constants** → **EC-16105**
- If the action item mentions both sides, split into two tickets.

**Dump Script:**
- If the work involves **Hive UI page for authoring/editing/deleting dump scripts, FMS dispatch with dump config** → **AVP-57421**
- If the work involves **stack execution of dump sequences, DumpBedConfig proto, behavior tree, hopper/paddock autonomy logic, authority-gated spot selection** → **EC-12454** or **EC-16498**
- If ambiguous between UI and stack, prefer EC if the action item owner is Walter Wang or an autonomy engineer; prefer AVP if owner is Anisha Jain, Avi Agarwal, or a product/FMS engineer.

**Fuel level display in Hive (EC-16512 vs AVP-57541):**
- FMS UI display of fuel percentage matching Figma → **EC-16512** (this ticket was opened in EC by mistake per standard but confirm before routing)
- FMS event/alerting/command layer → **AVP-57541**

**HMI:**
- V4 manual haul truck HMI (fleet control UI for manual trucks) → **AVP-58172**
- Onboard HMI for loader/dozer (tablet) → **AVP-43609**
- Stack-level HMI capability epics (V3 bulldozer, excavator, controller CONOPs) → EC (EC-14619, EC-14624, EC-14625) — these are V3 and likely complete; don't create new tickets under them without confirming

**Ground Truth Network / Rajant:**
- On-prem network, mesh install, vehicle connectivity, network drop testing → **EC** (EC-15497 parent, sub-epics EC-15850, EC-15655, EC-15997, EC-15998, EC-16003, EC-16004)
- FMS visualization of uncertainty ellipse / vehicle connectivity monitoring → **AVP-52398**

---

## 2. AVP Epic Map (children of AVP-34993)

Parent of all FMS/Obsidian V4 AVP work: **AVP-34993** (C-Cube: Fleet Management)

| Epic Key | Feature | Keywords |
|---|---|---|
| AVP-57421 | Dump Script Creation page/modal | dump script, authoring scripts, create script, configure dump steps, raise/wait/forward |
| AVP-57537 | Dump Zone Configuration | dump zone, zone configuration, LHD assignment, hopper zone, paddock zone, map panel zone |
| AVP-57539 | Mission Page | mission, create mission, load zone, dump zone, assign haul truck, haul route |
| AVP-57541 | Fuel Bay / Staging Points (FMS) | fuel bay, staging point, send to fuel, fuel level, cycle state display, FMS fuel alert |
| AVP-57543 | Loader V2 | loader V2, wheel loader UI, bench loader UI, load path UI |
| AVP-57546 | Dynamic FMS UI Map Updates | dynamic map, FMS map update, bench shape update, stack map sync |
| AVP-57547 | Dynamic Map Visualization | map visualization, Three.js, Cesium replacement, SLAM imagery, drone imagery layer |
| AVP-58171 | Heidelberg Customer Cluster (Prod) | Heidelberg, AU cluster, Australian region, production cluster |
| AVP-58172 | Manual Haul Truck HMI | manual truck, manual haul, manual HMI, manual vehicle fleet |
| AVP-43609 | Tablet / SDS Mining HMI | tablet, HMI tablet, onboard HMI, tablet productionization, maps tablet |
| AVP-49321 | Reporting & Analytics | reporting, analytics, shift report, exception report, variance report, performance report |
| AVP-51568 | Site Configuration | site config, timezone, shift days, speed limit, units, metrics units |
| AVP-55510 | Shift Management | shift management, shift scheduling, shift handover |
| AVP-55524 | Time Governance | time governance, equipment time, time classification, time allocation |
| AVP-52398 | Ground Truth Network (FMS viz) | uncertainty ellipse, vehicle connectivity visualization, FMS network monitor |
| AVP-53044 | Fleet Management Productionization | fleet productionization, FMS stability, FMS tech debt |

**Flag for verification:** AVP-57547 (Dynamic Map Visualization) did not appear as a direct child of AVP-34993 in Jira query results — confirm parent before using.

---

## 3. EC Epic Map (children of EC-11955)

Parent of all Obsidian V4 EC/stack work: **EC-11955**

| Epic Key | Feature | Keywords |
|---|---|---|
| EC-12454 | Dumping — Hopper/Paddock | dump behavior, hopper dump, paddock dump, fleet management dumping, dump mission planner |
| EC-16103 | Wheel Loader (stack) | wheel loader, WL autonomy, wheel loader stack, WL loading |
| EC-16104 | Bench Loading | bench loading, bench loader, load path, occupancy-based stopping, VARIABLE path, bench occupancy |
| EC-16105 | Fuel Bay — Mission Planner (stack) | fuel bay stack, mission planner fuel, QueuedForFuel, Fueling state, fuel behavior tree, fuel MQTT |
| EC-16107 | Mixed Operation (V2V/X2V) | mixed operation, V2V, X2V, multi-vehicle, distributed mapping, VehicleMetadata, BedrockVehicleManager, x2v detections |
| EC-16122 | Triple Leader Follower | triple LF, triple leader follower, 3-vehicle LHD, ADT-201, RAP-107, KOM-101 multi |
| EC-16134 | Map Improvements | map improvement, map toolset, SLAM data, drone imagery, map workflow, map validation, on-site cluster map |
| EC-16174 | Rockwell Buildout | Rockwell, site bringup, hopper construction, slope bringup, wheel loader sourcing, HIL bench |
| EC-16183 | Multi-Ego Simulation | multi-ego sim, AxionSim, Isaac-Sim, multi-vehicle sim, bedrock multi-ego |
| EC-16190 | Stability, Robustness, Performance Metrics | metrics, stability, robustness, pass/fail criteria, regression metrics, performance metrics |
| EC-16410 | Uncertainty Framework | uncertainty, BedrockStreaming uncertainty, uncertainty ellipse, Hive viz uncertainty |
| EC-15497 | On-prem Network / Ground Truth | on-prem network, Rajant, mesh network, ground truth, network integration |
| EC-16016 | Autonomy Uptime / Project 1000 Hours | time-in-autonomy, autonomy uptime, 1000 hours, efficiency improvement |
| EC-16454 | Fault List Audits / Driverless | fault list, driverless operation, fault audit, subsystem fault, CONOP |
| EC-16498 | Authority-Gated Dump Spot Selection | dump spot, authority gated, spot selection, dump authority |
| EC-16500 | Slope — Reverse Direction Bug | slope, reverse direction sign, slope bug |
| EC-16503 | Slope — Understand ADT Capability | slope handling, ADT slope, grade handling, 10% grade |
| EC-16668 | Slope — Hill Start Assist | hill start assist, hill start, slope assist |
| EC-16407 | MPK Deployment | MPK, mission planning kit, pre-deployment |
| EC-16600 | Integrate Loaders/Dozers onto Network | loader network, dozer network, excavator network, on-prem integration |

---

## 4. Epic Selection Logic

When matching an action item to an epic:

1. **Check for explicit Jira key** already in the doc line (e.g., "[EC-16104]") — use that directly.
2. **Check the assignee** — each DRI has a primary area (see DRI map below).
3. **Match keywords** from the action item text against the Keywords column above.
4. **Use section context** — the meeting section heading or parent requirement doc heading is strong signal (e.g., if the action item is under a "Bench Loading" section, default to EC-16104).
5. **If still ambiguous**, select the closest parent epic and note uncertainty in the preview — don't block ticket creation.

### DRI → Primary Epic Mapping

| Person | Primary Area | Default Epic(s) |
|---|---|---|
| Walter Wang | Mission Planner / Dumping | EC-12454, EC-16498, EC-16105 |
| Avi Agarwal | FMS backend / Dump Zone / Mission | AVP-57537, AVP-57539, AVP-57421 |
| Anisha Jain | FMS frontend / UI | AVP-57421, AVP-57537, AVP-57543 |
| Kamil Nocon | Fuel Bay, Sim, Map | EC-16105, EC-16183, AVP-57541, AVP-57546 |
| Wenkai Ren / Li Jin | Bench Loading | EC-16104 |
| Zeyuan Jin | Wheel Loader | EC-16103 |
| Peter Redman | Mixed Operation | EC-16107 |
| Abhijit Chilukuri | Triple LF, MPK | EC-16122, EC-16407 |
| Jensen Solar | Metrics, Uptime | EC-16190, EC-16016 |
| Tom Jennings | Rockwell, Network | EC-16174, EC-15497 |
| Camille Lin | Network, Connectivity | EC-15497, EC-16560, EC-16600 |
| Pankaj Saini | Reporting, Cluster | AVP-49321, AVP-58171 |
| Shreya Vemuri | Mission Page, Shift | AVP-57539, AVP-55510 |
| Naveen Kumar Aproop | Uncertainty | EC-16410 |
| Huaiqian Shou | Slope Handling | EC-16503, EC-16500, EC-16668 |
| Morgan David | Regulations / Requirements | flag for manual review |
| Gyuri Han | Design / UI | flag for AVP, confirm epic |

---

## 5. Carryover Task Detection

The doc is the primary source for carryover detection — no revision history API needed.

**Detection logic:**
1. Before creating a ticket for an action item in the target section, search all previous sprint sections (`## MMM DD, YYYY` headers earlier in the doc) for similar text.
2. Match on: assignee name + similar task description (semantic similarity, not exact string match).
3. If found in a prior section **with a linked ticket key** (EC-XXXXX or AVP-XXXXX inline) → state = **carryover, already ticketed** → propose linking rather than creating.
4. If found in a prior section **without a linked ticket key** → state = **carryover, no ticket** → still create, but note in preview that this appears to be a carried-over task.
5. If the same task text appears in 2+ prior sections, it is a recurring carry-over — flag this explicitly.

---

## 6. Field Inference Rules

### Priority
- Default: **Medium**
- High: words like "blocking", "blocked", "urgent", "before X date", "demo", "customer milestone", "safety"
- Critical: "P0", "site safety", "production down"
- Low: "nice to have", "post-V4", "future", "stretch goal", "backlog"

### Sprint
- Default to current active sprint (Eng Sprint v2 for both projects)
- If action item references a specific date or milestone, map to the sprint containing that date
- If item is explicitly "post-V4" or has no near-term deadline, leave sprint unset

### Due Date (EC only)
- Set only if explicitly mentioned in the action item or its meeting section context
- Format: YYYY-MM-DD

### Parent
- **EC**: Always set to the epic from Section 3 above. Exception: top-level initiatives and field test tickets may omit parent.
- **AVP**: Always set to the epic from Section 2 above.
- If no epic match is found, set parent to the program-level parent (EC-11955 or AVP-34993) and note uncertainty.

### Acceptance Criteria (AVP only)
- Required before backlog → To Do transition
- Use "Done when..." format, 2-5 bullets
- Base on the task description; reference the feature's design doc or requirements section in the Obsidian doc if one exists

### Assignee
- Use the `[Name](mailto:...)` from the action item directly
- If only a name is mentioned without email, resolve via the DRI map above
- If no assignee is specified, leave unset

### Components
- Set based on the epic area (e.g., "FMS", "Mission Planner", "Networking", "Simulation") — derive from the epic matched

---

## 7. Flagged Items (Verify Before Use)

- **AVP-57547** (Dynamic Map Visualization / Three.js) — not confirmed as direct child of AVP-34993 in Jira; verify parent before assigning
- **EC-11955 children** — Jira query failed during setup; epic list in Section 3 was sourced from the Obsidian doc. Verify any new epics against Jira directly before routing to them
- **EC-16512** (Fuel level display in Hive) — appears to be an EC ticket for what is functionally an FMS UI task; confirm correct project before creating children under it
