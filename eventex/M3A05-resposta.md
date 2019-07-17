Olá pessoal!

Segue a minha jornada para resolver o desafio de *usar hash ao invés da pk*. Espero que seja útil!

- Primeiramente, eu entendi que precisava mudar o ```def test_post(self):``` da ```class SubscribePostValid(TestCase):``` para que no assert contemplasse um hash gerado a partir de algum dos campos do  ```name, cpf,            email, phone```. Então escolhi o campo ```email``` por ser, em princípio, único.

- Agora qual função hash do ```Python``` usar? _Google it!_ :) Cheguei até a ```hashlib```:
```python
import hashlib

print(hashlib.md5('contato@eventex.com.br'.encode()).hexdigest())

700ca7ede7d6bf88aa59a3305080299b
```

- Então já sabia qual resultado esperar na url após o inscricao: ```/inscricao/700ca7ede7d6bf88aa59a3305080299b/```. E não mais ```/inscricao/1/```

- Substitui no assert do test e tornei o dicionário ```data``` um atributo da classe para que as funções pudessem visualizá-lo:

```python
def setUp(self):
        self.data = dict(name='Allan Lima', cpf='45773653320',
                         email='arglbr@gmail.com', phone='85-98872-8779')
        self.resp = self.client.post('/inscricao/', self.data)

    def test_post(self):
        """ Valid POST should redirect to /inscricao/hashlib.md5(self.data['email'].encode())/"""

        # Já verifica o status code
        hash_object = hashlib.md5(self.data['email'].encode())
        self.assertRedirects(self.resp,
                             f'/inscricao/{hash_object.hexdigest()}/')
```

- Importei a módulo de hash:
```python
import hashlib

from django.core import mail
from django.test import TestCase

from eventex.subscriptions.forms import SubscriptionForm
from eventex.subscriptions.models import Subscription
```

- Rodei os testes e o erro era que o ```Redirects``` retornou 1 e não o valor do hash do email:
```command
(.wttd) D:\WTTD\wttd>manage test
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
..........................F..
======================================================================
FAIL: test_post (eventex.subscriptions.tests.test_view_subscribe.SubscribePostValid)
Valid POST should redirect to /inscricao/1/
----------------------------------------------------------------------
Traceback (most recent call last):
  File "D:\WTTD\wttd\eventex\subscriptions\tests\test_view_subscribe.py", line 57, in test_post
    f'/inscricao/{hash_object.hexdigest()}/')
  File "D:\WTTD\wttd\.wttd\lib\site-packages\django\test\testcases.py", line 383, in assertRedirects
    msg_prefix + "Response redirected to '%s', expected '%s'" % (url, expected_url)
  File "D:\WTTD\wttd\.wttd\lib\site-packages\django\test\testcases.py", line 403, in assertURLEqual
    msg_prefix + "Expected '%s' to equal '%s'." % (url1, url2)
AssertionError: '/inscricao/1/' != '/inscricao/be1e46e221d9a9d36483778cf30a9f26/'
- /inscricao/1/
+ /inscricao/be1e46e221d9a9d36483778cf30a9f26/
 : Response redirected to '/inscricao/1/', expected '/inscricao/be1e46e221d9a9d36483778cf30a9f26/'Expected '/inscricao/1/' to equal '/inscricao/be1e46e221d9a9d36483778cf30a9f26/'.

----------------------------------------------------------------------
Ran 29 tests in 0.320s

FAILED (failures=1)
Destroying test database for alias 'default'...
```

- Então alterei a view ```create``` do ```views.py``` para retornar o hash (importei o módulo ```hashlib``` também) e não mais a ```pk```:
```python
def create(request):
    form = SubscriptionForm(request.POST)

    if not form.is_valid():
        return render(request, 'subscriptions/subscription_form.html',
                      {'form': form})

    subscription = Subscription.objects.create(**form.cleaned_data)
    subscription.hash_url = hashlib.md5(subscription.email.encode()).hexdigest()

    # Send subscription email
    _send_mail('Confirmação de inscrição',
               settings.DEFAULT_FROM_EMAIL,
               subscription.email,
               'subscriptions/subscription_email.txt',
               {'subscription': subscription})

    return HttpResponseRedirect(f'/inscricao/{subscription.hash_url}/')

```

