"""Integrate directly observed collective selectors into the documentation handoff."""
import json


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
    return stats
