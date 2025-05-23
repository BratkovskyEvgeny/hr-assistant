import time

import streamlit as st
import streamlit as st

from utils import (
    analyze_skills,
    calculate_similarity,
    extract_text_from_file,
    get_detailed_analysis,
)

# Настройка страницы
st.set_page_config(
    page_title="HR Assistant - Оценка резюме",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Стили для красивого отображения
st.markdown(
    """
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #4CAF50;
        color: white;
        font-size: 1.2em;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .css-1d391kg {
        padding: 2rem;
    }
    .stProgress .st-bo {
        background-color: #4CAF50;
    }
    .stProgress .st-bp {
        background-color: #45a049;
    }
    .stAlert {
        border-radius: 5px;
        padding: 1rem;
    }
    .stExpander {
        border-radius: 5px;
        border: 1px solid #e0e0e0;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Заголовок с анимацией
st.markdown(
    """
    <div style='text-align: center; padding: 2rem;'>
        <h1 style='color: #2E4053; font-size: 3em; margin-bottom: 1rem;'>
            🤖 HR Assistant - Оценка резюме
        </h1>
        <p style='color: #566573; font-size: 1.2em;'>
            Анализ соответствия резюме требованиям вакансии
        </p>
    </div>
""",
    unsafe_allow_html=True,
)

# Создаем две колонки для основного контента
col1, col2 = st.columns([1, 1])

with col1:
    # Секция для ввода описания вакансии
    st.markdown(
        """
        <div style='background-color: #f8f9fa; padding: 1.5rem; border-radius: 10px; margin-bottom: 2rem;'>
            <h2 style='color: #2E4053; margin-bottom: 1rem;'>📋 Описание вакансии</h2>
        </div>
    """,
        unsafe_allow_html=True,
    )

    job_description = st.text_area(
        "Введите описание вакансии",
        height=200,
        help="Опишите требования к вакансии, необходимые навыки и опыт",
    )

with col2:
    # Секция для загрузки резюме
    st.markdown(
        """
        <div style='background-color: #f8f9fa; padding: 1.5rem; border-radius: 10px; margin-bottom: 2rem;'>
            <h2 style='color: #2E4053; margin-bottom: 1rem;'>📄 Загрузка резюме</h2>
        </div>
    """,
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader(
        "Загрузите резюме (PDF или DOCX)", type=["pdf", "docx"]
    )

if uploaded_file is not None and job_description:
    # Показываем прогресс анализа
    with st.spinner("Анализируем резюме..."):
        progress_bar = st.progress(0)
        for i in range(100):
            time.sleep(0.01)
            progress_bar.progress(i + 1)

        # Извлекаем текст из резюме
        resume_text = extract_text_from_file(uploaded_file)

        # Анализируем соответствие
        similarity_score = calculate_similarity(job_description, resume_text)
        analysis_results = analyze_skills(job_description, resume_text)
        detailed_analysis = get_detailed_analysis(job_description, resume_text)

    # Отображаем результаты
    st.markdown(
        """
        <div style='background-color: #f8f9fa; padding: 1.5rem; border-radius: 10px; margin: 2rem 0;'>
            <h2 style='color: #2E4053; margin-bottom: 1rem;'>📊 Результаты анализа</h2>
        </div>
    """,
        unsafe_allow_html=True,
    )

    # Создаем колонки для отображения результатов
    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Процент соответствия",
            f"{similarity_score:.1f}%",
            delta=f"{similarity_score - 50:.1f}%" if similarity_score > 50 else None,
        )

    with col2:
        if analysis_results["missing_skills"] or analysis_results["missing_experience"]:
            st.warning("Обнаружены несоответствия")
        else:
            st.success("Все требования соответствуют!")

    # Отображаем отсутствующие навыки
    if analysis_results["missing_skills"]:
        st.markdown(
            """
            <div style='background-color: #fff3cd; padding: 1.5rem; border-radius: 10px; margin: 1rem 0;'>
                <h3 style='color: #856404; margin-bottom: 1rem;'>🔍 Отсутствующие навыки</h3>
            </div>
        """,
            unsafe_allow_html=True,
        )

        # Сортируем навыки для лучшей читаемости
        missing_skills = sorted(analysis_results["missing_skills"])
        # Отображаем навыки в виде списка
        for skill in missing_skills:
            st.markdown(
                f"""
                <div style='background-color: #fff; padding: 0.5rem 1rem; border-radius: 5px; margin: 0.5rem 0;'>
                    • {skill}
                </div>
            """,
                unsafe_allow_html=True,
            )

    # Отображаем отсутствующий опыт
    if analysis_results["missing_experience"]:
        st.markdown(
            """
            <div style='background-color: #f8d7da; padding: 1.5rem; border-radius: 10px; margin: 1rem 0;'>
                <h3 style='color: #721c24; margin-bottom: 1rem;'>⚠️ Отсутствующий опыт</h3>
            </div>
        """,
            unsafe_allow_html=True,
        )

        for exp in analysis_results["missing_experience"]:
            st.markdown(
                f"""
                <div style='background-color: #fff; padding: 0.5rem 1rem; border-radius: 5px; margin: 0.5rem 0;'>
                    • {exp}
                </div>
            """,
                unsafe_allow_html=True,
            )

    # Отображаем детальный анализ
    st.markdown(
        """
        <div style='background-color: #f8f9fa; padding: 1.5rem; border-radius: 10px; margin: 2rem 0;'>
            <h2 style='color: #2E4053; margin-bottom: 1rem;'>📑 Детальный анализ</h2>
        </div>
    """,
        unsafe_allow_html=True,
    )

    # Создаем вкладки для разных секций
    tabs = st.tabs(["Опыт работы", "Образование", "Навыки"])

    section_mapping = {
        "Опыт работы": "experience",
        "Образование": "education",
        "Навыки": "skills",
    }

    for tab, section in zip(tabs, section_mapping.keys()):
        with tab:
            if section_mapping[section] in detailed_analysis:
                analysis = detailed_analysis[section_mapping[section]]
                st.metric("Релевантность", f"{analysis['relevance']:.1f}%")
                st.text_area("Текст", analysis["text"], height=150, disabled=True)
            else:
                st.info("Информация не найдена")
