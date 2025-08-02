from flask import Flask, render_template, request, jsonify, send_from_directory
import random
import os
import uuid
import string
import time
# from pyngrok import ngrok  # Vercel 배포시 제거

app = Flask(__name__)

# 더 간단한 정적 파일 서빙
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

# 추가 정적 파일 라우트 (Vercel 호환성)
@app.route('/static/images/<path:filename>')
def static_images(filename):
    """이미지 파일 서빙"""
    try:
        return send_from_directory('static/images', filename)
    except Exception as e:
        print(f"이미지 파일 서빙 오류: {e}")
        return f"이미지를 찾을 수 없습니다: {filename}", 404

# 카테고리별 단어 목록
CATEGORIES = {
    "fruit": [
        ("apple", "사과"),
        ("peach", "복숭아"),
        ("lemon", "레몬"),
        ("cherry", "체리"),
        ("pineapple", "파인애플"),
        ("banana", "바나나"),
        ("orange", "오렌지"),
        ("grape", "포도"),
        ("strawberry", "딸기"),
        ("watermelon", "수박")
    ],
    "weather": [
        ("sunny", "맑은, 화창한"),
        ("rainy", "비 오는"),
        ("cloudy", "흐린"),
        ("windy", "바람이 부는"),
        ("snowy", "눈 오는"),
        ("hot", "덥다"),
        ("cold", "춥다"),
        ("warm", "따뜻한"),
        ("cool", "시원한"),
        ("stormy", "폭풍우가 치는")
    ],
    "food": [
        ("rice", "밥, 쌀"),
        ("bread", "빵"),
        ("milk", "우유"),
        ("egg", "달걀"),
        ("chicken", "닭고기"),
        ("apple", "사과"),
        ("banana", "바나나"),
        ("soup", "수프, 국"),
        ("salad", "샐러드"),
        ("fish", "생선")
    ],
    "country": [
        ("Korea", "한국"),
        ("USA", "미국"),
        ("China", "중국"),
        ("Japan", "일본"),
        ("England", "영국"),
        ("France", "프랑스"),
        ("Canada", "캐나다"),
        ("Australia", "호주"),
        ("Germany", "독일"),
        ("India", "인도")
    ],
    "number": [
        ("one", "1"),
        ("two", "2"),
        ("three", "3"),
        ("four", "4"),
        ("five", "5"),
        ("six", "6"),
        ("seven", "7"),
        ("eight", "8"),
        ("nine", "9"),
        ("ten", "10")
    ],
    "school": [
        ("pencil", "연필"),
        ("eraser", "지우개"),
        ("ruler", "자"),
        ("notebook", "공책"),
        ("book", "책"),
        ("pen", "펜"),
        ("marker", "마커, 사인펜"),
        ("scissors", "가위"),
        ("glue", "풀"),
        ("bag", "가방")
    ]
}

# 교사가 생성한 방 정보 저장
teacher_rooms = {}

# 게임 상태 저장소
game_states = {}

# 사용된 단어 추적 (세션별)
used_words = {}

