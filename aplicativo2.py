from kivymd.app import MDApp
from kivy.uix.scrollview import ScrollView
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.list import OneLineIconListItem, IconLeftWidget
from kivy.core.window import Window
import sqlite3

# Configuração de cor do fundo para melhorar a visibilidade
Window.clearcolor = (0.95, 0.95, 0.95, 1)

# Função para decodificar a string da zona
def decodificar_dados_zona(zona_dados):
    """
    Decodifica uma string de 16 caracteres representando dados meteorológicos de uma zona.
    Exemplo de entrada: "0031000429770972"
    """
    try:
        # Extrai cada segmento da string
        zona_numero = zona_dados[0:2]  # Zona número (ex: "00" para 0 metros acima do MDP)
        direcao_vento = int(zona_dados[2:5])*10  # Direção do vento em mils (ex: "310" -> 310 mils)
        velocidade_vento = int(zona_dados[5:8])  # Velocidade do vento em nós, multiplicada por 10
        temperatura = int(zona_dados[8:12]) / 10.0  # Temperatura em décimos de Kelvin, dividida por 10
        pressao = int(zona_dados[12:16])  # Pressão em milibares (ex: "0972" -> 972 mb)

        # Retorna as informações formatadas
        return [
            (f"Zona Número: {zona_numero} (indica {int(zona_numero) * 100} metros acima do MDP)", "map-marker"),
            (f"Direção do Vento: {direcao_vento} mils", "compass"),
            (f"Velocidade do Vento: {velocidade_vento} nós", "weather-windy"),
            (f"Temperatura Virtual do Ar: {temperatura:.1f} K", "thermometer"),
            (f"Pressão do Ar: {pressao} mb", "gauge")
        ]
    except (ValueError, IndexError) as e:
        # Retorna erro caso a string não esteja no formato esperado
        return [(f"Erro na decodificação dos dados: {e}", "alert")]

# Função para buscar dados do boletim a partir da altura no banco de dados
def buscar_dados_altura_do_banco(altura):
    try:
        with sqlite3.connect("dados_meteorologicos.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM boletim ORDER BY id DESC LIMIT 1")
            resultado = cursor.fetchone()

            if not resultado:
                return [("Nenhum boletim encontrado no banco de dados.", "alert")]

            # Mapeamento das zonas para alturas conforme a tabela fornecida
            zonas = {
                "00": (0, 0),
                "01": (0, 200),
                "02": (200, 500),
                "03": (500, 1000),
                "04": (1000, 1500),
                "05": (1500, 2000),
                "06": (2000, 2500),
                "07": (2500, 3000),
                "08": (3000, 3500),
                "09": (3500, 4000),
                "10": (4000, 4500),
                "11": (4500, 5000),
                "12": (5000, 5500),
                "13": (6000, 7000),
                "14": (7000, 8000),
                "15": (8000, 9000),
                "16": (9000, 10000),
                "17": (10000, 11000),
                "18": (11000, 12000),
                "19": (12000, 13000),
                "20": (13000, 14000),
                "21": (14000, 15000),
                "22": (15000, 16000),
                "23": (16000, 17000),
                "24": (17000, 18000),
                "25": (18000, 19000),
                "26": (19000, 20000),
                "27": (20000, 22000),
                "28": (22000, 24000),
                "29": (24000, 26000),
                "30": (26000, 28000),
                "31": (28000, 30000),
            }
            
            # Determina a zona correta com base na altura
            zona_encontrada = None
            for zona, (altura_min, altura_max) in zonas.items():
                if altura_min <= altura <= altura_max:
                    zona_encontrada = zona
                    break

            if zona_encontrada is None:
                return [("Altura fora do intervalo suportado. Use entre 0 e 30000 metros.", "alert")]

            # Localiza os dados da zona encontrada no banco de dados
            zona_index = int(zona_encontrada) + 4  # Offset para o cabeçalho
            zona_dados = resultado[zona_index]

            # Decodifica os dados da zona
            return decodificar_dados_zona(zona_dados)
    except sqlite3.Error as e:
        return [(f"Erro ao acessar o banco de dados: {e}", "alert")]

