from kivymd.app import MDApp
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton
from kivy.core.window import Window
import sqlite3
from kivy.uix.popup import Popup
from kivy.uix.label import Label

# Definição de cores do tema
COLORS = {
    'primary': [0.2, 0.6, 0.86, 1],
    'secondary': [0.3, 0.3, 0.3, 1],
    'text': [0, 0, 0, 1],
    'background': [1, 1, 1, 1],
}

# Configura a cor de fundo da janela
Window.clearcolor = COLORS['background']

# Função para configurar o banco de dados
def configurar_banco():
    with sqlite3.connect("dados_meteorologicos.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS boletim (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                METCMQ TEXT, LaLaLaLoLoLo TEXT, YYGoGoGoG TEXT, hhhPdPdPd TEXT,
                zona0 TEXT, zona1 TEXT, zona2 TEXT, zona3 TEXT, zona4 TEXT,
                zona5 TEXT, zona6 TEXT, zona7 TEXT, zona8 TEXT, zona9 TEXT,
                zona10 TEXT, zona11 TEXT, zona12 TEXT, zona13 TEXT, zona14 TEXT,
                zona15 TEXT, zona16 TEXT, zona17 TEXT, zona18 TEXT, zona19 TEXT,
                zona20 TEXT, zona21 TEXT, zona22 TEXT, zona23 TEXT, zona24 TEXT,
                zona25 TEXT, zona26 TEXT, zona27 TEXT, zona28 TEXT, zona29 TEXT,
                zona30 TEXT, zona31 TEXT
            )
        """)
        conn.commit()

# Classe principal do app
class StanagApp(MDApp):
    def build(self):
        self.title = "Boletim STANAG 4082"
        self.theme_cls.primary_palette = "Blue"
        
        layout_principal = GridLayout(cols=1, padding=10, spacing=10)

        # Título da seção "Cabeçalho" como uma barra
        layout_principal.add_widget(MDRaisedButton(
            text="Cabeçalho",
            size_hint=(1, None),
            height=40,
            disabled=True,  # Desativa o botão para funcionar apenas como título visual
            md_bg_color=self.theme_cls.primary_color
        ))

        # Layout de introdução (Cabeçalho)
        layout_intro = GridLayout(cols=2, spacing=10, size_hint_y=None, height=200)
        self.intro_inputs = [MDTextField(hint_text=campo) for campo in ["METCMQ", "Latitude/Longitude", "Data e Duração", "Altura e Pressão MDP"]]
        for input_field in self.intro_inputs:
            layout_intro.add_widget(input_field)

        layout_principal.add_widget(layout_intro)

        # Título da seção "Corpo" como uma barra
        layout_principal.add_widget(MDRaisedButton(
            text="Corpo",
            size_hint=(1, None),
            height=40,
            disabled=True,
            md_bg_color=self.theme_cls.primary_color
        ))

        # Layout de zonas com rolagem
        scrollview = ScrollView(size_hint=(1, 1))
        layout_zonas = GridLayout(cols=1, padding=10, spacing=10, size_hint_y=None)
        layout_zonas.bind(minimum_height=layout_zonas.setter('height'))

        # Campos de entrada das zonas sem labels na lateral
        self.zona_inputs = []
        for zona in range(32):
            input_zona = MDTextField(
                hint_text=f"Zona {zona}",  # Nome da zona dentro do campo
                input_filter='int',       # Limita apenas a números inteiros
                input_type="number",      # Exibe teclado numérico
                multiline=False,
                size_hint_x=1             # O campo ocupa a largura total
            )
            self.zona_inputs.append(input_zona)
            layout_zonas.add_widget(input_zona)

        scrollview.add_widget(layout_zonas)
        layout_principal.add_widget(scrollview)

        # Botão para salvar
        btn_salvar = MDRaisedButton(
            text="Salvar Boletim",
            size_hint=(0.8, None),
            height=50,
            pos_hint={"center_x": 0.5},
            on_press=self.salvar_dados
        )
        layout_principal.add_widget(btn_salvar)

        return layout_principal

    def salvar_dados(self, instance):
        # 1. Coleta e valida os dados dos campos de introdução (campos principais)
        valores_intro = []
        for i, campo in enumerate(self.intro_inputs):
            texto = campo.text.strip()
            # Verifica se o campo está vazio ou se não tem exatamente 6 caracteres
            if not texto or len(texto) != 6:
                popup = Popup(
                    title="Erro",
                    content=Label(text=f"O campo '{campo.hint_text}' deve conter exatamente 6 caracteres."),
                    size_hint=(0.8, 0.2)
                )
                popup.open()
                return
            valores_intro.append(texto)

        # 2. Coleta e valida os dados dos campos de zona
        valores_zona = []
        for i, input_zona in enumerate(self.zona_inputs):
            texto_zona = input_zona.text.strip()
            # Se o campo não estiver vazio, valida que ele tem exatamente 16 caracteres numéricos
            if texto_zona:
                if len(texto_zona) != 16 or not texto_zona.isdigit():
                    popup = Popup(
                        title="Erro",
                        content=Label(text=f"O campo Zona {i} deve conter exatamente 16 caracteres numéricos."),
                        size_hint=(0.8, 0.2)
                    )
                    popup.open()
                    return
            valores_zona.append(texto_zona)

        # 3. Prepara os dados para inserção no banco
        valores = valores_intro + valores_zona

        # 4. Insere os dados no banco de dados
        try:
            with sqlite3.connect("dados_meteorologicos.db") as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO boletim (
                        METCMQ, LaLaLaLoLoLo, YYGoGoGoG, hhhPdPdPd,
                        zona0, zona1, zona2, zona3, zona4, zona5,
                        zona6, zona7, zona8, zona9, zona10, zona11,
                        zona12, zona13, zona14, zona15, zona16, zona17,
                        zona18, zona19, zona20, zona21, zona22, zona23,
                        zona24, zona25, zona26, zona27, zona28, zona29,
                        zona30, zona31
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, valores)
                conn.commit()

            # Feedback para o usuário
            popup = Popup(
                title="Sucesso",
                content=Label(text="Boletim salvo com sucesso!"),
                size_hint=(0.8, 0.2)
            )
            popup.open()

        except sqlite3.Error as e:
            # Tratamento de erro em caso de falha no salvamento
            popup = Popup(
                title="Erro de Banco de Dados",
                content=Label(text=f"Erro ao salvar os dados: {e}"),
                size_hint=(0.8, 0.2)
            )
            popup.open()

# Inicializa o banco de dados e roda o app
configurar_banco()
StanagApp().run()