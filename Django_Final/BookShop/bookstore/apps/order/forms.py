from django import forms
from .models import Order

class OrderCreateForm(forms.ModelForm):
	STATE_CHOICES = [
		('Andhra Pradesh', 'Andhra Pradesh'),
		('Arunachal Pradesh', 'Arunachal Pradesh'),
		('Assam', 'Assam'),
		('Bihar', 'Bihar'),
		('Chhattisgarh', 'Chhattisgarh'),
		('Goa', 'Goa'),
		('Gujarat', 'Gujarat'),
		('Haryana', 'Haryana'),
		('Himachal Pradesh', 'Himachal Pradesh'),
		('Jharkhand', 'Jharkhand'),
		('Karnataka', 'Karnataka'),
		('Kerala', 'Kerala'),
		('Madhya Pradesh', 'Madhya Pradesh'),
		('Maharashtra', 'Maharashtra'),
		('Manipur', 'Manipur'),
		('Meghalaya', 'Meghalaya'),
		('Mizoram', 'Mizoram'),
		('Nagaland', 'Nagaland'),
		('Odisha', 'Odisha'),
		('Punjab', 'Punjab'),
		('Rajasthan', 'Rajasthan'),
		('Sikkim', 'Sikkim'),
		('Tamil Nadu', 'Tamil Nadu'),
		('Telangana', 'Telangana'),
		('Tripura', 'Tripura'),
		('Uttar Pradesh', 'Uttar Pradesh'),
		('Uttarakhand', 'Uttarakhand'),
		('West Bengal', 'West Bengal'),
		('Andaman and Nicobar Islands', 'Andaman and Nicobar Islands'),
		('Chandigarh', 'Chandigarh'),
		('Dadra and Nagar Haveli and Daman and Diu', 'Dadra and Nagar Haveli and Daman and Diu'),
		('Delhi', 'Delhi'),
		('Jammu and Kashmir', 'Jammu and Kashmir'),
		('Ladakh', 'Ladakh'),
		('Lakshadweep', 'Lakshadweep'),
		('Puducherry', 'Puducherry'),
		('Other', 'Other'),
	]

	DISTRICT_CHOICES = [
		('Sample District', 'Sample District'),
		('Other', 'Other'),
	]

	PAYMENT_METHOD_CHOICES = (
		('GPay', 'GPay'),
		('EMI', 'EMI'),
		('COD', 'Cash on Delivery'),
	)

	state = forms.ChoiceField(choices=STATE_CHOICES, label='State')
	payment_method = forms.ChoiceField(choices=PAYMENT_METHOD_CHOICES, widget=forms.RadioSelect())

	class Meta:
		model = Order
		fields = ['name', 'email', 'phone', 'address', 'state', 'zip_code', 'payment_method', 'transaction_id']
