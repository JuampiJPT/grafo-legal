# Narración nueva de la parte de modelos (E15 a E15g), para ElevenLabs

Reemplaza la escena E15 del video por siete escenas (bitácora B69). Usá la misma voz y la misma configuración que en el resto del video.

**Cómo generarla** (para no repetir el problema de B67):
- Generá **un audio por bloque**. Pegá **solo el texto** que está dentro de cada recuadro, sin el título.
- Descargá cada audio con el nombre de su escena: `E15.mp3`, `E15b.mp3`, `E15c.mp3`, `E15d.mp3`, `E15e.mp3`, `E15f.mp3` y `E15g.mp3`.
- Si querés, generá dos versiones de cada uno (`E15b_1.mp3`, `E15b_2.mp3`) y elijo la mejor.
- Dejalos en `Descargas/elevenlabs_modelos/`.

## E15 · Aprender de ejemplos

```
Hasta acá, las reglas las escribimos nosotros, a mano. <break time="0.5s" /> La otra forma es que la máquina las aprenda sola, a partir de ejemplos. Eso se llama aprendizaje supervisado. <break time="0.5s" /> Cada ejemplo es un par de normas que encontró el detector: la norma A menciona a la norma B. <break time="0.4s" /> Y cada par trae la respuesta correcta, que sacamos de InfoLEG: uno si la relación existe, cero si es una cita al pasar. <break time="0.5s" /> Para aprender usamos solo los pares de desarrollo: ochocientos uno, de doscientas treinta normas. Cuatrocientos setenta y dos son relaciones reales, y trescientos veintinueve no. <break time="0.5s" /> Con eso entrenamos dos modelos. Al modelo de lenguaje, en cambio, no lo entrenamos: solo le damos instrucciones.
```

## E15b · Primer modelo: el random forest

```
El primer modelo es un random forest, y se entiende mejor empezando por un solo árbol de decisión. <break time="0.5s" /> Un árbol es una cadena de preguntas sobre los veintidós atributos del par. Este es el primer árbol de nuestro bosque, tal cual lo aprendió. <break time="0.4s" /> Primero pregunta si la norma aparece en el VISTO. Después, si el origen es un decreto. Después, cuántas veces se la menciona. <break time="0.5s" /> El problema es que un árbol solo memoriza los datos con los que se entrenó. <break time="0.4s" /> Por eso entrenamos cuatrocientos árboles. Cada uno ve una muestra distinta de los pares y, en cada pregunta, solo algunos atributos. Así se equivocan de formas distintas, y al votar, los errores se compensan. <break time="0.5s" /> La probabilidad es el promedio de lo que vota cada árbol. Si pasa de cero coma cuarenta y cinco, el modelo dice que hay relación.
```

## E15c · Segundo modelo: leer el contexto

```
El segundo modelo no mira atributos: lee el texto. <break time="0.5s" /> De cada mención toma ciento cincuenta caracteres para cada lado. Reemplaza la norma mencionada por la palabra DESTINO y los dígitos por numerales, y le agrega en qué parte del documento está. <break time="0.4s" /> Así aprende la forma de la frase, y no el número de una ley en particular. <break time="0.5s" /> Después, con te efe i de efe, cada fragmento se vuelve un vector: cuánto aparece cada palabra y cada par de palabras, pesado por qué tan rara es. Son diez mil ochocientas columnas. <break time="0.5s" /> Encima, una regresión logística aprende un peso para cada una. <break time="0.4s" /> Estos son los pesos reales. Estar en el articulado y hablar de un artículo suma mucho. Reemplazado por, derogado o concordantes restan, porque son citas de procedencia. <break time="0.5s" /> Y también aprendió cosas sin sentido, como be ese a ese, que sale de la línea de la fecha, Buenos Aires. Eso es memorizar.
```

## E15d · Entrenar sin hacer trampa

```
Tan importante como el modelo es cómo se lo evalúa. <break time="0.5s" /> Primero: el test queda aparte. Son las normas posteriores a dos mil diecinueve, y se usan una sola vez, al final. <break time="0.5s" /> Segundo: para elegir el modelo, el umbral y la regularización, usamos validación cruzada en cinco partes, agrupada por norma. <break time="0.4s" /> Todos los pares de una misma norma quedan del mismo lado. Si no, el modelo reconocería la norma, y el resultado saldría inflado. <break time="0.5s" /> Tercero: comparamos tres modelos, regresión logística, random forest y gradient boosting, con umbrales de cero coma dos a cero coma ocho. Ganó el random forest. <break time="0.5s" /> Recién ahí se reentrena con todo desarrollo, y se mide en test.
```

## E15e · Qué resultados dieron

```
¿Y qué tal les fue? <break time="0.5s" /> El random forest llegó a un efe uno de cero coma ochenta y dos en test. Las reglas, a cero coma ochenta y tres. Empate. <break time="0.5s" /> El modelo que lee el contexto, solo, fue peor: entre cero coma setenta y seis y cero coma setenta y ocho. <break time="0.5s" /> Funcionó mejor como ayudante: las reglas deciden los casos claros, y el modelo solo la zona gris. Así llegó a cero coma ochenta y cuatro, pero esa diferencia no es significativa. <break time="0.6s" /> La pregunta que quedaba era por qué. ¿Al modelo le faltaba entender, o le faltaban datos?
```

## E15f · ¿Faltaban datos? La curva de aprendizaje

```
Para responderlo, hicimos una curva de aprendizaje. <break time="0.5s" /> Entrenamos los modelos con el diez, el veinte, el treinta, el cincuenta, el setenta y el cien por ciento de los datos, y los medimos siempre sobre la misma validación. <break time="0.5s" /> Si la curva se aplana, al modelo le falta entender. Si sigue subiendo, le faltan datos. <break time="0.5s" /> Y sigue subiendo. Las tres curvas ganan unos dos puntos cada vez que se duplican los datos, y recién al final alcanzan a las reglas. <break time="0.5s" /> Además, sobre los datos que ya vieron aciertan casi todo, y sobre los nuevos, bastante menos: memorizan. <break time="0.5s" /> Y había mucho más disponible. Usamos solo el uno coma cinco por ciento de las normas que InfoLEG podía etiquetar.
```

## E15g · Con más datos

Este bloque se completa cuando termine el reentrenamiento con el corpus ampliado (B69), porque lleva los resultados nuevos.
