import os
from datetime import datetime

REPORT_ROOT = "/data/reports"
DASH_OUTPUT = "/data/reports/dashboard.html"

class CoreDashboard:
    def assemble(self):
        # Gather only the fragments
        fragments = [f for f in os.listdir(REPORT_ROOT) if f.endswith(".frag.html")]
        fragments.sort() # Keep them in alphabetical/logical order
        
        frag_content = ""
        for f_name in fragments:
            with open(os.path.join(REPORT_ROOT, f_name), 'r', encoding='utf-8') as f:
                frag_content += f.read()

        html = f"""
        <!DOCTYPE html><html><head>
        <title>KURO COMMAND CENTER</title>
        <style>
            body {{ background: #010409; color: #c9d1d9; font-family: 'Segoe UI', sans-serif; margin: 20px; }}
            h1 {{ border-bottom: 2px solid #58a6ff; padding-bottom: 10px; margin-bottom: 30px; }}
            .grid {{ 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); 
                gap: 25px; 
                align-items: start;
            }}
            .project-frag {{ 
                background: #0d1117; 
                border: 1px solid #30363d; 
                padding: 20px; 
                border-radius: 8px; 
                box-shadow: 0 4px 10px rgba(0,0,0,0.3);
            }}
            .milestone {{ background: #161b22; margin: 10px 0; padding: 10px; border-radius: 4px; border: 1px solid #30363d; }}
            summary {{ cursor: pointer; font-weight: bold; font-size: 1.1em; outline: none; }}
            .deliverables-list {{ list-style: none; padding-left: 15px; margin-top: 10px; border-left: 1px solid #30363d; }}
            .deliverable {{ font-size: 0.9em; margin-bottom: 5px; color: #8b949e; }}
            .complete {{ color: #3fb950; font-weight: bold; }}
            .incomplete {{ color: #f85149; }}
            .timestamp {{ float: right; font-size: 0.5em; color: #58a6ff; }}
        </style>
        </head><body>
            <h1>KURO COMMAND CENTER <span class="timestamp">SYNC: {datetime.now().strftime('%Y-%m-%d %H:%M')}</span></h1>
            <div class="grid">
                {frag_content if frag_content else "<p>Waiting for fragments...</p>"}
            </div>
        </body></html>"""

        with open(DASH_OUTPUT, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"--- DASHBOARD_READY: {DASH_OUTPUT} ---")

if __name__ == "__main__":
    CoreDashboard().assemble()
