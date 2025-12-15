# forms.py
from django import forms
from .models import FinancialValue, Metric, MetricCategory
from allauth.account.forms import SignupForm
from .models import Company

class CompanyForm(forms.ModelForm):
    excel_file = forms.FileField(required=False, label="Upload Excel Data Sheet")
    class Meta:
        model = Company
        fields = ("name","ticker","exchange","sector","industry","listing_date","is_active")




class FinancialValueAdminForm(forms.ModelForm):

    metric_category = forms.ModelChoiceField(
        queryset=MetricCategory.objects.all(),
        required=True,
        label="Metric Category"
    )

    class Meta:
        model = FinancialValue
        fields = ["company", "metric_category", "metric", "time_period", "value"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Default: no metrics until category selected
        self.fields["metric"].queryset = Metric.objects.none()

        # When category is selected (POST / GET)
        if "metric_category" in self.data:
            try:
                category_id = int(self.data.get("metric_category"))
                self.fields["metric"].queryset = Metric.objects.filter(
                    category_id=category_id
                )
            except (ValueError, TypeError):
                pass

        # When editing an existing FinancialValue
        elif self.instance.pk:
            category = self.instance.metric.category
            self.fields["metric_category"].initial = category
            self.fields["metric"].queryset = Metric.objects.filter(category=category)


class CustomSignupForm(SignupForm):
    first_name = forms.CharField(max_length=30, label="First Name")
    last_name = forms.CharField(max_length=30, label="Last Name")

    def save(self, request):
        user = super().save(request)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
        return user