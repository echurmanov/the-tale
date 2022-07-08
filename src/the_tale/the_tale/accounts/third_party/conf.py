
import smart_imports

smart_imports.all()


settings = utils_app_settings.app_settings('THIRD_PARTY',
                                           ACCESS_TOKEN_HEADER_KEY='third-party-token',
                                           ACCESS_TOKEN_SESSION_KEY='third-party-access-token',
                                           ACCESS_TOKEN_CACHE_KEY='tpat-token-%s',
                                           ACCESS_TOKEN_CACHE_TIMEOUT=10 * 60,
                                           UNPROCESSED_ACCESS_TOKEN_LIVE_TIME=10  # minutes
                                           )
