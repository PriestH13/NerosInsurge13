from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView, View, TemplateView
from django.views.generic.edit import FormMixin
from django.db.models import Count, Q
from .models import Petition, PetitionStatus, PetitionCategory, Signature, PendingSignature, PetitionVote, Notification, PetitionView, ModerationAction
from .forms import PetitionForm, SignatureForm, CommentForm, ReportForm, ModerationActionForm, Tag
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib import messages
from django.core.mail import send_mail
from django.urls import reverse
from .utils import get_client_ip
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from .utils import log_action
from django.db.models import Count


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

        # Petizioni secondo nr firme
        context['featured_petitions'] = Petition.objects.filter(
            status=PetitionStatus.PUBLISHED,
            is_active=True
        ).annotate(num_signatures=Count('signatures')).order_by('-num_signatures')[:5]

        return context



class AboutView(TemplateView):
    template_name = "other/about.html"

class TermsView(TemplateView):
    template_name = "other/terms.html"

class PrivacyView(TemplateView):
    template_name = "other/privacy.html"


class PetitionListView(LoginRequiredMixin, ListView):
    model = Petition
    template_name = 'petitions/petition_list.html'
    context_object_name = 'petitions'
    paginate_by = 6

    def get_queryset(self):
        qs = Petition.objects.filter(status=PetitionStatus.PUBLISHED, is_active=True)
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

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        petition = self.get_object()

        user = request.user if request.user.is_authenticated else None
        ip = get_client_ip(request)

        if user:
            PetitionView.objects.get_or_create(petition=petition, user=user)
        else:
            PetitionView.objects.get_or_create(petition=petition, user=None, ip_address=ip)

        return response

    def get_queryset(self):
        return Petition.objects.all()

    def get_success_url(self):
        return reverse('petitions:petition_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.get_form()
        context['comments'] = self.object.comments.select_related('user').order_by('-created_at')
        context['view_count'] = self.object.views.count()
        context['user_views'] = self.object.views.filter(user__isnull=False).count()
        context['anonymous_views'] = self.object.views.filter(user__isnull=True).count()
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
        response = super().form_valid(form)
        log_action(self.request.user, f"Created petition: {form.instance.title}", self.request)
        return response

    def get_success_url(self):
        return reverse_lazy('petitions:petition_detail', kwargs={'pk': self.object.pk})






class PetitionUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Petition
    form_class = PetitionForm
    template_name = 'petitions/petition_form.html'

    def test_func(self):
        petition = self.get_object()
        return self.request.user.is_superuser or petition.created_by == self.request.user

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            return HttpResponseForbidden("Non hai i permessi per modificare questa petizione.")
        else:
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
        qs = Petition.objects.filter(is_active=True)

        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))

        category = self.request.GET.get('category')
        if category:
            qs = qs.filter(category__name=category)

        status = self.request.GET.get('status')
        if status:
            qs = qs.filter(status=status)

        tags = self.request.GET.getlist('tags')
        if tags:
            qs = qs.filter(tags__name__in=tags).distinct()

        order = self.request.GET.get('order')
        if order == 'recenti':
            qs = qs.order_by('-created_at')
        elif order == 'meno_recente':
            qs = qs.order_by('created_at')
        elif order == 'popolari':
            qs = qs.annotate(num_signatures=Count('signatures')).order_by('-num_signatures')
        else:
            qs = qs.order_by('-created_at')

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        context['categories'] = PetitionCategory.objects.all()
        context['statuses'] = PetitionStatus.choices
        context['tags'] = Tag.objects.all()

        context['category_selected'] = self.request.GET.get('category', '')
        context['status_selected'] = self.request.GET.get('status', '')
        context['order_selected'] = self.request.GET.get('order', 'recenti')
        context['tags_selected'] = self.request.GET.getlist('tags')  # <--- aggiunto

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
        first_name = form.cleaned_data['first_name']
        last_name = form.cleaned_data['last_name']
        email = form.cleaned_data['email']
        petition = self.petition

        # Verifica firma già esistente
        already_signed = Signature.objects.filter(petition=petition, email=email).exists()
        already_pending = PendingSignature.objects.filter(petition=petition, email=email, confirmed=False).exists()

        if already_signed:
            messages.info(self.request, "Hai già firmato questa petizione con questa email.")
        elif already_pending:
            messages.info(self.request, "Hai già richiesto di firmare questa petizione. Controlla la tua email.")
        else:
            if self.request.user.is_authenticated:
                Signature.objects.create(
                    petition=petition,
                    first_name=first_name,
                    last_name=last_name,
                    email=email
                )
                Notification.objects.create(
                    user=petition.created_by,
                    message=f"{first_name} {last_name} ha firmato la tua petizione '{petition.title}'.",
                    link=reverse('petitions:petition_detail', kwargs={'pk': petition.pk})
                )
                messages.success(self.request, "Hai firmato con successo questa petizione.")
            else:
                pending = PendingSignature.objects.create(petition=petition, email=email)
                confirm_url = self.request.build_absolute_uri(
                    reverse('petitions:confirm_signature', kwargs={'token': pending.token})
                )
                send_mail(
                    subject='Conferma la tua firma',
                    message=f'Clicca per confermare la firma:\n{confirm_url}',
                    from_email='noreply@nerosinsurge13.it',
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
            return redirect('petitions:home')

        Signature.objects.create(
            petition=pending.petition,
            email=pending.email,
            first_name=pending.first_name,
            last_name=pending.last_name,
        )
        pending.confirmed = True
        pending.save()

        messages.success(request, "La tua firma è stata confermata!")
        return redirect('petitions:petition_detail', pk=pending.petition.pk)



class PetitionVoteView(View):
    def post(self, request, pk):
        petition = get_object_or_404(Petition, pk=pk)
        is_upvote = request.POST.get('vote') == 'up'
        ip = get_client_ip(request)
        user = request.user if request.user.is_authenticated else None

        vote_filter = {'petition': petition}
        if user:
            vote_filter['user'] = user
            vote_filter['ip_address__isnull'] = True
        else:
            vote_filter['user__isnull'] = True
            vote_filter['ip_address'] = ip

        vote = PetitionVote.objects.filter(**vote_filter).first()
        if vote:
            if vote.is_upvote != is_upvote:
                vote.is_upvote = is_upvote
                vote.save()
            else:
                vote.delete()
        else:
            PetitionVote.objects.create(
                petition=petition,
                user=user,
                ip_address=None if user else ip,
                is_upvote=is_upvote,
            )

        petition.refresh_from_db()

        html = render_to_string("petitions/partials/votes.html", {
            "petition": petition,
            "user_vote": PetitionVote.objects.filter(**vote_filter).first()
        }, request=request)

        return JsonResponse({'html': html})



class ReportPetitionView(LoginRequiredMixin, FormView):
    form_class = ReportForm
    template_name = 'reports/report_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.petition = get_object_or_404(Petition, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['petition'] = self.petition
        return context

    def form_valid(self, form):
        report = form.save(commit=False)
        report.reported_by = self.request.user
        report.petition = self.petition
        report.save()
        return redirect('petitions:petition_detail', pk=self.petition.pk)


class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'notification/notification_list.html'
    context_object_name = 'notifications'
    paginate_by = 10

    def get_queryset(self):
        return self.request.user.notifications.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['unread_notifications_count'] = self.request.user.notifications.filter(is_read=False).count()
        return context


@require_POST
@login_required
def mark_notification_read(request, pk):
    try:
        notif = Notification.objects.get(pk=pk, user=request.user)
        notif.is_read = True
        notif.save()
        return JsonResponse({'status': 'ok'})
    except Notification.DoesNotExist:
        return JsonResponse({'status': 'not_found'}, status=404)

@login_required
def go_to_notification(request, pk):
    notif = get_object_or_404(Notification, pk=pk, user=request.user)
    if not notif.is_read:
        notif.is_read = True
        notif.save()
    if notif.link:
        return redirect(notif.link)
    else:
        return redirect('petitions:notification_list')

@method_decorator(staff_member_required, name='dispatch')
class ModerationActionCreateView(CreateView):
    model = ModerationAction
    form_class = ModerationActionForm
    template_name = 'moderation/moderation_form.html'

    def form_valid(self, form):
        form.instance.moderator = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('petitions:petition_detail', kwargs={'pk': self.object.petition.pk})