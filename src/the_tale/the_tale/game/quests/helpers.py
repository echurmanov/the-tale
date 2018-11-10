
import smart_imports

smart_imports.all()


def setup_quest(hero):
    hero_info = logic.create_hero_info(hero)
    knowledge_base = logic.create_random_quest_for_hero(hero_info, mock.Mock())
    logic.setup_quest_for_hero(hero, knowledge_base.serialize())


class QuestTestsMixin(object):

    def turn_to_quest(self, storage, hero_id):

        hero = storage.heroes[hero_id]

        while hero.actions.current_action.TYPE != actions_prototypes.ActionQuestPrototype.TYPE or not self.hero.quests.has_quests:
            storage.process_turn()
            game_turn.increment()

        storage.save_changed_data()

        return hero.quests.current_quest


class QuestWith2ChoicePoints(questgen_quests_base_quest.BaseQuest):
    TYPE = 'quest_with_2_choice_points'
    TAGS = ('normal', 'can_start', 'can_continue')

    @classmethod
    def construct_from_place(cls, nesting, selector, start_place):
        initiator = selector.new_person(first_initiator=(nesting == 0), restrict_places=False, places=(start_place.uid, ))
        receiver = selector.new_person(first_initiator=False)

        initiator_position = selector.place_for(objects=(initiator.uid,))
        receiver_position = selector.place_for(objects=(receiver.uid,))

        ns = selector._kb.get_next_ns()

        start = questgen_facts.Start(uid=ns + 'start', type=cls.TYPE, nesting=nesting)

        choice_1 = questgen_facts.Choice(uid=ns + 'choice_1')

        choice_2 = questgen_facts.Choice(uid=ns + 'choice_2')

        finish_1_1 = questgen_facts.Finish(uid=ns + 'finish_1_1',
                                           start=start.uid,
                                           results={initiator.uid: questgen_quests_base_quest.RESULTS.SUCCESSED,
                                                    initiator_position.uid: questgen_quests_base_quest.RESULTS.FAILED,
                                                    receiver.uid: questgen_quests_base_quest.RESULTS.SUCCESSED,
                                                    receiver_position.uid: questgen_quests_base_quest.RESULTS.SUCCESSED},
                                           nesting=nesting)
        finish_1_2 = questgen_facts.Finish(uid=ns + 'finish_1_2',
                                           start=start.uid,
                                           results={initiator.uid: questgen_quests_base_quest.RESULTS.FAILED,
                                                    initiator_position.uid: questgen_quests_base_quest.RESULTS.FAILED,
                                                    receiver.uid: questgen_quests_base_quest.RESULTS.FAILED,
                                                    receiver_position.uid: questgen_quests_base_quest.RESULTS.FAILED},
                                           nesting=nesting)
        finish_2 = questgen_facts.Finish(uid=ns + 'finish_2',
                                         start=start.uid,
                                         results={initiator.uid: questgen_quests_base_quest.RESULTS.SUCCESSED,
                                                  initiator_position.uid: questgen_quests_base_quest.RESULTS.SUCCESSED,
                                                  receiver.uid: questgen_quests_base_quest.RESULTS.FAILED,
                                                  receiver_position.uid: questgen_quests_base_quest.RESULTS.FAILED},
                                         nesting=nesting)

        participants = [questgen_facts.QuestParticipant(start=start.uid, participant=initiator.uid, role=questgen_quests_base_quest.ROLES.INITIATOR),
                        questgen_facts.QuestParticipant(start=start.uid, participant=initiator_position.uid, role=questgen_quests_base_quest.ROLES.INITIATOR_POSITION),
                        questgen_facts.QuestParticipant(start=start.uid, participant=receiver.uid, role=questgen_quests_base_quest.ROLES.RECEIVER),
                        questgen_facts.QuestParticipant(start=start.uid, participant=receiver_position.uid, role=questgen_quests_base_quest.ROLES.RECEIVER_POSITION)]

        quest_facts = [start,
                       choice_1,
                       choice_2,
                       finish_1_1,
                       finish_1_2,
                       finish_2,

                       questgen_facts.Jump(state_from=start.uid, state_to=choice_1.uid),

                       questgen_facts.Option(state_from=choice_1.uid, state_to=finish_2.uid, type='opt_1', markers=()),
                       questgen_facts.Option(state_from=choice_1.uid, state_to=choice_2.uid, type='opt_2', markers=()),
                       questgen_facts.Option(state_from=choice_2.uid, state_to=finish_1_1.uid, type='opt_2_1', markers=()),
                       questgen_facts.Option(state_from=choice_2.uid, state_to=finish_1_2.uid, type='opt_2_2', markers=())
                       ]

        return participants + quest_facts


class FakeWriter(quests_writers.Writer):

    def __init__(self, fake_uid, **kwargs):
        super(FakeWriter, self).__init__(**kwargs)
        self._counter = 0
        self._fake_uid = fake_uid

    def get_message(self, type_, **kwargs):
        self._counter += 1
        return '%s_%s_%d' % (self._fake_uid, type_, self._counter)
