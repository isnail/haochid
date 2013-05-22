__author__ = 'biyanbing'

from django import forms

from models import *
from product.models import *

class CommentAddForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('content', 'is_send', 'product', 'parent')

    def clean_is_send(self):
        is_send = self.cleaned_data.get('is_send')
        if is_send and is_send == '1':
            return True
        return False

    def clean_product(self):
        product = self.cleaned_data.get('product')
        if product:
            try:
                product = Product.objects.get(id=product)
                return product
            except:
                raise forms.ValidationError('product error')
        else:
            raise forms.ValidationError('product error')

    def clean_parent(self):
        parent = self.cleaned_data.get('parent')
        if parent:
            try:
                parent = Comment.objects.get(id=parent)
                return parent
            except:
                return None
