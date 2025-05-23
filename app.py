import streamlit as st

from utils import (
    analyze_skills,
    calculate_similarity,
    extract_text_from_file,
    get_detailed_analysis,
)

st.set_page_config(
    page_title="HR Assistant - Оценка резюме", page_icon="📝", layout="wide"
)

st.title("🤖 HR Assistant - Оценка резюме")

# Секция для ввода описания вакансии
st.header("📋 Описание вакансии")
job_description = st.text_area(
    "Введите описание вакансии",
    height=200,
    help="Опишите требования к вакансии, необходимые навыки и опыт",
)

# Секция для загрузки резюме
st.header("📄 Загрузка резюме")
uploaded_file = st.file_uploader(
    "Загрузите резюме (PDF или DOCX)", type=["pdf", "docx"]
)

if uploaded_file is not None and job_description:
    # Извлекаем текст из резюме
    resume_text = extract_text_from_file(uploaded_file)

    # Анализируем соответствие
    similarity_score = calculate_similarity(job_description, resume_text)
    analysis_results = analyze_skills(job_description, resume_text)
    detailed_analysis = get_detailed_analysis(job_description, resume_text)

    # Отображаем результаты
    st.header("📊 Результаты анализа")

    # Создаем колонки для отображения результатов
    col1, col2 = st.columns(2)

    with col1:
        st.metric("Процент соответствия", f"{similarity_score:.1f}%")

    with col2:
        if analysis_results["missing_skills"] or analysis_results["missing_experience"]:
            st.warning("Обнаружены несоответствия")
        else:
            st.success("Все требования соответствуют!")

    # Отображаем отсутствующие навыки
    if analysis_results["missing_skills"]:
        st.subheader("🔍 Отсутствующие навыки")
        # Группируем навыки по категориям
        categories = {
            "Языки программирования": [
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
            ],
            "Фреймворки и библиотеки": [
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
            ],
            "Базы данных": [
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
            ],
            "DevOps и инструменты": [
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
            ],
            "Другое": [],
        }

        # Распределяем навыки по категориям
        categorized_skills = {category: [] for category in categories}
        for skill in sorted(analysis_results["missing_skills"]):
            skill_lower = skill.lower()
            categorized = False
            for category, keywords in categories.items():
                if any(keyword in skill_lower for keyword in keywords):
                    categorized_skills[category].append(skill)
                    categorized = True
                    break
            if not categorized:
                categorized_skills["Другое"].append(skill)

        # Отображаем навыки по категориям
        for category, skills in categorized_skills.items():
            if skills:
                with st.expander(f"📚 {category}"):
                    for skill in sorted(skills):
                        st.write(f"- {skill}")

    # Отображаем отсутствующий опыт
    if analysis_results["missing_experience"]:
        st.subheader("⚠️ Отсутствующий опыт")
        for exp in analysis_results["missing_experience"]:
            st.write(f"- {exp}")

    # Отображаем детальный анализ
    st.header("📑 Детальный анализ")

    # Создаем вкладки для разных секций
    tabs = st.tabs(["Опыт работы", "Образование", "Навыки", "Проекты"])

    section_mapping = {
        "Опыт работы": "experience",
        "Образование": "education",
        "Навыки": "skills",
        "Проекты": "projects",
    }

    for tab, section in zip(tabs, section_mapping.keys()):
        with tab:
            if section_mapping[section] in detailed_analysis:
                analysis = detailed_analysis[section_mapping[section]]
                st.metric("Релевантность", f"{analysis['relevance']:.1f}%")
                st.text_area("Текст", analysis["text"], height=150, disabled=True)
            else:
                st.info("Информация не найдена")
