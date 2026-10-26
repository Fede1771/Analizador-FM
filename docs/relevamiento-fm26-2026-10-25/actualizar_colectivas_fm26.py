"""Integrate directly observed collective selectors into the documentation handoff."""
import json
import re


def apply_team_review(out):
    path = out / 'verificacion-colectivas.json'
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding='utf-8'))
    controls = data['controls']
    def dump(name, value):
        (out / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    def update(name, replacements, appendix=''):
        p = out / name
        text = p.read_text(encoding='utf-8')
        for old, new in replacements:
            text = text.replace(old, new)
        marker = '\n## Actualización: selectores colectivos observados\n'
        if marker in text:
            text = text.split(marker)[0].rstrip() + '\n'
        if appendix:
            text += marker + '\n' + appendix + '\n'
        p.write_text(text, encoding='utf-8')

    count = len(controls)
    stats = {
        'team_selector_panels_verified': count,
        'team_selector_dimensions_verified': sum(len(c.get('dimensions', {})) or 1 for c in controls.values()),
        'shared_team_controls_verified': len(data['shared_state_checks']),
    }
    coverage = json.loads((out / 'cobertura-y-pendientes.json').read_text(encoding='utf-8'))
    coverage.update(stats)
    coverage.update(all_listed_team_selector_option_sets_observed=True,
                    all_team_instruction_variants_verified=False,
                    all_collective_option_help_texts_opened_in_ui=False,
                    marking_research='Excluido de nuevas verificaciones por indicación del usuario')
    dump('cobertura-y-pendientes.json', coverage)
    catalog = json.loads((out / 'catalogo-para-reconstruccion.json').read_text(encoding='utf-8'))
    catalog['team_instruction_selector_verification'] = data
    catalog['verification_coverage'] = coverage
    catalog['team_review_final_state'] = {
        'evidence': 'capturas/308-trampa-compartida-subfases.jpg',
        'changed_for_verification': ['Regate: Desanimar → Animar',
                                     'Carreras de apoyo: interior Ambas bandas → Equilibrado; banda Equilibrado → Ambas bandas',
                                     'Trampa de presión: interior → Presionar fuera'],
        'restoration_required': False,
        'note': 'Las instantáneas anteriores son históricas. No se avanzó fecha ni se guardó la partida en esta continuación.'}
    dump('catalogo-para-reconstruccion.json', catalog)

    lines = ['# Adenda: selectores colectivos observados en FM26',
             '', f'Se abrieron {count} paneles únicos de selectores colectivos en las ocho vistas. Hay 28 dimensiones de valor porque Carreras de apoyo contiene dos ejes. Las 29 apariciones anteriores incluyen dos controles repetidos: Regate y Trampa de presión. Capturas 276–308.',
             '', '**Alcance:** se transcribieron los conjuntos de opciones visibles. Esto no acredita la disponibilidad de cada opción bajo cualquier combinación ni que se hayan seleccionado todas o leído todas sus ayudas en pantalla. Las descripciones y reacciones por opción están en ANEXO-TEXTOS-INSTRUCCIONES.md como recursos instalados; no convertirlas en bloqueos comprobados.',
             '', '| Fase / área | Selector | Opciones visibles | Evidencia |', '|---|---|---|---|']
    for c in controls.values():
        options = '; '.join(c['options_ui'])
        if c.get('dimensions'):
            options = '<br>'.join(d['label_ui'] + ': ' + '; '.join(d['options_ui']) for d in c['dimensions'].values())
        lines.append('| ' + c['phase'] + ' | ' + c['label_ui'] + ' | ' + options + ' | [captura](' + c['evidence'] + ') |')
    lines += ['', '## Reglas comprobadas', '',
              '- Regate comparte estado entre Avance y Último tercio: Desanimar → Animar modifica ambas apariciones. [285](capturas/285-regate-compartido-subfases.jpg).',
              '- Trampa de presión comparte estado entre Presión adelantada y Bloque medio: interior → Presionar fuera modifica ambas apariciones. [308](capturas/308-trampa-compartida-subfases.jpg).',
              '- Carreras de apoyo tiene dos ejes: Doblar por banda y Doblar por dentro. Con interior Ambas bandas, las tres opciones no equilibradas de banda se muestran deshabilitadas [289](capturas/289-colectiva-carreras-apoyo.jpg). Con ambos ejes Equilibrado se habilitan [290](capturas/290-carreras-interiores-equilibradas.jpg). Con banda Ambas bandas, las tres opciones no equilibradas interiores se deshabilitan [291](capturas/291-doblar-ambas-bandas.jpg). No extrapolar esto a todas las combinaciones cruzadas de costado.',
              '', '## Consecuencias para Touchline', '',
              '- Conservar cinco niveles de Ritmo de juego, cinco de Pases directos, cinco de Amplitud del ataque, cinco de Línea defensiva y cinco de Activar presión.',
              '- Estilo de centros tiene cuatro valores, incluido Equilibrada. Buscar balón parado tiene dos; no agregar un tercer valor estándar.',
              '- Modelar una sola fuente de estado para Regate y otra para Trampa de presión, aunque se presenten en dos subfases.',
              '- Separar los dos ejes de Carreras de apoyo. No reducirlos a un enum con Equilibrado/Izquierda/Derecha/Ambas.',
              '- La distribución corta del portero en Sin posesión afecta la salida del portero rival y tiene No/Sí. Es distinta del destino y velocidad del propio portero en Con posesión.',
              '- Mantener los rótulos reales por selector: Equilibrado, Equilibrada, Estándar y Normal no son una única etiqueta universal.',
              '', '## Pendiente preciso', '',
              '- Variantes de disponibilidad por formación, mentalidad, puesto/rol, alcance Posición/Jugador y personalización. No se probaron todas las combinaciones.',
              '- Combinaciones cruzadas izquierda/derecha entre desdobles por banda y por dentro.',
              '- Confirmar si los botones duplicados Bandas y Laterales en el dibujo de distribución del propio portero son equivalentes o admiten diferencias por lado. Solo se transcribieron sus etiquetas, sin afirmar independencia.',
              '- Ayudas de cada alternativa: no se abrieron todas en la UI; los textos instalados se conservan con su procedencia.',
              '- Marcaje: excluido de la investigación adicional por pedido del usuario. No presentarlo como una tarea pendiente para retomar.',
              '- Identificadores de partida y pesos del motor: fuera del relevamiento visual; necesarios solo para una futura lectura automática o investigación del motor.',
              '', 'El JSON verificacion-colectivas.json conserva los controles, dimensiones, evidencia y límites. options_shown_available describe su apariencia en el contexto observado, no disponibilidad universal.']
    (out / 'ADENDA-COLECTIVAS.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    summary = (f'Se revisaron **{count} paneles colectivos únicos (28 dimensiones)** y se confirmaron dos controles compartidos. '
               'Leé [ADENDA-COLECTIVAS.md](ADENDA-COLECTIVAS.md) y [verificacion-colectivas.json](verificacion-colectivas.json). '
               'Estas pruebas cierran la lista de opciones visibles y las duplicaciones de Regate/Trampa de presión; las combinaciones de contexto y todas las ayudas siguen sin certificarse. '
               'El marcaje queda excluido de nuevas investigaciones por pedido del usuario.')
    update('REPORTE.md', [
        ('**no se abrieron todas las variantes de cada selector colectivo**', '**actualización: se abrieron los 27 paneles únicos y se transcribieron sus opciones; no todas las combinaciones ni ayudas**'),
        ('- Abrir todas las opciones colectivas para verificar disponibilidad y si los controles repetidos por subfase comparten valor.', '- Consultar ADENDA-COLECTIVAS.md: conjuntos de opciones y dos controles compartidos confirmados; falta verificar combinaciones de contexto y ayudas no abiertas.'),
        ('Queda comprobar cómo varían durante el partido y ante cambios rivales.', 'La investigación adicional de marcaje queda excluida por pedido del usuario.')], summary)
    update('PENDIENTES.md', [
        ('- Las ocho vistas colectivas están leídas, pero falta abrir todas las variantes, ayudas y restricciones de cada selector y comprobar qué controles repetidos comparten estado.', '- Los 27 selectores colectivos tienen opciones visibles registradas; Regate y Trampa de presión comparten estado. Restan combinaciones de contexto, cruce de costados en desdobles, equivalencia por lado de destinos del portero y ayudas no abiertas. Ver ADENDA-COLECTIVAS.md.'),
        ('- Los destinos de marca se verificaron en el prepartido observado. Falta su actualización durante un partido o ante cambios rivales.', '- Marcaje: excluido de nuevas verificaciones por pedido del usuario; se conserva la evidencia histórica.')], summary)
    observations = json.loads((out / 'observaciones-ui.json').read_text(encoding='utf-8'))
    update('INFORME-INTEGRAL.md', [
        ('Ocho vistas y 29 apariciones de controles; variantes aún pendientes', 'Ocho vistas, 29 apariciones, 27 selectores únicos con sus opciones; 28 dimensiones y dos estados compartidos confirmados'),
        ('276 registros de capturas', f'{len(observations)} registros de capturas'),
        ('- Todas las variantes, ayudas y restricciones colectivas, y si los controles repetidos por subfase comparten estado.', '- Combinaciones de contexto y ayudas colectivas aún no abiertas: ver ADENDA-COLECTIVAS.md. Los estados compartidos de Regate y Trampa de presión ya están confirmados.'),
        ('- Cómo se actualizan los objetivos de marca durante un partido y ante cambios rivales.', '- El marcaje queda excluido de nuevas verificaciones por pedido del usuario.')], summary)
    update('PROMPT-PARA-OTRA-IA.md', [], summary + '\n\nIntegrá estas opciones y únicamente los bloqueos observados, conservando el trabajo actual. No agregues nuevos requisitos de marcaje. Priorizá estos datos frente a listas históricas de variantes pendientes.')
    stats.update(_apply_side_review(out))
    stats.update(_apply_scope_closure(out))
    return stats


def _apply_side_review(out):
    source = out / 'verificacion-costados-portero-2026-10-26.json'
    if not source.exists():
        return {}
    data = json.loads(source.read_text(encoding='utf-8'))
    def dump(name, value):
        (out / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    def revise(name, replacements=(), appendix=''):
        path = out / name
        text = path.read_text(encoding='utf-8')
        for old, new in replacements:
            text = text.replace(old, new)
        marker = '\n## Actualización del 26/10/2026: costados y portero\n'
        if marker in text:
            text = text.split(marker)[0].rstrip() + '\n'
        if appendix:
            text += marker + '\n' + appendix + '\n'
        path.write_text(text, encoding='utf-8')

    stats = {'support_run_side_combinations_verified': len(data['support_runs']['matrix']),
             'support_run_side_combinations_selected': sum(r['allowed'] for r in data['support_runs']['matrix']),
             'support_run_side_combinations_blocked': sum(not r['allowed'] for r in data['support_runs']['matrix']),
             'gk_distribution_duplicate_button_pairs_verified': 2}
    coverage = json.loads((out / 'cobertura-y-pendientes.json').read_text(encoding='utf-8'))
    coverage.update(stats)
    coverage.update(support_run_side_matrix_verified_in_documented_context=True,
                    gk_distribution_duplicate_buttons_equivalent_verified=True)
    dump('cobertura-y-pendientes.json', coverage)
    catalog = json.loads((out / 'catalogo-para-reconstruccion.json').read_text(encoding='utf-8'))
    catalog['verification_coverage'] = coverage
    catalog['side_and_gk_verification_2026_10_26'] = data
    catalog['team_review_final_state_previous_review'] = catalog['team_review_final_state']
    catalog['team_review_final_state'] = data['final_state']
    dump('catalogo-para-reconstruccion.json', catalog)

    title = 'ADENDA-COSTADOS-PORTERO-2026-10-26.md'
    matrix = data['support_runs']['matrix']
    lines = ['# Continuación del 26/10/2026: desdobles por costado y distribución del portero', '',
             'Se cerraron las dos dudas específicas solicitadas. Se incorporaron 17 capturas (309–325). Pruebas en la partida del 14/9/2028 13:15, mentalidad Ofensivo y formación CP 3-2-4-1; estos resultados no certifican todos los contextos posibles.', '',
             '## Desdobles: matriz completa del selector en el contexto observado', '',
             'Cada eje elige Equilibrado, Izquierda, Derecha o Ambas bandas. Se seleccionaron las nueve combinaciones compatibles y se observaron las siete incompatibles como botones deshabilitados. Se intentó pulsar Interior derecha con Banda derecha y el caso izquierdo equivalente: no modificaron el estado.', '',
             '| Doblar por banda | Doblar por dentro | Resultado | Evidencia |', '|---|---|---|---|']
    for row in matrix:
        lines.append('| ' + row['overlap'] + ' | ' + row['underlap'] + ' | ' + ('Seleccionado' if row['allowed'] else 'Bloqueado') + ' | [captura](' + row['evidence'] + ') |')
    lines += ['', 'Los costados opuestos pueden coexistir: banda izquierda + interior derecha, y banda derecha + interior izquierda. En un mismo costado son excluyentes. Ambas bandas en un eje deja al otro únicamente Equilibrado.', '',
              'Regla de implementación que resume la observación: convertir cada valor en un conjunto de costados (Equilibrado = vacío) y permitir la pareja si su intersección es vacía. No presentar esta fórmula como código extraído del motor ni convertir Equilibrado en ausencia de movimientos espontáneos.', '',
              '## Distribución del propio portero', '',
              'Los dos botones Bandas son representaciones del mismo destino global. Los dos Laterales también. Se probaron los cuatro botones cambiando de destino: ambos del mismo nombre se resaltan simultáneamente, muestran el mismo título y descripción y dejan un único valor en el resumen. No son opciones izquierda/derecha.', '',
              '| Botón pulsado | Valor resultante | Evidencia |', '|---|---|---|']
    for row in data['gk_distribution_target']['checks']:
        lines.append('| ' + row['clicked'] + ' | ' + row['value_ui'] + ' | [captura](' + row['evidence'] + ') |')
    lines += ['', 'Mantener un selector de siete destinos; no agregar Bandas izquierda/derecha ni Laterales izquierda/derecha. Si la interfaz reproduce el dibujo de FM, ambos botones de cada nombre deben reflejar el mismo valor.', '',
              '## Entrega a la IA que trabaja en Touchline', '',
              'Integrar incrementalmente sobre el trabajo existente: aplicar la matriz documentada a los dos ejes de Carreras de apoyo y tratar los botones duplicados del portero como alias gráficos de un solo destino. Preservar datos y configuraciones. Si existen selecciones incompatibles, informarlas y permitir corregirlas sin reemplazarlas silenciosamente.', '',
              'Fuentes estructuradas: verificacion-costados-portero-2026-10-26.json, verificacion-colectivas.json y catálogo actualizado. El archivo nuevo contiene toda la matriz, pruebas de clic bloqueado, contexto y referencias de evidencia.', '',
              '## Pendientes restantes', '',
              '- Disponibilidad en otros contextos de puesto/rol, alcance, formación, mentalidad y personalización no ensayados.',
              '- Ayudas colectivas no abiertas individualmente; los textos de instalación ya están conservados.',
              '- Marcaje excluido por el usuario. Identificadores de partida y pesos del motor permanecen fuera del relevamiento visual.', '',
              'Estado final: ambos ejes de desdobles Equilibrado y destino del propio portero Laterales. [Captura final](capturas/325-cierre-costados-portero.jpg). No se avanzó fecha ni se guardó la partida.']
    (out / title).write_text('\n'.join(lines) + '\n', encoding='utf-8')
    summary = ('Quedaron cerrados los desdobles por costado y los botones duplicados del portero. '
               'La matriz 4×4 tiene nueve combinaciones seleccionadas y siete bloqueadas en el contexto observado: '
               'exterior e interior coexisten en lados opuestos y se excluyen en el mismo lado. '
               'Los dos botones Bandas son equivalentes entre sí; también los dos Laterales. '
               f'Leé [{title}]({title}) y [verificacion-costados-portero-2026-10-26.json](verificacion-costados-portero-2026-10-26.json). '
               'Se incorporaron 17 capturas nuevas. Persisten únicamente los contextos no ensayados y las ayudas no abiertas; no extrapolar reglas universales.')
    revise('ADENDA-COLECTIVAS.md', [
        ('No extrapolar esto a todas las combinaciones cruzadas de costado.', 'La matriz completa de costados quedó comprobada el 26/10/2026 en el contexto documentado; ver la nueva adenda.'),
        ('- Combinaciones cruzadas izquierda/derecha entre desdobles por banda y por dentro.\n', ''),
        ('- Confirmar si los botones duplicados Bandas y Laterales en el dibujo de distribución del propio portero son equivalentes o admiten diferencias por lado. Solo se transcribieron sus etiquetas, sin afirmar independencia.\n', '')], summary)
    revise('PENDIENTES.md', [
        ('Restan combinaciones de contexto, cruce de costados en desdobles, equivalencia por lado de destinos del portero y ayudas no abiertas.', 'Restan combinaciones de contexto y ayudas no abiertas. La matriz de desdobles por costado y la equivalencia de botones del portero quedaron cerradas el 26/10/2026.')], summary)
    revise('REPORTE.md', appendix=summary)
    revise('INFORME-INTEGRAL.md', appendix=summary)
    master = out / 'INFORME-INTEGRAL.md'
    text = master.read_text(encoding='utf-8')
    capture_count = len(json.loads((out / 'observaciones-ui.json').read_text(encoding='utf-8')))
    text = re.sub(r'\d+ registros de capturas', f'{capture_count} registros de capturas', text)
    master.write_text(text, encoding='utf-8')
    revise('PROMPT-PARA-OTRA-IA.md', appendix=summary + '\n\nConservá tu implementación actual e integrá únicamente lo que falte. No reinicies el proyecto ni reemplaces configuraciones del usuario. Validá los casos de costados opuestos, mismo costado y Ambas bandas, y la equivalencia de los cuatro botones probados del portero.')
    return stats


def _apply_scope_closure(out):
    source = out / 'cierre-relevamiento.json'
    if not source.exists():
        return {}
    closure = json.loads(source.read_text(encoding='utf-8'))
    summary = ('El relevamiento queda completo para el alcance acordado; no hay identificado un dato indispensable pendiente. '
               'Los contextos no ensayados y las ayudas no abiertas individualmente son límites no bloqueantes. '
               'No se confirmó que cambiar la mentalidad modifique los candados individuales: no implementar bloqueos por esa hipótesis. '
               'La búsqueda web no proporcionó una matriz universal ni certifica los textos exactos de la instalación; se conservan los recursos locales extraídos. '
               'Aplicar las restricciones documentadas con su procedencia, mantener desconocidos explícitos y revisar casos nuevos ante discrepancias concretas. '
               'El marcaje sigue excluido. Ver [ALCANCE-Y-CIERRE.md](ALCANCE-Y-CIERRE.md) y '
               '[PROMPT-ACTUALIZACION-INCREMENTAL.md](PROMPT-ACTUALIZACION-INCREMENTAL.md). '
               'Este cierre prevalece sobre listas históricas que parezcan exigir probar todas las combinaciones antes de implementar.')
    marker = '\n## Cierre del alcance acordado — 26/10/2026\n'
    for name in ('REPORTE.md', 'INFORME-INTEGRAL.md', 'PENDIENTES.md',
                 'ADENDA-COLECTIVAS.md', 'ADENDA-COSTADOS-PORTERO-2026-10-26.md',
                 'PROMPT-PARA-OTRA-IA.md'):
        path = out / name
        text = path.read_text(encoding='utf-8').split(marker)[0].rstrip()
        text = text.replace('falta verificar combinaciones de contexto y ayudas no abiertas.',
                            'las combinaciones de contexto y ayudas no abiertas son límites no bloqueantes del alcance acordado.')
        if name == 'PENDIENTES.md':
            text = text.replace('## Límites de verificación', '## Límites de verificación no bloqueantes')
            text = text.replace('Restan combinaciones de contexto y ayudas no abiertas.',
                                'No se ensayaron todas las combinaciones de contexto ni se abrieron todas las ayudas; no hay identificado un faltante indispensable.')
        if name == 'ADENDA-COSTADOS-PORTERO-2026-10-26.md':
            text = text.replace('## Pendientes restantes', '## Límites no bloqueantes de la verificación')
        if name == 'ADENDA-COLECTIVAS.md':
            text = text.replace('## Pendiente preciso', '## Límites no bloqueantes y exclusiones')
        path.write_text(text + '\n' + marker + '\n' + summary + '\n', encoding='utf-8')
    coverage_path = out / 'cobertura-y-pendientes.json'
    coverage = json.loads(coverage_path.read_text(encoding='utf-8'))
    coverage.update(agreed_scope_complete=True,
                    known_indispensable_missing_data=[],
                    universal_context_coverage_claimed=False,
                    mentality_changes_individual_locks_confirmed=False)
    coverage_path.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    catalog_path = out / 'catalogo-para-reconstruccion.json'
    catalog = json.loads(catalog_path.read_text(encoding='utf-8'))
    catalog['verification_coverage'] = coverage
    catalog['scope_closure_2026_10_26'] = closure
    catalog_path.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return {'agreed_scope_complete': True, 'known_indispensable_missing_data': []}
