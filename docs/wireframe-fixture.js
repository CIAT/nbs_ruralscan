/* SYNTHETIC DISPLAY FIXTURE. These sequences are authored examples, not
   analytical thresholds, weights, evidence or schema-derived results.
   Keep separate from method/runtime code. No T0–T7 tables are loaded. */
window.WIREFRAME_FIXTURE = Object.freeze({
  version: 'illustration-2026-10-29.2',
  nominalAreaHa: 2500,
  suitability: {
    agro: ['vh','h','m','h','l','vh','m','h','unknown','excluded','h','m'],
    forest: ['m','vh','h','l','vh','m','h','unknown','h','excluded','m','h'],
    water: ['h','m','vh','h','m','l','h','unknown','vh','excluded','l','m']
  },
  future: {
    agro: ['h','m','m','vh','l','h','l','h','unknown','excluded','h','m'],
    forest: ['m','h','m','l','vh','h','h','unknown','m','excluded','h','h'],
    water: ['m','h','h','m','h','l','h','unknown','h','excluded','m','m']
  },
  priority: {
    resilience: ['vh','h','m','h','h','m','vh','h','h','m','l','h'],
    nature: ['l','m','vh','h','m','vh','l','h','m','h','h','l']
  },
  fire: [true,false,false,true,false,false,false,true,false,true,false,false],
  flood: [false,false,true,true,false,true,false,true,false,false,false,true],
  water: [true,true,false,false,true,false,false,true,false,true,false,false],
  food: [false,true,true,false,true,false,true,false,true,false,true,false],
  biodiversity: [true,false,true,false,false,true,true,false,true,false,false,true],
  people: [170,230,120,90,310,60,150,200,110,80,220,140]
});
