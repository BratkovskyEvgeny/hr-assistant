import re

import nltk
import PyPDF2
from docx import Document
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Загрузка необходимых ресурсов NLTK
nltk.download("punkt")
nltk.download("stopwords")
nltk.download("averaged_perceptron_tagger")

# Инициализация модели для многоязычного анализа
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

# Словари технических навыков
TECH_SKILLS = {
    # Языки программирования
    "languages": {
        "python",
        "java",
        "javascript",
        "typescript",
        "c++",
        "c#",
        "php",
        "ruby",
        "go",
        "rust",
        "swift",
        "kotlin",
        "scala",
        "r",
        "matlab",
    },
    # Фреймворки и библиотеки
    "frameworks": {
        "django",
        "flask",
        "fastapi",
        "spring",
        "laravel",
        "express",
        "asp.net",
        "rails",
        "react",
        "angular",
        "vue",
        "node.js",
        "tensorflow",
        "pytorch",
        "pandas",
        "numpy",
        "scikit-learn",
        "keras",
        "spark",
        "hadoop",
    },
    # Базы данных
    "databases": {
        "sql",
        "nosql",
        "mongodb",
        "postgresql",
        "mysql",
        "oracle",
        "redis",
        "elasticsearch",
        "cassandra",
        "neo4j",
        "dynamodb",
    },
    # DevOps и инструменты
    "devops": {
        "docker",
        "kubernetes",
        "aws",
        "azure",
        "gcp",
        "linux",
        "unix",
        "git",
        "jenkins",
        "gitlab",
        "jira",
        "confluence",
        "ansible",
        "terraform",
    },
    # Методологии
    "methodologies": {"agile", "scrum", "kanban", "waterfall", "devops", "ci/cd"},
}

# Ключевые слова для определения обязанностей
RESPONSIBILITY_KEYWORDS = {
    "разработка",
    "development",
    "разработать",
    "develop",
    "создание",
    "creation",
    "создать",
    "create",
    "внедрение",
    "implementation",
    "внедрить",
    "implement",
    "оптимизация",
    "optimization",
    "оптимизировать",
    "optimize",
    "поддержка",
    "maintenance",
    "поддерживать",
    "maintain",
    "тестирование",
    "testing",
    "тестировать",
    "test",
    "анализ",
    "analysis",
    "анализировать",
    "analyze",
    "управление",
    "management",
    "управлять",
    "manage",
    "координация",
    "coordination",
    "координировать",
    "coordinate",
}


def extract_text_from_file(file):
    """Извлекает текст из PDF или DOCX файла"""
    if file.name.endswith(".pdf"):
        return extract_text_from_pdf(file)
    elif file.name.endswith(".docx"):
        return extract_text_from_docx(file)
    else:
        raise ValueError("Неподдерживаемый формат файла")


def extract_text_from_pdf(file):
    """Извлекает текст из PDF файла"""
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text


def extract_text_from_docx(file):
    """Извлекает текст из DOCX файла"""
    doc = Document(file)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text


def preprocess_text(text):
    """Предобработка текста"""
    # Приведение к нижнему регистру
    text = text.lower()

    # Удаление специальных символов
    text = re.sub(r"[^\w\s]", " ", text)

    # Токенизация
    tokens = word_tokenize(text)

    # Удаление стоп-слов
    stop_words = set(stopwords.words("russian") + stopwords.words("english"))
    tokens = [token for token in tokens if token not in stop_words]

    return " ".join(tokens)


def calculate_similarity(job_description, resume_text):
    """Рассчитывает процент соответствия резюме требованиям вакансии"""
    try:
        # Получаем эмбеддинги текстов
        job_embedding = model.encode(job_description)
        resume_embedding = model.encode(resume_text)

        # Рассчитываем косинусное сходство
        similarity = cosine_similarity(
            job_embedding.reshape(1, -1), resume_embedding.reshape(1, -1)
        )[0][0]

        # Преобразование в проценты
        return similarity * 100
    except Exception as e:
        print(f"Ошибка при расчете схожести: {str(e)}")
        return 0.0


