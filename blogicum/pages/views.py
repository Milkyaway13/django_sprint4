from django.http import Http404
from django.views.generic import TemplateView


class AboutView(TemplateView):
    template_name = 'pages/about.html'

    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except Http404:
            return self.handle_404()

    def handle_404(self):
        return self.render_to_response(template_name='pages/404.html')

    def handle_403_csrf(self):
        return self.render_to_response(template_name='pages/403csrf.html')

    def handle_500(self):
        return self.render_to_response(template_name='pages/500.html')


class RulesView(TemplateView):
    template_name = 'pages/rules.html'

    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except Http404:
            return self.handle_404()

    def handle_404(self):
        return self.render_to_response(template_name='pages/404.html')

    def handle_403_csrf(self):
        return self.render_to_response(template_name='pages/403csrf.html')

    def handle_500(self):
        return self.render_to_response(template_name='pages/500.html')
