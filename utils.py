import os
import re

import nltk
import numpy as np
import PyPDF2
from docx import Document
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from transformers import logging

# Отключаем предупреждения transformers
logging.set_verbosity_error()

# Загружаем необходимые ресурсы NLTK
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt", quiet=True)

# Путь для кэширования модели
CACHE_DIR = os.path.join(os.path.dirname(__file__), "model_cache")

# Инициализация модели для многоязычного анализа
model = None


def get_model() -> SentenceTransformer:
    """Получает модель с кэшированием"""
    try:
        # Проверяем наличие кэшированной модели
        if os.path.exists(CACHE_DIR):
            return SentenceTransformer(
                "paraphrase-multilingual-MiniLM-L12-v2",
                cache_folder=CACHE_DIR,
                use_auth_token=True,
            )

        # Если кэша нет, создаем директорию и загружаем модель
        os.makedirs(CACHE_DIR, exist_ok=True)
        return SentenceTransformer(
            "paraphrase-multilingual-MiniLM-L12-v2",
            cache_folder=CACHE_DIR,
            use_auth_token=True,
        )
    except Exception as e:
        print(f"Ошибка при загрузке модели: {str(e)}")
        # Возвращаем None в случае ошибки
        return None


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
        "langchain",
        "chromadb",
        "transformers",
        "huggingface",
        "streamlit",
        "gradio",
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
        "pinecone",
        "weaviate",
        "qdrant",
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
        "prometheus",
        "grafana",
    },
    # Методологии
    "methodologies": {
        "agile",
        "scrum",
        "kanban",
        "waterfall",
        "devops",
        "ci/cd",
    },
    # AI/ML инструменты
    "ai_ml": {
        "langchain",
        "chromadb",
        "transformers",
        "huggingface",
        "pinecone",
        "weaviate",
        "qdrant",
        "tensorflow",
        "pytorch",
        "scikit-learn",
        "keras",
    },
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


def calculate_similarity(text1: str, text2: str) -> float:
    """Вычисляет семантическую схожесть между двумя текстами"""
    try:
        model = get_model()
        if model is None:
            return 0.0

        # Разбиваем тексты на предложения
        sentences1 = sent_tokenize(text1)
        sentences2 = sent_tokenize(text2)

        # Получаем эмбеддинги
        embeddings1 = model.encode(sentences1)
        embeddings2 = model.encode(sentences2)

        # Вычисляем косинусное сходство
        similarity = np.mean(
            [
                np.max(
                    [
                        np.dot(emb1, emb2)
                        / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
                        for emb2 in embeddings2
                    ]
                )
                for emb1 in embeddings1
            ]
        )

        # Преобразуем в проценты
        return float(similarity * 100)
    except Exception as e:
        print(f"Ошибка при вычислении схожести: {str(e)}")
        return 0.0


