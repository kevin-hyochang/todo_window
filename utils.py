import json
import datetime
import logging
import os

CONFIG_FILE = 'config.json'

now = datetime.datetime.now()

LOG_FILE = os.path.join('logs', f'logs_{now.year}_{now.month:02d}.log')

# 로그 디렉토리 생성
if not os.path.exists('logs'):
    os.makedirs('logs')

# 로깅 설정
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    encoding='utf-8')  # 파일 인코딩 추가

def load_config():
    """config.json 파일에서 Todo 항목을 로드합니다."""
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
            return config
    except FileNotFoundError or json.JSONDecodeError:
        # config.json 파일이 없거나 오류가 발생하는 경우 초기화
        default_config = {
            "days": ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일"],  # 요일 목록
            "times": ["오전", "오후"],  # 시간대 목록
            "todos": {},  # 할 일 목록
            "last_reset_date": str(datetime.date.today()),
            "show_reset_button": True
        }
        
        default_config["todos"] = {
            day: {time: [] for time in default_config["times"]}
            for day in default_config["days"]
        }
        
        # 토요일 추가 (오전/오후 구분 없이)
        default_config["todos"]["토요일"] = {"전체": []}        
        
        save_config(default_config)  # config.json 파일 생성
        return default_config

def save_config(config):
    """Todo 항목을 config.json 파일에 저장합니다."""
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

def log_completion(day, time, task):
    """Todo 항목 완료 로그를 기록합니다."""
    logging.info(f"{day} {time}: {task} 완료")

def reset_weekly_todos():
    """모든 Todo 항목의 확인 표시를 제거합니다."""
    config = load_config()
    for day in config['todos']:
        for time in config['todos'][day]:
            for task in config['todos'][day][time]:
                task['completed'] = False
    config['last_reset_date'] = str(datetime.date.today())
    save_config(config)

def check_and_reset_todos():
    """ last_modified_date가 지난주인 경우 Todo 항목을 초기화합니다."""
    config = load_config()
        
    today = datetime.date.today()
    last_reset_date = datetime.datetime.strptime(config['last_reset_date'], '%Y-%m-%d').date()

    # 오늘이 월요일이거나, 마지막 초기화 날짜가 이번 주 이전이거나, 파일 수정일이 지난주인 경우 초기화
    if last_reset_date < today - datetime.timedelta(days=today.weekday()) :
        reset_weekly_todos()