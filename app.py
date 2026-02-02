import streamlit as st
import json
from pathlib import Path
from datetime import datetime, date
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

# ---------------- CONFIG ----------------
WARNING_PERCENT = 0.10
EXPORT_DIR = Path("exports")
EXPORT_DIR.mkdir(exist_ok=True)

st.set_page_config(page_title="Service Checklist", layout="wide")
st.title("🛠️ Machine Service Checklist")

# ---------------- FILES ----------------
CHECKLIST_FILE = Path("checklist.json")
MACHINES_FILE = Path("machines.json")
TEMPLATES_FILE = Path("templates.json")


# ---------------- LOAD DATA ----------------
def load_json(file, default={}):
    return json.load(open(file)) if file.exists() else default


CHECKLIST = {c["id"]: c for c in load_json(CHECKLIST_FILE, [])}
MACHINES = load_json(MACHINES_FILE, {})
TEMPLATES = load_json(TEMPLATES_FILE, {})


# ---------------- HELPERS ----------------
def resolve_checks_multi(machine):
    merged = {}
    for tmpl_name in machine.get("templates", []):
        tmpl = TEMPLATES.get(tmpl_name, {})
        for cid, cfg in tmpl.items():
            merged[cid] = cfg.copy()
    for cid, cfg in machine.get("overrides", {}).items():
        merged[cid] = merged.get(cid, {}).copy()
        merged[cid].update(cfg)
    return merged


def save_checklist():
    json.dump(list(CHECKLIST.values()), open(CHECKLIST_FILE, "w"), indent=4)


def save_machines():
    json.dump(MACHINES, open(MACHINES_FILE, "w"), indent=4)


def save_templates():
    json.dump(TEMPLATES, open(TEMPLATES_FILE, "w"), indent=4)


def cleanup_deleted_check(cid):
    for tmpl in TEMPLATES.values():
        if cid in tmpl:
            del tmpl[cid]
    save_templates()
    for machine in MACHINES.values():
        if "overrides" in machine and cid in machine["overrides"]:
            del machine["overrides"][cid]
    save_machines()


# ---------------- TABS ----------------
tab_checklist, tab_summary, tab_templates, tab_machines, tab_checks = st.tabs(
    [
        "🔧 Checklist",
        "📊 Summary",
        "🛠️ Template Builder",
        "🏭 Machine Builder",
        "📝 Check Builder",
    ]
)

# ================= CHECK BUILDER =================
with tab_checks:
    st.subheader("📝 Check Builder")
    st.info("Add or remove checks dynamically. Changes saved to checklist.json.")

    # Add new check
    with st.expander("➕ Add New Check"):
        check_type = st.selectbox("Check Type", ["numeric", "boolean"])
        title = st.text_input("Check Title", key="new_check_title")
        min_val = max_val = None
        unit = ""
        if check_type == "numeric":
            unit = st.text_input(
                "Unit (e.g., mm, %, etc.)", value="", key="new_check_unit"
            )
            min_val = st.number_input("Lower limit", value=0.0, key="new_check_min")
            max_val = st.number_input("Upper limit", value=100.0, key="new_check_max")

        if st.button("Add Check"):
            if not title:
                st.error("Check must have a title!")
            else:
                cid = title.lower().replace(" ", "_")
                if cid in CHECKLIST:
                    st.error("Check ID already exists!")
                else:
                    CHECKLIST[cid] = {"id": cid, "title": title, "type": check_type}
                    if check_type == "numeric":
                        CHECKLIST[cid].update(
                            {"unit": unit, "min": min_val, "max": max_val}
                        )
                    save_checklist()
                    st.success(f"Check '{title}' added!")

    # Remove existing check
    with st.expander("🗑️ Remove Existing Checks"):
        if CHECKLIST:
            remove_check = st.selectbox(
                "Select a check to remove", options=list(CHECKLIST.keys())
            )
            if st.button("Delete Check"):
                if remove_check in CHECKLIST:
                    del CHECKLIST[remove_check]
                    save_checklist()
                    cleanup_deleted_check(remove_check)
                    st.success(
                        f"Check '{remove_check}' removed from checklist, templates, and machine overrides!"
                    )
        else:
            st.info("No checks available to remove.")

