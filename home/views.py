from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

from .models import Road, Image, Issue, IssueDetail

# Create your views here.
def index(request):
    if request.user.is_authenticated:
        return redirect('home:dashboard')
    return render(request, 'home/index.html')

@login_required
def dashboard(request):
    if request.user.role == 'min':
        state = request.GET.get('state', None)
        district = request.GET.get('district', None)
        block = request.GET.get('block', None)

        roads = Road.objects.all()
        states = roads.values_list('state', flat=True).distinct().order_by('state')

        if state and district and block:
            roads = roads.filter(state=state)
            districts = roads.values_list('district', flat=True).distinct().order_by('district')
            roads = roads.filter(district=district)
            blocks = roads.values_list('block', flat=True).distinct().order_by('block')
            roads = roads.filter(block=block)
            if roads.exists():
                context = {
                    'states': states,
                    'districts': districts,
                    'blocks': blocks,
                    'roads': roads,

                    'selected_state': state,
                    'selected_district': district,
                    'selected_block': block,
                }
                return render(request, 'home/dashboard.html', context)
            else:
                return redirect('home:dashboard')

        context = {
            'states': states,
        }
        return render(request, 'home/dashboard.html', context)
    else:
        roads = request.user.assigned_roads.all()
        context = {
            'roads': roads,
        }
        return render(request, 'home/dashboard.html', context)
    

@login_required
def road_details(request, slug):
    if request.user.role == 'min':
        road = get_object_or_404(Road, slug=slug)
    else:
        road = get_object_or_404(Road, slug=slug, assigned_to=request.user)
    context = {
        'road': road,
    }
    return render(request, 'home/road_details.html', context)

def ajax_state_changed(request):
    state = request.GET.get('state', None)
    data = {}

    if state:
        roads = Road.objects.filter(state=state)
        districts = roads.values_list('district', flat=True).distinct().order_by('district')

        for district in districts:
            data[district] = district

    return JsonResponse(data)

def ajax_district_changed(request):
    state = request.GET.get('state', None)
    district = request.GET.get('district', None)
    data = {}

    if state and district:
        roads = Road.objects.filter(state=state, district=district)
        blocks = roads.values_list('block', flat=True).distinct().order_by('block')

        for block in blocks:
            data[block] = block

    return JsonResponse(data)