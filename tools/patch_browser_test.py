path = 'tests/browser.test.mjs'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read().replace('\r\n', '\n')

old_target = """  await check('pressing request retains counterpress',async()=>{await set('#prompt-input','Presión alta, recuperar rápido','input');await evaluate(`document.querySelector('[data-action="apply-prompt"]').click()`);await ready();assert.equal(await evaluate(`document.querySelector('#style-select').value`),'press');assert.equal(await evaluate(`document.querySelector('#override-defensive_transition_oop').value`),'Counter-Press');});"""

new_check = """  await check('pressing request retains counterpress',async()=>{await set('#prompt-input','Presión alta, recuperar rápido','input');await evaluate(`document.querySelector('[data-action="apply-prompt"]').click()`);await ready();assert.equal(await evaluate(`document.querySelector('#style-select').value`),'press');assert.equal(await evaluate(`document.querySelector('#override-defensive_transition_oop').value`),'Counter-Press');});
  await check('collective instructions options and support runs mutual exclusions',async()=>{
    await evaluate(`document.querySelector('#override-tempo').closest('details').open=true`);
    assert.equal(await evaluate(`document.querySelectorAll('#override-attacking_width_ip option').length`), 5);
    assert.equal(await evaluate(`document.querySelectorAll('#override-tempo option').length`), 5);
    assert.equal(await evaluate(`document.querySelectorAll('#override-crossing_style_ip option').length`), 4);
    assert.equal(await evaluate(`document.querySelectorAll('#override-play_for_set_pieces_ip option').length`), 2);
    assert.equal(await evaluate(`document.querySelectorAll('#override-short_goalkeeper_distribution_oop option').length`), 2);

    await set('#override-underlap_ip', 'Underlap - Both Flanks');
    const overlapDisabled = await evaluate(`Array.from(document.querySelectorAll('#override-overlap_ip option')).filter(o => o.disabled).map(o => o.value)`);
    assert.deepEqual(overlapDisabled, ['Overlap - Left', 'Overlap - Right', 'Overlap - Both Flanks']);

    await set('#override-underlap_ip', 'Underlap - Balanced');
    const overlapReenabled = await evaluate(`Array.from(document.querySelectorAll('#override-overlap_ip option')).filter(o => o.disabled).length`);
    assert.equal(overlapReenabled, 0);
  });"""

assert old_target in text, "old_target not found in browser.test.mjs"
text = text.replace(old_target, new_check)
with open(path, 'w', encoding='utf-8') as f:
    f.write(text)
print('Updated tests/browser.test.mjs with collective instructions test')
