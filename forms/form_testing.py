from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FloatField, DateField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError

class GoalForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(min=1, max=100)])
    description = TextAreaField("Description", validators=[DataRequired()])
    amount = FloatField("Amount", validators=[DataRequired()])
    due_date = DateField("Due Date", validators=[DataRequired()])
    status = SelectField("Status", choices=[("active", "Active"), ("completed", "Completed")])
    submit = SubmitField("Create Goal")