import os
import yaml
from flask import Flask, render_template
from datetime import datetime

PROJECTS_DIR = "/data/projects"
app = Flask(__name__)

# This route is what the browser actually looks at
@app.route('/')
def dashboard():
    results = []
    for filename in os.listdir(PROJECTS_DIR):
        if filename.endswith(".yml") and filename != "playbook.yml":
            report = audit_file(os.path.join(PROJECTS_DIR, filename))
            results.append(report)
    return render_template('dashboard.html', reports=results)

# ANSI Colors for terminal debugging
G, Y, R, RESET = "\033[92m", "\033[93m", "\033[91m", "\033[0m"

def audit_file(path):
    try:
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
        
        if not isinstance(data, dict):
            raise ValueError("Not a dictionary")

        meta = data.get('project_metadata', {})
        total_val, done_val = 0, 0
        scheduled_tasks = []

        # Milestone and Task Processing
        for m in data.get('milestones', []):
            for req in m.get('requirements', []):
                for dlvr in req.get('deliverables', []):
                    total_val += 1
                    if dlvr.get('status') == 'Complete':
                        done_val += 1
                    
                    # Date Parsing for Calendar
                    task_name = dlvr.get('task', '')
                    if task_name.startswith('['):
                        try:
                            # Extract day from "[MM-DD]"
                            day_part = int(task_name[4:6])
                            scheduled_tasks.append({'day': day_part, 'name': task_name[7:]})
                        except (ValueError, IndexError):
                            continue

        return {
            'display': meta.get('display_name', os.path.basename(path)),
            'display_name': meta.get('display_name', os.path.basename(path)),
            'status': meta.get('status', 'G'),
            'last_updated': meta.get('last_updated', 'Unknown'),
            'alert_msg': meta.get('alert_msg', ''),
            'pct': int((done_val / total_val * 100)) if total_val > 0 else 100,
            'progress': int((done_val / total_val * 100)) if total_val > 0 else 100,
            'scheduled_tasks': scheduled_tasks
        }

    except Exception as e:
        return {
            'display': os.path.basename(path),
            'display_name': os.path.basename(path),
            'status': 'Y',
            'last_updated': 'ERROR',
            'alert_msg': f"Malformed: {str(e)}",
            'pct': 0,
            'progress': 0,
            'scheduled_tasks': []
        }

def run_pulse():
    results = []
    alerts = []
    
    for filename in os.listdir(PROJECTS_DIR):
        if filename.endswith(".yml") and filename != "playbook.yml":
            report = audit_file(os.path.join(PROJECTS_DIR, filename))
            results.append(report)
            
            # Special Handling for Alert Tab
            if report['status'] == 'R':
                alerts.append(report)
    
    results.sort(key=lambda x: x['last_updated'], reverse=True)
    
    # 1. Output terminal summary with colors (ROI)
    print(f"\n--- [ Hydra Pulse: {datetime.now().strftime('%H:%M')} ] ---")
    for r in results:
        color = R if r['status'] == 'R' else G
        icon = "■" if r['status'] == 'R' else "●"
        print(f"{color}{icon}{RESET} {r['display'][:15]:<15} | {r['pct']}% | {r['last_updated']}")

    # 2. Render Alert Tab if R events exist
    if alerts:
        print(f"\n{R}!!! ACTIVE ALERTS !!!{RESET}")
        for a in alerts:
            print(f" -> {a['display']}: {a['alert']}")

if __name__ == "__main__":
    run_pulse()
    print("\n--- Starting Web Dashboard on Port 5000 ---")
    app.run(host='0.0.0.0', port=5000, debug=False)
