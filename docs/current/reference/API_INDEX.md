# Generated MANA API Index

**Page kind:** Reference

This page is generated from the current function reference and runtime event/error definitions. Run `python tools/generate_reference_index.py` after changing those sources.

## Functions and language constructs

| Name | Description | Reference |
|---|---|---|
| `def name(parameters):` | define a normal calculation function | [Function reference](FUNCTION_REFERENCE.md#def-nameparameters-define-a-normal-calculation-function) |
| `spldef name():` | define a spell | [Function reference](FUNCTION_REFERENCE.md#spldef-name-define-a-spell) |
| `spldef name(element):` | define a base-element spell template | [Function reference](FUNCTION_REFERENCE.md#spldef-nameelement-define-a-base-element-spell-template) |
| `tune(spell.operation) = target, value` | update an existing operation | [Function reference](FUNCTION_REFERENCE.md#tunespelloperation-target-value-update-an-existing-operation) |
| `skip` | no-operation statement | [Function reference](FUNCTION_REFERENCE.md#skip-no-operation-statement) |
| `incant value` | supply a result to the caller | [Function reference](FUNCTION_REFERENCE.md#incant-value-supply-a-result-to-the-caller) |
| `name = create Element` | create a magical object | [Function reference](FUNCTION_REFERENCE.md#name-create-element-create-a-magical-object) |
| `Mana` | pure-mana type selector | [Function reference](FUNCTION_REFERENCE.md#mana-pure-mana-type-selector) |
| `mana` | pure-mana effects and universal control namespace | [Function reference](FUNCTION_REFERENCE.md#mana-pure-mana-effects-and-universal-control-namespace) |
| `name = tgset:` | define a target profile | [Function reference](FUNCTION_REFERENCE.md#name-tgset-define-a-target-profile) |
| `show value[, value ...]` | print output | [Function reference](FUNCTION_REFERENCE.md#show-value-value-or-showvalue-print-output) |
| `post(spell_name)` | trial command | [Function reference](FUNCTION_REFERENCE.md#postspellname-trial-command) |
| `release(spell_name)` | fire command | [Function reference](FUNCTION_REFERENCE.md#releasespellname-fire-command) |
| `load library_name` | load an optional library namespace | [Function reference](FUNCTION_REFERENCE.md#load-libraryname-load-an-optional-library-namespace) |
| `active_objects()` | inspect committed objects | [Function reference](FUNCTION_REFERENCE.md#activeobjects-inspect-committed-objects) |
| `detect(object[, property_name])` | Language construct | [Function reference](FUNCTION_REFERENCE.md#detectobject-propertyname) |
| `has_domain(element_object, domain_name)` | Language construct | [Function reference](FUNCTION_REFERENCE.md#hasdomainelementobject-domainname) |
| `span(stop)` | Language construct | [Function reference](FUNCTION_REFERENCE.md#spanstop-spanstart-stop-step) |
| `length(value)` | count a supported sequence | [Function reference](FUNCTION_REFERENCE.md#lengthvalue-count-a-supported-sequence) |
| `sqrt(value)` | Language construct | [Function reference](FUNCTION_REFERENCE.md#sqrtvalue) |
| `shape(object, geometry)` | Language construct | [Function reference](FUNCTION_REFERENCE.md#shapeobject-geometry) |
| `move(object, distance[, direction_vector])` | Language construct | [Function reference](FUNCTION_REFERENCE.md#moveobject-distance-directionvector) |
| `velocity(object, speed_or_vector)` | Language construct | [Function reference](FUNCTION_REFERENCE.md#velocityobject-speedorvector) |
| `accelerate(object, acceleration)` | Language construct | [Function reference](FUNCTION_REFERENCE.md#accelerateobject-acceleration) |
| `decelerate(object, acceleration)` | Language construct | [Function reference](FUNCTION_REFERENCE.md#decelerateobject-acceleration) |
| `tgset(target):` | temporary casting target | [Function reference](FUNCTION_REFERENCE.md#tgsettarget-temporary-casting-target) |
| `rotate(object, angle)` | Language construct | [Function reference](FUNCTION_REFERENCE.md#rotateobject-angle) |
| `scale(object, factor)` | Language construct | [Function reference](FUNCTION_REFERENCE.md#scaleobject-factor) |
| `reflect(object, surface_normal)` | Language construct | [Function reference](FUNCTION_REFERENCE.md#reflectobject-surfacenormal) |
| `anchor(object[, position_vector])` | Language construct | [Function reference](FUNCTION_REFERENCE.md#anchorobject-positionvector) |
| `unanchor(object)` | Language construct | [Function reference](FUNCTION_REFERENCE.md#unanchorobject) |
| `heat(object, temperature_change)` | Language construct | [Function reference](FUNCTION_REFERENCE.md#heatobject-temperaturechange) |
| `cool(object, temperature_change)` | Language construct | [Function reference](FUNCTION_REFERENCE.md#coolobject-temperaturechange) |
| `transform(object, state)` | Language construct | [Function reference](FUNCTION_REFERENCE.md#transformobject-state) |
| `compress(object, pressure)` | Language construct | [Function reference](FUNCTION_REFERENCE.md#compressobject-pressure) |
| `expand(object, volume)` | Language construct | [Function reference](FUNCTION_REFERENCE.md#expandobject-volume) |
| `combine(object_a, object_b[, mana_a=...][, mana_b=...])` | Language construct | [Function reference](FUNCTION_REFERENCE.md#combineobjecta-objectb-manaa-manab) |
| `separate(composite)` | Language construct | [Function reference](FUNCTION_REFERENCE.md#separatecomposite) |
| `split(object, parts)` | Language construct | [Function reference](FUNCTION_REFERENCE.md#splitobject-parts) |
| `bind(object[, anchor])` | Language construct | [Function reference](FUNCTION_REFERENCE.md#bindobject-anchor) |
| `dispel(object)` | Language construct | [Function reference](FUNCTION_REFERENCE.md#dispelobject) |
| `push(object, force[, direction])` | Language construct | [Function reference](FUNCTION_REFERENCE.md#pushobject-force-direction) |
| `pull(object, source_object, force)` | Language construct | [Function reference](FUNCTION_REFERENCE.md#pullobject-sourceobject-force) |
| `force(object)` | Language construct | [Function reference](FUNCTION_REFERENCE.md#forceobject) |
| `momentum(object)` | Language construct | [Function reference](FUNCTION_REFERENCE.md#momentumobject) |
| `kinetic_energy(object)` | Language construct | [Function reference](FUNCTION_REFERENCE.md#kineticenergyobject) |
| `pressure(object, area)` | Language construct | [Function reference](FUNCTION_REFERENCE.md#pressureobject-area) |
| `matter_to_mana(mass)` | Language construct | [Function reference](FUNCTION_REFERENCE.md#mattertomanamass) |
| `mana_to_matter(mana_amount)` | Language construct | [Function reference](FUNCTION_REFERENCE.md#manatomattermanaamount) |
| `mana_to_energy(mana_amount)` | Language construct | [Function reference](FUNCTION_REFERENCE.md#manatoenergymanaamount) |
| `energy_to_mana(energy)` | Language construct | [Function reference](FUNCTION_REFERENCE.md#energytomanaenergy) |
| `wait duration` | Language construct | [Function reference](FUNCTION_REFERENCE.md#wait-duration) |
| `after duration:` | Language construct | [Function reference](FUNCTION_REFERENCE.md#after-duration) |
| `every interval:` | Language construct | [Function reference](FUNCTION_REFERENCE.md#every-interval) |
| `when event_name:` | Language construct | [Function reference](FUNCTION_REFERENCE.md#when-eventname) |
| `advance_time(duration[, timestep=...][, gravity=...])` | Language construct | [Function reference](FUNCTION_REFERENCE.md#advancetimeduration-timestep-gravity) |
| `emit(event_name[, arguments...])` | Language construct | [Function reference](FUNCTION_REFERENCE.md#emiteventname-arguments) |
| `simul:` | Language construct | [Function reference](FUNCTION_REFERENCE.md#simul) |
| `last_collisions()` | inspect recent collision records | [Function reference](FUNCTION_REFERENCE.md#lastcollisions-inspect-recent-collision-records) |
| `c` | Language construct | [Function reference](FUNCTION_REFERENCE.md#c) |
| `pi` | Language construct | [Function reference](FUNCTION_REFERENCE.md#pi) |

## Events

| Event | Reference |
|---|---|
| `being_animated` | [Event names and rules](../foundations/EXECUTION_TIME_AND_EVENTS.md) |
| `being_reanimated` | [Event names and rules](../foundations/EXECUTION_TIME_AND_EVENTS.md) |
| `being_returned` | [Event names and rules](../foundations/EXECUTION_TIME_AND_EVENTS.md) |
| `being_summoned` | [Event names and rules](../foundations/EXECUTION_TIME_AND_EVENTS.md) |
| `being_tamed` | [Event names and rules](../foundations/EXECUTION_TIME_AND_EVENTS.md) |
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
