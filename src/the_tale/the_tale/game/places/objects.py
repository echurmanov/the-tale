
import smart_imports

smart_imports.all()


class Place(game_names.ManageNameMixin2):
    __slots__ = ('id',
                 'x', 'y',
                 'updated_at',
                 'updated_at_turn',
                 'created_at',
                 'created_at_turn',
                 'habit_honor',
                 'habit_honor_positive',
                 'habit_honor_negative',
                 'habit_peacefulness',
                 'habit_peacefulness_positive',
                 'habit_peacefulness_negative',
                 'is_frontier',
                 'description',
                 'race',
                 'persons_changed_at_turn',
                 'attrs',
                 'utg_name',
                 'races',
                 'nearest_cells',
                 'effects',
                 'job',
                 '_modifier',

                 # mames mixin
                 '_utg_name_form__lazy',
                 '_name__lazy')

    def __init__(self,
                 id,
                 x, y,
                 updated_at,
                 updated_at_turn,
                 created_at,
                 created_at_turn,
                 habit_honor,
                 habit_honor_positive,
                 habit_honor_negative,
                 habit_peacefulness,
                 habit_peacefulness_positive,
                 habit_peacefulness_negative,
                 is_frontier,
                 description,
                 race,
                 persons_changed_at_turn,
                 attrs,
                 utg_name,
                 races,
                 nearest_cells,
                 effects,
                 job,
                 modifier):
        self.id = id
        self.x = x
        self.y = y
        self.updated_at = updated_at
        self.updated_at_turn = updated_at_turn
        self.created_at = created_at
        self.created_at_turn = created_at_turn
        self.habit_honor = habit_honor
        self.habit_honor_positive = habit_honor_positive
        self.habit_honor_negative = habit_honor_negative
        self.habit_peacefulness = habit_peacefulness
        self.habit_peacefulness_positive = habit_peacefulness_positive
        self.habit_peacefulness_negative = habit_peacefulness_negative
        self.is_frontier = is_frontier
        self.description = description
        self.race = race
        self.persons_changed_at_turn = persons_changed_at_turn
        self.attrs = attrs
        self.utg_name = utg_name
        self.races = races
        self.nearest_cells = nearest_cells
        self.effects = effects
        self.job = job
        self._modifier = modifier

    @property
    def updated_at_game_time(self): return tt_calendar.converter(self.updated_at_turn)

    @property
    def is_new(self):
        return (datetime.datetime.now() - self.created_at).total_seconds() < c.PLACE_NEW_PLACE_LIVETIME

    @property
    def new_for(self):
        return self.created_at + datetime.timedelta(seconds=c.PLACE_NEW_PLACE_LIVETIME)

    @property
    def description_html(self): return utils_bbcode.render(self.description)

    def linguistics_restrictions(self):
        restrictions = [linguistics_restrictions.get(self.race),
                        linguistics_restrictions.get(self.habit_honor.interval),
                        linguistics_restrictions.get(self.habit_honor.interval),
                        linguistics_restrictions.get(self.terrain)]

        restrictions.extend(self._modifier.linguistics_restrictions())

        return tuple(restrictions)

    @property
    def depends_from_all_heroes(self):
        return self.is_frontier

    def update_heroes_habits(self):
        habits_values = heroes_preferences.HeroPreferences.count_habit_values(self, all=self.depends_from_all_heroes)

        self.habit_honor_positive = habits_values[0][0]
        self.habit_honor_negative = habits_values[0][1]
        self.habit_peacefulness_positive = habits_values[1][0]
        self.habit_peacefulness_negative = habits_values[1][1]

    @classmethod
    def _habit_change_speed(cls, current_value, positive, negative):
        positive = abs(positive)
        negative = abs(negative)

        if positive < negative:
            if positive < 0.0001:
                result = -c.PLACE_HABITS_CHANGE_SPEED_MAXIMUM
            else:
                result = -min(c.PLACE_HABITS_CHANGE_SPEED_MAXIMUM, negative / positive)
        elif positive > negative:
            if negative < 0.0001:
                result = c.PLACE_HABITS_CHANGE_SPEED_MAXIMUM
            else:
                result = min(c.PLACE_HABITS_CHANGE_SPEED_MAXIMUM, positive / negative)
        else:
            result = 0

        return result - c.PLACE_HABITS_CHANGE_SPEED_MAXIMUM_PENALTY * (float(current_value) / c.HABITS_BORDER)

    @property
    def habit_honor_change_speed(self):
        return self._habit_change_speed(self.habit_honor.raw_value, self.habit_honor_positive, self.habit_honor_negative)

    @property
    def habit_peacefulness_change_speed(self):
        return self._habit_change_speed(self.habit_peacefulness.raw_value, self.habit_peacefulness_positive, self.habit_peacefulness_negative)

    def sync_habits(self):
        self.habit_honor.change(self.habit_honor_change_speed)
        self.habit_peacefulness.change(self.habit_peacefulness_change_speed)

    def can_habit_event(self):
        return random.uniform(0, 1) < c.PLACE_HABITS_EVENT_PROBABILITY

    @property
    def url(self):
        return dext_urls.url('game:places:show', self.id)

    def name_from(self, with_url=True):
        if with_url:
            return '<a href="%s" target="_blank">%s</a>' % (self.url, self.name)

        return self.name

    @property
    def persons(self):
        return sorted((person for person in persons_storage.persons.all() if person.place_id == self.id),
                      key=lambda p: p.created_at_turn)  # fix persons order

    @property
    def persons_by_power(self):
        return sorted((person for person in persons_storage.persons.all() if person.place_id == self.id),
                      key=lambda p: politic_power_storage.persons.total_power_fraction(p.id),
                      reverse=True)  # fix persons order

    def mark_as_updated(self): self.updated_at_turn = game_turn.number()

    @property
    def terrains(self):
        map_info = map_storage.map_info.item
        terrains = set()
        for cell in self.nearest_cells:
            terrains.add(map_info.terrain[cell[1]][cell[0]])
        return terrains

    @property
    def terrain(self):
        map_info = map_storage.map_info.item
        return map_info.terrain[self.y][self.x]

    def shift(self, dx, dy):
        self.x += dx
        self.y += dy

    def sync_race(self):
        self.races.update(persons=self.persons)

    def is_modifier_active(self):
        return getattr(self.attrs, 'MODIFIER_{}'.format(self.modifier.name).lower(), 0) >= c.PLACE_TYPE_ENOUGH_BORDER

    def is_wrong_race(self):
        return self.races.dominant_race and self.race != self.races.dominant_race

    def _effects_generator(self):
        yield game_effects.Effect(name='город', attribute=relations.ATTRIBUTE.TAX, value=0.0)

        yield game_effects.Effect(name='город', attribute=relations.ATTRIBUTE.STABILITY, value=1.0)

        if len(self.persons) > c.PLACE_MAX_PERSONS:
            yield game_effects.Effect(name='избыток Мастеров',
                                      attribute=relations.ATTRIBUTE.STABILITY,
                                      value=c.PLACE_STABILITY_PENALTY_FOR_MASTER * (len(self.persons) - c.PLACE_MAX_PERSONS))

        if self.is_wrong_race():
            dominant_race_power = self.races.get_race_percents(self.races.dominant_race)
            current_race_power = self.races.get_race_percents(self.race)
            yield game_effects.Effect(name='расовая дискриминация',
                                      attribute=relations.ATTRIBUTE.STABILITY,
                                      value=c.PLACE_STABILITY_PENALTY_FOR_RACES * (dominant_race_power - current_race_power))

        yield game_effects.Effect(name='город', attribute=relations.ATTRIBUTE.STABILITY_RENEWING_SPEED, value=c.PLACE_STABILITY_RECOVER_SPEED)

        # politic radius
        yield game_effects.Effect(name='размер города', attribute=relations.ATTRIBUTE.POLITIC_RADIUS, value=self.attrs.size * 0.625)
        yield game_effects.Effect(name='культура', attribute=relations.ATTRIBUTE.POLITIC_RADIUS, value=self.attrs.size * self.attrs.culture * 0.625)

        # terrain radius
        yield game_effects.Effect(name='размер города', attribute=relations.ATTRIBUTE.TERRAIN_RADIUS, value=self.attrs.size * 0.5)
        yield game_effects.Effect(name='культура', attribute=relations.ATTRIBUTE.TERRAIN_RADIUS, value=self.attrs.size * self.attrs.culture * 0.5)

        for effect in self.effects.effects:
            yield effect

        if self.is_modifier_active():
            for effect in self._modifier.effects:
                yield effect

        elif not self.modifier.is_NONE:
            modifier_points = getattr(self.attrs, 'MODIFIER_{}'.format(self.modifier.name).lower(), 0)
            yield game_effects.Effect(name='Несоответствие специализации',
                                      attribute=relations.ATTRIBUTE.STABILITY,
                                      value=c.PLACE_STABILITY_PENALTY_FOR_SPECIALIZATION * (c.PLACE_TYPE_ENOUGH_BORDER - modifier_points) / c.PLACE_TYPE_ENOUGH_BORDER)

        for exchange in storage.resource_exchanges.get_exchanges_for_place(self):
            resource_1, resource_2, place_2 = exchange.get_resources_for_place(self)
            if resource_1.parameter is not None:
                yield game_effects.Effect(name=place_2.name if place_2 is not None else resource_2.text,
                                          attribute=resource_1.parameter,
                                          value=-resource_1.amount * resource_1.direction)
            if resource_2.parameter is not None:
                yield game_effects.Effect(name=place_2.name if place_2 is not None else resource_1.text,
                                          attribute=resource_2.parameter,
                                          value=resource_2.amount * resource_2.direction)

        # economic
        yield game_effects.Effect(name='город', attribute=relations.ATTRIBUTE.AREA, value=len(self.nearest_cells))

        # мы ожидаем, что радиус владений города сравним с его размером и домножаем на поправочный коэфициент
        area_size_equivalent = ((math.sqrt(self.attrs.area) - 1) / 2) * 2

        if self.is_frontier:
            area_size_equivalent /= 2

        yield game_effects.Effect(name='экономика', attribute=relations.ATTRIBUTE.PRODUCTION, value=0.66 * self.attrs.power_economic * c.PLACE_GOODS_BONUS)
        yield game_effects.Effect(name='владения', attribute=relations.ATTRIBUTE.PRODUCTION, value=0.34 * area_size_equivalent * c.PLACE_GOODS_BONUS)

        yield game_effects.Effect(name='потребление', attribute=relations.ATTRIBUTE.PRODUCTION, value=-self.attrs.size * c.PLACE_GOODS_BONUS)
        yield game_effects.Effect(name='стабильность', attribute=relations.ATTRIBUTE.PRODUCTION, value=(1.0 - self.attrs.stability) * c.PLACE_STABILITY_MAX_PRODUCTION_PENALTY)

        if self.attrs.get_next_keepers_goods_spend_amount():
            yield game_effects.Effect(name='дары Хранителей', attribute=relations.ATTRIBUTE.PRODUCTION, value=self.attrs.get_next_keepers_goods_spend_amount())

        # safety
        yield game_effects.Effect(name='город', attribute=relations.ATTRIBUTE.SAFETY, value=1.0)
        yield game_effects.Effect(name='монстры', attribute=relations.ATTRIBUTE.SAFETY, value=-c.BATTLES_PER_TURN)
        yield game_effects.Effect(name='стабильность', attribute=relations.ATTRIBUTE.SAFETY, value=(1.0 - self.attrs.stability) * c.PLACE_STABILITY_MAX_SAFETY_PENALTY)

        if self.is_frontier:
            yield game_effects.Effect(name='дикие земли', attribute=relations.ATTRIBUTE.SAFETY, value=-c.WHILD_BATTLES_PER_TURN_BONUS)

        # transport
        yield game_effects.Effect(name='дороги', attribute=relations.ATTRIBUTE.TRANSPORT, value=1.0)
        yield game_effects.Effect(name='трафик', attribute=relations.ATTRIBUTE.TRANSPORT, value=-c.TRANSPORT_FROM_PLACE_SIZE_PENALTY * self.attrs.size)

        if self.is_frontier:
            yield game_effects.Effect(name='бездорожье', attribute=relations.ATTRIBUTE.TRANSPORT, value=-c.WHILD_TRANSPORT_PENALTY)

        yield game_effects.Effect(name='стабильность', attribute=relations.ATTRIBUTE.TRANSPORT, value=(1.0 - self.attrs.stability) * c.PLACE_STABILITY_MAX_TRANSPORT_PENALTY)

        # freedom
        yield game_effects.Effect(name='город', attribute=relations.ATTRIBUTE.FREEDOM, value=1.0)
        yield game_effects.Effect(name='стабильность', attribute=relations.ATTRIBUTE.FREEDOM, value=(1.0 - self.attrs.stability) * c.PLACE_STABILITY_MAX_FREEDOM_PENALTY)

        # culture
        yield game_effects.Effect(name='город', attribute=relations.ATTRIBUTE.CULTURE, value=1.0)
        yield game_effects.Effect(name='стабильность', attribute=relations.ATTRIBUTE.CULTURE, value=(1.0 - self.attrs.stability) * c.PLACE_STABILITY_MAX_CULTURE_PENALTY)

        for person in self.persons:
            for effect in person.place_effects():
                yield effect

    def effects_generator(self, order):
        # TODO: do something with postchecks
        safety = 0
        transport = 0
        stability = 0
        culture = 0
        freedom = 0

        for effect in self._effects_generator():
            if effect.attribute.order != order:
                continue
            if effect.attribute.is_SAFETY:
                safety += effect.value
            if effect.attribute.is_TRANSPORT:
                transport += effect.value
            if effect.attribute.is_STABILITY:
                stability += effect.value
            if effect.attribute.is_CULTURE:
                culture += effect.value
            if effect.attribute.is_FREEDOM:
                freedom += effect.value
            yield effect

        if relations.ATTRIBUTE.SAFETY.order == order:
            if safety < c.PLACE_MIN_SAFETY:
                yield game_effects.Effect(name='Серый Орден', attribute=relations.ATTRIBUTE.SAFETY, value=c.PLACE_MIN_SAFETY - safety)
            if safety > 1:
                yield game_effects.Effect(name='демоны', attribute=relations.ATTRIBUTE.SAFETY, value=1 - safety)

        if relations.ATTRIBUTE.TRANSPORT.order == order:
            if transport < c.PLACE_MIN_TRANSPORT:
                yield game_effects.Effect(name='Серый Орден', attribute=relations.ATTRIBUTE.TRANSPORT, value=c.PLACE_MIN_TRANSPORT - transport)

        if relations.ATTRIBUTE.STABILITY.order == order:
            if stability < c.PLACE_MIN_STABILITY:
                yield game_effects.Effect(name='Серый Орден', attribute=relations.ATTRIBUTE.STABILITY, value=c.PLACE_MIN_STABILITY - stability)
            if stability > 1:
                yield game_effects.Effect(name='демоны', attribute=relations.ATTRIBUTE.STABILITY, value=1 - stability)

        if relations.ATTRIBUTE.CULTURE.order == order:
            if culture < c.PLACE_MIN_CULTURE:
                yield game_effects.Effect(name='бродячие артисты', attribute=relations.ATTRIBUTE.CULTURE, value=c.PLACE_MIN_CULTURE - culture)

        if relations.ATTRIBUTE.FREEDOM.order == order:
            if freedom < c.PLACE_MIN_FREEDOM:
                yield game_effects.Effect(name='Пять звёзд', attribute=relations.ATTRIBUTE.FREEDOM, value=c.PLACE_MIN_FREEDOM - freedom)

    def effects_for_attribute(self, attribute):
        for effect in self.effects_generator(attribute.order):
            if effect.attribute == attribute:
                yield effect

    def tooltip_effects_for_attribute(self, attribute):
        effects = [(effect.name, effect.value) for effect in self.effects_for_attribute(attribute)]
        effects.sort(key=lambda x: x[1], reverse=True)
        return effects

    def attribute_ui_info(self, attribute_name):
        attribute = getattr(relations.ATTRIBUTE, attribute_name.upper())
        return (attribute, getattr(self.attrs, attribute_name.lower()))

    def all_effects(self):
        for order in relations.ATTRIBUTE.EFFECTS_ORDER:
            for effect in self.effects_generator(order):
                yield effect

    def refresh_attributes(self):
        self.attrs.reset()

        for effect in self.all_effects():
            effect.apply_to(self.attrs)

        self.attrs.sync()

    def effects_update_step(self):
        stability_effects = [effect for effect in self.effects.effects if effect.attribute.is_STABILITY]

        if stability_effects:
            speed = self.attrs.stability_renewing_speed

            divider = 2
            speed_sum = 0

            for effect in stability_effects:
                delta = 0

                if divider < 1000:
                    delta = speed / divider

                effect.delta = delta
                speed_sum += delta

                divider *= 2

            stability_effects[0].delta += (speed - speed_sum)

        self.effects.update_step()

    def set_modifier(self, modifier):
        self._modifier = modifier
        self.refresh_attributes()

    @property
    def modifier(self):
        return self._modifier

    def get_same_places(self):
        return [place for place in storage.places.all() if self.is_frontier == place.is_frontier]

    def map_info(self):
        return {'id': self.id,
                'pos': {'x': self.x, 'y': self.y},
                'race': self.race.value,
                'name': self.name,
                'size': self.attrs.size}

    def meta_object(self):
        return meta_relations.Place.create_from_object(self)


