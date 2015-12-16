from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.conf import settings

from trackingapp.importer import ingest
from trackingapp.models import Card, Expansion, Source, SourceExpansion


def home(request, template_name="home.html"):
    attributes = {}
    attributes['sources'] = Source.objects.all()
    return render(request, template_name, attributes)


def source_details(request, source_id, template_name="source_details.html"):
    attributes = {}
    attributes['source'] = Source.objects.get(pk=source_id)
    attributes['source_expansions'] = SourceExpansion.objects.filter(source=attributes['source'])
    return render(request, template_name, attributes)


def expansion_details(request, expansion_id, template_name="expansion_details.html"):
    attributes = {}
    attributes['expansion'] = Expansion.objects.get(pk=expansion_id)
    attributes['cards'] = Card.objects.filter(expansion=attributes['expansion'])
    return render(request, template_name, attributes)


@csrf_exempt
def api(request, api_key, template_name="api.html"):
    attributes = {}

    if settings.API_KEY != api_key:
        attributes['error'] = 'Incorect api key'
        return render(request, template_name, attributes)

    # import_data = request.GET.get('d')
    # if import_data:
    #     ingest(import_data)

    print request.POST
    import_data = request.POST.get('d')
    if import_data:
        ingest(import_data)

    return redirect("/")