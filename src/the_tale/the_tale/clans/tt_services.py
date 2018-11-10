
import smart_imports

smart_imports.all()


class ClansChronicleClient(tt_api_events_log.Client):

    def cmd_add_event(self, clan, event, tags, **kwargs):
        tags = set(tags)
        tags.add(clan.meta_object().tag)
        tags.add(event.meta_object().tag)
        return super().cmd_add_event(tags=tags, **kwargs)

    def cmd_get_events(self, clan, tags, **kwargs):
        tags = set(tags)
        tags.add(clan.meta_object().tag)
        return super().cmd_get_events(tags=tags, **kwargs)

    def cmd_get_last_events(self, clan, tags, **kwargs):
        tags = set(tags)
        tags.add(clan.meta_object().tag)
        return super().cmd_get_last_events(tags=tags, **kwargs)


chronicle = ClansChronicleClient(entry_point=conf.settings.TT_CHRONICLE_ENTRY_POINT)