def generate_room_code():
    """6자리 방코드 생성"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def detect_word_category(word, meaning):
    """단어와 뜻을 보고 어떤 카테고리에 속하는지 감지"""
    for cat_name, words in CATEGORIES.items():
        for w, m in words:
            if w.lower() == word.lower() or m == meaning:
                return cat_name
    # 감지되지 않으면 기본값으로 fruit 반환
    return 'fruit'

def get_random_word(category="fruit", custom_words=None):
    """사용되지 않은 랜덤 단어 선택"""
    global used_words
    
    if custom_words:
        # 교사가 입력한 커스텀 단어들 사용
        available_words = [(word, meaning) for word, meaning in custom_words 
                          if word not in used_words.get('default', set())]
    else:
        # 카테고리별 기본 단어들 사용
        words = CATEGORIES.get(category, CATEGORIES["fruit"])
        available_words = [(word, meaning) for word, meaning in words 
                          if word not in used_words.get('default', set())]
    
    if not available_words:
        # 모든 단어를 사용했으면 초기화
        used_words['default'] = set()
        if custom_words:
            available_words = custom_words
        else:
            available_words = CATEGORIES.get(category, CATEGORIES["fruit"])
    
    # 랜덤 선택
    word, meaning = random.choice(available_words)
    
    # 사용된 단어로 표시
    if 'default' not in used_words:
        used_words['default'] = set()
    used_words['default'].add(word)
    
    # 실제 카테고리 감지 (커스텀 단어의 경우)
    if custom_words:
        actual_category = detect_word_category(word, meaning)
    else:
        actual_category = category
    
    return word, meaning, actual_category

MAX_ATTEMPTS = 4  # 다리 4단계
BRIDGE_LENGTH = 10

@app.route('/')
def index():
    """메인 페이지"""
    return render_template('index.html')

@app.route('/get_categories')
def get_categories():
    """카테고리 목록 반환"""
    return jsonify({
        'categories': list(CATEGORIES.keys()),
        'category_names': {
            'fruit': '과일',
            'weather': '날씨',
            'food': '음식',
            'country': '나라',
            'number': '숫자',
            'school': '학용품'
        }
    })

@app.route('/create_room', methods=['POST'])
def create_room():
    """교사용 방 생성"""
    print("방 생성 요청 받음")  # 디버깅 로그
    data = request.json
    print(f"받은 데이터: {data}")  # 디버깅 로그
    custom_words = data.get('words', [])
    print(f"커스텀 단어: {custom_words}")  # 디버깅 로그
    
    if not custom_words:
        print("단어가 없음")  # 디버깅 로그
        return jsonify({'error': '단어를 입력해주세요.'})
    
    # 방코드 생성
    room_code = generate_room_code()
    while room_code in teacher_rooms:
        room_code = generate_room_code()
    
    print(f"생성된 방코드: {room_code}")  # 디버깅 로그
    
    # 방 정보 저장
    teacher_rooms[room_code] = {
        'words': custom_words,
        'created_at': time.time()
    }
    
    print(f"저장된 방 정보: {teacher_rooms[room_code]}")  # 디버깅 로그
    
    return jsonify({
        'success': True,
        'room_code': room_code,
        'message': f'방이 생성되었습니다. 방코드: {room_code}'
    })

@app.route('/join_room', methods=['POST'])
def join_room():
    """방코드로 방 참여"""
    data = request.json
    room_code = data.get('room_code', '').upper()
    
    if room_code not in teacher_rooms:
        return jsonify({'error': '존재하지 않는 방코드입니다.'})
    
    return jsonify({
        'success': True,
        'message': '방에 참여했습니다.',
        'room_code': room_code
    })

@app.route('/start_game', methods=['POST'])
def start_game():
    """새 게임 시작"""
    data = request.json
    game_id = data.get('game_id', 'default')
    category = data.get('category', 'fruit')
    room_code = data.get('room_code', None)
    reset_score = data.get('reset_score', False)
    
    # 커스텀 단어 사용 여부 확인
    custom_words = None
    if room_code and room_code in teacher_rooms:
        custom_words = teacher_rooms[room_code]['words']
    
    # 랜덤 단어 선택
    word, meaning, actual_category = get_random_word(category, custom_words)
    
    # 기존 게임 상태가 있으면 점수와 문제 번호를 유지
    if game_id in game_states and not reset_score:
        existing_state = game_states[game_id]
        current_score = existing_state['score']
        current_question_num = existing_state['current_question_num']
    else:
        current_score = 0
        current_question_num = 1
    
    # 총 문제 수 계산
    if custom_words:
        total_questions = len(custom_words)
    else:
        total_questions = len(CATEGORIES.get(category, CATEGORIES["fruit"]))
    
    game_states[game_id] = {
        'word': word,
        'meaning': meaning,
        'attempts_left': MAX_ATTEMPTS,
        'guessed_letters': set(),
        'wrong_attempts': 0,
        'score': current_score,
        'round_num': 1,
        'total_questions': total_questions,
        'current_question_num': current_question_num,
        'category': actual_category,
        'room_code': room_code,
        'hint_count': 2  # 각 단어당 힌트 2번
    }
    
    return jsonify({
        'success': True,
        'game_state': get_game_state(game_id)
    })

@app.route('/start_new_word', methods=['POST'])
def start_new_word():
    """새로운 단어 시작 (힌트 카운트 리셋)"""
    data = request.json
    game_id = data.get('game_id', 'default')
    category = data.get('category', 'fruit')
    room_code = data.get('room_code', None)
    
    print(f"start_new_word 호출됨 - game_id: {game_id}, category: {category}, room_code: {room_code}")
    
    # 커스텀 단어 사용 여부 확인
    custom_words = None
    if room_code and room_code in teacher_rooms:
        custom_words = teacher_rooms[room_code]['words']
    
    # 랜덤 단어 선택
    word, meaning, actual_category = get_random_word(category, custom_words)
    
    # 기존 게임 상태에서 점수와 문제 번호 유지
    if game_id in game_states:
        existing_state = game_states[game_id]
        current_score = existing_state['score']
        current_question_num = existing_state['current_question_num']
    else:
        current_score = 0
        current_question_num = 1
    
    # 총 문제 수 계산
    if custom_words:
        total_questions = len(custom_words)
    else:
        total_questions = len(CATEGORIES.get(category, CATEGORIES["fruit"]))
    
    game_states[game_id] = {
        'word': word,
        'meaning': meaning,
        'attempts_left': MAX_ATTEMPTS,
        'guessed_letters': set(),
        'wrong_attempts': 0,
        'score': current_score,
        'round_num': 1,
        'total_questions': total_questions,
        'current_question_num': current_question_num,
        'category': actual_category,
        'room_code': room_code,
        'hint_count': 2  # 새로운 단어마다 힌트 2번 리셋
    }
    
    print(f"새 단어 설정 완료 - word: {word}, hint_count: {game_states[game_id]['hint_count']}")
    
    return jsonify({
        'success': True,
        'game_state': get_game_state(game_id)
    })

@app.route('/use_hint', methods=['POST'])
def use_hint():
    """힌트 사용"""
    data = request.json
    game_id = data.get('game_id', 'default')
    
    if game_id not in game_states:
        return jsonify({'error': '게임을 먼저 시작해주세요.'})
    
    game_state = game_states[game_id]
    
    # 힌트 사용 가능 여부 확인
    if game_state['hint_count'] <= 0:
        return jsonify({'error': '이 단어에 대한 힌트를 모두 사용했습니다.'})
    
    word = game_state['word']
    guessed_letters = game_state['guessed_letters']
    
    # 가장 많이 나오는 알파벳 찾기 (이미 추측한 것 제외)
    letter_count = {}
    for letter in word.lower():
        if letter.isalpha() and letter.upper() not in guessed_letters:
            letter_count[letter] = letter_count.get(letter, 0) + 1
    
    if not letter_count:
        return jsonify({'error': '더 이상 힌트를 제공할 수 없습니다.'})
    
    # 가장 많이 나오는 알파벳 선택
    most_common_letter = max(letter_count.items(), key=lambda x: x[1])[0].upper()
    
    # 힌트로 제공된 글자를 guessed_letters에 추가
    game_state['guessed_letters'].add(most_common_letter)
    game_state['hint_count'] -= 1  # 힌트 사용 횟수 감소
    
    return jsonify({
        'success': True,
        'hint': most_common_letter,
        'hint_count': game_state['hint_count'],
        'game_state': get_game_state(game_id)
    })

@app.route('/process_input', methods=['POST'])
def process_input():
    """사용자 입력 처리"""
    data = request.json
    game_id = data.get('game_id', 'default')
    user_input = data.get('input', '').lower().strip()
    
    if game_id not in game_states:
        return jsonify({'error': '게임을 먼저 시작해주세요.'})
    
    game_state = game_states[game_id]
    
    if not user_input:
        return jsonify({'error': '입력을 해주세요.'})
    
    # 전체 단어 추측
    if len(user_input) > 1:
        if user_input.isalpha():
            if check_full_word_guess(game_state['word'], user_input):
                return jsonify({
                    'success': True,
                    'message': f"🎉 정답입니다! '{game_state['word']}'를 맞혔습니다!",
                    'word_complete': True,
                    'game_state': get_game_state(game_id)
                })
            else:
                game_state['wrong_attempts'] += 1
                game_state['attempts_left'] -= 1
                return jsonify({
                    'success': True,
                    'message': f"❌ '{user_input}'는 정답이 아닙니다.",
                    'game_state': get_game_state(game_id)
                })
        else:
            return jsonify({'error': '단어는 알파벳만 입력하세요.'})
    else:
        # 단일 알파벳 추측
        if not user_input.isalpha():
            return jsonify({'error': '알파벳만 입력하세요.'})
        
        if user_input in game_state['guessed_letters']:
            return jsonify({'error': '이미 시도한 알파벳입니다.'})
        
        game_state['guessed_letters'].add(user_input)
        
        # 대소문자 구분 없이 확인
        if user_input.lower() in game_state['word'].lower():
            message = f"✅ '{user_input}'가 단어에 있습니다!"
        else:
            message = f"❌ '{user_input}'는 단어에 없습니다."
            game_state['wrong_attempts'] += 1
            game_state['attempts_left'] -= 1
        
        # 게임 상태 확인
        if game_state['attempts_left'] <= 0:
            return jsonify({
                'success': True,
                'message': f"💀 게임 오버! 정답은 '{game_state['word']}'였습니다.",
                'game_over': True,
                'game_state': get_game_state(game_id)
            })
        elif check_word_complete(game_state['word'], game_state['guessed_letters']):
            return jsonify({
                'success': True,
                'message': "🎉 단어를 완성했습니다!",
                'word_complete': True,
                'game_state': get_game_state(game_id)
            })
        else:
            return jsonify({
                'success': True,
                'message': message,
                'game_state': get_game_state(game_id)
            })

@app.route('/check_quiz', methods=['POST'])
def check_quiz():
    """퀴즈 답안 확인"""
    data = request.json
    game_id = data.get('game_id', 'default')
    answer = data.get('answer', '')
    
    if game_id not in game_states:
        return jsonify({'error': '게임을 먼저 시작해주세요.'})
    
    game_state = game_states[game_id]
    
    if answer == game_state['meaning']:
        # 정답인 경우에만 1점 추가
        game_state['score'] += 1
        message = "🎊 정답입니다! 보물을 획득했습니다! +1점"
    else:
        # 틀린 경우 점수 추가 없음
        message = f"❌ 틀렸습니다. 정답은 '{game_state['meaning']}'입니다."
    
    # 다음 문제로 진행
    game_state['current_question_num'] += 1
    
    # 모든 문제가 끝났는지 확인
    if game_state['current_question_num'] > game_state['total_questions']:
        return jsonify({
            'success': True,
            'message': message,
            'correct': answer == game_state['meaning'],
            'score': game_state['score'],
            'game_complete': True,
            'final_score': game_state['score'],
            'completion_message': f"🎉 모든 문제를 완료했습니다! 최종 점수: {game_state['score']}점"
        })
    else:
        return jsonify({
            'success': True,
            'message': message,
            'correct': answer == game_state['meaning'],
            'score': game_state['score'],
            'next_question': True
        })

@app.route('/get_category_meanings', methods=['GET'])
def get_category_meanings():
    """카테고리별 뜻 목록 반환"""
    category = request.args.get('category', 'fruit')
    
    if category in CATEGORIES:
        # 해당 카테고리의 모든 뜻들을 반환
        meanings = [meaning for word, meaning in CATEGORIES[category]]
        return jsonify({
            'success': True,
            'meanings': meanings
        })
    else:
        # 기본값으로 과일 카테고리 반환
        meanings = [meaning for word, meaning in CATEGORIES['fruit']]
        return jsonify({
            'success': True,
            'meanings': meanings
        })

@app.route('/end_game', methods=['POST'])
def end_game():
    """게임 종료"""
    data = request.json
    game_id = data.get('game_id', 'default')
    
    if game_id not in game_states:
        return jsonify({'error': '게임을 먼저 시작해주세요.'})
    
    game_state = game_states[game_id]
    final_score = game_state['score']
    
    # 게임 상태 삭제
    del game_states[game_id]
    
    return jsonify({
        'success': True,
        'message': f"게임이 종료되었습니다. 최종점수는 {final_score}점 입니다.",
        'final_score': final_score
    })

def check_word_complete(word, guessed_letters):
    """단어가 완성되었는지 확인"""
    # 대소문자 구분 없이 확인
    word_lower = word.lower()
    guessed_lower = {letter.lower() for letter in guessed_letters}
    return all(letter in guessed_lower for letter in word_lower)

def check_full_word_guess(word, full_word_guess):
    """전체 단어 추측이 정답인지 확인"""
    return word.lower() == full_word_guess.lower()

def get_game_state(game_id):
    """게임 상태를 반환"""
    if game_id not in game_states:
        return None
    
    game_state = game_states[game_id]
    word_length = len(game_state['word'])
    
    # 단어 표시 생성
    display_word = ""
    correct_letters_count = 0  # 맞춘 알파벳 개수
    for letter in game_state['word']:
        # 대소문자 구분 없이 확인
        if letter.lower() in {g.lower() for g in game_state['guessed_letters']}:
            display_word += letter.upper() + " "
            correct_letters_count += 1
        else:
            display_word += "_ "
    
    # 캐릭터 위치 계산 - 단어 길이에 따라 조정
    # 단어 길이만큼 이동하면 보물에 도달
    character_pos = min(correct_letters_count, word_length)
    treasure_pos = word_length  # 보물은 단어 길이 위치에
    
    # 다리 상태 생성
    bridge_display = []
    for i in range(BRIDGE_LENGTH):
        if i == character_pos:
            bridge_display.append("🏃")
        elif i == treasure_pos:
            bridge_display.append("🌰")
        else:
            bridge_display.append("□")
    
    # 보물 획득 여부 확인
    treasure_acquired = correct_letters_count >= word_length
    
    return {
        'word': game_state['word'],
        'meaning': game_state['meaning'],  # 단어의 뜻 추가
        'category': game_state.get('category', 'fruit'),  # 카테고리 정보 추가
        'word_display': display_word.strip(),
        'attempts_left': game_state['attempts_left'],
        'guessed_letters': sorted(list(game_state['guessed_letters'])),
        'wrong_attempts': game_state['wrong_attempts'],
        'bridge_stage': game_state['wrong_attempts'] + 1,
        'bridge_display': bridge_display,
        'character_pos': character_pos + 1,
        'treasure_pos': treasure_pos + 1,
        'treasure_acquired': treasure_acquired,
        'score': game_state['score'],
        'round_num': game_state['round_num'],
        'total_questions': game_state['total_questions'],
        'current_question_num': game_state['current_question_num'],
        'hint_count': game_state['hint_count']  # 힌트 카운트 추가
    }

if __name__ == '__main__':
    # 로컬 개발용 - 다른 포트 사용
    app.run(debug=True, host='127.0.0.1', port=8080) 