# Interface KivyMD para o App de Altura
class AlturaApp(MDApp):
    def build(self):
        self.title = "Consulta de Dados STANAG 4082"
        
        # Layout principal
        layout_principal = MDBoxLayout(orientation='vertical', padding=20, spacing=20)
        
        # Título da aplicação
        titulo = MDLabel(
            text="Consulta de Altura - STANAG 4082",
            halign="center",
            font_style="H5",
            theme_text_color="Primary"
        )
        layout_principal.add_widget(titulo)
        
        # Área de status inicial para exibir se há dados disponíveis
        self.status_inicial = MDLabel(
            text="Nenhum boletim encontrado no banco de dados.",
            halign="center",
            font_style="Body1",
            theme_text_color="Secondary"
        )
        layout_principal.add_widget(self.status_inicial)

        # Campo de entrada para altura
        self.entrada_altura = MDTextField(
            hint_text="Digite a altura em metros (máximo 30000)",
            helper_text="Exemplo: 5000",
            helper_text_mode="on_focus",
            input_filter="int",  # Apenas números inteiros
            font_size=18,
            size_hint_x=0.9,
            pos_hint={"center_x": 0.5},
            on_text_validate=self.validar_altura
        )
        layout_principal.add_widget(self.entrada_altura)

        # Botão para buscar dados
        btn_buscar = MDRaisedButton(
            text="Buscar Dados",
            size_hint=(0.5, None),
            height=50,
            pos_hint={"center_x": 0.5},
            md_bg_color=self.theme_cls.primary_color,
            on_press=self.buscar_dados
        )
        layout_principal.add_widget(btn_buscar)

        # Área para exibir o resultado com rolagem
        scrollview = ScrollView(size_hint=(1, 0.6))
        self.resultado_layout = MDBoxLayout(orientation="vertical", spacing=10, padding=10, size_hint_y=None)
        self.resultado_layout.bind(minimum_height=self.resultado_layout.setter('height'))
        scrollview.add_widget(self.resultado_layout)
        
        layout_principal.add_widget(scrollview)
        
        return layout_principal

    # Função de validação para garantir que o valor seja até 30.000
    def validar_altura(self, instance):
        altura_texto = self.entrada_altura.text.strip()
        if altura_texto.isdigit():
            altura = int(altura_texto)
            if altura > 30000:
                self.entrada_altura.text = "30000"
                self.mostrar_resultado([("A altura máxima permitida é 30.000 metros.", "alert")])

    # Função para buscar e exibir dados com base na altura
    def buscar_dados(self, instance):
        altura_texto = self.entrada_altura.text.strip()
        if not altura_texto.isdigit():
            self.mostrar_resultado([("Por favor, insira uma altura válida em metros.", "alert")])
            return
        altura = int(altura_texto)
        resultado = buscar_dados_altura_do_banco(altura)
        
        # Atualiza a área de status com as informações meteorológicas
        self.atualizar_status_inicial(resultado)
        self.mostrar_resultado(resultado)

    # Função para atualizar o status inicial com informações meteorológicas
    def atualizar_status_inicial(self, dados_meteorologicos):
        if dados_meteorologicos and isinstance(dados_meteorologicos[0], tuple):
            # Atualiza o status inicial com a primeira informação
            self.status_inicial.text = "\n".join([dado[0] for dado in dados_meteorologicos[:4]])

    def mostrar_resultado(self, resultado):
        # Limpa resultados anteriores
        self.resultado_layout.clear_widgets()

        # Exibe cada linha de resultado com um ícone
        for texto, icone in resultado:
            item = OneLineIconListItem(text=texto)
            item.add_widget(IconLeftWidget(icon=icone))
            self.resultado_layout.add_widget(item)

# Inicializa o app
AlturaApp().run()