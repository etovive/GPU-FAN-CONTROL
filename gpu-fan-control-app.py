import os
import time
import subprocess
import tkinter as tk
from tkinter import ttk
import threading
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json

class CurvaVentilador:
    def __init__(self):
        self.puntos = [
            (20, 10), (30, 10), (40, 23), (50, 33),
            (60, 55), (70, 73), (80, 76), (90, 100), (100, 100)
        ]

    def obtener_velocidad_ventilador(self, temp):
        for i, punto in enumerate(self.puntos):
            if temp <= punto[0]:
                if i == 0:
                    return punto[1]
                punto_anterior = self.puntos[i-1]
                dif_temp = punto[0] - punto_anterior[0]
                dif_vel = punto[1] - punto_anterior[1]
                ratio_temp = (temp - punto_anterior[0]) / dif_temp
                return punto_anterior[1] + (dif_vel * ratio_temp)
        return self.puntos[-1][1]

class AplicacionControlVentilador:
    def __init__(self, master):
        self.master = master
        master.title("Control de Ventilador GPU")
        master.configure(bg='#F0F0F0')
        master.geometry("510x520")

        master.update_idletasks()
        width = master.winfo_width()
        height = master.winfo_height()
        x = (master.winfo_screenwidth() // 2) - (width // 2)
        y = (master.winfo_screenheight() // 2) - (height // 2)
        master.geometry('{}x{}+{}+{}'.format(width, height, x, y))

        self.estilo = ttk.Style()
        self.estilo.theme_use('clam')
        self.estilo.configure('TFrame', background='#F0F0F0')
        self.estilo.configure('TLabel', background='#F0F0F0', foreground='black', font=('Helvetica', 10))
        self.estilo.configure('TButton', font=('Helvetica', 10), background='#E0E0E0', foreground='black')
        self.estilo.configure('TCheckbutton', background='#F0F0F0', foreground='black', font=('Helvetica', 10))
        self.estilo.configure('Green.TButton', background='#4CAF50', foreground='white')

        self.curvas_ventilador = [CurvaVentilador(), CurvaVentilador(), CurvaVentilador()]
        self.perfil_activo = 0
        self.velocidad_ventilador = tk.IntVar(value=10)
        self.modo_automatico = tk.BooleanVar(value=True)
        self.temp_gpu = tk.StringVar(value="N/A")
        self.nombre_gpu = tk.StringVar(value="Detectando GPU...")

        self.marco_principal = ttk.Frame(master, padding="10 10 10 10")
        self.marco_principal.pack(fill=tk.BOTH, expand=True)
       
        self.crear_controles()
        self.crear_grafica()

        self.hilo_actualizacion = threading.Thread(target=self.bucle_actualizacion, daemon=True)
        self.hilo_actualizacion.start()

        self.alternar_modo_automatico()
        self.cargar_perfiles()
        self.detectar_gpu()

    def crear_controles(self):
        ttk.Label(self.marco_principal, text="Velocidad del Ventilador:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        velocidad_frame = ttk.Frame(self.marco_principal)
        velocidad_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.deslizador_velocidad = ttk.Scale(velocidad_frame, from_=0, to=100, orient=tk.HORIZONTAL, 
                                              variable=self.velocidad_ventilador, command=self.actualizar_velocidad_ventilador,
                                              length=250, style="Elegante.Horizontal.TScale")
        self.deslizador_velocidad.pack(side=tk.LEFT, expand=True, fill=tk.X)

        self.estilo.configure("Elegante.Horizontal.TScale", background='#E0E0E0', troughcolor='#BDBDBD', thickness=25)
        self.estilo.map("Elegante.Horizontal.TScale", background=[('active', '#D0D0D0')])

        self.etiqueta_velocidad = ttk.Label(velocidad_frame, textvariable=self.velocidad_ventilador, width=3)
        self.etiqueta_velocidad.pack(side=tk.LEFT, padx=(10, 150))

        info_frame = ttk.Frame(self.marco_principal)
        info_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0,1))
       # info_frame.place(y=45)
        ttk.Label(info_frame, textvariable=self.nombre_gpu).pack(side=tk.LEFT)
        ttk.Label(info_frame, text="GPU:").pack(side=tk.LEFT)
        ttk.Label(info_frame, textvariable=self.temp_gpu).pack(side=tk.LEFT)
     
   
        checkbutton_frame = ttk.Frame(self.marco_principal)
        checkbutton_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 1))


        self.casilla_automatico = ttk.Checkbutton(checkbutton_frame, text="Modo Automático", variable=self.modo_automatico, 
                                           command=self.alternar_modo_automatico)
        self.casilla_automatico.pack(side=tk.LEFT)
      #  self.casilla_automatico.place(y=5)
     
        

    def crear_grafica(self):
        fig_frame = ttk.Frame(self.marco_principal)
        fig_frame.grid(row=4, column=0, columnspan=3, pady=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        #fig_frame.place(y=80)
        self.fig, self.ax = plt.subplots(figsize=(5, 4), facecolor='#F0F0F0')
        self.canvas = FigureCanvasTkAgg(self.fig, master=fig_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.line, = self.ax.plot(*zip(*self.curvas_ventilador[self.perfil_activo].puntos), 'ro-')
        self.ax.set_xlim(20, 100)
        self.ax.set_ylim(0, 110)
        self.ax.set_xlabel('Temperatura (°C)', color='black')
        self.ax.set_ylabel('Velocidad del Ventilador (%)', color='black')
        self.ax.set_title('Curva de Velocidad del Ventilador', color='black')
        self.ax.grid(True, color='#E0E0E0')
        self.ax.set_facecolor('#F0F0F0')
        for spine in self.ax.spines.values():
            spine.set_edgecolor('black')
        self.ax.tick_params(colors='black')
        
        self.fill = self.ax.fill_between([], [], color='red', alpha=0.2)

        self.canvas.mpl_connect('button_press_event', self.on_press)
        self.canvas.mpl_connect('button_release_event', self.on_release)
        self.canvas.mpl_connect('motion_notify_event', self.on_motion)

        self.selected_point = None
        self.dragging = False

        # Profile buttons
        profile_frame = ttk.Frame(fig_frame)
        profile_frame.pack(side=tk.LEFT, fill=tk.Y)
        profile_frame.place(x=460, y=45)  ##CAMBIAR POSICION
        for i in range(3):
            ttk.Button(profile_frame, text=str(i+1), width=2, command=lambda i=i: self.cambiar_perfil(i)).pack(pady=3)
       
        ttk.Button(profile_frame, text="S", width=2, style='Green.TButton', command=self.guardar_perfiles).pack(pady=5)

    def on_press(self, event):
        if event.inaxes != self.ax:
            return
        cont, ind = self.line.contains(event)
        if cont:
            self.selected_point = ind["ind"][0]
            self.dragging = True

    def on_release(self, event):
        self.dragging = False
        self.selected_point = None

    def on_motion(self, event):
        if not self.dragging or self.selected_point is None:
            return
        x, y = event.xdata, event.ydata
        if x is not None and y is not None:
            x = max(20, min(100, x))
            y = max(0, min(100, y))
            self.curvas_ventilador[self.perfil_activo].puntos[self.selected_point] = (x, y)
            self.curvas_ventilador[self.perfil_activo].puntos.sort(key=lambda p: p[0])
            self.actualizar_grafica()

    def actualizar_grafica(self):
        x, y = zip(*self.curvas_ventilador[self.perfil_activo].puntos)
        self.line.set_data(x, y)
        self.fill.remove()
        self.fill = self.ax.fill_between(x, 0, y, color='gray', alpha=0.4)
        self.canvas.draw()



    def actualizar_velocidad_ventilador(self, event=None):
        if not self.modo_automatico.get():
            velocidad = int(self.velocidad_ventilador.get())
            self.velocidad_ventilador.set(velocidad)
            self.establecer_velocidad_ventilador_gpu(velocidad)

    def alternar_modo_automatico(self):
        if self.modo_automatico.get():
            self.deslizador_velocidad.state(['disabled'])
        else:
            self.deslizador_velocidad.state(['!disabled'])

    def obtener_temp_gpu(self):
        try:
            return float(subprocess.check_output("nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader", shell=True))
        except:
            return 20  # Valor predeterminado si no se puede obtener la temperatura

    def establecer_velocidad_ventilador_gpu(self, velocidad):
        try:
            os.system(f"nvidia-settings -a [gpu:0]/GPUFanControlState=1 -a [fan:0]/GPUTargetFanSpeed={velocidad}")
        except:
            print(f"No se pudo establecer la velocidad del ventilador a {velocidad}%")

    def bucle_actualizacion(self):
        while True:
            temp_gpu = self.obtener_temp_gpu()
            self.temp_gpu.set(f"{temp_gpu:.1f} °C")
            
            if self.modo_automatico.get():
                velocidad_ventilador = int(self.curvas_ventilador[self.perfil_activo].obtener_velocidad_ventilador(temp_gpu))
                self.velocidad_ventilador.set(velocidad_ventilador)
                self.establecer_velocidad_ventilador_gpu(velocidad_ventilador)
            
            time.sleep(2)

    def cambiar_perfil(self, perfil):
        self.perfil_activo = perfil
        self.boton_seleccionado_texto = str(perfil + 1)  #guardo el boton    
       
        self.actualizar_grafica()

    def guardar_perfiles(self):
      perfiles = []
    
      for i, curva in enumerate(self.curvas_ventilador):
         perfil = {
            'puntos': curva.puntos,
            'boton_texto': str(i + 1) if i == self.perfil_activo else None  #guardo el boton que se selecciono
        }
         perfiles.append(perfil)
      with open('perfiles_ventilador.json', 'w') as f:
       json.dump(perfiles, f, indent=4) 


    def cargar_perfiles(self):
        try:
            with open('perfiles_ventilador.json', 'r') as f:
                perfiles = json.load(f)

            for i, perfil in enumerate(perfiles):
             self.curvas_ventilador[i].puntos = perfil['puntos']  # cargo la curva

             if perfil.get('boton_texto') is not None and perfil.get('boton_texto') == str(i + 1):
                self.cambiar_perfil(i)  # llamo a perfil
               
        except FileNotFoundError:
            pass  

    def detectar_gpu(self):
        try:
            gpu_info = subprocess.check_output("nvidia-smi --query-gpu=name --format=csv,noheader", shell=True).decode().strip()
            self.nombre_gpu.set(gpu_info)
        except:
            self.nombre_gpu.set("GPU no detectada")

if __name__ == "__main__":
    root = tk.Tk()
    app = AplicacionControlVentilador(root)
    root.mainloop()