# ================= TEMPLATE BUILDER =================
with tab_templates:
    st.subheader("🛠️ Machine Template Builder")
    st.info("Create, edit, or delete templates. Changes saved to templates.json.")
    template_names = list(TEMPLATES.keys())
    selected_template = st.selectbox(
        "Select a template", ["<New Template>"] + template_names
    )
    if selected_template == "<New Template>":
        template_name = st.text_input("New template name")
        template_checks = {}
        delete_button = False
    else:
        template_name = selected_template
        template_checks = TEMPLATES[selected_template]
        delete_button = True

    st.markdown("**Select checks to include in this template:**")
    for cid, check in CHECKLIST.items():
        include = st.checkbox(check["title"], value=(cid in template_checks))
        if include:
            if check["type"] == "numeric":
                min_val = st.number_input(
                    f"Min ({check['unit']}) for {check['title']}",
                    value=template_checks.get(cid, {}).get("min", check.get("min", 0)),
                    key=f"{template_name}_{cid}_min",
                )
                max_val = st.number_input(
                    f"Max ({check['unit']}) for {check['title']}",
                    value=template_checks.get(cid, {}).get(
                        "max", check.get("max", 100)
                    ),
                    key=f"{template_name}_{cid}_max",
                )
                template_checks[cid] = {"min": min_val, "max": max_val}
            else:
                template_checks[cid] = {}
        elif cid in template_checks:
            del template_checks[cid]

    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Save Template"):
            if not template_name:
                st.error("Template must have a name!")
            else:
                TEMPLATES[template_name] = template_checks
                save_templates()
                st.success(f"Template '{template_name}' saved!")
    with col2:
        if delete_button:
            if st.button("🗑️ Delete Template"):
                del TEMPLATES[template_name]
                save_templates()
                st.success(f"Template '{template_name}' deleted!")

# ================= MACHINE BUILDER =================
with tab_machines:
    st.subheader("🏭 Machine Builder")
    st.info("Create, edit, or delete machines. Changes saved to machines.json.")
    machine_names = list(MACHINES.keys())
    selected_machine = st.selectbox(
        "Select a machine", ["<New Machine>"] + machine_names
    )
    if selected_machine == "<New Machine>":
        machine_name = st.text_input("New machine name")
        machine_templates = []
        machine_overrides = {}
        delete_button = False
    else:
        machine_name = selected_machine
        machine_templates = MACHINES[selected_machine].get("templates", [])
        machine_overrides = MACHINES[selected_machine].get("overrides", {})
        delete_button = True

    st.markdown("**Select templates for this machine:**")
    all_templates = list(TEMPLATES.keys())
    safe_defaults = [t for t in machine_templates if t in all_templates]
    selected_templates = st.multiselect(
        "Templates", options=all_templates, default=safe_defaults
    )

    st.markdown("**Set machine-specific numeric overrides (optional):**")
    overrides = {}
    for cid in CHECKLIST:
        if CHECKLIST[cid]["type"] == "numeric":
            current = machine_overrides.get(cid, {})
            min_val = st.number_input(
                f"Override Min ({CHECKLIST[cid]['title']})",
                value=current.get("min", 0),
                key=f"{machine_name}_{cid}_min",
            )
            max_val = st.number_input(
                f"Override Max ({CHECKLIST[cid]['title']})",
                value=current.get("max", 0),
                key=f"{machine_name}_{cid}_max",
            )
            if min_val != 0 or max_val != 0:
                overrides[cid] = {"min": min_val, "max": max_val}

    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Save Machine"):
            if not machine_name:
                st.error("Machine must have a name!")
            else:
                MACHINES[machine_name] = {"templates": selected_templates}
                if overrides:
                    MACHINES[machine_name]["overrides"] = overrides
                elif "overrides" in MACHINES.get(machine_name, {}):
                    del MACHINES[machine_name]["overrides"]
                save_machines()
                st.success(f"Machine '{machine_name}' saved!")
    with col2:
        if delete_button:
            if st.button("🗑️ Delete Machine"):
                del MACHINES[machine_name]
                save_machines()
                st.success(f"Machine '{machine_name}' deleted!")

