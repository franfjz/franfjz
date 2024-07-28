Bienvenid@ a este programita para scrapear HTML.

Por defecto, busca dentro de la etiqueta body, fuera de header y footer.
Reduce el html a la etiqueta y es capaz de extraer elementos anidados. El resultado es una lista de cadenas de texto.

resultado = scraper(data, "etiqueta", "parámetro", "atributo/s", "filtrar_texto")

Inputs de la función:

-- data -> es la variable que contiene el texto html del que queremos extraer los datos. Lo convierte a cadena de texto.
-- etiqueta -> es una cadena de texto con la etiqueta/tag. Identifica las que tienen apertura y cierre. Ej: "div", "p", "a"... 
-- parámetro -> es una cadena de texto con el nombre del parámetro contenido en la etiqueta. Ej: "class", "id", "href",...
-- atributo/s -> es una cadena de texto con uno o varios atributos dentro de un parámetro concreto. Ej.: "col-md-3"...
-- filtrar_texto (opcional) -> es el texto que debe aparecer en el contenido dentro de la etiqueta.

-------------- Ejemplos de uso --------------

El ejemplo más básico es buscar una etiqueta, parámetro y atributo concreto.

Si queremos buscar los elementos en <code><div class="ejemplo">XXX</div></code> podemos usar:

resultado = scraper(data, "div", "class", "ejemplo", "")
Devolverá una lista con todas las etiquetas div class="ejemplo" y su contenido

Se incluyen las opciones "todos" en etiqueta, parámetro y atributo/s, de forma que se pueden obtener todos los elementos que cumplan alguna de las condiciones.

Todas las etiquetas -> resultado = scraper(data, "todos", "", "", "")
Todas las clases de una etiqueta -> resultado = scraper(data, "div", "todos", "", "")
Todos los atributos de una clase -> resultado = scraper(data, "div", "class", "todos", "")

En todos los casos anteriores podemos añadir un valor a "filtrar_texto" si queremos buscar los elementos que contengan una palabra que aparezca visible en la web, es decir, dentro de los elementos que estemos buscando. En el primer ejemplo: "XXX". Si queremos buscar el enlace del Buscador, podemos utilizar:

resultado = scraper(data, "a", "href", "enlace", "Buscador")

resultado = scraper(data, "todos, "", "", "", "Buscador")
...

-------------- Funciones extra --------------

Como extra, incluye la función "limpiar_tags", para devolver el contenido de un elemento de la lista sin etiquetas.
Esta función elimina también las etiquetas HTML sin cierre: "img", "br", "hr", "embed", etc.
