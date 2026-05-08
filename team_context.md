# Team Context — Obsidian Program

This file is maintained dynamically by the Jira ticket agent. After each approved ticket batch,
the agent updates it to reflect current feature area assignments based on actual ticket history.
Use this as the primary source for assignee inference — it reflects who is currently working on
what, including temporary assignments (e.g., bandwidth help across areas).

Last updated: 2026-05-07 (seeded from Obsidian doc and Jira epic analysis)

---

## Current Feature Area Assignments

| Person | Email | Current Areas | Recent Ticket Evidence |
|---|---|---|---|
| Walter Wang | walter.wang@applied.co | Mission Planner, Dumping (stack), Fuel Bay (stack) | EC-12454, EC-16498, EC-16105 |
| Avi Agarwal | avi.agarwal@applied.co | FMS backend, Dump Zone, Mission Page | AVP-57537, AVP-57539, AVP-57421 |
| Anisha Jain | anisha.jain@applied.co | FMS frontend/UI, Loader V2, Dump Script UI | AVP-57421, AVP-57537, AVP-57543 |
| Kamil Nocon | kamil.nocon@applied.co | Fuel Bay (FMS), Multi-Ego Sim, Dynamic Map | EC-16105, EC-16183, AVP-57541, AVP-57546 |
| Wenkai Ren | wenkai.ren@applied.co | Bench Loading | EC-16104 |
| Li Jin | li.jin@applied.co | Bench Loading, Map Workflow | EC-16104, EC-16134 |
| Zeyuan Jin | zeyuan.jin@applied.co | Wheel Loader | EC-16103 |
| Peter Redman | peter.redman@applied.co | Mixed Operation (V2V/X2V) | EC-16107 |
| Abhijit Chilukuri | abhijit.chilukuri@applied.co | Triple Leader Follower, MPK | EC-16122 |
| Jensen Solar | jensen.solar@applied.co | Stability/Metrics, Autonomy Uptime | EC-16190, EC-16016 |
| Tom Jennings | harrison.salmon@applied.co | Rockwell Buildout, Networking | EC-16174, EC-15497 |
| Camille Lin | camille@applied.co | Networking, Ground Truth, Connectivity | EC-15497 |
| Pankaj Saini | pankaj.saini@applied.co | Reporting, Heidelberg Cluster | AVP-49321, AVP-58171 |
| Shreya Vemuri | shreya.vemuri@applied.co | Mission Page (FMS), Shift Management | AVP-57539, AVP-55510 |
| Naveen Kumar Aproop | naveen.aproop@applied.co | Uncertainty Framework | EC-16410 |
| Huaiqian Shou | huaiqian.shou@applied.co | Slope Handling | EC-16503, EC-16500, EC-16668 |
| Gyuri Han | gyuri.han@applied.co | UI/UX Design (FMS) | AVP (confirm epic per task) |
| Morgan David | morgan.david@applied.co | Regulations, Requirements | EC or AVP depending on task |
| Harry Salmon | harrison.salmon@applied.co | Bench Loading (stack sanity) | EC-16104 |

---

## Update Instructions (for the agent)

After each approved ticket batch, update this file:
1. Add any new assignee→area assignments observed
2. If a person received tickets in an area outside their listed areas, add it with a note like "(bandwidth help, sprint 2026.XX)"
3. If a person's primary area shifts across multiple sprints, update their Current Areas column
4. Preserve the "Recent Ticket Evidence" column with the latest ticket keys

The agent should query recent tickets (last 3 sprints) for each person to verify this file
is not stale before relying on it for a new batch.
