
import smart_imports

smart_imports.all()


@utils_jinja2.jinjaglobal
def sorted_recipients(recipients_ids, accounts):
    recipients = [accounts[recipient_id] for recipient_id in recipients_ids]
    recipients.sort(key=lambda account: account.nick_verbose)
    return recipients


@utils_jinja2.jinjaglobal
def new_messages_number_url():
    return utils_jinja2.Markup(logic.new_messages_number_url())


@utils_jinja2.jinjaglobal
def personal_messages_settings():
    return conf.settings
