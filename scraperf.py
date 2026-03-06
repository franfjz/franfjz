from logger_config import logger
from typing import Tuple, List, Optional
import re


def listar_tags(d: str) -> set[str]:
    """
    :param d: HTML completo
    :return: Set con tags si hay cierres de etiqueta {</div>, </a>, </p>...}
    """
    #d = str(d)
    #tags = d.split("</")
    #t_cierre: set = {x[:x.find(">")] for x in tags if ">" in x}
    #return {x.lower() for x in t_cierre if "<" + x in d}
    return {t.lower() for t in re.findall(r'</([a-zA-Z0-9_-]+)>', str(d))}
def listar_atributos(d: str, tag: str) -> Tuple[list[str], set[str]]:
    """
    Contenedores: Lista con las etiquetas de apertura completas de un tag seleccionado (contenedores) (<div class="x"...>)
    Atributos: Set con todos los atributos dentro de todos los contenedores ("class, "id"...)
    :param d: HTML completo
    :param tag: etiqueta
    :return: Tuple de una lista con contenedores_tag y un set de atributos.
    """
    contenedores = d.split("<"+tag)
    contenedores_tag = ["<"+tag + x[:x.find('>')+1] for x in contenedores[1:]]
    contenedores_tag = [x.replace("'", '"')
                        for x in contenedores_tag if "<"+tag+" " in x or "<"+tag+">" in x]
    contenedores_tag = [re.sub(r'\s{2,}', ' ', x) for x in contenedores_tag] # eliminar dobles espacios en tag
    contenedores_tag = [x.replace(" >", ">").replace('=" ', '="') for x in contenedores_tag] # eliminar espacios al final en tag

    def extraer_atributos(tag: str, contenedor: list) -> set[str]:
        """ Extrae los atributos de un contenedor, previos al símbolo "=". Por ejemplo: [class, id...] """
        if "<"+tag+" " in contenedor[0]:
            contenedor[0] = contenedor[0].replace("<"+tag+" ", "")
        return {x[:x.find("=")] for x in contenedor} # if "=" in x

    atbs: list = [x.split('" ') for x in contenedores_tag]
    atbs: list = [extraer_atributos(tag, x) for x in atbs]
    atributos: set = {x.strip(" ") for z in atbs for x in z if "<" not in x}
    atributos.discard("")

    return contenedores_tag, atributos
def listar_valores(contenedores_tag: list[str], atb: str) -> Tuple[list[str], set[str]]:
    """
    Contenedores_atb: una lista de los contenedores con el atributo seleccionado.  (class -> <div class="x">, <div class="z"...)
    Valores: un set con todos los atributos disponibles para el parámetro seleccionado.  (class="caca culo pedo" -- > {caca, culo, pedo})
    :param contenedores_tag: Lista de contenedores de una etiqueta
    :param atb: Atributo
    :return: Tuple de una lista con contenedores_atb y un set de valores.
    """
    contenedores_atb: list = [x for x in contenedores_tag if atb+'="' in x]
    def extraer_valores(atb: str, contenedor: str):
        """  Extrae los valores de un contenedor, previos a la clase+"=". Por ejemplo: [w3-col, clase1...] """
        if contenedor.find('" '):  #Si el contenedor contiene varios atributos
            atributos: list = contenedor.rstrip('">').split('" ')                    # Separar parámetros del contenedor (cierre de campos)
            vals: list = [x[x.find(atb+'="')+len(atb)+2:] for x in atributos if atb+'="' in x]        # Encontrar elementos después del parámetro ("=")
            if len(vals) == 0:
                vals = [""] # evita errores con atributos sin valor. ej. div class=""
        else:  #Si el contenedor sólo tiene un atributo
            vals: list = [contenedor[contenedor.find('="')+2:contenedor.rfind('">')]]
        return vals[0].split(" ")

    valores: list = [extraer_valores(atb, x) for x in contenedores_atb]
    valores: set = {x for z in valores for x in z if x != ""}
    return contenedores_atb, valores
