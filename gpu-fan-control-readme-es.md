# Aplicación de Control de Ventilador de GPU

## Descripción

Esta aplicación proporciona una interfaz gráfica para controlar la velocidad del ventilador de GPUs NVIDIA en sistemas Linux. Permite a los usuarios ajustar manualmente las velocidades del ventilador o configurar curvas de ventilador personalizadas para el control automático basado en la temperatura de la GPU.

## Características

- Monitoreo en tiempo real de la temperatura de la GPU
- Control manual de la velocidad del ventilador
- Control automático de la velocidad del ventilador basado en curvas personalizadas
- Tres perfiles de curva de ventilador personalizables
- Gráfico interactivo para editar fácilmente las curvas de ventilador
- Capacidad para guardar y cargar perfiles de curvas de ventilador

## Requisitos

- Python 3.x
- GPU NVIDIA con controladores propietarios instalados
- Herramientas de línea de comandos `nvidia-smi` y `nvidia-settings`
- Bibliotecas de Python requeridas:
  - tkinter
  - matplotlib
  - threading
  - subprocess
  - json

## Instalación

1. Asegúrate de tener Python 3.x instalado en tu sistema.
2. Instala las bibliotecas de Python requeridas:
   ```
   pip install matplotlib
   ```
   (Nota: tkinter generalmente viene preinstalado con Python)
3. Clona este repositorio o descarga el archivo `gpu-fan-control-app.py`.

## Uso

1. Abre una terminal en el directorio que contiene el script.
2. Ejecuta la aplicación:
   ```
   python gpu-fan-control-app.py
   ```
3. Aparecerá la ventana de la aplicación, mostrando la temperatura actual de la GPU y la velocidad del ventilador.

### Modo Manual
- Desmarca la casilla "Modo Automático".
- Usa el deslizador para ajustar manualmente la velocidad del ventilador.

### Modo Automático
- Asegúrate de que la casilla "Modo Automático" esté marcada.
- La velocidad del ventilador se ajustará automáticamente según el perfil de curva de ventilador activo.

### Personalización de Curvas de Ventilador
- Haz clic y arrastra los puntos en el gráfico para ajustar la curva del ventilador.
- Usa los botones numéricos (1, 2, 3) para cambiar entre diferentes perfiles de curva de ventilador.
- Haz clic en el botón "S" para guardar tus perfiles personalizados.

## Solución de problemas

- Si la aplicación no detecta tu GPU o no controla la velocidad del ventilador, asegúrate de que:
  1. Tienes una GPU NVIDIA con los controladores adecuados instalados.
  2. Las herramientas `nvidia-smi` y `nvidia-settings` están instaladas y accesibles desde la línea de comandos.
  3. Tienes los permisos necesarios para controlar el ventilador de la GPU (es posible que necesites ejecutar la aplicación con sudo).

## Contribuciones

Las contribuciones para mejorar la aplicación son bienvenidas. Por favor, siéntete libre de enviar pull requests o abrir issues para errores y solicitudes de características.

## Licencia

Este proyecto es de código abierto y está disponible bajo la Licencia MIT.

## Descargo de responsabilidad

Usa esta aplicación bajo tu propio riesgo. Una configuración inadecuada de la velocidad del ventilador puede llevar a sobrecalentamiento y posibles daños a tu GPU. Siempre monitorea las temperaturas de tu GPU y asegura un enfriamiento adecuado.
