import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import json
import os
import subprocess
import re
import random
import shutil  
from datetime import datetime, timedelta
import webbrowser
import smtplib
import ssl
import certifi
from email.message import EmailMessage
import secrets
import string
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage


# All extra files
BACKEND_EXE = "backend.exe" if os.name == 'nt' else "./backend"
ASSETS_DIR = "book_covers"

# Book categories and their subcategories
CATEGORIES_CONFIG = {
    "hudozhnya": {
        "label": "Художня література",
        "subs": {"all": "Всі художні", "romance": "Романтична проза", "detective": "Детективи", "thriller": "Трилери", "scifi": "Фантастика", "classic": "Класична література"}
    },
    "applied": {
        "label": "Прикладна література",
        "subs": {"all": "Всі прикладні", "history": "Історія", "psychology": "Психологія", "selfhelp": "Саморозвиток", "business": "Бізнес"}
    },
    "kids": {
        "label": "Дитяча література",
        "subs": {"all": "Всі дитячі", "0-4": "До 4 років", "4-6": "4-6 років", "7-12": "7-12 років", "school": "Шкільна"}
    },
    "ebooks": {
        "label": "E-Books",
        "subs": {"hudozhnya": "Художні", "applied": "Прикладні", "kids": "Дитячі"}
    },
    "audio": {
        "label": "Аудіокниги",
        "subs": {"hudozhnya": "Художні", "applied": "Прикладні", "kids": "Дитячі", "business": "Бізнес"}
    },
    "announce": {"label": "Анонси", "subs": {"all": "Всі анонси"}},
    "special": {"label": "Спецпропозиції", "subs": {"sale": "Знижки", "sets": "Комплекти", "new": "Новинки", "hit": "Хіти"}}
}

# Automail
SMTP_SERVER = "smtp.gmail.com" 
SMTP_PORT = 465
SENDER_EMAIL = "skdpublishinghouse@gmail.com"
SENDER_PASSWORD = "itpn hduj egcl jaix"

def generate_strong_password(length=10):
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()_+-="
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def send_email_real(to_email, new_password):
    subject = "Відновлення паролю у системі видавницва - SKD"
    body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background-color:#f4f4f7; padding:20px;">
        <div style="max-width:600px; margin:0 auto; background:#ffffff; border-radius:8px; padding:30px; border:1px solid #e5e5e5;">
      
        <h2 style="color:#333333; text-align:center;">Скидання пароля</h2>
      
        <p style="font-size:16px; color:#444444;">
            Вітаємо!
        </p>
      
        <p style="font-size:16px; color:#444444;">
            Ваш пароль було успішно скинуто на ваш запит.
        </p>

        <div style="background:#f0f3ff; padding:15px 20px; border-left:4px solid #4a6cf7; margin:20px 0; border-radius:5px;">
            <p style="font-size:16px; margin:0; color:#333333;">
            <strong>Ваш новий пароль:</strong> <span style="color:#4a6cf7;">{new_password}</span>
            </p>
        </div>

        <p style="font-size:16px; color:#444444;">
            З міркувань безпеки радимо змінити цей пароль після першого входу в систему.
        </p>

        <p style="font-size:16px; color:#444444;">
            Якщо ви не надсилали запит на скидання пароля, будь ласка, негайно зв’яжіться з нашою службою підтримки.
        </p>

        <hr style="margin:30px 0; border:0; border-top:1px solid #e5e5e5;">

        <p style="font-size:14px; color:#888888; text-align:center;">
            З повагою, <br>
            Команда підтримки
        </p>

        </div>
    </body>
    </html>
    """

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = SENDER_EMAIL
    msg['To'] = to_email

    # Add HTML text
    msg.add_alternative(body, subtype="html")

    try:
        context = ssl.create_default_context(cafile=certifi.where())
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Помилка відправки: {e}")
        return False

def send_order_email(to_email, order_id, cart_items, total_sum, bonuses_earned, address):
    
    msg = MIMEMultipart('related') 
    msg['Subject'] = f"Замовлення #{order_id} успішно прийнято!"
    msg['From'] = SENDER_EMAIL
    msg['To'] = to_email


    items_html_rows = ""
    images_to_attach = [] 

    for index, item in enumerate(cart_items):
        book_obj = item['obj'] 
        qty = item['qty']
        

        if isinstance(book_obj, Book):
            title = book_obj.title
            price = book_obj.price
            img_path = book_obj.image_path 
        else:
            title = book_obj.get('title', 'Комплект')
            price = book_obj.get('price', 0.0)
            img_path = book_obj.get('image', '')
        
        img_cid = f"img_{index}" 
        img_tag = ""
        
        if img_path and os.path.exists(img_path):
            images_to_attach.append((img_path, img_cid))
            img_tag = f'<img src="cid:{img_cid}" alt="Book" width="60" height="80" style="border-radius: 5px;">'
        else:
            img_tag = '<div style="width:60px; height:80px; background:#eee; text-align:center; line-height:80px;">📚</div>'

        items_html_rows += f"""
        <tr>
            <td style="padding: 10px; border-bottom: 1px solid #ddd;">{img_tag}</td>
            <td style="padding: 10px; border-bottom: 1px solid #ddd;">
                <b style="font-size: 16px; color: #333;">{title}</b>
            </td>
            <td style="padding: 10px; border-bottom: 1px solid #ddd; text-align: center;">x{qty}</td>
            <td style="padding: 10px; border-bottom: 1px solid #ddd; text-align: right;">
                <b>{price * qty:.2f} грн</b>
            </td>
        </tr>
        """

    # The letter 
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #f4f6f7; padding: 20px;">
        <div style="max_width: 600px; margin: 0 auto; background: #ffffff; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 10px rgba(0,0,0,0.1);">
            
            <div style="background-color: #2c3e50; padding: 20px; text-align: center; color: white;">
                <h1 style="margin: 0;">Book System</h1>
                <p style="margin: 5px 0 0; opacity: 0.8;">Ваше замовлення прийнято</p>
            </div>

            <div style="padding: 20px;">
                <p style="font-size: 16px;">Вітаємо! Ми вже готуємо ваші книги до відправки. </p>
                <div style="background: #ecf0f1; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
                    <p style="margin: 5px 0;"><b>Номер замовлення:</b> {order_id}</p>
                    <p style="margin: 5px 0;"><b>Адреса доставки:</b> {address}</p>
                </div>

                <table style="width: 100%; border-collapse: collapse;">
                    {items_html_rows}
                </table>

                <div style="margin-top: 20px; text-align: right;">
                    <p style="font-size: 18px; color: #27ae60;"><b>Нараховано бонусів: +{bonuses_earned}</b></p>
                    <h2 style="color: #e74c3c; margin: 10px 0;">Сума разом із довставкою: {total_sum:.2f} грн</h2>
                </div>
            </div>

            <div style="background-color: #eee; padding: 15px; text-align: center; font-size: 12px; color: #777;">
                Дякуємо, що обираєте нас! <br>
                Це автоматичний лист, відповідати не потрібно.
            </div>
        </div>
    </body>
    </html>
    """


    msg_alternative = MIMEMultipart('alternative')
    msg.attach(msg_alternative)
    msg_alternative.attach(MIMEText(html_content, 'html'))


    for img_path, img_cid in images_to_attach:
        try:
            with open(img_path, 'rb') as f:
                mime_img = MIMEImage(f.read())
                mime_img.add_header('Content-ID', f'<{img_cid}>')
                mime_img.add_header('Content-Disposition', 'inline')
                msg.attach(mime_img)
        except Exception as e:
            print(f"Не вдалося прикріпити фото {img_path}: {e}")

    # Go
    try:
        context = ssl.create_default_context(cafile=certifi.where())
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        print("HTML лист відправлено!")
        return True
    except Exception as e:
        print(f"Помилка email: {e}")
        return False

def fix_paste(entry):
    def paste(event):
        try:
            entry.insert(tk.INSERT, entry.clipboard_get())
        except tk.TclError:
            pass
        return "break"

    entry.bind("<Control-v>", paste)
    entry.bind("<Control-V>", paste)

    entry.bind("<Button-3>", paste)





# DATA

class Book:
    def __init__(self, data):
        self.isbn = data.get("isbn", "")
        self.title = data.get("title", "Без назви")
        self.author_name = data.get("author_name", "")
        self.author_surname = data.get("author_surname", "")
        self.category = data.get("category", "other")
        self.subcategory = data.get("subcategory", "")
        
        self.format = data.get("format", "physical") 
        
        self.image_path = data.get("image_path", "") or data.get("image", "")
        self.description = data.get("description", "")
        self.excerpt = data.get("excerpt", "")
        
        self.price = float(data.get("price", 0.0))
        self.discount_percent = int(data.get("discount_percent", 0))
        
        self.reviews = data.get("reviews", [])
        self.ratings = data.get("ratings", [])
        self.year = data.get("year", "-") 
        
        self.pages = data.get("pages", "-")
        self.weight = data.get("weight", "-")
        self.duration = data.get("duration", "-")
        self.stock = int(data.get("stock", 0))


    def get_final_price(self):
        if self.discount_percent > 0:
            return self.price * (1 - self.discount_percent / 100)
        return self.price

    def get_full_author(self):

        return f"{self.author_name} {self.author_surname}"

    def get_avg_rating(self):
        if not self.ratings:
            return 0.0
        return sum(self.ratings) / len(self.ratings)

    def is_available(self, quantity=1):
        return self.stock >= quantity

    def to_dict(self):
        return {
            "isbn": self.isbn,
            "title": self.title,
            "author_name": self.author_name,
            "author_surname": self.author_surname,
            "category": self.category,
            "subcategory": self.subcategory,
            "format": self.format, 
            "image_path": self.image_path,
            "price": self.price,
            "stock": self.stock, 
            "discount_percent": self.discount_percent,
            "description": self.description,
            "excerpt": self.excerpt,
            "year": self.year,
            "pages": self.pages, 
            "weight": self.weight, 
            "duration": self.duration, 
            "reviews": self.reviews,
            "ratings": self.ratings
        }

class PhysicalBook(Book):
    def __init__(self, data):
        super().__init__(data)
        self.format = "physical"
        self.pages = data.get("pages", 0)
        self.weight = data.get("weight", 0)
        self.stock = int(data.get("stock", 0))

    pass

class Ebook(Book):
    def __init__(self, data):
        super().__init__(data)
        self.format = "electronic"
        self.pages = data.get("pages", 0)
        
    def is_available(self, quantity=1):
        return True

class AudioBook(Book):
    def __init__(self, data):
        super().__init__(data)
        self.format = "audio"
        self.duration = data.get("duration", "-")

    def is_available(self, quantity=1):
        return True


class DataManager:
    def __init__(self):
        if not os.path.exists(ASSETS_DIR):
            os.makedirs(ASSETS_DIR)

    def load(self):
        try:
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            result = subprocess.check_output(
                [BACKEND_EXE, "get_all"], 
                text=True, 
                encoding='utf-8', 
                startupinfo=startupinfo
            )

            data = json.loads(result)
            
            if "books" in data:
                book_objects = []
                for item in data["books"]:
                    fmt = item.get("format", "physical")
                    if fmt == "electronic":
                        book_objects.append(Ebook(item))
                    elif fmt == "audio":
                        book_objects.append(AudioBook(item))
                    else:
                        book_objects.append(PhysicalBook(item))
                
                data["books"] = book_objects
            
            return data
            
        except Exception as e:
            print(f"Data Load Error: {e}")
            return {}

    def save(self, data):

        try:
            data_to_save = data.copy()
            
            if "books" in data_to_save:
                data_to_save["books"] = [
                    b.to_dict() if isinstance(b, Book) else b 
                    for b in data_to_save["books"]
                ]

            json_str = json.dumps(data_to_save, ensure_ascii=False)
            
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                
            subprocess.run(
                [BACKEND_EXE, "save_all_stdin"], 
                input=json_str,       
                text=True,            
                encoding='utf-8',      
                startupinfo=startupinfo,
                check=True 
            )
            
        except Exception as e:
            print(f"Data Save Error: {e}")
            messagebox.showerror("Критична помилка", f"Не вдалося зберегти дані:\n{e}")