- Rodei os testes e o erro foi um belo 404, ou seja, o Django não conseguiu redirecionar para a página com o caminho do hash.
```command
(.wttd) D:\WTTD\wttd>manage test
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
..........................F..
======================================================================
FAIL: test_post (eventex.subscriptions.tests.test_view_subscribe.SubscribePostValid)
Valid POST should redirect to /inscricao/1/
----------------------------------------------------------------------
Traceback (most recent call last):
  File "D:\WTTD\wttd\eventex\subscriptions\tests\test_view_subscribe.py", line 57, in test_post
    f'/inscricao/{hash_object.hexdigest()}/')
  File "D:\WTTD\wttd\.wttd\lib\site-packages\django\test\testcases.py", line 378, in assertRedirects
    % (path, redirect_response.status_code, target_status_code)
AssertionError: 404 != 200 : Couldn't retrieve redirection page '/inscricao/be1e46e221d9a9d36483778cf30a9f26/': response code was 404 (expected 200)

----------------------------------------------------------------------
Ran 29 tests in 0.386s

FAILED (failures=1)
Destroying test database for alias 'default'...
```

-  Nesse momento eu travei e percebi que não havia compreendido algum conceito. Então resolvi executar o servidor, criar uma inscrição e ver o erro no Django:
```html
Page not found (404)
Request Method: 	GET
Request URL: 	http://127.0.0.1:8000/inscricao/1d54c15e32a8ac08effdeff4aaa673f7/

Using the URLconf defined in eventex.urls, Django tried these URL patterns, in this order:

    inscricao/
    inscricao/<int:pk>/
    admin/

The current path, inscricao/1d54c15e32a8ac08effdeff4aaa673f7/, didn't match any of these.
```

