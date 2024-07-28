def preparar_html(d: str):

    d = str(d)

    tags_borrar = ["script", "style", "<!--"]
    partes_borrar = ["header", "footer"] 

    # REEMPLAZAR CARACTERES DE HTML
    
    limpiar = [
        ["\n", ""], ["  ", " "],                            # quitar saltos de línea y espacios dobles
        ["-- >", "-->"], ["< !--", "<!--"],                 # corregir espacios antes y después de ">" y "<" en comentarios
        ["='", '="'], ["' ", '" '], ["'>", '">'],           # sustituir " ' " por ' " ' dentro de contenedores
        ["&nbsp;", " "], ["&lt;", "<"], ["&gt;", ">"],      # entidades clave html (key html entities)
        ["&amp;", "&"], ["&quot;", '"'], ["&euro;", "€"],   # LISTA COMPLETA: https://www.freeformatter.com/html-entities.html
        ["&laquo;", "«"], ["&raquo;", "»"]
        ]
    for x in limpiar:
        if x[0] in d:
            d = d.replace(x[0], x[1])

    def eliminar_etiqueta(d: str, tag: str):
        """
        Elimina todas las etiquetas y su contenido en HTML
        """    
        i = "<"+tag
        f = "</"+tag+">"
        if tag == "<!--": # tag comentarios
            i = "<!--"
            f = "-->"
        # Eliminar cierres sin abrir (al inicio del texto) ... d.find(i) - apertura // d.find(f) - cierre
        while d.find(f) < d.find(i) and d.find(f) != -1: 
            d = d[d.find(f)+len(f):]
        # Eliminar aperturas sin cerrar (al final del texto)... d.rfind(i) - última apertura // d.rfind(f) - último cierre
        while d.rfind(i) > d.rfind(f) and d.rfind(i) != -1: 
            d = d[:d.rfind(i)]
        # Eliminar etiquetas en el texto ... d.find(i) - apertura // d.find(f) - cierre
        for _ in range(d.count(i)):
            tag = d[d.find(i):d.find(f)+len(f)]
            d = d.replace(tag, "")
        return d

    # borrar etiquetas de javascript, estilos CSS y comentarios
    
    # Limitar al body
    if "<body" in d:
        d = d[d.find("<body"):d.find("</body>")+7]

    # Eliminar tags
    for tag in tags_borrar:
        d = eliminar_etiqueta(d, tag)

    # Borrar partes de una web que sólo aparecen una vez
    for parte in partes_borrar:
        if "<"+parte in d:
            d = d.replace(d[d.find("<"+parte):d.find("</"+parte+">")+len(parte)+3], "")

    # EXTRAER TAGS
    # La estrategia si basa en encontrar primero los cierres (</div>, </a>, </p>...) 
    # e incluirlos a tags si hay aperturas que coincidan (<div, <a, <p...)
    tags: list = d.split("</")
    t_cierre: set = {x[:x.find(">")] for x in tags if ">" in x}
    tags: set = {x for x in t_cierre if "<"+x in d}
    
    # d es el código html limpio
    # tags es la lista de etiquetas de contenedores en el código html 

    return d, tags


def listar_parametros(d: str, tag: str):

    contenedores: list = d.split("<"+tag)
    #contenedores = contenedores[1:]
    contenedores: list = list("<"+tag + x[:x.find(">")+1] for x in contenedores[1:])

    def extraer_parametros(tag: str, contenedor: list):
        # Extrae los parámetros de un contenedor previos al símbolo "=". Por ejemplo: [class, id,...]
        if "<"+tag+" " in contenedor[0]:
            contenedor[0] = contenedor[0].replace("<"+tag+" ", "")
        return list(x[:x.find("=")] for x in contenedor if "=" in x)

    pmts: list = list(x.split('" ') for x in contenedores)
    pmts: list = list(extraer_parametros(tag, x) for x in pmts)

    parametros: set = {x for z in pmts for x in z}

    # contenedores: una lista de todas las líneas de apertura de un tag. Por ejemplo: [<div class="x">, <div>, <div id="x"]
    # parametros: un set con los parámetros disponibles para ese tag sin duplicados: "class, id..."

    return contenedores, parametros



