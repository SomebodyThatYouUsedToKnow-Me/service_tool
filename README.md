# 🛠️ Machine Service Checklist

[![Python](https://img.shields.io/badge/python-3.14+-blue)](https://www.python.org/)  
[![Streamlit](https://img.shields.io/badge/streamlit-✓-orange)](https://streamlit.io/)  
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

A **web-based service checklist application** for field engineers to efficiently inspect machines, track numeric and boolean checks, and generate professional PDF service reports. Built with **Python** and **Streamlit**, fully configurable via JSON files.  

---

## 📌 Features

### ✅ Check Builder
- Add/remove **numeric** (with min/max limits) and **boolean** checks.  
- Changes are saved automatically to `checklist.json`.  

### ✅ Template Builder
- Create reusable machine templates.  
- Assign multiple templates per machine.  
- Customize numeric limits per template.  

### ✅ Machine Builder
- Add, edit, or delete machines.  
- Assign templates and optional numeric overrides for machine-specific tolerances.  
- Collapse/expand machines for a clean UI.  

### ✅ Checklist Tab
- Fill inspections dynamically for each machine.  
- Numeric checks automatically display **pass/warning/fail**.  
- Add notes per check.  

### ✅ PDF Export
- Generate professional, customer-ready PDF reports.  
- Includes service header (date, engineer, job ID) and inspection summary.  

### ✅ Summary Tab
- Quick overview of all machines and their inspection status.  
- Expand to see detailed check results.  

---

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/machine-service-checklist.git
cd machine-service-checklist
