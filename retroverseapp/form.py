from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectMultipleField,TextAreaField,DecimalField,RadioField

from flask_wtf.file import FileField, FileAllowed

from wtforms.validators import DataRequired


class ProductForm(FlaskForm):
    productname = StringField('Product Name', validators=[DataRequired()])
    productdescription = TextAreaField('Description', validators=[DataRequired()])
    productprice = DecimalField('Price', validators=[DataRequired()])
    productimage = FileField('Image', validators=[FileAllowed(["jpg","png","webp","jpeg"], 'Images only!')])
    sizes = RadioField('Sizes', choices=[('Small', 'Small'), ('Medium', 'Medium'), ('Large', 'Large'), ('X-Large', 'X-Large')], validators=[DataRequired()])
    category = RadioField('Categories', choices=[('1', 'Accesories'), ('2', 'Clothing')], validators=[DataRequired()])
    Tag = StringField('Tag', validators=[DataRequired()])
    submit = SubmitField('Add Product')