# IMORTANT APP CONTROL

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Information System for Managing a Book Publishing House")
        w, h = 1280, 810
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f'{w}x{h}+{int((sw-w)/2)}+{int((sh-h)/2)}')
        self.resizable(False, False)
        
        self.data_mgr = DataManager()
        self.user = None
        self.cart = [] 
        self.img_cache = {} 
        
        if not os.path.exists(BACKEND_EXE):
            messagebox.showwarning("System", "backend.exe відсутній! Розрахунки емулюються.")

        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)
        self.current_frame = None

        self.show("AuthFrame")

    def show(self, name, data=None):
        if self.current_frame:
            self.current_frame.destroy()
        try:
            cls = globals()[name]
            self.current_frame = cls(self.container, self, data) if data else cls(self.container, self)
            self.current_frame.pack(fill="both", expand=True)
        except KeyError:
            messagebox.showerror("Error", f"Screen {name} not found!")

    def cpp_exec(self, mode, *args):
        try:
            safe_args = []
            for a in args:
                s = str(a).replace(',', '.')
                if not re.match(r'^-?\d+(\.\d+)?$', s): s = "0"
                safe_args.append(s)
            cmd = [BACKEND_EXE, mode] + safe_args
            return subprocess.check_output(cmd, text=True).strip()
        except: return "0.00"

    def create_scrollable_frame(self, parent, bg_color="#f0f2f5"):
        canvas = tk.Canvas(parent, borderwidth=0, background=bg_color)
        frame = tk.Frame(canvas, background=bg_color)
        vsb = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        
        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        
        canvas.create_window((0,0), window=frame, anchor="nw", width=1250)
        
        def on_conf(event): canvas.configure(scrollregion=canvas.bbox("all"))
        frame.bind("<Configure>", on_conf)
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        return frame

    def create_scrolled_tree(self, parent, columns):
        f = tk.Frame(parent)
        f.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        vsb = ttk.Scrollbar(f, orient="vertical")
        hsb = ttk.Scrollbar(f, orient="horizontal")
        tree = ttk.Treeview(f, columns=columns, show="headings", yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        for c in columns:
            tree.heading(c, text=c); tree.column(c, width=100)
        vsb.config(command=tree.yview); hsb.config(command=tree.xview)
        vsb.pack(side=tk.RIGHT, fill=tk.Y); hsb.pack(side=tk.BOTTOM, fill=tk.X)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        return tree

    def load_image_to_label(self, parent, path, width=150, height=200):
        fr = tk.Frame(parent, bg="#bdc3c7", width=width, height=height)
        fr.pack_propagate(False) 
        
        valid_path = None
        if path:
            if os.path.exists(path): 
                valid_path = path
            elif os.path.exists(os.path.join(ASSETS_DIR, os.path.basename(path))): 
                valid_path = os.path.join(ASSETS_DIR, os.path.basename(path))
        
        if valid_path:
            try:
                if not valid_path.lower().endswith(('.png', '.gif', '.ppm', '.pgm')):
                    tk.Label(fr, text="Тільки PNG/GIF!", bg="#bdc3c7", fg="white", font=("Arial",8)).pack(expand=True)
                    return fr
                    
                img = tk.PhotoImage(file=valid_path)
                
                iw, ih = img.width(), img.height()
                if iw > width or ih > height:
                    factor = max(1, max(iw // width, ih // height))
                    img = img.subsample(factor, factor)
                
                l = tk.Label(fr, image=img, bg="white")
                l.image = img 
                l.pack(expand=True)
            except Exception as e:
                print(f"Img Error: {e}")
                tk.Label(fr, text="Помилка фото", bg="#bdc3c7", fg="white").pack(expand=True)
        else:
            tk.Label(fr, text="Немає фото", bg="#bdc3c7", fg="white").pack(expand=True)
        
        return fr
    
    def save_image_safe(self, source_path):
        if not source_path or not os.path.exists(source_path):
            return ""
        
        if not source_path.lower().endswith('.png'):
             messagebox.showwarning("Формат", "Будь ласка, використовуйте тільки .PNG файли!\n(Tkinter без PIL не підтримує JPG)")
             return ""

        try:
            ext = os.path.splitext(source_path)[1]
            new_name = f"cover_{random.randint(10000,99999)}{ext}"
            dest_path = os.path.join(ASSETS_DIR, new_name)
            shutil.copy(source_path, dest_path)
            return dest_path 
        except Exception as e:
            print(f"Copy Error: {e}")
            return source_path 

# AUTHENTICATION
class AuthFrame(tk.Frame):
    def __init__(self, parent, ctrl):
        super().__init__(parent, bg="#2c3e50"); self.ctrl = ctrl
        c = tk.Frame(self, bg="white", padx=40, pady=40, bd=2, relief="raised")
        c.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        tk.Label(c, text="📚 SKD BOOK STORE", font=("Impact", 24), bg="white", fg="#2c3e50").pack(pady=20)
        tk.Label(c, text="Логін:", bg="white").pack(anchor='w'); self.el = tk.Entry(c, width=35, font=("Arial",12)); self.el.pack(pady=5); fix_paste(self.el)
        tk.Label(c, text="Пароль:", bg="white").pack(anchor='w'); self.ep = tk.Entry(c, width=35, show="*", font=("Arial",12)); self.ep.pack(pady=5); fix_paste(self.ep)
        tk.Button(c, text="ВХІД", bg="#e67e22", fg="white", font=("bold",11), command=self.login).pack(pady=20, fill=tk.X)
        l = tk.Frame(c, bg="white"); l.pack(fill=tk.X)
        tk.Button(l, text="Реєстрація", bg="white", fg="blue", bd=0, command=lambda: ctrl.show("RegisterFrame")).pack(side=tk.LEFT)
        tk.Button(l, text="Забув пароль?", bg="white", fg="gray", bd=0, command=lambda: ctrl.show("ForgotPasswordFrame")).pack(side=tk.RIGHT)

    def login(self):
        l, p = self.el.get().strip(), self.ep.get().strip()
        d = self.ctrl.data_mgr.load()
        u = next((x for x in d["users"] if (x["login"]==l or x["email"]==l or x["phone"]==l) and x["pass"]==p), None)
        if u:
            if u.get("role") == "blocked": return messagebox.showerror("Блок", "Акаунт заблоковано!")
            self.ctrl.user = u
            self.ctrl.show("AdminDashboard" if u["role"]=="admin" else "ClientFrame")
        else: messagebox.showerror("Err", "Невірні дані")

class ForgotPasswordFrame(tk.Frame):
    def __init__(self, parent, ctrl):
        super().__init__(parent, bg="#ecf0f1")
        self.ctrl = ctrl
        self.c = tk.Frame(self, padx=30, pady=30, bg="white", bd=1, relief="solid")
        self.c.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        tk.Label(self.c, text="Відновлення доступу", font=("Arial", 18, "bold"), bg="white").pack(pady=(0, 20))
        self.frame_login = tk.Frame(self.c, bg="white")
        self.frame_login.pack(fill=tk.X)
        tk.Label(self.frame_login, text="Введіть ваш логін:", bg="white", fg="gray").pack(anchor="w")
        self.e_login = tk.Entry(self.frame_login, width=30, font=("Arial", 12))
        self.e_login.pack(pady=5)

        tk.Button(self.frame_login, text="Знайти користувача", bg="#3498db", fg="white", 
                  font=("Arial", 10, "bold"), command=self.find_user).pack(pady=10, fill=tk.X)
        self.frame_method = tk.Frame(self.c, bg="white")
        self.lbl_found = tk.Label(self.frame_method, text="", bg="white", fg="#27ae60", font=("Arial", 10))
        self.lbl_found.pack(pady=5)
        tk.Label(self.frame_method, text="Оберіть метод відновлення:", bg="white").pack(pady=5)
        self.btn_phone = tk.Button(self.frame_method, text="Через Телефон (СМС)", 
                                   bg="#f1c40f", command=self.recover_via_phone)
        self.btn_phone.pack(fill=tk.X, pady=2)
        self.btn_email = tk.Button(self.frame_method, text="Через Email", 
                                   bg="#e67e22", fg="white", command=self.recover_via_email)
        self.btn_email.pack(fill=tk.X, pady=2)

        tk.Button(self.c, text="⬅ Назад до входу", command=self.go_back).pack(pady=(20, 0))
        
        self.found_user_data = None 

    def find_user(self):
        login = self.e_login.get().strip()
        if not login:
            return messagebox.showwarning("Увага", "Введіть логін!")

        d = self.ctrl.data_mgr.load()
        user = next((x for x in d.get("users", []) if x.get("login") == login), None)
        
        if user:
            self.found_user_data = user
            self.frame_login.pack_forget() 
            self.frame_method.pack(fill=tk.X) 
            self.lbl_found.config(text=f"Користувача {user['login']} знайдено!")
        else:
            messagebox.showerror("Помилка", "Користувача з таким логіном не існує.")

    def generate_strong_password(length=10):
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*()_+-="
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    def generate_new_pass(self):
        new_pass = generate_strong_password(10)  
        d = self.ctrl.data_mgr.load()
        for u in d["users"]:
            if u["login"] == self.found_user_data["login"]:
                u["pass"] = new_pass
                break
        self.ctrl.data_mgr.save(d)
        return new_pass

    def recover_via_phone(self):
        if not self.found_user_data.get("phone"):
            return messagebox.showerror("Помилка", "У цього користувача не вказаний телефон!")
        np = self.generate_new_pass()
        win = tk.Toplevel(self.ctrl)
        win.title("Новий пароль")
        win.geometry("400x150")
        win.resizable(False, False)
        tk.Label(win, text="Новий пароль:", font=("Arial", 12)).pack(pady=5)
        entry = tk.Entry(win, font=("Arial", 14), justify="center")
        entry.insert(0, np)
        entry.pack(pady=5, padx=10, fill="x")
        def block_typing(event):
            return "break"
        entry.bind("<Key>", block_typing)  
        def copy():
            self.ctrl.clipboard_clear()
            self.ctrl.clipboard_append(np)
            self.ctrl.update()
            messagebox.showinfo("Скопійовано", "Пароль скопійовано в буфер!")

        tk.Button(win, text="Скопіювати в буфер", command=copy).pack(pady=10)

    def recover_via_email(self):
        email = self.found_user_data.get("email")
        if not email:
            return messagebox.showerror("Помилка", "У цього користувача не вказана пошта!")
        np = self.generate_new_pass()

        try:
            success = send_email_real(email, np) 
            if success:
                messagebox.showinfo("Успіх", f"Лист з новим паролем відправлено на {email}")
                self.go_back()
            else:
                messagebox.showerror("Помилка", "Не вдалося відправити лист. Перевірте налаштування сервера.")
        except Exception as e:
             messagebox.showerror("Помилка", f"Сталася помилка: {e}")

    def go_back(self):
        self.e_login.delete(0, tk.END)
        self.frame_method.pack_forget()
        self.frame_login.pack(fill=tk.X)
        self.found_user_data = None
        self.ctrl.show("AuthFrame")

class RegisterFrame(tk.Frame):
    def __init__(self, parent, ctrl):
        super().__init__(parent)
        self.ctrl = ctrl
        self.configure(bg="#f0f2f5") 

        # --- Стилі ---
        self.colors = {
            "bg": "#f0f2f5",
            "card_bg": "#ffffff",
            "primary": "#27ae60",
            "primary_hover": "#219150",
            "text": "#333333",
            "text_light": "#666666",
            "error": "#e74c3c"
        }
        self.fonts = {
            "header": ("Helvetica", 24, "bold"),
            "label": ("Helvetica", 10, "bold"),
            "entry": ("Helvetica", 11),
            "btn": ("Helvetica", 11, "bold")
        }

        self.card = tk.Frame(self, bg=self.colors["card_bg"], padx=40, pady=40)
        self.card.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.card.config(highlightbackground="#d1d5db", highlightthickness=1)

        tk.Label(
            self.card, 
            text="Створення акаунту", 
            font=self.fonts["header"], 
            bg=self.colors["card_bg"], 
            fg=self.colors["text"]
        ).pack(pady=(0, 25))

        self.ents = {}
        fields = [
            ("Логін", False), ("Пароль", True), 
            ("Ім'я", False), ("Прізвище", False), 
            ("По батькові", False), ("Дата народження", False), 
            ("Телефон", False), ("Email", False)
        ]

        for label_text, is_password in fields:
            row = tk.Frame(self.card, bg=self.colors["card_bg"])
            row.pack(fill=tk.X, pady=5)

            tk.Label(
                row, 
                text=label_text, 
                font=self.fonts["label"], 
                bg=self.colors["card_bg"], 
                fg=self.colors["text_light"],
                anchor='w'
            ).pack(fill=tk.X)

            e = tk.Entry(
                row, 
                font=self.fonts["entry"], 
                bg="#f9fafb", 
                relief=tk.FLAT, 
                highlightthickness=1, 
                highlightbackground="#d1d5db"
            )
            e.pack(fill=tk.X, ipady=5, pady=(2, 0))
            
            if is_password:
                e.config(show="•") 
            
            fix_paste(e) 
            self.ents[label_text] = e

        btn_container = tk.Frame(self.card, bg=self.colors["card_bg"])
        btn_container.pack(fill=tk.X, pady=(30, 0))
        self.btn_reg = tk.Button(
            btn_container,
            text="Зареєструватися",
            font=self.fonts["btn"],
            bg=self.colors["primary"],
            fg="white",
            activebackground=self.colors["primary_hover"],
            activeforeground="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.on_register
        )
        self.btn_reg.pack(fill=tk.X, ipady=8)
        self.btn_reg.bind("<Enter>", lambda e: self.btn_reg.config(bg=self.colors["primary_hover"]))
        self.btn_reg.bind("<Leave>", lambda e: self.btn_reg.config(bg=self.colors["primary"]))

        self.btn_back = tk.Button(
            btn_container,
            text="Вже є акаунт? Увійти",
            font=("Helvetica", 9),
            bg=self.colors["card_bg"],
            fg=self.colors["primary"],
            activebackground=self.colors["card_bg"],
            activeforeground=self.colors["primary_hover"],
            relief=tk.FLAT,
            cursor="hand2",
            bd=0,
            command=lambda: ctrl.show("AuthFrame")
        )
        self.btn_back.pack(fill=tk.X, pady=(10, 0))

    def on_register(self):
        v = {k: x.get().strip() for k, x in self.ents.items()}

        if not all(v.values()):
            return messagebox.showerror("Помилка", "Будь ласка, заповніть всі поля!")

        if len(v["Логін"]) < 4:
            return messagebox.showerror("Помилка", "Логін має бути не коротше 4 символів.")
        if not re.match(r"^[a-zA-Z0-9_]+$", v["Логін"]):
            return messagebox.showerror("Помилка", "Логін може містити лише латинські літери, цифри та '_'")

        if len(v["Пароль"]) < 6:
            return messagebox.showerror("Помилка", "Пароль має бути не коротше 6 символів.")

        for field in ["Ім'я", "Прізвище", "По батькові"]:
            if not v[field].replace("-", "").replace("'", "").isalpha(): 
                return messagebox.showerror("Помилка", f"Поле '{field}' повинно містити лише літери.")

        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, v["Email"]):
            return messagebox.showerror("Помилка", "Введіть коректний Email (наприклад, user@example.com).")

        clean_phone = re.sub(r"[\s\-\(\)]", "", v["Телефон"])
        if not re.match(r"^\+?\d{10,13}$", clean_phone):
            return messagebox.showerror("Помилка", "Некоректний номер телефону (наприклад: +380991234567).")

        try:
            dob_date = datetime.strptime(v["Дата народження"], "%d.%m.%Y")
            
            if dob_date > datetime.now():
                return messagebox.showerror("Помилка", "Дата народження не може бути в майбутньому.")
            age = (datetime.now() - dob_date).days // 365
            if age < 6:
                return messagebox.showerror("Помилка", "Реєстрація дозволена з 6 років.")
            if age > 120:
                return messagebox.showerror("Помилка", "Перевірте правильність року народження.")

        except ValueError:
            return messagebox.showerror("Помилка", "Невірний формат дати. Використовуйте: ДД.ММ.РРРР (наприклад, 31.12.1990).")

        try:
            d = self.ctrl.data_mgr.load()
            
            if any(u['login'] == v["Логін"] for u in d['users']):
                return messagebox.showerror("Помилка", "Цей логін вже зайнятий.")
            
            if any(u.get('email') == v["Email"] for u in d['users']):
                return messagebox.showerror("Помилка", "Користувач з таким Email вже існує.")

            new_user = {
                "login": v["Логін"],
                "pass": v["Пароль"],
                "role": "client",
                "name": v["Ім'я"],
                "surname": v["Прізвище"],
                "patronymic": v["По батькові"],
                "dob": v["Дата народження"],
                "phone": clean_phone,
                "email": v["Email"],
                "orders_count": 0,
                "total_spent": 0.0,
                "registered_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S") 
            }
            
            d["users"].append(new_user)
            self.ctrl.data_mgr.save(d)
            
            messagebox.showinfo("Успіх", "Реєстрація успішна! Тепер ви можете увійти.")
            self.ctrl.show("AuthFrame")
            
        except Exception as e:
            messagebox.showerror("Системна помилка", f"Не вдалося зберегти дані: {e}")

# CLIENT PART

class ClientFrame(tk.Frame):
    def __init__(self, parent, ctrl):
        super().__init__(parent); self.ctrl = ctrl
        

        self.cat_icons = {
            "hudozhnya": "🎨", 
            "applied": "🧠", 
            "kids": "🧸", 
            "ebooks": "📱", 
            "audio": "🎧", 
            "announce": "📢", 
            "special": "🎁"
        }

        self.sub_cat_icons = {
            "history": "📜",
            "fantasy": "🐉",
            "detective": "🕵️",
            "business": "💼",
            "psychology": "🧘",
            "classic": "🏛️",
            "sale": "🔥"
        }

        # --- ВЕРХНЯ ПАНЕЛЬ ---
        h = tk.Frame(self, bg="white", height=70, bd=1, relief="raised"); h.pack(fill=tk.X)
        tk.Button(h, text="📖 КНИГАРНЯ", font=("Impact", 20), fg="#e67e22", bg="white", bd=0, command=self.show_home).pack(side=tk.LEFT, padx=20)
        
        self.e_search = tk.Entry(h, width=30, font=("Arial", 12))
        self.e_search.pack(side=tk.LEFT, padx=20)
        tk.Button(h, text="🔍", command=self.do_search).pack(side=tk.LEFT)
        
        tk.Button(h, text="Вихід", command=lambda: ctrl.show("AuthFrame")).pack(side=tk.RIGHT, padx=10)
        self.b_cart = tk.Button(h, text="🛒 Кошик (0)", bg="#2ecc71", fg="white", font=("Arial", 11, "bold"), command=lambda: ctrl.show("CartFrame"))
        self.b_cart.pack(side=tk.RIGHT, padx=10)
        tk.Button(h, text="👤 Профіль", bg="#3498db", fg="white", command=lambda: ctrl.show("ClientProfileFrame")).pack(side=tk.RIGHT, padx=10)
        
        # --- НАВІГАЦІЯ  ---
        nav = tk.Frame(self, bg="#34495e", height=45); nav.pack(fill=tk.X)
        cats = ["hudozhnya", "applied", "kids", "ebooks", "audio", "announce", "special"]
        
        for cat in cats:
            lbl = CATEGORIES_CONFIG[cat]["label"]
            tk.Button(nav, text=lbl, bg="#34495e", fg="white", bd=0, font=("Arial", 10, "bold"),
                      command=lambda c=cat: self.show_sub_menu(c)).pack(side=tk.LEFT, padx=10)
        
        tk.Button(nav, text="Про нас", bg="#34495e", fg="white", bd=0, font=("bold",10), command=lambda: ctrl.show("ClientAbout")).pack(side=tk.RIGHT, padx=10)
        tk.Button(nav, text="Новини", bg="#c0392b", fg="white", bd=0, command=lambda: ctrl.show("ClientNewsPage")).pack(side=tk.RIGHT, padx=10)
        
        self.sub_nav = tk.Frame(self, bg="#ecf0f1", height=40); self.sub_nav.pack(fill=tk.X)
        
        self.scroll = ctrl.create_scrollable_frame(self, bg_color="white")
        self.update_cart()
        self.show_home()

    def clear_content(self):
        for w in self.scroll.winfo_children():
            w.destroy()
        self.scroll.update() 
        self.scroll.master.configure(scrollregion=(0, 0, 1, 1))
        self.scroll.master.yview_moveto(0) 
        self.scroll.master.xview_moveto(0)

    def refresh_scroll_region(self):
        self.scroll.update_idletasks()
        self.scroll.master.configure(scrollregion=self.scroll.master.bbox("all"))

    def update_cart(self):
        self.b_cart.config(text=f"🛒 Кошик ({sum(i['qty'] for i in self.ctrl.cart)})")

    def do_search(self):
        q = self.e_search.get().lower()
        if not q: return
        self.clear_content()
        tk.Label(self.scroll, text=f"🔎 Результати пошуку: {q}", font=("Arial", 16)).pack(fill=tk.X, padx=20, pady=10)
        grid = tk.Frame(self.scroll, bg="white"); grid.pack(fill=tk.BOTH, expand=True, padx=20)
        d = self.ctrl.data_mgr.load()
        books = [b for b in d["books"] if q in b.title.lower() or q in b.author_surname.lower()]
        r, c = 0, 0
        for b in books:
            self.create_card(grid, b, r, c); c+=1
            if c>4: c=0; r+=1

    def show_home(self):
        for w in self.sub_nav.winfo_children(): w.destroy()
        self.clear_content()
        
        d = self.ctrl.data_mgr.load()
        main_news = next((n for n in d["news"] if n.get("is_main")), None)
        if main_news:
            ban = tk.Frame(self.scroll, bg="#2c3e50"); ban.pack(fill=tk.X, padx=20, pady=10)
            if main_news.get("image"):
               self.ctrl.load_image_to_label(ban, main_news["image"], 200, 150).pack(side=tk.LEFT, padx=10, pady=10)
            tk.Label(ban, text=f"⚡ {main_news['title']}", font=("Arial", 22, "bold"), fg="white", bg="#2c3e50").pack(pady=10)
            tk.Label(ban, text=main_news['content'][:150]+"...", fg="#bdc3c7", bg="#2c3e50").pack()
            tk.Button(ban, text="👉 Читати далі", command=lambda: self.ctrl.show("ClientNewsPage"), bg="#f39c12", fg="white").pack(pady=10)


        self.load_section("🔥 ХІТИ ТА ЗНИЖКИ", "special")
        self.load_section("📦 КОМПЛЕКТИ", "sets")
        self.load_section("📚 ДИТЯЧА ЛІТЕРАТУРА", "kids")

    def load_section(self, title, cat):
        tk.Label(self.scroll, text=title, font=("Arial", 18, "bold"), bg="white", fg="#2c3e50", anchor='w').pack(fill=tk.X, padx=20, pady=(20,10))
        fr = tk.Frame(self.scroll, bg="white"); fr.pack(fill=tk.X, padx=20)
        d = self.ctrl.data_mgr.load()
        
        if cat == "sets":
            items = d.get("book_sets", [])
            for i, s in enumerate(items[:5]): self.create_set_card(fr, s, 0, i)
        else:
            books = [b for b in d["books"] if (cat=="special" and b.discount_percent > 0) or b.category == cat]
            if not books and cat=="special": books = d["books"][:5] # Fallback
            random.shuffle(books)
            for i, b in enumerate(books[:5]): self.create_card(fr, b, 0, i)

    def show_sub_menu(self, main_cat):
        for w in self.sub_nav.winfo_children(): w.destroy()
        self.clear_content()
        subs = CATEGORIES_CONFIG[main_cat]["subs"]
        
        tk.Label(self.sub_nav, text=f"📂 {CATEGORIES_CONFIG[main_cat]['label']}:", bg="#ecf0f1", fg="gray").pack(side=tk.LEFT, padx=10)
        
        for k, v in subs.items():
            tk.Button(self.sub_nav, text=v, bg="#ecf0f1", bd=0, fg="#2c3e50", command=lambda m=main_cat, s=k: self.load_grid(m, s)).pack(side=tk.LEFT, padx=5)
        
        self.load_grid(main_cat, "all" if "all" in subs else list(subs.keys())[0])

    def load_grid(self, main_cat, sub_cat, sort_mode="def"):
        self.clear_content()
        
        flt = tk.Frame(self.scroll, bg="white"); flt.pack(fill=tk.X, padx=20, pady=10)
        
 
        text_name = CATEGORIES_CONFIG[main_cat]['subs'].get(sub_cat, sub_cat)
        

        icon = self.sub_cat_icons.get(sub_cat, self.cat_icons.get(main_cat, "📚"))
        
        header_text = f"{text_name} {icon}"
        
        tk.Label(flt, text=header_text, font=("Arial", 18, "bold"), bg="white", fg="#2c3e50").pack(side=tk.LEFT)
        
        # Сортування
        cb = ttk.Combobox(flt, values=["За замовчуванням", "📉 Спершу дешевші", "📈 Спершу дорожчі"], state="readonly"); cb.pack(side=tk.RIGHT)
        cb.set("Сортування")
        cb.bind("<<ComboboxSelected>>", lambda e: self.load_grid(main_cat, sub_cat, cb.get()))

        grid = tk.Frame(self.scroll, bg="white"); grid.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        d = self.ctrl.data_mgr.load(); books = []
        
        if main_cat == "special" and sub_cat == "sets":
             for i, s in enumerate(d.get("book_sets", [])): self.create_set_card(grid, s, i//5, i%5)
             return

        for b in d["books"]:
            match = True
            if main_cat == "audio" and b.format != "audio": match = False
            elif main_cat == "ebooks" and b.format != "electronic": match = False
            elif main_cat == "announce" and b.category != "announce": match = False
            elif main_cat == "special" and sub_cat == "sale" and b.discount_percent == 0: match = False
            elif main_cat not in ["special"] and b.category != main_cat: match = False
            
            if main_cat not in ["special", "announce"] and sub_cat != "all" and b.subcategory != sub_cat: match = False
            if match: books.append(b)
            
        if "📉" in sort_mode: books.sort(key=lambda x: x.price)
        elif "📈" in sort_mode: books.sort(key=lambda x: x.price, reverse=True)

        r, c = 0, 0
        for b in books:
            self.create_card(grid, b, r, c); c+=1
            if c>4: c=0; r+=1

        self.refresh_scroll_region()

    def create_card(self, parent, b, r, c):
        card = tk.Frame(parent, bg="white", width=200, height=360, bd=1, relief="solid")
        card.grid(row=r, column=c, padx=10, pady=10); card.pack_propagate(False)
        
        
        self.ctrl.load_image_to_label(card, b.image_path, 180, 150).pack(pady=10) # ПРАВИЛЬНО: .image_path
        tk.Label(card, text=b.title, font=("bold", 10), wraplength=180, bg="white").pack() # ПРАВИЛЬНО: .title
        tk.Label(card, text=b.author_name, font=("Arial", 9), bg="white", fg="gray").pack() # ПРАВИЛЬНО: .author_name
        tk.Label(card, text=b.author_surname, font=("Arial", 9), bg="white", fg="gray").pack() # ПРАВИЛЬНО: .author_surname
        
        price_fr = tk.Frame(card, bg="white"); price_fr.pack(pady=2)
        
        # ВИКОРИСТАННЯ МЕТОДУ/АТРИБУТІВ КЛАСУ BOOK
        if b.discount_percent > 0:
            old = b.price # ПРАВИЛЬНО: .price
            new_p = b.get_final_price() # ПРАВИЛЬНО: використовуємо метод
            tk.Label(price_fr, text=f"{old:.0f}", font=("Arial", 10, "overstrike"), fg="gray", bg="white").pack(side=tk.LEFT)
            tk.Label(price_fr, text=f" {new_p:.0f} грн", font=("bold", 12), fg="red", bg="white").pack(side=tk.LEFT)
        else:
            tk.Label(price_fr, text=f"{b.price} грн", font=("bold", 12), fg="orange", bg="white").pack() # ПРАВИЛЬНО: .price
        # ...
        btn_fr = tk.Frame(card, bg="white"); btn_fr.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
        tk.Button(btn_fr, text="Інфо", command=lambda: self.show_product_page(b)).pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(btn_fr, text="В кошик", bg="#27ae60", fg="white", command=lambda: self.add(b)).pack(side=tk.RIGHT, fill=tk.X, expand=True)

    def create_set_card(self, parent, s, r, c):
        card = tk.Frame(parent, bg="#fff8e1", width=200, height=360, bd=1, relief="solid")
        card.grid(row=r, column=c, padx=10, pady=10); card.pack_propagate(False)
        
        tk.Label(card, text="🎁 КОМПЛЕКТ", bg="#f39c12", fg="white", font=("bold",8)).pack(fill=tk.X)
        self.ctrl.load_image_to_label(card, s.get("image", ""), 180, 140).pack(pady=5)
        
        tk.Label(card, text=s["title"], font=("bold", 10), wraplength=180, bg="#fff8e1").pack()
        
        all_books = self.ctrl.data_mgr.load().get("books", [])
        set_isbns = s.get("items", []) 
        
        is_available = True
        for isbn in set_isbns:
            # b["isbn"] на b.isbn
            found_book = next((b for b in all_books if b.isbn == isbn), None)
            # Використовуємо метод is_available()
            if not found_book or not found_book.is_available():
                is_available = False
        
        tk.Label(card, text=f"{s['price']} грн", font=("bold", 14), fg="#c0392b", bg="#fff8e1").pack(pady=5)
        
        btn_fr = tk.Frame(card, bg="#fff8e1"); btn_fr.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
        
        tk.Button(btn_fr, text="Інфо", command=lambda: self.show_set_page(s)).pack(side=tk.LEFT, fill=tk.X, expand=True)

        if is_available:
            tk.Button(btn_fr, text="Купити", bg="#e67e22", fg="white", 
                      command=lambda: self.add_set(s)).pack(side=tk.RIGHT, fill=tk.X, expand=True)
        else:
            tk.Button(btn_fr, text="Немає", bg="#95a5a6", fg="white", state="disabled").pack(side=tk.RIGHT, fill=tk.X, expand=True)

    def show_set_page(self, s):
        self.clear_content()
        tk.Button(
            self.scroll, 
            text="⬅ До списку комплектів", 
            command=lambda: self.load_grid('sets', 'all'),
            bg="#f0f2f5", bd=0, cursor="hand2"
        ).pack(anchor='w', padx=20, pady=(10, 5))
        
        main = tk.Frame(self.scroll, bg="white", padx=15, pady=15)
        main.pack(fill=tk.BOTH, expand=True, padx=20)
        
        left = tk.Frame(main, bg="white")
        left.pack(side=tk.LEFT, anchor='n', padx=(0, 20))
        self.ctrl.load_image_to_label(left, s.get("image", ""), 220, 330).pack()

        right = tk.Frame(main, bg="white")
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        tk.Label(
            right, 
            text=s['title'], 
            font=("Arial", 22, "bold"), 
            bg="white", 
            wraplength=550, 
            justify="left"
        ).pack(anchor='w')
        
        tk.Label(
            right, 
            text="Ексклюзивний комплект книг", 
            font=("Arial", 12), 
            fg="gray", 
            bg="white"
        ).pack(anchor='w', pady=(2, 10))

        p_fr = tk.Frame(right, bg="#fff8e1", pady=10, padx=15, bd=1, relief="solid")
        p_fr.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(
            p_fr, 
            text=f"{s['price']} грн", 
            font=("Arial", 20, "bold"), 
            fg="#c0392b", 
            bg="#fff8e1"
        ).pack(side=tk.LEFT)
        
        all_books = self.ctrl.data_mgr.load().get("books", [])
        set_isbns = s.get("items", [])
        
        is_available = True
        included_books = [] 
        
        for isbn in set_isbns:
            # b.isbn замість b["isbn"]
            found = next((b for b in all_books if b.isbn == isbn), None)
            if found:
                included_books.append(found)
                # Використовуємо метод is_available() або перевіряємо .stock
                if not found.is_available():
                    is_available = False
            else:
                is_available = False

        if is_available:
            tk.Button(
                p_fr, 
                text="КУПИТИ КОМПЛЕКТ", 
                bg="#e67e22", fg="white", 
                font=("Arial", 12, "bold"), 
                padx=15,
                command=lambda: self.add_set(s)
            ).pack(side=tk.RIGHT)
            
            tk.Label(p_fr, text="В наявності", fg="green", bg="#fff8e1", font=("bold", 9)).pack(side=tk.RIGHT, padx=15)
        else:
            tk.Button(
                p_fr, 
                text="НЕМАЄ В НАЯВНОСТІ", 
                bg="#95a5a6", fg="white", 
                font=("Arial", 12, "bold"), 
                state="disabled", 
                padx=15
            ).pack(side=tk.RIGHT)

        tk.Label(
            right, 
            text=f"📚Книги у комплекті ({len(included_books)}):", 
            font=("bold", 12), 
            bg="white"
        ).pack(anchor='w', pady=(10, 5))
        
        books_list_frame = tk.Frame(right, bg="white")
        books_list_frame.pack(fill=tk.BOTH, expand=True)

        for b in included_books:
            b_row = tk.Frame(books_list_frame, bg="#f9f9f9", bd=1, relief="solid", pady=2, padx=2)
            b_row.pack(fill=tk.X, pady=2)

            # ПРАВИЛЬНО:
            self.ctrl.load_image_to_label(b_row, b.image_path, 30, 40).pack(side=tk.LEFT, padx=5)

            info_fr = tk.Frame(b_row, bg="#f9f9f9")
            info_fr.pack(side=tk.LEFT, padx=5)


            tk.Label(info_fr, text=b.title, font=("bold", 10), bg="#f9f9f9").pack(anchor='w')
            tk.Label(
                    info_fr, 
                    text=f"{b.author_surname}",  # ПРАВИЛЬНО
                    font=("Arial", 8), 
                    fg="gray", 
                    bg="#f9f9f9"
                    ).pack(anchor='w')
            
            tk.Button(
                b_row, 
                text="➡", 
                width=3,
                bg="white", 
                command=lambda current_book=b: self.show_product_page(current_book)
            ).pack(side=tk.RIGHT, padx=5)

    def show_product_page(self, b):
        self.clear_content()
        
        btn_back = tk.Button(
            self.scroll, 
            text="⬅ Повернутися", 
            bg="#f0f2f5", bd=0, cursor="hand2",
            command=lambda: self.load_grid(b.category, 'all') 
        )
        btn_back.pack(anchor='w', padx=20, pady=(10, 5))
        
        main = tk.Frame(self.scroll, bg="white", padx=15, pady=15)
        main.pack(fill=tk.BOTH, expand=True, padx=20)

        left_frame = tk.Frame(main, bg="white")
        left_frame.pack(side=tk.LEFT, anchor='n', padx=(0, 20))

        img_box = self.ctrl.load_image_to_label(left_frame, b.image_path, 220, 330)
        img_box.pack()

        right_frame = tk.Frame(main, bg="white")
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        tk.Label(
            right_frame, 
            text=b.title, 
            font=("Arial", 22, "bold"), 
            bg="white", 
            wraplength=550, 
            justify="left"
        ).pack(anchor='w')
        
        tk.Label(
            right_frame, 
            text=f"Автор: {b.get_full_author()}", 
            font=("Arial", 12), 
            fg="gray", 
            bg="white"
        ).pack(anchor='w', pady=(2, 5))
        
        ratings = b.ratings 
        avg_rating = sum(ratings) / len(ratings) if ratings else 0
            
        tk.Label(
            right_frame, 
            text=f"Рейтинг: ⭐ {avg_rating:.1f}  ({len(ratings)} відгуків)", 
            bg="white", 
            font=("Arial", 11)
        ).pack(anchor='w')

        price_frame = tk.Frame(right_frame, bg="#f8f9fa", pady=10, padx=15, bd=1, relief="solid")
        price_frame.pack(fill=tk.X, pady=(15, 15))
        
        tk.Label(
            price_frame, 
            text=f"{b.get_final_price():.2f} грн", 
            font=("Arial", 20, "bold"), 
            fg="#e67e22", 
            bg="#f8f9fa"
        ).pack(side=tk.LEFT)
        
        btn_state = "normal"
        btn_text = "В КОШИК" 
        btn_bg = "#27ae60"
        
        if b.category == "announce":
            btn_state = "disabled"; btn_text = "ОЧІКУЄТЬСЯ"; btn_bg = "#95a5a6"
        elif not b.is_available(): 
            btn_state = "disabled"; btn_text = "НЕМАЄ"; btn_bg = "#c0392b"
            
        tk.Button(
            price_frame, 
            text=btn_text, 
            bg=btn_bg, fg="white", 
            font=("Arial", 12, "bold"), 
            state=btn_state, 
            padx=15,
            command=lambda: self.add(b)
        ).pack(side=tk.RIGHT)
        
        if b.format in ["electronic", "audio"]:
             tk.Label(price_frame, text="✅Миттєво", fg="blue", bg="#f8f9fa", font=("bold", 9)).pack(side=tk.RIGHT, padx=15)
        elif b.stock > 0:
            tk.Label(price_frame, text="✅Є", fg="green", bg="#f8f9fa", font=("bold", 9)).pack(side=tk.RIGHT, padx=15)

        notebook = ttk.Notebook(right_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        tab1 = tk.Frame(notebook, bg="white", pady=10)
        notebook.add(tab1, text="Про книгу")
        
        tk.Label(
            tab1, 
            text=b.description, 
            font=("Arial", 10), 
            bg="white", 
            wraplength=550, 
            justify="left"
        ).pack(anchor='w')
        
        tk.Label(tab1, text="Уривок:", font=("bold", 10), bg="white").pack(anchor='w', pady=(10, 0))
        tk.Label(
            tab1, 
            text=b.excerpt, 
            bg="#f9f9f9", fg="gray", font=("Arial", 9),
            wraplength=550, justify="left"
        ).pack(anchor='w', fill=tk.X, padx=5)

        tab2 = tk.Frame(notebook, bg="white", pady=10)
        notebook.add(tab2, text="Характеристики")
        
        fmt = b.format
        
        details = [
            ("Рік видання", b.year),
            ("ISBN", b.isbn),
            ("Формат", fmt.upper())
        ]

        if fmt == 'audio':
            details.insert(1, ("Тривалість", f"{b.duration} хв"))
        else:
            details.insert(1, ("Сторінок", b.pages))

        if fmt == 'physical':
            details.append(("Вага", f"{b.weight} г"))
        elif fmt == 'electronic':
            details.append(("Розмір файлу", "2-5 MB")) 

        for key, value in details:
            row = tk.Frame(tab2, bg="white")
            row.pack(fill=tk.X, pady=1)
            tk.Label(row, text=key, font=("bold", 9), width=15, anchor='w', bg="white").pack(side=tk.LEFT)
            tk.Label(row, text=value, bg="white", font=("Arial", 9)).pack(side=tk.LEFT)
            
        tab3 = tk.Frame(notebook, bg="white", pady=10)
        notebook.add(tab3, text="Відгуки")
        
        reviews = b.reviews 
        if not reviews:
            tk.Label(tab3, text="Немає відгуків.", bg="white", fg="gray").pack(anchor='w')
            
        for r in reviews[-3:]: 
            rev_frame = tk.Frame(tab3, bg="#f0f0f0", pady=2, padx=5)
            rev_frame.pack(fill=tk.X, pady=2)
            tk.Label(rev_frame, text=f"👤 {r['user']}   ⭐ {r['rating']}", font=("bold", 9), bg="#f0f0f0").pack(anchor='w')
            tk.Label(rev_frame, text=r['text'], bg="#f0f0f0", font=("Arial", 9)).pack(anchor='w')
            
        write_rev_frame = tk.LabelFrame(tab3, text="Написати відгук", bg="white", padx=5, pady=5)
        write_rev_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(write_rev_frame, text="Оцінка:", bg="white", font=("Arial", 9)).pack(side=tk.LEFT)
        
        
        self.entry_rating = tk.Entry(write_rev_frame, width=3) 
        self.entry_rating.pack(side=tk.LEFT, padx=5)
        
        tk.Label(write_rev_frame, text="Текст:", bg="white", font=("Arial", 9)).pack(side=tk.LEFT)
        
        self.entry_text = tk.Entry(write_rev_frame, width=30)
        self.entry_text.pack(side=tk.LEFT, padx=5)
        
        self.current_book = b

        self.refresh_scroll_region()
        


        def send_rev(self):
            try:
                rating_val = int(self.entry_rating.get()) 
        
                if 1 <= rating_val <= 5:
                    data = self.ctrl.data_mgr.load()

                    found_item_in_db = None
                    target_isbn = self.current_book.isbn 
            
                    for book_item in data["books"]:
                        if book_item.isbn == target_isbn:
                            found_item_in_db = book_item
                            break
            
                    if found_item_in_db:
                        new_review = {"user": self.ctrl.user['login'], "rating": rating_val, "text": self.entry_text.get()}
                
                        found_item_in_db.reviews.append(new_review)
                        found_item_in_db.ratings.append(rating_val)
                
                        self.ctrl.data_mgr.save(data)
                
                        messagebox.showinfo("Дякуємо", "Відгук додано!")
                        self.ctrl.show("ClientFrame") 
                    else:
                        messagebox.showerror("Помилка", "Книгу не знайдено в базі даних.")

                else: messagebox.showerror("Помилка", "Оцінка має бути цілим числом від 1 до 5!")
            except AttributeError:
                messagebox.showerror("Помилка", "Не знайдено поля вводу. Спробуйте оновити сторінку.")
            except ValueError: 
                messagebox.showerror("Помилка", "Оцінка має бути числом!")
                
        tk.Button(write_rev_frame, text="OK", bg="orange", font=("bold", 8), command=self.send_rev).pack(side=tk.RIGHT)
        self.refresh_scroll_region()

    def add(self, b):
        f = False

        price = b.get_final_price()
    
        for i in self.ctrl.cart:
            if i['type'] == 'book' and i['obj'].isbn == b.isbn: 
                i['qty'] += 1
                f = True
                break
            
        if not f: 
            self.ctrl.cart.append({"type":"book", "obj":b, "qty":1, "price": price})
    
        self.update_cart()
        messagebox.showinfo("Кошик", "Додано")

    def add_set(self, s):
        self.ctrl.cart.append({"type":"set", "obj":s, "qty":1, "price": s['price']})
        self.update_cart(); messagebox.showinfo("Кошик", "Комплект додано")

class ClientAbout(tk.Frame):
    def __init__(self, parent, ctrl):
        super().__init__(parent, bg="white")
        self.ctrl = ctrl
        
        header = tk.Frame(self, bg="#2c3e50", height=80)
        header.pack(fill=tk.X)

        btn_back = tk.Button(header, text="⬅ Назад", font=("Arial", 11, "bold"), 
                             bg="#2c3e50", fg="white", activebackground="#34495e", activeforeground="white",
                             bd=0, cursor="hand2", command=lambda: ctrl.show("ClientFrame"))
        btn_back.pack(side=tk.LEFT, padx=20, pady=20)
        
        tk.Label(header, text="ПРО КОМПАНІЮ", font=("Arial", 14, "bold"), bg="#2c3e50", fg="#ecf0f1").pack(side=tk.RIGHT, padx=30)

        container = tk.Frame(self, bg="white")
        container.pack(fill=tk.BOTH, expand=True, padx=50, pady=20)
        
        try:
            original_image = tk.PhotoImage(file="logo_skd.png")
            tk_image = original_image.subsample(8, 8)
            logo_label = tk.Label(container, image=tk_image, bg="white")
            logo_label.image = tk_image 
            logo_label.pack(pady=(10, 5))
        except Exception as e:
            tk.Label(container, text="📚 SKD PUBLISHING", font=("Impact", 36), fg="#2c3e50", bg="white").pack(pady=(10, 5))

        mission_frame = tk.Frame(container, bg="white")
        mission_frame.pack(pady=10)
        tk.Label(mission_frame, text="Since 2025", font=("Arial", 10, "bold"), fg="#e67e22", bg="white").pack()
        
        desc_text = (
            "Ми — провідне видавництво нового покоління.\n"
            "Ми не просто друкуємо книги, ми створюємо культуру читання.\n"
            "Наша мета: поєднати класичні традиції з цифровими інноваціями."
        )
        tk.Label(container, text=desc_text, font=("Segoe UI", 12), bg="white", fg="#555", justify="center").pack(pady=10)

        ttk.Separator(container, orient='horizontal').pack(fill=tk.X, padx=100, pady=20)
        contact_card = tk.Frame(container, bg="#f8f9fa", bd=1, relief="solid", padx=30, pady=30)
        contact_card.pack(pady=10)

        tk.Label(contact_card, text="Наші Контакти", font=("Arial", 16, "bold"), bg="#f8f9fa", fg="#2c3e50").pack(pady=(0, 20))
        grid_fr = tk.Frame(contact_card, bg="#f8f9fa")
        grid_fr.pack()
        def add_contact(row, col, icon, title, value, link=None):
            f = tk.Frame(grid_fr, bg="#f8f9fa", padx=20, pady=10)
            f.grid(row=row, column=col, sticky="w")
            tk.Label(f, text=icon, font=("Segoe UI Emoji", 24), bg="#f8f9fa").pack(side=tk.LEFT, padx=(0, 10))
            txt_frame = tk.Frame(f, bg="#f8f9fa")
            txt_frame.pack(side=tk.LEFT)
            tk.Label(txt_frame, text=title, font=("Arial", 9, "bold"), fg="gray", bg="#f8f9fa", anchor='w').pack(anchor='w')
            val_lbl = tk.Label(txt_frame, text=value, font=("Arial", 11), bg="#f8f9fa", fg="#2c3e50", anchor='w')
            val_lbl.pack(anchor='w')
            if link:
                val_lbl.config(fg="#2980b9", cursor="hand2")
                val_lbl.bind("<Button-1>", lambda e: webbrowser.open(link))
        add_contact(0, 0, "📞", "Гаряча лінія", "+380 50 597 35 62")
        add_contact(0, 1, "📧", "Email підтримки", "skdpublishinghouse@gmail.com", "mailto:skdpublishinghouse@gmail.com")
        add_contact(1, 0, "✈️", "Telegram Bot", "@skd_books_bot", "https://t.me/ksd_books_bot")
        add_contact(1, 1, "📍", "Головний офіс", "м. Львів, вул. Лукаша, 5", "https://maps.app.goo.gl/JTFqjNSTh31dbowTA")

        tk.Label(self, text="© 2025-3025 SKD Publishing Group. Всі права захищено.", bg="white", fg="#bdc3c7", font=("Arial", 8)).pack(side=tk.BOTTOM, pady=10)

class ClientNewsPage(tk.Frame):
    def __init__(self, parent, ctrl):
        super().__init__(parent); self.ctrl=ctrl
        h = tk.Frame(self, bg="#2c3e50", height=60); h.pack(fill=tk.X)
        tk.Button(h, text="⬅ Назад", bg="#95a5a6", command=lambda: ctrl.show("ClientFrame")).pack(side=tk.LEFT, padx=20, pady=15)
        tk.Label(h, text="НОВИНИ ТА БЛОГ", font=("Arial", 18, "bold"), bg="#2c3e50", fg="white").pack(side=tk.LEFT, padx=20)
        self.scroll = ctrl.create_scrollable_frame(self, bg_color="#ecf0f1")
        
        for n in self.ctrl.data_mgr.load()["news"]:
            card = tk.Frame(self.scroll, bg="white", padx=20, pady=20, bd=1, relief="solid"); card.pack(fill=tk.X, padx=40, pady=10)
            tk.Label(card, text=n['title'], font=("Arial", 16, "bold"), fg="#2c3e50", bg="white").pack(anchor='w')
            tk.Label(card, text=f"📅 {n.get('date','Now')}", fg="gray", bg="white").pack(anchor='w')
            if n.get("image"):
                 self.ctrl.load_image_to_label(card, n["image"], 400, 200).pack(pady=10)
            
            lbl_txt = tk.Label(card, text=n['content'][:200]+"...", font=("Arial", 12), bg="white", justify="left", wraplength=800)
            lbl_txt.pack(anchor='w')
            
            def expand(l=lbl_txt, t=n['content'], b=None):
                l.config(text=t)
                if b: b.destroy()
            
            btn = tk.Button(card, text="Читати більше ⬇", command=lambda l=lbl_txt, t=n['content'], x=None: expand(l,t,x)) # Hack to access self inside
            btn.config(command=lambda l=lbl_txt, t=n['content'], b=btn: expand(l,t,b))
            btn.pack(anchor='e')

class ClientProfileFrame(tk.Frame):
    def __init__(self, parent, ctrl):
        super().__init__(parent); self.ctrl = ctrl

        h = tk.Frame(self, bg="#2c3e50", height=60); h.pack(fill=tk.X)
        tk.Button(h, text="⬅ Назад до магазину", bg="#f39c12", fg="white", font=("bold",10),
                  command=lambda: ctrl.show("ClientFrame")).pack(side=tk.LEFT, padx=20, pady=15)
        tk.Label(h, text="ОСОБИСТИЙ КАБІНЕТ", font=("Arial", 18, "bold"), fg="white", bg="#2c3e50").pack(side=tk.LEFT, padx=20)
        
        main = tk.Frame(self, bg="#ecf0f1"); main.pack(fill=tk.BOTH, expand=True)
        

        left = tk.Frame(main, bg="white", width=400, padx=20, pady=20, bd=1, relief="solid")
        left.pack(side=tk.LEFT, fill=tk.Y, padx=20, pady=20)
        left.pack_propagate(False)
        
        u = ctrl.user
        self.check_birthday(left, u)

        tk.Label(left, text="👤", font=("Arial", 60), bg="white", fg="#bdc3c7").pack()
        tk.Label(left, text=f"{u['surname']} {u['name']}", font=("Arial", 18, "bold"), bg="white").pack(pady=10)

        tk.Button(left, text="Редагувати профіль", bg="#3498db", fg="white", 
                  command=self.open_edit_window).pack(fill=tk.X, pady=(0, 20))

        info_box = tk.Frame(left, bg="#f9f9f9", padx=10, pady=10); info_box.pack(fill=tk.X, pady=10)
        
        def add_info_row(parent, icon, label, val):
            row = tk.Frame(parent, bg="#f9f9f9"); row.pack(fill=tk.X, pady=2)
            tk.Label(row, text=icon, width=3, bg="#f9f9f9").pack(side=tk.LEFT)
            tk.Label(row, text=label, width=10, anchor='w', bg="#f9f9f9", fg="gray").pack(side=tk.LEFT)
            tk.Label(row, text=val, bg="#f9f9f9", font=("bold", 10)).pack(side=tk.LEFT)

        add_info_row(info_box, "🔑", "Логін:", u['login'])
        add_info_row(info_box, "📧", "Email:", u['email'])
        add_info_row(info_box, "📱", "Телефон:", u['phone'])
        add_info_row(info_box, "🎂", "Д.Н.:", u.get('dob', '-'))
        
        tk.Label(left, text="Статистика:", font=("bold",12), bg="white", anchor='w').pack(fill=tk.X, pady=(20,5))
        
        stat_box = tk.Frame(left, bg="white"); stat_box.pack(fill=tk.X)
        tk.Label(stat_box, text=f"📦 Замовлень: {u['orders_count']}", bg="white", fg="blue").pack(anchor='w')
        tk.Label(stat_box, text=f"💰 Витрачено: {u['total_spent']:.2f} грн", bg="white", fg="green").pack(anchor='w')
        bonuses = u.get("bonuses", 0)
        tk.Label(stat_box, text=f"💎 Бонуси: {bonuses}", bg="white", fg="#8e44ad", font=("bold", 11)).pack(anchor='w', pady=5)

        # --- RIGHT PANEL (Orders Scroll) ---
        right = tk.Frame(main, bg="#ecf0f1"); right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=20, padx=(0,20))
        tk.Label(right, text="Історія замовлень", font=("Arial", 16), bg="#ecf0f1").pack(anchor='w', pady=(0,10))
        
        scroll_orders = ctrl.create_scrollable_frame(right, bg_color="#ecf0f1")
        
        d = ctrl.data_mgr.load()
        orders = [o for o in reversed(d["orders"]) if o["user_login"] == u["login"]]
        books_db = d["books"] 
        
        if not orders:
            tk.Label(scroll_orders, text="Історія порожня", bg="#ecf0f1", fg="gray").pack(pady=50)
        
        for o in orders:
            c = tk.Frame(scroll_orders, bg="white", bd=1, relief="raised", padx=15, pady=10)
            c.pack(fill=tk.X, pady=5, padx=5)
            
            # Header Row
            row1 = tk.Frame(c, bg="white"); row1.pack(fill=tk.X)
            tk.Label(row1, text=f"Замовлення #{o['id']}", font=("bold",11), bg="white").pack(side=tk.LEFT)
            tk.Label(row1, text=f"{o['date']}", fg="gray", bg="white").pack(side=tk.LEFT, padx=10)
            
            st_col = "#2ecc71" if o['status'] == 'shipped' else "#f39c12"
            st_txt = "ВІДПРАВЛЕНО" if o['status'] == 'shipped' else "НОВЕ"
            if o['status'] == 'cancelled': st_col="#e74c3c"; st_txt="СКАСОВАНО"
            
            tk.Label(row1, text=st_txt, fg="white", bg=st_col, padx=5, font=("bold",8)).pack(side=tk.RIGHT)
            

            items_container = tk.Frame(c, bg="white")
            items_container.pack(fill=tk.X, pady=5)

            items_list = o['items'].split(', ')
            for item_str in items_list:
                try:
                    title_part = item_str.rsplit(' x', 1)[0] 
                except:
                    title_part = item_str

                item_row = tk.Frame(items_container, bg="white")
                item_row.pack(fill=tk.X, anchor='w')
                
                tk.Label(item_row, text=f"• {item_str}", bg="white", fg="#555").pack(side=tk.LEFT)


                found_book = next((b for b in books_db if b.title == title_part), None)
                

                if found_book and o['status'] != 'cancelled':
                    fmt = found_book.format 
                    if fmt in ['audio', 'electronic']:
                       btn_txt = "Слухати/Скачати" if fmt == 'audio' else "Скачати PDF"
                       btn_col = "#8e44ad" if fmt == 'audio' else "#2980b9"
                    
                       tk.Button(item_row, text=btn_txt, bg=btn_col, fg="white", font=("Arial", 7, "bold"),
                                padx=5, pady=0, bd=0, cursor="hand2",
                                command=lambda b=found_book: self.download_content(b)).pack(side=tk.LEFT, padx=10)
            row3 = tk.Frame(c, bg="white"); row3.pack(fill=tk.X, pady=(5,0))
            tk.Label(row3, text=f"Сума: {o['total']:.2f} грн", font=("bold",12), bg="white").pack(side=tk.RIGHT)

    def download_content(self, book):
        
        fmt = book.format
        ext = ".mp3" if fmt == 'audio' else ".pdf"
        file_type = "Audiobook" if fmt == 'audio' else "E-Book"
        
        save_path = filedialog.asksaveasfilename(
            defaultextension=ext,
            initialfile=f"{book.title}{ext}", 
            title=f"Зберегти {file_type}",
            filetypes=[(f"{file_type} files", f"*{ext}"), ("All files", "*.*")]
        )
        
        if save_path:
            try:
                with open(save_path, "w", encoding="utf-8") as f:
                    f.write(f"Це контент книги: {book.title}\n")
                    f.write(f"Формат: {fmt}\n")
                    f.write("Дякуємо за покупку в SKD Publishing!")
                
                messagebox.showinfo("Успіх", f"Файл успішно збережено:\n{save_path}")
            except Exception as e:
                messagebox.showerror("Помилка", f"Не вдалося зберегти файл: {e}")

    def check_birthday(self, parent, user):
        dob_str = user.get('dob', '')
        if not dob_str: return
        
        try:
            today = datetime.now()
            dob_date = datetime.strptime(dob_str, "%d.%m.%Y")
            
            if today.day == dob_date.day and today.month == dob_date.month:
                banner = tk.Frame(parent, bg="#2ecc71", padx=10, pady=10)
                banner.pack(fill=tk.X, pady=(0, 10))
                tk.Label(banner, text="🎉 З ДНЕМ НАРОДЖЕННЯ!", font=("bold", 12), fg="white", bg="#2ecc71").pack()
                tk.Label(banner, text="Вам доступна знижка 10%\nпри оформленні замовлення!", 
                         fg="white", bg="#2ecc71", justify="center").pack()
        except Exception:
            pass 

    def open_edit_window(self):
        win = tk.Toplevel(self)
        win.title("Редагування профілю")
        win.geometry("400x550")
        win.resizable(False, False)
        u = self.ctrl.user
        tk.Label(win, text="Зміна даних", font=("Arial", 16, "bold")).pack(pady=20)
        
        ents = {}
        fields = {
            "login": "Логін (використовується для входу)",
            "pass": "Пароль",
            "email": "Email",
            "phone": "Телефон",
            "name": "Ім'я",
            "surname": "Прізвище",
            "dob": "Дата народження (DD.MM.YYYY)"
        }
        
        for key, label in fields.items():
            tk.Label(win, text=label, anchor='w').pack(fill=tk.X, padx=30, pady=(10,0))
            e = tk.Entry(win)
            e.insert(0, u.get(key, ""))
            e.pack(fill=tk.X, padx=30)
            ents[key] = e
        
        def save_changes():
            new_data = {k: v.get().strip() for k, v in ents.items()}
            
            if not all(new_data.values()):
                return messagebox.showerror("Помилка", "Всі поля мають бути заповнені!")

            db = self.ctrl.data_mgr.load()
            users = db['users']
            
            other_users = [usr for usr in users if usr['login'] != u['login']] 

            for usr in other_users:
                if usr['login'] == new_data['login']:
                    return messagebox.showerror("Помилка", "Цей Логін вже зайнятий!")
                if usr['email'] == new_data['email']:
                    return messagebox.showerror("Помилка", "Цей Email вже використовується!")
                if usr['phone'] == new_data['phone']:
                    return messagebox.showerror("Помилка", "Цей Телефон вже використовується!")

            old_login = u['login']
            new_login = new_data['login']
            
            if old_login != new_login:
                if messagebox.askyesno("Зміна логіну", "Ви змінюєте логін. Це оновить історію замовлень та відгуків. Продовжити?"):
                    for order in db['orders']:
                        if order['user_login'] == old_login: order['user_login'] = new_login
                    
                    for book in db['books']:
                        if 'reviews' in book:
                            for review in book['reviews']:
                                if review['user'] == old_login: review['user'] = new_login
                else:
                    return 

            for i, usr in enumerate(users):
                if usr['login'] == old_login:
                    usr.update(new_data)
                    self.ctrl.user = usr
                    break
            
            self.ctrl.data_mgr.save(db)
            messagebox.showinfo("Успіх", "Дані успішно оновлено!")
            win.destroy()
            self.ctrl.show("ClientProfileFrame") 

        tk.Button(win, text="💾 ЗБЕРЕГТИ", bg="#27ae60", fg="white", font=("bold", 12), 
                  command=save_changes).pack(pady=30, fill=tk.X, padx=30)

class CartFrame(tk.Frame):
    def __init__(self, parent, ctrl):
        super().__init__(parent)
        self.ctrl = ctrl
        
        tk.Label(self, text="ВАШ КОШИК", font=("Arial", 22, "bold"), pady=10).pack(side=tk.TOP, fill=tk.X)
        
        self.bot = tk.Frame(self, bg="#ecf0f1", height=100, bd=1, relief="raised")
        self.bot.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.scroll = ctrl.create_scrollable_frame(self)
        
        self.render_items()

    def render_items(self):
        for w in self.scroll.winfo_children(): 
            w.destroy()
        
        self.scroll.update()
        self.scroll.master.configure(scrollregion=(0, 0, 1, 1))
        self.scroll.master.yview_moveto(0)
        self.scroll.master.xview_moveto(0)
        
        total = 0
        valid = True 
        d = self.ctrl.data_mgr.load()
        has_post = len(d.get("postal_services", [])) > 0 

        if not self.ctrl.cart:
            tk.Label(self.scroll, text="Кошик порожній", font=("Arial", 14), bg="#f0f2f5").pack(pady=30)
            self.render_bottom_content(0, False)
            return

        for idx, item in enumerate(self.ctrl.cart):
            obj = item['obj']
            q = item['qty']
            pr = item['price']
            

            if isinstance(obj, Book):
                title = obj.title
                img_path = obj.image_path
                discount = obj.discount_percent
                original_price = obj.price
                stock_ok = obj.is_available(q)
                stock_val = obj.stock
                fmt = obj.format
            else:
                title = obj.get('title', 'Комплект')
                img_path = obj.get('image', '')
                discount = 0
                original_price = pr
                stock_ok = True 
                stock_val = 9999
                fmt = "set"

            cost = pr * q
            total += cost
            

            row = tk.Frame(self.scroll, bg="white", pady=5, bd=1, relief="raised")
            row.pack(fill=tk.X, padx=20, pady=2)
            
            self.ctrl.load_image_to_label(row, img_path, 40, 60).pack(side=tk.LEFT, padx=5)
            
            info = tk.Frame(row, bg="white")
            info.pack(side=tk.LEFT, padx=10)
            
            tk.Label(info, text=title, font=("Arial", 11, "bold"), bg="white").pack(anchor='w')

            price_row = tk.Frame(info, bg="white")
            price_row.pack(anchor='w')
            
            # Логіка відображення ціни
            if discount > 0 and item['type'] == 'book':
                tk.Label(price_row, text=f"{original_price:.0f}", font=("Arial", 9, "overstrike"), fg="gray", bg="white").pack(side=tk.LEFT)
                tk.Label(price_row, text=f" {pr:.2f} грн", font=("Arial", 10, "bold"), fg="red", bg="white").pack(side=tk.LEFT)
                tk.Label(price_row, text=f" (-{discount}%)", font=("Arial", 8), fg="red", bg="white").pack(side=tk.LEFT)
            else:
                tk.Label(price_row, text=f"{pr:.2f} грн", font=("Arial", 10), fg="gray", bg="white").pack(side=tk.LEFT)


            if item['type'] == 'book' and not stock_ok:
                tk.Label(info, text=f"Тільки {stock_val} шт!", fg="red", bg="white", font=("bold", 8)).pack(anchor='w')
                valid = False
            
            # --- КНОПКИ УПРАВЛІННЯ ---
            ctrls = tk.Frame(row, bg="white")
            ctrls.pack(side=tk.RIGHT, padx=10)

            tk.Label(ctrls, text=f"{cost:.2f} грн", font=("bold", 11), width=10, bg="white", anchor='e').pack(side=tk.RIGHT, padx=5)
            
            # Кнопки +/-
            qty_fr = tk.Frame(ctrls, bg="white", bd=1, relief="solid")
            qty_fr.pack(side=tk.RIGHT, padx=5)
            tk.Button(qty_fr, text="-", width=2, bd=0, bg="#ecf0f1", command=lambda i=idx: self.chg(i, -1)).pack(side=tk.LEFT)
            tk.Label(qty_fr, text=f"{q}", font=("bold", 10), bg="white", width=3).pack(side=tk.LEFT)
            tk.Button(qty_fr, text="+", width=2, bd=0, bg="#ecf0f1", command=lambda i=idx: self.chg(i, 1)).pack(side=tk.LEFT)
            
            # Видалення
            tk.Button(ctrls, text="✕", fg="red", bg="white", bd=0, font=("Arial", 10, "bold"),
                      command=lambda i=idx: self.rem(i)).pack(side=tk.RIGHT, padx=5)

        self.render_bottom_content(total, valid and has_post)

    def render_bottom_content(self, tot, ok):
        for w in self.bot.winfo_children(): w.destroy()
        
        info = tk.Frame(self.bot, bg="#ecf0f1")
        info.pack(side=tk.LEFT, padx=30, pady=15)
        tk.Label(info, text="До сплати:", font=("Arial", 12), bg="#ecf0f1", fg="gray").pack(anchor='w')
        tk.Label(info, text=f"{tot:.2f} грн", font=("Arial", 20, "bold"), bg="#ecf0f1", fg="#2c3e50").pack(anchor='w')
        
        actions = tk.Frame(self.bot, bg="#ecf0f1")
        actions.pack(side=tk.RIGHT, padx=30)
        
        if not ok and self.ctrl.cart:
             tk.Label(actions, text="Перевірте наявність або служби доставки", fg="red", bg="#ecf0f1").pack(pady=5)
        st = "normal" if ok else "disabled"
        tk.Button(actions, text="Продовжити покупки", bg="white", fg="black", font=("bold",10),
                  command=lambda: self.ctrl.show("ClientFrame")).pack(side=tk.LEFT, padx=10)
    
        tk.Button(actions, text="ОФОРМИТИ ЗАМОВЛЕННЯ ➡", bg="#27ae60", fg="white", font=("Arial", 12, "bold"), 
                  state=st, padx=20, pady=5,
                  command=lambda: self.ctrl.show("CheckoutFrame", tot)).pack(side=tk.LEFT)

    def chg(self, i, d):
        self.ctrl.cart[i]['qty'] += d
        if self.ctrl.cart[i]['qty'] < 1: self.ctrl.cart[i]['qty'] = 1
        self.render_items()

    def rem(self, i):
        del self.ctrl.cart[i]
        self.render_items()

class CheckoutFrame(tk.Frame):
    def __init__(self, parent, ctrl, items_total):
        super().__init__(parent, bg="#f4f6f7")
        self.ctrl = ctrl
        self.items_total = items_total 
        
        self.original_total = 0
        for item in self.ctrl.cart:
            obj = item['obj']
            qty = item['qty']

            if isinstance(obj, Book):

                price_value = obj.price
            else:

                price_value = obj['price']
                
            self.original_total += price_value * qty
        
        self.is_birthday = False
        try:
            today = datetime.now()
            udob = datetime.strptime(ctrl.user['dob'], "%d.%m.%Y")
            if today.day == udob.day and today.month == udob.month: 
                self.is_birthday = True
        except: pass

        tk.Label(self, text="ОФОРМЛЕННЯ ЗАМОВЛЕННЯ", font=("Arial", 24, "bold"), bg="#f4f6f7", fg="#2c3e50").pack(pady=20)

        main = tk.Frame(self, bg="#f4f6f7"); main.pack(fill=tk.BOTH, expand=True, padx=50)
        
        left = tk.Frame(main, bg="white", bd=1, relief="solid", padx=20, pady=20)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 20))
        
        tk.Label(left, text="1. Доставка", font=("bold", 14), bg="white").pack(anchor='w', pady=(0,10))
        tk.Label(left, text="Місто:", bg="white").pack(anchor='w'); self.e_city = tk.Entry(left, width=30); self.e_city.pack(anchor='w', pady=2)
        tk.Label(left, text="Адреса / Відділення:", bg="white").pack(anchor='w'); self.e_addr = tk.Entry(left, width=30); self.e_addr.pack(anchor='w', pady=2)
        
        tk.Label(left, text="Служба:", bg="white").pack(anchor='w', pady=(10,0))
        d = ctrl.data_mgr.load()
        posts = [p['name'] for p in d.get('postal_services', [])]
        self.cb_post = ttk.Combobox(left, values=posts); self.cb_post.pack(anchor='w', fill=tk.X)
        self.cb_post.bind("<<ComboboxSelected>>", self.recalc)
        
        tk.Label(left, text="2. Оплата", font=("bold", 14), bg="white").pack(anchor='w', pady=(20,10))
        self.pay_var = tk.StringVar(value="card")
        tk.Radiobutton(left, text="Карткою онлайн", variable=self.pay_var, value="card", bg="white").pack(anchor='w')
        tk.Radiobutton(left, text="При отриманні", variable=self.pay_var, value="cod", bg="white").pack(anchor='w')
        
        tk.Label(left, text="3. Бонуси", font=("bold", 14), bg="white").pack(anchor='w', pady=(20,10))
        u_bonuses = ctrl.user.get("bonuses", 0)
        tk.Label(left, text=f"Доступно: {u_bonuses}", fg="green", bg="white").pack(anchor='w')
        self.bonus_var = tk.IntVar(value=0)
        self.sc_bonus = tk.Scale(left, from_=0, to=u_bonuses, orient=tk.HORIZONTAL, bg="white", variable=self.bonus_var, command=lambda e: self.recalc())
        self.sc_bonus.pack(fill=tk.X)

        # --- RIGHT COLUMN ---
        right = tk.Frame(main, bg="#ecf0f1", bd=1, relief="solid", padx=20, pady=20, width=300)
        right.pack(side=tk.RIGHT, fill=tk.Y)
        right.pack_propagate(False)
        
        tk.Label(right, text="ВАШЕ ЗАМОВЛЕННЯ", font=("bold", 14), bg="#ecf0f1").pack(pady=(0,20))
        
        self.lbl_items = tk.Label(right, text=f"Товари: {self.original_total:.2f} грн", bg="#ecf0f1", anchor='w')
        self.lbl_items.pack(fill=tk.X)
        
        self.lbl_bday = tk.Label(right, text="🔥 Знижка: -0.00", fg="green", bg="#ecf0f1", anchor='w')
        self.lbl_bday.pack(fill=tk.X)
        
        self.lbl_bonus = tk.Label(right, text="💎 Бонуси: -0.00", fg="blue", bg="#ecf0f1", anchor='w')
        self.lbl_bonus.pack(fill=tk.X)
        
        self.lbl_del = tk.Label(right, text="🚚 Доставка: 0.00", bg="#ecf0f1", anchor='w')
        self.lbl_del.pack(fill=tk.X)
        
        tk.Frame(right, height=2, bg="gray").pack(fill=tk.X, pady=20)
        self.lbl_total = tk.Label(right, text="0.00 грн", font=("Arial", 24, "bold"), fg="#e74c3c", bg="#ecf0f1")
        self.lbl_total.pack()
        
        tk.Button(right, text="ПІДТВЕРДИТИ", bg="#27ae60", fg="white", font=("bold", 14), pady=10, command=self.submit).pack(fill=tk.X, side=tk.BOTTOM)
        tk.Button(right, text="Назад", command=lambda: ctrl.show("CartFrame")).pack(side=tk.BOTTOM, pady=10)
        
        self.recalc()

    def recalc(self, _=None):
        bonuses = self.bonus_var.get()
        limit = 1000.0        
        delivery_price = 0.0  

        d = self.ctrl.data_mgr.load()
        selected_post_name = self.cb_post.get()

        if selected_post_name:
             p = next((x for x in d.get('postal_services', []) if x['name'] == selected_post_name), None)
             if p: 
                 limit = float(p.get('free_limit', 1000))
                 delivery_price = float(p.get('price', 0))

        fin = float(self.ctrl.cpp_exec("calc_final_checkout", 
                                       self.items_total, 
                                       1 if self.is_birthday else 0, 
                                       bonuses, 
                                       limit, 
                                       delivery_price))
        
        product_discount = self.original_total - self.items_total
        birthday_discount = 0
        if self.is_birthday:
            birthday_discount = self.items_total * 0.10
            
        total_savings = product_discount + birthday_discount
        price_pre_delivery = (self.items_total - birthday_discount) - bonuses
        del_cost = fin - price_pre_delivery
        if del_cost < 0.01: del_cost = 0 

        self.lbl_bday.config(text=f"🔥 Знижка: -{total_savings:.2f}")
        self.lbl_bonus.config(text=f"💎 Бонуси: -{bonuses:.2f}")
        self.lbl_del.config(text=f"🚚 Доставка: {del_cost:.2f}")
        self.lbl_total.config(text=f"{fin:.2f} грн")
        
        self.final_sum = fin

    def submit(self):
        city, addr, post = self.e_city.get(), self.e_addr.get(), self.cb_post.get()
        if not city or not addr or not post: 
            return messagebox.showerror("Err", "Будь ласка, заповніть всі поля доставки!")
        
        d = self.ctrl.data_mgr.load()
        u = self.ctrl.user
        
        earned_bonus = int(self.ctrl.cpp_exec("calc_earned_bonuses", self.final_sum))

        for usr in d["users"]:
            if usr["login"] == u["login"]:
                usr["bonuses"] = usr.get("bonuses", 0) - self.bonus_var.get() + earned_bonus
                usr["total_spent"] += self.final_sum
                usr["orders_count"] += 1
                self.ctrl.user = usr 
                break
        
        items_str = ", ".join([f"{i['obj'].title} x{i['qty']}" for i in self.ctrl.cart])
        order_id = f"ORD-{random.randint(10000, 99999)}"
        
        o = {
            "id": order_id,
            "user_login": u["login"], 
            "date": str(datetime.now().date()),
            "total": self.final_sum, 
            "city": city, 
            "post": post, 
            "address": addr,
            "items": items_str, 
            "status": "new", 
            "pay_method": self.pay_var.get()
        }
        d["orders"].append(o)
        
        for i in self.ctrl.cart:
            item_obj = i['obj']
            qty = i['qty']
            
            if "isbn" in item_obj:
                for b in d["books"]:
                    if b.get("isbn") == item_obj["isbn"]: b["stock"] -= qty
            
            elif "items" in item_obj and isinstance(item_obj["items"], list):
                for component_isbn in item_obj["items"]:
                    for b in d["books"]:
                        if b.get("isbn") == component_isbn: b["stock"] -= qty

        self.ctrl.data_mgr.save(d)
        
        if u.get("email"):
            try:
                send_order_email(u["email"], order_id, self.ctrl.cart, self.final_sum, earned_bonus, f"{city}, {post}, {addr}")
            except: pass
        
        messagebox.showinfo("Успіх", f"Замовлення {order_id} оформлено!\nБонусів нараховано: +{earned_bonus}")
        self.ctrl.cart = [] 
        self.ctrl.show("ClientFrame")

    def submit(self):
        city, addr, post = self.e_city.get(), self.e_addr.get(), self.cb_post.get()
        if not city or not addr or not post: 
            return messagebox.showerror("Err", "Будь ласка, заповніть всі поля доставки!")
        
        d = self.ctrl.data_mgr.load()
        u = self.ctrl.user
        
        earned_bonus = int(self.ctrl.cpp_exec("calc_earned_bonuses", self.final_sum))
        
        for usr in d["users"]:
            if usr["login"] == u["login"]:
                usr["bonuses"] = usr.get("bonuses", 0) - self.bonus_var.get() + earned_bonus
                usr["total_spent"] += self.final_sum
                usr["orders_count"] += 1
                self.ctrl.user = usr 
                break
        

        items_str = ", ".join([f"{i['obj'].title} x{i['qty']}" for i in self.ctrl.cart])
        
        order_id = f"ORD-{random.randint(10000, 99999)}"
        full_address = f"{city}, {post}, {addr}"

        o = {
            "id": order_id,
            "user_login": u["login"], 
            "date": str(datetime.now().date()),
            "total": self.final_sum, 
            "city": city, 
            "post": post, 
            "address": addr,
            "items": items_str, 
            "status": "new", 
            "pay_method": self.pay_var.get()
        }
        d["orders"].append(o)
        

        for i in self.ctrl.cart:
            item_obj = i['obj']
            qty_to_remove = i['qty']
            

            if isinstance(item_obj, Book):
                for b in d["books"]:
                    if b.isbn == item_obj.isbn: 
                        b.stock -= qty_to_remove
                        break
            
            elif "items" in item_obj and isinstance(item_obj["items"], list):
                for component_isbn in item_obj["items"]:
                    for b in d["books"]:
                        if b.isbn == component_isbn: 
                            b.stock -= qty_to_remove
                            break

        self.ctrl.data_mgr.save(d)
        
        if u.get("email"):
            try:
                send_order_email(
                    to_email=u["email"],
                    order_id=order_id,
                    cart_items=self.ctrl.cart, 
                    total_sum=self.final_sum,
                    bonuses_earned=earned_bonus,
                    address=full_address
                )
            except Exception as e:
                print(f"Помилка відправки листа: {e}")
        
        messagebox.showinfo("Успіх", f"Замовлення {order_id} успішно оформлено!\nНараховано бонусів: +{earned_bonus}")
        self.ctrl.cart = [] 
        self.ctrl.show("ClientFrame")