# ================= CHECKLIST TAB =================
with tab_checklist:
    st.subheader("📄 Service Report Details")
    col1, col2 = st.columns(2)
    with col1:
        service_date = st.date_input("Service date", value=date.today())
        engineer = st.text_input("Engineer name")
    with col2:
        job_id = st.text_input("Job / Work order ID")
        customer_field = st.text_input("Customer / Site")

    report_header = {
        "service_date": service_date.isoformat(),
        "engineer": engineer,
        "job_id": job_id,
        "customer": customer_field,
    }

    all_results = {}
    if not MACHINES or not TEMPLATES or not CHECKLIST:
        st.info("No machines, templates, or checks configured. Please add them first.")
    else:
        for machine_name, machine_data in MACHINES.items():
            checks = resolve_checks_multi(machine_data)
            if not checks:
                st.warning(
                    f"No checks configured for machine '{machine_name}'. Please assign templates."
                )
                continue

            machine_results = {}
            with st.expander(f"🔧 {machine_name}", expanded=False):
                for cid, limits in checks.items():
                    item = CHECKLIST[cid]
                    st.markdown(f"**{item['title']}**")
                    key = f"{machine_name}_{cid}"
                    if item["type"] == "numeric":
                        min_v = limits["min"]
                        max_v = limits["max"]
                        value = st.number_input(
                            f"Value ({item.get('unit','')})", key=key
                        )
                        span = max_v - min_v
                        warn_min = min_v + span * WARNING_PERCENT
                        warn_max = max_v - span * WARNING_PERCENT
                        passed = min_v <= value <= max_v
                        warning = passed and (value <= warn_min or value >= warn_max)
                        if not passed:
                            st.error(f"❌ Out of tolerance ({min_v}-{max_v})")
                        elif warning:
                            st.warning("⚠️ Close to tolerance limit")
                        else:
                            st.success("✅ Within tolerance")
                        note = st.text_input("Notes", key=f"{key}_note")
                        machine_results[cid] = {
                            "pass": passed,
                            "warning": warning,
                            "value": value,
                            "min": min_v,
                            "max": max_v,
                            "note": note,
                        }
                    else:
                        ok = st.checkbox("OK", key=key)
                        note = st.text_input("Notes", key=f"{key}_note")
                        machine_results[cid] = {"pass": ok, "note": note}
            fail = any(not r["pass"] for r in machine_results.values())
            warn = any(r.get("warning", False) for r in machine_results.values())
            status, icon = (
                ("FAIL", "🔴")
                if fail
                else ("WARNING", "🟡") if warn else ("PASS", "🟢")
            )
            all_results[machine_name] = {
                "status": status,
                "icon": icon,
                "results": machine_results,
            }

        # -------- EXPORT PDF --------
        def export_pdf():
            file = EXPORT_DIR / f"service_report_{datetime.now():%Y%m%d_%H%M%S}.pdf"
            styles = getSampleStyleSheet()
            doc = SimpleDocTemplate(str(file), pagesize=A4)
            elements = []
            elements.append(
                Paragraph("<b>SERVICE REPORT – SUMMARY</b>", styles["Title"])
            )
            elements.append(Spacer(1, 12))
            for k, v in report_header.items():
                elements.append(
                    Paragraph(f"{k.replace('_',' ').title()}: {v}", styles["Normal"])
                )
            elements.append(Spacer(1, 20))
            summary_table = [["Machine", "Status"]] + [
                [m, f"{d['icon']} {d['status']}"] for m, d in all_results.items()
            ]
            elements.append(
                Table(
                    summary_table,
                    colWidths=[250, 150],
                    style=[
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                    ],
                )
            )
            elements.append(PageBreak())
            for m, d in all_results.items():
                elements.append(
                    Paragraph(
                        f"{d['icon']} <b>{m}</b> — {d['status']}", styles["Heading2"]
                    )
                )
                elements.append(Spacer(1, 10))
                rows = [["Check", "Result", "Details", "Notes"]]
                for cid, r in d["results"].items():
                    item = CHECKLIST[cid]
                    if not r["pass"]:
                        txt, col = "FAIL", "red"
                    elif r.get("warning", False):
                        txt, col = "WARNING", "orange"
                    else:
                        txt, col = "PASS", "green"
                    details = (
                        f"{r['value']} (min {r['min']}/max {r['max']})"
                        if "value" in r
                        else ""
                    )
                    rows.append(
                        [
                            item["title"],
                            Paragraph(
                                f"<font color='{col}'>{txt}</font>", styles["Normal"]
                            ),
                            details,
                            r.get("note", ""),
                        ]
                    )
                elements.append(
                    Table(
                        rows,
                        colWidths=[180, 70, 160, 120],
                        style=[
                            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                        ],
                    )
                )
                elements.append(Spacer(1, 20))
            doc.build(elements)
            return file

        if st.button("🖨️ Export PDF"):
            st.success(f"PDF exported: {export_pdf()}")

# ================= SUMMARY TAB =================
with tab_summary:
    st.subheader("📊 Inspection Summary")
    if not all_results:
        st.info("No machines with checks to display.")
    else:
        for m, d in all_results.items():
            with st.expander(
                f"{d['icon']} {m} — {d['status']}", expanded=d["status"] != "PASS"
            ):
                for cid, r in d["results"].items():
                    title = CHECKLIST[cid]["title"]
                    if not r["pass"]:
                        st.error(f"❌ {title}")
                    elif r.get("warning", False):
                        st.warning(f"⚠️ {title}")
                    else:
                        st.success(f"✅ {title}")
