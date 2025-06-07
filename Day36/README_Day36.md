
# Día 36 - Stock Trading News Alert Project (Acciones de TESLA)

## 📝 Descripción

Este proyecto consiste en un sistema de alerta para noticias relacionadas con el precio de las acciones de **Tesla Inc (TSLA)**. Su propósito es detectar cambios significativos en el precio de las acciones (más del 5% entre ayer y anteayer) y, en caso de detectar uno, enviar un mensaje con los titulares de las noticias más recientes relacionadas con la empresa.

El sistema combina tres servicios web para su funcionamiento:

-   📈 [Alpha Vantage](https://www.alphavantage.co/): para obtener datos diarios del precio de las acciones.
    
-   📰 [NewsAPI](https://newsapi.org/): para buscar noticias relevantes relacionadas con Tesla Inc.
    
-   📱 [Twilio](https://www.twilio.com/en-us): para enviar los titulares como mensajes SMS directamente al teléfono del usuario.
    

Este proyecto es útil como ejercicio práctico para integrar múltiples APIs, trabajar con datos en tiempo real y automatizar notificaciones con condiciones definidas.

---
## 📁 Estructura del proyecto
```bash
Day36/
├── README.md
├── requirements.txt
├── TESLA_stock-news-hard-start/
│   ├── main.py
│   └── .env
├── XRP_stock-news-hard-start/
│   ├── main.py
│   └── .env
└── assets/   # En este caso solo imágenes para el README
```

---

## ⚙️ Instalación

1. Clona este repositorio o descarga solo esta carpeta:

```bash
Descarga esta carpeta:
git clone https://github.com/Jose-Escamilla/100-days-of-code.git
```
2. Navega a esta carpeta del día:
```bash
cd 100-days-of-code/DayX
```
3. (Opcional) Crea y activa un entorno virtual:

	**🧪 Usando VS Code (sin Anaconda)**

		Desde la terminal de VS Code, ejecuta:
	```bash
	python -m venv venv
	```
	Luego activa el entorno virtual:
	- En **Windows**:
	 ```bash
	.\venv\Scripts\activate
	```
	-  En **Mac/Linux**:
	 ```bash
	source venv/bin/activate
	```
	Si estás en VS Code y tienes la extensión de Python instalada, podrás seleccionar el entorno en la esquina inferior izquierda donde aparece el intérprete. Haz clic y selecciona el nuevo entorno `./venv`.

	**🐍 Usando Anaconda**
	- Crea el entorno con un nombre, por ejemplo `dayX-env`:
	```bash
	conda create -n dayX-env python=3.11
	```
	- Activa el entorno:
	```bash
	conda activate dayX-env
	```
	- Si usas VS Code, asegúrate de seleccionar el entorno correcto como intérprete (`dayX-env`) desde la paleta de comandos (`Ctrl+Shift+P` → _Python: Select Interpreter_).

4. Instala dependencias si las hay:
```bash
pip install -r requirements.txt
```

---
## ▶️ Cómo ejecutar
```bash
python main.py
```
Antes de ejecutar el archivo, asegúrate de instalar las dependencias necesarias. Puedes hacerlo con el siguiente comando:
```bash
pip install -r requirements.txt
```
> **Nota:** Este proyecto se ejecuta en la terminal/console. No tiene interfaz gráfica. Para funcionar correctamente, también necesita un archivo `.env` con las claves de las APIs.
```bash
ALPHAVANTAGE_API_KEY=tu_clave_de_alphavantage
NEWS_API_KEY=tu_clave_de_newsapi
TWILIO_SID=tu_account_sid_de_twilio
TWILIO_AUTH_TOKEN=tu_auth_token_de_twilio
TWILIO_PHONE=tu_numero_de_twilio
MY_PHONE=tu_numero_personal
```
---
## 🎥 Demo / Capturas

A continuación se muestran capturas del proyecto en ejecución y del mensaje recibido vía SMS:

<p align="center"> <img src="assets/run_code.png" width="500" alt="Ejecución del código en VSCode"> </p> <p align="center"> <img src="assets/sms_in_phone.png" width="300" alt="Mensaje recibido en el teléfono"> </p>

---
## 💡 Problema y solución


### Problema planteado:

Estar al tanto de noticias relevantes que puedan afectar el precio de acciones o criptomonedas requiere tiempo y atención constante. Los inversionistas o entusiastas del mercado pueden perder información importante si no monitorean los movimientos del mercado y las noticias en tiempo real.

### Enfoque y solución:

Este proyecto resuelve el problema automatizando la vigilancia de precios y noticias. Utilizando la API de Alpha Vantage, el programa obtiene el precio de cierre de una acción o criptomoneda durante los últimos dos días y calcula el cambio porcentual. Si el cambio supera un umbral (por ejemplo, ±5%), se realiza una solicitud a NewsAPI para obtener las 3 noticias más recientes relacionadas con la empresa. Finalmente, se envía cada noticia al número personal del usuario mediante SMS usando Twilio.

La estructura del código sigue una lógica clara y modular:

1. **Obtención de datos financieros** desde Alpha Vantage.
2. **Cálculo del cambio porcentual** para determinar si se deben obtener noticias.
3. **Consulta de artículos de prensa** a través de NewsAPI.
4. **Envío automatizado de mensajes** vía Twilio si se detecta un cambio significativo.


---
## 🚀 Mejoras futuras / Limitaciones
- 🔄 **Uso de una base de datos o historial local** para evitar enviar mensajes duplicados en días con movimientos similares.
- ⏱️ **Soporte para notificaciones programadas**, como envío diario a una hora fija sin necesidad de ejecutar manualmente el script.
- 📊 **Visualización gráfica** de los cambios porcentuales o tendencias a través de una interfaz web o gráfica.
- 🌍 **Compatibilidad con múltiples acciones o criptomonedas** dentro de una misma ejecución.
- 📉 **Mejor manejo de límites de uso de API**, especialmente en Alpha Vantage, ya que la versión gratuita tiene un límite estricto de 25 llamadas por día.
- 📵 **Agregar opción para recibir notificaciones por otros medios** como correo electrónico o Telegram, además de SMS.
- ❌ **No contempla errores de conexión a internet o fallas en el servicio Twilio/NewsAPI**, se podría implementar una reintento o logging detallado.
---
## 🧠 Explicación de mi proceso de pensamiento

Durante el desarrollo de este proyecto, mi principal enfoque fue integrar varias APIs para obtener datos de acciones, noticias relevantes y enviar notificaciones por SMS. Inicialmente enfrenté retos relacionados con el manejo correcto de las respuestas de la API, especialmente con las limitaciones y formatos de los datos que recibía.

Para superar estos obstáculos, implementé validaciones exhaustivas para verificar la presencia de las claves esperadas en las respuestas y manejar adecuadamente los posibles errores, como límites de cuota o respuestas vacías. También aprendí la importancia de leer cuidadosamente la documentación de cada API para entender sus limitaciones y parámetros.

Este proyecto me enseñó a estructurar el código en pasos claros (obtener datos, analizar cambios, buscar noticias, enviar alertas) y a manejar las excepciones para que el programa sea más robusto. En futuros proyectos, aplicaré este enfoque modular y la validación anticipada de datos para mejorar la confiabilidad de mis aplicaciones.


---
## 📬 Contacto

**Autor:** José Escamilla  
**Email:** 
**Tel:** 
