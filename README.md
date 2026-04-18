1.  ¿Qué ventajas le proporciona a un proyecto el uso de un pipeline de CI? Menciona al menos tres ventajas *específicas* y explica por qué son importantes.
  - Permite detectar errores de integración de manera temprana, lo que reduce el tiempo y esfuerzo necesarios para corregirlos.
  - Facilita la colaboración entre desarrolladores al automatizar la construcción y pruebas del código.
  - Mejora la calidad del software al garantizar que cada cambio pase por un proceso de validación antes de ser integrado al código principal.

2.  ¿Cuál es la diferencia principal entre una prueba unitaria y una prueba de aceptación? Da un ejemplo de algo que probarías con una prueba unitaria y algo que probarías con una prueba de aceptación (en el contexto de cualquier aplicación que conozcas, descríbela primero).
- Una prueba unitaria se enfoca en verificar el correcto funcionamiento de una función o componente específico del código, mientras que una prueba de aceptación evalúa si el sistema cumple con los requisitos y expectativas del usuario final. Por ejemplo, en una aplicación de calculadora, una prueba unitaria podría verificar que la función de suma devuelve el resultado correcto para dos números dados, mientras que una prueba de aceptación podría validar que el usuario puede ingresar dos números y obtener el resultado correcto a través de la interfaz de usuario.
3.  Describe brevemente qué hace cada uno de los *steps* principales de tu workflow de GitHub Actions (desde el checkout hasta el push de Docker). Explica el propósito de cada uno **(qué hace y para qué se hace)**.
- Checkout: Este paso clona el repositorio en el runner de GitHub Actions para que el código esté disponible para los siguientes pasos.
- Setup Python: Configura el entorno de Python necesario para ejecutar las pruebas y construir la aplicación
- Install dependencies: Instala las dependencias necesarias para ejecutar las pruebas y construir la aplicación, asegurando que el entorno esté listo para el desarrollo.
- Run tests: Ejecuta las pruebas unitarias para validar que el código funciona correctamente antes de proceder con la construcción de la imagen Docker.
- Build Docker image: Construye una imagen Docker de la aplicación, lo que permite empaquetar el código y sus dependencias en un entorno aislado para su despliegue.
- Push Docker image: Sube la imagen Docker construida a un registro de contenedores (como Docker Hub), lo que facilita su distribución y despliegue en diferentes entornos.
4.  ¿Qué problemas o dificultades encontraste al implementar este taller? ¿Cómo los solucionaste? (Si no encontraste ningún problema, describe algo nuevo que hayas aprendido).
- Teniamos que acceptar algunos issues en SonarCloud que no eran tan relevantes para el proyecto
- El entorno del usuario cambió el formato de los archivos, lo que causó problemas con el pipeline. Para solucionarlo, tuvimos que apagar ese funcionamiento en el editor.
5.  ¿Qué ventajas ofrece empaquetar la aplicación en una imagen Docker al final del pipeline en lugar de simplemente validar el código?
- Empaquetar la aplicación en una imagen Docker permite garantizar que el entorno de ejecución sea consistente en diferentes máquinas y entornos, lo que facilita el despliegue y la escalabilidad de la aplicación. Además, las imágenes Docker pueden ser fácilmente compartidas y versionadas, lo que mejora la colaboración entre equipos y la gestión de dependencias.