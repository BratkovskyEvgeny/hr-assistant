import time

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
    /* Основные стили */
    .main {
        background-color: #0E1117;
        color: #FFFFFF;
    }
    
    /* Стили для контейнеров */
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
        padding: 2rem;
    }
    
    /* Стили для заголовков */
    h1, h2, h3 {
        color: #FFFFFF;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    
    /* Стили для кнопок */
    .stButton>button {
        background-color: #FF4B4B;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background-color: #FF6B6B;
        box-shadow: 0 2px 8px rgba(255, 75, 75, 0.3);
    }
    
    /* Стили для текстовых полей */
    .stTextArea>div>div>textarea {
        background-color: #262730;
        color: #FFFFFF;
        border: 1px solid #3E3E3E;
        border-radius: 4px;
    }
    
    /* Стили для прогресс-бара */
    .stProgress .st-bo {
        background-color: #FF4B4B;
    }
    
    .stProgress .st-bp {
        background-color: #FF6B6B;
    }
    
    /* Стили для алертов */
    .stAlert {
        background-color: #262730;
        border: 1px solid #3E3E3E;
        border-radius: 4px;
        color: #FFFFFF;
    }
    
    /* Стили для вкладок */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #262730;
        border-radius: 4px;
        padding: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #FFFFFF;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #3E3E3E;
    }
    
    /* Стили для метрик */
    .stMetric {
        background-color: #262730;
        border-radius: 4px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    /* Стили для списков */
    .skill-item {
        background-color: #262730;
        border-radius: 4px;
        padding: 0.8rem 1.2rem;
        margin: 0.5rem 0;
        border: 1px solid #3E3E3E;
    }
    
    /* Стили для файлового загрузчика */
    .stFileUploader>div {
        background-color: #262730;
        border: 1px solid #3E3E3E;
        border-radius: 4px;
        padding: 1rem;
    }
    
    /* Стили для разделителей */
    hr {
        border-color: #3E3E3E;
        margin: 2rem 0;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Заголовок
st.markdown(
    """
    <div style='text-align: center; margin-bottom: 3rem;'>
        <h1 style='font-size: 2.5rem; margin-bottom: 1rem;'>
            🤖 HR Assistant
        </h1>
        <p style='color: #9CA3AF; font-size: 1.2rem;'>
            Оценка соответствия резюме требованиям вакансии
        </p>
    </div>
""",
    unsafe_allow_html=True,
)

# Основной контент
st.markdown("### 📋 Описание вакансии")
job_description = st.text_area(
    "Введите описание вакансии",
    height=200,
    help="Опишите требования к вакансии, необходимые навыки и опыт",
    placeholder="Вставьте текст описания вакансии здесь...",
)

st.markdown("### 📄 Загрузка резюме")
uploaded_file = st.file_uploader(
    "Загрузите резюме (PDF или DOCX)",
    type=["pdf", "docx"],
    help="Поддерживаются файлы в форматах PDF и DOCX",
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

    st.markdown("### 📊 Результаты анализа")

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
        st.markdown("### 🔍 Отсутствующие навыки")

        # Сортируем навыки для лучшей читаемости
        missing_skills = sorted(analysis_results["missing_skills"])
        # Отображаем навыки в виде списка
        for skill in missing_skills:
            st.markdown(
                f"""
                <div class='skill-item'>
                    • {skill}
                </div>
            """,
                unsafe_allow_html=True,
            )

    # Отображаем отсутствующий опыт
    if analysis_results["missing_experience"]:
        st.markdown("### ⚠️ Отсутствующий опыт")

        for exp in analysis_results["missing_experience"]:
            st.markdown(
                f"""
                <div class='skill-item'>
                    • {exp}
                </div>
            """,
                unsafe_allow_html=True,
            )

    # Отображаем детальный анализ
    st.markdown("### 📑 Детальный анализ")

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
