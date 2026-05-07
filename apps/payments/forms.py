from django import forms
from .models import Deposit, Withdrawal


class DepositForm(forms.ModelForm):
    class Meta:
        model  = Deposit
        fields = ('method', 'amount_usd', 'tx_hash')
        widgets = {
            'method':     forms.Select(attrs={'class': 'form-select', 'id': 'id_method'}),
            'amount_usd': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'min': '10', 'step': '0.01'}),
            'tx_hash':    forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Paste your transaction hash / ID here'}),
        }
        labels = {
            'amount_usd': 'Amount (USD)',
            'tx_hash':    'Transaction Hash / ID',
        }

    def clean_amount_usd(self):
        amount = self.cleaned_data.get('amount_usd')
        if amount and amount < 10:
            raise forms.ValidationError("Minimum deposit is $10.00 USD.")
        return amount


class WithdrawalForm(forms.ModelForm):
    class Meta:
        model  = Withdrawal
        fields = ('amount', 'bank_name', 'account_name', 'account_number', 'routing_number', 'swift_code')
        widgets = {
            'amount':         forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'min': '20', 'step': '0.01'}),
            'bank_name':      forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Ghana Commercial Bank'}),
            'account_name':   forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Account holder full name'}),
            'account_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Account number'}),
            'routing_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Routing number (US banks)'}),
            'swift_code':     forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'SWIFT/BIC code (international)'}),
        }

    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount and self.user:
            if amount < 20:
                raise forms.ValidationError("Minimum withdrawal is $20.00.")
            if amount > self.user.balance:
                raise forms.ValidationError(
                    f"Insufficient balance. Your available balance is ${self.user.balance:.2f}."
                )
        return amount
