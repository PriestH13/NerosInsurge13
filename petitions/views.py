from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.db.models import Count, Q
from .models import Petition, PetitionStatus, PetitionCategory
from .forms import PetitionForm
from django.contrib.auth.mixins import LoginRequiredMixin

class HomeView(ListView):
    model = Petition
    template_name = 'base.html'
    context_object_name = 'petitions'
    paginate_by = 6

    def get_queryset(self):
        return Petition.objects.filter(status=PetitionStatus.PUBLISHED, is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = PetitionCategory.objects.all()

        context['featured_petitions'] = Petition.objects.filter(
            status=PetitionStatus.PUBLISHED,
            is_active=True
        ).order_by('-created_at')[:5]

        return context



class PetitionListView(ListView):
    model = Petition
    template_name = 'petitions/petition_list.html'
    context_object_name = 'petitions'
    paginate_by = 6

    def get_queryset(self):
        qs = Petition.objects.filter(status=PetitionStatus.PUBLISHED, is_active=True)

        # Filtro ricerca
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))

        # Filtro categoria
        category = self.request.GET.get('category')
        if category:
            qs = qs.filter(category__name__iexact=category)

        # Ordinamento
        order = self.request.GET.get('order')
        if order == 'recenti':
            qs = qs.order_by('-created_at')
        elif order == 'popolari':
            qs = qs.annotate(num_signatures=Count('signatures')).order_by('-num_signatures')
        else:
            qs = qs.order_by('-created_at')

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = PetitionCategory.objects.all()
        return context


class PetitionDetailView(DetailView):
    model = Petition
    template_name = 'petitions/petition_detail.html'
    context_object_name = 'petition'

    def get_queryset(self):
        return Petition.objects.all()


class PetitionCreateView(LoginRequiredMixin, CreateView):
    model = Petition
    form_class = PetitionForm
    template_name = 'petitions/petition_form.html'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('petitions:petition_detail', kwargs={'pk': self.object.pk})





class PetitionUpdateView(LoginRequiredMixin, UpdateView):
    model = Petition
    form_class = PetitionForm
    template_name = 'petitions/petition_form.html'

    def get_queryset(self):
        # Solo l'autore o admin può aggiornare
        if self.request.user.is_superuser:
            return Petition.objects.all()
        return Petition.objects.filter(created_by=self.request.user)

    def get_success_url(self):
        return reverse_lazy('petitions:petition_detail', kwargs={'pk': self.object.pk})


class PetitionDeleteView(LoginRequiredMixin, DeleteView):
    model = Petition
    template_name = 'petitions/petition_confirm_delete.html'
    success_url = reverse_lazy('petitions:petition_list')

    def get_queryset(self):
        # Solo l'autore o admin può cancellare
        if self.request.user.is_superuser:
            return Petition.objects.all()
        return Petition.objects.filter(created_by=self.request.user)