# ADMIN PART

class AdminDashboard(tk.Frame):
    def __init__(self, parent, ctrl):
        super().__init__(parent); self.ctrl=ctrl
        
        sb = tk.Frame(self, bg="#2c3e50", width=250); sb.pack(side=tk.LEFT, fill=tk.Y); sb.pack_propagate(False)
        tk.Label(sb, text="ADMIN PANEL", bg="#2c3e50", fg="white", font=("Impact", 18)).pack(pady=30)

        btn_exit = tk.Button(sb, text="ВИХІД (LOGOUT)", bg="#c0392b", fg="white", 
                             font=("Arial", 10, "bold"), cursor="hand2",
                             command=lambda: ctrl.show("AuthFrame"))
        btn_exit.pack(side=tk.BOTTOM, fill=tk.X, ipady=10) 

        cv = tk.Canvas(sb, bg="#2c3e50", highlightthickness=0)
        sc = tk.Scrollbar(sb, command=cv.yview, bg="#2c3e50")
        men = tk.Frame(cv, bg="#2c3e50")

        men.bind("<Configure>", lambda e: cv.configure(scrollregion=cv.bbox("all")))
        cv.create_window((0,0), window=men, anchor="nw", width=230)
        cv.configure(yscrollcommand=sc.set)

       
        cv.pack(side="top", fill="both", expand=True) 
       
        
        def btn(txt, cmd, col="#34495e"):
            tk.Button(men, text=txt, bg=col, fg="white", bd=0, anchor='w', padx=20, font=("Arial", 10), cursor="hand2", command=cmd).pack(fill=tk.X, pady=1)
        

        btn("ДАШБОРД / ЗВІТИ", lambda: ctrl.show("AdminReports"), "#2980b9")
        
        def open_warehouse_safe():
            d = ctrl.data_mgr.load()
            has_warehouse = any(c['type'] == 'con_warehouse' and c.get("status") == "active" for c in d.get("contracts", []))
            if has_warehouse:
                ctrl.show("AdminBooks")
            else:
                messagebox.showerror("Доступ заборонено", "У вас немає складу!\nСпочатку підпишіть контракт зі Складом.")

        btn("КНИГИ (СКЛАД)", open_warehouse_safe)
        btn("МАРКЕТИНГ", lambda: ctrl.show("AdminMarketing"))
        btn("КОРИСТУВАЧІ", lambda: ctrl.show("AdminUsers"))
        btn("ЗАМОВЛЕННЯ", lambda: ctrl.show("AdminOrders"))
        btn("ВИРОБНИЦТВО (PIPELINE)", lambda: ctrl.show("AdminProduction"), "#8e44ad")
        
        tk.Label(men, text="КОНТРАКТИ", bg="#2c3e50", fg="#95a5a6", font=("Arial", 9, "bold")).pack(pady=15, anchor='w', padx=10)
        
        cons = [
            ("Український Автор", "con_author_ua", "ukr"), ("Іноземний Автор", "con_author_foreign", "foreign"),
            ("Перекладач", "con_translator", "translator"), ("Альфа-Рідер", "con_reader", "alpha"),
            ("Бета-Рідер", "con_reader", "beta"), ("Редактор", "con_editor", "editor"),
            ("Коректор", "con_editor", "corrector"), ("Ілюстратор", "con_visual", "illustrator"),
            ("Дизайнер", "con_visual", "designer"), ("Верстальник (E-book)", "con_ebook", "layout"),
            ("Друкарня", "con_printer", "printer"), ("Озвучувач", "con_reader", "voice"), ("Звукорежисер", "con_editor", "sound"),
            ("Книгарні", "con_bookstore", None), ("Склад", "con_warehouse", None), ("Пошта", "con_post", None)
        ]
        
        for t, m, r in cons:
            btn(f"{t}", lambda tm=t, mm=m, rr=r: ctrl.show("AdminContracts", {"title":tm, "mode":mm, "role":rr}))
        tk.Label(men, text="", bg="#2c3e50", height=4).pack()
        tk.Button(sb, text="ВИХІД (LOGOUT)", bg="#c0392b", fg="white", font=("Arial", 10, "bold"), cursor="hand2",
                  command=lambda: ctrl.show("AuthFrame")).place(relx=0, rely=1.0, anchor="sw", x=0, y=0, relwidth=1.0, height=50)
        

        main = tk.Frame(self, bg="#ecf0f1"); main.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        tk.Label(main, text="Ласкаво просимо, Адмін!", font=("Arial", 26, "bold"), bg="#ecf0f1", fg="#34495e").place(relx=0.5, rely=0.4, anchor=tk.CENTER)
        tk.Label(main, text="Використовуйте меню зліва для навігації.", font=("Arial", 12), bg="#ecf0f1", fg="#7f8c8d").place(relx=0.5, rely=0.5, anchor=tk.CENTER)

