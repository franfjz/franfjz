exec(open("scraper.py", encoding="utf-8").read())


import pytest
from pprint import pprint

# marcar tests: @pytest.mark.nombre
# filtrar tests: pytest -m slow -vvv / pytest -m "not slow" -vvv
# filtrar test nombres funcion: pytest -k func(parte-del-nombre) -vvv (not func/func and not func_)


@pytest.fixture
def data():
    return """

    <test_pmt pmt="test"> test parametro</test_pmt>
    <test_dos_pmt pmt="test" id="57"> test parametro</test_dos_pmt>
    <test_varios_pmt pmt="test"></test_varios_pmt>
    <test_varios_pmt class="test"></test_varios_pmt>
    <test_varios_pmt id="test"></test_varios_pmt>

    <test_atb pmt="atb_test"> test atributos</test_atb>
    <test_dos_atb pmt="atb_test atb_test2"> test parametro</test_dos_atb>
    <test_varios_atb pmt="test"></test_varios_atb>
    <test_varios_atb class="test"></test_varios_atb>
    <test_varios_atb id="test"></test_varios_atb>

    <div class="a"> test div class a </div>
    <div class="b"> test div class b </div>
    <div class="b c"> test div class b/c </div>

    <section class="test"> el problema es que 5 < 6 > 8 falla </section>
    <section class="test_img"> el problema es que el triángulo <img src=".jpg"> 5 < 6 > 8 falla con </section>

    <span class="a-end" id="chachi">más chulo que un <area> </br> <br/> <img src="">ocho > cinco y < que 16</span>
    <span class="aok-hidden" id="a-end"> yeah </span>

    <anidados class="abuelo">abuelo<anidados class="padre">padre<anidados class="hijo">hijo</anidados></anidados></anidados>

    <anidados class="papa"><anidados class="hermano">hermano 1</anidados><anidados class="hermano">hermano 2<anidados class="minino">minino</anidados></anidados></anidados>

    <anidados class="trio"><trio id="1">primero</trio><trio id="2">segundo</trio><trio id="3">tercero</trio></anidados>
    """




###################################################################
##############     OTROS    ##########################
###################################################################



def test_basico_parentesis(data):
    # búsqueda básica de un contenedor
    resultado = scraper(data, "section", "class", "test", "")
    resultado_esperado = ['<section class="test"> el problema es que 5 < 6 > 8 falla </section>']
    assert  resultado == resultado_esperado


def test_basico_parentesis_img(data):
    # búsqueda básica de un contenedor
    resultado = scraper(data, "section", "class", "test_img", "")
    resultado_esperado = ['<section class="test_img"> el problema es que el triángulo <img src=".jpg"> 5 < 6 > 8 falla con </section>']
    assert  resultado == resultado_esperado

def test_basico_span_img(data):
    # búsqueda básica de un contenedor
    resultado = scraper(data, "span", "class", "a-end", "")
    resultado_esperado = ['<span class="a-end" id="chachi">más chulo que un <area> </br> <br/> <img src="">ocho > cinco y < que 16</span>']
    assert  resultado == resultado_esperado


def test_span_img_limpiar_tags(data):
    # búsqueda básica de un contenedor
    resultado = limpiar_tags(scraper(data, "span", "class", "a-end", "")[0])
    resultado_esperado = 'más chulo que un ocho > cinco y < que 16'
    assert  resultado == resultado_esperado


###################################################################
##############     SCRAPER LOCALIZAR BÁSICO    ##########################
###################################################################


def test_basico_div_a(data):
    # búsqueda básica de un contenedor
    resultado = scraper(data, "div", "class", "a", "")
    resultado_esperado = ['<div class="a"> test div class a </div>']
    assert  resultado == resultado_esperado

def test_basico_div_b(data):
    # búsqueda básica de un contenedor en varios elementos
    resultado = scraper(data, "div", "class", "b", "")
    resultado_esperado = ['<div class="b"> test div class b </div>', '<div class="b c"> test div class b/c </div>']
    assert  resultado == resultado_esperado





###################################################################
##############     TEST EXTRAER PARÁMETROS    #####################
###################################################################

