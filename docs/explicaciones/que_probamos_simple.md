# Qué probamos, explicado simple (B73)

Texto para escuchar como audio (ElevenLabs, voz Roger). El audio no va al repo: está en Descargas como «Explicacion simple - que probamos.mp3».

El objetivo es armar un grafo: un mapa donde cada norma es un punto, y una flecha une dos normas cuando una modifica a la otra. Cada flecha guarda el pedazo de texto que la justifica.

Para armar esas flechas hay tres pasos. Primero, encontrar las citas: frases como «Ley 20.744» dentro del texto de cada norma. Segundo, saber a qué norma del corpus se refiere cada cita. Tercero, decidir si la cita es una modificación real o solo una mención al pasar. Ese tercer paso es el difícil, porque una norma puede nombrar a otra para cambiarla, o solo para recordar que existe.

Probamos cuatro formas de resolver ese tercer paso.

**1. Reglas.** Las escribimos nosotros: si la cita está en el articulado y al lado hay un verbo como «sustitúyese» o «derógase», es una modificación. Son rápidas, se entienden, y llegan a F1 = 0,83. El F1 es una nota de 0 a 1 que combina cuántas flechas acertamos y cuántas se nos escaparon.

**2. Random forest.** En vez de escribir reglas, le mostramos 800 ejemplos ya resueltos, con datos de cada cita: dónde aparece, cuántas veces, si la norma es un decreto. El modelo aprende solo qué combinaciones indican una modificación. Llegó a 0,82: empató con las reglas.

**3. TF-IDF con regresión logística.** Este modelo no mira datos sueltos, sino las palabras alrededor de la cita, y aprende qué palabras suelen acompañar a una modificación. Solo, llegó a cerca de 0,78. Usado como ayudante, donde las reglas deciden los casos claros y el modelo solo los dudosos, llegó a 0,84.

**4. Modelo de lenguaje (LLM).** Lee el fragmento y responde si hay modificación, de qué tipo y sobre qué artículo. Llegó a 0,84, y combinado con las reglas quedó parecido.

**¿Dónde se aplica cada uno?** Todos trabajan en el mismo lugar: el tercer paso. Las reglas y el LLM, además, dicen el tipo de modificación. El random forest y el TF-IDF solo dicen sí o no, así que usan las citas y los tipos que ya encontraron las reglas.

Ahora cada método tiene su grafo en Neo4j: las reglas, el LLM, los híbridos, el random forest y el TF-IDF. Se pueden comparar flecha por flecha.

**¿Qué aprendimos?** Que en este problema las reglas son una base muy fuerte. Que los modelos que aprenden empatan porque tienen pocos ejemplos, y la curva de aprendizaje muestra que mejorarían con más datos. Y que lo más difícil no es encontrar la cita, sino decidir si modifica o no, sobre todo cuando el texto no lo dice con todas las letras.
