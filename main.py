import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import utils
import os
import sys

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
        self.todo_widgets = {}

        self.create_widgets()
        self.check_weekly_reset()
        # 8시간마다 check_weekly_reset 실행
        self.schedule_weekly_reset()
        
    def create_widgets(self):
        # days = ["월요일", "화요일", "수요일", "목요일", "금요일"]
        # times = ["오전", "오후"]
        days = self.config.get('days')
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
            day_label = ttk.Label(header_frame, text=day, anchor="center")
            day_label.grid(row=0, column=i, sticky="nsew", padx=5)
            day_label.bind("<Button-1>", lambda e: self.clear_all_selections())
            header_frame.columnconfigure(i, weight=1)

        # 오전/오후 헤더를 위한 프레임 생성 (너비 고정)
        time_frame = ttk.Frame(main_frame, width=40)
        time_frame.grid(row=1, column=0, rowspan=len(times), sticky="ns")
        time_frame.grid_propagate(False)  # 너비 고정

        # 오전/오후 헤더 생성
        for i, time in enumerate(times):
            time_label = ttk.Label(time_frame, text=time, anchor="center")
            time_label.grid(row=i, column=0, sticky="nsew", pady=5)
            time_label.configure(justify="center")  # 텍스트 중앙 정렬
            time_frame.rowconfigure(i, weight=1)
            time_frame.columnconfigure(0, weight=1)  # 열도 가중치 설정하여 중앙 정렬 보장

        # Todo 리스트 생성
        for i, time in enumerate(times):
            for j, day in enumerate(days):
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
        listbox = tk.Listbox(list_frame, width=20, height=5, font=("Helvetica", 12),
                             borderwidth=0, highlightthickness=0,  selectmode='single')  # 테두리 제거
        listbox.pack(pady=0, padx=0, fill="both", expand=True)  # 패딩 및 여백 제거
        
        # 리스트 박스에 고유한 이름 부여
        listbox_name = f"{day}_{time}_listbox"
        listbox.name = listbox_name
                
        # 각 리스트 박스에 대한 toggle_completion 함수를 개별적으로 바인딩
        listbox.bind("<Button-1>", lambda event, d=day, t=time, lb=listbox: self.toggle_completion(event, d, t, lb))
        listbox.bind("<Double-Button-1>", lambda event, d=day, t=time, lb=listbox: self.edit_item(event, d, t, lb))
        listbox.bind("<MouseWheel>", lambda event: self.scroll_listbox(event, listbox))
        listbox.bind("<Double-Button-3>", lambda event, d=day, t=time, lb=listbox: self.add_new_item(d, t, lb))      
       
        self.todo_widgets[(day, time)] = listbox
        self.load_items(day, time, listbox)

    def load_items(self, day, time, listbox):
        """Todo 항목을 리스트 박스에 로드합니다."""
        items = self.todo_items[day][time]
        for item in items:
            listbox.insert(tk.END, item['text'])
            if item['completed']:
                listbox.itemconfig(listbox.size()-1, fg="grey")
                
    def clear_all_selections(self):
        """모든 리스트박스의 선택을 해제합니다."""
        for listbox in self.todo_widgets.values():
            listbox.selection_clear(0, tk.END) 
    
    def toggle_completion(self, event, day, time, listbox):
        """Todo 항목 클릭 시 색 변경"""
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
        
        if item['completed']:
            listbox.itemconfig(index, fg="grey")
            utils.log_completion(day, time, item['text'])
        else:
            listbox.itemconfig(index, fg="black")
        
        utils.save_config(self.config)
    
    def edit_item(self, event, day, time, listbox):
        """Todo 항목 수정"""
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

    def check_weekly_reset(self):
        """매주 월요일에 Todo 항목을 초기화합니다."""
        utils.check_and_reset_todos()
        self.update_list_box()

    def reset_todos_check(self):
        """Todo 항목을 초기화합니다."""
        if messagebox.askyesno("초기화 확인", "모든 Todo 항목을 초기화하시겠습니까?"):
            utils.reset_weekly_todos()           

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
        # self.root.after(3600000*8, self.schedule_weekly_reset)
        self.root.after(1000, self.schedule_weekly_reset)
        

if __name__ == "__main__":
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()