# TEST EXTRAER 1 PARÁMETRO
def test_pmt_contenedor_solo_uno(data):
    contenedores, parametros = listar_parametros(data, "test_pmt")
    contenedor_esperado = ['<test_pmt pmt="test">']
    assert contenedores == contenedor_esperado

def test_pmt_solo_uno(data):
    contenedores, parametros = listar_parametros(data, "test_pmt")
    parametros_esperados = {'pmt'}
    assert parametros == parametros_esperados

# TEST EXTRAER 2 PARÁMETROS
def test_pmt_contenedor_dos(data):
    contenedores, parametros = listar_parametros(data, "test_dos_pmt")
    contenedor_esperado = ['<test_dos_pmt pmt="test" id="57">']
    assert contenedores == contenedor_esperado

def test_pmt_dos(data):
    contenedores, parametros = listar_parametros(data, "test_dos_pmt")
    parametros_esperados = {'pmt', 'id'}
    assert parametros == parametros_esperados

# TEST EXTRAER VARIOS PARÁMETROS DE VARIOS CONTENEDORES
def test_pmt_contenedor_varios(data):
    contenedores, parametros = listar_parametros(data, "test_varios_pmt")
    contenedor_esperado = ['<test_varios_pmt pmt="test">', '<test_varios_pmt class="test">', '<test_varios_pmt id="test">']
    assert contenedores == contenedor_esperado

def test_pmt_varios(data):
    contenedores, parametros = listar_parametros(data, "test_varios_pmt")
    parametros_esperados = {'pmt', 'id', 'class'}
    assert parametros == parametros_esperados




###################################################################
##############     TEST EXTRAER ATRIBUTOS    ######################
###################################################################

#def listar_atributos(contenedores: list, pmt: str):

# TEST EXTRAER 1 ATRIBUTO DE UN CONTENEDOR
def test_atb_contenedor_solo_uno():
    contenedores, atributos = listar_atributos(['<test_atb pmt="atb_test">'], "pmt")
    atributos_esperados = {'atb_test'}
    assert atributos == atributos_esperados

# TEST EXTRAER 2 ATRIBUTOS DE UN CONTENEDOR
def test_atb_contenedor_dos():
    contenedores, atributos = listar_atributos(['<test_dos_atb pmt="atb_test atb_test_2">'], "pmt")
    atributos_esperados = {'atb_test', 'atb_test_2'}
    assert atributos == atributos_esperados

# TEST EXTRAER 3 ATRIBUTOS DE UN CONTENEDOR
def test_atb_contenedor_dos():
    contenedores, atributos = listar_atributos(['<test_dos_atb pmt="atb_test_1 atb_test_2 atb_test_3">'], "pmt")
    atributos_esperados = {'atb_test_1', 'atb_test_2', 'atb_test_3'}
    assert atributos == atributos_esperados

# TEST EXTRAER 1 ATRIBUTO DE VARIOS CONTENEDORES
def test_atb_uno_varios_contenedores():
    contenedores, atributos = listar_atributos(['<test_atb pmt="atb_test">', '<test_atb pmt="atb_test">'], "pmt")
    atributos_esperados = {'atb_test'}
    assert atributos == atributos_esperados

# TEST EXTRAER VARIOS ATRIBUTOS DE VARIOS CONTENEDORES

def test_atb_varios_contenedores():
    contenedores, atributos = listar_atributos(['<test_atb pmt="atb_test_1">', '<test_atb pmt="atb_test_2">'], "pmt")
    atributos_esperados = {'atb_test_1', 'atb_test_2'}
    assert atributos == atributos_esperados

def test_atb_varios_contenedores_duplicados():
    contenedores, atributos = listar_atributos(['<test_atb pmt="atb_test_1">', '<test_atb pmt="atb_test_1 atb_test_2">'], "pmt")
    atributos_esperados = {'atb_test_1', 'atb_test_2'}
    assert atributos == atributos_esperados


###################################################################
##############     ANIDADOS    ##########################
###################################################################

                    # ANIDADOS ABUELO/PADRE/HIJO

