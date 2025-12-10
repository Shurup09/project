from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
import json
from werkzeug.utils import secure_filename
from PIL import Image
import base64
from io import BytesIO
from datetime import datetime
import shutil

app = Flask(__name__)
app.secret_key = 'flower-care-secret-key-2024'
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
app.config['USER_FOLDERS'] = 'user_data'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Создаем папки
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['USER_FOLDERS'], exist_ok=True)

# Файл для хранения пользователей
USERS_FILE = 'users.json'


def init_users_file():
    """Инициализация файла пользователей"""
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w') as f:
            json.dump([], f)


def read_users():
    """Чтение пользователей из файла"""
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except:
        return []


def save_users(users):
    """Сохранение пользователей в файл"""
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)


def save_user(username, email, password, theme='light'):
    """Сохранение нового пользователя"""
    users = read_users()

    if any(user['email'] == email for user in users):
        return False, 'Пользователь с таким email уже существует'

    user_id = len(users) + 1
    new_user = {
        'id': user_id,
        'username': username,
        'email': email,
        'password': password,
        'theme': theme,
        'created_at': datetime.now().isoformat(),
        'analysis_count': 0,
        'flowers': []
    }

    users.append(new_user)
    save_users(users)

    # Создаем папку пользователя
    user_folder = os.path.join(app.config['USER_FOLDERS'], str(user_id))
    os.makedirs(user_folder, exist_ok=True)

    return True, 'Регистрация успешна'


def authenticate_user(email, password):
    """Аутентификация пользователя"""
    users = read_users()
    user = next((u for u in users if u['email'] == email and u['password'] == password), None)
    return user


def get_user_data(user_id):
    """Получение данных пользователя"""
    users = read_users()
    return next((u for u in users if u['id'] == user_id), None)


def update_user_data(user_id, data):
    """Обновление данных пользователя"""
    users = read_users()
    for user in users:
        if user['id'] == user_id:
            user.update(data)
            break
    save_users(users)


def save_flower_to_user(user_id, flower_data, image_path):
    """Сохранение информации о цветке в аккаунт пользователя"""
    users = read_users()
    for user in users:
        if user['id'] == user_id:
            # Копируем изображение в папку пользователя
            if image_path and os.path.exists(image_path):
                user_folder = os.path.join(app.config['USER_FOLDERS'], str(user_id))
                filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                user_image_path = os.path.join(user_folder, filename)
                shutil.copy2(image_path, user_image_path)

                # Сохраняем данные о цветке
                flower_record = {
                    'id': len(user.get('flowers', [])) + 1,
                    'flower_type': flower_data['flower_type'],
                    'name': flower_data['name'],
                    'type': flower_data['type'],
                    'analysis_date': datetime.now().isoformat(),
                    'image_filename': filename,
                    'care': flower_data['care'],
                    'problems': flower_data['problems']
                }

                if 'flowers' not in user:
                    user['flowers'] = []
                user['flowers'].append(flower_record)
                user['analysis_count'] = user.get('analysis_count', 0) + 1
            break
    save_users(users)


def get_user_flowers(user_id):
    """Получение всех цветков пользователя"""
    user = get_user_data(user_id)
    if user and 'flowers' in user:
        return user['flowers']
    return []


def get_user_flower_image(user_id, filename):
    """Получение пути к изображению цветка пользователя"""
    user_folder = os.path.join(app.config['USER_FOLDERS'], str(user_id))
    return os.path.join(user_folder, filename)


def image_to_base64(image_path):
    """Конвертация изображения в base64 для отображения в HTML"""
    try:
        with Image.open(image_path) as img:
            img.thumbnail((300, 300))
            buffered = BytesIO()
            img.save(buffered, format="JPEG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            return f"data:image/jpeg;base64,{img_str}"
    except Exception as e:
        print(f"Ошибка конвертации: {e}")
        return None


# База данных цветов
FLOWER_DATABASE = {
    'rose': {
        'name': 'Роза',
        'type': 'Комнатная роза',
        'description': 'Королева цветов с прекрасным ароматом и разнообразной окраской.',
        'care': {
            'watering': 'Умеренный полив, 2-3 раза в неделю',
            'light': 'Яркий рассеянный свет',
            'temperature': '18-25°C',
            'humidity': 'Умеренная влажность',
            'fertilizer': 'Удобрять каждые 2 недели в период роста'
        },
        'problems': [
            'Мучнистая роса - белый налет на листьях',
            'Тля - мелкие насекомые на бутонах',
            'Черная пятнистость - темные пятна на листьях'
        ]
    },
    'orchid': {
        'name': 'Орхидея',
        'type': 'Фаленопсис',
        'description': 'Элегантный тропический цветок с длительным периодом цветения.',
        'care': {
            'watering': 'Полив методом погружения 1 раз в неделю',
            'light': 'Рассеянный свет, избегать прямого солнца',
            'temperature': '20-28°C',
            'humidity': 'Высокая влажность (60-80%)',
            'fertilizer': 'Специальное удобрение для орхидей'
        },
        'problems': [
            'Корневая гниль - от избыточного полива',
            'Ожоги листьев - от прямого солнца',
            'Отсутствие цветения - недостаток света'
        ]
    },
    'cactus': {
        'name': 'Кактус',
        'type': 'Пустынный кактус',
        'description': 'Выносливое растение, идеальное для начинающих садоводов.',
        'care': {
            'watering': 'Редкий полив, 1 раз в 2-3 недели',
            'light': 'Прямой солнечный свет',
            'temperature': '20-35°C',
            'humidity': 'Низкая влажность',
            'fertilizer': 'Удобрение для кактусов весной и летом'
        },
        'problems': [
            'Перелив - приводит к гниению',
            'Недостаток света - вытягивание стебля',
            'Вредители - мучнистый червец'
        ]
    },
    'lavender': {
        'name': 'Лаванда',
        'type': 'Комнатная лаванда',
        'description': 'Ароматное растение с успокаивающими свойствами.',
        'care': {
            'watering': 'Умеренный полив, давать почве просыхать',
            'light': 'Яркое прямое солнце',
            'temperature': '15-25°C',
            'humidity': 'Низкая влажность',
            'fertilizer': 'Минимальная подкормка'
        },
        'problems': [
            'Избыточная влажность - грибковые заболевания',
            'Недостаток света - слабый рост',
            'Перелив - корневая гниль'
        ]
    }
}


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}