def listar_atributos(contenedores: list, pmt: str):

    contenedores_pmt: list = list(x for x in contenedores if pmt in x)

    def extraer_atributos(pmt: str, contenedor: list):

        atbs = []

        if '" ' not in contenedor and pmt+"=" in contenedor: #Si sólo tiene un parámetro

            atbs = contenedor[contenedor.find('="')+2:contenedor.find(">")].replace('"', '')
            atbs = atbs.split(" ")

        if '" ' in contenedor: #Si contiene varios parámetros:

            contenedor = contenedor.split('" ')  # Separar parámetros del contenedor (cierre de campos)
            atbs = list(x[x.find('="')+2:] for x in contenedor if pmt+"=" in x) # Encontrar elementos después del parámetro ("=")
            if len(atbs) > 0:
                atbs = atbs[0].split(" ")                                   # Separar campos por espacio (" ")
                atbs = list(x.replace('">', "") for x in atbs)              # Quitar comillas del último elemento '"'

        return atbs

    atbs: list = list(extraer_atributos(pmt, x) for x in contenedores_pmt if pmt in x)
    atributos: set = {x for z in atbs for x in z}

    # contenedores_pmt: una lista de los contenedores con el parámetro seleccionado.  
    # Por ejemplo: (class) <div class="x">, <div class="z"...

    # atributos: un set con todos los atributos disponibles para el parámetro seleccionado. 
    # Por ejemplo: class="caca culo pedo" -- > {caca, culo, pedo}

    return contenedores_pmt, atributos


def seleccionar_contenedores(contenedores_pmt: list, pmt: str, atb: str):

    def contenedor_parametro_campo(cont: list, pmt:str, atb: str):
        cont = cont[cont.find(pmt+'="')+len(pmt)+2:]
        cont = cont[:cont.find('"')]

        return cont.split(" ")

    if " " not in atb:
        contenedores_pmt_atb = list(x for x in contenedores_pmt if atb in contenedor_parametro_campo(x, pmt, atb))

    else: #si hay varios atributos dentro del parámetro. Por ejemplo: class="padre hijo"
        contenedores_pmt_atb = []
        atributos = atb.split(" ") #Lista de atributos seleccionados

        # Función para verificar si todos los textos están en el texto principal
        # En este caso, se utiliza para verificar que todos los atributos seleccionados están en el campo de atributos del contenedor
        def todos_atributos_presentes(lista_atributos, atributos_contenedor):
            return all(texto_parcial in atributos_contenedor for texto_parcial in lista_atributos)

        for contenedor in contenedores_pmt:
            atbs_ = contenedor[contenedor.find(pmt+'="')+len(pmt)+2:]
            atributos_contenedor = atbs_[:atbs_.find('"')] # Lista de atributos de cada contenedor
            if todos_atributos_presentes(atributos, atributos_contenedor) == True:
                contenedores_pmt_atb.append(contenedor)

    # contenedores_pmt_cmp contiene las aperturas cuando incluyen el tag, el parámetro y el atributo seleccionado
    # Por ejemplo: (div, class, ok ---- >> [<div .... class="ok" .... >, <div class="ok otras"  ..... >)

    return contenedores_pmt_atb


