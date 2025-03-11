import unittest
from tkinter import Tk
from main import TodoApp
from datetime import datetime
import utils
import json
import os

class TestTodoAppIntegration(unittest.TestCase):
    def setUp(self):
        """테스트 환경 설정"""
        # 원본 config.json 파일 백업
        self.original_config_file = "config.json"
        self.test_config_file = "config_test.json"
        
        # 테스트용 초기 설정 생성
        days = ["월요일", "화요일", "수요일", "목요일", "금요일"]
        times = ["오전", "오후"]
        
        # todos 딕셔너리 초기화
        todos = {}
        for day in days:
            todos[day] = {}
            for time in times:
                todos[day][time] = []
        
        test_initial_config = {
            "days": days,
            "times": times,
            "todos": todos,
            "show_saturday": False,
            "work_end_time": "18:00",
            "show_reset_button": True,
            "last_reset_date": str(datetime.now().date())
        }
        
        # 테스트용 설정 파일 생성
        with open(self.test_config_file, 'w', encoding='utf-8') as test_f:
            json.dump(test_initial_config, test_f, ensure_ascii=False, indent=4)
        
        # utils의 CONFIG_FILE 경로를 테스트용으로 변경
        utils.CONFIG_FILE = self.test_config_file
        
        self.root = Tk()
        self.app = TodoApp(self.root)
        self.app._test_mode = True
        
    def tearDown(self):
        """테스트 환경 정리"""
        self.root.destroy()
        
        # 테스트용 config 파일 삭제
        if os.path.exists(self.test_config_file):
            os.remove(self.test_config_file)
        
        # utils의 CONFIG_FILE 경로를 원래대로 복원
        utils.CONFIG_FILE = self.original_config_file

    def test_initial_setup(self):
        """초기 설정 테스트"""
        self.assertIsNotNone(self.app.config)
        self.assertIsNotNone(self.app.todo_items)
        self.assertEqual(self.app.config.get('work_end_time', '18:00'), '18:00')
        self.assertFalse(self.app.config.get('show_saturday', True))

    def test_work_end_time_setting(self):
        """업무 종료 시간 설정 테스트"""
        self.app.config['work_end_time'] = '17:00'
        utils.save_config(self.app.config)
        end_time = self.app.get_work_end_time()
        self.assertEqual(end_time.hour, 17)
        self.assertEqual(end_time.minute, 0)

    def test_todo_items_manipulation(self):
        """Todo 항목 조작 테스트"""
        # 기존 항목 초기화
        day = "월요일"
        time = "오전"
        self.app.todo_items[day] = {}
        self.app.todo_items[day][time] = []
        
        # 새 항목 추가
        new_item = {"text": "테스트 항목", "completed": False}
        self.app.todo_items[day][time].append(new_item)
        utils.save_config(self.app.config)  # 설정 저장
        
        # 항목 확인
        self.assertEqual(len(self.app.todo_items[day][time]), 1)
        self.assertEqual(self.app.todo_items[day][time][0]["text"], "테스트 항목")

    def test_saturday_toggle(self):
        """토요일 표시 설정 테스트"""
        initial_state = self.app.config.get('show_saturday', False)
        self.app.toggle_saturday()
        self.assertNotEqual(initial_state, self.app.config.get('show_saturday'))

    def test_incomplete_tasks_check(self):
        """미완료 항목 체크 테스트"""
        # 테스트용 미완료 항목 추가
        today = ["월요일", "화요일", "수요일", "목요일", "금요일"][datetime.now().weekday()]
        self.app.todo_items[today] = {"오전": [{"text": "테스트 항목", "completed": False}]}
        
        # 미완료 항목 체크
        try:
            self.app.check_incomplete_tasks()
            self.assertTrue(True)  # 예외가 발생하지 않으면 성공
        except Exception as e:
            self.fail(f"예상치 못한 예외 발생: {str(e)}")

    def test_config_persistence(self):
        """설정 저장 및 로드 테스트"""
        test_config = {
            "work_end_time": "17:30",
            "show_saturday": True,
            "show_reset_button": False
        }
        
        # 설정 저장
        utils.save_config(test_config)
        
        # 설정 로드
        loaded_config = utils.load_config()
        self.assertEqual(loaded_config.get("work_end_time"), "17:30")
        self.assertTrue(loaded_config.get("show_saturday"))
        self.assertFalse(loaded_config.get("show_reset_button"))

if __name__ == '__main__':
    unittest.main()