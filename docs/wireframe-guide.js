/* Guidance selections frame the walkthrough; they never set analytical weights. */
(function () {
  'use strict';
  const byId = id => document.getElementById(id);
  const introductions = {
    setup: ['What should this project improve?', 'Start with the problem, then explore where rural nature-based solutions could fit. This wireframe explains scoping; it is not a final tool design or a feasibility assessment.', 'Maps and figures are examples, not pilot results. Local partners must refine and validate any proposed intervention before implementation.'],
    vars: ['Which inputs and settings need closer inspection?', 'Technical configuration is optional. Inspect data coverage and local inputs first; review analytical rules and weights only when needed.', 'These are illustrative settings. Current recipe tables and runtime outputs are not connected; changing a control does not execute the method.'],
    opp: ['Where could these practices fit?', 'Explore the example footprint for each NbS, then inspect the livelihood needs and context within that opportunity space. Use the local selector to choose the practice being viewed.', 'Opportunity is a scoping result, not proof of site suitability, land availability or benefits. Example country, grid and climate labels describe the displayed illustration.'],
    prisk: ['What could damage the investment or obstruct delivery?', 'Inspect hazards affecting the intervention and conditions that could make implementation difficult. This is a different question from climate risk to rural livelihoods.', 'Read this as an illustrative screening concept, not an official World Bank risk rating or completed safeguards assessment. Local verification is still required.'],
    hotspot: ['Where do opportunities meet project priorities?', 'Compare example priority patterns within the opportunity space. Keep your project objectives in view when interpreting which places merit further investigation.', 'Your objectives guide this walkthrough; they do not set weights or recalculate rankings. Hotspots identify places to investigate, not approved investment sites.'],
    compare: ['Which NbS deserve closer consideration?', 'Compare the example footprints and response profiles of candidate practices. Use differences to frame a shortlist and identify evidence gaps.', 'These examples do not establish a preferred investment, cost-benefit result or guaranteed impact. Practices may overlap and need local assessment.'],
    next: ['What needs checking before implementation?', 'Turn the scoping discussion into questions for local partners and specialist studies. Identify missing data, design needs and conditions to validate.', 'The project delivers a methodology and reproducible pilot analyses. Detailed feasibility, hydrological modelling and engineering design sit downstream of this scoping work.'],
    todo: ['What remains under development?', 'Internal notes record unresolved design and method questions. They are not instructions for a project team using the scoping method.', 'This demonstrator includes provisional and illustrative content. Review notes do not establish agreed analytical rules.'],
    danger: ['Which actions need technical oversight?', 'This internal area illustrates administration controls outside the normal scoping journey.', 'Use the main sections to explore the method. This demonstrator does not run or administer a production analysis service.']
  };
  let previousPanel = 'setup';
  let returnPanel = 'setup';
  const currentPanel = () => document.querySelector('[role="tabpanel"][data-active]')?.dataset.tab || 'setup';
  function updateIntroduction() {
    const panel = currentPanel();
    if (panel === 'vars' && previousPanel !== 'vars') returnPanel = previousPanel;
    previousPanel = panel;
    const copy = introductions[panel] || introductions.setup;
    ['journey-title', 'journey-purpose', 'journey-limit'].forEach((id, i) => { byId(id).textContent = copy[i]; });
    byId('journey-config').hidden = ['vars', 'todo', 'danger'].includes(panel);
    byId('journey-back').hidden = panel !== 'vars';
    byId('journey-config').textContent = ['opp', 'hotspot'].includes(panel) ? 'Technical configuration for this section' : 'Inspect optional technical configuration';
  }
  const revealIntroduction = () => document.querySelector('.journey-intro').scrollIntoView({ block: 'start' });
  byId('journey-config').addEventListener('click', () => {
    const origin = currentPanel();
    window.openVariableConfig();
    const surface = origin === 'hotspot' ? 'priority' : 'suit';
    document.querySelector('.cfg-surface-switch button[data-surface="' + surface + '"]')?.click();
    revealIntroduction();
  });
  byId('journey-back').addEventListener('click', () => {
    if (returnPanel === 'setup') window.__setupSub = 'scope';
    byId('tab-' + returnPanel).click();
    revealIntroduction();
  });
  const objectives = Array.from(document.querySelectorAll('input[name="project-objective"]'));
  function updateObjectives() {
    const selected = objectives.filter(input => input.checked);
    objectives.forEach(input => { input.disabled = selected.length === 3 && !input.checked; });
    byId('journey-objectives').textContent = selected.length ? selected.map(input => input.value).join(' · ') : 'Choose two or three in Setup.';
    byId('objective-status').textContent = selected.length < 2 ? (selected.length ? 'One objective selected. Choose one or two more.' : 'No objectives selected. Choose two or three.') : selected.length + ' objectives selected. ' + (selected.length === 3 ? 'Deselect one to choose another.' : 'Continue, or choose one more.');
    byId('guide-to-scope').disabled = selected.length < 2;
  }
  objectives.forEach(input => input.addEventListener('change', updateObjectives));
  byId('guide-to-scope').addEventListener('click', () => {
    const scope = byId('setup-scope-details');
    scope.open = true;
    scope.querySelector('summary').focus();
    scope.scrollIntoView({ block: 'start' });
  });
  byId('guide-open-example').addEventListener('click', () => { byId('tab-opp').click(); revealIntroduction(); });
  document.addEventListener('wireframe:viewchange', updateIntroduction);
  updateObjectives();
  updateIntroduction();
})();
