from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError as RESTValidationError
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import URLValidator
from tasks import run
from . import IMPORT_TASK_NAME


class ImportView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *wargs, **kwargs):
        url = request.data.get('url')

        if not url:
            raise RESTValidationError(
                {
                    'url': 'Specify a value.'
                }
            )

        validate_url = URLValidator()

        try:
            validate_url(url)
        except DjangoValidationError:
            raise RESTValidationError(
                {
                    'url': 'Specify a valid value.'
                }
            )

        job = run(
            IMPORT_TASK_NAME,
            url=url,
            api_access_key=str(request.auth)
        )

        return Response(
            {
                'url': url,
                'job': {
                    'id': job.id,
                    'status': job.status
                }
            },
            status=201
        )
