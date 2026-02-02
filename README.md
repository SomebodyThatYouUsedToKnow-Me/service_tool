# 🛠️ Machine Service Checklist

[![Python](https://img.shields.io/badge/python-3.14+-blue)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/streamlit-✓-orange)](https://streamlit.io/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

A **web-based service checklist application** for field engineers to efficiently inspect machines, perform consistent checks across varying machine setups, and generate professional PDF service reports.

Built with **Python** and **Streamlit**, the entire system is **configuration-driven via JSON**, so no code changes are required when machines, checks, or templates change.

---

## 🎯 Why This Tool Exists

Field service engineers often face the same problem:

- The **same checks** must be performed  
- On **many different machines**  
- With **slightly different configurations**  
- While still producing **clear, professional service reports**

This tool was built to:
- Eliminate repetitive paperwork  
- Standardize inspections  
- Reduce mistakes caused by forgotten checks  
- Allow fast configuration **without touching code**  
- Produce customer-ready documentation directly from the field  

It is especially suited for **tablet use on-site**.

---

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/SomebodyThatYouUsedToKnow-Me/service_tool
cd machine-service-checklist

pip install streamlit reportlab

streamlit run app.py
```

## 🧩 Core Concepts

- **Checks**  
  Individual inspection items (numeric or boolean).

- **Templates**  
  Reusable collections of checks (e.g. conveyor, drive unit, safety).

- **Machines**  
  Machines combine one or more templates and may optionally override limits.

This structure keeps the system flexible, scalable, and clean.

---

## 📝 Features

### ✅ Check Builder

- Add and remove:
  - **Numeric checks** (with min/max limits)
  - **Boolean checks** (OK / Not OK)
- Stored automatically in `checklist.json`

---

### ✅ Template Builder

- Create reusable templates
- Assign multiple checks per template
- Templates can be combined on a single machine
- Safe behavior when **no templates exist**

---

### ✅ Machine Builder

- Add, edit, or delete machines
- Assign multiple templates per machine
- Optional machine-specific numeric overrides
- Collapse / expand machines for a clean tablet UI

---

### ✅ Checklist Execution

- Dynamic checklist generation per machine
- Numeric checks show:
  - ✅ Pass
  - ⚠️ Warning
  - ❌ Fail
- Notes can be added per check

---

### ✅ PDF Export

- Professional, customer-ready PDF reports
- Includes:
  - Service date
  - Engineer name
  - Job ID
  - Machine results
  - Check values and notes
- Files saved automatically to `/exports`

---

### ✅ Summary View

- Overview of all machines in the service
- Quick visual status per machine
- Expand for detailed inspection results

## 💡 Tips & Best Practices

- **Numeric warnings**  
  Values close to tolerance limits are automatically flagged.

- **Notes per check**  
  Keep track of issues or observations for future reference.

- **Expandable UI**  
  Makes the app tablet-friendly and clean for field use.

- **PDF Export**  
  Save reports immediately after completing inspections for documentation.

---

## ⚙️ Tech Stack

- **Python 3.14+**
- **Streamlit** – Interactive web UI
- **ReportLab** – PDF report generation
- **JSON** – Configuration storage for checks, templates, and machines

---

## 📈 Future Improvements

- Optional customer-specific checklists (currently removed).
- User authentication for multi-engineer tracking.
- Cloud database sync for multi-user teams.

---

## 📄 License

MIT License – free to use and modify.