def extract_skills(text):
    """Извлекает навыки из текста с учетом категорий"""
    skills = {category: set() for category in TECH_SKILLS.keys()}

    # Разбиваем текст на предложения
    sentences = sent_tokenize(text.lower())

    # Словарь для хранения контекста использования навыков
    skill_context = {category: {} for category in TECH_SKILLS.keys()}

    # Ищем технические навыки в тексте с учетом контекста
    for sentence in sentences:
        words = sentence.split()

        # Проверяем наличие ключевых слов опыта
        has_experience = any(
            word in ["опыт", "experience", "работал", "worked", "использовал", "used"]
            for word in words
        )

        for category, skill_set in TECH_SKILLS.items():
            for skill in skill_set:
                skill_lower = skill.lower()

                # Проверяем точное совпадение слова
                if skill_lower in words:
                    # Получаем контекст вокруг навыка
                    try:
                        skill_index = words.index(skill_lower)
                        context = words[
                            max(0, skill_index - 3) : min(len(words), skill_index + 4)
                        ]

                        # Проверяем наличие отрицаний
                        has_negation = any(
                            word in ["нет", "не", "без", "no", "not", "without"]
                            for word in context[:skill_index]
                        )

                        # Проверяем наличие ключевых слов опыта
                        has_skill_experience = any(
                            word in RESPONSIBILITY_KEYWORDS for word in context
                        )

                        # Добавляем навык только если нет отрицания и есть опыт
                        if not has_negation and (
                            has_experience or has_skill_experience
                        ):
                            skills[category].add(skill)
                            # Сохраняем контекст использования
                            if skill not in skill_context[category]:
                                skill_context[category][skill] = []
                            skill_context[category][skill].append(sentence)
                    except ValueError:
                        continue

    # Фильтруем навыки на основе контекста
    filtered_skills = {category: set() for category in TECH_SKILLS.keys()}
    for category in TECH_SKILLS.keys():
        for skill in skills[category]:
            contexts = skill_context[category][skill]
            # Проверяем, что навык упоминается в контексте реального использования
            if any(
                any(
                    word in context
                    for word in [
                        "разработка",
                        "development",
                        "создание",
                        "creation",
                        "внедрение",
                        "implementation",
                        "опыт",
                        "experience",
                    ]
                )
                for context in contexts
            ):
                filtered_skills[category].add(skill)

    return filtered_skills


def extract_responsibilities(text):
    """Извлекает обязанности из текста"""
    responsibilities = []
    sentences = sent_tokenize(text.lower())

    for sentence in sentences:
        # Проверяем, содержит ли предложение ключевые слова обязанностей
        if any(keyword in sentence for keyword in RESPONSIBILITY_KEYWORDS):
            # Получаем эмбеддинг предложения
            sentence_embedding = model.encode(sentence)

            # Проверяем, не является ли это дубликатом
            is_duplicate = False
            for existing_resp in responsibilities:
                existing_embedding = model.encode(existing_resp)
                similarity = cosine_similarity(
                    sentence_embedding.reshape(1, -1), existing_embedding.reshape(1, -1)
                )[0][0]
                if similarity > 0.8:  # Порог схожести
                    is_duplicate = True
                    break

            if not is_duplicate:
                responsibilities.append(sentence)

    return responsibilities


def analyze_skills(job_description, resume_text):
    """Анализирует отсутствующие навыки и опыт"""
    # Извлекаем навыки из описания вакансии и резюме
    job_skills = extract_skills(job_description)
    resume_skills = extract_skills(resume_text)

    # Извлекаем обязанности
    job_responsibilities = extract_responsibilities(job_description)
    resume_responsibilities = extract_responsibilities(resume_text)

    # Анализируем отсутствующие навыки по категориям
    missing_skills = {category: set() for category in TECH_SKILLS.keys()}
    for category in TECH_SKILLS.keys():
        missing_skills[category] = job_skills[category] - resume_skills[category]

    # Анализируем отсутствующий опыт
    missing_experience = []
    for job_resp in job_responsibilities:
        job_resp_embedding = model.encode(job_resp)
        max_similarity = 0
        for resume_resp in resume_responsibilities:
            resume_resp_embedding = model.encode(resume_resp)
            similarity = cosine_similarity(
                job_resp_embedding.reshape(1, -1), resume_resp_embedding.reshape(1, -1)
            )[0][0]
            max_similarity = max(max_similarity, similarity)

        if max_similarity < 0.5:  # Порог схожести
            missing_experience.append(job_resp)

    return {"missing_skills": missing_skills, "missing_experience": missing_experience}


def get_detailed_analysis(job_description, resume_text):
    """Получает детальный анализ резюме"""
    # Разбиваем текст на секции
    sections = {
        "experience": ["опыт работы", "experience", "work experience"],
        "education": ["образование", "education"],
        "skills": ["навыки", "skills", "технические навыки"],
        "projects": ["проекты", "projects"],
    }

    analysis = {}

    # Анализируем каждую секцию
    for section, keywords in sections.items():
        # Находим соответствующие части текста
        section_text = ""
        for keyword in keywords:
            if keyword in resume_text.lower():
                # Извлекаем текст после ключевого слова
                idx = resume_text.lower().find(keyword)
                section_text += resume_text[idx:].split("\n")[0] + "\n"

        if section_text:
            try:
                # Получаем эмбеддинги для анализа
                section_embedding = model.encode(section_text)
                job_embedding = model.encode(job_description)

                # Рассчитываем сходство
                similarity = cosine_similarity(
                    section_embedding.reshape(1, -1), job_embedding.reshape(1, -1)
                )[0][0]

                analysis[section] = {
                    "text": section_text,
                    "relevance": similarity * 100,
                }
            except Exception as e:
                print(f"Ошибка при анализе секции {section}: {str(e)}")

    return analysis
