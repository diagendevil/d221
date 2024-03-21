from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QListWidgetItem
from ui import Ui_MainWindow
from PyQt5.QtGui import QPixmap, QImage
from PIL.ImageFilter import SHARPEN
from PIL import Image
import os

class Widget(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.workimage = self.ImageProcessor(self.ui)

        # Приклад підключення кнопок до методів ImageProcessor
        self.ui.pushButton.clicked.connect(self.chooseWorkdir)

        #Підкючення кнопок для оброблення
        self.ui.pushButton_6.clicked.connect(self.workimage.do_bw)
        self.ui.pushButton_2.clicked.connect(self.workimage.do_left)



    def chooseWorkdir(self):
        self.workimage.image_load()

    class ImageProcessor:
        def __init__(self, ui):
            self.image = None
            self.dir = None
            self.filename = None
            self.save_dir = None
            self.ui = ui  # Зберігаємо посилання на Ui_MainWindow

            # Додали QListWidget для відображення списку файлів
            self.ui.listWidget.itemClicked.connect(self.showChosenImage)

        def image_load(self):
            # QFileDialog.getExistingDirectory(), воно відображає діалогове вікно, 
            #де користувач може вибрати папку,
            dir = QFileDialog.getExistingDirectory()
            if dir:
                # Отримати список файлів та папок у вибраному каталозі
                files = os.listdir(dir)
                # Вибрати лише файли зображень (з розширеннями .png, .jpeg, .jpg)
                image_files = self.image_filter(files)
                if image_files:
                    # Зберегти шлях до обраного каталогу
                    self.dir = dir
                    # Очистити QListWidget для відображення нового списку файлів
                    self.ui.listWidget.clear()
                    # Додати кожен файл до QListWidget
                    for file in image_files:
                        # Створити елемент QListWidgetItem для кожного файлу
                        item = QListWidgetItem(file)
                        # Встановити дані елемента як шлях до повного файлу
                        item.setData(0, os.path.join(dir, file))
                        # Додати елемент в QListWidget
                        self.ui.listWidget.addItem(item)

                    # Отримати перший елемент списку
                    first_item = self.ui.listWidget.item(0)
                    # Зберегти ім'я першого файлу
                    self.filename = first_item.text()
                    # Зберегти повний шлях до першого файлу
                    image_path = first_item.data(0)
                    # Завантажити зображення з першого файлу та відобразити його
                    self.image = Image.open(image_path)
                    self.showImage(image_path, self.image)

        def showImage(self,path,image):
            self.image = image
            #Маштабуємо зображення, щоб воно вміщалося в QLabel
            q_image= self.convert(image)
            pixmap = QPixmap.fromImage(q_image)
            scaled_pixmap = pixmap.scaled(self.ui.label.width(),self.ui.label.height(), QtCore.Qt.KeepAspectRatio)
            # QtCore.Qt.KeepAspectRatio -використовуємо для вказівки на тип збереження пропорцій
            # при маштабуванні зображення (зберігає пропорції)
            self.ui.label.setPixmap(scaled_pixmap)
            # setPixmap - використовуємо для встановлення зображення на віджет PyQt
            self.ui.label.show()

        def convert(self, pil_image):
            #Конвертуємо зображення у формат "RGBA"
            image = pil_image.convert("RGBA")
            #Отримаємо ширину та висоту зображення
            width, height = image.size
            # Обчислимо кількість байтів для кожного рядка
            bytes = 4 * width
            # Конвертуємо зображення у QImage
            q_image = QImage(image.tobytes("raw","RGBA"), width, height,bytes,QImage.Format_RGBA8888)
            return q_image

        def image_filter(self, files):
            # Створюємо порожній список для зберігання відфільтрованих файлів
            result = []
            # Зазначаємо розширення файлів, які хочемо включити
            extension = ['.png', '.jpeg', '.jpg']
            # Проходимося по кожному файлу у переданому списку
            for file in files:
                # Проходимося по кожному дозволеному розширенню
                for ext in extension:
                    # Перевіряємо, чи файл закінчується заданим розширенням
                    if file.endswith(ext):
                        # Якщо так, додаємо файл до списку результатів
                        result.append(file)
            # Повертаємо відфільтрований список файлів
            return result

        def saveImage(self,path,image):
            try:
                #Стовримо директорію для оброблених зображень
                processed_images_dir = os.path.join(self.dir, "processed_images")
                if not os.path.exists(processed_images_dir):
                    os.makedirs(processed_images_dir)
                # Сформуємо повний шлях для збереження обробленого зображення
                image_path =os.path.join(processed_images_dir, os.path.basename(path))
                # os.path.join - об'єднує шляхи файлів або папок в один
                # os.path.basename - функція, яка повертає отанню чатину шляху до файлу(папки)
                # Зберегти оброблене зображення за вказаним шляхом
                image.save(image_path)
                print("Обролене зображення збережено:", image_path)
            except Exception as e:
                print("Помилка під час saveImage")

        def do_bw(self):
            try:
                self.image = self.image.convert("L") #Робимо ч/б
                # формуємо шлях
                image_path = os.path.join(self.dir, "processed_images",self.filename)
                self.saveImage(image_path, self.image) #зберігаємо фотографію
                self.showImage(image_path, self.image) #відображаємо збережену фотогорафію
            except Exception as e:
                print("Помилка під час do_bw")

        def do_left(self):
            try:
                self.image = self.image.transpose(Image.ROTATE_90)
                # формуємо шлях
                image_path = os.path.join(self.dir, "processed_images",self.filename)
                self.saveImage(image_path, self.image) #зберігаємо фотографію
                self.showImage(image_path, self.image) #відображаємо збережену фотогорафію
            except Exception as e:
                print("Помилка під час do_bw")
        






        def showChosenImage(self, item):
            # Отримуємо текст(ім'я файлу) та шлях до обраного елемента списку
            self.filename = item.text()
            image_path = item.data(0)
            # Відкрити обране зображення за вказаним шляхом
            self.image = Image.open(image_path)
            # Викликаємо функцію showImage для відображення
            self.showImage(image_path, self.image)



app = QApplication([])
ex = Widget()
ex.show()
app.exec_()
