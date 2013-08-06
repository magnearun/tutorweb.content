from zope import schema

from plone.app.textfield import RichText
from plone.autoform import directives as form
from plone.namedfile.field import NamedBlobImage, NamedBlobFile
from plone.supermodel import model

from collective.z3cform.datagridfield import DictRow

from tutorweb.content import _


class IStaticQuestionAnswer(model.Schema):
    text = schema.TextLine(
        title=_(u'Answer text'),
        required=True)
    correct = schema.Bool(
        title=_(u'Correct?'),
        required=False)
    randomize = schema.Bool(
        title=_(u'Randomize order'),
        required=False)


class IStaticQuestion(model.Schema):
    """Static question (i.e. one not generated by R)"""
    title = schema.TextLine(
        title=_(u'Question Title'),
        description=_(u'The title of the question'),
        required=True)
    image = NamedBlobImage(
        title=_(u'Question Image'),
        description=_(u'An image associated to the question'),
        required=False)
    #TODO: Make this check box do something useful
    processLatex = schema.Bool(
        title=_(u'Process LaTeX formulae?'),
        description=_(u'Convert $$ surrounded LaTeX formulae into graphics'),
        default=True,
        required=False)
    text = RichText(
        title=u"Question text",
        default_mime_type='text/html',
        output_mime_type='text/html',
        allowed_mime_types=('text/html', 'text/plain',),
        required=False)
    choices = schema.List(
        title=_(u"Answers"),
        description=_(u'''Specify the answer text, if the answer is correct
                        and if the answer should be in a randomized order
                        when displayed in a quiz.'''),
        value_type=DictRow(title=u"tablerow", schema=IStaticQuestionAnswer),
        required=False)
    form.widget(choices=
                'collective.z3cform.datagridfield.DataGridFieldFactory')
    explanation = RichText(
        title=u"Explanation text",
        description=_(u'Displayed to the student after the question is asked'),
        default_mime_type='text/html',
        output_mime_type='text/html',
        allowed_mime_types=('text/html', 'text/plain',),
        required=False)

class ILecture(model.Schema):
    """A lecture contains Slides and quiz questions"""
    title = schema.TextLine(
        title=_(u'Title'),
        description=_(u'The title of the lecture'),
        required=True)
    hist_selection = schema.Float(
        title=_(u'Historical Selection probability'),
        description=_(u'''The chance that a question before this given as part
                      of this lecture. A negative value will mean the default
                      for this tutorial is used.'''),
        default=-1.0,
        min=-1.0,
        max=1.0,
        required=True)
    Pdf=NamedBlobFile(
        title=_(u'Generated lecture PDF'),
        required=False)
