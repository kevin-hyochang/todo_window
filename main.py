import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import utils
import os
import sys
import tkinter.font

class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Weekly Todo List")

        # 아이콘 설정 (Windows)
        try:
            base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
            icon_path = os.path.join(base_path, "todo.ico")
            self.root.iconbitmap(icon_path)
        except:
            pass  # 아이콘 파일이 없거나 오류가 발생해도 프로그램이 계속 실행되도록 함

        self.config = utils.load_config()
        self.todo_items = self.config['todos']


        ## 이전 버전과 호완성을 위해 추가함

        # show_saturday 설정이 없는 경우 기본값 False로 설정
        if 'show_saturday' not in self.config:
            self.config['show_saturday'] = False
            utils.save_config(self.config)

        if "토요일" not in self.todo_items:
            self.todo_items["토요일"] = {"전체": []}
            utils.save_config(self.config)  # 설정 저장
        ## 이전 버전과 호완성을 위해 추가함

        self.last_click_time = 0  # 마지막 클릭 시간을 저장할 변수
        self.click_timer = None  # 클릭 타이머를 저장할 변수
        self.editing = False  # 편집 상태를 추적할 변수
        
        self.todo_widgets = {}

        self.create_menu()
        self.create_widgets()
        self.check_weekly_reset()
        # 8시간마다 check_weekly_reset 실행
        self.schedule_weekly_reset()
        
    def create_menu(self):
        """메뉴 바 생성"""
        self.menu_bar = tk.Menu(self.root)

        # "설정" 메뉴        
        settings_menu = tk.Menu(self.menu_bar, tearoff=0)

        # BooleanVar 변수를 인스턴스 변수로 저장
        self.reset_button_var = tk.BooleanVar(value=self.config.get('show_reset_button'))
        self.saturday_var = tk.BooleanVar(value=self.config.get('show_saturday'))

        # 체크박스 메뉴 항목 추가
        settings_menu.add_checkbutton(
            label="초기화 버튼 활성화 여부",
            variable=self.reset_button_var,
            command=self.toggle_reset_button
        )
        settings_menu.add_checkbutton(
                label="토요일 활성화",
                variable=self.saturday_var,
                command=self.toggle_saturday
            ) 

        self.menu_bar.add_cascade(label="설정", menu=settings_menu)

        # 메뉴 바를 윈도우에 설정
        self.root.config(menu=self.menu_bar)

    def toggle_reset_button(self):
        """초기화 버튼 활성화 여부 토글"""
        
        self.config['show_reset_button'] = not self.config.get('show_reset_button')
        utils.save_config(self.config)
        self.update_reset_button_checkbutton()
        self.update_widgets()  # 위젯 업데이트

    def toggle_saturday(self):
        """토요일 활성화 여부를 토글합니다."""
        self.config['show_saturday'] = not self.config['show_saturday']
        utils.save_config(self.config)
        # 변경사항을 즉시 반영하기 위해 전체 위젯 새로고침
        self.refresh_widgets()

    def refresh_widgets(self):
        """전체 위젯을 새로고침합니다."""
        # 기존 위젯 제거
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # 위젯 재생성
        self.create_menu()
        self.create_widgets()
        

    def update_reset_button_checkbutton(self):
        """체크박스 상태를 업데이트합니다."""
        self.reset_button_var.set(self.config.get('show_reset_button'))
        
    def update_widgets(self):
        """초기화 버튼 표시 여부만 업데이트"""
        bottom_frame = None
        main_frame = None
        
        # 먼저 main_frame을 찾습니다
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Frame):
                main_frame = widget
                break
        
        if main_frame:
            # main_frame에서 bottom_frame을 찾습니다
            for widget in main_frame.winfo_children():
                if isinstance(widget, ttk.Frame) and widget.grid_info().get('row') == 3:  # 행 번호로 식별
                    bottom_frame = widget
                    break
        
        if bottom_frame:
            # 기존 버튼들 제거
            for widget in bottom_frame.winfo_children():
                widget.destroy()
 
            # show_reset_button 설정에 따라 버튼 다시 생성
            if self.config.get('show_reset_button', True):
                reset_button = ttk.Button(
                    bottom_frame, 
                    text="초기화", 
                    command=self.reset_todos_check,
                    width=10
                )
                reset_button.pack(side="right", padx=5)
        
    def create_widgets(self):
        """요일 및 시간대에 따른 Todo 리스트 위젯 생성"""
        days = self.config.get('days')
        
        if self.config.get('show_saturday') == False:
            if days.count("토요일") > 0:
                days.remove("토요일")
        else :
            if days.count("토요일") == 0:
                days.append("토요일")

        times = self.config.get('times')

        # Grid 레이아웃을 위한 프레임 생성
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # 요일 헤더를 위한 프레임 생성 (높이 고정)
        header_frame = ttk.Frame(main_frame, height=20)
        header_frame.grid(row=0, column=1, columnspan=len(days), sticky="ew")
        header_frame.grid_propagate(False)  # 높이 고정

        # 요일 헤더 생성
        for i, day in enumerate(days):
            # 각 요일 열에 동일한 가중치 부여
            header_frame.columnconfigure(i, weight=1)

            day_label = ttk.Label(header_frame, text=day, anchor="center")
            day_label.grid(row=0, column=i, sticky="nsew", padx=5)
            day_label.bind("<Button-1>", lambda e, d=day: self.clear_all_selections())
            header_frame.columnconfigure(i, weight=1)

        # 오전/오후 헤더를 위한 프레임 생성 (너비 고정)
        time_frame = ttk.Frame(main_frame, width=60)
        time_frame.grid(row=1, column=0, rowspan=len(times), sticky="ns")
        time_frame.grid_propagate(False)  # 너비 고정

        # 오전/오후 헤더 생성
        for i, time in enumerate(times):
            time_label = ttk.Label(time_frame, text=time, anchor="center")
            time_label.grid(row=i, column=0, sticky="nsew", pady=5)
            time_label.configure(justify="center")  # 텍스트 중앙 정렬
            time_frame.rowconfigure(i, weight=1)

        # Todo 리스트 생성
        for i, time in enumerate(times):
            for j, day in enumerate(days):
     
                if day == "토요일":
                    if i ==0:
                        frame = ttk.Frame(main_frame)
                        frame.grid(row=1, column=j+1, rowspan=2, sticky="nsew", padx=5, pady=5)
                        self.create_time_widgets(frame, day, "전체")             
                else :     
                    frame = ttk.Frame(main_frame)
                    frame.grid(row=i+1, column=j+1, sticky="nsew", padx=5, pady=5)
                    self.create_time_widgets(frame, day, time)

        # 하단 여백을 위한 빈 프레임과 초기화 버튼
        bottom_frame = ttk.Frame(main_frame, height=20)
        bottom_frame.grid(row=len(times)+1, column=0, columnspan=len(days)+1, sticky="ew")
        bottom_frame.grid_propagate(False)  # 높이 고정
        
        if self.config.get('show_reset_button', True):
        # 초기화 버튼 추가
            reset_button = ttk.Button(
                bottom_frame, 
                text="초기화", 
                command=self.reset_todos_check,
                width=10
            )
            reset_button.pack(side="right", padx=5)

        # Grid 레이아웃 설정
        for i in range(1, len(days) + 1):
            main_frame.columnconfigure(i, weight=1)
        for i in range(1, len(times) + 1):
            main_frame.rowconfigure(i, weight=1)

    def create_time_widgets(self, frame, day, time):
        # 리스트 박스와 스크롤바를 담을 프레임 생성
        list_frame = ttk.Frame(frame)
        list_frame.pack(fill="both", expand=True)
        
        # Todo 항목을 표시할 리스트 박스
        listbox = tk.Listbox(
            list_frame, 
            width=20,  # 초기 너비 설정
            height=5, 
            font=("Helvetica", 12),
            borderwidth=0, 
            highlightthickness=0, 
            selectmode='single'
        )
        listbox.pack(pady=0, padx=0, fill="both", expand=True)

        # 텍스트 너비에 따른 리스트박스 크기 조정 함수
        def adjust_width(event=None):
            self.adjust_listbox_width(listbox, day, time)
        
        # 초기 너비 조정
        adjust_width()
        
        # 항목 추가/수정 시 너비 자동 조정을 위한 바인딩
        listbox.bind('<<ListboxSelect>>', adjust_width)
        
        # 리스트 박스에 고유한 이름 부여
        listbox_name = f"{day}_{time}_listbox"
        listbox.name = listbox_name
     
        # 각 리스트 박스에 대한 이벤트 바인딩
        listbox.bind("<Double-Button-1>", lambda event, d=day, t=time, lb=listbox: self.handle_double_click(event, d, t, lb))
        listbox.bind("<Button-1>", lambda event, d=day, t=time, lb=listbox: self.handle_single_click(event, d, t, lb))
        listbox.bind("<Button-3>", lambda event, d=day, t=time, lb=listbox: self.delete_item(event, d, t, lb))  # 우클릭 이벤트 추가
        listbox.bind("<MouseWheel>", lambda event: self.scroll_listbox(event, listbox))
        listbox.bind("<Double-Button-3>", lambda event, d=day, t=time, lb=listbox: self.add_new_item(d, t, lb))      
       
        self.todo_widgets[(day, time)] = listbox
        self.load_items(day, time, listbox)

    def load_items(self, day, time, listbox):
        """Todo 항목을 리스트 박스에 로드합니다."""
        items = self.todo_items[day][time]
        for item in items:
            if item['completed']:
                # 취소선이 있는 텍스트 생성
                strike_text = '\u0336'.join(item['text']) + '\u0336'
                listbox.insert(tk.END, strike_text)
                listbox.itemconfig(listbox.size()-1, fg="grey")
            else:
                # 일반 텍스트
                listbox.insert(tk.END, item['text'])
        self.adjust_listbox_width(listbox, day, time)
     
     
    def clear_all_selections(self):
        """모든 리스트박스의 선택을 해제합니다."""
        for listbox in self.todo_widgets.values():
            listbox.selection_clear(0, tk.END) 
    
    def toggle_completion(self, event, day, time, listbox):
        """Todo 항목 클릭 시 색 변경"""
        current_time = event.time
        # 300ms 이내의 클릭은 더블클릭으로 간주하여 무시
        if current_time - self.last_click_time < 300:
            return
        self.last_click_time = current_time
        
        # 클릭한 위치의 항목 인덱스를 가져옵니다
        index = listbox.nearest(event.y)
        
        # 클릭한 위치가 실제 항목 영역인지 확인
        bbox = listbox.bbox(index)
        if bbox is None or event.y > bbox[1] + bbox[3]:  # bbox[1]은 y좌표, bbox[3]은 높이
            # 빈 영역 클릭 시 새 항목 추가
            self.add_new_item(day, time, listbox)
            return

        # 항목이 없는 경우 새 항목 추가
        if not (0 <= index < listbox.size()):
            self.add_new_item(day, time, listbox)
            return

        item = self.todo_items[day][time][index]
        item['completed'] = not item['completed']

        # 현재 텍스트 가져오기
        current_text = item['text']
        
        if item['completed']:
            # 취소선 추가 (유니코드 취소선 문자 사용)
            strike_text = '\u0336'.join(current_text) + '\u0336'
            listbox.delete(index)
            listbox.insert(index, strike_text)
            listbox.itemconfig(index, fg="grey")
            utils.log_completion(day, time, current_text)
        else:
            # 취소선 제거
            listbox.delete(index)
            listbox.insert(index, current_text)
            listbox.itemconfig(index, fg="black")
        
        utils.save_config(self.config)
    
    def edit_item(self, event, day, time, listbox):
        """Todo 항목 수정"""
        self.last_click_time = event.time  # 더블클릭 시간 저장
        
        index = listbox.nearest(event.y)

        # 예외 처리: 리스트에 항목이 없는 경우
        if not (0 <= index < listbox.size()):
            return

        item = self.todo_items[day][time][index]
        
        # 텍스트 입력 다이얼로그 표시
        new_text = simpledialog.askstring("Edit Item", "Enter new text", initialvalue=item['text'])
        if new_text:
            item['text'] = new_text
            listbox.delete(index)
            listbox.insert(index, new_text)
            
            # 너비 재조정
            self.adjust_listbox_width(listbox, day, time)
            
            utils.save_config(self.config)

    def add_new_item(self, day, time, listbox):
        """새로운 Todo 항목 추가"""
        new_text = simpledialog.askstring("Add Item", "Enter new item")
        if new_text:
            # 처음 추가하는 경우에도 동작하도록 구조 확인 및 초기화
            if not self.todo_items.get(day):
                self.todo_items[day] = {}
            if not self.todo_items[day].get(time):
                self.todo_items[day][time] = []
     
            # 새 항목 추가    
            self.todo_items[day][time].append({"text": new_text, "completed": False})
            listbox.insert(tk.END, new_text)
            utils.save_config(self.config)
 
    def scroll_listbox(self, event, listbox):
        """마우스 휠 스크롤"""
        listbox.yview_scroll(int(-1*(event.delta/120)), "units")

    def delete_item(self, event, day, time, listbox):
        """Todo 항목 삭제"""
        # 클릭한 위치의 항목 인덱스를 가져옵니다
        index = listbox.nearest(event.y)
        
        # 클릭한 위치가 실제 항목 영역인지 확인
        bbox = listbox.bbox(index)
        if bbox is None or event.y > bbox[1] + bbox[3]:  # bbox[1]은 y좌표, bbox[3]은 높이
            return

        # 항목이 없는 경우 return
        if not (0 <= index < listbox.size()):
            return

        # 삭제 확인 메시지
        item = self.todo_items[day][time][index]
        if messagebox.askyesno("삭제 확인", f"'{item['text']}' 항목을 삭제하시겠습니까?"):
            # 항목 삭제
            del self.todo_items[day][time][index]
            listbox.delete(index)
            
            # 너비 재조정
            self.adjust_listbox_width(listbox, day, time)
            
            utils.save_config(self.config)

    def check_weekly_reset(self):
        """매주 월요일에 Todo 항목을 초기화합니다."""
        utils.check_and_reset_todos()
        self.update_list_box()

    def reset_todos_check(self):
        """Todo 항목을 초기화합니다."""
        if messagebox.askyesno("초기화 확인", "모든 Todo 항목을 초기화하시겠습니까?"):
            utils.reset_weekly_todos()
            self.update_list_box()

    def update_list_box(self):
        self.config = utils.load_config()
        self.todo_items = self.config['todos']     
        # 모든 리스트 박스 업데이트
        for (day, time), listbox in self.todo_widgets.items():
            listbox.delete(0, tk.END)
            self.load_items(day, time, listbox)
     
    def schedule_weekly_reset(self):
        """주기적으로 weekly_reset을 체크합니다."""
        self.check_weekly_reset()
        # 8시간 후에 다시 실행
        self.root.after(3600000*8, self.schedule_weekly_reset)        

    def adjust_listbox_width(self, listbox, day, time):
        """리스트박스의 너비를 내용에 맞게 조정합니다."""
        items = self.todo_items[day][time]
        min_width = 20  # 최소 너비
        padding = 2     # 여유 공간

        if not items:  # 항목이 없으면 최소 너비 설정
            listbox.configure(width=min_width)
            return

        # 리스트박스의 폰트 정보를 가져옴
        font = tkinter.font.Font(font=listbox['font'])
        
        # 한글 기준 문자 너비 (캐싱)
        base_width = font.measure('가')
        
        # 가장 긴 텍스트의 너비 계산
        max_char_width = min_width
        for item in items:
            text = item['text']
            # 전체 텍스트의 픽셀 너비를 한 번에 계산
            text_width = font.measure(text)
            # 문자 단위로 변환
            char_width = int(text_width / base_width)
            max_char_width = max(max_char_width, char_width)

        # 최종 너비 설정
        listbox.configure(width=max_char_width + padding)
        
        
    def handle_double_click(self, event, day, time, listbox):
        """더블클릭 이벤트 처리"""
        if self.click_timer:
            self.root.after_cancel(self.click_timer)
            self.click_timer = None
        self.editing = True
        self.edit_item(event, day, time, listbox)
        self.editing = False

    def handle_single_click(self, event, day, time, listbox):
        """단일 클릭 이벤트 처리"""
        if self.click_timer:
            self.root.after_cancel(self.click_timer)
        # 300ms 후에 toggle_completion 실행
        self.click_timer = self.root.after(300, lambda: self.delayed_toggle(event, day, time, listbox))

    def delayed_toggle(self, event, day, time, listbox):
        """지연된 토글 처리"""
        if not self.editing:  # 편집 중이 아닐 때만 토글
            self.toggle_completion(event, day, time, listbox)
        self.click_timer = None

if __name__ == "__main__":
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()