def test_anidados_abuelo(data):
    # abuelo con padre e hijo anidados
    resultado = scraper(data, "anidados", "class", "abuelo", "")
    resultado_esperado = ['<anidados class="abuelo">abuelo<anidados class="padre">padre<anidados class="hijo">hijo</anidados></anidados></anidados>']
    assert  resultado == resultado_esperado   

def test_anidados_padre(data):
    # padre dentro de abuelo con hijo anidado
    resultado = scraper(data, "anidados", "class", "padre", "")
    resultado_esperado = ['<anidados class="padre">padre<anidados class="hijo">hijo</anidados></anidados>']
    assert  resultado == resultado_esperado  

def test_anidados_hijo(data):
    # hijo dentro de padre y abuelo
    resultado = scraper(data, "anidados", "class", "hijo", "")
    resultado_esperado = ['<anidados class="hijo">hijo</anidados>']
    assert  resultado == resultado_esperado  


                    #### ANIDADOS PAPA Y HERMANOS CON MININO


def test_anidados_papa(data):
    # papa con varios hijos (hermanos)
    resultado = scraper(data, "anidados", "class", "papa", "")
    resultado_esperado = ['<anidados class="papa"><anidados class="hermano">hermano 1</anidados><anidados class="hermano">hermano 2<anidados class="minino">minino</anidados></anidados></anidados>']
    assert  resultado == resultado_esperado  

def test_anidados_hermanos(data):
    # lista de hermanos con minino
    resultado = scraper(data, "anidados", "class", "hermano", "")
    resultado_esperado = ['<anidados class="hermano">hermano 1</anidados>', '<anidados class="hermano">hermano 2<anidados class="minino">minino</anidados></anidados>']
    assert  resultado == resultado_esperado  

def test_anidados_minino(data):
    # minino de uno de los hermanos
    resultado = scraper(data, "anidados", "class", "minino", "")
    resultado_esperado = ['<anidados class="minino">minino</anidados>']
    assert  resultado == resultado_esperado  

def test_anidados_hermano_minino(data):
    # hermano que contiene a minino
    resultado = scraper(data, "anidados", "class", "hermano", "minino")
    resultado_esperado = ['<anidados class="hermano">hermano 2<anidados class="minino">minino</anidados></anidados>']
    assert  resultado == resultado_esperado  


                    #### ANIDADOS TRIO


def test_anidados_trio(data):
    # trio sin id
    resultado = scraper(data, "anidados", "class", "trio", "")
    resultado_esperado = ['<anidados class="trio"><trio id="1">primero</trio><trio id="2">segundo</trio><trio id="3">tercero</trio></anidados>']
    assert  resultado == resultado_esperado  

def test_trio_id(data):
    # trio con parametro id
    resultado = scraper(data, "trio", "id", "todos", "")
    resultado_esperado = ['<trio id="1">primero</trio>', '<trio id="2">segundo</trio>', '<trio id="3">tercero</trio>']
    assert  resultado == resultado_esperado  

def test_trio_id_3(data):
    # trio con parametro id
    resultado = scraper(data, "trio", "id", "3", "")
    resultado_esperado = ['<trio id="3">tercero</trio>']
    assert  resultado == resultado_esperado  

def test_trio_todos_segundo(data):
    # trio con texto
    resultado = scraper(data, "trio", "todos", "", "segundo")
    resultado_esperado = ['<trio id="2">segundo</trio>']
    assert  resultado == resultado_esperado  

def test_trio_id_todos_segundo(data):
    # trio con texto
    resultado = scraper(data, "trio", "id", "todos", "segundo")
    resultado_esperado = ['<trio id="2">segundo</trio>']
    assert  resultado == resultado_esperado  

def test_trio_id_2_segundo(data):
    # trio con texto
    resultado = scraper(data, "trio", "id", "2", "segundo")
    resultado_esperado = ['<trio id="2">segundo</trio>']
    assert  resultado == resultado_esperado  

#def test(data):

    #resultado = scraper(data, "div", "class", "a", "")
    #resultado_esperado = ['<div class="a">test div class a</div>']
    #assert  resultado == resultado_esperado

