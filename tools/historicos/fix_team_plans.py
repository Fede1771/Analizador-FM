from pathlib import Path

fm26_path = Path('fm_app/fm26.py')
code = fm26_path.read_text(encoding='utf-8')

# Ensure underlap_ip is in all 4 plans
# In possession:
code = code.replace(
    "'dribbling_ip':'Balanced','overlap_ip':'Overlap - Balanced',",
    "'dribbling_ip':'Balanced','overlap_ip':'Overlap - Balanced','underlap_ip':'Underlap - Balanced',"
)

# In press:
code = code.replace(
    "'dribbling_ip':'Encourage','overlap_ip':'Overlap - Both Flanks',",
    "'dribbling_ip':'Encourage','overlap_ip':'Overlap - Both Flanks','underlap_ip':'Underlap - Balanced',"
)

# In counter:
code = code.replace(
    "'dribbling_ip':'Encourage','overlap_ip':'Overlap - Balanced',\n\n     'patience_ip':",
    "'dribbling_ip':'Encourage','overlap_ip':'Overlap - Balanced','underlap_ip':'Underlap - Balanced',\n\n     'patience_ip':"
)
code = code.replace(
    "'short_goalkeeper_distribution_oop':'No',\n\n     'pressing_trap_oop':'Trap Outside'",
    "'short_goalkeeper_distribution_oop':'No','tackling_oop':'Standard',\n\n     'pressing_trap_oop':'Trap Outside'"
)

# In wide:
code = code.replace(
    "'dribbling_ip':'Encourage','overlap_ip':'Overlap - Both Flanks',\n\n     'patience_ip':",
    "'dribbling_ip':'Encourage','overlap_ip':'Overlap - Both Flanks','underlap_ip':'Underlap - Balanced',\n\n     'patience_ip':"
)
code = code.replace(
    "'short_goalkeeper_distribution_oop':'No',\n\n     'pressing_trap_oop':'Trap Inside'",
    "'short_goalkeeper_distribution_oop':'No','tackling_oop':'Standard',\n\n     'pressing_trap_oop':'Trap Inside'"
)

fm26_path.write_text(code, encoding='utf-8')
print('Updated TEAM_PLANS in fm_app/fm26.py')
