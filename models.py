import datetime

from django.db import models
from django.utils import timezone

from django.core.validators import RegexValidator

import re


class Question(models.Model):
    """
    The Question model has following attributes: 
    question_text: question for a poll.
    pub_date: published date of the poll.
    """
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')

    def __str__(self):
        """
        returns `question_text` value when a Question object is called.
        """
        return self.question_text

    def was_published_recently(self):
        """
        returns whether a poll was published within 1 day interval
        from the current date.
        """
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now

    """
    The attribute of the `was_published_recently` method: 
    admin_order_field: adds a custom column called `was_published_recently`,
    specifies the sort order to the database field `pub_date`.
    """
    was_published_recently.admin_order_field = 'pub_date'
    was_published_recently.boolean = True
    was_published_recently.short_description = 'Published recently?'


class Choice(models.Model):
    """
    The Choice model has following attributes: 
    question: foreign key to Question.
    choice_text: choices for the `question' of a poll.
    choice_color: hex color value for the choice, 
                  default color is black, 
                  RegexValidator checks whether input color choice is 
                  valid hex color. 
    votes: number of votes for the choice. 
    """
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    choice_color = models.CharField(max_length=7, 
        default='#000000',
        validators = [
        RegexValidator(
            regex = '(^#[0-9A-Fa-f]{6}$)',
            message = 'Hex color is invalid',
            code = 'invalid_color'),
        ]
        ) 
    votes = models.IntegerField(default=0)

    def __str__(self):
        """
        returns `choice_text` value when Choice object is called. 
        """
        return self.choice_text

    def has_valid_hex_color_format(self):
        """
        returns whether `choice_color` has correct hex color format. 
        """
        hex_pattern =  re.compile('(^#[0-9A-Fa-f]{6}$)')
        return bool(hex_pattern.match(self.choice_color))

