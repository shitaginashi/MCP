import yaml
import os
import argparse
from datetime import datetime

PROJ_ROOT = "/data/projects"
REPORT_ROOT = "/data/reports"

class CoreLedger:
    def __init__(self):
        os.makedirs(PROJ_ROOT, exist_ok=True)
        os.makedirs(REPORT_ROOT, exist_ok=True)

    def load_project(self, name):
        filename = name if name.endswith(".yml") else f"{name}.yml"
        path = os.path.join(PROJ_ROOT, filename)
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def audit_metrics(self, data):
        total_h, done_h = 0, 0
        focus_summary = {"Deep": 0.0, "Maintenance": 0.0}
        
        for m in data.get("milestones", []):
            m_total, m_done = 0, 0
            for r in m.get("requirements", []):
                for d in r.get("deliverables", []):
                    est, done = d.get("est_hours", 0), d.get("hours_done", 0)
                    m_total += est
                    m_done += done
                    profile = d.get("focus_profile", "Deep")
                    focus_summary[profile] += max(0, est - done)
            
            m["calc_perc"] = round((m_done / m_total * 100), 1) if m_total > 0 else 0
            total_h += m_total
            done_h += m_done

        overall = round((done_h / total_h * 100), 1) if total_h > 0 else 0
        return overall, focus_summary

    def generate_html(self, data, overall, focus, fragment_only=False):
        meta = data["project_metadata"]
        milestone_html = ""
        for m in data.get("milestones", []):
            deliv_html = ""
            for r in m.get("requirements", []):
                for d in r.get("deliverables", []):
                    status_class = "complete" if d["hours_done"] >= d["est_hours"] else "incomplete"
                    deliv_html += f'<li class="deliverable {status_class}"><strong>{d["task"]}</strong> - {d["hours_done"]}/{d["est_hours"]}h</li>'
            
            milestone_html += f"""
            <details class='milestone'>
                <summary>{m['mark']} - {m['calc_perc']}%</summary>
                <ul class="deliverables-list">{deliv_html}</ul>
            </details>"""

        content = f"""<div class="project-frag"><h1>{meta['display_name']} ({overall}%)</h1>{milestone_html}</div>"""
        if fragment_only: return content
        return f"<html><body>{content}</body></html>"

    def run_update(self, name):
        data = self.load_project(name)
        if not data: return print(f"NOT_FOUND|{name}")
        overall, focus = self.audit_metrics(data)
        with open(os.path.join(REPORT_ROOT, f"{name}.frag.html"), "w", encoding="utf-8") as f:
            f.write(self.generate_html(data, overall, focus, True))
        print(f"AUDIT_SUCCESS|{name}|{overall}%")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True)
    CoreLedger().run_update(parser.parse_args().project)
