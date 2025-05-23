import re

import nltk
import PyPDF2
from docx import Document
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics.pairwise import cosine_similarity

# Загрузка необходимых ресурсов NLTK
nltk.download("punkt")
nltk.download("stopwords")

# Инициализация модели для многоязычного анализа
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")


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
    """Извлекает навыки из текста"""
    # Разбиваем текст на предложения
    sentences = nltk.sent_tokenize(text)

    # Определяем ключевые слова для навыков
    skill_keywords = [
        "опыт",
        "навыки",
        "умения",
        "знания",
        "технологии",
        "experience",
        "skills",
        "abilities",
        "knowledge",
        "technologies",
    ]

    # Словарь технических навыков
    tech_skills = {
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
        "html",
        "css",
        "react",
        "angular",
        "vue",
        "node.js",
        "django",
        "flask",
        "spring",
        "laravel",
        "express",
        "asp.net",
        "rails",
        "docker",
        "kubernetes",
        "aws",
        "azure",
        "gcp",
        "linux",
        "unix",
        "git",
        "sql",
        "nosql",
        "mongodb",
        "postgresql",
        "mysql",
        "oracle",
        "redis",
        "elasticsearch",
        "kafka",
        "rabbitmq",
        "jenkins",
        "gitlab",
        "jira",
        "confluence",
        "agile",
        "scrum",
        "kanban",
    }

    skills = set()

    # Ищем технические навыки в тексте
    for skill in tech_skills:
        if skill.lower() in text.lower():
            skills.add(skill)

    # Ищем предложения, содержащие ключевые слова
    for sentence in sentences:
        if any(keyword in sentence.lower() for keyword in skill_keywords):
            # Извлекаем слова, которые могут быть навыками
            words = sentence.lower().split()
            for word in words:
                if len(word) > 3 and word.isalpha():
                    skills.add(word)

    return skills


def analyze_skills(job_description, resume_text):
    """Анализирует отсутствующие навыки"""
    job_skills = extract_skills(job_description)
    resume_skills = extract_skills(resume_text)

    # Находим отсутствующие навыки
    missing_skills = job_skills - resume_skills

    return list(missing_skills)


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