class AdminBase(tk.Frame):
    def __init__(self, parent, ctrl, title):
        super().__init__(parent); self.ctrl=ctrl
        h=tk.Frame(self, bg="white", height=60, bd=1, relief="raised"); h.pack(fill=tk.X)
        tk.Button(h, text="⬅ Меню", bg="#f39c12", fg="white", font=("Arial", 10, "bold"),
                  command=lambda: ctrl.show("AdminDashboard")).pack(side=tk.LEFT, padx=15, pady=10)
        tk.Label(h, text=title, font=("Arial", 16, "bold"), bg="white", fg="#2c3e50").pack(side=tk.LEFT, padx=20)

class AdminProduction(AdminBase):
    def __init__(self, parent, ctrl):
        super().__init__(parent, ctrl, "Виробничий Конвеєр")
        self.scroll = ctrl.create_scrollable_frame(self)
        self.load_projects()
    
    def load_projects(self):
        for w in self.scroll.winfo_children(): w.destroy()
        d = self.ctrl.data_mgr.load()
        projects = d.get("projects", [])
        
        if not projects:
            tk.Label(self.scroll, text="Немає активних проектів. Підпишіть контракт з Автором, щоб розпочати.", 
                     bg="#f0f2f5", fg="gray", font=("Arial", 12)).pack(pady=50)
            return

        for p in reversed(projects):
            self.create_project_card(p)

    def create_project_card(self, p):
        card = tk.Frame(self.scroll, bg="white", bd=1, relief="raised", padx=15, pady=15)
        card.pack(fill=tk.X, padx=30, pady=10)
        
        h = tk.Frame(card, bg="white"); h.pack(fill=tk.X)
        src_text = "Іноземна" if "foreign" in p.get("source_type", "") else "Українська"
        tk.Label(h, text=f"📘 {p['book_title']} ({p['type'].upper()} | {src_text})", font=("bold",14), bg="white").pack(side=tk.LEFT)
        tk.Label(h, text=f"ID: {p['id']}", fg="gray", bg="white").pack(side=tk.RIGHT)
        
        can = tk.Canvas(card, bg="white", height=180, highlightthickness=0); can.pack(fill=tk.X, pady=10)
        
        vis_st = []
        txt_st = []
        mrg_st = []
        
        if p['type'] == 'audio':
            vis_st = ["illustrator", "designer"] 
            if "foreign" in p.get("source_type",""):
                txt_st = ["translator", "alpha", "editor", "corrector", "beta", "voice", "sound"]
            else:
                txt_st = ["editor", "corrector", "beta", "voice", "sound"]
            mrg_st = ["layout", "published"] 

        elif p['type'] == 'ebook':
            vis_st = ["illustrator", "designer"]
            if "foreign" in p.get("source_type",""):
                txt_st = ["translator", "alpha", "editor", "corrector", "beta"]
            else:
                txt_st = ["editor", "corrector", "beta"]
            mrg_st = ["layout", "published"]

        else: 
            vis_st = ["illustrator", "designer"]
            if "foreign" in p.get("source_type",""):
                txt_st = ["translator", "alpha", "editor", "corrector", "beta"]
            else:
                txt_st = ["editor", "corrector", "beta"]
            mrg_st = ["layout", "printer", "published"]

        w_step = 130; start_x = 60
        y_vis, y_mrg, y_txt = 40, 90, 140
        
        def draw_node(x, y, label, is_done, is_active):
            col = "#2ecc71" if is_done else ("#f39c12" if is_active else "#bdc3c7")
            can.create_oval(x, y, x+30, y+30, fill=col, outline=col)
            can.create_text(x+15, y-15 if y < y_mrg else y+45, text=label.title(), font=("Arial", 8, "bold"), fill="#34495e")
            return x+30, y+15

        if vis_st:
            for i, s in enumerate(vis_st):
                nx, ny = draw_node(start_x + i*w_step, y_vis, s, p['vis_step']>i, p['vis_step']==i)
                if i < len(vis_st)-1: can.create_line(nx, ny, start_x + (i+1)*w_step, y_vis+15, fill="#bdc3c7", width=2)

        for i, s in enumerate(txt_st):
            nx, ny = draw_node(start_x + i*w_step, y_txt, s, p['txt_step']>i, p['txt_step']==i)
            if i < len(txt_st)-1: can.create_line(nx, ny, start_x + (i+1)*w_step, y_txt+15, fill="#bdc3c7", width=2)

        merge_x = start_x + max(len(vis_st), len(txt_st)) * w_step + 40
        
        if vis_st:
            can.create_line(start_x + (len(vis_st)-1)*w_step + 30, y_vis+15, merge_x, y_mrg+15, fill="#95a5a6", dash=(4,2))
        
        can.create_line(start_x + (len(txt_st)-1)*w_step + 30, y_txt+15, merge_x, y_mrg+15, fill="#95a5a6", dash=(4,2))

        branches_done = (p['vis_step'] >= len(vis_st)) and (p['txt_step'] >= len(txt_st))
        
        for i, s in enumerate(mrg_st):
            done = p['main_step'] > i
            active = (p['main_step'] == i and branches_done)
            if not branches_done and i==0: 
                can.create_text(merge_x + 15, y_mrg-20, text="Очікування", fill="red", font=("Arial",8))
            nx, ny = draw_node(merge_x + i*w_step, y_mrg, s, done, active)
            if i < len(mrg_st)-1: can.create_line(nx, ny, merge_x + (i+1)*w_step, y_mrg+15, fill="#bdc3c7", width=2)

        ctrl = tk.Frame(card, bg="#f9f9f9", pady=5); ctrl.pack(fill=tk.X)
        
        if p['vis_step'] < len(vis_st):
            req = vis_st[p['vis_step']]
            self.render_stage_btn(ctrl, p, "vis", req, side=tk.LEFT)
        else: tk.Label(ctrl, text="Візуал завершено", fg="green", bg="#f9f9f9").pack(side=tk.LEFT, padx=10)

        if p['txt_step'] < len(txt_st):
            req = txt_st[p['txt_step']]
            self.render_stage_btn(ctrl, p, "txt", req, side=tk.LEFT)
        else: tk.Label(ctrl, text="Основа завершена", fg="green", bg="#f9f9f9").pack(side=tk.LEFT, padx=10)

        if branches_done:
            if p['main_step'] < len(mrg_st):
                req = mrg_st[p['main_step']]
                if req == "published":
                    tk.Button(ctrl, text="ДОДАТИ В МАГАЗИН", bg="green", fg="white", command=lambda: self.open_publish_window(p)).pack(side=tk.RIGHT)
                else:
                    self.render_stage_btn(ctrl, p, "main", req, side=tk.RIGHT)
            else: tk.Label(ctrl, text="ГОТОВО", fg="#8e44ad", font=("bold",12), bg="#f9f9f9").pack(side=tk.RIGHT, padx=10)
        else: tk.Label(ctrl, text="Очікування", fg="gray", bg="#f9f9f9").pack(side=tk.RIGHT, padx=10)

    def render_stage_btn(self, parent, p, branch, role, side):
        d = self.ctrl.data_mgr.load()
        con = None
        pending = next((x for x in d.get("notifications",[]) if x['project_id']==p['id'] and x['role']==role and x['status']=='pending'), None)
        

        for c in d["contracts"]:
            if c.get("project_id") and c.get("project_id") == p["id"] and c.get("role") == role:
                con = c; break
            elif not c.get("project_id") and p['book_title'] in c['details'] and c.get('role') == role:
                con = c; break
        
        if not con:
            if pending:
                tk.Label(parent, text="✉️ Запит надіслано", fg="blue", bg="#f9f9f9").pack(side=side, padx=5)
            else:
                tk.Button(parent, text=f"Запит на контракт: {role.title()}", bg="#3498db", fg="white",
                          command=lambda: self.send_notification(p, role)).pack(side=side, padx=5)
        else:
            if con.get("status") == "done":
                tk.Button(parent, text=f"➡ Завершити: {role.title()}", bg="#27ae60", fg="white",
                          command=lambda: self.check_files_and_advance(p, branch, role)).pack(side=side, padx=5)
            else:
                tk.Label(parent, text=f"⏳ {role} в роботі...", fg="#f39c12", bg="#f9f9f9").pack(side=side, padx=5)

    def check_files_and_advance(self, p, branch, role):
        self.advance_stage(p, branch)

    def send_notification(self, p, role):
        d = self.ctrl.data_mgr.load()
        d["notifications"].append({
            "project_id": p['id'], "role": role, "book_title": p['book_title'], "status": "pending"
        })
        self.ctrl.data_mgr.save(d)
        messagebox.showinfo("Сповіщення", f"Надіслано запит у відділ контрактів: {role}")
        self.load_projects()

    def advance_stage(self, p, branch):
        d = self.ctrl.data_mgr.load()
        for proj in d["projects"]:
            if proj["id"] == p["id"]:
                if branch == "vis": proj["vis_step"] += 1
                elif branch == "txt": proj["txt_step"] += 1
                elif branch == "main": proj["main_step"] += 1
        self.ctrl.data_mgr.save(d); self.load_projects()

    def open_publish_window(self, p):
        win = tk.Toplevel(self); win.title("Публікація Книги"); win.geometry("500x700")
        tk.Label(win, text="Фінальні дані книги", font=("bold",14)).pack(pady=10)
        
        ents = {}
        tk.Label(win, text="ISBN:").pack(anchor="w", padx=20)
        e = tk.Entry(win); e.pack(fill=tk.X, padx=20); ents["isbn"]=e
        
        tk.Label(win, text="Категорія:").pack(anchor="w", padx=20)
        cb_cat = ttk.Combobox(win, values=list(CATEGORIES_CONFIG.keys()))
        cb_cat.pack(fill=tk.X, padx=20); ents["category"] = cb_cat
        
        tk.Label(win, text="Підкатегорія:").pack(anchor="w", padx=20)
        cb_sub = ttk.Combobox(win); cb_sub.pack(fill=tk.X, padx=20); ents["subcategory"] = cb_sub
        
        def update_subs(e):
            cat_key = cb_cat.get()
            if cat_key in CATEGORIES_CONFIG:
                subs_dict = CATEGORIES_CONFIG[cat_key]["subs"]
                cb_sub['values'] = list(subs_dict.keys()) 
                if cb_sub['values']: cb_sub.current(0)
        cb_cat.bind("<<ComboboxSelected>>", update_subs)

        tk.Label(win, text="Обкладинка (Файл):").pack(anchor="w", padx=20)
        e_cov = tk.Entry(win); e_cov.pack(fill=tk.X, padx=20); ents["cover"]=e_cov
        tk.Button(win, text="...", command=lambda: e_cov.insert(0, filedialog.askopenfilename())).pack(anchor="e", padx=20)

        tk.Label(win, text="Ціна:").pack(anchor="w", padx=20); e_pr = tk.Entry(win); e_pr.pack(fill=tk.X, padx=20); ents["price"]=e_pr
        tk.Label(win, text="Сток:").pack(anchor="w", padx=20); e_st = tk.Entry(win); e_st.pack(fill=tk.X, padx=20); ents["stock"]=e_st
        tk.Label(win, text="Рік:").pack(anchor="w", padx=20); e_yr = tk.Entry(win); e_yr.pack(fill=tk.X, padx=20); ents["year"]=e_yr
        tk.Label(win, text="Сторінок:").pack(anchor="w", padx=20); e_pg = tk.Entry(win); e_pg.pack(fill=tk.X, padx=20); ents["pages"]=e_pg
        tk.Label(win, text="Вага (г):").pack(anchor="w", padx=20); e_wg = tk.Entry(win); e_wg.pack(fill=tk.X, padx=20); ents["weight"]=e_wg
        
        tk.Label(win, text="Опис:").pack(anchor="w", padx=20); e_ds = tk.Entry(win); e_ds.pack(fill=tk.X, padx=20); ents["desc"]=e_ds
        tk.Label(win, text="Уривок:").pack(anchor="w", padx=20); e_ex = tk.Entry(win); e_ex.pack(fill=tk.X, padx=20); ents["excerpt"]=e_ex

        if p['type'] in ['ebook','audio']: e_st.insert(0, "9999")

        def commit():
            d = self.ctrl.data_mgr.load()
            has_warehouse = False
            for c in d.get("contracts", []):
                if c["type"] == "con_warehouse" and c.get("status") == "active":
                    has_warehouse = True
                    break
            if p['type'] not in ['ebook', 'audio'] and not has_warehouse:
                return messagebox.showerror("Помилка", "Неможливо опублікувати фізичну книгу!\nСпочатку підпишіть контракт зі Складом.")

            for proj in d["projects"]:
                if proj["id"] == p["id"]: proj["main_step"] += 1
            
            fmt = "physical"
            if p['type']=='ebook': fmt="electronic"
            elif p['type']=='audio': fmt="audio"
            
            local_img = self.ctrl.save_image_safe(ents["cover"].get())
            
            new_b = {
                "isbn": ents["isbn"].get(), "title": p["book_title"], 
                "author_name":"(Контракт)", "author_surname":"(Контракт)", 
                "category":cb_cat.get(), "subcategory":cb_sub.get(), "format":fmt,
                "price": float(ents["price"].get() or 0), "stock": int(ents["stock"].get() or 0), 
                "ratings":[], "image_path":local_img, "description":ents["desc"].get(),
                "year": ents["year"].get(), "pages": ents["pages"].get(), "weight": ents["weight"].get(),
                "excerpt": ents["excerpt"].get(), "reviews": []
            }
            d["books"].append(new_b); self.ctrl.data_mgr.save(d)
            messagebox.showinfo("Успіх", "Книга додана в магазин!"); win.destroy(); self.load_projects()
            
        tk.Button(win, text="ОПУБЛІКУВАТИ", bg="green", fg="white", font=("bold",12), command=commit).pack(pady=20)


