# todo_window

## 기술 스택
### python, windows

## 요구사항
### python 기반 윈도우 앱
### 월화수목금, 오전/오후 별 todo 리스트 관리 필요.
### todo 항목을 한번 클릭하면 배경색이 바뀌면서 취소선이 그여져 완료 표시.
### todo 항목을 한번 더 클릭하면 다시 배경색이 돌아오고 취소선이 없어짐.
### 반복되는 업무기 때문에 last_reset_date가 지난주인 경우 completed는 false로 바뀐다.
### todo 항목을 클릭했을 때, 완료가 된 로그를 저장한다.
### 리스트 맨 아래 부분을 클릭하여 새로운 항목을 추가 할 수 있어야 한다.
### todo 항목은 ./ 경로에 config.json형식으로 관리된다.
### 로그는 ./logs 경로에 월별로 로그가 쌓인다.
### 토요일 활성화/비활성화 기능 추가
### 초기화 버튼 클릭 기능 추가

## TODO
### 월/분기/반기/년 별로 루틴되는 업무를 추가하고 관리하는 기능 추가.

## dependencies
### pip install tk
### pip install pyinstaller
### pip install win10toast

#### pyinstaller --onefile --noconsole --add-data "todo.ico;." --icon todo.ico --name WeeklyTodo main.py


## 테스트 수행
### python -m unittest test_integration.py