- Então o óbvio foi apresetado para mim: alterar os parâmetros do ```urls.py``` para contemplar o hash no lugar do inteiro da ```pk```. Fiquei na dúvida de qual [conversor de caminho](https://docs.djangoproject.com/en/2.2/topics/http/urls/#path-converters) usar e escolhi o tipo ```string``` que era o mais simples e que *fazia funcionar*:
```python
urlpatterns = [
    path('', eventex.core.views.home),
    path('inscricao/', subscribe),
    path('inscricao/<str:hash_url>/', detail),
    path('admin/', admin.site.urls),
]
```

- Rodei os testes e tive como resultado que seis deram erro.
```command
(.wttd) D:\WTTD\wttd>manage test
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
...........EEEEE..........E..
======================================================================
ERROR: test_context (eventex.subscriptions.tests.test_view_detail.SubscriptionDetailGet)
----------------------------------------------------------------------
======================================================================
ERROR: test_get (eventex.subscriptions.tests.test_view_detail.SubscriptionDetailGet)
----------------------------------------------------------------------
======================================================================
ERROR: test_html (eventex.subscriptions.tests.test_view_detail.SubscriptionDetailGet)
----------------------------------------------------------------------
======================================================================
ERROR: test_template (eventex.subscriptions.tests.test_view_detail.SubscriptionDetailGet)
----------------------------------------------------------------------
======================================================================
ERROR: test_not_found (eventex.subscriptions.tests.test_view_detail.SubscriptionDetailNotFound)
----------------------------------------------------------------------
======================================================================
ERROR: test_post (eventex.subscriptions.tests.test_view_subscribe.SubscribePostValid)
Valid POST should redirect to /inscricao/1/
----------------------------------------------------------------------
Ran 29 tests in 0.923s

FAILED (errors=6)
Destroying test database for alias 'default'...
```

- Depois que enxuguei as lágrimas, eu pensei: vou manter foco apenas no ```test_post```. Vamos ver o que ele me disse: a view ```detail()``` recebeu o argumento não esperado chamado ```hash_url```. E ao verificar os parâmetros da bendita view encontramos o ```pk```. 
```command
======================================================================
ERROR: test_post (eventex.subscriptions.tests.test_view_subscribe.SubscribePostValid)
Valid POST should redirect to /inscricao/1/
----------------------------------------------------------------------
Traceback (most recent call last):
  File "D:\WTTD\wttd\eventex\subscriptions\tests\test_view_subscribe.py", line 57, in test_post
    f'/inscricao/{hash_object.hexdigest()}/')
  File "D:\WTTD\wttd\.wttd\lib\site-packages\django\test\testcases.py", line 371, in assertRedirects
    redirect_response = response.client.get(path, QueryDict(query), secure=(scheme == 'https'))
  File "D:\WTTD\wttd\.wttd\lib\site-packages\django\test\client.py", line 535, in get
    response = super().get(path, data=data, secure=secure, **extra)
  File "D:\WTTD\wttd\.wttd\lib\site-packages\django\test\client.py", line 347, in get
    **extra,
  File "D:\WTTD\wttd\.wttd\lib\site-packages\django\test\client.py", line 422, in generic
    return self.request(**r)
  File "D:\WTTD\wttd\.wttd\lib\site-packages\django\test\client.py", line 503, in request
    raise exc_value
  File "D:\WTTD\wttd\.wttd\lib\site-packages\django\core\handlers\exception.py", line 34, in inner
    response = get_response(request)
  File "D:\WTTD\wttd\.wttd\lib\site-packages\django\core\handlers\base.py", line 115, in _get_response
    response = self.process_exception_by_middleware(e, request)
  File "D:\WTTD\wttd\.wttd\lib\site-packages\django\core\handlers\base.py", line 113, in _get_response
    response = wrapped_callback(request, *callback_args, **callback_kwargs)
TypeError: detail() got an unexpected keyword argument 'hash_url'
```

```python
def detail(request, pk):
    try:
        subscription = Subscription.objects.get(pk=pk)
    except  Subscription.DoesNotExist:
        raise Http404


    return render(request, 'subscriptions/subscription_detail.html',
                  {'subscription': subscription})

```


- Então, eu percebi outro problema: o valor do hash nunca ia ser igual ao valor da ```pk```. Inicialmente eu pensei em passar outro parâmetro no ```urls.py``` ou nos dados do **POST**, mas não tive sucesso. Então pesquisei no fórum e encontrei a [dica](https://forum.welcometothedjango.com.br/t/m3a05-desafio-de-usar-um-hash-como-id-na-rota/2091): *...Idealmente você mantém o ID do banco e adiciona um campo novo para o UUID. Assim, o ID do banco segue normalmente com as sequências e índices padrões do Django e o UUID entra como funcionalidade complementar....*. Bingo! Então é só criar um campo novo no modelo para guardar o hash e pesquisar pelo valor do hash.
```python
class Subscription(models.Model):
    name = models.CharField('nome', max_length=100)
    cpf = models.CharField('CPF', max_length=11)
    email = models.EmailField('e-mail')
    phone = models.CharField('telefone', max_length=20)
    created_at = models.DateTimeField('criado em', auto_now_add=True)
    hash_url = models.CharField('URL', max_length=32, null=True)
```

- Rodei os testes e recebi o seguinte erro: a coluna ```hash_url``` não existe na tabela ```subscriptions_subscription```. Então chegou a hora criar uma ```migration``` de banco de dados e aplicá-la.
```command
django.db.utils.OperationalError: no such column: subscriptions_subscription.hash_url
```

```command
(.wttd) D:\WTTD\wttd>manage makemigrations
Migrations for 'subscriptions':
  eventex\subscriptions\migrations\0002_auto_20190714_1917.py
    - Change Meta options on subscription
    - Add field hash_url to subscription
    - Alter field cpf on subscription
    - Alter field created_at on subscription
    - Alter field email on subscription
    - Alter field name on subscription
    - Alter field phone on subscription
```

```command
(.wttd) D:\WTTD\wttd>manage migrate
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, sessions, subscriptions
Running migrations:
  Applying subscriptions.0002_auto_20190714_1917... OK
```

- Rodei os testes e ao contrário de seis erros foram quatro falhas e um erro!
```command
(.wttd) D:\WTTD\wttd>manage test
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
...........EFF...........F..
----------------------------------------------------------------------
Ran 29 tests in 0.821s

FAILED (failures=4, errors=1)
Destroying test database for alias 'default'...
```

- Tive progresso! E o que ```test_post``` disse? 404!  Ou seja, o ```Redirect``` não vai encontrar o valor da ```hash_url``` no banco porque eu não salvei o valor!
```command
======================================================================
FAIL: test_post (eventex.subscriptions.tests.test_view_subscribe.SubscribePostValid)
Valid POST should redirect to /inscricao/1/
----------------------------------------------------------------------
Traceback (most recent call last):
  File "D:\WTTD\wttd\eventex\subscriptions\tests\test_view_subscribe.py", line 57, in test_post
    f'/inscricao/{hash_object.hexdigest()}/')
  File "D:\WTTD\wttd\.wttd\lib\site-packages\django\test\testcases.py", line 378, in assertRedirects
    % (path, redirect_response.status_code, target_status_code)
AssertionError: 404 != 200 : Couldn't retrieve redirection page '/inscricao/be1e46e221d9a9d36483778cf30a9f26/': response code was 404 (expected 200)
```

- Então acrescentei ```subscription.save()```:
```python
def create(request):
    form = SubscriptionForm(request.POST)

    if not form.is_valid():
        return render(request, 'subscriptions/subscription_form.html',
                      {'form': form})

    subscription = Subscription.objects.create(**form.cleaned_data)
    subscription.hash_url = hashlib.md5(subscription.email.encode()).hexdigest()
    subscription.save()

    # Send subscription email
    _send_mail('Confirmação de inscrição',
               settings.DEFAULT_FROM_EMAIL,
               subscription.email,
               'subscriptions/subscription_email.txt',
               {'subscription': subscription})

    return HttpResponseRedirect(f'/inscricao/{subscription.hash_url}/')
```
 
- Rodei os testes e PQP!!!! Diminuiu a quantidade de falhas e errors! Três falharam e um erro! E o ```test_post``` passou com sucesso!
```command
(.wttd) D:\WTTD\wttd>manage test
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
...........EFF..............
======================================================================
ERROR: test_context (eventex.subscriptions.tests.test_view_detail.SubscriptionDetailGet)
----------------------------------------------------------------------
======================================================================
FAIL: test_get (eventex.subscriptions.tests.test_view_detail.SubscriptionDetailGet)
----------------------------------------------------------------------
======================================================================
FAIL: test_html (eventex.subscriptions.tests.test_view_detail.SubscriptionDetailGet) (<subtest>)
----------------------------------------------------------------------
======================================================================
FAIL: test_template (eventex.subscriptions.tests.test_view_detail.SubscriptionDetailGet)
----------------------------------------------------------------------
Ran 29 tests in 0.331s

FAILED (failures=3, errors=1)
Destroying test database for alias 'default'...
```

- Escolhi consertar os testes na ordem de baixo para cima. Assim escolhi o ```test_template```. Ele procurou um template e não encontrou. Ao investigar o ```setUp``` percebemos que o dado utilizado no teste não atribuia o valor do hash para o campo ```hash_url```. Além disso, tentava chamar o método ```get``` usando a ```pk``` e não o ```hash_url```.
```command
======================================================================
FAIL: test_template (eventex.subscriptions.tests.test_view_detail.SubscriptionDetailGet)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "D:\WTTD\wttd\eventex\subscriptions\tests\test_view_detail.py", line 21, in test_template
    self.resp, 'subscriptions/subscription_detail.html')
  File "D:\WTTD\wttd\.wttd\lib\site-packages\django\test\testcases.py", line 644, in assertTemplateUsed
    % (template_name, ', '.join(template_names))
AssertionError: False is not true : Template 'subscriptions/subscription_detail.html' was not a template used to render the response. Actual template(s) used: 404.html, base.html
```

```python
def setUp(self):
        email = 'arglbr@gmail.com'
        hash_url = hashlib.md5(email.encode()).hexdigest()

        self.obj = Subscription.objects.create(
            name='Allan Reffson',
            cpf='45773653320',
            email=email,
            phone='85-988728779',
            hash_url=hash_url
        )
        self.resp = self.client.get(f'/inscricao/{self.obj.hash_url}/')
```

- Rodei os testes e o resultado foi:
```command
(.wttd) D:\WTTD\wttd>manage test
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
.............................
----------------------------------------------------------------------
Ran 29 tests in 0.334s

OK
Destroying test database for alias 'default'...
```

- Enchi o peito de ar e falei um senhor PQP, que meus filhos correram da sala com medo!

- Depois disso acrescentei o campo no ```Admin``` para ver os valores *in natura*

- O resultado final está disponível no github: https://github.com/arglbrce/eventex/commit/27a41b36e752b7c02e51f8572e12adec95c0c191