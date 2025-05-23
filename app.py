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
        if (
            any(analysis_results["missing_skills"].values())
            or analysis_results["missing_experience"]
        ):
            st.warning("Обнаружены несоответствия")
        else:
            st.success("Все требования соответствуют!")

    # Отображаем отсутствующие навыки по категориям
    st.subheader("🔍 Отсутствующие навыки")

    for category, skills in analysis_results["missing_skills"].items():
        if skills:
            with st.expander(f"📚 {category.capitalize()}"):
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

    # Отображаем полный текст резюме
    with st.expander("Просмотр текста резюме"):
        st.text(resume_text)