def extract_skills(text):
    """Извлекает навыки из текста"""
    # Разбиваем текст на предложения
    sentences = sent_tokenize(text.lower())

    # Множество для хранения найденных навыков
    skills = set()

    # Стоп-слова для фильтрации
    stop_words = {
        "опыт",
        "experience",
        "работа",
        "work",
        "разработка",
        "development",
        "создание",
        "creation",
        "внедрение",
        "implementation",
        "использование",
        "using",
        "знание",
        "knowledge",
        "умение",
        "ability",
        "навык",
        "skill",
        "требование",
        "requirement",
        "обязанность",
        "responsibility",
        "задача",
        "task",
        "проект",
        "project",
        "верим",
        "делать",
        "жизнь",
        "инструмент",
        "интеллект",
        "который",
        "легче",
        "лучше",
        "нам",
        "наш",
        "помогает",
        "усиливает",
        "что",
        "это",
        "агентов",
        "баз",
        "будут",
        "вакансии",
        "валюта",
        "векторизованных",
        "владельцев",
        "внедрить",
        "выполнять",
        "достаточно",
        "драгоценные",
        "задач",
        "задачу",
        "знаний",
        "конкретного",
        "которые",
        "лет",
        "металлы",
        "название",
        "обязательно",
        "опыта",
        "организация",
        "пайплайна",
        "перед",
        "полученного",
        "продуктов",
        "промышленное",
        "процесса",
        "процессе",
        "работу",
        "ранжирование",
        "реализация",
        "роли",
        "сильных",
        "слабых",
        "собой",
        "создания",
        "создать",
        "ставим",
        "сторон",
        "требования",
        "уровне",
        "цепочек",
        "часть",
        "эффективные",
    }

    # Ищем технологии в тексте
    for sentence in sentences:
        # Разбиваем предложение на слова
        words = sentence.split()

        # Проверяем каждое слово
        for word in words:
            # Очищаем слово от специальных символов
            clean_word = re.sub(r"[^\w\s]", "", word)

            # Пропускаем короткие слова, стоп-слова и слова с цифрами
            if (
                len(clean_word) < 3
                or clean_word in stop_words
                or any(c.isdigit() for c in clean_word)
                or clean_word in ["the", "and", "for", "with", "using", "use", "used"]
            ):
                continue

            # Проверяем, что слово не является частью фразы
            if not any(
                clean_word in phrase for phrase in ["опыт работы", "work experience"]
            ):
                # Проверяем, что слово похоже на технологию
                if (
                    clean_word.endswith(
                        ("js", "py", "net", "db", "sql", "api", "sdk", "ml", "ai")
                    )
                    or clean_word.startswith(
                        (
                            "react",
                            "angular",
                            "vue",
                            "node",
                            "django",
                            "flask",
                            "fast",
                            "spring",
                            "laravel",
                        )
                    )
                    or clean_word
                    in [
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
                        "langchain",
                        "chromadb",
                        "mongodb",
                        "postgresql",
                        "mysql",
                        "oracle",
                        "redis",
                        "elasticsearch",
                        "cassandra",
                        "neo4j",
                        "dynamodb",
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
                        "prometheus",
                        "grafana",
                    ]
                ):
                    skills.add(clean_word)

    return skills


def extract_responsibilities(text):
    """Извлекает обязанности из текста"""
    responsibilities = []
    sentences = sent_tokenize(text.lower())
    model = get_model()

    if model is None:
        print("Ошибка: модель не была загружена")
        return responsibilities

    try:
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
                        sentence_embedding.reshape(1, -1),
                        existing_embedding.reshape(1, -1),
                    )[0][0]
                    if similarity > 0.8:  # Порог схожести
                        is_duplicate = True
                        break

                if not is_duplicate:
                    responsibilities.append(sentence)
    except Exception as e:
        print(f"Ошибка при извлечении обязанностей: {str(e)}")
        return responsibilities

    return responsibilities


def analyze_skills(job_description, resume_text):
    """Анализирует отсутствующие навыки и опыт"""
    # Извлекаем навыки из описания вакансии и резюме
    job_skills = extract_skills(job_description)
    resume_skills = extract_skills(resume_text)

    # Извлекаем обязанности
    job_responsibilities = extract_responsibilities(job_description)
    resume_responsibilities = extract_responsibilities(resume_text)

    # Анализируем отсутствующие навыки
    missing_skills = job_skills - resume_skills

    # Анализируем отсутствующий опыт
    missing_experience = []
    model = get_model()

    if model is None:
        print("Ошибка: модель не была загружена")
        return {
            "missing_skills": missing_skills,
            "missing_experience": missing_experience,
        }

    try:
        for job_resp in job_responsibilities:
            job_resp_embedding = model.encode(job_resp)
            max_similarity = 0
            for resume_resp in resume_responsibilities:
                resume_resp_embedding = model.encode(resume_resp)
                similarity = cosine_similarity(
                    job_resp_embedding.reshape(1, -1),
                    resume_resp_embedding.reshape(1, -1),
                )[0][0]
                max_similarity = max(max_similarity, similarity)

            if max_similarity < 0.5:  # Порог схожести
                missing_experience.append(job_resp)
    except Exception as e:
        print(f"Ошибка при анализе опыта: {str(e)}")
        return {
            "missing_skills": missing_skills,
            "missing_experience": missing_experience,
        }

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
    model = get_model()

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