class AdminContracts(AdminBase):
    def __init__(self, parent, ctrl, data):
        super().__init__(parent, ctrl, f"Контракт: {data['title']}")
        self.mode = data['mode']
        self.role = data.get('role')
        self.book_prefill = data.get('book_prefill', "")
        
        self.target_project_id = data.get('project_id') 

        self.service_modes = ["con_bookstore", "con_warehouse", "con_post"]

        left = tk.Frame(self, bg="#f8f9fa", width=400, bd=1, relief="ridge"); left.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10); left.pack_propagate(False)
        right = tk.Frame(self); right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(left, text="Нова угода", font=("bold",12), bg="#f8f9fa").pack(pady=10)
        self.ents={}
        self.rights_var = tk.StringVar(value="print")
        
        fmap = {
            "con_author_ua": ["ПІБ Автора", "Назва Книги", "Аванс (грн)", "Тираж (шт)", "Роздрібна ціна (грн)", "Роялті (%)"],
            "con_author_foreign": ["ПІБ Автора", "Назва Книги", "Вартість Прав (грн)", "Тираж (шт)", "Роздрібна ціна (грн)", "Роялті (%)"],
            "con_post": ["Служба доставки", "Прогноз посилок (шт/міс)", "Ціна доставки (грн)", "Безкоштовно від (грн)"],
            "con_bookstore": ["Мережа книгарень", "Назва Книги", "Кількість (шт)", "Роздрібна ціна (грн)", "Знижка мережі (%)"],
            "con_warehouse": ["Назва Складу", "Площа (м2)", "Оренда за м2 (грн)", "Термін оренди (міс)"],
            "default": ["Контрагент", "Предмет угоди", "Параметр 1", "Параметр 2"]
        }
        
        if self.role == "translator": 
            fmap[self.mode] = ["ПІБ Перекладача", "Назва Книги", "Обсяг (знаків)", "Ставка (за 1000 зн)"]
        elif self.role in ["alpha", "beta", "editor", "corrector", "sound"]: 
            fmap[self.mode] = ["ПІБ Спеціаліста", "Назва Книги", "Обсяг робіт", "Ставка (грн)"]
        elif self.role == "illustrator": 
            fmap[self.mode] = ["ПІБ Ілюстратора", "Назва Книги", "К-сть ілюстрацій", "Ціна за 1 ілюстрацію"]
        elif self.role == "designer": 
            fmap[self.mode] = ["ПІБ Дизайнера", "Назва Книги", "Вартість обкладинки (грн)"]
        elif self.role == "voice": 
            fmap[self.mode] = ["ПІБ Актора озвучки", "Назва Книги", "Тривалість (годин)", "Ціна за годину"]
        elif self.role == "layout": 
            fmap[self.mode] = ["ПІБ Верстальника", "Назва Книги", "Кількість форматів", "Ціна за формат"]
        elif self.role == "printer": 
            fmap[self.mode] = ["Назва Друкарні", "Назва Книги", "Тираж (шт)", "Ціна паперу (за аркуш)", "Вартість друку (за 1 шт)"]

        fields = fmap.get(self.mode, fmap["default"])
        
        if "author" in self.mode:
            tk.Label(left, text="Тип Прав:", bg="#f8f9fa").pack(anchor='w', padx=10)
            cb = ttk.Combobox(left, textvariable=self.rights_var, values=["Друк", "E-book", "Audio", "Друк+E-book", "Друк+Audio", "E-book+Audio", "Всі права"]); cb.pack(fill=tk.X, padx=10); cb.current(0)

        for f in fields:
            tk.Label(left, text=f, anchor='w', bg="#f8f9fa").pack(fill=tk.X, padx=10)
            
            if self.mode == "con_bookstore" and f == "Назва Книги":
                d = self.ctrl.data_mgr.load()
                books_data = d.get("books", [])
                available_titles = [b.title for b in books_data if b.stock > 0]
                if not available_titles:
                    tk.Label(left, text="(Склад порожній)", fg="red", bg="#f8f9fa", font=("Arial", 8)).pack(anchor='w', padx=10)
                cb_books = ttk.Combobox(left, values=available_titles, state="readonly")
                cb_books.pack(fill=tk.X, padx=10)
                self.ents[f] = cb_books
                self.ents[f].bind("<<ComboboxSelected>>", self.on_bookstore_select)
            else:
                e = tk.Entry(left)
                e.pack(fill=tk.X, padx=10)
                self.ents[f] = e
                if "Книг" in f and self.book_prefill and self.mode != "con_bookstore": 
                    e.delete(0, tk.END); e.insert(0, self.book_prefill)
                    e.config(state="readonly")

        if self.mode not in self.service_modes:
            tk.Label(left, text="Дедлайн:", anchor='w', bg="#f8f9fa").pack(fill=tk.X, padx=10, pady=(10,0))
            self.ed=tk.Entry(left)
            self.ed.pack(fill=tk.X, padx=10)
            self.ed.insert(0, (datetime.now()+timedelta(days=30)).strftime("%Y-%m-%d"))
        
        tk.Button(left, text="ПІДПИСАТИ", bg="#27ae60", fg="white", font=("bold", 10), command=self.save).pack(pady=20, fill=tk.X, padx=10)
        
        if self.mode not in self.service_modes:
            tk.Label(right, text="Очікують підписання (Клікніть щоб заповнити)", fg="red", font=("bold",10)).pack(anchor='w')
            self.notif_frame = tk.Frame(right, height=100); self.notif_frame.pack(fill=tk.X, pady=5)
            self.load_notifications()
        
        tk.Label(right, text="Архів угод", font=("bold",10)).pack(anchor='w', pady=(10,0))
        self.scroll = ctrl.create_scrollable_frame(right, bg_color="white")
        self.load()

    def on_bookstore_select(self, event):
        selected_title = self.ents["Назва Книги"].get()
        if not selected_title: return
        d = self.ctrl.data_mgr.load()
        books_data = d.get("books", [])
        target_book = next((b for b in books_data if b.title == selected_title), None)
        if target_book:
            price = target_book.price
            stock = target_book.stock
            if "Роздрібна ціна (грн)" in self.ents:
                self.ents["Роздрібна ціна (грн)"].delete(0, tk.END)
                self.ents["Роздрібна ціна (грн)"].insert(0, str(price))
            if "Кількість (шт)" in self.ents:
                self.ents["Кількість (шт)"].delete(0, tk.END)
                self.ents["Кількість (шт)"].insert(0, str(stock)) 
                self.ents["Кількість (шт)"].config(bg="#e8f8f5") 

    def load_notifications(self):
        if not hasattr(self, 'notif_frame'): return
        for w in self.notif_frame.winfo_children(): w.destroy()
        d = self.ctrl.data_mgr.load()
        notifs = [n for n in d.get("notifications", []) if n['role'] == self.role and n['status'] == 'pending']
        if not notifs: tk.Label(self.notif_frame, text="Немає запитів", fg="gray").pack()
        for n in notifs:
            b = tk.Button(self.notif_frame, text=f"Запит на: {n['book_title']}", bg="#ffdddd", anchor='w',
                          command=lambda x=n: self.fill_from_notif(x))
            b.pack(fill=tk.X, pady=1)

    def fill_from_notif(self, n):
        keys = list(self.ents.keys())
        target_key = keys[1] if len(keys) > 1 else keys[0]
        if isinstance(self.ents[target_key], tk.Entry):
            self.ents[target_key].delete(0, tk.END)
            self.ents[target_key].insert(0, n['book_title'])
            self.ents[target_key].config(bg="#e8f8f5")
            self.current_notif_id = n
            self.target_project_id = n.get('project_id')

    

    def finish_work(self, c):
        skip_list = ["printer", "warehouse", "bookstore", "con_post"]
        path = ""
        if c.get('role') not in skip_list and self.mode not in skip_list:
            path = filedialog.askopenfilename(title=f"Прикріпити роботу від {c['party']}")
            if not path: return messagebox.showwarning("Увага", "Прикріпіть файл!")
        d = self.ctrl.data_mgr.load()
        for x in d["contracts"]:
            if x["id"] == c["id"]: x["status"] = "done"; x["file"] = path
        match = re.search(r"BOOK:\s*(.+?)(?:\s*\}|$)", c['details'])
        if match:
            book_title = match.group(1).strip()
            for p in d["projects"]:
                if p["book_title"] == book_title:
                    if "submissions" not in p: p["submissions"] = {}
                    p["submissions"][c.get("role", "unknown")] = path
        self.ctrl.data_mgr.save(d); self.load(); messagebox.showinfo("Успіх", "Роботу здано!")

    def st(self, c, s):
        d = self.ctrl.data_mgr.load()
        for x in d["contracts"]: 
            if x["id"]==c["id"]: x["status"]=s
        self.ctrl.data_mgr.save(d); self.load()

    def dele(self, c):
        if messagebox.askyesno("?","Видалити?"):
            d = self.ctrl.data_mgr.load()
            d["contracts"] = [x for x in d["contracts"] if x["id"]!=c["id"]]
            self.ctrl.data_mgr.save(d); self.load()

    def on_bookstore_select(self, event):
        selected_title = self.ents["Назва Книги"].get()
        if not selected_title: return
        d = self.ctrl.data_mgr.load()
        books_data = d.get("books", [])
        target_book = next((b for b in books_data if b.title == selected_title), None)
        if target_book:
            price = target_book.price
            stock = target_book.stock
            if "Роздрібна ціна (грн)" in self.ents:
                self.ents["Роздрібна ціна (грн)"].delete(0, tk.END)
                self.ents["Роздрібна ціна (грн)"].insert(0, str(price))
            if "Кількість (шт)" in self.ents:
                self.ents["Кількість (шт)"].delete(0, tk.END)
                self.ents["Кількість (шт)"].insert(0, str(stock)) 
                self.ents["Кількість (шт)"].config(bg="#e8f8f5") 

    def load_notifications(self):
        if not hasattr(self, 'notif_frame'): return
        for w in self.notif_frame.winfo_children(): w.destroy()
        d = self.ctrl.data_mgr.load()
        notifs = [n for n in d.get("notifications", []) if n['role'] == self.role and n['status'] == 'pending']
        if not notifs: tk.Label(self.notif_frame, text="Немає запитів", fg="gray").pack()
        for n in notifs:
            b = tk.Button(self.notif_frame, text=f"Запит на: {n['book_title']}", bg="#ffdddd", anchor='w',
                          command=lambda x=n: self.fill_from_notif(x))
            b.pack(fill=tk.X, pady=1)

    def fill_from_notif(self, n):
        keys = list(self.ents.keys())
        target_key = keys[1] if len(keys) > 1 else keys[0]
        if isinstance(self.ents[target_key], tk.Entry):
            self.ents[target_key].delete(0, tk.END)
            self.ents[target_key].insert(0, n['book_title'])
            self.ents[target_key].config(bg="#e8f8f5")
            self.current_notif_id = n
            self.target_project_id = n.get('project_id')

    def save(self):
        v = {k: x.get().strip() for k, x in self.ents.items()}

        if not all(v.values()):
            return messagebox.showerror("Помилка", "Будь ласка, заповніть усі поля")
        
        # Валідація
        numeric_keywords = ["Ціна", "Вартість", "Тираж", "Роялті", "Аванс", "Ліміт", "Знижка", 
                            "Кількість", "Ставка", "Обсяг", "Годин", "Площа", "Прогноз", "Оренда"]
        
        for label_text, value in v.items():
             is_numeric_field = any(keyword in label_text for keyword in numeric_keywords)
             if is_numeric_field:
                 clean_val = value.replace(",", ".")
                 try:
                     float_val = float(clean_val)
                     if float_val < 0: return messagebox.showerror("Помилка", f"Поле '{label_text}' не може бути від'ємним!")
                 except ValueError:
                     return messagebox.showerror("Помилка", f"У полі '{label_text}' має бути число")

        d = self.ctrl.data_mgr.load()
        party = list(v.values())[0] 
        res = ""
        nums_for_cpp = []
        mode_to_execute = self.mode


        if self.mode == "con_bookstore":
            qty_req = int(v.get("Кількість (шт)", 0))
            nums_for_cpp = [str(qty_req), v["Роздрібна ціна (грн)"].replace(",", "."), v["Знижка мережі (%)"].replace(",", ".")]
            book_t = v.get("Назва Книги", "")
            found_book = next((b for b in d["books"] if b.title == book_t), None)
            if not found_book: return messagebox.showerror("Помилка", "Книгу не знайдено!")
            if found_book.stock < qty_req: return messagebox.showerror("Помилка", f"На складі лише {found_book.stock} шт.")
            found_book.stock -= qty_req
        elif self.mode in ["con_author_ua", "con_author_foreign"]:
            key_base = "Аванс (грн)" if self.mode == "con_author_ua" else "Вартість Прав (грн)"
            nums_for_cpp = [v[key_base].replace(",", "."), v["Тираж (шт)"].replace(",", "."), v["Роздрібна ціна (грн)"].replace(",", "."), v["Роялті (%)"].replace(",", ".")]
        elif self.mode == "con_warehouse":
            nums_for_cpp = [v["Площа (м2)"].replace(",", "."), v["Оренда за м2 (грн)"].replace(",", "."), v["Термін оренди (міс)"].replace(",", ".")]
        elif self.mode == "con_printer":
            nums_for_cpp = [v["Тираж (шт)"].replace(",", "."), v["Назва Книги"], v["Ціна паперу (за аркуш)"].replace(",", "."), v["Вартість друку (за 1 шт)"].replace(",", ".")]
        elif self.mode == "con_post":
            nums_for_cpp = [
                v["Прогноз посилок (шт/міс)"].replace(",", "."), 
                v["Ціна доставки (грн)"].replace(",", ".")
            ]
        elif self.mode == "con_ebook":
             nums_for_cpp = [
                 v["Кількість форматів"].replace(",", "."), 
                 v["Ціна за формат"].replace(",", ".")
             ]
        elif self.mode == "con_translator":
            nums_for_cpp = [v["Обсяг (знаків)"].replace(",", "."), v["Ставка (за 1000 зн)"].replace(",", ".")]
        elif self.role in ["illustrator", "designer", "editor", "corrector", "sound", "voice", "alpha", "beta"]:
            
            if self.role == "illustrator":
                 nums_for_cpp = [v["К-сть ілюстрацій"].replace(",", "."), v["Ціна за 1 ілюстрацію"].replace(",", ".")]
                 mode_to_execute = "con_visual"
            
            elif self.role == "designer":
                 nums_for_cpp = ["1.0", v["Вартість обкладинки (грн)"].replace(",", ".")]
                 mode_to_execute = "con_visual"
            
            elif self.role == "voice":
                 nums_for_cpp = [v["Тривалість (годин)"].replace(",", "."), v["Ціна за годину"].replace(",", ".")]
                 mode_to_execute = "con_audio"
            

            elif self.role in ["alpha", "beta"]:
                 nums_for_cpp = [v["Обсяг робіт"].replace(",", "."), v["Ставка (грн)"].replace(",", ".")]
                 mode_to_execute = "con_reader" 
            
            else: 

                 nums_for_cpp = [v["Обсяг робіт"].replace(",", "."), v["Ставка (грн)"].replace(",", ".")]
                 mode_to_execute = "con_editor"
        
        # Виконання C++
        if nums_for_cpp:
            res = self.ctrl.cpp_exec(mode_to_execute, *nums_for_cpp)
        
        try:
            if not res or not re.match(r'^-?\d+(\.\d+)?$', res.strip().replace(',', '.')): 
                if nums_for_cpp: raise ValueError(f"Bad backend response: {res}")
                else: final_cost = 0.0
            else:
                final_cost = float(res)
        except: final_cost = 0.0
        
        if hasattr(self, 'ed'): dl_val = self.ed.get()
        else: dl_val = "Безстроково"

        # Генеруємо ID контракту
        new_con_id = f"C{random.randint(10000,99999)}"
        project_id_to_save = getattr(self, 'target_project_id', None)

        # --- СТВОРЕННЯ ПРОЕКТУ  ---
        if self.mode in ["con_author_ua", "con_author_foreign"]:
            rights = self.rights_var.get()
            b_title = v["Назва Книги"]
            
            new_proj_id = f"P{random.randint(1000,9999)}"
            project_id_to_save = new_proj_id 
            
            p_type = "print"
            if "Audio" in rights and "Друк" not in rights and "E-book" not in rights: p_type = "audio"
            elif "E-book" in rights and "Друк" not in rights: p_type = "ebook"
            
            new_project = {
                "id": new_proj_id,
                "book_title": b_title,
                "type": p_type,
                "source_type": "foreign" if self.mode == "con_author_foreign" else "ua",
                "vis_step": 0, "txt_step": 0, "main_step": 0,
                "submissions": {}
            }

            if "projects" not in d: d["projects"] = []
            d["projects"].append(new_project)
            
            messagebox.showinfo("Новий проект", f"Створено проект '{b_title}' у виробництві!")


        con = {
            "id": new_con_id, 
            "type": self.mode, 
            "role": self.role if self.role else "author", 
            "party": party, 
            "date": str(datetime.now().date()), 
            "deadline": dl_val,
            "details": str(v), 
            "cost": float(final_cost), 
            "status": "active",
            "project_id": project_id_to_save 
        }
        d["contracts"].append(con)
        
        if self.mode == "con_post":
            new_service = {
                "name": v["Служба доставки"],
                "price": float(v["Ціна доставки (грн)"].replace(",", ".")),
                "free_limit": float(v["Безкоштовно від (грн)"].replace(",", "."))
            }
            
            if "postal_services" not in d: d["postal_services"] = []
            d["postal_services"] = [s for s in d["postal_services"] if s["name"] != new_service["name"]]
            
            d["postal_services"].append(new_service)
            
        self.ctrl.data_mgr.save(d) 
        self.load()
        
        msg_type = "Нараховано дохід" if self.mode == "con_bookstore" else "Витрати"
        messagebox.showinfo("Успіх", f"Угоду підписано! {msg_type}: {final_cost:.2f} грн")

    def load(self):
        for w in self.scroll.winfo_children(): w.destroy()
        cs = [c for c in self.ctrl.data_mgr.load()["contracts"] if c["type"] == self.mode]
        for c in reversed(cs):
            fr = tk.Frame(self.scroll, bg="white", bd=1, relief="solid", padx=10, pady=5)
            fr.pack(fill=tk.X, padx=10, pady=5)
            tk.Label(fr, text=f"{c['party']} | Дедлайн: {c.get('deadline','?')}", font=("Arial", 11, "bold"), bg="white").pack(anchor='w')
            tk.Label(fr, text=c['details'], bg="white", fg="gray", wraplength=500, justify="left").pack(anchor='w', pady=(2,5))
            bfs = tk.Frame(fr, bg="white"); bfs.pack(fill=tk.X, pady=(0, 5))
            if c.get("status") != "done":
                if c["type"] in self.service_modes:
                    tk.Label(bfs, text="АКТИВНИЙ", fg="#27ae60", bg="white", font=("Arial", 8, "bold")).pack(side=tk.LEFT)
                else:
                    tk.Button(bfs, text="ЗДАТИ", bg="#2ecc71", font=("Arial",8, "bold"), command=lambda x=c: self.finish_work(x)).pack(side=tk.LEFT)
                    tk.Button(bfs, text="Очікування", bg="#f1c40f", font=("Arial",8), command=lambda x=c: self.st(x, "delayed")).pack(side=tk.LEFT, padx=5)
            else:
                tk.Label(bfs, text="ЗАВЕРШЕНО", fg="green", bg="white", font=("Arial", 8, "bold")).pack(side=tk.LEFT)
                if c.get("file"): tk.Label(bfs, text=f"📎 {os.path.basename(c['file'])[:15]}...", fg="gray", bg="white", font=("Arial", 8)).pack(side=tk.LEFT, padx=5)
            tk.Button(bfs, text="🗑 Видалити", fg="white", bg="#c0392b", bd=0, font=("Arial", 8), command=lambda x=c: self.dele(x)).pack(side=tk.LEFT, padx=20)

    def finish_work(self, c):
        skip_list = ["printer", "warehouse", "bookstore", "con_post"]
        path = ""
        if c.get('role') not in skip_list and self.mode not in skip_list:
            path = filedialog.askopenfilename(title=f"Прикріпити роботу від {c['party']}")
            if not path: return messagebox.showwarning("Увага", "Прикріпіть файл!")
        d = self.ctrl.data_mgr.load()
        for x in d["contracts"]:
            if x["id"] == c["id"]: x["status"] = "done"; x["file"] = path
        match = re.search(r"BOOK:\s*(.+?)(?:\s*\}|$)", c['details'])
        if match:
            book_title = match.group(1).strip()
            for p in d["projects"]:
                if p["book_title"] == book_title:
                    if "submissions" not in p: p["submissions"] = {}
                    p["submissions"][c.get("role", "unknown")] = path
        self.ctrl.data_mgr.save(d); self.load(); messagebox.showinfo("Успіх", "Роботу здано!")

    def st(self, c, s):
        d = self.ctrl.data_mgr.load()
        for x in d["contracts"]: 
            if x["id"]==c["id"]: x["status"]=s
        self.ctrl.data_mgr.save(d); self.load()

    def dele(self, c):
        if messagebox.askyesno("?","Видалити?"):
            d = self.ctrl.data_mgr.load()
            d["contracts"] = [x for x in d["contracts"] if x["id"]!=c["id"]]
            self.ctrl.data_mgr.save(d); self.load()

