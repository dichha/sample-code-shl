from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone

from .models import Choice, Question


class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def queryset(self):
        """
        i) Returns the last five published questions with choice_ set (not including those set to be published in the future).
        ii) questions with choice_set are only displayed
        """
        return Question.objects.filter(
                pub_date__lte=timezone.now(),
                choice__isnull = False,
        ).distinct().order_by('-pub_date')[:5]


class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
        """
        Excludes any questions 
        i) that aren't published yet.
        ii) has no choice_set for the question.
        """
        return Question.objects.filter(
            pub_date__lte=timezone.now(),
            choice__isnull = False,
            ).distinct()


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'

    def get_queryset(self):
        '''
        Excludes any questions
        i) that aren't published yet.
        ii) has no choice_set for the question.
        '''
        return Question.objects.filter(
            pub_date__lte = timezone.now(),
            choice__isnull = False,
            ).distinct()


def vote(request, question_id):
    """
    Increases vote count for a particular choice when the choice is clicked
    else gives error.
    """
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        return HttpResponseRedirect(reverse('polls:results',
                                            args=(question.id,)))
