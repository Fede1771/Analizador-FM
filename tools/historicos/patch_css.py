from pathlib import Path

p = Path("web/style.css")
c = p.read_text(encoding="utf-8")
c_norm = c.replace("\r\n", "\n")

old_phase_sp = """.phase-sp {
  background: #381a22;
  color: #fca5a5;
  border: 1px solid #7f1d1d;
}
.phase-cp {
  background: #143527;
  color: #86efac;
  border: 1px solid #166534;
}
.phase-pill {
  font-size: 0.72rem;
  font-weight: 750;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  padding: 3px 8px;
  border-radius: 4px;
}
.pill-sp {
  background: #3f1821;
  color: #fca5a5;
  border: 1px solid #991b1b;
}
.pill-cp {
  background: #143829;
  color: #86efac;
  border: 1px solid #15803d;
}"""

new_phase_sp = """.phase-sp {
  background: rgba(99, 102, 241, 0.12);
  color: #a5b4fc;
  border: 1px solid rgba(99, 102, 241, 0.28);
}
.phase-cp {
  background: rgba(45, 212, 191, 0.12);
  color: #5eead4;
  border: 1px solid rgba(45, 212, 191, 0.28);
}
.phase-pill {
  font-size: 0.72rem;
  font-weight: 750;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  padding: 3px 8px;
  border-radius: 4px;
}
.pill-sp {
  background: rgba(99, 102, 241, 0.14);
  color: #c7d2fe;
  border: 1px solid rgba(99, 102, 241, 0.35);
}
.pill-cp {
  background: rgba(45, 212, 191, 0.14);
  color: #99f6e4;
  border: 1px solid rgba(45, 212, 191, 0.35);
}"""

assert old_phase_sp in c_norm, "old_phase_sp not found in style.css"
c_norm = c_norm.replace(old_phase_sp, new_phase_sp, 1)

# Add grid layout and responsive rules at end of file
extra_css = """

/* Touchline Current View Grid & Responsive Layout */
.current-main-grid {
  display: grid;
  grid-template-columns: minmax(320px, 1.15fr) minmax(300px, 0.85fr);
  gap: 16px;
  align-items: start;
  margin-bottom: 20px;
}

.current-pitch-panel,
.current-priorities-panel {
  margin-bottom: 0;
}

.current-pitch-panel .split {
  margin-bottom: 12px;
}

.current-pitch-panel .pitch {
  margin: 0 auto;
}

.current-summary-panel {
  margin-bottom: 16px;
}

.current-details-panel {
  margin-bottom: 16px;
}

/* Compact headers and controls on narrow viewports */
@media (max-width: 960px) {
  .current-main-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .main-shell {
    padding: 12px 10px;
  }
  .page-heading {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
    margin-bottom: 14px;
  }
  .page-heading .actions {
    width: 100%;
    flex-wrap: wrap;
    gap: 6px;
  }
  .topbar .actions {
    flex-wrap: wrap;
    gap: 6px;
  }
  .executive-dashboard-grid {
    grid-template-columns: 1fr;
  }
  .table-scroll {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }
}
"""

c_norm += extra_css
p.write_text(c_norm, encoding="utf-8")
print("style.css updated successfully")
