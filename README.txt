Bienvenid@ a este programita para scrapear HTML con funciones.

resultado = scraper(data, "etiqueta", "atributo", "valor/es", "filtrar_texto")
El resultado es una lista de cadenas de texto.

Inputs de la función:

-- data -> es la variable que contiene el texto html del que queremos extraer los datos. Lo convierte a cadena de texto.
-- etiqueta -> es una cadena de texto con la etiqueta/tag. Identifica las que tienen apertura y cierre. Ej: "div", "p", "a"... 
-- atributo -> es una cadena de texto con el nombre del atributo contenido en la etiqueta. Ej: "class", "id", "href",...
-- valor/es -> es una cadena de texto con uno o varios valores dentro de un atributo concreto. Ej.: "col-md-3"...
-- filtrar_texto (opcional) -> es el texto que debe aparecer en el contenido dentro de la etiqueta.

-------------- Ejemplos de uso --------------

El ejemplo más básico es buscar una etiqueta, atributo y valor concreto.

Si queremos buscar los elementos en <div class="ejemplo">XXX</div> podemos usar:

resultado = scraper(data, "div", "class", "ejemplo", "")
Devolverá una lista con todas las etiquetas div class="ejemplo" y su contenido

Se incluyen las opciones "__todos__" en etiqueta, parámetro y atributo/s, de forma que se pueden obtener todos los elementos que cumplan alguna de las condiciones.

Todas las etiquetas -> resultado = scraper(data, "__todos__", "", "", "")
Todas las clases de una etiqueta -> resultado = scraper(data, "div", "__todos__", "", "")
Todos los atributos de una clase -> resultado = scraper(data, "div", "class", "__todos__", "")

En todos los casos anteriores podemos añadir un valor a "filtrar_texto" si queremos buscar los elementos que contengan una palabra que aparezca visible en la web, es decir, dentro de los elementos que estemos buscando. En el primer ejemplo: "XXX". Si queremos buscar el enlace del Buscador, podemos utilizar:

resultado = scraper(data, "a", "href", "enlace", "Buscador")
resultado = scraper(data, "__todos__, "", "", "", "Buscador")
...

-------------- Funciones extra --------------

Como extra, incluye la función "limpiar_tags", para devolver el contenido de un elemento de la lista sin etiquetas.
Esta función elimina también las etiquetas HTML sin cierre: "img", "br", "hr", "embed", etc.