class AdminBooks(AdminBase):
    def __init__(self, parent, ctrl):
        super().__init__(parent, ctrl, "Склад Книг (Інвентар)")
        left = tk.Frame(self); left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.right = tk.Frame(self, bg="#f0f0f0", width=450, bd=1, relief="solid"); self.right.pack(side=tk.RIGHT, fill=tk.Y); self.right.pack_propagate(False)
        
        top = tk.Frame(left); top.pack(fill=tk.X, padx=4, pady=4)
        self.e_search = tk.Entry(top); self.e_search.pack(side=tk.LEFT)
        tk.Button(top, text="Пошук", command=self.load).pack(side=tk.LEFT)
        self.cb_sort = ttk.Combobox(top, values=["Ціна ↑", "Ціна ↓", "Залишок ↑", "Автор A-Z"]); self.cb_sort.pack(side=tk.LEFT, padx=5)
        self.cb_sort.bind("<<ComboboxSelected>>", lambda e: self.load())
        
        cols = ("ISBN", "Назва", "Автор", "Ціна", "Сток", "Жанр", "Рейтинг")
        self.tree = ctrl.create_scrolled_tree(left, cols)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        
        self.load()
        self.render_form(None)

    def load(self):
        for i in self.tree.get_children(): 
            self.tree.delete(i)
        
        d = self.ctrl.data_mgr.load()
        books = d["books"] 

        q = self.e_search.get().lower()
        if q: 
            books = [b for b in books if q in b.title.lower() or q in b.isbn]

        s = self.cb_sort.get()
        if "Ціна ↑" in s: 
            books.sort(key=lambda x: x.price)
        elif "Ціна ↓" in s: 
            books.sort(key=lambda x: x.price, reverse=True)
            
        for b in books:

            rt = b.get_avg_rating()
            

            self.tree.insert("", tk.END, values=(
                b.isbn, 
                b.title, 
                b.author_surname, 
                b.price, 
                b.stock, 
                b.category, 
                f"{rt:.1f}"
            ))

    def on_select(self, e):
        sel = self.tree.selection()
        if not sel: return
        

        isbn = self.tree.item(sel[0])['values'][0]
        
        d = self.ctrl.data_mgr.load()

        book = next((b for b in d["books"] if str(b.isbn) == str(isbn)), None)
        
        self.render_form(book)

    def render_form(self, b):
        for w in self.right.winfo_children(): w.destroy()
        
        header_txt = "Редагування книги" if b else "Додавання книги"
        tk.Label(self.right, text=header_txt, font=("Arial", 14, "bold"), bg="#f0f0f0", fg="#333").pack(pady=(15, 10))

        canvas = tk.Canvas(self.right, bg="#f0f0f0", highlightthickness=0)
        form_frame = tk.Frame(canvas, bg="#f0f0f0")
        scrollbar = ttk.Scrollbar(self.right, orient="vertical", command=canvas.yview)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.create_window((0, 0), window=form_frame, anchor="nw", width=420)

        form_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        self.edit_ents = {}
        
        # --- КАТЕГОРІЯ ---
        tk.Label(form_frame, text="Category:", anchor='w', bg="#f0f0f0", font=("bold", 9)).pack(fill=tk.X, padx=15, pady=(5,0))
        cb_cat = ttk.Combobox(form_frame, values=list(CATEGORIES_CONFIG.keys()), state="readonly")
        cb_cat.pack(fill=tk.X, padx=15, pady=2)
        if b: cb_cat.set(b.category)
        self.edit_ents["category"] = cb_cat
        
        # --- ПІДКАТЕГОРІЯ ---
        tk.Label(form_frame, text="Subcategory:", anchor='w', bg="#f0f0f0", font=("bold", 9)).pack(fill=tk.X, padx=15, pady=(5,0))
        cb_sub = ttk.Combobox(form_frame, state="readonly")
        cb_sub.pack(fill=tk.X, padx=15, pady=2)
        if b: cb_sub.set(b.subcategory) 
        self.edit_ents["subcategory"] = cb_sub
        
        def upd_sub(e): 
            vals = CATEGORIES_CONFIG.get(cb_cat.get(), {}).get("subs", {})
            cb_sub['values'] = list(vals.keys())
            if vals: cb_sub.current(0)
        cb_cat.bind("<<ComboboxSelected>>", upd_sub)

        # --- ФОРМАТ ---
        tk.Label(form_frame, text="Format:", anchor='w', bg="#f0f0f0", font=("bold", 9)).pack(fill=tk.X, padx=15, pady=(5,0))
        cb_fmt = ttk.Combobox(form_frame, values=["physical", "electronic", "audio"], state="readonly")
        cb_fmt.pack(fill=tk.X, padx=15, pady=2)
        
        # ПРАВИЛЬНО: b.format
        current_fmt = b.format if b else "physical" 
        cb_fmt.set(current_fmt)
        self.edit_ents["format"] = cb_fmt

        # --- СТОРІНКИ / ТРИВАЛІСТЬ ---
        self.lbl_pages_duration = tk.Label(form_frame, text="Pages:", anchor='w', bg="#f0f0f0", font=("bold", 9))
        self.lbl_pages_duration.pack(fill=tk.X, padx=15, pady=(5,0))
        
        self.e_pages_duration = tk.Entry(form_frame)
        self.e_pages_duration.pack(fill=tk.X, padx=15, pady=2)
        
        def on_format_change(event=None):
            fmt = cb_fmt.get()
            if fmt == "audio":
                self.lbl_pages_duration.config(text="Duration (minutes):")
            else:
                self.lbl_pages_duration.config(text="Pages:")
        
        cb_fmt.bind("<<ComboboxSelected>>", on_format_change)
        on_format_change() 

        if b:
            val = b.duration if b.format == "audio" else b.pages
            self.e_pages_duration.insert(0, str(val) if val else "")
        
        self.edit_ents["pages_or_duration"] = self.e_pages_duration

        # --- ОСНОВНІ ПОЛЯ (Цикл) ---
        flds = ["isbn", "title", "author_name", "author_surname", "price", "stock", "description", "year", "weight", "excerpt"]
        
        for f in flds:
            display_name = f.replace("_", " ").title()
            tk.Label(form_frame, text=f"{display_name}:", anchor='w', bg="#f0f0f0", font=("bold", 9)).pack(fill=tk.X, padx=15, pady=(5,0))
            e = tk.Entry(form_frame)
            e.pack(fill=tk.X, padx=15, pady=2)

            if b: e.insert(0, str(getattr(b, f, "")))
            
            self.edit_ents[f] = e

        # --- ФОТО ---
        tk.Label(form_frame, text="Cover Image:", anchor='w', bg="#f0f0f0", font=("bold", 9)).pack(fill=tk.X, padx=15, pady=(5,0))
        fr_img = tk.Frame(form_frame, bg="#f0f0f0")
        fr_img.pack(fill=tk.X, padx=15, pady=2)
        e_img = tk.Entry(fr_img)
        e_img.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        if b: e_img.insert(0, b.image_path)
        
        tk.Button(fr_img, text="📂", width=3, command=lambda: e_img.insert(0, filedialog.askopenfilename())).pack(side=tk.RIGHT, padx=(5,0))
        self.edit_ents["image_path"] = e_img
        
        # --- КНОПКИ ---
        btn_fr = tk.Frame(form_frame, bg="#f0f0f0", pady=20)
        btn_fr.pack(fill=tk.X, padx=15)

        tk.Button(btn_fr, text="ЗБЕРЕГТИ ЗМІНИ", bg="#27ae60", fg="white", font=("Arial", 10, "bold"), pady=8,
                  command=lambda: self.save(b)).pack(fill=tk.X, pady=5)
        
        tk.Button(btn_fr, text="Очистити форму", bg="#3498db", fg="white", font=("Arial", 9), pady=5,
                  command=lambda: self.render_form(None)).pack(fill=tk.X, pady=5)
        
        if b: 
            tk.Button(btn_fr, text="ВИДАЛИТИ КНИГУ", bg="#c0392b", fg="white", font=("Arial", 9, "bold"), pady=5,
                      command=lambda: self.delete(b)).pack(fill=tk.X, pady=(15, 5))
            
    def save(self, old_b):
        d = self.ctrl.data_mgr.load()
        
        has_warehouse = any(c['type'] == 'con_warehouse' and c.get("status") == "active" for c in d.get("contracts", []))
        
        if not old_b and not has_warehouse:
             return messagebox.showerror("Помилка", "Немає активного контракту зі складом!\nДодавання нових книг заборонено.")


        new_b_dict = {k: v.get() for k,v in self.edit_ents.items() if k != "pages_or_duration"}
        
        dyn_val = self.edit_ents["pages_or_duration"].get()
        

        if new_b_dict.get("format") == "audio":
            new_b_dict["duration"] = dyn_val
            new_b_dict["pages"] = "-" 
        else:
            new_b_dict["pages"] = dyn_val
            new_b_dict["duration"] = "-" 


        try: 
            new_b_dict['price'] = float(new_b_dict['price'])
            new_b_dict['stock'] = int(new_b_dict['stock'])
        except: 
            return messagebox.showerror("Err", "Ціна та Сток мають бути числами!")

        if old_b:

            new_b_dict['ratings'] = old_b.ratings
            new_b_dict['reviews'] = old_b.reviews

            new_b_dict['isbn'] = old_b.isbn 
        else:

            new_b_dict['ratings'] = []
            new_b_dict['reviews'] = []



        new_book_obj = Book(new_b_dict)

        new_book_obj.image_path = self.ctrl.save_image_safe(new_b_dict['image_path'])

        if old_b: 

            d["books"] = [x for x in d["books"] if x.isbn != old_b.isbn]
        

        d["books"].append(new_book_obj)
        self.ctrl.data_mgr.save(d)
        
        messagebox.showinfo("Успіх", "Дані успішно збережено!")
        self.load()
        self.render_form(None)

    def delete(self, b):

        if messagebox.askyesno("Підтвердження", f"Ви впевнені, що хочете видалити книгу '{b.title}'?"):
            d = self.ctrl.data_mgr.load()
            

            d["books"] = [x for x in d["books"] if x.isbn != b.isbn]
            
            self.ctrl.data_mgr.save(d)
            self.load()
            self.render_form(None)

