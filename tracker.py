import tkinter as tk
from tkinter import ttk
import tkintermapview
from pyorbital.orbital import Orbital
import datetime as dt
import json
import requests

class Tracker:
    def __init__(self):
        self.window = self.__make_tracker_window()
        self.map_widget = None
        self.control_frame = None
        # Создаем панель управления
        self.control_frame = self.__make_control_panel(self.window)
        # Создаем карту
        self.__create_map()

        self.main()

    def __update_tle(self):
        json_file_path = "numbers.json"
        output_file_path = self.tle_path_var.get()
        with open(json_file_path, 'r') as json_file:
            numbers = json.load(json_file)
        if not isinstance(numbers, list):
            return
        with open(output_file_path, 'w') as output_file:
            for number in numbers:
                try:
                    url = f"https://celestrak.org/NORAD/elements/gp.php?CATNR={number}&FORMAT=tle"
                    response = requests.get(url)
                    response.raise_for_status()
                    output_file.write(response.text.replace('\r', ''))
                    self.status_label.config(text=f"Успешно обработан номер: {number}", fg='green')
                    self.window.update()
                except requests.exceptions.RequestException as e:
                    self.status_label.config(text=f"Ошибка: Ошибка при обработке номера {number}: {e}", fg='red')
                    self.window.update()
        self.status_label.config(text=f"TLE обновлены!", fg='green')

    def __get_sat_list(self):
        with open(self.tle_path_var.get(), 'r') as text_file:
            lines = text_file.readlines()
            names = lines[::3]
            name_strp = []
            for name in names:
                name_strp.append(name.strip())
            return name_strp

    def __make_tracker_window(self):
        root_tk = tk.Tk()
        root_tk.geometry(f"{1920}x{1080}")
        root_tk.title("Спутниковый трекер")
        root_tk.resizable(False, True)
        return root_tk

    def __create_map(self):
        """Создание нового виджета карты"""
        # Если карта уже существует, удаляем её
        if self.map_widget:
            self.map_widget.destroy()

        # Создаем новую карту
        self.map_widget = tkintermapview.TkinterMapView(
            self.window, 
            width=1920, 
            height=1080, 
            corner_radius=0
        )

        self.map_widget.place(x=0, y=0)

        # Устанавливаем начальную позицию
        self.map_widget.set_position(0.0, 0.0)
        self.map_widget.set_zoom(2)
        self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=y&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)  # google satellite

        # Поднимаем панель управления над картой
        if self.control_frame:
            self.control_frame.lift()

    def __make_control_panel(self, root_tk: tk.Tk):
        # Создаем фрейм для панели управления
        control_frame = tk.Frame(root_tk, bg='lightgray', width=350, height=560)
        control_frame.place(x=0, y=0)
        control_frame.pack_propagate(False)

        # Заголовок
        title_label = tk.Label(control_frame, text="Управление трекером", 
                                font=("Arial", 16, "bold"), bg='lightgray')
        title_label.pack(pady=20)

        # Поле для пути к TLE файлу
        tk.Label(control_frame, text="Путь к TLE файлу:", bg='lightgray').pack(pady=5)
        self.tle_path_var = tk.StringVar(value="tle_data.txt")
        tle_path_entry = tk.Entry(control_frame, textvariable=self.tle_path_var, width=40)
        tle_path_entry.pack(pady=2)

        # ComboBox для назвния спутника
        tk.Label(control_frame, text="Отслеживаемый спутник:", bg='lightgray').pack(pady=5)
        sat_list=self.__get_sat_list()
        self.combo = ttk.Combobox(control_frame, values=sat_list, state="readonly")
        self.combo.current(0) # Установить значение по умолчанию
        self.combo.pack(pady=2)

        # Поле для количества точек прогноза
        tk.Label(control_frame, text="Количество точек прогноза:", bg='lightgray').pack(pady=5)
        self.predict_iters_var = tk.IntVar(value=90)
        predict_iters_spinbox = tk.Spinbox(control_frame, from_=1, to=500, 
                                            textvariable=self.predict_iters_var, width=10)
        predict_iters_spinbox.pack(pady=2)

        # Поле для шага прогноза (секунды)
        tk.Label(control_frame, text="Шаг прогноза (секунды):", bg='lightgray').pack(pady=5)
        self.predict_sec_per_step_var = tk.IntVar(value=10)
        predict_sec_spinbox = tk.Spinbox(control_frame, from_=1, to=3600, 
                                        textvariable=self.predict_sec_per_step_var, width=10)
        predict_sec_spinbox.pack(pady=2)

        # Поле для времени прогноза
        tk.Label(control_frame, text="Время прогноза (ГГГГ-ММ-ДД ЧЧ:ММ:СС) UTC+0 :", bg='lightgray').pack(pady=5)
        self.time_predict_var = tk.StringVar(value=dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S"))
        time_predict_entry = tk.Entry(control_frame, textvariable=self.time_predict_var, width=40)
        time_predict_entry.pack(pady=2)

        # Кнопка для установки текущего времени
        current_time_btn = tk.Button(control_frame, text="Текущее время UTC", 
                                    command=self.__set_current_time)
        current_time_btn.pack(pady=2)

        # Кнопка применения настроек
        apply_btn = tk.Button(control_frame, text="Применить настройки и обновить карту", 
                                command=self.__apply_settings,
                                bg='green', fg='white', font=("Arial", 10, "bold"))
        apply_btn.pack(pady=5)

        # Кнопка обновления TLE
        tle_btn = tk.Button(control_frame, text="Обновить TLE", 
                                command=self.__update_tle,
                                bg='gray', fg='white')
        tle_btn.pack(pady=5)

        # Кнопка принудительной перезагрузки карты
        reload_btn = tk.Button(control_frame, text="Перезагрузить карту", 
                                command=self.__reload_map,
                                bg='blue', fg='white')
        reload_btn.pack(pady=5)

        # Статусная строка
        self.status_label = tk.Label(control_frame, text="Готов к работе", 
                                    bg='lightgray', fg='blue')
        self.status_label.pack(pady=10)

        return control_frame

    def __set_current_time(self):
        """Установка текущего времени UTC в поле ввода"""
        current_time = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        self.time_predict_var.set(current_time)

    def __reload_map(self):
        """Принудительная перезагрузка карты"""
        self.status_label.config(text="Перезагрузка карты...", fg='orange')
        self.window.update()

        # Пересоздаем карту
        self.__create_map()
        self.status_label.config(text="Карта перезагружена", fg='green')

    def __split_path_at_antimeridian(self, dots_arr):
        """
        Разбивает путь на сегменты, если есть переход через 180-й меридиан
        Возвращает список сегментов (каждый сегмент - список точек)
        """
        if len(dots_arr) < 2:
            return [dots_arr] if dots_arr else []

        segments = []
        current_segment = [dots_arr[0]]

        for i in range(1, len(dots_arr)):
            prev_lat, prev_lon = current_segment[-1]
            curr_lat, curr_lon = dots_arr[i]
            # Проверяем, есть ли переход через 180-й меридиан
            lon_diff = abs(curr_lon - prev_lon)
            # Если разница долгот больше 180 градусов, значит был переход через антимеридиан
            if lon_diff > 180:
                # Начинаем новый сегмент
                if len(current_segment) > 1:  # Сохраняем сегмент, если в нем больше 1 точки
                    segments.append(current_segment)
                current_segment = [dots_arr[i]]  # Начинаем новый сегмент с текущей точки
            else:
                # Добавляем точку в текущий сегмент
                current_segment.append(dots_arr[i])

        # Добавляем последний сегмент
        if len(current_segment) > 1:
            segments.append(current_segment)
        elif len(current_segment) == 1 and len(segments) == 0:
            # Если всего одна точка во всем пути
            segments.append(current_segment)

        return segments

    def __apply_settings(self):
        """Применение настроек и обновление карты"""
        try:
            # Получаем значения из полей ввода
            sat_name = self.combo.get().strip()
            tle_path = self.tle_path_var.get().strip()
            predict_iters = self.predict_iters_var.get()
            predict_sec_per_step = self.predict_sec_per_step_var.get()
            # Парсим время
            try:
                time_predict = dt.datetime.strptime(self.time_predict_var.get(), "%Y-%m-%d %H:%M:%S")
                time_predict = time_predict.replace(tzinfo=dt.timezone.utc)
            except ValueError:
                self.status_label.config(text="Ошибка: неверный формат времени", fg='red')
                return
            # Перезагружаем карту перед отрисовкой новой траектории
            self.__reload_map()
            # Обновляем статус
            self.status_label.config(text="Вычисление траектории...", fg='orange')
            self.window.update()
            # Вычисляем новую траекторию
            dots_arr = self.__make_predict_dots(
                sat_name=sat_name,
                tle_path=tle_path,
                predict_iters=predict_iters,
                predict_sec_per_step=predict_sec_per_step,
                map_widget=self.map_widget,
                time_predict=time_predict
            )
            # Отображаем путь с учетом разбиения на сегменты
            if dots_arr:
                # Разбиваем путь на сегменты при переходах через 180-й меридиан
                segments = self.__split_path_at_antimeridian(dots_arr)
                if segments:
                    # Отрисовываем каждый сегмент отдельно
                    for i, segment in enumerate(segments):
                        if len(segment) > 1:
                            path = self.map_widget.set_path(
                                segment,
                                color="red"  # Разные цвета, если надо, для наглядности
                            )
                    # Центрируем карту на первой точке первого сегмента
                    self.map_widget.set_position(segments[0][0][0], segments[0][0][1])
                    self.map_widget.set_zoom(2)
                    self.status_label.config(
                        text=f"Траектория обновлена: {len(dots_arr)} точек, {len(segments)} сегментов", 
                        fg='green'
                    )
                else:
                    self.status_label.config(text="Не удалось построить траекторию", fg='red')
            else:
                self.status_label.config(text="Не удалось построить траекторию", fg='red')
        except Exception as e:
            self.status_label.config(text=f"Ошибка: {str(e)}", fg='red')
            import traceback
            traceback.print_exc()

    def __make_predict_dots(self, sat_name: str = "INNOSAT 16 (RS92S7)", 
                            tle_path: str = "tle_data.txt", 
                            predict_iters: int = 90, 
                            predict_sec_per_step: int = 10, 
                            map_widget: tkintermapview.TkinterMapView = None, 
                            time_predict: dt.datetime = None):

        if time_predict is None:
            time_predict = dt.datetime.now(dt.timezone.utc)

        try:
            sat = Orbital(sat_name, tle_file=tle_path)
        except Exception as e:
            self.status_label.config(text=f"Ошибка загрузки TLE: {str(e)}", fg='red')
            return []

        dots_arr = []
        current_time = time_predict

        for i in range(predict_iters):
            try:
                lon, lat, alt = sat.get_lonlatalt(current_time)
                # Создаем маркер
                marker = map_widget.set_marker(
                    lat, lon, 
                    text=f"{' '*25}{current_time.strftime('%H:%M:%S')}",
                    icon = tk.PhotoImage(file="icon.png"),
                    text_color = "#FFFFFF",
                )
                # Добавляем координаты в массив
                dots_arr.append((lat, lon))
                current_time += dt.timedelta(seconds=predict_sec_per_step)
                # Обновляем статус каждые 10 итераций
                if i % 10 == 0:
                    self.status_label.config(text=f"Вычисление... {i+1}/{predict_iters}")
                    self.window.update()
            except Exception as e:
                print(f"Ошибка при вычислении точки {i}: {e}")
                continue
        return dots_arr

    def main(self):
        # начальный расчет
        self.window.after(100, self.__apply_settings)
        self.window.mainloop()

if __name__ == "__main__":
    Tracker()