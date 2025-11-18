from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Post, Profile

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'autocomplete': 'email'}))
    first_name = forms.CharField(required=True, max_length=30)
    last_name = forms.CharField(required=False, max_length=150)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Já existe uma conta com este e-mail.")
        return email

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content', 'image']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'No que você está pensando?',
                'rows': 3,
                'maxlength': 5000
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }
        labels = {
            'content': 'Conteúdo',
            'image': 'Imagem (opcional)'
        }

class ProfileEditForm(forms.ModelForm):
    # Campos do User
    first_name = forms.CharField(
        max_length=150,
        required=False,
        label='Nome',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Seu nome'
        })
    )
    last_name = forms.CharField(
        max_length=150,
        required=False,
        label='Sobrenome',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Seu sobrenome'
        })
    )
    email = forms.EmailField(
        required=True,
        label='E-mail',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'seu@email.com'
        })
    )
    
    # Campos do Profile
    avatar = forms.ImageField(
        required=False,
        label='Foto de Perfil',
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        })
    )
    bio = forms.CharField(
        required=False,
        label='Biografia',
        max_length=500,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Conte um pouco sobre você...',
            'rows': 4,
            'maxlength': '500'
        }),
        help_text='Máximo 500 caracteres'
    )
    
    # Campos de redes sociais
    facebook_url = forms.URLField(
        required=False,
        label='Facebook',
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'https://facebook.com/seu-perfil'
        })
    )
    instagram_url = forms.URLField(
        required=False,
        label='Instagram',
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'https://instagram.com/seu-perfil'
        })
    )
    linkedin_url = forms.URLField(
        required=False,
        label='LinkedIn',
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'https://linkedin.com/in/seu-perfil'
        })
    )
    twitter_url = forms.URLField(
        required=False,
        label='Twitter/X',
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'https://twitter.com/seu-perfil'
        })
    )
    github_url = forms.URLField(
        required=False,
        label='GitHub',
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'https://github.com/seu-usuario'
        })
    )
    
    class Meta:
        model = Profile
        fields = ['avatar', 'bio']
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.user:
            # Preencher campos do User
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial = self.user.last_name
            self.fields['email'].initial = self.user.email
            
            # Preencher redes sociais se existirem
            if self.instance and self.instance.socials:
                for social in self.instance.socials:
                    network = social.get('network', '').lower()
                    url = social.get('url', '')
                    field_name = f'{network}_url'
                    if field_name in self.fields:
                        self.fields[field_name].initial = url
    
    def save(self, commit=True):
        profile = super().save(commit=False)
        
        # Atualizar dados do User
        if self.user:
            self.user.first_name = self.cleaned_data.get('first_name', '')
            self.user.last_name = self.cleaned_data.get('last_name', '')
            self.user.email = self.cleaned_data.get('email', '')
            if commit:
                self.user.save()
        
        # Montar array de redes sociais
        socials = []
        social_networks = {
            'facebook': {'icon_class': 'bi bi-facebook', 'name': 'Facebook'},
            'instagram': {'icon_class': 'bi bi-instagram', 'name': 'Instagram'},
            'linkedin': {'icon_class': 'bi bi-linkedin', 'name': 'LinkedIn'},
            'twitter': {'icon_class': 'bi bi-twitter-x', 'name': 'Twitter'},
            'github': {'icon_class': 'bi bi-github', 'name': 'GitHub'},
        }
        
        for network, info in social_networks.items():
            url_field = f'{network}_url'
            url = self.cleaned_data.get(url_field, '').strip()
            if url:
                socials.append({
                    'network': network,
                    'name': info['name'],
                    'url': url,
                    'icon_class': info['icon_class']
                })
        
        profile.socials = socials
        
        if commit:
            profile.save()
        
        return profile