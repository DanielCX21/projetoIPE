from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.window import Window
from datetime import datetime
import socket
import re

# Configura a cor de fundo da janela
Window.clearcolor = (0.95, 0.95, 0.95, 1)  # Fundo claro

class StanagApp(App):
    def build(self):
        self.title = "Boletim STANAG 4082"
        
        # Layout principal
        layout_principal = BoxLayout(orientation='vertical', padding=10, spacing=10)
        layout_principal.add_widget(Label(text="Boletim STANAG 4082", font_size=24, bold=True, color=(0, 0, 0, 1), size_hint_y=None, height=50))
        
        # Campos para o IP e a Porta do dispositivo de destino
        self.ip_input = TextInput(hint_text="IP do App 2", multiline=False, font_size=16, size_hint_y=None, height=40,
                                  background_color=(1, 1, 1, 1), foreground_color=(0, 0, 0, 1))
        self.port_input = TextInput(hint_text="Porta do App 2", multiline=False, input_filter="int", font_size=16,
                                    size_hint_y=None, height=40, background_color=(1, 1, 1, 1), foreground_color=(0, 0, 0, 1))
        layout_principal.add_widget(self.ip_input)
        layout_principal.add_widget(self.port_input)

        # Layout da introdução (Cabeçalho)
        layout_intro = GridLayout(cols=2, spacing=10, size_hint_y=None, height=200)
        campos_intro = ["METCMQ", "Latitude/Longitude", "Data e Duração", "Altura e Pressão MDP"]
        self.intro_inputs = []
        
        for campo in campos_intro:
            layout_intro.add_widget(Label(text=campo, font_size=16, color=(0, 0, 0, 1), size_hint_y=None, height=40))
            input_campo = TextInput(multiline=False, font_size=16, size_hint_y=None, height=40,
                                    background_color=(1, 1, 1, 1), foreground_color=(0, 0, 0, 1))
            self.intro_inputs.append(input_campo)
            layout_intro.add_widget(input_campo)
        
        layout_principal.add_widget(layout_intro)

        # Layout de Zonas com rolagem
        scrollview = ScrollView(size_hint=(1, 1))
        layout_zonas = GridLayout(cols=2, padding=10, spacing=10, size_hint_y=None)
        layout_zonas.bind(minimum_height=layout_zonas.setter('height'))

        self.zona_inputs = []

        for zona in range(32):
            layout_zonas.add_widget(Label(text=f"Zona {zona}", font_size=14, color=(0, 0, 0, 1), size_hint_y=None, height=40))
            input_zona = TextInput(multiline=False, font_size=14, size_hint_y=None, height=40,
                                   background_color=(1, 1, 1, 1), foreground_color=(0, 0, 0, 1))
            self.zona_inputs.append(input_zona)
            layout_zonas.add_widget(input_zona)

        scrollview.add_widget(layout_zonas)
        layout_principal.add_widget(scrollview)
        
        # Botão Salvar e Enviar Boletim
        btn_salvar = Button(text="Enviar Boletim", size_hint_y=None, height=50, font_size=20,
                            background_color=(0.2, 0.2, 0.2, 1), color=(1, 1, 1, 1))
        btn_salvar.bind(on_press=self.enviar_dados)
        layout_principal.add_widget(btn_salvar)

        # Label para mensagens de status
        self.status_label = Label(text="", font_size=16, color=(1, 0, 0, 1))
        layout_principal.add_widget(self.status_label)

        return layout_principal

    def enviar_dados(self, instance):
        # Coleta os dados do cabeçalho e das zonas, preenchendo com valores vazios se necessário
        valores_intro = [campo.text if campo.text else "" for campo in self.intro_inputs]
        valores_zona = [zona.text if zona.text else "" for zona in self.zona_inputs]
        horario_salvo = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Monta o boletim como uma string
        dados_boletim = f"Boletim STANAG 4082 - {horario_salvo}\n"
        dados_boletim += "\n".join([f"{campo}: {valor}" for campo, valor in zip(
            ["METCMQ", "Latitude/Longitude", "Data e Duração", "Altura e Pressão MDP"], valores_intro)])
        dados_boletim += "\n" + "\n".join([f"Zona {i}: {valores_zona[i]}" for i in range(32)])

        # Obter IP e Porta e validar
        ip_destino = self.ip_input.text.strip()
        porta_destino = self.port_input.text.strip()

        if not self.validar_ip(ip_destino) or not porta_destino.isdigit():
            self.status_label.text = "IP ou Porta inválidos. Verifique os campos."
            return

        porta_destino = int(porta_destino)

        # Enviar dados via UDP
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.sendto(dados_boletim.encode(), (ip_destino, porta_destino))
            self.status_label.text = "Dados enviados com sucesso."
        except Exception as e:
            self.status_label.text = f"Erro ao enviar dados: {e}"

    def validar_ip(self, ip):
        # Expressão regular para verificar IPs válidos
        ip_regex = re.compile(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$")
        if ip_regex.match(ip):
            # Verifica se cada parte do IP está no intervalo de 0 a 255
            return all(0 <= int(part) <= 255 for part in ip.split("."))
        return False

StanagApp().run()