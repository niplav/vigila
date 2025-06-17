### Procurement

[…]

Thermo Scientific is preferrable as a supplier because the Orexin likely
has higher purity, is available in powder form that can be stored in the
freezer indefinitely during the experiment (since neuropeptides such as
Orexin degrade fairly quickly when dissolved in liquid).

### In the Case of Success

> If we find a clear effect or promising indicators (like strong effects
on some psychological variables, but not others, and few or no negative
effects) we’ll talk to some prospective funders about running a more
large-scale experiment and publishing the results, possibly ARIA and
Emergent Ventures. TODO

If our experiment shows promising results, we'll contact some prospective
funders, e.g. ARIA or Emergent Ventures, about running a larger-scale
experiment and publishing the result. Promising results would include
strong effects on at least some psychological variables, and few or no
negative effects.

Since Orexin isn't patentable, it seems unlikely that this project could
be turned into a for-profit company. And since sleep isn't classified as a
disease, FDA approval appears unlikely. The best case is that this spurs
research into Orexin agonists for narcolepsy, and that Orexin is sold
at higher volume (and thus lower price) at online nootropics suppliers.

### Appendix: Other Experiments

### Appendix: Experimental Protocol

* Store Orexin powder in the freezer
* Before a block:
        * Dissolve Orexin powder in the saline solution in *one* spray bottle, so that it contains an adequate amount (administration results in ~1μg/kg of bodymass)
        * Put saline solution in the other bottle
        * Put the Orexin-filled spray bottle in one container, together with the 'O' piece of paper
        * Put the saline solution spray bottle in the other container, together with the 'P' piece of paper
        * Shuffle the containers until you don't remember which is which, put them in the fridge
* During the block:
        * Day 1:
                * Sleep only 5-6 hours
                * Pick a container at random, take out only the bottle, administer nasal spray
                * Mark the container so that you know that you took it on day one of the block
                * Wait 20 minutes
                * Run [a bunch of measurements](#Measurements)
		* In the evening (~16:00): Collect the measurements again
        * Day 2:
                * Sleep a normal amount
        * Day 3:
                * Sleep only 5-6 hours
                * Pick the other container, take out only the bottle, administer nasal spray
                * Mark the container so that you know that you took it on day three of the block
                * Wait 20 minutes
                * Run [a bunch of measurements](#Measurements)
		* In the evening (~16:00): Collect the measurements again
        * Day 4:
                * Sleep a normal amount
                * Look into the containers, write down whether you took placebo/orexin on days one and three

It doesn't matter when a block starts, it can be any day of the week,
and one can take a couple of days off from the experiment when something
(e.g. a holiday) comes in the way.

#### Measurements

We'd like to keep the measurements manageable and scalable: There is a
core of measurements performed in each block, but if I feel like I have
slack I might decide to do more extensive measurements for one block.

If done per block, this will not impact the quality of the data, but
please don't decide within a block to switch the detail of measurements.

Measurements were selected according to how much they
degrade with sleep deprivation, informed by [this auto-generated
report](./doc/orexin/impact_of_sleep_deprivation_on_psychological_metrics_elicit_2025.pdf)
using [Elicit](https://elicit.org/).

Most of the datapoints will be collected with an application using
pygame<!--TODO: link-->.

* Active measurements
        * Reaction speed via the [psychomotor vigilance task](https://en.wikipedia.org/wiki/Psychomotor_vigilance_task): ≥10 datapoints/day, collected via the tool
        * Attention via the [digit symbol substitution test](https://en.wikipedia.org/wiki/Digit_symbol_substitution_test): 1 datapoint/day, collected via the tool
        * Digit span: ≥10 datapoints/day, collected via the tool
        * [Stanford Sleepiness Scale](https://en.wikipedia.org/wiki/Stanford_Sleepiness_Scale)
        * Subjective well-being: ≥4 datapoints/day, collected via MoodPatterns
        * Time perception accuracy, collected via the tool
* Passive measurements
        * Whatever is collected by the fitbit
