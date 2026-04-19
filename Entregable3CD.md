# Taller Entregable 3: Despliegue Continuo (CD) con AWS ECS e Infraestructura como Código

Este taller es una continuación del Taller 2, donde construimos un pipeline de Integración Continua (CI) que genera una imagen Docker de nuestra aplicación. Ahora, nos enfocaremos en la **Entrega Continua (Continuous Delivery)** y el **Despliegue Continuo (Continuous Deployment)**, automatizando el despliegue de esa imagen Docker a **AWS Elastic Container Service (ECS)**, primero a un entorno de **Staging** y luego a **Producción**, utilizando **Infraestructura como Código (IaC)** con **Terraform**.

Te invito a que investigues un poco sobre estos servicios y conceptos antes de comenzar, ya que son fundamentales para el desarrollo moderno de software y la entrega continua.

Aquí algunos links útiles para ello:
* [AWS ECS](https://aws.amazon.com/ecs/)
* [Terraform](https://developer.hashicorp.com/terraform/docs)
* [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)

## Conceptos Previos
* **AWS CLI**: Interfaz de línea de comandos para interactuar con AWS. Permite gestionar recursos y servicios de AWS desde la terminal.
* **Terraform**: Herramienta de Infraestructura como Código (IaC) de HashiCorp que permite crear, modificar y eliminar recursos en múltiples proveedores cloud (AWS, Azure, GCP, etc.) mediante archivos de configuración declarativos escritos en HCL (HashiCorp Configuration Language).
* **Docker**: Plataforma para desarrollar, enviar y ejecutar aplicaciones en contenedores. Permite empaquetar aplicaciones y sus dependencias en un solo contenedor, asegurando que funcionen de manera consistente en diferentes entornos.

## Pre requisitos
* Haber finalizado el taller 2 y tener los artefactos desarrollados en ese taller (app, Dockerfile, tests, pipeline de CI, etc.).
* Instalar AWS CLI. Puedes seguir la guía oficial [aquí](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html).
* Instalar Terraform. Puedes seguir la guía oficial [aquí](https://developer.hashicorp.com/terraform/install). Verifica la instalación ejecutando `terraform --version` (debe retornar versión ≥ 1.6.0).
* Instalar Docker. Puedes seguir la guía oficial [aquí](https://docs.docker.com/get-docker/). Puedes omitir este paso si ya tienes Docker instalado y funcionando en tu máquina. Asegúrate de que Docker esté corriendo y que puedas ejecutar comandos de Docker desde la terminal. Puedes verificarlo ejecutando `docker --version`.
* Tener acceso a una cuenta de AWS:
  * Para este curso, les debió haber llegado en la(s) ultima(s) semanas un correo electrónico con asunto "Course Invitation" de AWS Academy. 
  ![alt text](images/e3-image-1.png)
  * Lo abren, hacen click en el botón "Get Started" y siguen las instrucciones para crear su cuenta de Canvas y AWS Academy.
  * Una vez tienen su cuenta creada, pueden ingresar usando el siguiente [link](https://www.awsacademy.com/vforcesite/LMS_Login), en el botón "Student Login" con su correo y contraseña.
  * Una vez ingresan, van a estar en el dashboard y deben hacer click en el curso llamado "AWS Academy Learning Lab".
  * Una vez dentro del curso, van a la sección "Modules" o "Modulos" y buscan el apartado "AWS Academy Learning Lab" y dan click en "Launch AWS Academy Learning Lab".
  ![alt text](images/e3-image-2.png)
  * Bajan hasta el final y aceptan los términos y condiciones "I agree".
  * Luego, les debe aparecer una consola como esta, allí deben dar click en "Start Lab" (aparecerá un icono de carga que puede tomar varios minutos). Esto les va a habilitar una cuenta de AWS con un presupuesto de $50 USD para que puedan hacer los ejercicios de este taller. Cada vez que dan "Start Lab" se inicia una sesión que dura 4 horas, al finalizarse la sesión se suspende la cuenta y su uso.
  ![alt text](images/e3-image-3.png)
  * Una vez el botón al lado de AWS (que estaba en rojo y durante el encendido estaba en amarillo) se pone en verde, pueden dar click en "AWS Details" para ver los detalles de su cuenta de AWS. Allí pueden dar click en `AWS CLI: Show` para ver sus credenciales de acceso programático (Access Key ID, Secret Access Key y Session Token) que necesitarán para configurar el AWS CLI. **¡Nunca compartas tus credenciales ni las subas a GitHub directamente!**. En la parte de abajo también pueden ver el ID y región de su cuenta de AWS, que es importante para la configuración del pipeline de GitHub Actions.
  ![alt text](images/e3-image-4.png)
  * Si dan click al botón de "AWS" en la parte superior, se abrirá una consola de AWS en una nueva pestaña. Allí pueden ver todos los servicios de AWS disponibles para su cuenta. **Recuerden que esta cuenta tiene un presupuesto limitado de $50 USD, así que deben tener cuidado con los recursos que crean y eliminarlos cuando terminen de usarlos.** En el taller no será necesario crear recursos manualmente, ya que todo se hará a través de Terraform y el pipeline de GitHub Actions. Sin embargo, si necesitan crear recursos manualmente o validar la creación de los recursos y la salud de los mismos, pueden hacerlo desde esta consola.
  * **¡MUY IMPORTANTE!**: Recuerden que esta cuenta de AWS es temporal y solo está disponible durante la duración del curso. No deben usarla para proyectos personales o producción. Al finalizar el curso, su cuenta será desactivada y perderán acceso a todos los recursos creados.

  *  **Características clave de la sesión y la cuenta de AWS:**

        1.  **Persistente:** Aunque tu sesión termine cuando el contador llegue a 0:00, todos los datos y recursos que hayas creado se guardarán. Al iniciar una nueva sesión (incluso otro día), encontrarás tu trabajo anterior.
        2.  **Estado de los Recursos al Terminar/Iniciar Sesión:**
            * **Instancias EC2:** Se detendrán al finalizar la sesión y se reiniciarán automáticamente la próxima vez que inicies una.
            * **Instancias de Notebook SageMaker:** Se detendrán, pero *no* se reiniciarán automáticamente en la siguiente sesión.
            * **Aplicaciones SageMaker Canvas:** Permanecerán activas a menos que las elimines manualmente.
        3.  **¡MUY IMPORTANTE: Presupuesto!**
            * Debes monitorear constantemente tu presupuesto restante en la interfaz del laboratorio.
            * Esta información del presupuesto se actualiza cada 8 a 12 horas, por lo que puede no reflejar tu gasto más reciente inmediatamente.
            * **Si excedes tu presupuesto, tu cuenta será desactivada y perderás TODO tu progreso y recursos.** Es fundamental que administres tus gastos para evitarlo.
            * Monitoriza tu gasto en la interfaz de Learner Lab. Usa los recursos mínimos sugeridos y considera **destruir la infraestructura con `terraform destroy`** después de validar el taller para ahorrar presupuesto.
        4. **Región:**
            * **SOLO** puedes usar las regiones `us-east-1` (N. Virginia) o `us-west-2` (Oregón) para todos tus recursos (CLI, secretos). Cualquier intento de usar otra región fallará.
            * **La región que utilizaremos en este taller es `us-east-1` (N. Virginia)**. Asegúrate de que tu configuración local (AWS CLI) y el pipeline de GitHub Actions estén configurados para esta región (ver sección 5.1).
        5. **Rol IAM `LabRole`:** No puedes crear roles IAM libremente. Debes usar el rol pre-creado `LabRole` donde sea necesario (especialmente en la configuración de tareas ECS). Los archivos de Terraform ya lo tienen en cuenta. Este rol tiene permisos limitados y no puedes modificarlo.


## 1. Conceptos de Entrega Continua y Despliegue Continuo (CD)

* **Entrega Continua (Continuous Delivery):** Práctica donde los cambios de código (empaquetados como artefactos, en nuestro caso, una imagen Docker) se construyen, prueban y preparan *automáticamente* para producción. La imagen se despliega automáticamente a un entorno de **Staging** (o pre-producción). La *liberación* a **Producción** requiere una **aprobación manual** o un trigger deliberado. El objetivo es tener *siempre* una versión validada lista para ir a producción rápidamente.
* **Despliegue Continuo (Continuous Deployment):** Va un paso más allá. *Cada cambio* (cada nueva imagen Docker) que pasa *todas* las etapas automatizadas (incluyendo pruebas en Staging) se despliega **automáticamente a Producción** sin intervención humana. Requiere una confianza extrema en la automatización y las pruebas. **Este es el enfoque que implementaremos principalmente en este taller.**

**Flujo de trabajo General:**

1.  **CI (Integración Continua):** Código -> Build -> Pruebas (Unit) -> Análisis -> **Imagen Docker (Artefacto)** -> Push a Docker Hub. (Cubierto en Taller 2).
2.  **CD (Este Taller - Deployment con Staging y Terraform):** Imagen Docker -> **Deploy Infra Staging (Terraform - Auto)** -> **Pruebas Aceptación en Staging (Auto)** -> **Deploy Infra Producción (Terraform - Auto)** -> **Pruebas Humo en Producción (Auto)** -> Monitoreo (Inherente en ECS).

## 2. Diferencias entre Continuous Deployment y Continuous Delivery

| Característica         | Continuous Delivery                      | Continuous Deployment                         |
| :--------------------- | :--------------------------------------- | :-------------------------------------------- |
| **Despliegue a Prod.** | Manual (requiere aprobación)             | Automático (sin intervención manual)          |
| **Frecuencia Despl.** | Controlada (puede ser frecuente)         | Muy frecuente (cada imagen validada)          |
| **Confianza Automat.** | Alta                                     | **Extrema** (requiere pruebas/monitoreo robustos) |
| **Velocidad (Lead Time)**| Más lento                                | Más rápido                                    |
| **Intervención Humana**| Sí (para liberar a Prod)                 | No (idealmente)                               |
| **Feedback Producción**| Retrasado por aprobación                   | Muy rápido (directamente de producción)       |

La elección depende del contexto. En este taller implementaremos un flujo de Despliegue Continuo utilizando AWS ECS y Terraform, introduciendo un entorno de Staging y un despliegue automático a Producción una vez validadas las pruebas en Staging.

## 3. Introducción a AWS y ECS

Para este taller, utilizaremos **Amazon Web Services (AWS)**, el proveedor líder de servicios en la nube. Específicamente, usaremos **Elastic Container Service (ECS)** para orquestar y ejecutar nuestros contenedores Docker. ECS es un servicio altamente escalable y de alto rendimiento que facilita la ejecución de aplicaciones en contenedores en AWS similar a Docker Swarm o Kubernetes.

**¿Por qué AWS ECS para este taller?**

* Es un servicio de orquestación de contenedores potente y ampliamente utilizado en la industria.
* Se integra nativamente con otros servicios de AWS (VPC, Load Balancing, IAM, CloudWatch).
* Ofrece opciones flexibles de cómputo (EC2 y Fargate). Usaremos **Fargate** para simplificar la gestión.
* Los créditos iniciales pueden cubrir los costos de este ejercicio si se usan recursos mínimos (instancias `nano` o configuraciones Fargate pequeñas).
* Nos permite implementar **Infraestructura como Código** usando Terraform.

## 4. CI/CD en Arquitecturas Modernas

### 4.1 Contenedores (Docker)

Los contenedores Docker son la base de nuestro despliegue. Como vimos en el Taller 2, empaquetan nuestra aplicación Flask y sus dependencias. Son consistentes, portátiles y permiten despliegues rápidos. La imagen generada en CI se subirá a Docker Hub y AWS ECS la descargará para ejecutarla.

**Ventajas clave para CD:**

* **Inmutabilidad:** Una vez construida, la imagen no cambia. Desplegamos la *misma* imagen en Staging y Producción, garantizando consistencia.
* **Portabilidad:** La imagen creada localmente o en CI se puede ejecutar en AWS ECS sin modificaciones.
* **Despliegue rápido:** Iniciar un contenedor es mucho más rápido que aprovisionar una VM.

**Docker en nuestro CI/CD con AWS:**

1.  **Dockerfile:** Definido en Taller 2.
2.  **Construcción y Push:** Realizado en el pipeline de CI (Taller 2), la imagen se almacena en Docker Hub.
3.  **Registro:** Usamos Docker Hub como nuestro registro de imágenes. AWS ECS descargará la imagen desde allí.
4.  **Despliegue en ECS:** El pipeline de CD le dirá a AWS ECS que descargue una versión específica de la imagen (identificada por su tag, ej: el SHA del commit) y la ejecute como un servicio.

### 4.2 Kubernetes (Alternativa a ECS)

Kubernetes (K8s) es otro potente orquestador de contenedores. Aunque no lo usaremos en este taller, es importante conocerlo como una alternativa a ECS, especialmente para escenarios multicloud o de mayor complejidad. AWS ofrece un servicio gestionado de Kubernetes llamado EKS (Elastic Kubernetes Service). Los conceptos de Pods, Services, Deployments son similares a los Task Definitions, Services y Load Balancers en ECS.

### 4.3 Serverless (Alternativa a Contenedores para ciertos casos)

Serverless, como AWS Lambda, es excelente para código basado en eventos o APIs simples. Para una aplicación web como la nuestra, que necesita estar ejecutándose constantemente para recibir peticiones HTTP, ECS (o K8s) suele ser más adecuado que una arquitectura puramente basada en funciones Lambda + API Gateway, aunque existen patrones híbridos.

## 5. AWS CLI (Command Line Interface)

La AWS CLI es una herramienta unificada para administrar tus servicios de AWS desde la línea de comandos. Es esencial para automatizar tareas e interactuar con AWS desde scripts o pipelines de CI/CD.

```bash
# Verifica la instalación de AWS CLI que realizaste en la sección de prerequisitos
aws --version
```

### 5.1 Configuración Local

Una vez instalado, necesitas configurar la CLI con tus credenciales de AWS. Desde AWS Academy copia todo el archivo de credenciales (Access Key ID, Secret Access Key y Session Token) tal y como se muestra en la consola de AWS Academy incluyendo el perfil `[default]`. 

Luego, busca el archivo de credenciales en tu máquina local (usualmente `~/.aws/credentials` en Linux/Mac o `C:\Users\<tu_usuario>\.aws\credentials` en Windows) y pega el contenido del archivo de credenciales que copiaste de AWS Academy.

Luego corre el comando `aws configure` en la terminal para configurar la CLI. Este comando te pedirá que ingreses tus credenciales de AWS (simplemente presiona Enter si ya las copiaste en el archivo de credenciales). Luego, te pedirá que ingreses la región y el formato de salida. Puedes dejar el formato de salida en blanco o elegir `json` y la región `us-east-1` (N. Virginia) como se mencionó anteriormente.

Finalmente, puedes probar si la configuración funciona correctamente ejecutando un comando simple como:
```bash
aws sts get-caller-identity
```

Te debe retornar información sobre tu identidad de AWS, algo similar a:
```json
{
    "UserId": "AIDAEXAMPLE",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/YourUserName"
}
```
Esto indica que la CLI está configurada correctamente y puede interactuar con tu cuenta de AWS.

### 5.2 Uso en el Pipeline

En nuestro pipeline de GitHub Actions, no usaremos `aws configure` interactivamente. En su lugar, utilizaremos una acción específica (`aws-actions/configure-aws-credentials`) que configura las credenciales de forma segura usando secretos almacenados en GitHub. Los comandos de Terraform (`terraform init`, `terraform apply`, `terraform output`) y de la AWS CLI (como `aws ecs update-service`) se ejecutarán directamente en los pasos del workflow después de configurar las credenciales.

**Ten en cuenta que las credenciales que setearemos en el pipeline de GitHub Actions son temporales** y solo tienen acceso a los recursos que les otorguemos. Esto es una buena práctica de seguridad, ya que minimiza el riesgo de exposición de credenciales permanentes.

**Al ser temporales quiere decir que tienen un tiempo de vida limitado usualmente de 1 a 4 horas. Esto significa que si pasa ese tiempo y queremos re ejecutar el pipeline, las credenciales ya no serán válidas y tendremos que volver a configurar las variables de entorno en los secretos de GitHub Actions para que el pipeline pueda acceder a los recursos de AWS nuevamente.**

## 6. Infraestructura como Código (IaC) con Terraform

**Infraestructura como Código (IaC)** es la práctica de gestionar infraestructura mediante código. Terraform es la herramienta de IaC open source de HashiCorp que permite modelar y aprovisionar recursos en múltiples proveedores cloud de forma segura y repetible usando archivos de configuración declarativos.

**Ventajas de Terraform:**

* **Declarativo:** Defines el estado deseado, Terraform se encarga de alcanzarlo.
* **Multi-cloud:** El mismo lenguaje (HCL) funciona con AWS, Azure, GCP y más de 1.000 proveedores.
* **Automatización y Consistencia:** Despliegues rápidos, repetibles y consistentes entre entornos.
* **Versionado:** Los archivos `.tf` se pueden versionar en Git.
* **Plan antes de aplicar:** `terraform plan` muestra exactamente qué va a cambiar *antes* de hacerlo, reduciendo el riesgo de cambios inesperados.
* **Gestión de Estado:** Mantiene el estado de la infraestructura y permite actualizaciones y eliminaciones controladas.

**Archivos de configuración de Terraform:**

* Son archivos de texto con extensión **`.tf`** escritos en HCL (HashiCorp Configuration Language).
* **Estructura Principal:**
    * `terraform {}`: Bloque de configuración del backend y los proveedores requeridos.
    * `provider "aws" {}`: Configuración del proveedor de AWS (región, credenciales).
    * `variable {}`: Valores de entrada para parametrizar la configuración (ej: nombre del entorno, ARN del rol, URI de la imagen).
    * `resource {}`: La definición de los recursos AWS a crear (ECS Cluster, Service, ALB, etc.). **Esta es la sección principal.**
    * `output {}`: Valores que se exponen después de aplicar la configuración (ej: URL del ALB).
* **Archivos que crearemos:**
    * `infra/variables.tf`: Declara los parámetros de entrada.
    * `infra/main.tf`: Define todos los recursos AWS.
    * `infra/outputs.tf`: Expone los valores de salida (URL del ALB, nombres del cluster y servicio).

**Consideraciones para Learner Lab:**

* **Permisos:** Terraform ejecutará las acciones usando las credenciales con las que se invoca (tu rol de Learner Lab). Como no tienes el permiso `iam:CreateRole`, **no podemos crear recursos de tipo `aws_iam_role`** en Terraform. Debemos referenciar el `LabRole` existente mediante un `data source`.
* **VPC por Defecto:** Para simplificar y evitar posibles problemas de permisos al crear VPCs/Subnets/Gateways, usaremos la **VPC por defecto** y sus **subredes públicas**. Deberás identificar los IDs de estas subredes en tu cuenta/región.
* **Estado de Terraform (`terraform.tfstate`):** Terraform guarda el estado de la infraestructura en un archivo local `terraform.tfstate`. **Este archivo nunca debe subirse a Git** (contiene información sensible). Agrégalo al `.gitignore`. En un entorno de producción real se usaría un backend remoto (S3 + DynamoDB), pero para este laboratorio trabajaremos con estado local.

## 7. Implementación del Pipeline CD con Staging y Producción en AWS ECS usando Terraform

1.  **Asegúrate de que el código de la aplicación y las pruebas estén listos:**

    * **`app/app.py`**:
        * Debe usar un puerto configurable: `app_port = int(os.environ.get("PORT", 5000))` (ECS suele inyectar la variable `PORT`). Gunicorn en el Dockerfile ya expone el puerto 8000.
        * Debe tener `debug=False`.
        * **Debe tener configurado el `secret_key` para Flask-WTF (CSRF).** Flask-WTF requiere un `secret_key` para generar tokens CSRF. En ECS el contenedor no tiene acceso a archivos locales ni a variables que no se le pasen explícitamente. Terraform inyectará la variable de entorno `FLASK_SECRET_KEY` al contenedor (ver paso 4 y 8).
            * **Si tu `app.py` usa `app.config.from_prefixed_env()`** (la forma recomendada): no necesitas ninguna línea adicional. Flask lee automáticamente `FLASK_SECRET_KEY` del entorno y lo mapea a `app.secret_key`.
            * **Si tu `app.py` NO usa `from_prefixed_env()`**: añade esta línea después de crear la instancia `app`:
            ```python
            app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-only-insecure-key")
            ```
            El valor de fallback `"dev-only-insecure-key"` solo sirve para desarrollo local. En ECS se usará el valor del secreto `SECRET_KEY` de GitHub Actions, que Terraform inyectará al contenedor como `FLASK_SECRET_KEY`.
        * Debe incluir el endpoint `/health`:
            ```python
            @app.route("/health")
            def health():
                return "OK", 200
            ```
            Este endpoint es importante para el **health check** del ALB. El ALB enviará peticiones a este endpoint para verificar que la aplicación esté viva y respondiendo. Si no responde o devuelve un error, el ALB considerará que la tarea está fallando y tomará las acciones necesarias (como reiniciar la tarea (contenedor) o redirigir el tráfico a otra instancia).
    * **Pruebas de Aceptación (`tests/test_acceptance_app.py`):**
        * Asegúrate de que este archivo exista (creado en Taller 2).
        * Verifica que la `BASE_URL` se lea desde una variable de entorno `APP_BASE_URL` que luego estableceremos en el pipeline para apuntar al ALB de Staging.
        * Un ALB es un balanceador de carga que distribuye el tráfico entre múltiples instancias de tu aplicación. En este caso dichas instancias son los contenedores de ECS que ejecutan tu aplicación Flask. El ALB se encargará de enrutar las peticiones HTTP a los contenedores disponibles, asegurando alta disponibilidad y escalabilidad.
            ```python
            # Ejemplo en tests/test_acceptance_app.py
            import os
            # ... otros imports ...
            BASE_URL = os.environ.get("APP_BASE_URL", "http://localhost:5000") # La variable APP_BASE_URL se inyectará en el pipeline con la URL del ALB de Staging.
            # ...
            def test_calculadora(browser, num1, num2, operacion, resultado_esperado):
                 browser.get(BASE_URL + "/") # Asegúrate que usa la variable
                 # ... resto de la prueba ...
            ```
    * **Pruebas de Humo (`tests/test_smoke_app.py`):**
        * **Crea este archivo nuevo en la carpeta `tests/`** con el siguiente contenido:
            ```python
            # tests/test_smoke_app.py
            import os
            from selenium.webdriver.common.by import By
            from selenium import webdriver
            import pytest

            # Fixture para configurar el navegador (similar a las pruebas de aceptación)
            @pytest.fixture
            def browser():
                options = webdriver.ChromeOptions()
                options.add_argument("--headless")  # Ejecuta sin interfaz gráfica
                options.add_argument("--no-sandbox") # Necesario para algunos entornos
                options.add_argument("--disable-dev-shm-usage") # Necesario para algunos entornos
                driver = webdriver.Chrome(options=options)
                yield driver
                driver.quit()

            def test_smoke_test(browser):
                """SMOKE TEST: Verifica carga básica y título."""
                # Lee la URL de producción desde una variable de entorno
                app_url = os.environ.get("APP_BASE_URL", "http://localhost:5000") # Usar la variable de entorno APP_BASE_URL que inyectaremos en el pipeline con la URL del ALB de Producción
                print(f"Smoke test ejecutándose contra: {app_url}") # Imprime para depuración
                try:
                    browser.get(app_url + "/")
                    print(f"Título de la página: {browser.title}")
                    assert "Calculadora" in browser.title # Verifica que el título contenga "Calculadora"
                    h1_element = browser.find_element(By.TAG_NAME, "h1")
                    print(f"Texto H1: {h1_element.text}")
                    assert h1_element.text == "Calculadora" # Verifica el texto del H1
                    print("Smoke test pasado exitosamente.")
                except Exception as e:
                    print(f"Smoke test falló: {e}")
                    # Opcional: tomar captura de pantalla si falla
                    # browser.save_screenshot('smoke_test_failure.png')
                    raise # Vuelve a lanzar la excepción para que pytest marque el test como fallido
            ```
        * Esta prueba verifica la carga básica de la página principal y el título en el entorno de **Producción**. Utiliza la variable de entorno `APP_BASE_URL` que configuraremos en el pipeline para apuntar al ALB de Producción.

        * **`.github/workflows/ci.yml`**:
            * Modifica el archivo `ci.yml` para excluir de las pruebas unitarias el archivo `tests/test_smoke_app.py` (ya que no queremos ejecutar pruebas de humo en Staging). Puedes hacerlo agregando un filtro en el paso de pruebas unitarias:
            ```yaml
            - name: Run Unit Tests with pytest and Coverage
              run: |
                pytest --ignore=tests/test_acceptance_app.py  --ignore=tests/test_smoke_app.py
            ```

3.  **Identifica Recursos de la VPC por Defecto y ARN de LabRole:**
    * **ARN de LabRole:**
        * Ve a la consola de AWS en la barra de búsqueda escribe `IAM` y selecciona el servicio IAM, luego haz clic en `Roles` en el menú de la izquierda.
        * Busca el rol llamado `LabRole`.
        * Haz clic en él y copia su **ARN** (ej: `arn:aws:iam::123456789012:role/LabRole`). **Lo necesitarás.**
    * **ID de la VPC por Defecto:**
        * Ve a la consola de AWS en la barra de búsqueda escribe `VPC` y selecciona el servicio VPC. Luego haz clic en `Your VPCs` en el menú de la izquierda.
        * Copia el **ID** de la VPC por defecto (ej: `vpc-zzzzzzzzzzzzzzzzz`). **Lo necesitarás.**
    * **IDs de Subredes Públicas por Defecto:**
        * Ve a la consola de AWS en la barra de búsqueda escribe `VPC` y selecciona el servicio VPC. Luego haz clic en `Subnets` en el menú de la izquierda.
        * Identifica al menos **dos** subredes en diferentes Zonas de Disponibilidad dentro de esa VPC por defecto. Verifica que sus tablas de rutas asociadas tengan una ruta `0.0.0.0/0` apuntando a un Internet Gateway (`igw-...`). Estas son tus subredes públicas.
        * Copia los **IDs** de estas subredes (ej: `subnet-xxxxxxxxxxxxxxxxx`, `subnet-yyyyyyyyyyyyyyyyy`). **Los necesitarás.**

4.  **Crea los archivos de Terraform en la carpeta `infra/`:**
    * Crea una carpeta llamada `infra/` en la raíz de tu repositorio.
    * Dentro de ella, crea los tres archivos siguientes. Lee los comentarios cuidadosamente.

**`infra/variables.tf`**

```hcl
# infra/variables.tf

variable "environment_name" {
  description = "Nombre del entorno (ej: staging, production). Usado para nombrar recursos."
  type        = string
  validation {
    condition     = contains(["staging", "production"], var.environment_name)
    error_message = "El entorno debe ser 'staging' o 'production'."
  }
}

variable "docker_image_uri" {
  description = "URI completo de la imagen Docker a desplegar (ej: usuario/repo:tag)."
  type        = string
}

variable "lab_role_arn" {
  description = "ARN completo del rol IAM 'LabRole' existente en la cuenta."
  type        = string
}

variable "vpc_id" {
  description = "ID de la VPC por defecto donde desplegar."
  type        = string
}

variable "subnet_ids" {
  description = "Lista de al menos DOS IDs de subredes públicas de la VPC por defecto en diferentes AZs."
  type        = list(string)
}

variable "aws_region" {
  description = "Región de AWS a usar."
  type        = string
  default     = "us-east-1"
}

variable "secret_key" {
  description = "Clave secreta para Flask (usada por flask-wtf para tokens CSRF). Nunca se imprime en logs gracias a sensitive = true."
  type        = string
  sensitive   = true
  default     = "dev-only-insecure-key"
}
```

**`infra/main.tf`**

```hcl
# infra/main.tf

terraform {
  required_version = ">= 1.6.0"
  backend "s3" {}

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# --- Grupo de Logs para ECS ---
resource "aws_cloudwatch_log_group" "ecs_logs" {
  name              = "/ecs/calculadora-${var.environment_name}-task"
  retention_in_days = 7

  tags = {
    Environment = var.environment_name
  }
}

# --- Cluster ECS ---
resource "aws_ecs_cluster" "main" {
  name = "calculadora-${var.environment_name}-cluster"

  tags = {
    Environment = var.environment_name
  }
}

# --- Seguridad ---
# Security Group para el Load Balancer (permite HTTP desde internet)
resource "aws_security_group" "alb_sg" {
  name        = "alb-sg-${var.environment_name}"
  description = "Permite trafico HTTP al ALB"
  vpc_id      = var.vpc_id

  ingress {
    description = "HTTP desde internet"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Environment = var.environment_name
  }
}

# Security Group para el Servicio ECS (permite trafico desde el ALB en el puerto 8000)
resource "aws_security_group" "ecs_sg" {
  name        = "ecs-service-sg-${var.environment_name}"
  description = "Permite trafico desde el ALB al servicio ECS"
  vpc_id      = var.vpc_id

  ingress {
    description     = "Trafico desde el ALB"
    from_port       = 8000 # Puerto del contenedor
    to_port         = 8000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb_sg.id] # Solo permite desde el ALB SG
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Environment = var.environment_name
  }
}

# --- Load Balancer ---
resource "aws_lb" "main" {
  name               = "calculadora-${var.environment_name}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb_sg.id]
  subnets            = var.subnet_ids # Debe estar en subredes publicas

  tags = {
    Environment = var.environment_name
  }
}

# Target Group para las tareas ECS
resource "aws_lb_target_group" "ecs_tg" {
  name        = "tg-ecs-${var.environment_name}"
  port        = 8000 # Puerto del contenedor
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "ip" # Necesario para Fargate

  health_check {
    enabled             = true
    path                = "/health" # Endpoint de health check de la app
    port                = "8000"    # Puerto del contenedor
    protocol            = "HTTP"
    healthy_threshold   = 2
    unhealthy_threshold = 2
    interval            = 15
    timeout             = 5
    matcher             = "200"
  }

  tags = {
    Environment = var.environment_name
  }
}

# Listener HTTP en el puerto 80
resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.ecs_tg.arn
  }
}

# --- Definición de Tarea ECS ---
resource "aws_ecs_task_definition" "app" {
  family                   = "calculadora-${var.environment_name}-task"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "256"  # 0.25 vCPU (minimo Fargate)
  memory                   = "512"  # 0.5 GB (minimo Fargate)
  task_role_arn            = var.lab_role_arn       # Rol para permisos DENTRO del contenedor
  execution_role_arn       = var.lab_role_arn       # Rol para que ECS/Fargate pueda descargar imagen, enviar logs, etc.

  container_definitions = jsonencode([
    {
      name  = "calculadora-${var.environment_name}-container"
      image = var.docker_image_uri # Imagen de Docker Hub

      portMappings = [
        {
          containerPort = 8000
          protocol      = "tcp"
        }
      ]

      # Variable de entorno inyectada al contenedor: clave secreta para Flask-WTF (CSRF).
      # El prefijo FLASK_ hace que from_prefixed_env() la recoja automáticamente como app.secret_key.
      environment = [
        {
          name  = "FLASK_SECRET_KEY"
          value = var.secret_key
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.ecs_logs.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  ])

  tags = {
    Environment = var.environment_name
  }
}

# --- Servicio ECS ---
resource "aws_ecs_service" "main" {
  name            = "calculadora-${var.environment_name}-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.app.arn
  desired_count   = 1 # Numero inicial de tareas
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = var.subnet_ids # Las mismas subredes publicas del ALB
    security_groups  = [aws_security_group.ecs_sg.id]
    assign_public_ip = true # Necesario en subredes publicas sin NAT Gateway
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.ecs_tg.arn
    container_name   = "calculadora-${var.environment_name}-container"
    container_port   = 8000
  }

  deployment_minimum_healthy_percent = 50  # Permite que baje al 50% durante el deploy
  deployment_maximum_percent         = 200 # Permite que suba al 200% temporalmente

  # Ignorar desired_count para permitir ajustes manuales sin reescribirlos en cada apply.
  lifecycle {
    ignore_changes = [desired_count]
  }

  depends_on = [aws_lb_listener.http] # Asegura que el listener exista antes de crear el servicio

  tags = {
    Environment = var.environment_name
  }
}
```

**`infra/outputs.tf`**

```hcl
# infra/outputs.tf

output "alb_dns_name" {
  description = "DNS Name del Application Load Balancer"
  value       = aws_lb.main.dns_name
}

output "alb_url" {
  description = "URL completa del ALB (con http://)"
  value       = "http://${aws_lb.main.dns_name}/"
}

output "ecs_cluster_name" {
  description = "Nombre del ECS Cluster"
  value       = aws_ecs_cluster.main.name
}

output "ecs_service_name" {
  description = "Nombre del ECS Service"
  value       = aws_ecs_service.main.name
}
```

**Agrega Terraform al `.gitignore`:**

```bash
# Agrega estas líneas al .gitignore de tu repositorio
# Terraform
infra/.terraform/
infra/.terraform.lock.hcl
infra/terraform.tfstate
infra/terraform.tfstate.backup
infra/terraform.tfstate.d/
infra/*.tfvars
```

> **Nota:** la carpeta `terraform.tfstate.d/` es donde Terraform guarda los archivos de estado de cada workspace (staging/production). Nunca la subas a Git, ya que contiene información sensible de tu infraestructura.

5. **Versiona los cambios en tu repositorio:**

    ```bash
    git add .
    git commit -m "Ajustes código, pruebas de humo y archivos Terraform"
    git push origin main
    ```

6. **Asegurate de que el pipeline de CI actual corra bien y llegue hasta desplegar la nueva imágen Docker en Docker Hub.**
    * Verifica que la imagen se haya subido correctamente a Docker Hub. Ve a tu repositorio de Docker Hub y verifica que la imagen `cicd-pipeline-python` esté disponible con el tag `latest` (o el SHA del commit) y que el **last pushed sea reciente**.

    * Esto es importante porque esta nueva versión de la imágen Docker será la que usaremos en el despliegue de Terraform para Staging y Producción. Si no se subió correctamente, el despliegue fallará o nunca finalizará por que no encontrará el health check del ALB lo que hará que el servicio ECS no esté disponible.

    * Si el pipeline no corre bien, corrige los defectos, pruebas unitarias y demás hasta que llegue a la etapa de subir la imagen Docker a Docker Hub. **No continúes hasta que el pipeline corra bien y suba la imagen Docker.**

7.  **Despliega la Infraestructura Inicialmente (Manual con Terraform):**
    * Asegúrate de tener la AWS CLI configurada.
    * Navega a la carpeta `infra/` de tu repositorio.
    * Reemplaza todos los placeholders `<...>` con tus valores reales antes de ejecutar los comandos.
    * Comandos a utilizar:
      * **`terraform init`**: Descarga los plugins del proveedor de AWS. Solo es necesario ejecutarlo una vez (o cuando se cambia la versión del proveedor).
      * **`terraform workspace new <nombre>`**: Crea un workspace nuevo con estado aislado. Cada workspace tiene su propio `terraform.tfstate` guardado en `terraform.tfstate.d/<nombre>/`.
      * **`terraform apply -auto-approve`**: Crea o actualiza los recursos definidos en los archivos `.tf`. El flag `-auto-approve` evita la confirmación interactiva.
      * **`terraform output`**: Muestra los valores definidos en `outputs.tf`, como la URL del ALB, el nombre del cluster y el nombre del servicio ECS.


      > **¿Por qué usar Terraform Workspaces?**
      > Terraform guarda el estado de tu infraestructura en un archivo local `terraform.tfstate`. Si ejecutas `terraform apply` dos veces en la misma carpeta (una para staging y otra para producción), el segundo `apply` **sobreescribe** el estado del primero, destruyendo los recursos de staging o mezclando ambos entornos. Para evitar esto, usamos **Terraform Workspaces**: cada workspace mantiene su propio archivo de estado aislado, lo que permite gestionar staging y producción de forma completamente independiente desde la misma carpeta.
    ---

    **Paso 1 — Navegar a la carpeta de Terraform e inicializar:**

    ```bash
    cd infra/
    ```

    **Temporalmente comenta en `main.tf` la línea `backend "s3" {}` para que use estado local y no intente conectarse a un bucket S3 que no existe. Esto es solo para esta sección de despliegue manual, luego lo descomentaremos para el pipeline.**

    ```bash
    # Descarga el provider de AWS (solo la primera vez, o cuando cambia la versión del provider)
    terraform init
    ```

    ---

    **Paso 2 — Crear workspace y desplegar Staging:**

    ```bash
    # Crea el workspace de staging y actívalo
    terraform workspace new staging
    ```

    > Si el workspace ya existe (por ejemplo, en un segundo intento), usa `terraform workspace select staging` en lugar de `new`.

    > **`secret_key` en el apply manual:** La variable `secret_key` tiene un valor por defecto (`"dev-only-insecure-key"`) definido en `variables.tf`, así que no es necesario pasarla explícitamente durante la validación local. En el pipeline de GitHub Actions, el valor real se inyecta automáticamente desde el secreto `SECRET_KEY` de GitHub, que Terraform pasa al contenedor como la variable de entorno `FLASK_SECRET_KEY`.

    **Recuerda reemplazar las variables `<TU_USUARIO_DOCKERHUB>`, `<ARN_COMPLETO_DE_TU_LABROLE>`, `<ID_DE_TU_VPC_POR_DEFECTO>`, `<ID_SUBNET_PUBLICA_1>`, `<ID_SUBNET_PUBLICA_2>` con tus valores reales antes de ejecutar el siguiente comando.**

    **Linux / Mac:**
    ```bash
    terraform apply \
      -var="environment_name=staging" \
      -var="docker_image_uri=dpletzke/cicd-pipeline-python:latest" \
      -var="lab_role_arn=arn:aws:iam::900125261172:role/LabRole" \
      -var="vpc_id=vpc-097e66b6b8d074810" \
      -var='subnet_ids=["subnet-009c1a27ce36602eb","subnet-031fb189dd14cb09b"]' \
      -auto-approve
    ```

    **Windows (PowerShell):**
    ```powershell
    # El prefijo --% le indica a PowerShell que pase el resto de argumentos literalmente,
    # lo que evita problemas con las comillas en la lista de subnets.
    terraform --% apply -var="environment_name=staging" -var="docker_image_uri=<TU_USUARIO_DOCKERHUB>/cicd-pipeline-python:latest" -var="lab_role_arn=<ARN_COMPLETO_DE_TU_LABROLE>" -var="vpc_id=<ID_DE_TU_VPC_POR_DEFECTO>" -var="subnet_ids=[\"<ID_SUBNET_PUBLICA_1>\",\"<ID_SUBNET_PUBLICA_2>\"]" -auto-approve
    ```

    ```bash
    # Obtén y anota los valores de salida de Staging (URLs del ALB, nombres del cluster y servicio)
    terraform output
    ```

    ---

    **Paso 3 — Crear workspace y desplegar Producción:**

    ```bash
    # Crea el workspace de producción y actívalo
    terraform workspace new production
    ```

    > Si el workspace ya existe, usa `terraform workspace select production`.

    **Linux / Mac:**
    ```bash
    terraform apply \
      -var="environment_name=production" \
      -var="docker_image_uri=<TU_USUARIO_DOCKERHUB>/cicd-pipeline-python:latest" \
      -var="lab_role_arn=<ARN_COMPLETO_DE_TU_LABROLE>" \
      -var="vpc_id=<ID_DE_TU_VPC_POR_DEFECTO>" \
      -var='subnet_ids=["<ID_SUBNET_PUBLICA_1>","<ID_SUBNET_PUBLICA_2>"]' \
      -auto-approve
    ```

    **Windows (PowerShell):**
    ```powershell
    terraform --% apply -var="environment_name=production" -var="docker_image_uri=<TU_USUARIO_DOCKERHUB>/cicd-pipeline-python:latest" -var="lab_role_arn=<ARN_COMPLETO_DE_TU_LABROLE>" -var="vpc_id=<ID_DE_TU_VPC_POR_DEFECTO>" -var="subnet_ids=[\"<ID_SUBNET_PUBLICA_1>\",\"<ID_SUBNET_PUBLICA_2>\"]" -auto-approve
    ```

    ```bash
    # Obtén y anota los valores de salida de Producción
    terraform output
    ```

    ---

    **Paso 4 — Verificación y Troubleshooting:**

    * **Verifica la creación de la infraestructura en la Consola:** Ve a la consola de AWS, busca los servicios `ECS` y `EC2 > Load Balancers` y confirma que los recursos de staging y producción se hayan creado correctamente. Deberías ver **dos clusters ECS** (`calculadora-staging-cluster` y `calculadora-production-cluster`) y **dos ALBs**.
    * **Obtén las Salidas:** Anota las URLs de los ALBs, los nombres de los Clusters y los nombres de los Servicios de la salida de `terraform output` de cada workspace.
    * **Valida el despliegue correcto de la imágen Docker en Staging:** Abre la URL del ALB de Staging en tu navegador (valor `alb_url` del output de Staging, ej: `http://calculadora-staging-alb-xxxxxx.us-east-1.elb.amazonaws.com/`) y verifica que la página cargue correctamente. Si no, sigue la guía de troubleshooting a continuación.
    * **Valida el despliegue correcto de la imágen Docker en Producción:** Repite el paso anterior con la URL del ALB de Producción.

    > **Troubleshooting: Problemas al desplegar la infraestructura**
    >
    > Los problemas se presentan en dos escenarios distintos. Identifica cuál es el tuyo y sigue los pasos correspondientes.
    >
    > ---
    >
    > **Escenario A — El servicio muestra "0 of 1 task running" y el deployment lleva varios minutos "in progress" sin tareas activas ni logs en CloudWatch**
    >
    > Esto significa que las tareas ni siquiera llegan a arrancar — el contenedor nunca se inicia. CloudWatch no tiene logs porque no hay nada que registrar aún.
    >
    > **A.1. Lee los eventos del servicio ECS — este es el primer lugar a revisar:**
    > - Ve a **ECS → Clusters → tu cluster → Services → clic en el nombre del servicio → pestaña `Events`**.
    > - **Importante:** NO uses "Event History" (esa pestaña requiere Container Insights y en el Learner Lab mostrará el error `Log group does not exist` — es un error esperado, no la causa de tu problema). La pestaña que necesitas es simplemente `Events`, dentro de la vista del servicio.
    > - En `Events` verás mensajes del scheduler de ECS como `service X was unable to place a task` o `ResourceInitializationError`. Ese mensaje te dirá exactamente qué está fallando.
    >
    > **A.2. Verifica si las subnets son verdaderamente públicas (causa más frecuente):**
    > - Fargate con `assign_public_ip = true` necesita que la subnet tenga una ruta hacia Internet para poder descargar la imagen de Docker Hub. Si la tabla de rutas de la subnet no tiene una entrada `0.0.0.0/0 → igw-xxx`, la tarea nunca podrá descargar la imagen y fallará silenciosamente.
    > - Ve a **VPC → Subnets** → selecciona cada subnet que usaste en `subnet_ids` → pestaña `Route table` → verifica que exista una ruta `0.0.0.0/0` apuntando a un Internet Gateway (`igw-...`).
    > - Si no existe esa ruta, no son subnets públicas. Elige otras subnets que sí la tengan y vuelve a ejecutar `terraform apply` con los nuevos IDs.
    >
    > **A.3. Verifica el URI exacto de la imagen Docker:**
    > - El valor que pasaste en `-var="docker_image_uri=..."` debe coincidir exactamente con lo que está en Docker Hub (usuario, nombre de repo y tag).
    > - Ve a [hub.docker.com](https://hub.docker.com), ingresa a tu repositorio y confirma que la imagen existe con ese tag exacto. Si el tag es `:latest`, asegúrate de que el pipeline de CI haya hecho push recientemente.
    >
    > **A.4. Verifica que el ARN pasado en `lab_role_arn` sea el del `LabRole` y no el de tu rol SSO:**
    > - Si en la pestaña `Events` del servicio ves el mensaje `ECS was unable to assume the role 'arn:aws:iam::...:role/aws-reserved/sso.amazonaws.com/AWSReservedSSO_...'`, significa que pasaste el ARN de tu rol de inicio de sesión SSO en lugar del `LabRole`. Son roles diferentes:
    >   - **Correcto:** `arn:aws:iam::<ACCOUNT_ID>:role/LabRole`
    >   - **Incorrecto:** `arn:aws:iam::<ACCOUNT_ID>:role/aws-reserved/sso.amazonaws.com/AWSReservedSSO_...`
    > - El ARN SSO es el que aparece en la sección `AWS Details` de la consola del Learner Lab como tu identidad de usuario. **No es el rol para las tareas ECS.**
    > - Para corregirlo: ve a **IAM → Roles** → busca `LabRole` → copia su ARN → vuelve a ejecutar `terraform apply` en cada workspace con el ARN correcto. No necesitas hacer destroy primero; Terraform actualizará los recursos existentes.
    >
    > ---
    >
    > **Escenario B — El servicio tiene tareas corriendo pero el navegador muestra "503 Service Temporarily Unavailable"**
    >
    > Esto significa que las tareas están corriendo pero los contenedores no pasan el health check del ALB.
    >
    > **B.1. Espera 1–2 minutos y recarga.** El ALB necesita al menos 30–60 s para registrar los primeros targets. Si sigue en 503 después de 2 minutos, continúa.
    >
    > **B.2. Verifica el estado del Target Group:**
    > - Ve a **EC2 → Load Balancing → Target Groups** → selecciona el TG de staging (`tg-ecs-staging`) → pestaña **Targets**.
    > - Si el estado es `unhealthy`, el contenedor está corriendo pero la app no responde en `/health` en el puerto 8000.
    > - **Causa más común:** la imagen desplegada no tiene el endpoint `/health` en `app/app.py`. Asegúrate de haberlo agregado (paso 7.1 de este taller), de que el pipeline de CI haya subido la nueva imagen a Docker Hub con tag `:latest`, y luego re-ejecuta el `terraform apply` del workspace correcto.
    >
    > **B.3. Revisa los logs del contenedor en CloudWatch:**
    > - Ve a **CloudWatch → Log groups** → `/ecs/calculadora-staging-task` → abre el log stream más reciente.
    > - Si ves `Address already in use` o un error de importación de Python, hay un bug en el código de la app.
    >
    > **B.4. Verifica los Security Groups:**
    > - El Security Group de ECS (`ecs-service-sg-staging`) debe permitir tráfico TCP en el puerto **8000** desde el Security Group del ALB (`alb-sg-staging`). Terraform lo crea automáticamente; si lo modificaste manualmente, restáuralo.

    ---

    **Paso 5 — Limpieza:**

    **Finalmente, destruye la infraestructura manualmente:** Si todo está bien, destruye la infraestructura de cada workspace antes de que el pipeline la recree automáticamente. Asegúrate de estar en el workspace correcto antes de cada destroy:

    ```bash
    # Destruir Staging
    terraform workspace select staging
    ```

    **Linux / Mac:**
    ```bash
    terraform apply -destroy \
      -var="environment_name=staging" \
      -var="docker_image_uri=<TU_USUARIO_DOCKERHUB>/cicd-pipeline-python:latest" \
      -var="lab_role_arn=<ARN_COMPLETO_DE_TU_LABROLE>" \
      -var="vpc_id=<ID_DE_TU_VPC_POR_DEFECTO>" \
      -var='subnet_ids=["<ID_SUBNET_PUBLICA_1>","<ID_SUBNET_PUBLICA_2>"]' \
      -auto-approve
    ```

    **Windows (PowerShell):**
    ```powershell
    terraform --% apply -destroy -var="environment_name=staging" -var="docker_image_uri=<TU_USUARIO_DOCKERHUB>/cicd-pipeline-python:latest" -var="lab_role_arn=<ARN_COMPLETO_DE_TU_LABROLE>" -var="vpc_id=<ID_DE_TU_VPC_POR_DEFECTO>" -var="subnet_ids=[\"<ID_SUBNET_PUBLICA_1>\",\"<ID_SUBNET_PUBLICA_2>\"]" -auto-approve
    ```

    ```bash
    # Destruir Producción
    terraform workspace select production
    ```

    **Linux / Mac:**
    ```bash
    terraform apply -destroy \
      -var="environment_name=production" \
      -var="docker_image_uri=<TU_USUARIO_DOCKERHUB>/cicd-pipeline-python:latest" \
      -var="lab_role_arn=<ARN_COMPLETO_DE_TU_LABROLE>" \
      -var="vpc_id=<ID_DE_TU_VPC_POR_DEFECTO>" \
      -var='subnet_ids=["<ID_SUBNET_PUBLICA_1>","<ID_SUBNET_PUBLICA_2>"]' \
      -auto-approve
    ```

    **Windows (PowerShell):**
    ```powershell
    terraform --% apply -destroy -var="environment_name=production" -var="docker_image_uri=<TU_USUARIO_DOCKERHUB>/cicd-pipeline-python:latest" -var="lab_role_arn=<ARN_COMPLETO_DE_TU_LABROLE>" -var="vpc_id=<ID_DE_TU_VPC_POR_DEFECTO>" -var="subnet_ids=[\"<ID_SUBNET_PUBLICA_1>\",\"<ID_SUBNET_PUBLICA_2>\"]" -auto-approve
    ```

    **Recuerda que en los siguientes pasos es el pipeline quién los volverá a crear automáticamente y ES NECESARIO QUE LOS DESTRUYAS ANTES DE CONTINUAR.**

    **RECUERDA también descomentar la sección `backend "s3" {}` en `main.tf` para que el pipeline use el backend remoto en S3.**

8.  **Crea los secretos y variables en GitHub:**
    * Antes de hacer lo siguiente, reinicia la sesión de AWS Academy (stop y start) para que se generen nuevas credenciales temporales. Esto es importante porque los secretos de GitHub Actions usarán estas credenciales para interactuar con AWS y Docker Hub (**recuerda que son temporales y tienen un tiempo de vida limitado**).
    * Ve a tu repositorio en GitHub -> **Settings -> Secrets and variables -> Actions**.

    **Secretos** (`New repository secret`) — valores sensibles que GitHub cifra y nunca muestra en logs:
      * `AWS_ACCESS_KEY_ID`: Tu AWS Access Key ID.
      * `AWS_SECRET_ACCESS_KEY`: Tu AWS Secret Access Key.
      * `AWS_SESSION_TOKEN`: Tu AWS Session Token.
      * `DOCKERHUB_TOKEN`: Tu token de Docker Hub. Si estás trabajando el mismo repositorio del taller 2, no es necesario, ya lo tienes creado.
      * `SONAR_TOKEN`: Tu token de SonarCloud. Si estás trabajando el mismo repositorio del taller 2, no es necesario, ya lo tienes creado.
      * **`SECRET_KEY`**: Una cadena aleatoria y segura que Flask usará como clave secreta para los tokens CSRF (ej: cualquier cadena larga de caracteres aleatorios). **Nunca uses un valor simple como `secret` o `password`.**

    **Variables** (pestaña `Variables` → `New repository variable`) — valores de configuración no sensibles, visibles en los logs:
      * `DOCKERHUB_USERNAME`: Tu usuario de Docker Hub. Si estás trabajando el mismo repositorio del taller 2, no es necesario, ya lo tienes creado.
      * `SONAR_HOST_URL`: `https://sonarcloud.io`. Si estás trabajando el mismo repositorio del taller 2, no es necesario, ya lo tienes creado.
      * **`LAB_ROLE_ARN`**: El ARN completo de tu `LabRole`.
      * **`VPC_ID`**: El ID de tu VPC por defecto.
      * **`SUBNET_IDS`**: Los IDs de tus dos subredes públicas, separados por coma (ej: `subnet-xxx,subnet-yyy`).
      * **`TF_STATE_BUCKET`**: El nombre del bucket de S3 donde se almacenará el estado de Terraform (debe ser una cadena de texto sin espacios ni caracteres especiales, sólo letras, números y guiones). Recuerda que los buckets de S3 tienen un namespace global, así que elige un nombre único (ej: `mi-estado-terraform-12345`, modificando el `12345` por tus iniciales o un número aleatorio para que sea único).

    > **¿Por qué separar secretos de variables?** Los **secretos** están cifrados y nunca aparecen en los logs del pipeline. Las **variables** son visibles — son datos de configuración que no representan un riesgo si alguien los ve (un ARN, un ID de VPC o un usuario de Docker Hub no permiten acceso a los recursos por sí solos).

9.  **Renombra y modifica el archivo `.github/workflows/ci.yml` por `.github/workflows/ci-cd.yml`:**

    Renombra el archivo `.github/workflows/ci.yml` por `.github/workflows/ci-cd.yml` y modifica su contenido para que quede como el siguiente. **Asegúrate de que los nombres de los secretos y variables para las pruebas coincidan con los que creaste en el paso anterior y en el ajuste del código.**

```yaml
# Nombre del Workflow
name: CI/CD Pipeline AWS ECS con Terraform

# Disparadores del Workflow
on:
  push:
    branches:
      - main # Se ejecuta en push a la rama main
  pull_request:
    branches:
      - main # Se ejecuta en pull requests hacia main
  workflow_dispatch: # Permite ejecución manual desde la UI de GitHub Actions

# Definición de los trabajos (Jobs)
jobs:
  # -------------------------------------
  # Job de CI (Build, Test, Publish Docker Image)
  # -------------------------------------
  build-test-publish:
    runs-on: ubuntu-latest # Runner a utilizar
    outputs:
      repo_name: ${{ steps.set_outputs.outputs.repo_name }}
      image_tag: ${{ steps.set_outputs.outputs.image_tag }}

    steps:
      # 1. Checkout del código del repositorio
      - name: Checkout code
        uses: actions/checkout@v4

      # 2. Configurar el entorno de Python
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12' # Especificar versión de Python

      # 3. Instalar dependencias de Python
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt # Instalar paquetes listados en requirements.txt

      # 4. Ejecutar Black (Formateador de código) en modo chequeo
      - name: Run Black (Formatter)
        run: black app --check

      # 5. Ejecutar Pylint (Linter) y guardar reporte
      - name: Run Pylint (Linter)
        run: pylint app --output-format=text --fail-under=9 > pylint-report.txt || true # Continúa aunque falle Pylint (para Sonar)

      # 6. Ejecutar Flake8 (Linter) y guardar reporte
      - name: Run Flake8 (Linter)
        run: flake8 app --output-file=flake8-report.txt || true # Continúa aunque falle Flake8 (para Sonar)

      # 7. Ejecutar Pruebas Unitarias con Pytest y generar reporte de cobertura
      - name: Run Unit Tests with pytest and Coverage
        run: |
          # Ejecuta solo pruebas unitarias, excluyendo aceptación y humo
          pytest --ignore=tests/test_acceptance_app.py  --ignore=tests/test_smoke_app.py  # Genera un informe XML para SonarCloud

      # SE ELIMINAN DEL JOB DE CI EL PASO DE ACCEPTANCE TESTS, PASA AL JOB DE CD.

      # 7.1. Cargar reportes de cobertura y pruebas unitarias como artefactos
      - name: Upload Test Reports Artifacts
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: test-reports
          path: |
            htmlcov/
            report.html

      # 9. Ejecutar análisis con SonarCloud
      - name: SonarCloud Scan
        uses: SonarSource/sonarqube-scan-action@v5.0.0
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}  # Automáticamente proporcionado
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}   # El secreto que creaste

      # --- Pasos de Docker (solo en push a main) ---

      # 9. Configurar QEMU (para buildx multi-plataforma, aunque no lo usemos explícitamente)
      - name: Set up QEMU
        if: github.event_name == 'push' && github.ref == 'refs/heads/main'
        uses: docker/setup-qemu-action@v3

      # 10. Configurar Docker Buildx (constructor avanzado)
      - name: Set up Docker Buildx
        if: github.event_name == 'push' && github.ref == 'refs/heads/main'
        uses: docker/setup-buildx-action@v3

      # 11. Iniciar sesión en Docker Hub
      - name: Login to Docker Hub
        if: github.event_name == 'push' && github.ref == 'refs/heads/main'
        uses: docker/login-action@v3
        with:
          username: ${{ vars.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      # 12. Construir y pushear imagen Docker a Docker Hub
      - name: Build and push Docker image
        id: docker_build_push # Darle ID para referenciar output
        if: github.event_name == 'push' && github.ref == 'refs/heads/main'
        uses: docker/build-push-action@v5
        with:
          context: .
          file: ./Dockerfile
          push: true
          tags: |
            ${{ vars.DOCKERHUB_USERNAME }}/${{ github.event.repository.name }}:${{ github.sha }}
            ${{ vars.DOCKERHUB_USERNAME }}/${{ github.event.repository.name }}:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max

      # 13. Establecer las salidas del job usadas para el despliegue
      - name: Set Job Outputs
        id: set_outputs
        if: github.event_name == 'push' && github.ref == 'refs/heads/main'
        run: |
          echo "repo_name=${{ github.event.repository.name }}" >> $GITHUB_OUTPUT
          echo "image_tag=${{ github.sha }}" >> $GITHUB_OUTPUT


  # -------------------------------------
  # Job de Despliegue Terraform Staging
  # -------------------------------------
  deploy-tf-staging:
    needs: build-test-publish # Depende del job anterior (necesita image_uri)
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main' # Solo en push a main
    outputs:
      alb_url_staging: ${{ steps.get_tf_outputs.outputs.alb_url }}
      cluster_name_staging: "calculadora-staging-cluster"
      service_name_staging: "calculadora-staging-service"

    steps:
      # 1. Checkout del código (para acceder a los archivos de Terraform)
      - name: Checkout code
        uses: actions/checkout@v4

      # 2. Configurar credenciales de AWS (CON SESSION TOKEN)
      - name: Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-session-token: ${{ secrets.AWS_SESSION_TOKEN }} # <--- USO DEL SESSION TOKEN
          aws-region: us-east-1

      # 3. Crear el bucket del estado remoto si no existe
      - name: Ensure Terraform State Bucket
        run: |
          if [ -z "${{ vars.TF_STATE_BUCKET }}" ]; then
            echo "Error: Debes definir la variable del repositorio TF_STATE_BUCKET."
            exit 1
          fi

          if aws s3api head-bucket --bucket "${{ vars.TF_STATE_BUCKET }}" 2>/dev/null; then
            echo "El bucket de estado ya existe."
          else
            echo "Creando bucket de estado ${{ vars.TF_STATE_BUCKET }}..."
            aws s3api create-bucket --bucket "${{ vars.TF_STATE_BUCKET }}" --region us-east-1
          fi

          aws s3api put-bucket-versioning \
            --bucket "${{ vars.TF_STATE_BUCKET }}" \
            --versioning-configuration Status=Enabled

      # 4. Configurar Terraform
      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: "~1.6"
          terraform_wrapper: false # Necesario para capturar outputs correctamente

      # 5. Inicializar Terraform usando estado remoto en S3
      - name: Terraform Init (Staging)
        working-directory: infra
        run: |
          terraform init -reconfigure \
            -backend-config="bucket=${{ vars.TF_STATE_BUCKET }}" \
            -backend-config="key=staging/terraform.tfstate" \
            -backend-config="region=us-east-1"

      # 6. Desplegar/Actualizar la infraestructura de Staging con Terraform
      - name: Terraform Apply (Staging)
        working-directory: infra
        env:
          TF_VAR_environment_name: staging
          TF_VAR_lab_role_arn: ${{ vars.LAB_ROLE_ARN }}
          TF_VAR_vpc_id: ${{ vars.VPC_ID }}
          TF_VAR_secret_key: ${{ secrets.SECRET_KEY }}
        run: |
          # Reconstruir la URI de la imagen usando la variable y las salidas separadas
          IMAGE_URI="${{ vars.DOCKERHUB_USERNAME }}/${{ needs.build-test-publish.outputs.repo_name }}:${{ needs.build-test-publish.outputs.image_tag }}"
          echo "Deploying Image URI: $IMAGE_URI"

          # Convertir "subnet-xxx,subnet-yyy" en ["subnet-xxx","subnet-yyy"] para Terraform
          SUBNET_LIST=$(echo "${{ vars.SUBNET_IDS }}" | \
            awk -F',' '{printf "["; for(i=1;i<=NF;i++){printf "\"%s\"%s",$i,(i<NF?",":"")}; printf "]"}')

          terraform apply -auto-approve \
            -var="docker_image_uri=${IMAGE_URI}" \
            -var="subnet_ids=${SUBNET_LIST}"

      # 7. Obtener las salidas de Terraform (Staging)
      - name: Get Terraform Outputs (Staging)
        id: get_tf_outputs
        working-directory: infra
        run: |
          ALB_URL=$(terraform output -raw alb_url)

          if [ -z "$ALB_URL" ]; then
            echo "Error: No se pudo obtener alb_url de Terraform (Staging)."
            exit 1
          fi

          echo "ALB URL Staging: $ALB_URL"
          echo "alb_url=${ALB_URL}" >> $GITHUB_OUTPUT

  # -------------------------------------
  # Job de Actualización Servicio Staging (ECS - Forzar despliegue)
  # -------------------------------------
  update-service-staging:
    # Depende de que Terraform haya actualizado la Task Definition
    needs: [build-test-publish, deploy-tf-staging]
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'

    steps:
      # 1. Configurar credenciales de AWS (CON SESSION TOKEN)
      - name: Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-session-token: ${{ secrets.AWS_SESSION_TOKEN }} # <--- USO DEL SESSION TOKEN
          aws-region: us-east-1

      # 2. Forzar un nuevo despliegue en el servicio ECS de Staging
      - name: Force New Deployment ECS Service Staging
        run: |
          echo "Forcing new deployment for Staging service..."
          aws ecs update-service --cluster ${{ needs.deploy-tf-staging.outputs.cluster_name_staging }} \
                                --service ${{ needs.deploy-tf-staging.outputs.service_name_staging }} \
                                --force-new-deployment \
                                --region us-east-1
          # Esperar a que el despliegue se estabilice
          echo "Waiting for Staging service deployment to stabilize..."
          aws ecs wait services-stable --cluster ${{ needs.deploy-tf-staging.outputs.cluster_name_staging }} --services ${{ needs.deploy-tf-staging.outputs.service_name_staging }} --region us-east-1
          echo "Staging service deployment stable."

  # -------------------------------------
  # Job de Pruebas de Aceptación en Staging
  # -------------------------------------
  test-staging:
    needs: [update-service-staging, deploy-tf-staging] # Depende de que el servicio esté estable con la nueva versión
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'

    steps:
      # 1. Checkout del código (para acceder a las pruebas)
      - name: Checkout code
        uses: actions/checkout@v4

      # 2. Configurar Python
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      # 3. Instalar dependencias de prueba
      - name: Install test dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt # Incluye selenium, pytest

      # 4. Ejecutar pruebas de aceptación contra el entorno de Staging
      - name: Run Acceptance Tests against Staging
        env:
          APP_BASE_URL: ${{ needs.deploy-tf-staging.outputs.alb_url_staging }} # URL del ALB de Staging desde salidas de Terraform
        run: |
          echo "Running acceptance tests against: $APP_BASE_URL"
          sleep 30 # Espera prudencial para el registro del target en el ALB
          pytest tests/test_acceptance_app.py # Ejecutar las pruebas de aceptación

  # -------------------------------------
  # Job de Despliegue Terraform Producción
  # -------------------------------------
  deploy-tf-prod:
    needs: [build-test-publish, test-staging] # Depende de la imagen y de que Staging esté OK
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    outputs: # Definir salida para la URL del ALB de producción
      alb_url_prod: ${{ steps.get_tf_outputs.outputs.alb_url }}
      cluster_name_prod: "calculadora-production-cluster"
      service_name_prod: "calculadora-production-service"

    steps:
      # 1. Checkout del código
      - name: Checkout code
        uses: actions/checkout@v4

      # 2. Configurar credenciales de AWS (CON SESSION TOKEN)
      - name: Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-session-token: ${{ secrets.AWS_SESSION_TOKEN }} # <--- USO DEL SESSION TOKEN
          aws-region: us-east-1

      # 3. Crear el bucket del estado remoto si no existe
      - name: Ensure Terraform State Bucket
        run: |
          if [ -z "${{ vars.TF_STATE_BUCKET }}" ]; then
            echo "Error: Debes definir la variable del repositorio TF_STATE_BUCKET."
            exit 1
          fi

          if aws s3api head-bucket --bucket "${{ vars.TF_STATE_BUCKET }}" 2>/dev/null; then
            echo "El bucket de estado ya existe."
          else
            echo "Creando bucket de estado ${{ vars.TF_STATE_BUCKET }}..."
            aws s3api create-bucket --bucket "${{ vars.TF_STATE_BUCKET }}" --region us-east-1
          fi

          aws s3api put-bucket-versioning \
            --bucket "${{ vars.TF_STATE_BUCKET }}" \
            --versioning-configuration Status=Enabled

      # 4. Configurar Terraform
      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: "~1.6"
          terraform_wrapper: false # Necesario para capturar outputs correctamente

      # 5. Inicializar Terraform usando estado remoto en S3
      - name: Terraform Init (Production)
        working-directory: infra
        run: |
          terraform init -reconfigure \
            -backend-config="bucket=${{ vars.TF_STATE_BUCKET }}" \
            -backend-config="key=production/terraform.tfstate" \
            -backend-config="region=us-east-1"

      # 6. Desplegar/Actualizar la infraestructura de Producción con Terraform
      - name: Terraform Apply (Production)
        working-directory: infra
        env:
          TF_VAR_environment_name: production
          TF_VAR_lab_role_arn: ${{ vars.LAB_ROLE_ARN }}
          TF_VAR_vpc_id: ${{ vars.VPC_ID }}
          TF_VAR_secret_key: ${{ secrets.SECRET_KEY }}
        run: |
          # Reconstruir la URI de la imagen usando la variable y las salidas separadas
          IMAGE_URI="${{ vars.DOCKERHUB_USERNAME }}/${{ needs.build-test-publish.outputs.repo_name }}:${{ needs.build-test-publish.outputs.image_tag }}"
          echo "Deploying Image URI: $IMAGE_URI"

          # Convertir "subnet-xxx,subnet-yyy" en ["subnet-xxx","subnet-yyy"] para Terraform
          SUBNET_LIST=$(echo "${{ vars.SUBNET_IDS }}" | \
            awk -F',' '{printf "["; for(i=1;i<=NF;i++){printf "\"%s\"%s",$i,(i<NF?",":"")}; printf "]"}')

          terraform apply -auto-approve \
            -var="docker_image_uri=${IMAGE_URI}" \
            -var="subnet_ids=${SUBNET_LIST}"

      # 7. Obtener las salidas de Terraform (Producción)
      - name: Get Terraform Outputs (Production)
        id: get_tf_outputs
        working-directory: infra
        run: |
          ALB_URL=$(terraform output -raw alb_url)

          if [ -z "$ALB_URL" ]; then
            echo "Error: No se pudo obtener alb_url de Terraform (Production)."
            exit 1
          fi

          echo "ALB URL Production: $ALB_URL"
          echo "alb_url=${ALB_URL}" >> $GITHUB_OUTPUT

  # -------------------------------------
  # Job de Actualización Servicio Producción (ECS - Forzar despliegue)
  # -------------------------------------
  update-service-prod:
    needs: [build-test-publish, deploy-tf-prod] # Depende de que Terraform haya actualizado la Task Def de Prod
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'

    steps:
      # 1. Configurar credenciales de AWS (CON SESSION TOKEN)
      - name: Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-session-token: ${{ secrets.AWS_SESSION_TOKEN }} # <--- USO DEL SESSION TOKEN
          aws-region: us-east-1

      # 2. Forzar un nuevo despliegue en el servicio ECS de Producción
      - name: Force New Deployment ECS Service Production
        run: |
          echo "Forcing new deployment for Production service..."
          aws ecs update-service --cluster ${{ needs.deploy-tf-prod.outputs.cluster_name_prod }} \
                                --service ${{ needs.deploy-tf-prod.outputs.service_name_prod }} \
                                --force-new-deployment \
                                --region us-east-1
          # Esperar a que el despliegue se estabilice
          echo "Waiting for Production service deployment to stabilize..."
          aws ecs wait services-stable --cluster ${{ needs.deploy-tf-prod.outputs.cluster_name_prod }} --services ${{ needs.deploy-tf-prod.outputs.service_name_prod }} --region us-east-1
          echo "Production service deployment stable."

  # -------------------------------------
  # Job de Pruebas de Humo en Producción
  # -------------------------------------
  smoke-test-prod:
    needs: [update-service-prod, deploy-tf-prod] # Depende de que el servicio de prod esté estable
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'

    steps:
      # 1. Checkout del código
      - name: Checkout code
        uses: actions/checkout@v4

      # 2. Configurar Python
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      # 3. Instalar dependencias de prueba
      - name: Install test dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      # 4. Ejecutar pruebas de humo contra el entorno de Producción
      - name: Run Smoke Tests against Production
        env:
          APP_BASE_URL: ${{ needs.deploy-tf-prod.outputs.alb_url_prod }} # URL del ALB de Producción desde salidas de Terraform
        run: |
          echo "Running smoke tests against: $APP_BASE_URL"
          sleep 30 # Espera prudencial
          pytest tests/test_smoke_app.py # Ejecutar las pruebas de humo
```

10.  **Sube los cambios a GitHub:**
    * Asegúrate de tener la carpeta `infra/` con los tres archivos Terraform y `.github/workflows/ci-cd.yml` actualizados.
      ```bash
        git add .
        git commit -m "CICD complete pipeline with IaC in AWS ECS using Terraform"
        git push origin main
        ```

11. **Verifica el despliegue:**
    * Ve a la pestaña "Actions" de tu repositorio. El workflow debería ejecutarse.
    * Monitoriza la ejecución. Los jobs `deploy-tf-*` ejecutarán `terraform apply`. Puedes ver el progreso detallado en los logs del job.
    * Los jobs `update-service-*` forzarán el despliegue de la nueva imagen en ECS.
    * Verifica que las pruebas de aceptación y humo pasen contra las URLs de los ALBs correctos.
    * Accede a las URLs de los ALBs de Staging y Producción para probar la aplicación manualmente (puedes ver las URL en las salidas de los jobs `deploy-tf-*` en el paso de "Get Terraform Outputs"). Abre las URLs en tu navegador (ej: `http://calculadora-staging-alb-xxxxxx.us-east-1.elb.amazonaws.com/` o similar para Staging y `http://calculadora-production-alb-xxxxxx.us-east-1.elb.amazonaws.com/` o similar para Producción) y verifica que la página cargue correctamente.

12. **Validación:**
    * Asegúrate de que el pipeline CI/CD con Terraform funcione correctamente.
    * Verifica los despliegues en Staging y Producción.
    * Confirma que el health check `/health` funcione y los Target Groups estén saludables. Desde la consola de AWS, busca `EC2` en la barra de búsqueda y luego ve a `Target Groups` en el menú de la izquierda (en la sección de Load Balancing). Selecciona ambos Target Groups que corresponden a tu servicios de ECS en Staging y Producción y ve a la pestaña `Targets`. Allí deberías ver los targets con estado `healthy` (saludables). Si no, revisa los logs de ECS en CloudWatch para identificar problemas.
    * Valida que las pruebas de aceptación y humo pasen.
    * Asegúrate de no tener hallazgos de calidad/seguridad (SonarCloud, linters).
    * Asegúrate de tener una cobertura de pruebas unitarias de al menos un 80%.

13. **Incluye nuevas funcionalidades a la calculadora:**
    Incluye al menos 2 funciones adicionales en tu aplicación de la calculadora (ej: potencia, módulo, etc.) y asegúrate de que las pruebas unitarias y de aceptación cubran estas nuevas funciones. Esto te ayudará a practicar la integración continua y la entrega continua, asegurando que tu aplicación esté siempre lista para producción.

    Tras incluir estas funciones deberías poder ver que el pipeline de CI/CD funciona correctamente y si pasan todas las pruebas, la aplicación debería estar disponible en Staging y Producción con las nuevas funciones.

14. **Validación final:**
    * Repite TODAS las validaciones del numeral 12. Todas serán tenidas en cuenta en la evaluación y entrega de este taller.

## 8. Monitoreo y Health Checks en AWS ECS (con Terraform)

Los Health Checks son una parte crucial de la infraestructura de AWS ECS y ALB, estos se realizan de manera automática a la ruta `/health` de la aplicación. En este taller, hemos configurado los Health Checks en el Target Group de ECS (en el archivo `infra/main.tf`) para asegurarnos de que las instancias de la aplicación estén saludables y disponibles para recibir tráfico.

Si el ECS o ALB no pueden acceder a la ruta `/health` intentarán reiniciar automáticamente las instancias. Si el problema persiste, el Target Group marcará las instancias como `unhealthy` y no recibirán tráfico. Esto es esencial para garantizar que solo las instancias saludables manejen las solicitudes de los usuarios.

## 9. Entregable

### 9.1. Responde las preguntas y documenta los despliegues en tu README.md

Abre el archivo `README.md` de tu repositorio y añade:

**a) Las URLs de los ALBs obtenidas del `terraform output` de cada entorno:**
```
Staging ALB URL:    http://calculadora-staging-alb-xxxxxx.us-east-1.elb.amazonaws.com/
Production ALB URL: http://calculadora-production-alb-xxxxxx.us-east-1.elb.amazonaws.com/
```
> Estas URLs son evidencia del despliegue. Aunque la infraestructura se destruya después, el historial del README y del workflow quedan como registro.

**b) Las respuestas a las siguientes preguntas** (con formato libre: subtítulos, párrafos, listas, etc.):

1.  Explica brevemente el flujo de trabajo **nuevo** completo que implementaste con **Terraform** (commit -> CI -> Build/Push Imagen -> Deploy TF Staging -> Update Service Staging -> Test Staging -> Deploy TF Prod -> Update Service Prod -> Smoke Test Prod). Sé *específico* sobre *qué artefacto se mueve, qué hace cada job principal, y qué valida cada tipo de prueba*.
2.  ¿Qué ventajas y desventajas encontraste al usar Terraform o infraestructura como código en vez de desplegar manualmente? ¿Qué te pareció definir la infraestructura en HCL?
3.  ¿Qué ventajas y desventajas tiene introducir un entorno de Staging en el pipeline de despliegue a AWS? ¿Cómo impacta esto la velocidad vs. la seguridad del despliegue?
4.  ¿Qué diferencia hay entre las pruebas ejecutadas contra Staging (`test-staging`) y las ejecutadas contra Producción (`smoke-test-production`) en tu pipeline? ¿Por qué esta diferencia?
5.  Considerando un ciclo completo de DevOps, ¿qué partes importantes (fases, herramientas, prácticas) crees que aún le faltan a este pipeline de CI/CD que has construido? (Menciona 2, explica por qué son importantes y cómo podrían implementarse brevemente).
6.  ¿Cómo te pareció implementar dos funcionalidades nuevas? ¿Qué tal fue tu experiencia? ¿Encontraste útil implementar CI/CD a la hora de realizar cambios y despliegues? ¿Por qué? ¿Qué no fue tan útil?

Haz commit y push del README actualizado:

```bash
git add README.md
git commit -m "Agregar respuestas y URLs del despliegue al README"
git push origin main
```

### 9.2. Entrega

Ingresa al buzón del **Entregable 3** en **EAFIT Interactiva** y proporciona los siguientes tres datos en el campo de texto:

1.  **URL del repositorio de GitHub** (debe ser público): `https://github.com/TU_USUARIO/cicd-pipeline-python`
2.  **URL del proyecto en SonarCloud** (debe ser público, accesible sin login): `https://sonarcloud.io/project/overview?id=TU_USUARIO_cicd-pipeline-python`
3.  **Nombre de la imagen en Docker Hub** (debe ser público): `tunombredeusuario/cicd-pipeline-python`

> Antes de entregar, verifica en una pestaña de incógnito que:
> - El repositorio de GitHub es accesible sin iniciar sesión.
> - La URL de SonarCloud muestra el proyecto con Quality Gate `Passed` sin necesidad de login.
> - La imagen existe en Docker Hub con la etiqueta `latest`.

**Criterios de evaluación:**

* Repositorio GitHub público con todos los archivos requeridos (`ci-cd.yml`, carpeta `infra/`, `test_smoke_app.py`, etc.).
* Carpeta `infra/` con los tres archivos Terraform (`main.tf`, `variables.tf`, `outputs.tf`) presentes y con el `AUTOR` reemplazado en `app/calculadora.py`.
* Ejecución completa y exitosa de **todos** los jobs del workflow `ci-cd.yml` (build -> staging -> test -> production -> smoke).
* Proyecto en SonarCloud público con Quality Gate `Passed` y cobertura ≥ 80%.
* Imagen en Docker Hub pública con etiquetas `latest` y SHA.
* Al menos 2 nuevas funciones en `calculadora.py` con pruebas unitarias y de aceptación que las cubran.
* URLs de ALB Staging y Producción documentadas en el `README.md`.
* Respuestas a las 6 preguntas incluidas en el `README.md`.

**RECUERDA QUE TANTO TU REPOSITORIO GITHUB COMO TU PROYECTO EN SONARCLOUD Y TU IMAGEN EN DOCKER HUB DEBEN SER PÚBLICOS O NO SE PODRÁN CALIFICAR**

## 10. Eliminación de recursos para evitar cargos adicionales

Una vez hayas terminado el taller, realizado la entrega en EAFIT Interactiva y confirmado que ya no necesitas volver a desplegar, elimina todos los recursos para evitar consumo innecesario del presupuesto de AWS Academy.

> **Importante:** si vuelves a hacer `push` a `main` o ejecutas manualmente el workflow `ci-cd.yml`, GitHub Actions puede recrear la infraestructura. Haz esta limpieza al final del todo, cuando ya no necesites más despliegues.

### 10.1 Destruye la infraestructura creada por el pipeline

En la validación **manual/local** del paso 7 trabajaste con **Terraform workspaces**. Pero en el pipeline `ci-cd.yml` la separación entre entornos se hace de otra forma: usando el mismo bucket S3 y una **`key` distinta por entorno** (`staging/terraform.tfstate` y `production/terraform.tfstate`).

Por eso, para eliminar específicamente lo que creó el pipeline, aquí **no debes usar `terraform workspace select`**. Debes reinicializar Terraform apuntando a la `key` correcta del estado remoto y luego ejecutar `terraform destroy` para ese entorno.

Ubícate en la carpeta `infra/` de tu repositorio. Si abriste una sesión nueva de AWS Academy, vuelve a configurar tus credenciales temporales antes de destruir:

```bash
cd infra/
```

Destruye primero Staging y luego Producción. Reemplaza los placeholders `<...>` con tus valores reales.

**Inicializa Terraform apuntando al estado remoto de Staging:**

**Linux / Mac:**
```bash
terraform init \
  -reconfigure \
  -backend-config="bucket=<TF_STATE_BUCKET>" \
  -backend-config="key=staging/terraform.tfstate" \
  -backend-config="region=us-east-1" \
  -backend-config="use_lockfile=true"
```

**Windows (PowerShell):**
```powershell
terraform init -reconfigure -backend-config="bucket=<TF_STATE_BUCKET>" -backend-config="key=staging/terraform.tfstate" -backend-config="region=us-east-1" -backend-config="use_lockfile=true"
```

**Linux / Mac:**
```bash
terraform destroy \
  -var="environment_name=staging" \
  -var="docker_image_uri=<TU_USUARIO_DOCKERHUB>/cicd-pipeline-python:latest" \
  -var="lab_role_arn=<ARN_COMPLETO_DE_TU_LABROLE>" \
  -var="vpc_id=<ID_DE_TU_VPC_POR_DEFECTO>" \
  -var='subnet_ids=["<ID_SUBNET_PUBLICA_1>","<ID_SUBNET_PUBLICA_2>"]' \
  -auto-approve
```

**Windows (PowerShell):**
```powershell
terraform --% destroy -var="environment_name=staging" -var="docker_image_uri=<TU_USUARIO_DOCKERHUB>/cicd-pipeline-python:latest" -var="lab_role_arn=<ARN_COMPLETO_DE_TU_LABROLE>" -var="vpc_id=<ID_DE_TU_VPC_POR_DEFECTO>" -var="subnet_ids=[\"<ID_SUBNET_PUBLICA_1>\",\"<ID_SUBNET_PUBLICA_2>\"]" -auto-approve
```

**Inicializa Terraform apuntando al estado remoto de Producción:**

**Linux / Mac:**
```bash
terraform init \
  -reconfigure \
  -backend-config="bucket=<TF_STATE_BUCKET>" \
  -backend-config="key=production/terraform.tfstate" \
  -backend-config="region=us-east-1" \
  -backend-config="use_lockfile=true"
```

**Windows (PowerShell):**
```powershell
terraform init -reconfigure -backend-config="bucket=<TF_STATE_BUCKET>" -backend-config="key=production/terraform.tfstate" -backend-config="region=us-east-1" -backend-config="use_lockfile=true"
```

**Linux / Mac:**
```bash
terraform destroy \
  -var="environment_name=production" \
  -var="docker_image_uri=<TU_USUARIO_DOCKERHUB>/cicd-pipeline-python:latest" \
  -var="lab_role_arn=<ARN_COMPLETO_DE_TU_LABROLE>" \
  -var="vpc_id=<ID_DE_TU_VPC_POR_DEFECTO>" \
  -var='subnet_ids=["<ID_SUBNET_PUBLICA_1>","<ID_SUBNET_PUBLICA_2>"]' \
  -auto-approve
```

**Windows (PowerShell):**
```powershell
terraform --% destroy -var="environment_name=production" -var="docker_image_uri=<TU_USUARIO_DOCKERHUB>/cicd-pipeline-python:latest" -var="lab_role_arn=<ARN_COMPLETO_DE_TU_LABROLE>" -var="vpc_id=<ID_DE_TU_VPC_POR_DEFECTO>" -var="subnet_ids=[\"<ID_SUBNET_PUBLICA_1>\",\"<ID_SUBNET_PUBLICA_2>\"]" -auto-approve
```

> **Verificación recomendada:** entra a la consola de AWS y confirma que ya no existan los ECS Clusters, Services, Target Groups, Load Balancers, Security Groups y Log Groups creados por Terraform para `staging` y `production`.

### 10.2 Elimina el bucket de estado remoto de Terraform

Si creaste un bucket S3 únicamente para este taller (`TF_STATE_BUCKET`), elimínalo también. Antes de borrarlo, debes vaciarlo porque S3 no permite eliminar buckets con objetos dentro.

**Linux / Mac:**
```bash
aws s3 rm s3://<TF_STATE_BUCKET> --recursive
aws s3 rb s3://<TF_STATE_BUCKET>
```

**Windows (PowerShell):**
```powershell
aws s3 rm s3://<TF_STATE_BUCKET> --recursive
aws s3 rb s3://<TF_STATE_BUCKET>
```

> Si el bucket tenía versionado habilitado por tu cuenta o por una configuración manual, primero elimina también las versiones y delete markers desde la consola de S3; de lo contrario el comando de borrado del bucket fallará.

### 10.3 Evita recreaciones accidentales desde GitHub Actions

Para dejar todo realmente limpio, evita que una ejecución futura vuelva a crear la infraestructura sin querer:

1. No hagas nuevos `push` a `main` mientras los secretos de AWS sigan configurados.
2. Si ya terminaste definitivamente el taller, elimina en GitHub los secretos `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN`, `SECRET_KEY` y las variables `LAB_ROLE_ARN`, `VPC_ID`, `SUBNET_IDS`, `TF_STATE_BUCKET`.
3. Opcionalmente, deshabilita temporalmente el workflow `ci-cd.yml` desde la pestaña **Actions** si quieres conservar la configuración pero impedir ejecuciones accidentales.

### 10.4 Cierra la sesión del laboratorio

Cuando termines, vuelve a AWS Academy Learner Lab y usa **Stop Lab**. Esto no reemplaza la destrucción de recursos persistentes, pero sí evita seguir consumiendo tiempo de laboratorio innecesariamente en esa sesión.