def extraer_texto(d: str, tag: str, contenedores: list):

    def obtener_posiciones(d: str, tag: str):

        tag_i = "<"+tag
        tag_f = "</"+tag+">"

        n_tag_i = d.count(tag_i) #cuenta las veces que aparece la apertura del tag en data
        n_tag_f = d.count(tag_f) #cuenta las veces que aparece el cierre del tag en data


        def indexar_tag(d: str, tag: str, n_tag: int):

            indice = [0]   # Crea un índice con un elemento 0. Empieza en cero para que no haya error al crear la posición (casi) absoluta en data

            for n in range(n_tag): # Para evitar while, se itera en función del número de veces que aparece tag en datos

                posicion = d.find(tag)
                indice.append(posicion + indice[-1] + len(tag)) 
                # a la posición relativa, suma el valor del último elemento en indice para que sea la posicion (casi) absoluta 
                # Casi, porque suma la longitud del tag para contrarrestar el recorte en data en el siguiente paso
                
                d = d[d.find(tag)+len(tag):] # Recorta data para pasar al siguiente tag en data 

            indice = list(x - len(tag) for x in indice if x > 0)
            # Al añadir len(tag) al índice, se genera un desfase con los datos reales
            # Se resta a cada índice len(tag) para obtener las posiciones absolutas exactas

            #Devuelve una lista numérica con las posiciones de la etiqueta (se puede utilizar apertura o cierre)
            return indice

        indice_i = indexar_tag(d, tag_i, n_tag_i) + [len(d) + 1] #lista de aperturas, añadiendo la longitud total de data
        indice_f = indexar_tag(d, tag_f, n_tag_f) + [len(d)]     # lista de cierres, añadiendo la longitud total de data
        
        return indice_i, indice_f



    #AL LÍO

    # La idea es utilizar índices de los tags de apertura y cierre para identificar elementos anidados
    # Por ejemplo <div class="padre"><div class="hijo"></div></div>
    # El objetivo es dentificar la etiqueta de cierre correcta, independientemente del número de elementos anidados

    resultado = []

    for contenedor in contenedores: # por cada contenedor que coincide con los criterios de tag, parámetro y campo

        # Crea dos índices, uno con las posiciones de los tags de apertura <tag, y otro con los de cierre </tag>
        indice_i, indice_f = obtener_posiciones(d, tag) #
        # Localiza la posición del contenedor (<tag parametro="campo") en datos 
        posicion = d.find(contenedor) 
        # Busca esa posición en el índice de aperturas(indice_i), y devuele su posición dentro de la lista
        indice = indice_i.index(posicion)

        # En el caso del índice de cierres finales, hay que reducirlo,
        # Sólo deben aparecer los cierres con una posición mayor a la posición de apertura del tag. 
        # Esto ayuda a empezar por una lista de posibles cierres, descartando los anteriores.
        indice_f_reformado = list(i for i in indice_f if i > indice_i[indice])

        
        # Itera la lista de aperturas. Es importante que i comience como 1, en "range(1, len(indice_i))"
        # El número "i" determina la posición de las siguientes aperturas que va a comparar con el primer cierre 

        for i in range(1, len(indice_i)):

            # Compara la posición de la siguiente apertura con la posición del primer cierre disponible
            if indice_i[indice + i] > indice_f_reformado[0]:

                # Mientras la posición de la siguiente apertura sea mayor a la posición del primer cierre,
                # sinfica que hay "i" elementos anidados

                # Por tanto, la posición de apertura es la primera posición en indice_i (la que estábamos buscando)
                # y la posición de cierre es el primer elemento + cada iteración - 1

                # El -1 es para contrarrestar que la iteración comienza por 1 (en range(1, len(indice_i)))
                # Si no estuviera, añadiría uno de los divs de cierre.

                posicion_apertura = indice_i[indice]
                posicion_cierre = indice_f_reformado[0 + i]

                posicion_cierre = indice_f_reformado[0 + i -1]

                # Añade los fragmentos de d a la lista de resultados



                resultado.append(d[posicion_apertura:posicion_cierre + len("</"+tag+">")])

                # borra las posiciones de las listas de índices
                del indice_i[indice]                          # lo borra según la posición
                indice_f.remove(indice_f_reformado[0 + i -1]) # lo borra según el contenido (de indice_f_reformado a indice_f)

                d = d[posicion_apertura+1:] # recorta data para pasar al siguiente contenedor

                break

    def corregir_cierres(resultado: str, tag: str):
        while resultado.count("<"+tag) != resultado.count("</"+tag+">"):
            resultado = resultado + "</"+tag+">"
        return resultado

    resultado = [corregir_cierres(x, tag) for x in resultado]

    return resultado




