from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, DateField, RadioField, FieldList, FormField
from wtforms.validators import DataRequired


class PostForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    text = TextAreaField('Текст', validators=[DataRequired()])
    submit = SubmitField('Опубликовать')


class FeaturePlanForm(FlaskForm):
    feature_name = StringField('Название фичи', validators=[DataRequired()])
    feature_comment = TextAreaField('Описание фичи', validators=[DataRequired()])
    feature_planned_start = DateField('Дата начала работы', validators=[DataRequired()])
    feature_planned_end = DateField('Дата окончания работы', validators=[DataRequired()])
    submit = SubmitField('Опубликовать')


class VotingForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    description = TextAreaField('Описание', validators=[DataRequired()])
    submit = SubmitField('Опубликовать')


class VotingOptionForm(FlaskForm):
    title = StringField('Новыый вариант', validators=[DataRequired()])
    text = TextAreaField('Описание', validators=[DataRequired()])
    submit = SubmitField('Добавить')


class VoteRadio(FlaskForm):
    options = RadioField('', choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')])


class VoteForm(FlaskForm):

    texts = ""
    fields = FieldList(FormField(VoteRadio), min_entries=1)
    submit = SubmitField('Проголосовать')
