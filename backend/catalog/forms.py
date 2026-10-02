from django import forms

class DiscountForm(forms.Form):
    discount_percentage = forms.IntegerField(
        min_value=0,
        max_value=100,
        label="Discount Percentage (%)"
    )
