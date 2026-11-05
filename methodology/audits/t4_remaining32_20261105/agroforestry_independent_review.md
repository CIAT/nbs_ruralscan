# Independent review of agroforestry targeting candidates

Reviewed 5 November 2026. Scope: the two staged Rao, Nair and Ong (1997) candidates and the Bayala et al. (2015) referral, against the user's mandatory spatial implementation gate. This is a bounded independent review, not a claim that either whole paper has been fully extracted. No registers, intake files or source dispositions were changed.

## Decision

The Rao et al. hedgerow-intercropping passage passes the gate narrowly as author guidance on the agroclimates and soil conditions in which this specific practice is appropriate. Keep both candidates unapproved pending the scope and quotation corrections below. Neither establishes a universal rainfall threshold, an independent soil-pH response, or an executable suitability curve.

The Bayala et al. passage does not pass the practice-level T4 gate. It selects tree functional traits within simulated parkland systems. Keep the page-linked species/trait referral, but change the source's gate disposition from `pass: true` to screen-only failure for this authorized practice-level lane. Its present zero-unit outcome is appropriate; a positive gate outcome is not.

## Identity and checks

I opened the cached PDFs with the native PDF parser and compared their page text with the staged extracts. Rao et al. has 48 PDF pages; pages 1, 3, 4, 13, 15 and 16 match the staged text exactly. Bayala et al. has 11 PDF pages; pages 1, 8 and 9 match exactly. Both cache SHA-256 values match their staged identity records. The identity records report identical team-library copies. Opening-page authors and titles agree with the staged identities: the source ID `nair1997_biophys_interactions` refers to Rao, Nair and Ong, *Biophysical interactions in tropical agroforestry systems*. The Bayala paper is *Advances in knowledge of processes in soil–tree–crop interactions in parkland systems in the West African Sahel: A review*.

## Rao, Nair and Ong (1997): corrections before intake

1. **Retain the conclusion's scope.** PDF page 15 (printed page 17) introduces the conclusion: “Interactions related to soil fertility (F) and competition for growth resources (C) dominate hedge/crop interactions in HI on lands with slopes of less than 15%”. The staged quotations begin on the next page and omit this scope. Add the preceding conclusion as supporting context and preserve the less-than-15% slope scope in both candidates. Do not turn that number into an independent slope mask: this sentence describes the scope of the interaction conclusion, not the maximum slope on which hedgerow intercropping can be implemented. PDF page 13 also says the 29-trial synthesis excluded experiments on sloping lands whose primary benefit was soil conservation.

2. **Expand C and F in explanatory prose without altering the verbatim quotation.** PDF page 3 (printed page 5) defines soil fertility (F) as soil chemical, physical and biological interactions, and competition (C) as competition for soil water, soil nutrients and radiation. PDF page 15 repeats “soil fertility (F)” and “competition for growth resources (C)”. Thus C does not mean a climate class, and F does not mean facilitation. Suggested explanatory sentence: “The authors describe a balance between soil-fertility improvement and competition for water, nutrients and light; management can alter that balance.” Retain the exact source symbols inside quotes and supply this explanation in context.

3. **Broaden the soil-pH candidate's quotation.** Its current quote says only that positive responses may occur on acid soils with lime and phosphorus inputs. Include the preceding page-16 sentence beginning “In semiarid environments with inadequate water” through “competitive to benefit crops,” and retain the following amendment exception. Otherwise the quotation hides the acid-*infertile* soil condition and appears to support a standalone pH response. Keep the relationship conditional and the direction unclear: the source does not isolate pH from fertility, water supply, species, management or duration.

4. **Preserve the rainfall exceptions.** PDF page 13 reports substantial increases in two of ten semiarid studies, including a bimodal-rainfall highland site and a site with good soil and hedgerow management. PDF page 15 reports mixed outcomes even above 2,000 mm. The present hold against a hard 1,000-mm cutoff or globally monotonic response is correct. Preserve `<1000 mm rainfall yr–1` as a reported contextual condition only.

5. **Keep practice and species claims separate.** The genuine practice-level anchor is the page-16 guidance concerning hedgerow intercropping, including “In agroclimates where HI is suitable”. The subsequent recommendations for named trees on acid versus base-rich soils do not establish a generic planted-silvoarable pH envelope. The existing species referral and crop-host referral should remain separate.

The full source does principally review interactions and performance. Its page-4 purpose nevertheless explicitly includes determining “the biophysical limits of the system,” and the page-15–16 conclusion converts the synthesis into practice-specific conditional implementation guidance. That supports the narrow gate decision; it does not license treating every interaction table or study-site climate as suitability evidence. The current `expert_assertion` attribution is defensible for this author conclusion, rather than treating all reviewed trials as newly observed independent measurements.

## Bayala et al. (2015): gate correction

PDF page 8 (printed page 32) identifies the underlying exercise as Coulibaly et al. (2014) simulations using WaNuLCAS: tree density, pruning, mulching and root patterns are varied under current and future climate to examine sorghum production. The selected anchor then says: “Tree species with dynamic canopy and performing hydraulic function with deep root system were found to be suitable for both flooding and drought situations but for different reasons.” Its object is **tree species and traits**, not the location or feasibility envelope of the parkland practice. This falls directly under the user's species-only-model exclusion.

PDF page 9's conclusion calls for further work to tailor interventions to contexts; it supplies no additional practice-placement rule that rescues this particular referral. Therefore preserve page 8 as a secondary species/trait pointer, with Coulibaly et al. (2014) attribution and no invented primary source ID, but do not count it as a passed practice-level T4 source. No new source acquisition or secondary-unit extraction is authorized by this review.

## Readability

Before central intake, rewrite compressed narrative strings such as `Source<1000mm`, `Directiononlyconditional`, `29long-termtrialreports` and `No sourcehumanapproval` as normal readable sentences. Exact quotations and machine identifiers should remain unchanged. The findings above concern semantic scope and gate compliance; they do not confer human approval or certify a full-paper extraction.

## Resolution applied after parent authorization

The findings above describe the original review. Parent subsequently authorized staging corrections, which are now applied: Bayala's gate is false in its gate file, report and aggregate summary; its original quotation remains as an excluded species/trait referral with zero T4 candidates. Both Rao candidates now contain the native PDF page 15 scope and page 3 definitions, and the soil-acidity quotation includes the preceding joint condition. The original Rao unit quotations and context are preserved in `nair1997_biophys_interactions/independent_review_originals.json`. Candidate explanations were expanded into readable prose. Shape validation returns no errors for either unit; both primary quotes and the added scope quote match native PDF text. No executable slope cutoff, live register change or full-paper completion claim was introduced. Central intake checks and human semantic review remain outstanding.