class Building(game_names.ManageNameMixin2):
    __slots__ = ('id',
                 'x',
                 'y',
                 'type',
                 'integrity',
                 'created_at_turn',
                 'state',
                 'utg_name',
                 'person_id',

                 # mames mixin
                 '_utg_name_form__lazy',
                 '_name__lazy')

    def __init__(self, id, x, y, type, integrity, created_at_turn, state, utg_name, person_id):
        self.id = id
        self.x = x
        self.y = y
        self.type = type
        self.integrity = integrity
        self.created_at_turn = created_at_turn
        self.state = state
        self.utg_name = utg_name
        self.person_id = person_id

    def shift(self, dx, dy):
        self.x += dx
        self.y += dy

    @property
    def person(self):
        return persons_storage.persons[self.person_id]

    @property
    def place(self):
        return self.person.place

    @property
    def logical_integrity(self):
        return min(self.integrity, 1.0)

    @property
    def terrain_change_power(self):
        # +1 to prevent power == 0
        power = self.place.attrs.terrain_radius * self.logical_integrity * c.BUILDING_TERRAIN_POWER_MULTIPLIER + 1
        return int(round(power))

    def amortization_delta(self, turns_number):
        buildings_number = sum(storage.buildings.get_by_person_id(person.id) is not None
                               for person in self.place.persons)

        per_one_building = float(turns_number) / c.TURNS_IN_HOUR * c.BUILDING_AMORTIZATION_SPEED * self.person.attrs.building_amortization_speed
        return per_one_building * c.BUILDING_AMORTIZATION_MODIFIER**(buildings_number - 1)

    @property
    def amortization_in_day(self):
        return self.amortization_delta(c.TURNS_IN_HOUR * 24)

    def amortize(self, turns_number):
        self.integrity -= self.amortization_delta(turns_number)
        if self.integrity <= 0.0001:
            self.integrity = 0

    @property
    def repair_delta(self): return float(c.BUILDING_WORKERS_ENERGY_COST) / c.BUILDING_FULL_REPAIR_ENERGY_COST

    def repair(self, delta):
        self.integrity += delta

    @property
    def terrain(self):
        map_info = map_storage.map_info.item
        return map_info.terrain[self.y][self.x]

    def linguistics_restrictions(self):
        return [linguistics_restrictions.get(self.terrain.value)]

    def map_info(self):
        return {'id': self.id,
                'pos': {'x': self.x, 'y': self.y},
                'person': self.person.id,
                'place': self.place.id,
                'type': self.type.value}


class Popularity:
    __slots__ = ('_places_fame', )

    def __init__(self, places_fame):
        self._places_fame = [(place_id, fame) for place_id, fame in places_fame.items()]
        self._places_fame.sort(key=lambda x: x[1], reverse=True)

    def places_rating(self):
        return self._places_fame

    def get_allowed_places_ids(self, number):
        number -= 1

        if number >= len(self._places_fame):
            number = len(self._places_fame) - 1

        if number < 0:
            return set()

        min_fame = self._places_fame[number][1]

        return {place_id for place_id, fame in self._places_fame if fame >= min_fame}

    def has_popularity(self):
        return bool(self._places_fame)

    def get_fame(self, place_id, default=0):
        for checked_place_id, fame in self._places_fame:
            if checked_place_id == place_id:
                return fame

        return default
