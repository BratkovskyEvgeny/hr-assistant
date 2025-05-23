import re

import nltk
import PyPDF2
from docx import Document
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Загрузка необходимых ресурсов NLTK
nltk.download("punkt", quiet=True)
nltk.download("stopwords", quiet=True)
nltk.download("averaged_perceptron_tagger", quiet=True)

# Инициализация модели для многоязычного анализа
model = None


def get_model():
    """Ленивая загрузка модели"""
    global model
    if model is None:
        model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    return model


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


def calculate_similarity(job_description, resume_text):
    """Рассчитывает процент соответствия резюме требованиям вакансии"""
    try:
        model = get_model()
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
    """Извлекает навыки из текста"""
    skills = set()

    # Разбиваем текст на предложения
    sentences = sent_tokenize(text.lower())

    # Ключевые слова для определения технических навыков
    tech_keywords = {
        "язык",
        "language",
        "framework",
        "фреймворк",
        "библиотека",
        "library",
        "база данных",
        "database",
        "инструмент",
        "tool",
        "технология",
        "technology",
        "платформа",
        "platform",
        "api",
        "sdk",
        "middleware",
        "middleware",
    }

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
    }

    # Ищем технические навыки в тексте
    for sentence in sentences:
        words = sentence.split()

        # Проверяем, содержит ли предложение ключевые слова технических навыков
        has_tech_keyword = any(keyword in sentence for keyword in tech_keywords)

        if has_tech_keyword:
            for i, word in enumerate(words):
                # Пропускаем короткие слова, стоп-слова и слова с цифрами
                if (
                    len(word) < 3
                    or word in stop_words
                    or any(c.isdigit() for c in word)
                    or word in ["the", "and", "for", "with", "using", "use", "used"]
                ):
                    continue

                # Проверяем контекст вокруг слова
                context = words[max(0, i - 3) : min(len(words), i + 4)]

                # Проверяем наличие отрицаний
                has_negation = any(
                    neg in context[:i]
                    for neg in [
                        "нет",
                        "не",
                        "без",
                        "no",
                        "not",
                        "without",
                        "хочу",
                        "want",
                        "желательно",
                        "preferred",
                    ]
                )

                # Проверяем, что слово не является частью фразы
                is_part_of_phrase = any(
                    word in phrase
                    for phrase in [
                        "опыт работы",
                        "work experience",
                        "база данных",
                        "database",
                    ]
                )

                if not has_negation and not is_part_of_phrase:
                    # Очищаем слово от специальных символов
                    clean_word = re.sub(r"[^\w\s]", "", word)
                    if clean_word:
                        skills.add(clean_word)

    return skills


def extract_responsibilities(text):
    """Извлекает обязанности из текста"""
    responsibilities = []
    sentences = sent_tokenize(text.lower())
    model = get_model()

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

    # Анализируем отсутствующие навыки
    missing_skills = job_skills - resume_skills

    # Анализируем отсутствующий опыт
    missing_experience = []
    model = get_model()
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
