from flask_wtf import FlaskForm
from wtforms import StringField, SelectField
from wtforms.validators import DataRequired


class LegalEntityForm(FlaskForm):
    legal_entity = StringField('Юр. лицо полностью', validators=[DataRequired()])
    legal_entity_short = StringField('Юр. лицо кратко', validators=[DataRequired()])
    legal_entity_group = StringField('Юр. лицо кратко (альтернатива)', validators=[DataRequired()])
    legal_entity_short_eng = StringField('Юр. лицо кратко на английском', validators=[DataRequired()])
    legal_entity_code = StringField('Юр. лицо код', validators=[DataRequired()])


class FunctionForm(FlaskForm):
    function = StringField('Функция', validators=[DataRequired()])
    description = StringField('Описание', validators=[DataRequired()])


class CostCenterForm(FlaskForm):
    cost_center = StringField('Кост центр', validators=[DataRequired()])
    function_id = SelectField('Функция', coerce=int)
    public_name = StringField('Название костцентра', validators=[DataRequired()])
    description = StringField('Описание', validators=[DataRequired()])


class BranchForm(FlaskForm):
    branch = StringField('Бранч', validators=[DataRequired()])
    public_name = StringField('Название бранча', validators=[DataRequired()])
    description = StringField('Описание', validators=[DataRequired()])


class LocationsForm(FlaskForm):
    location = StringField('Локация', validators=[DataRequired()])
    public_name = StringField('Название локации', validators=[DataRequired()])
    description = StringField('Описание', validators=[DataRequired()])


class DivisionForm(FlaskForm):
    division = StringField('Дивизион', validators=[DataRequired()])
    public_name = StringField('Название дивизиона', validators=[DataRequired()])
    description = StringField('Описание', validators=[DataRequired()])


class AccessSettingForm(FlaskForm):
    user_id = SelectField('Пользователь', coerce=int)
    legal_entity_id = SelectField('Юр. Лицо', coerce=int)
    cost_center_id = SelectField('Кост центр', coerce=int)
    branch_id = SelectField('Бранч', coerce=int)
    location_id = SelectField('Локация', coerce=int)
    division_id = SelectField('Дивизион', coerce=int)