class AdminMarketing(AdminBase):
    def __init__(self, parent, ctrl):
        super().__init__(parent, ctrl, "МАРКЕТИНГ ТА АКЦІЇ")
        
        style = ttk.Style()
        style.configure("TNotebook", background="#ecf0f1")
        
        self.nb = ttk.Notebook(self)
        self.nb.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        self.tab_discounts = tk.Frame(self.nb, bg="#ecf0f1")
        self.tab_sets = tk.Frame(self.nb, bg="#ecf0f1")
        self.tab_news = tk.Frame(self.nb, bg="#ecf0f1")
        
        self.nb.add(self.tab_discounts, text="🏷️ Знижки")
        self.nb.add(self.tab_sets, text="📦 Комплекти")
        self.nb.add(self.tab_news, text="📰 Новини")

        self._setup_discounts_tab()
        self._setup_sets_tab()
        self._setup_news_tab()

    
    # TAB 1: Discounts
    
    def _setup_discounts_tab(self):
        left = tk.Frame(self.tab_discounts, bg="#ecf0f1")
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        right = tk.Frame(self.tab_discounts, bg="#ecf0f1")
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        lf_add = tk.LabelFrame(left, text="Нова знижка", bg="white", padx=10, pady=10)
        lf_add.pack(fill=tk.X)
        
        tk.Label(lf_add, text="Оберіть книгу:", bg="white").pack(anchor='w')
        
        d = self.ctrl.data_mgr.load()

        book_values = [f"{b.title} (ISBN: {b.isbn})" for b in d['books']]
        
        self.cb_books = ttk.Combobox(lf_add, values=book_values, state="readonly")
        self.cb_books.pack(fill=tk.X, pady=5)
        
        tk.Label(lf_add, text="Відсоток знижки (%):", bg="white").pack(anchor='w')
        self.e_proc = tk.Entry(lf_add)
        self.e_proc.pack(fill=tk.X, pady=5)
        
        tk.Button(lf_add, text="Застосувати", bg="#27ae60", fg="white", font=("bold", 10),
                  pady=5, command=self.apply_discount).pack(fill=tk.X, pady=10)

        lf_list = tk.LabelFrame(right, text="Активні знижки", bg="white", padx=10, pady=10)
        lf_list.pack(fill=tk.BOTH, expand=True)
        
        self.tree_disc = self.ctrl.create_scrolled_tree(lf_list, ["Назва", "ISBN", "Знижка"])
        
        tk.Button(lf_list, text="Прибрати знижку", bg="#e74c3c", fg="white", 
                  command=self.remove_discount).pack(fill=tk.X, pady=5)
        
        self.load_discounts_table()

    def load_discounts_table(self):
        for i in self.tree_disc.get_children(): self.tree_disc.delete(i)
        d = self.ctrl.data_mgr.load()
        for b in d['books']:

            if b.discount_percent > 0:
                self.tree_disc.insert("", tk.END, values=(b.title, b.isbn, f"{b.discount_percent}%"))

    def apply_discount(self):
        sel = self.cb_books.get()
        if not sel: return messagebox.showerror("Err", "Оберіть книгу!")
        try:
            val = int(self.e_proc.get())
            if not (0 <= val <= 100): raise ValueError
        except: return messagebox.showerror("Err", "Відсоток має бути 0-100")
        
        isbn = sel.split('(ISBN: ')[1][:-1]
        
        d = self.ctrl.data_mgr.load()
        for b in d['books']:

            if b.isbn == isbn:
                b.discount_percent = val
        
        self.ctrl.data_mgr.save(d)
        self.load_discounts_table()
        messagebox.showinfo("OK", "Знижку оновлено!")

    def remove_discount(self):
        sel = self.tree_disc.selection()
        if not sel: return
        isbn = self.tree_disc.item(sel[0])['values'][1] 
        
        d = self.ctrl.data_mgr.load()
        for b in d['books']:

            if str(b.isbn) == str(isbn):
                b.discount_percent = 0
        
        self.ctrl.data_mgr.save(d)
        self.load_discounts_table()


    # TAB 2: Sets

    def _setup_sets_tab(self):
        left = tk.Frame(self.tab_sets, bg="#ecf0f1"); left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        right = tk.Frame(self.tab_sets, bg="#ecf0f1"); right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        lf = tk.LabelFrame(left, text="Новий комплект", bg="white", padx=10, pady=10)
        lf.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(lf, text="Назва:", bg="white").pack(anchor='w')
        self.e_set_title = tk.Entry(lf); self.e_set_title.pack(fill=tk.X)
        
        tk.Label(lf, text="Ціна:", bg="white").pack(anchor='w')
        self.e_set_price = tk.Entry(lf); self.e_set_price.pack(fill=tk.X)
        
        tk.Label(lf, text="Фото:", bg="white").pack(anchor='w')
        fr_img = tk.Frame(lf, bg="white"); fr_img.pack(fill=tk.X)
        self.e_set_img = tk.Entry(fr_img); self.e_set_img.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(fr_img, text="...", command=lambda: self.e_set_img.insert(0, filedialog.askopenfilename())).pack(side=tk.LEFT)
        
        tk.Label(lf, text="Оберіть книги (Ctrl+Клік):", bg="white").pack(anchor='w', pady=(10,0))
        
        lb_frame = tk.Frame(lf); lb_frame.pack(fill=tk.BOTH, expand=True)
        sb = tk.Scrollbar(lb_frame); sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.lb_books = tk.Listbox(lb_frame, selectmode=tk.MULTIPLE, height=6, yscrollcommand=sb.set)
        self.lb_books.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.config(command=self.lb_books.yview)
        
        d = self.ctrl.data_mgr.load()

        for b in d['books']: self.lb_books.insert(tk.END, f"{b.title} (ISBN: {b.isbn})")
        
        tk.Button(lf, text="Створити комплект", bg="#2980b9", fg="white", 
                  command=self.add_set).pack(fill=tk.X, pady=10)
        
        lf_list = tk.LabelFrame(right, text="Існуючі комплекти", bg="white", padx=10, pady=10)
        lf_list.pack(fill=tk.BOTH, expand=True)
        
        self.tree_sets = self.ctrl.create_scrolled_tree(lf_list, ["Назва", "Ціна"])
        
        tk.Button(lf_list, text="Видалити комплект", bg="#e74c3c", fg="white", 
                  command=self.delete_set).pack(fill=tk.X, pady=5)
        
        self.load_sets_table()

    def load_sets_table(self):
        for i in self.tree_sets.get_children(): self.tree_sets.delete(i)
        for s in self.ctrl.data_mgr.load().get('book_sets', []):
            self.tree_sets.insert("", tk.END, values=(s['title'], f"{s['price']} грн"))

    def add_set(self):
        idxs = self.lb_books.curselection()
        if not idxs: return messagebox.showerror("Err", "Оберіть хоча б одну книгу")
        try: pr = float(self.e_set_price.get())
        except: return messagebox.showerror("Err", "Ціна некоректна")
        
        d = self.ctrl.data_mgr.load()
        all_books = d.get('books', [])
        

        isbns = [all_books[i].isbn for i in idxs if i < len(all_books)]
        
        path = self.ctrl.save_image_safe(self.e_set_img.get())
        
        new_set = {
            "title": self.e_set_title.get(),
            "price": pr,
            "image": path,
            "items": isbns
        }
        
        if 'book_sets' not in d: d['book_sets'] = []
        d['book_sets'].append(new_set)
        self.ctrl.data_mgr.save(d)
        self.load_sets_table()
        messagebox.showinfo("OK", "Комплект створено!")

    def delete_set(self):
        sel = self.tree_sets.selection()
        if not sel: return
        idx = self.tree_sets.index(sel[0])
        
        if messagebox.askyesno("?", "Видалити цей комплект?"):
            d = self.ctrl.data_mgr.load()
            del d['book_sets'][idx]
            self.ctrl.data_mgr.save(d)
            self.load_sets_table()


    # TAB 3: News


    def _setup_news_tab(self):
        left = tk.Frame(self.tab_news, bg="#ecf0f1"); left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        right = tk.Frame(self.tab_news, bg="#ecf0f1"); right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        lf = tk.LabelFrame(left, text="Публікація новини", bg="white", padx=10, pady=10)
        lf.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(lf, text="Заголовок:", bg="white").pack(anchor='w')
        self.e_news_title = tk.Entry(lf); self.e_news_title.pack(fill=tk.X)
        
        tk.Label(lf, text="Текст:", bg="white").pack(anchor='w')
        self.t_news_content = tk.Text(lf, height=5); self.t_news_content.pack(fill=tk.BOTH, expand=True)
        
        fr_img = tk.Frame(lf, bg="white"); fr_img.pack(fill=tk.X, pady=5)
        self.e_news_img = tk.Entry(fr_img); self.e_news_img.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(fr_img, text="Фото...", command=lambda: self.e_news_img.insert(0, filedialog.askopenfilename())).pack(side=tk.LEFT)
        
        self.v_main_news = tk.BooleanVar()
        tk.Checkbutton(lf, text="Головна новина (на банер)", variable=self.v_main_news, bg="white").pack(anchor='w')
        
        tk.Button(lf, text="Опублікувати", bg="#8e44ad", fg="white", command=self.add_news).pack(fill=tk.X, pady=10)
        
        lf_list = tk.LabelFrame(right, text="Опубліковані новини", bg="white", padx=10, pady=10)
        lf_list.pack(fill=tk.BOTH, expand=True)
        
        self.tree_news = self.ctrl.create_scrolled_tree(lf_list, ["Дата", "Заголовок"])
        
        tk.Button(lf_list, text="Видалити новину", bg="#e74c3c", fg="white", 
                  command=self.delete_news).pack(fill=tk.X, pady=5)
        
        self.load_news_table()

    def load_news_table(self):
        for i in self.tree_news.get_children(): self.tree_news.delete(i)
        for n in self.ctrl.data_mgr.load().get('news', []):
            title = n['title']
            if n.get('is_main'): title = "⭐" + title
            self.tree_news.insert("", tk.END, values=(n.get('date', '-'), title))

    def add_news(self):
        title = self.e_news_title.get()
        content = self.t_news_content.get("1.0", tk.END).strip()
        if not title: return messagebox.showerror("Err", "Введіть заголовок")
        
        d = self.ctrl.data_mgr.load()
        if self.v_main_news.get():
            for n in d['news']: n['is_main'] = False 
            
        path = self.ctrl.save_image_safe(self.e_news_img.get())
        
        new_n = {
            "title": title, "content": content, "image": path,
            "date": str(datetime.now().date()), "is_main": self.v_main_news.get()
        }
        
        d.setdefault('news', []).insert(0, new_n)
        self.ctrl.data_mgr.save(d)
        self.load_news_table()
        messagebox.showinfo("OK", "Новину додано!")

    def delete_news(self):
        sel = self.tree_news.selection()
        if not sel: return
        idx = self.tree_news.index(sel[0])
        
        if messagebox.askyesno("?", "Видалити новину?"):
            d = self.ctrl.data_mgr.load()
            del d['news'][idx]
            self.ctrl.data_mgr.save(d)
            self.load_news_table()