def seleccionar_contenedores(contenedores_atb: list[str], atb: str, val: str) -> list[str]:
    """
    :param contenedores_atb: Lista de los contenedores con el atributo seleccionado
    :param atb: atributo
    :param val: valor
    :return: Devuelve una lista con los contenedores que contienen un atributo y un valor seleccionado
    """
    def extraer_atributo_valor(cont: str, atb: str) -> set[str]:
        """ Devuelve un set de valores correspondientes a un atributo seleccionado """
        posicion_clase = cont.find(atb + '="') + len(atb) + 2
        valores = cont[posicion_clase:cont.find('"', posicion_clase)]
        return set(valores.split(" "))

    if " " not in val: # Si sólo hay un valor seleccionado. (class="xxx")
        contenedores_atb_val = list(x for x in contenedores_atb if val in extraer_atributo_valor(x, atb))
    else: # Si hay varios atributos dentro del parámetro. (class="x y z")
        contenedores_atb_val = []
        val = set(val.split(" ")) # Set de valores seleccionados {"x", "y", "z"}
        [contenedores_atb_val.append(x) for x in contenedores_atb if val.issubset(extraer_atributo_valor(x, atb))]
    return contenedores_atb_val
def extraer_texto(d: str, contenedores: list|str) -> list[str]:
    """
    Extrae el contenedor del HTML con su contenido (texto y contenido anidado)
    :param d: HTML completo
    :param contenedores: Lista de contenedores
    :return: Lista de resultados
    """
    if type(contenedores) is str:
        contenedores = [contenedores]

    def alargar_cadena(data: str, tag: str, cadena: str) -> str:
        """
        Extiende la cadena hasta la próxima etiqueta de cierre en data
        Si falta la etiqueta de cierre, la cadena es hasta el final de data
        :param data: html completo
        :param tag: etiqueta
        :param cadena: cadena anidada sin completar
        :return: cadena alargada hasta la siguiente cadena de cierre
        """
        pos_cadena = data.find(cadena) + len(cadena)
        if data[pos_cadena:].count("</" + tag.strip()) > 0:
            extension_cadena = data[pos_cadena:data.find("</" + tag.strip(), pos_cadena) + len(tag) + 3]
        else:
            extension_cadena = data[pos_cadena:]
        return cadena + extension_cadena

    def extraer_contenedor_html(texto: str, elementos: List[str]) -> Optional[str] | List[str]:
        """
        A partir del contenedor seleccionado, genera una búsqueda para aceptar variaciones en el HTML original.
        Por ejemplo, espacios entre elementos y el uso de comillas dobles o simples.
        :param texto: HTML completo original
        :param elementos: lista de elementos que componen el contenedor. Ej. ['div', 'class', 'hola']
        :return: cadena de texto literal del contenedor en el HTML. Ej. '<DIV   class= "hola"  >'
        """
        # escapamos los elementos y preparamos un grupo OR para detectarlos
        partes = [re.escape(e) for e in elementos]
        grupo = '|'.join(partes)

        # Caracteres permitidos:
        # - espacios (\s)
        # - comillas ' "
        # - signo =
        # - O cualquiera de los elementos en la lista (letras/dígitos incluidos)
        permitido = fr"(?:\s|['\"=]|{grupo})"

        # Construimos la secuencia en orden:
        # primer elemento obligatorio + el resto como lookaheads en orden
        lookaheads = ''.join(fr"(?={permitido}*{p})" for p in partes[1:])
        inicio = partes[0]

        # Regex final
        patron = fr"<\s*{inicio}{lookaheads}{permitido}*>"

        flags = re.IGNORECASE
        m = re.search(patron, texto, flags)
        return m.group(0) if m else "No se ha encontrado la etiqueta"

    resultado = []

    for contenedor in contenedores:
        contenedor = contenedor[1:-1]
        if " " in contenedor:
            tag = contenedor[:contenedor.find(" ")]
        else:
            tag = contenedor + ">"

        contenedor_limpio = (contenedor.replace("'", " ")
                             .replace('"', " ")
                             .replace("=", " ")
                             .replace("  ", " "))
        lista_elementos_contenedor = contenedor_limpio.strip().split(" ")

        # El contenedor tal y como aparece en el HTML (espacios, saltos de línea...)
        contenedor_html = extraer_contenedor_html(d, lista_elementos_contenedor)
        cadena = d[d.find(contenedor_html):]

        # COMPROBAR SI HAY ETIQUETA DE CIERRE
        if cadena.count("</"+tag) != 0: # Si hay etiqueta de cierre después de la apertura
            cadena = cadena[:cadena.find("</"+tag)+len(tag)+3]
        else:
            logger.critical(f'¡AVISO! -  Falta la etiqueta de cierre. Extrae desde el contenedor hasta el final')
            #print("¡AVISO! -  Falta la etiqueta de cierre. Extrae desde el contenedor hasta el final")
            resultado.append(cadena)

        # RESOLVER ANIDAMIENTO
        if cadena.count("<"+tag) == 1 and cadena.count("</"+tag.strip()) == 1: # No tiene elementos anidados
            resultado.append(cadena)
        else: # Tiene elementos anidados
            while cadena.count("<"+tag) != cadena.count("</"+tag.strip()):
                # Mientras no haya el mismo número de cierres y de aperturas en la cadena, alarga la cadena
                cadena = alargar_cadena(d, tag, cadena)
                if len(cadena) == len(d[d.find(cadena):]) and cadena.count("<"+tag) != cadena.count("</"+tag.strip()):
                    print(f' **** Falta un tag de cierre en cadenas anidadas --> {cadena[:cadena.find(">")+1]}')
                    break
            resultado.append(cadena)
        d = d[d.find(contenedor_html)+len(contenedor_html):] # recorta d para evitar duplicados
    return resultado

