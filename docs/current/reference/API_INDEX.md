# Generated MANA API Index

**Page kind:** Reference

This page is generated from the current function reference and runtime event/error definitions. Run `python tools/generate_reference_index.py` after changing those sources.

## Functions and language constructs

| Name | Description | Reference |
|---|---|---|
| `appraise spell_name` | preview a spell without committing | [Function reference](FUNCTION_REFERENCE.md#appraise-spell_name-preview-a-spell-without-committing) |
| `cast spell_name` | cast and commit a spell | [Function reference](FUNCTION_REFERENCE.md#cast-spell_name-cast-and-commit-a-spell) |
| `def name(parameters):` | define a normal calculation function | [Function reference](FUNCTION_REFERENCE.md#def-nameparameters-define-a-normal-calculation-function) |
| `spell name():` | define a spell | [Function reference](FUNCTION_REFERENCE.md#spell-name-define-a-spell) |
| `spell name(element):` | define a base-element spell template | [Function reference](FUNCTION_REFERENCE.md#spell-nameelement-define-a-base-element-spell-template) |
| `tune(spell.operation) = target, value` | update an existing operation | [Function reference](FUNCTION_REFERENCE.md#tunespelloperation-target-value-update-an-existing-operation) |
| `skip` | no-operation statement | [Function reference](FUNCTION_REFERENCE.md#skip-no-operation-statement) |
| `incant value` | supply a result to the caller | [Function reference](FUNCTION_REFERENCE.md#incant-value-supply-a-result-to-the-caller) |
| `name = create Element` | create a magical object | [Function reference](FUNCTION_REFERENCE.md#name-create-element-create-a-magical-object) |
| `Mana` | pure-mana type selector | [Function reference](FUNCTION_REFERENCE.md#mana-pure-mana-type-selector) |
| `mana` | pure-mana effects and universal control namespace | [Function reference](FUNCTION_REFERENCE.md#mana-pure-mana-effects-and-universal-control-namespace) |
| `name = tgset:` | define a target profile | [Function reference](FUNCTION_REFERENCE.md#name-tgset-define-a-target-profile) |
| `show value[, value ...]` | print output | [Function reference](FUNCTION_REFERENCE.md#show-value-value-or-showvalue-print-output) |
| `post(spell_name[, text|visual])` | legacy trial command | [Function reference](FUNCTION_REFERENCE.md#postspell_name-textvisual-legacy-trial-command) |
| `release(spell_name)` | legacy fire command | [Function reference](FUNCTION_REFERENCE.md#releasespell_name-legacy-fire-command) |
| `load library_name` | load an optional library namespace | [Function reference](FUNCTION_REFERENCE.md#load-library_name-load-an-optional-library-namespace) |
| `active_objects()` | inspect committed objects | [Function reference](FUNCTION_REFERENCE.md#active_objects-inspect-committed-objects) |
| `detect(object[, property_name])` | Language construct | [Function reference](FUNCTION_REFERENCE.md#detectobject-property_name) |
| `has_domain(element_object, domain_name)` | Language construct | [Function reference](FUNCTION_REFERENCE.md#has_domainelement_object-domain_name) |
| `span(stop)` | Language construct | [Function reference](FUNCTION_REFERENCE.md#spanstop-spanstart-stop-step) |
| `length(value)` | count a supported sequence | [Function reference](FUNCTION_REFERENCE.md#lengthvalue-count-a-supported-sequence) |
| `sqrt(value)` | Language construct | [Function reference](FUNCTION_REFERENCE.md#sqrtvalue) |
| `conjure(material[, mass][, position][, shape][, name][, density][, state])` | create physical material | [Function reference](FUNCTION_REFERENCE.md#conjurematerial-mass-position-shape-name-density-state-create-physical-material) |
| `summon(being[, source_plane][, position][, requirements])` | bring a catalogue being through a plane route | [Function reference](FUNCTION_REFERENCE.md#summonbeing-source_plane-position-requirements-bring-a-catalogue-being-through-a-plane-route) |
| `transmute(target, material[, preserve_mass=true][, density][, state])` | change material composition | [Function reference](FUNCTION_REFERENCE.md#transmutetarget-material-preserve_masstrue-density-state-change-material-composition) |
| `transfigure(target, form[, scale=1.0])` | change represented form | [Function reference](FUNCTION_REFERENCE.md#transfiguretarget-form-scale10-change-represented-form) |
| `world` | inspect and configure physical world laws | [Function reference](FUNCTION_REFERENCE.md#world-inspect-and-configure-physical-world-laws) |
| `periodic` | read-only periodic table and material reference | [Function reference](FUNCTION_REFERENCE.md#periodic-read-only-periodic-table-and-material-reference) |
| `weather.configure(kind="rain", ...)` | set world atmosphere | [Function reference](FUNCTION_REFERENCE.md#weatherconfigurekindrain-weatherset-set-world-atmosphere) |
| `shape(object, geometry)` | Language construct | [Function reference](FUNCTION_REFERENCE.md#shapeobject-geometry) |
| `move(object, distance[, direction_vector])` | Language construct | [Function reference](FUNCTION_REFERENCE.md#moveobject-distance-direction_vector) |
| `velocity(object, speed_or_vector)` | Language construct | [Function reference](FUNCTION_REFERENCE.md#velocityobject-speed_or_vector) |
| `impulse(object, momentum_vector)` | Language construct | [Function reference](FUNCTION_REFERENCE.md#impulseobject-momentum_vector) |
| `accelerate(object, acceleration)` | Language construct | [Function reference](FUNCTION_REFERENCE.md#accelerateobject-acceleration) |
| `decelerate(object, acceleration)` | Language construct | [Function reference](FUNCTION_REFERENCE.md#decelerateobject-acceleration) |
| `tgset(target):` | temporary casting target | [Function reference](FUNCTION_REFERENCE.md#tgsettarget-temporary-casting-target) |
| `rotate(object, angle)` | Language construct | [Function reference](FUNCTION_REFERENCE.md#rotateobject-angle) |
| `scale(object, factor)` | Language construct | [Function reference](FUNCTION_REFERENCE.md#scaleobject-factor) |
| `reflect(object, surface_normal)` | Language construct | [Function reference](FUNCTION_REFERENCE.md#reflectobject-surface_normal) |
| `anchor(object[, position_vector])` | Language construct | [Function reference](FUNCTION_REFERENCE.md#anchorobject-position_vector) |
| `unanchor(object)` | Language construct | [Function reference](FUNCTION_REFERENCE.md#unanchorobject) |
| `heat(object, temperature_change)` | Language construct | [Function reference](FUNCTION_REFERENCE.md#heatobject-temperature_change) |
| `cool(object, temperature_change)` | Language construct | [Function reference](FUNCTION_REFERENCE.md#coolobject-temperature_change) |
| `transform(object, state)` | Language construct | [Function reference](FUNCTION_REFERENCE.md#transformobject-state) |
| `compress(object, pressure)` | Language construct | [Function reference](FUNCTION_REFERENCE.md#compressobject-pressure) |
| `expand(object, volume)` | Language construct | [Function reference](FUNCTION_REFERENCE.md#expandobject-volume) |
| `combine(object_a, object_b[, mana_a=...][, mana_b=...])` | Language construct | [Function reference](FUNCTION_REFERENCE.md#combineobject_a-object_b-mana_a-mana_b) |
| `separate(composite)` | Language construct | [Function reference](FUNCTION_REFERENCE.md#separatecomposite) |
| `split(object, parts)` | Language construct | [Function reference](FUNCTION_REFERENCE.md#splitobject-parts) |
| `bind(object[, anchor])` | Language construct | [Function reference](FUNCTION_REFERENCE.md#bindobject-anchor) |
| `dispel(object)` | Language construct | [Function reference](FUNCTION_REFERENCE.md#dispelobject) |
| `push(object, force[, direction])` | Language construct | [Function reference](FUNCTION_REFERENCE.md#pushobject-force-direction) |
| `pull(object, source_object, force)` | Language construct | [Function reference](FUNCTION_REFERENCE.md#pullobject-source_object-force) |
| `force(object)` | Language construct | [Function reference](FUNCTION_REFERENCE.md#forceobject) |
| `momentum(object)` | Language construct | [Function reference](FUNCTION_REFERENCE.md#momentumobject) |
| `kinetic_energy(object)` | Language construct | [Function reference](FUNCTION_REFERENCE.md#kinetic_energyobject) |
| `pressure(object, area)` | Language construct | [Function reference](FUNCTION_REFERENCE.md#pressureobject-area) |
| `matter_to_mana(mass)` | Language construct | [Function reference](FUNCTION_REFERENCE.md#matter_to_manamass) |
| `mana_to_matter(mana_amount)` | Language construct | [Function reference](FUNCTION_REFERENCE.md#mana_to_mattermana_amount) |
| `mana_to_energy(mana_amount)` | Language construct | [Function reference](FUNCTION_REFERENCE.md#mana_to_energymana_amount) |
| `energy_to_mana(energy)` | Language construct | [Function reference](FUNCTION_REFERENCE.md#energy_to_manaenergy) |
| `wait duration` | Language construct | [Function reference](FUNCTION_REFERENCE.md#wait-duration) |
| `after duration:` | Language construct | [Function reference](FUNCTION_REFERENCE.md#after-duration) |
| `every interval:` | Language construct | [Function reference](FUNCTION_REFERENCE.md#every-interval) |
| `when event_name:` | Language construct | [Function reference](FUNCTION_REFERENCE.md#when-event_name) |
| `advance_time(duration[, timestep=...][, gravity=...])` | Language construct | [Function reference](FUNCTION_REFERENCE.md#advance_timeduration-timestep-gravity) |
| `emit(event_name[, arguments...])` | Language construct | [Function reference](FUNCTION_REFERENCE.md#emitevent_name-arguments) |
| `simul:` | Language construct | [Function reference](FUNCTION_REFERENCE.md#simul) |
| `last_collisions()` | inspect recent collision records | [Function reference](FUNCTION_REFERENCE.md#last_collisions-inspect-recent-collision-records) |
| `c` | Language construct | [Function reference](FUNCTION_REFERENCE.md#c) |
| `pi` | Language construct | [Function reference](FUNCTION_REFERENCE.md#pi) |

## Events

| Event | Reference |
|---|---|
| `being_animated` | [Event names and rules](../foundations/EXECUTION_TIME_AND_EVENTS.md) |
| `being_died` | [Event names and rules](../foundations/EXECUTION_TIME_AND_EVENTS.md) |
| `being_lichified` | [Event names and rules](../foundations/EXECUTION_TIME_AND_EVENTS.md) |
| `being_reanimated` | [Event names and rules](../foundations/EXECUTION_TIME_AND_EVENTS.md) |
| `being_reconstituted` | [Event names and rules](../foundations/EXECUTION_TIME_AND_EVENTS.md) |
| `being_returned` | [Event names and rules](../foundations/EXECUTION_TIME_AND_EVENTS.md) |
| `being_revived` | [Event names and rules](../foundations/EXECUTION_TIME_AND_EVENTS.md) |
| `being_summoned` | [Event names and rules](../foundations/EXECUTION_TIME_AND_EVENTS.md) |
| `being_tamed` | [Event names and rules](../foundations/EXECUTION_TIME_AND_EVENTS.md) |
| `blood_changed` | [Event names and rules](../foundations/EXECUTION_TIME_AND_EVENTS.md) |
| `collision` | [Event names and rules](../foundations/EXECUTION_TIME_AND_EVENTS.md) |
| `damaged` | [Event names and rules](../foundations/EXECUTION_TIME_AND_EVENTS.md) |
| `energy_arrived` | [Event names and rules](../foundations/EXECUTION_TIME_AND_EVENTS.md) |
| `impact` | [Event names and rules](../foundations/EXECUTION_TIME_AND_EVENTS.md) |
| `mana_burst` | [Event names and rules](../foundations/EXECUTION_TIME_AND_EVENTS.md) |
| `mana_emitted` | [Event names and rules](../foundations/EXECUTION_TIME_AND_EVENTS.md) |
| `mana_formed` | [Event names and rules](../foundations/EXECUTION_TIME_AND_EVENTS.md) |
| `object_ignited` | [Event names and rules](../foundations/EXECUTION_TIME_AND_EVENTS.md) |
| `path_closed` | [Event names and rules](../foundations/EXECUTION_TIME_AND_EVENTS.md) |
| `path_opened` | [Event names and rules](../foundations/EXECUTION_TIME_AND_EVENTS.md) |
| `plane_created` | [Event names and rules](../foundations/EXECUTION_TIME_AND_EVENTS.md) |

## Error classes

| Error class | Reference |
|---|---|
| `MagicLangError` | [Error catalogue](ERROR_CATALOGUE.md) |
| `SyntaxErrorML` | [Error catalogue](ERROR_CATALOGUE.md) |
| `TypeErrorML` | [Error catalogue](ERROR_CATALOGUE.md) |
| `UnitErrorML` | [Error catalogue](ERROR_CATALOGUE.md) |
| `RuntimeErrorML` | [Error catalogue](ERROR_CATALOGUE.md) |
| `MagicErrorML` | [Error catalogue](ERROR_CATALOGUE.md) |
| `PhysicsErrorML` | [Error catalogue](ERROR_CATALOGUE.md) |
