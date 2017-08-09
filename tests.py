import datetime

from django.utils import timezone

from django.test import TestCase

from .models import Question, Choice

from django.urls import reverse

#Create your tests here.

class QuestionMethodTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        '''
        was_published_recently() should return False for questions
        whose pub_date is in the future.
        '''
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date = time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        ''' 
        was_published_recently() should return False for 
        questions whose pub_data is older than 1 day
        '''
        time = timezone.now() - datetime.timedelta(days=30)
        old_question = Question(pub_date = time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        ''' 
        was_published_recently() should return True for questions
        whose pub_date is within the last day. 
        '''
        time = timezone.now() - datetime.timedelta(hours=1)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)


def create_question(question_text, days):
    ''' 
    creates a question with the given `question_text` and 
    published the given number of `days` offset to now (negative for 
    question published in the past, positive for the questions that have 
    yet to be published).
    '''
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date = time)


def create_choice(question, choice_text, choice_color):
    '''
    creates choice with a given `question`, `choice_text` and `choice_color` where a `question` is a foreign key to a Choice object.
    '''
    fk = question
    choice_text = choice_text
    choice_color = choice_color
    return Choice.objects.create(question = fk, choice_text = choice_text, choice_color = choice_color)


class ChoiceMethodTests(TestCase):      

    def test_has_valid_hex_color_format_with_incorrect_format(self):
        '''
        has valid_hex_color_format() should return False for invalid hex color
        '''
        question_for_color_test = create_question(question_text = 'Question for color test.', days = -1)
        choice_obj = create_choice(question = question_for_color_test, choice_text = "Choice for color.", choice_color = '#ien566')
        self.assertIs(choice_obj.has_valid_hex_color_format(), False)

    def test_has_valid_hex_color_format_with_correct_format(self):
        '''
        has_valid_hex_color_format() should return true for valid hex color
        '''
        question_for_color_test = create_question(question_text = 'Question for color test.', days = -1)
        choice_obj = create_choice(question = question_for_color_test, choice_text = 'Choice for color.', choice_color = '#e3a8f9')
        self.assertIs(choice_obj.has_valid_hex_color_format(), True)


class QuestionViewTests(TestCase):
    def test_index_view_with_no_questions(self):
        ''' 
        If no questions exist, an appropriate message should be displayed.
        '''
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'](), [])

    def test_index_view_with_a_past_question_and_no_choice_set(self):
        ''' 
        Questions with a pub_date in the past and no choice set should not be displayed on the index page.
        '''

        create_question(question_text = "Past question.", days = -30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'](), [])
    def test_index_view_with_a_past_question_and_choice_set(self):
        ''' 
        Questions with a pub_date in the past with choice set should be displayed on the index page.
        '''
        past_question_with_choice_set = create_question(question_text = "Past question with choice set.", days = -30)
        create_choice(question = past_question_with_choice_set, choice_text = 'Choice 1.', choice_color = '#e3a8f9' )
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'](), ['<Question: Past question with choice set.>'])


    def test_index_view_with_a_future_question_and_no_choice_set(self):
        ''' 
        Questions with a pub_date in the future  and no choice set should not be displayed on the index page. 
        '''
        create_question(question_text = "Future question.", days = 30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'](), [])  
    def test_index_view_with_a_future_question_and_choice_set(self):
        ''' 
        Questions with a pub_date in the future  and have choice set should not be displayed on the index page. 
        '''
        future_question_with_choice_set = create_question(question_text = "Future question.", days = 30)
        create_choice(question = future_question_with_choice_set, choice_text = 'Choice 1.', choice_color = '#e3a8f9')
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'](), [])  

    def test_index_view_with_future_question_and_past_question_with_no_choice_set(self):
        ''' 
        Past and future questions with no choice set, should not be displayed.
        '''
        create_question(question_text = "Past question.", days = -30)
        create_question(question_text = "Future question.", days = 30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'](),
            []
            )
    def test_index_view_with_future_question_and_past_question_with_choice_set(self):
        ''' 
        Even if both past and future questions with choice set exist, only past questions should be displayed.
        '''
        past_question_with_choice_set = create_question(question_text = "Past question.", days = -30)
        create_choice(question = past_question_with_choice_set, choice_text = 'Choice 1.', choice_color = '#e3a8f9')
        future_question_with_choice_set = create_question(question_text = "Future question.", days = 30)
        create_choice(question = past_question_with_choice_set, choice_text = 'Choice 1.', choice_color = '#e3a8f9')
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'](),
            ['<Question: Past question.>']
            )
    def test_index_view_with_two_past_questions_and_choice_set(self):
        ''' 
        The question index page may display multiple quesions that have choice set.
        '''
        past_question1_with_choice_set = create_question(question_text = "Past question 1.", days = -30)
        create_choice(question = past_question1_with_choice_set, choice_text = 'Choice 1.', choice_color = '#e3a8f9')
        past_question2_with_choice_set = create_question(question_text = "Past question 2.", days = -5)
        create_choice(question = past_question2_with_choice_set, choice_text = 'Choice 2.', choice_color = '#e3a8f9')
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'](), 
            ['<Question: Past question 2.>', '<Question: Past question 1.>']

        )

        
class QuestionIndexDetailTests(TestCase):
    def test_detail_view_with_a_future_question_and_no_choice_set(self):
        ''' 
        The detail view of a question with a pub_date in the future and no choice should return a 404 not found. 
        '''
        future_question_with_no_choice_set = create_question(question_text = 'Future question.', days = 5)
        url = reverse('polls:detail', args=(future_question_with_no_choice_set.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_detail_view_with_a_future_question_and_choice_set(self):
        ''' 
        The detail view of a question with a pub_date in the future and choice set should return a 404 not found. 
        '''
        future_question_with_choice_set = create_question(question_text = 'Future question.', days = 5)
        create_choice(question = future_question_with_choice_set, choice_text = 'Choice 1.', choice_color = '#e3a8f9')
        url = reverse('polls:detail', args=(future_question_with_choice_set.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


    def test_detail_view_with_a_past_question_no_choice_set(self):
        ''' 
        The detail view of a question with a pub_date in the past and no choice_set should return 404 not found.
        '''
        past_question_with_no_choice_set = create_question(question_text = 'Past Question.', days = -5)
        url = reverse('polls:detail', args = (past_question_with_no_choice_set.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_detail_view_with_a_past_question_with_choice_set(self):
        ''' \
        The detail view of a question with a pub_date in the past and choice set should display the question's text.
        '''
        past_question_with_choice_set = create_question(question_text = 'Past Question.', days = -5)
        create_choice(question = past_question_with_choice_set, choice_text = 'Choice 1.', choice_color = '#e3a8f9')
        url = reverse('polls:detail', args = (past_question_with_choice_set.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question_with_choice_set.question_text)


class QuestionResultViewTests(TestCase):
    def test_result_view_with_a_future_question_and_no_choice_set(self):
        '''
        The result view of a question with a pub_date in the future and no choice set should return a 404 not found
         '''
        future_question_with_no_choice_set = create_question(question_text = 'Future question.', days = 15)
        url = reverse('polls:results', args = (future_question_with_no_choice_set.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_result_view_with_a_past_question_and_no_choice_set(self):
        '''
        The result view of a question with a pub date in the past and no choice set should return a 404 not found.
        '''

        past_question_with_no_choice_set = create_question(question_text = 'Past Question.', days = -10)
        url = reverse('polls:results', args = (past_question_with_no_choice_set.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404 )

    ''' Rest of the testing for with choice set will be similar to that of class QuestionIndexDetailTest()'''
