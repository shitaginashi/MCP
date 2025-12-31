import os
import re
import yaml
from datetime import datetime, timedelta

class Cerberus:
    def __init__(self, target_path='/data/projects/quarterly_master_schedule.yml'):
        self.target_path = target_path
        self.control_dna = {
            "2025-12-11": ["Control: Past Entry - Verified"],
            "2025-12-18": ["Control: Mid-Quarter - Verified"],
            "2025-12-25": ["Control: Current Day - Verified"]
        }

    def harvest_from_wreckage(self, bak_path):
        """Scrapes valid user data from wreckage. Always returns a dict."""
        harvested = {}
        if not os.path.exists(bak_path):
            return harvested
        try:
            with open(bak_path, 'r') as f:
                content = f.read()
            pattern = r'(\d{4}-\d{2}-\d{2}):\s+.*?user:\s+\[(.*?)\]'
            matches = re.findall(pattern, content, re.DOTALL)
            for date_str, user_content in matches:
                items = [item.strip().strip("'").strip('"') for item in user_content.split(',') if item.strip()]
                harvested[date_str] = items
        except Exception:
            pass
        return harvested

    def build_sterile_matrix(self, year, quarter):
        """Architects a fresh, valid 90-92 day quarterly chassis."""
        # Calculate start date: Q1=Jan, Q2=Apr, Q3=Jul, Q4=Oct
        month = (quarter - 1) * 3 + 1
        start_date = datetime(year, month, 1)
        matrix = {}
        
        # Build approximately 92 days (enough to cover any quarter)
        for i in range(92):
            current = start_date + timedelta(days=i)
            # Stop if we bleed into the next quarter
            current_q = (current.month - 1) // 3 + 1
            if current_q != quarter:
                break
                
            d_str = current.strftime('%Y-%m-%d')
            matrix[d_str] = {
                'annum': [], 
                'sage_hooks': [],
                'system': ['Scrape 01:00 - Y', 'Scrape 07:00 - Y', 'Scrape 13:00 - Y', 'Scrape 22:00 - Y'],
                'user': ['[SYSTEM R] - AWAITING DATA GRAFT']
            }
        return matrix

    def heal(self, bak_path, year=2025, quarter=4):
        """The core methodology: Pathing -> Harvest -> Inject -> Build -> Graft -> Deploy."""
        # 1. Rule: Only Q4 2025 is the master schedule; all others use yyyy-Q#.yml
        if year == 2025 and quarter == 4:
            self.target_path = '/data/projects/quarterly_master_schedule.yml'
        else:
            self.target_path = f'/data/projects/{year}-Q{quarter}.yml'

        # 2. Process Data
        data = self.harvest_from_wreckage(bak_path)
        data.update(self.control_dna)
        
        # 3. Build Matrix
        matrix = self.build_sterile_matrix(year, quarter)
        
        # 4. Graft survivors onto new chassis
        for date, entries in data.items():
            if date in matrix:
                matrix[date]['user'] = entries
        
        # 5. Deploy
        os.makedirs(os.path.dirname(self.target_path), exist_ok=True)
        with open(self.target_path, 'w') as f:
            yaml.dump(matrix, f, indent=2, sort_keys=False, default_flow_style=False)
        print(f"HEAL COMPLETE: {self.target_path}")

if __name__ == "__main__":
    # Internal trigger for testing
    c = Cerberus()
    c.heal('/data/projects/quarterly_master_schedule.yml.bak', 2026, 1)
