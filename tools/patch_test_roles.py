p = 'tests/test_fm26_roles.py'
with open(p, 'r', encoding='utf-8') as f:
    s = f.read().replace('\r\n', '\n')

old = """        self.assertEqual(ins('team','tempo','Lower')['value'],'Más bajo')
        self.assertEqual(ins('team','defensive_line_oop','Lower')['value'],'Más baja')
        # LATAM is literally "Alto" at this key; Spain's translation is "Alta".
        self.assertEqual(ins('team','defensive_line_oop','Higher')['value'],'Alto')"""

new = """        # Verified empirical labels in FM26 UI
        self.assertEqual(ins('team','tempo','Lower')['value'],'Bajo')
        self.assertEqual(ins('team','defensive_line_oop','Lower')['value'],'Más retrasada')
        self.assertEqual(ins('team','defensive_line_oop','Higher')['value'],'Más adelantada')
        self.assertEqual(ins('team','attacking_width_ip','Standard')['value'],'Estándar')
        self.assertEqual(ins('team','tackling_oop','Get Stuck In')['value'],'Ser agresivos')"""

assert old in s, "old string not found"
with open(p, 'w', encoding='utf-8') as f:
    f.write(s.replace(old, new))
print('test_fm26_roles.py updated successfully')