def limpiar_tags(d: str ) -> str:
    """
    Elimina todas las etiquetas HTML de una cadena de texto
    Solo se usa para filtrar los resultados por el texto
    :param d: html completo
    :return: html sin tags
    """
    chunks: list = d.split("</")
    t_cierre: set = {x[:x.find(">")] for x in chunks if ">" in x}
    tags: set[str] = {x for x in t_cierre if "<"+x in d}

    def eliminar_apertura_cierre_tags(d: str, tags: set[str]) -> str:
        for tag in tags:
            # Eliminar aperturas
            while d.count("<"+tag) > 0:
                posicion_apertura = d.find("<"+tag)
                apertura_tag = d[posicion_apertura:d.find(">", posicion_apertura) + 1]
                d = d.replace(apertura_tag, "")
            d = d.replace("</" + tag + ">", "") # Eliminar cierre
        return d
    def eliminar_tags_sin_cierre(d: str) -> str:
        lista_tags_vacios: set = {
        # HTML5
        'area', 'base', 'col', 'embed', 'hr', 'img',  #br aparte
        'input', 'keygen', 'link', 'menuitem', 'meta', 'param', 'source', 'track', 'wbr',
        # Obsoletas después de  HTML5
        'basefont', 'bgsound', 'command', 'frame', 'image', 'isindex', 'nextid', 'spacer'
        }
        for tag in lista_tags_vacios:
            while d.count("<"+tag) > 0:
                posicion_apertura = d.find("<"+tag)
                tag_vacio = d[posicion_apertura:d.find(">", posicion_apertura) + 1]
                d = d.replace(tag_vacio, "")
        return d
    def sustituir_br(d: str) -> str:
        br: list = ["<br>", "<br/>", "</br>", "<br />", "</ br>"]
        for b in br:
            d = d.replace(b, "\\n").replace(b.upper(), "\\n")
        return d

    d = eliminar_apertura_cierre_tags(d, tags)
    d = eliminar_tags_sin_cierre(d)
    d = sustituir_br(d)
    return d
def filtrar_texto(lista_resultados: list[str], texto: str) -> list[str]:
    """ Devuelve las cadenas más cortas que contengan un texto definido previamente
    :param lista_resultados: Resultados obtenidos previamente
    :param texto: texto que busca
    :return: Lista con resultados con texto en el contenido anidado (después de limpiar_tags)
    """
    resultado = [x for x in lista_resultados if texto in limpiar_tags(x)]
    def n_contenedores (r, contenedores) -> int:
        """ Cuenta el número de contenedores que aparecen en el resultado """
        n = 0
        return sum(list(n + 1 for c in contenedores if c in r))
    resultado = [x for x in resultado if n_contenedores(x, lista_resultados) == 1] # Devuelve el resultado posible más corto
    return resultado