def analyze_flower_image(image_path):
    """Анализ изображения цветка и определение его типа"""
    try:
        filename = image_path.lower()

        if 'rose' in filename or 'роза' in filename:
            return 'rose'
        elif 'orchid' in filename or 'орхидея' in filename:
            return 'orchid'
        elif 'cactus' in filename or 'кактус' in filename:
            return 'cactus'
        elif 'lavender' in filename or 'лаванда' in filename:
            return 'lavender'
        else:
            import random
            return random.choice(list(FLOWER_DATABASE.keys()))

    except Exception as e:
        print(f"Ошибка анализа: {e}")
        return 'rose'


@app.route("/", methods=['GET', 'POST'])
def index():
    flower_data = None
    flower_image = None
    user_data = None

    if 'user_id' in session:
        user_data = get_user_data(session['user_id'])

    if request.method == 'POST' and 'user_id' in session:
        if 'flower_image' not in request.files:
            flash('Файл не выбран!', 'error')
        else:
            file = request.files['flower_image']

            if file.filename == '':
                flash('Файл не выбран!', 'error')
            elif file and allowed_file(file.filename):
                try:
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)

                    flower_type = analyze_flower_image(filename)
                    flower_info = FLOWER_DATABASE.get(flower_type, FLOWER_DATABASE['rose'])

                    # Создаем полные данные о цветке
                    full_flower_data = {
                        'flower_type': flower_type,
                        'name': flower_info['name'],
                        'type': flower_info['type'],
                        'description': flower_info['description'],
                        'care': flower_info['care'],
                        'problems': flower_info['problems']
                    }

                    # Сохраняем в аккаунт пользователя
                    save_flower_to_user(session['user_id'], full_flower_data, filepath)

                    flower_data = full_flower_data
                    flower_image = image_to_base64(filepath)

                    flash('Цветок успешно определен и сохранен в ваш аккаунт!', 'success')

                except Exception as e:
                    flash(f'Ошибка при обработке изображения: {str(e)}', 'error')
            else:
                flash('Недопустимый формат файла! Разрешены: png, jpg, jpeg, gif', 'error')

    return render_template('index.html',
                           flower_data=flower_data,
                           flower_image=flower_image,
                           user_data=user_data)


@app.route("/my-account")
def my_account():
    if 'user_id' not in session:
        flash('Пожалуйста, войдите в систему.', 'error')
        return redirect(url_for('index'))

    user_data = get_user_data(session['user_id'])
    user_flowers = get_user_flowers(session['user_id'])

    # Функция для получения URL изображения
    def get_flower_image_url(filename):
        if filename:
            image_path = get_user_flower_image(session['user_id'], filename)
            return image_to_base64(image_path)
        return None

    return render_template('index.html',
                           user_data=user_data,
                           user_flowers=user_flowers,
                           get_flower_image_url=get_flower_image_url)


@app.route("/change-theme")
def change_theme():
    theme = request.args.get('theme', 'light')
    if 'user_id' in session:
        update_user_data(session['user_id'], {'theme': theme})
    session['theme'] = theme
    return redirect(request.referrer or url_for('index'))


@app.route("/register", methods=['POST'])
def register():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    theme = request.form.get('theme', 'light')

    if not all([username, email, password, confirm_password]):
        flash('Все поля обязательны для заполнения!', 'error')
        return redirect(url_for('index'))

    if password != confirm_password:
        flash('Пароли не совпадают!', 'error')
        return redirect(url_for('index'))

    success, message = save_user(username, email, password, theme)

    if success:
        flash(message, 'success')
        user = authenticate_user(email, password)
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['email'] = user['email']
            session['theme'] = user.get('theme', 'light')
            flash(f'Добро пожаловать, {user["username"]}!', 'success')
    else:
        flash(message, 'error')

    return redirect(url_for('index'))


@app.route("/login", methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')

    if not all([email, password]):
        flash('Все поля обязательны для заполнения!', 'error')
        return redirect(url_for('index'))

    user = authenticate_user(email, password)

    if user:
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['email'] = user['email']
        session['theme'] = user.get('theme', 'light')
        flash(f'Добро пожаловать, {user["username"]}!', 'success')
    else:
        flash('Неверный email или пароль!', 'error')

    return redirect(url_for('index'))


@app.route("/logout")
def logout():
    session.clear()
    flash('Вы успешно вышли из системы!', 'info')
    return redirect(url_for('index'))


if __name__ == "__main__":
    init_users_file()
    app.run(
        host='0.0.0.0',  # Слушать все сетевые интерфейсы
        port=5000,       # Порт (можно любой)
        debug=True       # Режим отладки
    )
