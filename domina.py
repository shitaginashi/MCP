import sys, yaml, os, subprocess
from datetime import datetime, timedelta
from dateutil.rrule import rrulestr

PROJECTS_DIR = "/data/projects"
PLAYBOOK_PATH = os.path.join(PROJECTS_DIR, "playbook.yml")

class DominaCLI:
    # ANSI Color Codes
    G, Y, R, RESET = "\033[92m", "\033[93m", "\033[91m", "\033[0m"

    def color_log(self, level, message):
        """Returns a color-formatted string for terminal output."""
        icon = {"G": "●", "Y": "▲", "R": "■"}.get(level, "○")
        return f"{getattr(self, level)}{icon}{self.RESET} {message}"

    def _load_yaml(self, path):
        """Universal Shield: Catches ScannerErrors and returns dict or None."""
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    return yaml.safe_load(f)
            except Exception as e:
                print(self.color_log("R", f"Critically Malformed YAML at {os.path.basename(path)}: {e}"))
                return None
        return {}

    def log_event(self, project_file, task, status, msg, urgent=False):
        """NASA-grade Dual-Track Memory: 150-entry FIFO + Critical Pinning."""
        if not project_file.endswith(".yml"):
            project_file += ".yml"
        path = os.path.join(PROJECTS_DIR, project_file)
        data = self._load_yaml(path)
        if data is None: return

        meta = data.setdefault('project_metadata', {})
        meta['status'] = status
        meta['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        entry = {"ts": meta['last_updated'], "task": task, "status": status, "msg": msg}
        logs = data.setdefault('logs', {})

        if urgent or status == "R":
            logs.setdefault('pinned', []).append(entry)
            meta['alert_msg'] = msg
        else:
            fifo = logs.setdefault('fifo', [])
            fifo.append(entry)
            logs['fifo'] = fifo[-150:]

        with open(path, 'w') as f:
            yaml.dump(data, f, sort_keys=False)

    def get_agenda(self):
        playbook = self._load_yaml(PLAYBOOK_PATH)
        schedules = playbook.get('schedules', [])
        now = datetime.now()
        end_of_week = now + timedelta(days=7)
        
        print(f"\n--- [ Hydra Agenda: {now.strftime('%Y-%m-%d')} ] ---")
        found = False
        for item in schedules:
            try:
                rule = rrulestr(item['rule'], dtstart=now)
                next_occ = rule.after(now, inc=True)
                if next_occ and next_occ <= end_of_week:
                    level = "R" if item.get('requires_wake') else "G"
                    status_icon = "⚡" if level == "R" else "☁️"
                    msg = f"[{next_occ.strftime('%a %d')}] {item['task']} {status_icon}"
                    print(self.color_log(level, msg))
                    found = True
            except Exception:
                continue
        if not found:
            print("No actionable events scheduled.")

    def run_play(self, play_id):
        playbook = self._load_yaml(PLAYBOOK_PATH)
        play = next((p for p in playbook.get('immortal_plays', []) if p['id'] == play_id), None)
        target = play_id.split('_')[0] if "_" in play_id else "hydra"

        if play:
            try:
                print(f"[*] Executing {play_id}...")
                subprocess.run(play['cmd'], shell=True, check=True)
                self.log_event(target, play_id, "G", "Success")
            except subprocess.CalledProcessError as e:
                self.log_event(target, play_id, "R", str(e), urgent=True)
                print(self.color_log("R", f"Execution failed: {e}"))
        else:
            print(f"[!] Play {play_id} not found.")

    def review(self, project_file):
        """Interactive CLI session to update project status and review bugs."""
        if not project_file.endswith(".yml"):
            project_file += ".yml"
        path = os.path.join(PROJECTS_DIR, project_file)
        data = self._load_yaml(path)
        if not isinstance(data, dict): return
        
        print(f"\n--- [ Reviewing: {data.get('project_metadata', {}).get('display_name', project_file)} ] ---")
        
        pinned = data.get('logs', {}).get('pinned', [])
        if pinned:
            print(f"{self.R}[!] ACTIVE BUGS/ALERTS:{self.RESET}")
            for i, bug in enumerate(pinned):
                print(f"  {i+1}. {bug['ts']} - {bug['task']}: {bug['msg']}")
            if input("\nClear pinned bugs? (y/n): ").lower() == 'y':
                data['logs']['pinned'] = []

        for m in data.get('milestones', []):
            if m['status'] != "Complete":
                print(f"\nMilestone: {self.Y}{m['mark']}{self.RESET}")
                for req in m.get('requirements', []):
                    for dlvr in req.get('deliverables', []):
                        if dlvr.get('status') != "Complete":
                            print(f"  [ ] {dlvr['task']}")
                            if input("    Mark Complete? (y/n): ").lower() == 'y':
                                dlvr['status'] = "Complete"
                                dlvr['notes'] = input("    Note: ")

        with open(path, 'w') as f:
            yaml.dump(data, f, sort_keys=False)
        print(self.color_log("G", "Hardened."))

    def report(self):
        """The Narrator Bridge: Context for LLM with Health Stats."""
        context = []
        for f in os.listdir(PROJECTS_DIR):
            if f.endswith(".yml") and f != "playbook.yml":
                d = self._load_yaml(os.path.join(PROJECTS_DIR, f))
                if not isinstance(d, dict): continue

                logs_data = d.get('logs', {})
                if not isinstance(logs_data, dict): logs_data = {}
                
                fifo = logs_data.get('fifo', [])
                total = len(fifo)
                successes = len([e for e in fifo if e['status'] == "G"])
                rate = (successes / total * 100) if total > 0 else 100
                
                context.append({
                    "project": f,
                    "health": f"{rate:.1f}%",
                    "recent": fifo[-5:],
                    "pinned": logs_data.get('pinned', [])
                })
        print(f"\n--- [ {self.Y}Narrator Context{self.RESET} ] ---")
        print(yaml.dump(context, sort_keys=False))

    def propose(self, goal):
        cmd = "rsync -avzu /data/projects/ kuma@pusheen:/mnt/d/007/projects/"
        if "agent" in goal.lower():
            cmd = "rsync -avzu ~/agents/ kuma@pusheen:/mnt/d/007/agents/"
        print(yaml.dump([{"id": "sync", "cmd": cmd}], sort_keys=False))

    def execute(self, cmd, target=None):
        if cmd == "agenda": self.get_agenda()
        elif cmd == "run": self.run_play(target)
        elif cmd == "report": self.report()
        elif cmd == "review": self.review(target)
        elif cmd == "propose": self.propose(target)
        elif cmd == "update_timestamp": self.update_timestamp()
        else: print(f"[!] {cmd} unknown.")

    def update_timestamp(self):
        """Global Pulse: Updates the last_updated field for all projects."""
        for f in os.listdir(PROJECTS_DIR):
            if f.endswith(".yml") and f != "playbook.yml":
                path = os.path.join(PROJECTS_DIR, f)
                data = self._load_yaml(path)
                if isinstance(data, dict):
                    meta = data.setdefault('project_metadata', {})
                    meta['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M")
                    with open(path, 'w') as f_out:
                        yaml.dump(data, f_out, sort_keys=False)
        print(self.color_log("G", "Global Pulse: All timestamps synchronized."))

def update_timestamp(self):
        """Global Pulse: Updates the last_updated field for all projects."""
        for f in os.listdir(PROJECTS_DIR):
            if f.endswith(".yml") and f != "playbook.yml":
                path = os.path.join(PROJECTS_DIR, f)
                data = self._load_yaml(path)
                if isinstance(data, dict):
                    meta = data.setdefault('project_metadata', {})
                    meta['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M")
                    with open(path, 'w') as f_out:
                        yaml.dump(data, f_out, sort_keys=False)
        print(self.color_log("G", "Global Pulse: All timestamps synchronized."))

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "agenda"
    arg = sys.argv[2] if len(sys.argv) > 2 else None
    DominaCLI().execute(cmd, arg)