#######################################################################
#######################################################################
################         SCRAPER        ###############################
#######################################################################
#######################################################################

def scraper(d: str, tag: str, atributo: str = "__todos__", valor: str = "__todos__", texto: str = "") -> list[str]:
    # Devuelve una lista de etiquetas y contenido con los resultados según los parámetros de la función
    d = str(d)
    d_tags = listar_tags(d)

    if tag in d_tags:
        contenedores_tag, d_atributos = listar_atributos(d, tag)
        if atributo in d_atributos:
            contenedores_atb, d_valores = listar_valores(contenedores_tag, atributo)
            valores = set(valor.split(" "))
            if valores.issubset(d_valores):
                contenedores_atb_val = seleccionar_contenedores(contenedores_atb, atributo, valor)
                resultados = extraer_texto(d, contenedores_atb_val)
            else:
                if not (valor.startswith("__") and valor.endswith("__")):
                    logger.critical(f'Valor "{valor}" no está en la lista de atributos')
                    #print(f'Valor "{valor}" no está en la lista de valores')
                    return [""]
                resultados = extraer_texto(d, contenedores_atb) # Resultados de tag->atb
        else:
            if not (atributo.startswith("__") and valor.endswith("__")):
                logger.critical(f'Atributo "{atributo}" no está en la lista de atributos')
                #print(f'Atributo "{atributo}" no está en la lista de atributos')
                return [""]
            resultados = extraer_texto(d, contenedores_tag) # Resultados de tag

        # FILTRAR RESULTADOS POR TEXTO
        if texto != "":
            return filtrar_texto(resultados, texto)

        #logger.debug(f'Scraperf - Resultados: {resultados}')
        #print(f'Resultados: {resultados}')
        return resultados

    else:
        logger.critical(f'Scraperf - El tag "{tag}" no aparece en la lista ({d_tags})')
        #print(f'Scraperf - El tag "{tag}" no aparece en la lista ({d_tags})')
        return [""]

#######################################################################
#######################################################################
#################           EXTRAER ATRIBUTOS           ###############
#######################################################################
#######################################################################

def extraer_atributo(texto:str, atributo:str):
    if atributo+'="' in texto:
        pos_atb = texto.find(atributo+'="')+len(atributo)+2
        return texto[pos_atb:texto.find('"', pos_atb)]
    else:
        return ""
def extraer_link(texto: str):
    return extraer_atributo(texto, "href")
def extraer_img(texto: str):
    return extraer_atributo(texto, "src")


"""
#######################################################################
#######################################################################
################         BUSCADOR       ###############################
#######################################################################
#######################################################################

def buscador(d: str, tag: str = "", atributo: str = "__todos__", valor: str = "__todos__", texto: str = ""):

    print(f'\n\n.....  Bienvenido al buscador de scraper_f .....')
    resultado = []
    d_tags = listar_tags(d)
    print(f"Estos son los tags disponibles:\n{d_tags}")

    while tag not in d_tags:
        tag = input(f"Escribe un tag: ")

    if tag in d_tags:
        contenedores_tag, d_atributos = listar_atributos(d, tag)
        print(f'Estos los los atributos disponibles de {tag}: \n{d_atributos}')
        while atributo not in d_atributos:
            atributo = input(f"Escribe un atributo: ")

        if atributo in d_atributos:
            contenedores_atb, d_valores = listar_valores(contenedores_tag, atributo)
            print(f'Estos los los valores disponibles de {tag}>{atributo}: \n{d_valores}')
            while valor not in d_valores:
                valor = input(f"Escribe un valor o varios separados por espacio: ")

            if valor in d_valores:
                contenedores_atb_val = seleccionar_contenedores(contenedores_atb, atributo, valor)
                resultados = extraer_texto(d, contenedores_atb_val)
                print(f'Estos son los resultados:')
                [print(f'{i} -->  {x}') for i, x in enumerate(resultados)]

                respuesta = ""
                while respuesta not in ["s", "n"]:
                    respuesta = input(f'Sí (s), No (n): ')
                if respuesta == "s":
                    buscador(d)
                else:
                    print("chao chao cacao")
"""
