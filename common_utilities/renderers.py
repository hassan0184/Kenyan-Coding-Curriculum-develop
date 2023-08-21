from rest_framework.renderers import JSONRenderer
from .response_template import get_response_template


class CustomRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        if data is not None:
            if not ('success' in data):
                response_template = get_response_template()
                response_template['data'] = data
                data = response_template
        else:
            response_template = get_response_template()
            response_template['data'] = ''
            data = response_template
        return super().render(data, accepted_media_type, renderer_context)
