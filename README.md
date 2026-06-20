# Mughal Tools & Hardware

**Mughal Tools & Hardware** is a high-performance, modern, and offline-first desktop application designed specifically for Pakistani hardware and tools shops. It provides an intuitive, bilingual (English & Urdu) interface to manage inventory, sales billing, and credit accounts (*Easy Khata*).

---

## 🚀 Key Features

* **Bilingual Interface (English & Urdu)**: Toggle between English and Urdu with a single click. The UI dynamically shifts layout directions (LTR/RTL) and translations for native speakers.
* **Easy Khata (Udhaar Book)**: Manage customer and supplier credit balances (*Udhaar* & *Wasooli*) with double-entry ledger transactions.
* **Point of Sale (POS) Billing**: Quick-checkout cart interface. Instantly deducts stock and posts transactions directly to customer credit accounts if checked out on credit.
* **Printable Invoices (Raseed)**: Print-ready receipts optimized with standard Pakistani shop layouts.
* **Offline AI Bot (Candle + GGUF)**: An intelligent local AI assistant powered by Rust + Candle to answer inventory and outstanding debtor questions directly.
* **Server Monitor (Diagnostics)**: Uses `sysinfo` to monitor CPU/RAM utilization and top active processes directly on the dashboard.
* **Windows Service**: Core hooks prepared for running as a background Windows Service to handle scheduled backups.

---

## 🛠️ Technology Stack

* **Desktop Shell**: Tauri v2 + Rust stable
* **Backend Utilities**: `sysinfo` (resource diagnostics) & `windows-service` (background daemon)
* **Frontend**: React 18 + TypeScript + Vite
* **Styling**: Tailwind CSS v4 + Lucide React Icons
* **Package Manager**: Bun
* **Inference**: Candle ML (GGUF Quantized Models)
* **Database**: SQLite (local database)

---

## 📦 How to Build the Installer (.exe / .msi)

### 1. Cloud Build (Recommended)
This repository is pre-configured with a **GitHub Actions release workflow**.
1. Push this code to your GitHub repository.
2. Go to the **Actions** tab on GitHub, choose the **Release** workflow, and click **Run workflow** (or simply push to `main` branch).
3. Once compiled, download the ready-to-use `.exe` or `.msi` installers from the **Releases** tab on the right sidebar of your repository.

### 2. Local Build
If compiling on your local Windows computer:
1. Open PowerShell as Administrator and install the C++ build compilers:
   ```powershell
   winget install Microsoft.VisualStudio.2022.BuildTools --override "--add Microsoft.VisualStudio.Workload.VCTools --includeRecommended --passive --norestart"
   ```
2. Install dependencies:
   ```bash
   bun install
   ```
3. Run the development server:
   ```bash
   bun run tauri dev
   ```
4. Build the installers locally:
   ```bash
   bun run tauri build
   ```
