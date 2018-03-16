import django.dispatch


job_finished = django.dispatch.Signal(
    providing_args=['func', 'args', 'kwargs', 'data']
)

job_progress = django.dispatch.Signal(
    providing_args=['func', 'args', 'kwargs', 'data']
)

job_failed = django.dispatch.Signal(
    providing_args=['func', 'args', 'kwargs', 'data']
)
