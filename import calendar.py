import calendar
import datetime
import threading
import time
import tkinter as tk
from tkinter import ttk
from plyer import notification
import pystray
from PIL import Image, ImageDraw
import sys
# Uygulama ikonu için masaüstündeki fotoğrafı yükle




def get_second_workday(year, month):
    c = calendar.Calendar()
    workdays = [day for day in c.itermonthdates(year, month)
                if day.month == month and day.weekday() < 5]  # 0=Mon, 4=Fri
    return workdays[1]  # 2. iş günü

def show_notification():
    notification.notify(
        title="2. İş Günü Bildirimi",
        message="Bugün ayın 2. iş günü!",
        timeout=10
    )

def schedule_notification():
    now = datetime.datetime.now()
    today = now.date()
    second_workday = get_second_workday(today.year, today.month)
    if today == second_workday:
        # Bilgisayar açıldığında hemen bildir
        show_notification()
        # 5-10 dk sonra tekrar bildir
        threading.Timer(300, show_notification).start()  # 5 dakika sonra
    # Ertesi gün tekrar kontrol et
    tomorrow = now + datetime.timedelta(days=1)
    midnight = datetime.datetime.combine(tomorrow.date(), datetime.time(0, 1))
    seconds_until_midnight = (midnight - now).total_seconds()
    threading.Timer(seconds_until_midnight, schedule_notification).start()

def create_image():
    # Basit bir kırmızı daireli simge
    image = Image.new('RGB', (64, 64), (255, 255, 255))
    dc = ImageDraw.Draw(image)
    dc.ellipse((16, 16, 48, 48), fill=(255, 0, 0))
    return image

class CalendarApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("2. İş Günü Takvimi")
        self.root.protocol("WM_DELETE_WINDOW", self.hide_window)
        self.is_tray = False
        self.tray_icon = None
        self.setup_ui()

    def setup_ui(self):
        now = datetime.datetime.now()
        year, month = now.year, now.month
        self.second_workday = get_second_workday(year, month)
        cal = calendar.monthcalendar(year, month)
        self.tree = ttk.Treeview(self.root, columns=[str(i) for i in range(7)], show='headings', height=len(cal))
        for i, day in enumerate(['Pzt', 'Sal', 'Çar', 'Per', 'Cum', 'Cmt', 'Paz']):
            self.tree.heading(str(i), text=day)
            self.tree.column(str(i), width=30, anchor='center')
        for week in cal:
            row = []
            tags = []
            for i, day in enumerate(week):
                if day == 0:
                    row.append('')
                    tags.append('')
                else:
                    d = datetime.date(year, month, day)
                    if d == self.second_workday:
                        row.append(str(day))
                        tags.append('redcell')
                    else:
                        row.append(str(day))
                        tags.append('')
            item_id = self.tree.insert('', 'end', values=row)
            # Sadece 2. iş günü hücresini kırmızıya boya
            for idx, tag in enumerate(tags):
                if tag == 'redcell':
                    self.tree.tag_configure(f'redcell_{item_id}_{idx}', foreground='red')
                    self.tree.set(item_id, str(idx), row[idx])
                    self.tree.item(item_id, tags=(f'redcell_{item_id}_{idx}',))
        self.tree.pack()

    def hide_window(self):
        self.root.iconify()  # Sadece alta küçült
        # Eğer system tray özelliği de istenirse, aşağıdaki satırı ekleyebilirsiniz:
        # if not self.is_tray:
        #     self.show_tray_icon()

    def show_window(self, icon=None, item=None):
        self.root.after(0, self.root.deiconify)
        if self.tray_icon:
            self.tray_icon.stop()
            self.is_tray = False

    def quit_app(self, icon=None, item=None):
        if self.tray_icon:
            self.tray_icon.stop()
        self.root.quit()
        sys.exit()

    def show_tray_icon(self):
        image = create_image()
        menu = pystray.Menu(
            pystray.MenuItem('Göster', self.show_window),
            pystray.MenuItem('Kapat', self.quit_app)
        )
        self.tray_icon = pystray.Icon("2. İş Günü Takvimi", image, "2. İş Günü Takvimi", menu)
        self.is_tray = True
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    # Arka planda bildirim zamanlayıcıyı başlat
    threading.Thread(target=schedule_notification, daemon=True).start()
    # Takvim arayüzünü başlat
    app = CalendarApp()
    app.run()