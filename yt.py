from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.progressbar import ProgressBar
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
import yt_dlp
import os
import threading
import re
from datetime import datetime

class YouTubeDownloader(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = dp(10)
        self.padding = [dp(20), dp(30), dp(20), dp(20)]
        
        # App Header with Credits
        header_layout = BoxLayout(orientation='vertical', size_hint=(1, 0.2), spacing=dp(5))
        
        title_label = Label(
            text='YouTube Downloader Pro',
            font_size=dp(24),
            bold=True,
            color=get_color_from_hex('#FFFFFF'),
            size_hint=(1, 0.6)
        )
        
        credits_label = Label(
            text='Developed by Hamza Sami',
            font_size=dp(14),
            italic=True,
            color=get_color_from_hex('#B0BEC5'),
            size_hint=(1, 0.4)
        )
        
        header_layout.add_widget(title_label)
        header_layout.add_widget(credits_label)
        self.add_widget(header_layout)

        # URL Input Section
        url_section = BoxLayout(orientation='vertical', size_hint=(1, 0.15), spacing=dp(5))
        
        url_label = Label(
            text='Enter YouTube URL:',
            font_size=dp(16),
            color=get_color_from_hex('#FFFFFF'),
            size_hint=(1, 0.3),
            text_size=(None, None),
            halign='left'
        )
        
        self.url_input = TextInput(
            hint_text='https://www.youtube.com/watch?v=...',
            size_hint=(1, 0.7),
            multiline=False,
            background_color=get_color_from_hex('#37474F'),
            foreground_color=get_color_from_hex('#FFFFFF'),
            cursor_color=get_color_from_hex('#4CAF50'),
            font_size=dp(14),
            padding=[dp(10), dp(10)]
        )
        
        url_section.add_widget(url_label)
        url_section.add_widget(self.url_input)
        self.add_widget(url_section)

        # Quality Selection
        quality_section = BoxLayout(orientation='vertical', size_hint=(1, 0.12), spacing=dp(5))
        
        quality_label = Label(
            text='Select Quality:',
            font_size=dp(16),
            color=get_color_from_hex('#FFFFFF'),
            size_hint=(1, 0.4),
            halign='left'
        )
        
        self.quality_spinner = Spinner(
            text='Best Quality',
            values=['Best Quality', 'High (720p)', 'Medium (480p)', 'Low (360p)'],
            size_hint=(1, 0.6),
            background_color=get_color_from_hex('#4CAF50'),
            color=get_color_from_hex('#FFFFFF'),
            font_size=dp(14)
        )
        
        quality_section.add_widget(quality_label)
        quality_section.add_widget(self.quality_spinner)
        self.add_widget(quality_section)

        # Download Buttons
        btn_layout = BoxLayout(orientation='horizontal', spacing=dp(15), size_hint=(1, 0.15))
        
        self.mp4_btn = Button(
            text='📹 Download Video (MP4)',
            background_color=get_color_from_hex('#FF5722'),
            color=get_color_from_hex('#FFFFFF'),
            font_size=dp(16),
            bold=True
        )
        
        self.mp3_btn = Button(
            text='🎵 Download Audio (MP3)',
            background_color=get_color_from_hex('#4CAF50'),
            color=get_color_from_hex('#FFFFFF'),
            font_size=dp(16),
            bold=True
        )
        
        btn_layout.add_widget(self.mp4_btn)
        btn_layout.add_widget(self.mp3_btn)
        self.add_widget(btn_layout)

        # Progress Section
        progress_section = BoxLayout(orientation='vertical', size_hint=(1, 0.12), spacing=dp(5))
        
        self.progress = ProgressBar(
            max=100, 
            size_hint=(1, 0.5),
            value=0
        )
        
        self.progress_label = Label(
            text='0%',
            font_size=dp(14),
            color=get_color_from_hex('#B0BEC5'),
            size_hint=(1, 0.5)
        )
        
        progress_section.add_widget(self.progress)
        progress_section.add_widget(self.progress_label)
        self.add_widget(progress_section)

        # Status Label
        self.status = Label(
            text='Ready to download 🚀',
            size_hint=(1, 0.1),
            font_size=dp(16),
            color=get_color_from_hex('#4CAF50'),
            text_size=(None, None)
        )
        self.add_widget(self.status)

        # Info Section (Scrollable)
        info_scroll = ScrollView(size_hint=(1, 0.16))
        self.info_label = Label(
            text='Paste a YouTube URL above and select your preferred quality.\nSupports videos, playlists, and live streams.',
            font_size=dp(12),
            color=get_color_from_hex('#B0BEC5'),
            text_size=(None, None),
            halign='center',
            valign='top'
        )
        info_scroll.add_widget(self.info_label)
        self.add_widget(info_scroll)

        # Bind buttons
        self.mp4_btn.bind(on_press=self.download_mp4)
        self.mp3_btn.bind(on_press=self.download_mp3)
        
        # Set background color
        with self.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(*get_color_from_hex('#263238'))
            self.rect = Rectangle(size=self.size, pos=self.pos)
            self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def validate_url(self, url):
        """Validate YouTube URL"""
        youtube_regex = re.compile(
            r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/'
            r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
        )
        return youtube_regex.match(url) is not None

    def get_quality_format(self):
        """Get format based on quality selection"""
        quality = self.quality_spinner.text
        if quality == 'High (720p)':
            return 'best[height<=720]'
        elif quality == 'Medium (480p)':
            return 'best[height<=480]'
        elif quality == 'Low (360p)':
            return 'best[height<=360]'
        else:
            return 'best'

    def progress_hook(self, d):
        """Progress callback for yt-dlp"""
        if d['status'] == 'downloading':
            if 'total_bytes' in d:
                percent = (d['downloaded_bytes'] / d['total_bytes']) * 100
            elif 'total_bytes_estimate' in d:
                percent = (d['downloaded_bytes'] / d['total_bytes_estimate']) * 100
            else:
                percent = 0
            
            Clock.schedule_once(lambda dt: self.update_progress_ui(percent))
        elif d['status'] == 'finished':
            Clock.schedule_once(lambda dt: self.update_progress_ui(100))

    def update_progress_ui(self, percent):
        """Update progress bar and label"""
        self.progress.value = percent
        self.progress_label.text = f'{int(percent)}%'

    def update_status(self, message, color='#4CAF50'):
        """Update status label with color"""
        Clock.schedule_once(lambda dt: setattr(self.status, 'text', message))
        Clock.schedule_once(lambda dt: setattr(self.status, 'color', get_color_from_hex(color)))

    def download_mp4(self, instance):
        url = self.url_input.text.strip()
        if not url:
            self.show_popup('❌ Error', 'Please enter a YouTube URL')
            return
        
        if not self.validate_url(url):
            self.show_popup('❌ Invalid URL', 'Please enter a valid YouTube URL')
            return

        self.mp4_btn.disabled = True
        self.mp3_btn.disabled = True
        threading.Thread(target=self._download_mp4, args=(url,)).start()

    def _download_mp4(self, url):
        try:
            self.update_status('🔍 Fetching video information...', '#FF9800')
            
            download_path = os.path.join(os.path.expanduser('~'), 'Downloads', 'YouTube_Downloads')
            os.makedirs(download_path, exist_ok=True)
            
            ydl_opts = {
                'format': self.get_quality_format(),
                'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
                'progress_hooks': [self.progress_hook],
                'no_warnings': True,
                'extract_flat': False,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                title = info.get('title', 'Unknown')
                
                self.update_status(f'⬇️ Downloading: {title[:30]}...', '#2196F3')
                ydl.download([url])
                
                self.update_status(f'✅ Video saved successfully!\nLocation: {download_path}', '#4CAF50')
                Clock.schedule_once(lambda dt: setattr(self.progress, 'value', 0), 3)
                Clock.schedule_once(lambda dt: setattr(self.progress_label, 'text', '0%'), 3)

        except Exception as e:
            error_msg = f'Download failed: {str(e)}'
            self.update_status('❌ Download failed!', '#F44336')
            Clock.schedule_once(lambda dt: self.show_popup('❌ Error', error_msg))
        finally:
            Clock.schedule_once(lambda dt: setattr(self.mp4_btn, 'disabled', False))
            Clock.schedule_once(lambda dt: setattr(self.mp3_btn, 'disabled', False))

    def download_mp3(self, instance):
        url = self.url_input.text.strip()
        if not url:
            self.show_popup('❌ Error', 'Please enter a YouTube URL')
            return
        
        if not self.validate_url(url):
            self.show_popup('❌ Invalid URL', 'Please enter a valid YouTube URL')
            return

        self.mp4_btn.disabled = True
        self.mp3_btn.disabled = True
        threading.Thread(target=self._download_mp3, args=(url,)).start()

    def _download_mp3(self, url):
        try:
            self.update_status('🔍 Fetching audio information...', '#FF9800')
            
            download_path = os.path.join(os.path.expanduser('~'), 'Downloads', 'YouTube_Downloads')
            os.makedirs(download_path, exist_ok=True)
            
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
                'progress_hooks': [self.progress_hook],
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'no_warnings': True,
                'extract_flat': False,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                title = info.get('title', 'Unknown')
                
                self.update_status(f'⬇️ Downloading: {title[:30]}...', '#2196F3')
                ydl.download([url])
                
                self.update_status(f'🎵 Audio saved successfully!\nLocation: {download_path}', '#4CAF50')
                Clock.schedule_once(lambda dt: setattr(self.progress, 'value', 0), 3)
                Clock.schedule_once(lambda dt: setattr(self.progress_label, 'text', '0%'), 3)

        except Exception as e:
            error_msg = f'Download failed: {str(e)}'
            self.update_status('❌ Download failed!', '#F44336')
            Clock.schedule_once(lambda dt: self.show_popup('❌ Error', error_msg))
        finally:
            Clock.schedule_once(lambda dt: setattr(self.mp4_btn, 'disabled', False))
            Clock.schedule_once(lambda dt: setattr(self.mp3_btn, 'disabled', False))

    def show_popup(self, title, message):
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(20))
        
        msg_label = Label(
            text=message,
            font_size=dp(14),
            color=get_color_from_hex('#FFFFFF'),
            text_size=(dp(250), None),
            halign='center',
            valign='middle'
        )
        
        ok_btn = Button(
            text='OK',
            size_hint=(1, 0.3),
            background_color=get_color_from_hex('#4CAF50'),
            color=get_color_from_hex('#FFFFFF'),
            font_size=dp(16)
        )
        
        content.add_widget(msg_label)
        content.add_widget(ok_btn)
        
        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.85, 0.5),
            background_color=get_color_from_hex('#37474F'),
            title_color=get_color_from_hex('#FFFFFF')
        )
        
        ok_btn.bind(on_press=popup.dismiss)
        popup.open()

class YouTubeDownloaderApp(App):
    def build(self):
        self.title = 'YouTube Downloader Pro - by Hamza Sami'
        self.icon = 'icon.png'  # Add your app icon here
        return YouTubeDownloader()

if __name__ == '__main__':
    YouTubeDownloaderApp().run()