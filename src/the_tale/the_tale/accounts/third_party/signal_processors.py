
import smart_imports

smart_imports.all()


@django_dispatch.receiver(accounts_signals.on_before_logout, dispatch_uid='third_party__on_before_logout')
def on_before_logout(sender, **kwargs):
    from the_tale.accounts.third_party import conf
    from the_tale.accounts.third_party import prototypes

    request = kwargs['request']

    # remove third party access token on logout IF IT HAS BEEN ACCEPTED
    if conf.settings.ACCESS_TOKEN_SESSION_KEY in request.session:
        token = prototypes.AccessTokenPrototype.get_by_uid(request.session[conf.settings.ACCESS_TOKEN_SESSION_KEY])
        if token is not None and token.state.is_ACCEPTED:
            token.remove()