def scraper(d: str, tag: str, pmt: str, atb: str, contiene_texto: str):

    resultado = []

    #print(tag, pmt, atb, contiene_texto)

    d, tags = preparar_html(d) #preparar el html
    tags = sorted(list(tags))
    tags.append("todos")
    #print("- tags", tags)

    # Para empezar, necesita que el tag que se busque esté en la lista de tags disponibles
    #while tag not in tags:
        #print(f'Etiquetas disponibles: {tags}')
        #tag = str(input())

    # La opción tag = "todos" es para localizar un contenido especifico de una web que se quiera scrapear
    # La idea es, introduciendo un fragmento de texto, que devuelva los contenedores en los que aparece el texto
    if tag == "todos":

        contenedores = []

        # Por cada tag que encuentra, extrae todos los contenedores y todos los resultados
        # El filtrado por texto se realiza al final del proceso
        for tag_ in tags:
            contenedores_tag, parametros = listar_parametros(d, tag_)

            # filtro los contenedores sin parámetros, que no son fácilmente accesibles a posteriori
            # evita que aparezcan etiquetas como <strong>, <em>, <li>, <ul>, <div>...
            contenedores_tag = list(x for x in contenedores_tag if " " in x) 
            
            # devuelve todos los resultados (contenedor + texto) de todos los tags
            resultado_tag =  extraer_texto(d, tag_, contenedores_tag)

            # Añade la lista de cada tag a una lista general

            resultado.append(resultado_tag)
            contenedores.append(contenedores_tag)

        # Extrae todos los elementos de una lista dentro de una lista:
        # Por ejemplo: [[a, b][c, d]] --> [a, b, c, d]
        contenedores = list(x for z in contenedores for x in z)
        resultado = list(x for z in resultado for x in z) # coloca todos los elementos en una sola lista

    # Una vez seleccionado un tag (div, a, span...), empieza el rastreo
    elif tag in tags:
        # En primer lugar, genera una lista de contenedores (líneas de apertura que contienen ese tag. Ej. <div class="z">)
        # y parámetros: una lista de todas las posibilidades: ("class", "id", "href"...) que acompañan al tag seleccionado
        contenedores, parametros = listar_parametros(d, tag)
        parametros = sorted(list(parametros))
        parametros.append("todos")
        #print("-- parámetros", parametros)

        # Para continuar, si el parámetro está vacío, muestra las opciones posibles. Incluye la opción "todos"
        #while pmt not in parametros:
            #print(f'Parámetros disponibles: "todos",  {parametros}')
            #pmt = str(input())        

        # Es posible que ningún contenedor tenga parámetros. Ej. <h1>, <h2>. En ese caso, muestra los resultados directamente
        if len(parametros) == 0:
            #print("No hay parámetros disponibles")
            resultado = extraer_texto(d, tag, contenedores)

        # La opción "todos" devuelve todos los resultados de un tag, da igual si tiene o no qué parámetros.
        elif pmt == "todos":
            resultado = extraer_texto(d, tag, contenedores)

        # Si hay parámetros, es distinto de "todos" y está en la lista, continúa con la combinación tag+parámetro
        elif pmt in parametros:

            # Genera una lista con los contenedores que incluyen la dupla tag y parámetro
            # Por ejemplo: tag: div / pmt: class ----> todos los contenedores con <div class...>
            # Los atributos son una lista de atributos disponibles para el parámetro seleccionado
            # Por ejemplo: tag:a / pmt: href ----> todos los enlaces que contengan una ruta
            contenedores_pmt, atributos = listar_atributos(contenedores, pmt)
            atributos = sorted(list(atributos))            
            atributos.append("todos")

            #while atb == "": # Si el atb está vacío, muestra las opciones posibles
                #print(f'Campos disponibles: "todos", {atributos}')
                #atb = str(input())

            # La opción "todos" devuelve todos los contenedores con el tag y el parámetro seleccionado
            # sin importar el valor del parámetro. Muy útil para conseguir todos los enlaces. a / href / todos
            if atb == "todos":
                resultado = extraer_texto(d, tag, contenedores_pmt)

            else:  #Si no es "todos"

                # Si el atb está dentro de los valores para el parámetro seleccionado, busca las coincidencias de tag, pmt y campo
                # Posibilita buscar elementos más específicos, por ejemplo: div / id / xxx
                # Se pueden utilizar varios atributos sin importar el orden. por ejemplo: div / class / x y z
                # En este caso, sólo devuelve los contenedores con todos los atributos bajo el parámetro class
                contenedores_pmt_cmp = seleccionar_contenedores(contenedores_pmt, pmt, atb)
                resultado = extraer_texto(d, tag, contenedores_pmt_cmp)

    
    if contiene_texto != "":
        resultado = list(x for x in resultado if contiene_texto in x[x.find(">"):x.rfind("<")])

        # En caso de que queramos buscar un elemento por el texto, hay que añadir lo siguiente
        # para que se filtren los resultados lo más específicos posible

        if tag == "todos":

            def n_contenedores (r, contenedores):
                # Esta función cuenta el número de contenedores que aparecen en el resultado
                n = 0
                # Hay que añadir sum()
                # El resultado de la lista es el primer elemento (0) y el siguiente elemento cada vez
                # En este caso: [0, 1, 1, 1, ... n] por n en contenedores
                return sum(list(n + 1 for c in contenedores if c in r))

            # Devuelve los resultados en los que sólo hay un contenedor, es decir, el resultado más corto y más directo
            resultado = list(x for x in resultado if n_contenedores(x, contenedores) == 1)

    #print("------- RESULTADO --------- ")
    #print(list(set(resultado)))
    return resultado




