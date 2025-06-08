from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView, View
from django.views.generic.edit import FormMixin
from django.db.models import Count, Q
from .models import Petition, PetitionStatus, PetitionCategory, Signature, PendingSignature, Comment
from .forms import PetitionForm, SignatureForm, CommentForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.core.mail import send_mail
from django.urls import reverse


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



class PetitionListView(LoginRequiredMixin, ListView):
    model = Petition
    template_name = 'petitions/petition_list.html'
    context_object_name = 'petitions'
    paginate_by = 6

    def get_queryset(self):
        qs = Petition.objects.filter(status=PetitionStatus.PUBLISHED, is_active=True)
        # Se non sei admin, vedi solo le tue petizioni
        if not self.request.user.is_superuser:
            qs = qs.filter(created_by=self.request.user)

        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))

        category = self.request.GET.get('category')
        if category:
            qs = qs.filter(category__name__iexact=category)

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



class PetitionDetailView(FormMixin, DetailView):
    model = Petition
    template_name = 'petitions/petition_detail.html'
    context_object_name = 'petition'
    form_class = CommentForm

    def get_queryset(self):
        return Petition.objects.all()

    def get_success_url(self):
        return reverse('petitions:petition_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.get_form()
        context['comments'] = self.object.comments.select_related('user').order_by('-created_at')
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid() and request.user.is_authenticated:
            comment = form.save(commit=False)
            comment.petition = self.object
            comment.user = request.user
            comment.save()
            return redirect(self.get_success_url())
        else:
            return self.form_invalid(form)


class PetitionCreateView(LoginRequiredMixin, CreateView):
    model = Petition
    form_class = PetitionForm
    template_name = 'petitions/petition_form.html'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('petitions:petition_detail', kwargs={'pk': self.object.pk})





class PetitionUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Petition
    form_class = PetitionForm
    template_name = 'petitions/petition_form.html'

    def test_func(self):
        petition = self.get_object()
        # Controlla se è admin o autore della petizione
        return self.request.user.is_superuser or petition.created_by == self.request.user

    def handle_no_permission(self):
        # Se l'utente non ha permessi, restituisci 403
        if self.request.user.is_authenticated:
            return HttpResponseForbidden("Non hai i permessi per modificare questa petizione.")
        else:
            # Se non è autenticato, usa il comportamento standard (redirect login)
            return super().handle_no_permission()

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

class PetitionSearchView(ListView):
    model = Petition
    template_name = 'petitions/petition_search.html'
    context_object_name = 'results'
    paginate_by = 6

    def get_queryset(self):
        query = self.request.GET.get('q', '')
        qs = Petition.objects.filter(status=PetitionStatus.PUBLISHED, is_active=True)
        if query:
            qs = qs.filter(
                Q(title__icontains=query) | Q(description__icontains=query)
            ).order_by('-created_at')
        else:
            qs = qs.none()
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        context['categories'] = PetitionCategory.objects.all()
        return context

class RequestSignatureView(FormView):
    form_class = SignatureForm
    template_name = 'petitions/request_signature.html'

    def dispatch(self, request, *args, **kwargs):
        self.petition = get_object_or_404(Petition, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['petition'] = self.petition
        return context

    def form_valid(self, form):
        email = form.cleaned_data['email']
        petition = self.petition

        if Signature.objects.filter(petition=petition, email=email).exists():
            messages.info(self.request, "Hai già firmato questa petizione con questa email.")
        else:
            pending = PendingSignature.objects.create(petition=petition, email=email)
            confirm_url = self.request.build_absolute_uri(
                reverse('petitions:confirm_signature', kwargs={'token': pending.token})
            )
            send_mail(
                subject='Conferma la tua firma',
                message=f'Clicca per confermare la firma:\n{confirm_url}',
                from_email='noreply@tuosito.it',
                recipient_list=[email],
            )
            messages.success(self.request, "Ti abbiamo inviato un'email per confermare la firma.")
        return redirect('petitions:petition_detail', pk=petition.pk)


class ConfirmSignatureView(View):
    def get(self, request, token):
        try:
            pending = PendingSignature.objects.get(token=token, confirmed=False)
        except PendingSignature.DoesNotExist:
            messages.error(request, "Link non valido o firma già confermata.")
            return redirect('petitions:home')  # o 'home' se è fuori dal namespace

        Signature.objects.create(petition=pending.petition, email=pending.email)
        pending.confirmed = True
        pending.save()

        messages.success(request, "La tua firma è stata confermata!")
        return redirect('petitions:petition_detail', pk=pending.petition.pk)
