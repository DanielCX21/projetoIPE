import socket
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
import threading
from datetime import datetime

# Variável para armazenar o boletim recebido
boletim_atual = {}

# Função para processar o boletim e armazená-lo no dicionário em memória
def processar_boletim(dados_boletim):
    global boletim_atual
    boletim_atual.clear()  # Limpar dados anteriores
    zonas = ["METCMQ", "LaLaLaLoLoLo", "YYGoGoGoG", "hhhPdPdPd"] + [f"zona{i}" for i in range(32)]
    for i, campo in enumerate(zonas):
        boletim_atual[campo] = dados_boletim[i] if i < len(dados_boletim) else ""  # Armazena dados recebidos ou vazio
    boletim_atual["horario_salvo"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Armazena o timestamp
    print("Boletim atualizado:", boletim_atual)  # Log para ver o boletim recebido

# Função para buscar dados do boletim a partir da altura
def buscar_dados_altura(altura):
    # Mapeamento das zonas para alturas conforme a tabela fornecida
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

    # Determina a zona correta com base na altura
    zona_encontrada = None
    for zona, (altura_min, altura_max) in zonas.items():
        if altura_min <= altura <= altura_max:
            zona_encontrada = f"zona{zona}"
            break

    if zona_encontrada and zona_encontrada in boletim_atual:
        return f"Dados para altura {altura} metros (Zona {zona}):\n{boletim_atual[zona_encontrada]}"
    else:
        return "Altura fora do intervalo suportado ou dados não disponíveis."

class AlturaApp(App):
    def build(self):
        self.title = "Consulta de Dados STANAG 4082"
        
        # Layout principal
        layout_principal = BoxLayout(orientation='vertical', padding=20, spacing=20)
        
        # Campo para configurar a porta de recepção UDP
        self.port_input = TextInput(hint_text="Porta para Receber UDP", multiline=False, input_filter="int",
                                    font_size=18, size_hint=(1, 0.2), background_color=(1, 1, 1, 1),
                                    foreground_color=(0, 0, 0, 1))
        layout_principal.add_widget(self.port_input)

        # Botão para iniciar a recepção
        btn_iniciar = Button(text="Iniciar Recepção", font_size=18, size_hint=(1, 0.2),
                             background_color=(0.2, 0.6, 0.2, 1), color=(1, 1, 1, 1))
        btn_iniciar.bind(on_press=self.iniciar_recebimento)
        layout_principal.add_widget(btn_iniciar)

        # Campo para entrada de altura e busca de dados
        layout_entrada = BoxLayout(orientation='horizontal', padding=10, spacing=10)
        layout_entrada.add_widget(Label(text="Altura (m):", font_size=18, color=(0, 0, 0, 1), size_hint=(0.3, 1)))
        
        self.entrada_altura = TextInput(hint_text="Digite a altura em metros", multiline=False, input_filter="int",
                                        font_size=18, size_hint=(0.4, 1), background_color=(1, 1, 1, 1),
                                        foreground_color=(0, 0, 0, 1))
        layout_entrada.add_widget(self.entrada_altura)

        btn_buscar = Button(text="Buscar Dados", size_hint=(0.3, 1), font_size=18,
                            background_color=(0.2, 0.2, 0.6, 1), color=(1, 1, 1, 1))
        btn_buscar.bind(on_press=self.buscar_dados)
        layout_entrada.add_widget(btn_buscar)
        
        layout_principal.add_widget(layout_entrada)

        # Área para exibir o resultado
        self.resultado_label = Label(text="Aguardando dados...", font_size=16, halign="left", valign="top",
                                     color=(0, 0, 0, 1), size_hint=(1, 0.6))
        layout_principal.add_widget(self.resultado_label)
        
        return layout_principal

    def iniciar_recebimento(self, instance):
        if not self.port_input.text.isdigit():
            self.resultado_label.text = "Por favor, insira uma porta válida para recepção."
            return
        self.porta_recepcao = int(self.port_input.text.strip())
        
        # Iniciar a thread de escuta UDP
        self.listen_thread = threading.Thread(target=self.start_udp_listener)
        self.listen_thread.daemon = True
        self.listen_thread.start()
        self.resultado_label.text = f"Escutando na porta {self.porta_recepcao}..."

    def start_udp_listener(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.bind(("", self.porta_recepcao))
            print("UDP listener iniciado na porta", self.porta_recepcao)  # Log para confirmar o início
            while True:
                dados, _ = sock.recvfrom(4096)
                mensagem = dados.decode()
                print("Mensagem recebida:", mensagem)  # Log da mensagem recebida
                dados_boletim = mensagem.split("\n")
                processar_boletim(dados_boletim)
                # Atualizar a interface para mostrar que os dados foram recebidos
                Clock.schedule_once(lambda dt: self.update_status("Dados recebidos e processados com sucesso!"))

    def update_status(self, message):
        self.resultado_label.text = message

    def buscar_dados(self, instance):
        altura_texto = self.entrada_altura.text.strip()
        if not altura_texto.isdigit():
            self.resultado_label.text = "Por favor, insira uma altura válida em metros."
            return
        altura = int(altura_texto)
        resultado = buscar_dados_altura(altura)
        self.resultado_label.text = resultado

AlturaApp().run()