class AdminUsers(AdminBase):
    def __init__(self, parent, ctrl):
        super().__init__(parent, ctrl, "Користувачі (Cards)")
        
        top = tk.Frame(self); top.pack(fill=tk.X, padx=10, pady=5)
        self.es = tk.Entry(top); self.es.pack(side=tk.LEFT)
        tk.Button(top, text="🔍", command=self.load).pack(side=tk.LEFT)
        
        self.cb_sort = ttk.Combobox(top, values=["Всі", "Адміни", "Клієнти", "Заблоковані", "Топ Витрат"])
        self.cb_sort.pack(side=tk.LEFT, padx=10)
        self.cb_sort.bind("<<ComboboxSelected>>", lambda e: self.load())
        self.cb_sort.set("Всі") 

        self.scroll = ctrl.create_scrollable_frame(self)
        self.load()

    def load(self):
        for w in self.scroll.winfo_children(): w.destroy()
        
        d = self.ctrl.data_mgr.load()
        us = d["users"]
        q = self.es.get().lower()
        s = self.cb_sort.get()

        if q:
            us = [u for u in us if q in u['login'].lower() or q in u.get('surname','').lower()]

        if s == "Адміни": us = [u for u in us if u['role'] == 'admin']
        elif s == "Клієнти": us = [u for u in us if u['role'] == 'client']
        elif s == "Заблоковані": us = [u for u in us if u['role'] == 'blocked']
        elif s == "Топ Витрат": us.sort(key=lambda x: x['total_spent'], reverse=True)

        for u in us:
            c = tk.Frame(self.scroll, bg="white", bd=1, relief="raised", padx=10, pady=5)
            c.pack(fill=tk.X, padx=10, pady=5)
            
            icon = "👤"
            if u['role'] == 'admin': icon = "👑"
            elif u['role'] == 'blocked': icon = "🚫"
            
            tk.Label(c, text=icon, font=("Arial", 20), bg="white").pack(side=tk.LEFT)
            
            info = tk.Frame(c, bg="white")
            info.pack(side=tk.LEFT, padx=10)
            
            tk.Label(info, text=f"{u.get('surname','')} {u.get('name','')} ({u['login']})", font=("bold", 11), bg="white").pack(anchor='w')
            tk.Label(info, text=f"Витрачено: {u['total_spent']} грн | Замовлень: {u['orders_count']}", fg="gray", bg="white").pack(anchor='w')
            
            acts = tk.Frame(c, bg="white")
            acts.pack(side=tk.RIGHT)

            if u['role'] == 'admin':
                tk.Button(acts, text="Зняти адміна", bg="#bdc3c7", 
                          command=lambda x=u: self.role(x, 'client')).pack(side=tk.LEFT)
            
            elif u['role'] == 'blocked':
                tk.Button(acts, text="Розблокувати", bg="#2ecc71", fg="white", 
                          command=lambda x=u: self.role(x, 'client')).pack(side=tk.LEFT)
            
            else:
                tk.Button(acts, text="Зробити адміном", bg="#f1c40f", 
                          command=lambda x=u: self.role(x, 'admin')).pack(side=tk.LEFT, padx=2)
                tk.Button(acts, text="Заблокувати", bg="#e74c3c", fg="white", 
                          command=lambda x=u: self.role(x, 'blocked')).pack(side=tk.LEFT, padx=2)

    def role(self, u, r):
        d = self.ctrl.data_mgr.load()
        for x in d["users"]: 
            if x['login'] == u['login']:
                x['role'] = r
                break
        self.ctrl.data_mgr.save(d)
        self.load()

class AdminOrders(AdminBase):
    def __init__(self, parent, ctrl):
        super().__init__(parent, ctrl, "Замовлення (Cards)")
        
        top_bar = tk.Frame(self, bg="#f0f2f5", pady=10)
        top_bar.pack(fill=tk.X, padx=20)

        tk.Label(top_bar, text="Пошук:", bg="#f0f2f5", font=("Arial", 10)).pack(side=tk.LEFT)
        
        self.e_search = tk.Entry(top_bar, width=30, font=("Arial", 10))
        self.e_search.pack(side=tk.LEFT, padx=10)
        self.e_search.bind("<Return>", lambda e: self.load())

        tk.Button(top_bar, text="🔍 Знайти", bg="#3498db", fg="white", 
                  command=self.load).pack(side=tk.LEFT)
        
        tk.Button(top_bar, text="✖ Скинути", command=self.reset_search).pack(side=tk.LEFT, padx=5)

        self.scroll = ctrl.create_scrollable_frame(self)
        self.load()
        
    def reset_search(self):
        self.e_search.delete(0, tk.END)
        self.load()

    def load(self):
        for w in self.scroll.winfo_children(): w.destroy()
        
        d = self.ctrl.data_mgr.load()
        orders = d["orders"]
        
        query = self.e_search.get().lower().strip()
        
        filtered_orders = []
        for o in orders:
            search_text = f"{o['id']} {o['user_login']} {o['city']} {o['address']} {o['items']} {o.get('post','')} {o['status']}".lower()
            
            if query in search_text:
                filtered_orders.append(o)

        if not filtered_orders:
            tk.Label(self.scroll, text="Замовлень не знайдено", fg="gray", font=("Arial", 12)).pack(pady=20)
            return

        for o in reversed(filtered_orders):
            c = tk.Frame(self.scroll, bg="white", bd=1, relief="solid", padx=10, pady=10)
            c.pack(fill=tk.X, padx=20, pady=5)
            
            h = tk.Frame(c, bg="white"); h.pack(fill=tk.X)
            tk.Label(h, text=f"Замовлення #{o['id']}", font=("bold",12), bg="white").pack(side=tk.LEFT)
            
            col = "orange"
            st_text = o['status'].upper()
            if o['status'] == "shipped": col = "green"
            elif o['status'] == "cancelled": col = "red"; st_text = "СКАСОВАНО"
            
            tk.Label(h, text=st_text, fg=col, bg="white", font=("bold", 9)).pack(side=tk.RIGHT)
            
            tk.Label(c, text=f"Клієнт: {o['user_login']}", bg="white").pack(anchor='w')
            tk.Label(c, text=f"Адреса: {o['city']}, {o['address']} ({o.get('post','?')})", bg="white").pack(anchor='w')
            tk.Label(c, text=f"Товари: {o['items']}", fg="gray", bg="white").pack(anchor='w')

            f = tk.Frame(c, bg="white"); f.pack(fill=tk.X, pady=5)
            tk.Label(f, text=f"Сума: {o['total']:.2f} грн", font=("bold",11), bg="white").pack(side=tk.LEFT)
            
            if o['status'] == "new":
                tk.Button(f, text="ВІДПРАВИТИ", bg="#2ecc71", fg="white", command=lambda x=o: self.ship(x)).pack(side=tk.RIGHT)
                tk.Button(f, text="СКАСУВАТИ", bg="#e74c3c", fg="white", command=lambda x=o: self.cancel(x)).pack(side=tk.RIGHT, padx=5)

    def ship(self, o):
        d = self.ctrl.data_mgr.load()
        for x in d["orders"]:
             if x["id"] == o["id"]: x["status"] = "shipped"
        self.ctrl.data_mgr.save(d); self.load()
        
    def cancel(self, o):
        if messagebox.askyesno("?", "Скасувати замовлення?"):
            d = self.ctrl.data_mgr.load()
            for x in d["orders"]:
                 if x["id"] == o["id"]: x["status"] = "cancelled"
            self.ctrl.data_mgr.save(d); self.load()

class AdminReports(AdminBase):
    def __init__(self, parent, ctrl):
        super().__init__(parent, ctrl, "📊 АНАЛІТИЧНИЙ ЦЕНТР")
        
        self.main_scroll = ctrl.create_scrollable_frame(self, bg_color="#ecf0f1")
        
        top_bar = tk.Frame(self.main_scroll, bg="#ecf0f1")
        top_bar.pack(fill=tk.X, padx=20, pady=10)

        filter_frame = tk.Frame(top_bar, bg="#ecf0f1")
        filter_frame.pack(side=tk.LEFT)

        tk.Label(filter_frame, text="Період з:", bg="#ecf0f1", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        self.e_date_from = tk.Entry(filter_frame, width=12)
        self.e_date_from.pack(side=tk.LEFT)

        tk.Label(filter_frame, text="по:", bg="#ecf0f1", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        self.e_date_to = tk.Entry(filter_frame, width=12)
        self.e_date_to.pack(side=tk.LEFT)
        
        today = datetime.now()
        first_day = today.replace(day=1)
        self.e_date_from.insert(0, first_day.strftime("%Y-%m-%d"))
        self.e_date_to.insert(0, today.strftime("%Y-%m-%d"))

        btn_frame = tk.Frame(top_bar, bg="#ecf0f1")
        btn_frame.pack(side=tk.RIGHT)

        tk.Button(btn_frame, text="✖ Скинути", bg="#95a5a6", fg="white", font=("Arial", 9),
                  command=self.reset_filter).pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="Застосувати фільтр", bg="#3498db", fg="white", font=("Arial", 10, "bold"),
                  command=self.refresh).pack(side=tk.LEFT)

        self.content_frame = tk.Frame(self.main_scroll, bg="#ecf0f1")
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.refresh()

    def reset_filter(self):
        self.e_date_from.delete(0, tk.END)
        self.e_date_to.delete(0, tk.END)
        self.refresh()

    def is_date_in_range(self, date_str):
        d_from = self.e_date_from.get().strip()
        d_to = self.e_date_to.get().strip()

        if not d_from and not d_to:
            return True

        try:
            target_date = datetime.strptime(date_str, "%Y-%m-%d")
            
            if d_from:
                start_date = datetime.strptime(d_from, "%Y-%m-%d")
                if target_date < start_date: return False
            
            if d_to:
                end_date = datetime.strptime(d_to, "%Y-%m-%d")
                if target_date > end_date: return False
                
            return True
        except ValueError:
            return True

    def refresh(self):
        for w in self.content_frame.winfo_children(): w.destroy()
        data = self.ctrl.data_mgr.load()
        stats = self.calculate_stats(data)
        self.render_kpi_row(stats)
        columns = tk.Frame(self.content_frame, bg="#ecf0f1")
        columns.pack(fill=tk.BOTH, expand=True, pady=20)
        
        left_col = tk.Frame(columns, bg="#ecf0f1")
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        right_col = tk.Frame(columns, bg="#ecf0f1")
        right_col.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

        self.render_finance_chart(left_col, stats)
        self.render_production_status(left_col, data)
        self.render_bestsellers(right_col, stats)
        self.render_warehouse_alerts(right_col, data)

    def calculate_stats(self, d):
        filtered_orders = [
            o for o in d["orders"] 
            if o["status"] != "cancelled" and self.is_date_in_range(o["date"])
        ]

        filtered_contracts = [
            c for c in d["contracts"] 
            if c["status"] != "cancelled" and self.is_date_in_range(c["date"])
        ]

        web_income = sum(o["total"] for o in filtered_orders)
        
        bookstore_income = sum(c["cost"] for c in filtered_contracts if c["type"] == "con_bookstore")
        
        total_income = web_income + bookstore_income

        expenses = sum(c["cost"] for c in filtered_contracts if c["type"] != "con_bookstore")
        
        profit = total_income - expenses

        avg_check = web_income / len(filtered_orders) if filtered_orders else 0
        
        book_sales = {} 
        
        for o in filtered_orders:
            parts = o.get("items", "").split(", ")
            for p in parts:
                if " x" in p:
                    title, qty_str = p.rsplit(" x", 1)
                    if qty_str.isdigit():
                        book_sales[title] = book_sales.get(title, 0) + int(qty_str)
        
        sorted_books = sorted(book_sales.items(), key=lambda x: x[1], reverse=True)

        return {
            "income": total_income,
            "web_income": web_income,
            "bookstore_income": bookstore_income,
            "expenses": expenses,
            "profit": profit,
            "avg_check": avg_check,
            "bestsellers": sorted_books
        }

    def render_kpi_row(self, s):
        row = tk.Frame(self.content_frame, bg="#ecf0f1")
        row.pack(fill=tk.X)

        def card(parent, title, value, icon, color, subtext=""):
            f = tk.Frame(parent, bg="white", bd=1, relief="raised", padx=15, pady=15)
            f.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
            
            tk.Label(f, text=icon, font=("Arial", 24), bg="white", fg=color).pack(side=tk.LEFT)
            data_f = tk.Frame(f, bg="white")
            data_f.pack(side=tk.LEFT, padx=10)
            
            tk.Label(data_f, text=title, font=("Arial", 10, "bold"), fg="gray", bg="white").pack(anchor='w')
            tk.Label(data_f, text=value, font=("Arial", 16, "bold"), fg="#2c3e50", bg="white").pack(anchor='w')
            if subtext:
                 tk.Label(data_f, text=subtext, font=("Arial", 8), fg="#7f8c8d", bg="white").pack(anchor='w')

        inc_details = f"Сайт: {s['web_income']:.0f} | Опт: {s['bookstore_income']:.0f}"
        
        card(row, "Загальний Дохід", f"{s['income']:.0f} грн", "💰", "#27ae60", inc_details)
        card(row, "Витрати", f"{s['expenses']:.0f} грн", "💸", "#c0392b")
        card(row, "Чистий прибуток", f"{s['profit']:.0f} грн", "📈", "#2980b9" if s['profit']>=0 else "#e74c3c")
        card(row, "Середній чек", f"{s['avg_check']:.0f} грн", "🛒", "#f39c12")

    def render_finance_chart(self, parent, s):
        f = tk.LabelFrame(parent, text="Фінанси (за період)", bg="white", padx=10, pady=10, font=("bold", 10))
        f.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        cw, ch = 400, 200
        can = tk.Canvas(f, bg="white", width=cw, height=ch, highlightthickness=0)
        can.pack(fill=tk.BOTH, expand=True)
        
        max_val = max(s['income'], s['expenses'], 1)
        scale = (ch - 50) / max_val
        
        ih = s['income'] * scale
        can.create_rectangle(50, ch-20-ih, 150, ch-20, fill="#2ecc71", outline="")
        can.create_text(100, ch-25-ih, text=f"+{s['income']:.0f}", font=("Arial", 9, "bold"), fill="#27ae60")
        can.create_text(100, ch-5, text="ДОХІД", font=("Arial", 9))

        eh = s['expenses'] * scale
        can.create_rectangle(250, ch-20-eh, 350, ch-20, fill="#e74c3c", outline="")
        can.create_text(300, ch-25-eh, text=f"-{s['expenses']:.0f}", font=("Arial", 9, "bold"), fill="#c0392b")
        can.create_text(300, ch-5, text="ВИТРАТИ", font=("Arial", 9))
        
        can.create_line(20, ch-20, 380, ch-20, fill="#bdc3c7")

    def render_bestsellers(self, parent, s):
        f = tk.LabelFrame(parent, text="Топ продажів (за період)", bg="white", padx=10, pady=10, font=("bold", 10))
        f.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        if not s['bestsellers']:
            tk.Label(f, text="Немає даних за цей період", bg="white", fg="gray").pack()
            return

        for i, (title, qty) in enumerate(s['bestsellers'][:5]):
            row = tk.Frame(f, bg="white", pady=2)
            row.pack(fill=tk.X)
            tk.Label(row, text=f"{i+1}. {title[:20]}...", width=20, anchor='w', bg="white").pack(side=tk.LEFT)
            tk.Label(row, text=f"{qty} шт.", font=("bold", 9), bg="white").pack(side=tk.RIGHT)

    def render_warehouse_alerts(self, parent, d):
        f = tk.LabelFrame(parent, text="Склад (Актуальний стан)", bg="white", padx=10, pady=10, font=("bold", 10))
        f.pack(fill=tk.BOTH, expand=True)
        
        low = [b for b in d["books"] if b.stock < 10 and b.format == "physical"]
        
        if not low: tk.Label(f, text="✅ Норма", fg="green", bg="white").pack()
        else:
            for b in low[:5]:
                tk.Label(f, text=f"🔴{b.title} ({b.stock} шт)", fg="red", bg="white", anchor='w').pack(fill=tk.X)
        
        val = sum(b.price * b.stock for b in d['books'])
        tk.Label(f, text=f"Активи: {val:,.0f} грн", bg="#ecf0f1", pady=5).pack(fill=tk.X, pady=(10,0))

    def render_production_status(self, parent, d):
        f = tk.LabelFrame(parent, text="Виробництво (В роботі)", bg="white", padx=10, pady=10, font=("bold", 10))
        f.pack(fill=tk.BOTH, expand=True)
        projs = [p for p in d.get("projects", []) if p['main_step'] < 3]
        if not projs: tk.Label(f, text="Немає активних проектів", bg="white", fg="gray").pack()
        else:
            for p in projs[-4:]:
                tk.Label(f, text=f"📘 {p['book_title']}", font=("bold", 9), bg="white", anchor='w').pack(fill=tk.X)
                steps = p.get('vis_step',0) + p.get('txt_step',0) + p.get('main_step',0)
                perc = min(1.0, steps/8)
                c = tk.Canvas(f, height=5, bg="#ecf0f1", highlightthickness=0)
                c.pack(fill=tk.X, pady=(0,5))
                c.create_rectangle(0,0, c.winfo_reqwidth()*perc, 5, fill="purple", width=0)

if __name__ == "__main__":
    app = App()
    app.mainloop()
    
    
    
