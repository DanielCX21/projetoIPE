from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import ScrollView
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.list import OneLineIconListItem, IconLeftWidget
from kivy.core.window import Window
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
    """
    Processa a mensagem recebida, salvando os dados de cada zona em uma estrutura de dicionário.
    """
    global boletins_salvos
    boletim = {}
    zonas = ["METCMQ", "LaLaLaLoLoLo", "YYGoGoGoG", "hhhPdPdPd"] + [f"zona{i}" for i in range(32)]
    
    for i, campo in enumerate(zonas):
        boletim[campo] = dados_boletim[i] if i < len(dados_boletim) else "N/A"
    boletim["horario_salvo"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    boletins_salvos.append(boletim)
    print("Boletim atualizado:", boletim)  # Para depuração

# Função para decodificar a string da zona
def decodificar_dados_zona(zona_dados):
    #zona_dados = boletins_salvos[-1][zona_encontrada]
    #zona_dados é o valor de um dicionario dentro de uma lista de dicionarios
    #zona_dados é um dicionario
    try:
        
        zona_numero = zona_dados[len(zona_dados) - 16:len(zona_dados) -14]
        direcao_vento = int(zona_dados[len(zona_dados) - 14:len(zona_dados) - 11]) * 10  # Convertendo para mils
        velocidade_vento = int(zona_dados[len(zona_dados) - 11:len(zona_dados) - 8])  # knots
        temperatura = int(zona_dados[len(zona_dados) - 8:len(zona_dados) - 4]) / 10.0  # Kelvin
        pressao = int(zona_dados[len(zona_dados) - 4:len(zona_dados)])  # mb

        return [
            (f"Zona: {zona_numero}", "map-marker"),
            (f"Direção do Vento: {direcao_vento} mils", "compass"),
            (f"Velocidade do Vento: {velocidade_vento} nós", "weather-windy"),
            (f"Temperatura Virtual: {temperatura:.1f} K", "thermometer"),
            (f"Pressão do Ar: {pressao} mb", "gauge")
        ]
    except (ValueError, IndexError) as e:
        return [(f"Erro na decodificação dos dados: {e}", "alert")]

# Função para buscar dados de uma zona com base na altura
def buscar_dados_altura(altura_str):
    if not boletins_salvos:
        return [("Nenhum boletim foi recebido ainda.", "alert")]
    #nao da esse erro -> boletins_salvos = true

    # Mapeamento de alturas para zonas (usando strings para evitar conflitos de tipo)
    zonas = {
        "00": (0, 0), "01": (0, 200), "02": (200, 500), "03": (500, 1000),
        "04": (1000, 1500), "05": (1500, 2000), "06": (2000, 2500), "07": (2500, 3000),
        "08": (3000, 3500), "09": (3500, 4000), "10": (4000, 4500), "11": (4500, 5000),
        "12": (5000, 5500), "13": (6000, 7000), "14": (7000, 8000), "15": (8000, 9000),
        "16": (9000, 10000), "17": (10000, 11000), "18": (11000, 12000), "19": (12000, 13000),
        "20": (13000, 14000), "21": (14000, 15000), "22": (15000, 16000), "23": (16000, 17000),
        "24": (17000, 18000), "25": (18000, 19000), "26": (19000, 20000), "27": (20000, 22000),
        "28": (22000, 24000), "29": (24000, 26000), "30": (26000, 28000), "31": (28000, 30000),
    }

    try:
        altura = int(altura_str) #parametro recebido em buscar_dados_altura -> garanto que é inteiro
        zona_encontrada = None #defino zona_encontrada
        for zona, (altura_min, altura_max) in zonas.items():
        #   key    value1      value2         
            if int(altura_min) <= int(altura) <= int(altura_max):
                if zona[0] == "0":
                    zona_certo = zona[1:]
                    zona_certo = int(zona_certo) + 1
                    zona_certo = str(zona_certo)
                else:
                    zona_certo = int(zona)
                    zona_certo += 1
                    zona_certo = str(zona_certo)
                zona_encontrada = f"zona{zona_certo}"
                break
        # o loop é verdadeiro

        #print(boletins_salvos)
        #print(zona_encontrada)

        if zona_encontrada and zona_encontrada in boletins_salvos[-1]:
            zona_dados = boletins_salvos[-1][zona_encontrada]
            return decodificar_dados_zona(zona_dados)
        else:
            return [("Altura fora do intervalo suportado ou dados não disponíveis.", "alert")]
    except ValueError:
        return [("Por favor, insira uma altura válida em metros.", "alert")]

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
            size_hint=(1, 0.2),
            pos_hint={"center_x": 0.5}
        )
        layout_principal.add_widget(self.port_input)

        btn_iniciar = MDRaisedButton(
            text="Iniciar Recepção",
            size_hint=(0.8, None),
            height=50,
            pos_hint={"center_x": 0.5},
            on_press=self.iniciar_recebimento
        )
        layout_principal.add_widget(btn_iniciar)

        self.entrada_altura = MDTextField(
            hint_text="Digite a altura em metros (máximo 30000)",
            helper_text="Exemplo: 5000",
            helper_text_mode="on_focus",
            input_filter=None,
            font_size=18,
            size_hint_x=0.9,
            pos_hint={"center_x": 0.5},
            on_text_validate=self.buscar_dados
        )
        layout_principal.add_widget(self.entrada_altura)

        btn_buscar = MDRaisedButton(
            text="Buscar Dados",
            size_hint=(0.5, None),
            height=50,
            pos_hint={"center_x": 0.5},
            on_press=self.buscar_dados
        )
        layout_principal.add_widget(btn_buscar)

        scrollview = ScrollView(size_hint=(1, 0.6))
        self.resultado_layout = MDBoxLayout(orientation="vertical", spacing=10, padding=10, size_hint_y=None)
        self.resultado_layout.bind(minimum_height=self.resultado_layout.setter('height'))
        scrollview.add_widget(self.resultado_layout)
        
        layout_principal.add_widget(scrollview)
        
        return layout_principal

    def iniciar_recebimento(self, instance):
        if not self.port_input.text.isdigit():
            self.status_inicial.text = "Por favor, insira uma porta válida para recepção."
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
                mensagem = dados.decode().split("\n")
                processar_boletim(mensagem)
                Clock.schedule_once(lambda dt: self.update_status("Dados recebidos e processados com sucesso!"))

    def update_status(self, message):
        self.status_inicial.text = message

    def buscar_dados(self, instance=None):
        altura_texto = self.entrada_altura.text.strip()
        resultado = buscar_dados_altura(altura_texto)
        self.mostrar_resultado(resultado)

    def mostrar_resultado(self, resultado):
        self.resultado_layout.clear_widgets()
        for texto, icone in resultado:
            item = OneLineIconListItem(text=texto)
            item.add_widget(IconLeftWidget(icon=icone))
            self.resultado_layout.add_widget(item)

AlturaApp().run()