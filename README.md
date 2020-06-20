# Análisis de Reviews

## Autores

- Juan Pablo Gaviria Salazar
- Julian Daniel Florez Castrillon
- Yessica Henao Betancur
- Vladimir Arredondo Correa
- Javier Leomar Matamorros Villegas
- Alvaro Andres Castro Perez

## Objetivo

Realizar un análisis desde un enfoque de ciencia de datos sobre las reseñas escritas por usuarios del publico general acerca de un producto de entretenimiento, con el fin de detectar spam y review bombin y poder dar una calificación de un juego más inteligente que un promedio general.


## Extraccion de información

La primera fase del analisis realizado sobre las reviews de Metacritic es la extracción de información de Metacritic. El archivo extraccionMetacritic.py es el encargado de leer un archivo con las urls de los juegos a recolectar las reviews de los usuarios y descargar, página por página, todos los datos. Su salida es un archivo llamado trainingSet.csv, donde cada fila corresponde a una nueva review.

El formato que tiene que tener el archivo urls.csv es el siguiente:

- **Encabezado:** El encabezado debe tener las columnas ***url, status, paginasProcesadas, paginasTotales***.
- **Filas:** Cada fila debe de tener la url de reviews de usuarios seguido por tres comas que indican que los siguientes campos son vacios, por ejemplo: ***https://www.metacritic.com/game/pc/spore/user-reviews,,,***

Las columnas vacias **status, paginasProcesadas, paginasTotales** son se control para el script y guardan si la url ya fue procesada (status S para exitoso, F para fallido y P para parcial), las paginas que han sido procesadas (las reviews de los usuarios se guardan en paginaciones a partir de la página principal) y las páginas totales de reviews que tiene la url.

Adiconal a estos dos archivos, el script crea un archivo de control llamado **control.csv** donde se guardan todas las urls de paginaciones de cada juego y si su procesamiento fue exitoso o no. Este archivo se crea automaticamente y sirve para que, en caso de que falle el procesamiento de una url no se toque volver a procesar todas las demás.

Para la ejecución simplemente se ejecuta:

~~~ cmd
python extraccionMetacritic.py
~~~

El archivo de salida **trainingSet.csv** Tiene la siguiente estructura:

- **name:** Nombre de usuario que realizó la review
- **product:** Nombre del producto al que se realiza la review
- **platform:** Plataforma del producto
- **date:** Fecha en la que se realiza la review
- **rainting:** Calificación o puntaje asigando al producto por parte del usuario
- **upVotes:** Votos positivos de otros usuarios a la review
- **totVotes:** Votos totales de otros usuarios a la review
- **review:** Reseña escrita por el usuario acerca del producto
- **langReview:** Lenguaje en el que esta escrito la review