#### EXTRAS


def limpiar_tags(d: str):

    tags: list = d.split("</")
    t_cierre: set = {x[:x.find(">")] for x in tags if ">" in x}
    tags: set = {x for x in t_cierre if "<"+x in d}

    def eliminar_tags_sin_cierre(d: str):
        lista_tags_vacios = [
            "area",
            "base",
            "br",
            "col",
            "command",
            "embed",
            "hr",
            "img",
            "input",
            "keygen",
            "link",
            "meta",
            "param",
            "source",
            "track",
            "wbr"
            ]

        for tag in lista_tags_vacios:
            while d.count("<"+tag) > 0:
                apertura_tag = d[d.find("<"+tag):]
                apertura_tag = apertura_tag[:apertura_tag.find(">")+1]
                d = d.replace(apertura_tag, "")
        return d


    def eliminar_aperturas_tags(d: str, tags: list):
        for tag in tags:
            while d.count("<"+tag) > 0:
                apertura_tag = d[d.find("<"+tag):]
                apertura_tag = apertura_tag[:apertura_tag.find(">")+1]
                d = d.replace(apertura_tag, "")
        return d

    def eliminar_cierres_tags(d: str, tags: list):
        for tag in tags:
            d = d.replace("</"+tag+">", "")
        return d


    def eliminar_tags(d:str, tags: list):
        d = eliminar_tags_sin_cierre(d)
        d = eliminar_aperturas_tags(d, tags)
        d = eliminar_cierres_tags(d, tags)
        return d

    d = eliminar_tags(d, tags)

    while "  " in d:
        d = d.replace("  ", " ")

    return d
