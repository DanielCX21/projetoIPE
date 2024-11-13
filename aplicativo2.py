from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import ScrollView
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.list import OneLineIconListItem, IconLeftWidget
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.clock import Clock
import socket
import threading
from datetime import datetime

# Configuração de cor do fundo para melhorar a visibilidade
Window.clearcolor = (0.95, 0.95, 0.95, 1)

# Variável global para armazenar boletins recebidos na memória
boletins_salvos = []

# Função para processar e salvar o boletim na memória
def processar_boletim(dados_boletim):
    global boletins_salvos
    boletim = {}
    zonas = ["METCMQ", "LaLaLaLoLoLo", "YYGoGoGoG", "hhhPdPdPd"] + [f"zona{i}" for i in range(32)]
    
    for i, campo in enumerate(zonas):
        boletim[campo] = dados_boletim[i] if i < len(dados_boletim) else "N/A"
    boletim["horario_salvo"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    boletins_salvos.append(boletim)

# Função para interpretar o cabeçalho
def interpretar_cabecalho(boletim):
    metcmq = f"ID: {boletim['METCMQ']}"
    lat_lon = f"Lat/Lon: {boletim['LaLaLaLoLoLo'][:3]}°N, {boletim['LaLaLaLoLoLo'][3:]}°W"
    data = f"Data: {boletim['YYGoGoGoG'][:2]}/{boletim['YYGoGoGoG'][2:4]}, {boletim['YYGoGoGoG'][4:6]}:{boletim['YYGoGoGoG'][6:]} GMT"
    altura_pressao = f"Altura: {boletim['hhhPdPdPd'][:3]} dm, Pressão: {boletim['hhhPdPdPd'][3:]} mb"
    
    return [
        (metcmq, "information"),
        (lat_lon, "map"),
        (data, "calendar"),
        (altura_pressao, "gauge")
    ]

# Função para buscar dados de uma zona com base na altura
def buscar_dados_altura(altura):
    if not boletins_salvos:
        return [("Nenhum boletim foi recebido ainda.", "alert")]

    zonas = {
        "00": (0, 200), "01": (0, 200), "02": (200, 500), "03": (500, 1000),
        "04": (1000, 1500), "05": (1500, 2000), "06": (2000, 2500), "07": (2500, 3000),
        "08": (3000, 3500), "09": (3500, 4000), "10": (4000, 4500), "11": (4500, 5000),
        "12": (5000, 5500), "13": (6000, 7000), "14": (7000, 8000), "15": (8000, 9000),
        "16": (9000, 10000), "17": (10000, 11000), "18": (11000, 12000), "19": (12000, 13000),
        "20": (13000, 14000), "21": (14000, 15000), "22": (15000, 16000), "23": (16000, 17000),
        "24": (17000, 18000), "25": (18000, 19000), "26": (19000, 20000), "27": (20000, 22000),
        "28": (22000, 24000), "29": (24000, 26000), "30": (26000, 28000), "31": (28000, 30000),
    }

    zona_encontrada = None
    for zona, (altura_min, altura_max) in zonas.items():
        if altura_min <= altura <= altura_max:
            zona_encontrada = f"zona{zona}"
            break

    if zona_encontrada and zona_encontrada in boletins_salvos[-1]:
        return [(f"Dados para altura {altura} metros (Zona {zona}): {boletins_salvos[-1][zona_encontrada]}", "weather-windy")]
    else:
        return [("Altura fora do intervalo suportado ou dados não disponíveis.", "alert")]

class AlturaApp(MDApp):
    def build(self):
        self.title = "Consulta de Dados STANAG 4082"
        
        layout_principal = MDBoxLayout(orientation='vertical', padding=20, spacing=20)
        
        titulo = MDLabel(
            text="Consulta de Altura - STANAG 4082",
            halign="center",
            font_style="H5",
            theme_text_color="Primary"
        )
        layout_principal.add_widget(titulo)
        
        self.status_inicial = MDLabel(
            text="Aguardando dados...",
            halign="center",
            font_style="Body1",
            theme_text_color="Secondary"
        )
        layout_principal.add_widget(self.status_inicial)

        self.port_input = MDTextField(
            hint_text="Porta para Receber UDP",
            input_filter="int",
            font_size=18,
            size_hint=(1, None),
            height=40,
            pos_hint={"center_x": 0.5}
        )
        layout_principal.add_widget(self.port_input)

        btn_iniciar = MDRaisedButton(
            text="Iniciar Recepção",
            size_hint=(1, None),
            height=50,
            pos_hint={"center_x": 0.5},
            on_press=self.iniciar_recebimento
        )
        layout_principal.add_widget(btn_iniciar)

        self.entrada_altura = MDTextField(
            hint_text="Digite a altura em metros (máximo 30000)",
            helper_text="Exemplo: 5000",
            helper_text_mode="on_focus",
            input_filter="int",
            font_size=18,
            size_hint=(1, None),
            height=50,
            pos_hint={"center_x": 0.5}
        )
        layout_principal.add_widget(self.entrada_altura)

        btn_buscar = MDRaisedButton(
            text="Buscar Dados",
            size_hint=(1, None),
            height=50,
            pos_hint={"center_x": 0.5},
            on_press=self.buscar_dados
        )
        layout_principal.add_widget(btn_buscar)

        scrollview = ScrollView(size_hint=(1, 1))
        self.resultado_layout = MDBoxLayout(orientation="vertical", spacing=10, padding=10, size_hint_y=None)
        self.resultado_layout.bind(minimum_height=self.resultado_layout.setter('height'))
        scrollview.add_widget(self.resultado_layout)
        
        layout_principal.add_widget(scrollview)
        
        return layout_principal

    def iniciar_recebimento(self, instance):
        if not self.port_input.text.isdigit():
            self.exibir_popup("Por favor, insira uma porta válida para recepção.")
            return
        self.porta_recepcao = int(self.port_input.text.strip())
        
        self.listen_thread = threading.Thread(target=self.start_udp_listener)
        self.listen_thread.daemon = True
        self.listen_thread.start()
        self.status_inicial.text = f"Escutando na porta {self.porta_recepcao}..."

    def start_udp_listener(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.bind(("", self.porta_recepcao))
            while True:
                dados, _ = sock.recvfrom(4096)
                mensagem = dados.decode()
                dados_boletim = [linha for linha in mensagem.split("\n") if linha.strip()]
                processar_boletim(dados_boletim)
                Clock.schedule_once(lambda dt: self.update_status("Dados recebidos e processados com sucesso!"))

    def update_status(self, message):
        self.status_inicial.text = message

    def buscar_dados(self, instance):
        altura_texto = self.entrada_altura.text.strip()
        if not altura_texto.isdigit():
            self.exibir_popup("Por favor, insira uma altura válida em metros.")
            return
        altura = int(altura_texto)
        resultado = buscar_dados_altura(altura)
        self.mostrar_resultado(resultado)

    def exibir_popup(self, mensagem):
        popup = Popup(
            title="Notificação",
            content=MDLabel(
                text=mensagem,
                theme_text_color="Custom",
                text_color=[1, 1, 1, 1],  # Texto branco
                halign="center",
                valign="middle"
            ),
            size_hint=(0.8, 0.3),
            background_color=[0, 0, 0, 0.7]  # Fundo escuro
        )
        popup.open()

    def mostrar_resultado(self, resultado):
        self.resultado_layout.clear_widgets()
        for texto, icone in resultado:
            item = OneLineIconListItem(text=texto)
            item.add_widget(IconLeftWidget(icon=icone))
            self.resultado_layout.add_widget(item)

AlturaApp().run()
