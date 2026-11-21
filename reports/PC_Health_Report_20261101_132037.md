# 🛡️ AI PC Health & Optimization Report
*Generated on Sunday, November 01, 2026 13:20:37 on **PC-002***

![Health Score](https://img.shields.io/badge/PC_Health_Score-57%2F100-red?style=for-the-badge)

### 📊 Status: **Poor (System Bottlenecks Present)**

> **AI Summary:** PC Health Assessment: Poor (System Bottlenecks Present) (Score: 57/100).
- Memory: 3.65 GB used out of 3.88 GB (94.1%).
- Storage Bloat: Approximately 2.86 GB of recoverable junk and caches detected across temp directories and update caches.
- Startup items: 10 background boot applications active.
Recommended Action: Execute prioritized cleanup and memory trim to reclaim responsiveness and disk space.

---
## ⚡ Optimization Execution Summary

- **Status:** OPTIMIZATION_COMPLETE
- **Total Disk Space Reclaimed:** **91162.49 MB**
- **Total Working Sets Trimmed:** **0 processes**
- **DNS Resolver:** Skipped
- **SSD Optimization/TRIM:** Skipped

---
## 💻 System Specifications

| Component | Specification |
| :--- | :--- |
| **Operating System** | Microsoft Windows 10 Pro (64-bit) |
| **OS Build Version** | 10.0.19045 |
| **Processor (CPU)** | Intel(R) Core(TM) i3-2120 CPU @ 3.30GHz (2 cores, 4 logical) |
| **Memory (RAM)** | 3.88 GB Total | 3.65 GB Used (94.1%) | 0.23 GB Free |
| **Active Power Plan** | Balanced |

---
## 💾 Storage Drives

| Drive | Volume | Type | Used | Free | Total | % Full | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **C:** | System | HDD | 95.68 GB | 136.32 GB | 232 GB | 41.2% | 🟢 Normal |

---
## 🧹 Recoverable Junk & Cache Telemetry

| Target Directory / Cache | Size (MB) | File Count | Path |
| :--- | :--- | :--- | :--- |
| **User Temporary Files** | 1688.11 MB | 2102 | $env:TEMP |
| **Windows System Temp** | 9.77 MB | 26 | C:\Windows\Temp |
| **Windows Update Cache** | 1230.07 MB | 565 | C:\Windows\SoftwareDistribution\Download |
| **Application Crash Dumps** | 0 MB | 0 | %LOCALAPPDATA%\CrashDumps |
| **Windows Error Reports** | 0 MB | 0 | %LOCALAPPDATA%\Microsoft\Windows\WER |
| **Recycle Bin Items** | 0 MB | 0 | Recycle Bin |
| **TOTAL RECLAIMABLE** | **2927.95 MB (2.86 GB)** | - | - |

---
## ⚠️ Detected Health Bottlenecks

| Severity | Component | Issue Description | Recommended Resolution |
| :--- | :--- | :--- | :--- |
| 🔴 Critical | Memory (RAM) | RAM utilization is critically high (94.1%). Free memory is only 0.23 GB out of 3.88 GB. | Trim process memory working sets and terminate unnecessary background applications. |
| ℹ️ Notice | Disk Junk & Cache | Accumulated junk files (2.86 GB) ready for cleanup. | Run quick junk clean. |
| 🟡 Warning | Startup Clutter | 10 applications are set to launch at boot time, slowing startup time. | Review startup applications and disable unneeded background helpers. |

---
## 📈 Top Memory Consumers (Working Set)

| Process ID | Process Name | Memory (MB) | CPU Time (s) | Responding |
| :--- | :--- | :--- | :--- | :--- |
| 9636 | **msedge** | 407.7 MB | 175.8s | Yes |
| 1108 | **pwsh** | 247.3 MB | 536.9s | Yes |
| 4540 | **MsMpEng** | 180.3 MB | 0s | Yes |
| 9620 | **Antigravity** | 158.4 MB | 37.9s | Yes |
| 10336 | **SearchApp** | 152.7 MB | 37.4s | Yes |
| 8852 | **msedge** | 120.6 MB | 569.6s | Yes |
| 9204 | **OneDrive** | 119.4 MB | 143s | Yes |
| 8076 | **explorer** | 118 MB | 497.8s | Yes |
| 13832 | **language_server** | 103.2 MB | 13.9s | Yes |
| 3584 | **msedge** | 69.9 MB | 25.2s | Yes |
| 104 | **Registry** | 51.7 MB | 0s | Yes |
| 8132 | **OneDrive.Sync.Service** | 43.7 MB | 98.8s | Yes |
| 2836 | **StartMenuExperienceHost** | 42.5 MB | 13.7s | Yes |
| 9464 | **Telegram** | 39 MB | 48.5s | Yes |
| 6396 | **SearchIndexer** | 38.9 MB | 0s | Yes |

---
## 🚀 Startup Applications

| Application Name | Location | Scope | Command |
| :--- | :--- | :--- | :--- |
| **Sidebar** | Registry: HKCU Run | User | $(C:\Program Files\Windows Sidebar\Sidebar.exe /autoRun) |
| **OneDrive** | Registry: HKCU Run | User | $("C:\Program Files\Microsoft OneDrive\OneDrive.exe" /backg...) |
| **Spotify** | Registry: HKCU Run | User | $("C:\Users\KURONAIZUKO\AppData\Roaming\Spotify\Spotify.exe...) |
| **MicrosoftEdgeAutoLaunch_46D94850D1C3BF61FB89BC6FA40D0A9E** | Registry: HKCU Run | User | $("C:\Program Files (x86)\Microsoft\Edge\Application\msedge...) |
| **SecurityHealth** | Registry: HKLM Run | System | $(C:\WINDOWS\system32\SecurityHealthSystray.exe) |
| **NvBackend** | Registry: HKLM Run | System | $("C:\Program Files (x86)\NVIDIA Corporation\Update Core\Nv...) |
| **IgfxTray** | Registry: HKLM Run | System | $("C:\WINDOWS\system32\igfxtray.exe") |
| **HotKeysCmds** | Registry: HKLM Run | System | $("C:\WINDOWS\system32\hkcmd.exe") |
| **Persistence** | Registry: HKLM Run | System | $("C:\WINDOWS\system32\igfxpers.exe") |
| **Nearby Share** | Registry: HKLM Run | System | $("C:\Program Files\Google\NearbyShare\nearby_share_launche...) |


