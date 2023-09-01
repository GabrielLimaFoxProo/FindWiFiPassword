import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.uix.textinput import TextInput
from kivy.core.audio import SoundLoader
import subprocess
import time

class FindWiFiPassword(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical')

        self.add_logo()
        self.add_sound()
        self.show_logo_animation()

        return self.layout

    def add_logo(self):
        logo_path = os.path.join("resources", "logo.png")
        self.logo = Image(
            source=logo_path,
            size_hint=(1, 1),
            opacity=0  # Começa com opacidade 0 (invisível)
        )
        if not self.logo.texture:
            print("Logo image not loaded properly")

    def add_sound(self):
        sound_path = os.path.join("resources", "som.mp3")
        self.sound = SoundLoader.load(sound_path)
        if not self.sound:
            print("Sound not loaded properly")

    def play_sound(self):
        if self.sound:
            self.sound.play()

    def show_logo_animation(self):
        self.layout.clear_widgets()  # Limpa a tela
        self.layout.add_widget(self.logo)
        self.play_sound()  # Inicia a reprodução do som
        self.logo_opacity_animation(start_opacity=0, end_opacity=1, duration=2, callback=self.show_main_interface)

    def logo_opacity_animation(self, start_opacity, end_opacity, duration, callback):
        animation_steps = int(duration * 60)  # 60 frames por segundo
        opacity_delta = (end_opacity - start_opacity) / animation_steps

        def update_opacity(dt):
            self.logo.opacity += opacity_delta
            if opacity_delta > 0 and self.logo.opacity >= end_opacity:
                Clock.unschedule(update_opacity)
                callback()

        Clock.schedule_interval(update_opacity, 1 / 60)

    def show_main_interface(self):
        Clock.schedule_once(self.add_buttons_and_inputs, 5)  # Espera 5 segundos e adiciona botões e entradas

    def add_buttons_and_inputs(self, dt):
        self.layout.clear_widgets()  # Limpa a tela
        self.add_buttons()
        self.add_profile_inputs()
        self.add_output_area()

    def add_buttons(self):
        button_layout = BoxLayout(orientation='horizontal', size_hint=(0.4, 0.1))
        
        btn_show_profiles = Button(text='Redes Salvas')
        btn_show_profiles.bind(on_press=self.show_profiles)
        button_layout.add_widget(btn_show_profiles)

        btn_get_password = Button(text='Obter Senha')
        btn_get_password.bind(on_press=self.show_password_input)
        button_layout.add_widget(btn_get_password)

        btn_exit = Button(text='Sair')
        btn_exit.bind(on_press=self.exit_app)
        button_layout.add_widget(btn_exit)

        self.layout.add_widget(button_layout)

    def add_profile_inputs(self):
        input_layout = BoxLayout(orientation='vertical', size_hint=(0.4, 0.1))

        self.profile_inputs = []
        for i in range(1):  # Adicione quantos campos de entrada você desejar
            profile_input = TextInput(hint_text=f'Nome da Rede')
            self.profile_inputs.append(profile_input)
            input_layout.add_widget(profile_input)

        self.layout.add_widget(input_layout)

    def add_output_area(self):
        self.output_scrollview = ScrollView()
        self.output_label = Label(
            text='',
            valign='top',  # Alinhe o texto no topo
            halign='left',
            text_size=(None, None),
            size_hint=(1, 1.7),  # Ajuste o size_hint para se expandir horizontalmente
        )
        self.output_scrollview.add_widget(self.output_label)
        self.layout.add_widget(self.output_scrollview)

    def show_profiles(self, instance):
        process = subprocess.Popen('netsh wlan show profiles', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate()
        self.output_label.text = stdout
        self.output_scrollview.scroll_y = 1  # Role para o topo

    def show_password_input(self, instance):
        commands = [
            f'netsh wlan show profile name="{name}" key=clear' for name in self.get_profile_names() if name.strip()
        ]

        results = []
        for cmd in commands:
            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = process.communicate()
            results.append(stdout)
            results.append(stderr)
            time.sleep(1)

        self.output_label.text = '\n'.join(results)
        self.output_scrollview.scroll_y = 1  # Role para o topo

    def get_profile_names(self):
        return [input_field.text for input_field in self.profile_inputs]

    def exit_app(self, instance):
        App.get_running_app().stop()

if __name__ == '__main__':
    FindWiFiPassword().run()
