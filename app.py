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
        background-color: #1a1a1a;
        color: #ffd700;
        padding: 2rem;
    }
    
    /* Стили для контейнеров */
    .container {
        background: linear-gradient(145deg, #2a2a2a, #1a1a1a);
        border: 1px solid #ffd700;
        border-radius: 15px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(255, 215, 0, 0.1);
        transition: all 0.3s ease;
    }
    
    .container:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(255, 215, 0, 0.2);
    }
    
    /* Стили для заголовков */
    h1, h2, h3 {
        color: #ffd700;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
    }
    
    /* Стили для кнопок */
    .stButton>button {
        background: linear-gradient(145deg, #2a2a2a, #1a1a1a);
        color: #ffd700;
        border: 1px solid #ffd700;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background: linear-gradient(145deg, #ffd700, #ffa500);
        color: #1a1a1a;
        transform: scale(1.05);
    }
    
    /* Стили для текстовых полей */
    .stTextArea>div>div>textarea {
        background-color: #2a2a2a;
        color: #ffd700;
        border: 1px solid #ffd700;
        border-radius: 8px;
    }
    
    /* Стили для прогресс-бара */
    .stProgress .st-bo {
        background-color: #ffd700;
    }
    
    .stProgress .st-bp {
        background-color: #ffa500;
    }
    
    /* Стили для алертов */
    .stAlert {
        background: linear-gradient(145deg, #2a2a2a, #1a1a1a);
        border: 1px solid #ffd700;
        border-radius: 8px;
        color: #ffd700;
    }
    
    /* Стили для вкладок */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #1a1a1a;
        border: 1px solid #ffd700;
        border-radius: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #ffd700;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #2a2a2a;
    }
    
    /* Анимации */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .fade-in {
        animation: fadeIn 0.5s ease-out;
    }
    
    /* Стили для метрик */
    .stMetric {
        background: linear-gradient(145deg, #2a2a2a, #1a1a1a);
        border: 1px solid #ffd700;
        border-radius: 8px;
        padding: 1rem;
        transition: all 0.3s ease;
    }
    
    .stMetric:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 15px rgba(255, 215, 0, 0.2);
    }
    
    /* Стили для списков */
    .skill-item {
        background: linear-gradient(145deg, #2a2a2a, #1a1a1a);
        border: 1px solid #ffd700;
        border-radius: 8px;
        padding: 0.8rem 1.2rem;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
    }
    
    .skill-item:hover {
        transform: translateX(10px);
        background: linear-gradient(145deg, #ffd700, #ffa500);
        color: #1a1a1a;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Заголовок с анимацией
st.markdown(
    """
    <div class='container fade-in' style='text-align: center;'>
        <h1 style='font-size: 3.5em; margin-bottom: 1rem;'>
            🤖 HR Assistant
        </h1>
        <p style='color: #ffd700; font-size: 1.4em;'>
            Оценка соответствия резюме требованиям вакансии
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
        <div class='container fade-in'>
            <h2 style='margin-bottom: 1.5rem;'>📋 Описание вакансии</h2>
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
        <div class='container fade-in'>
            <h2 style='margin-bottom: 1.5rem;'>📄 Загрузка резюме</h2>
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
        <div class='container fade-in'>
            <h2 style='margin-bottom: 1.5rem;'>📊 Результаты анализа</h2>
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
            <div class='container fade-in'>
                <h3 style='margin-bottom: 1.5rem;'>🔍 Отсутствующие навыки</h3>
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
                <div class='skill-item fade-in'>
                    • {skill}
                </div>
            """,
                unsafe_allow_html=True,
            )

    # Отображаем отсутствующий опыт
    if analysis_results["missing_experience"]:
        st.markdown(
            """
            <div class='container fade-in'>
                <h3 style='margin-bottom: 1.5rem;'>⚠️ Отсутствующий опыт</h3>
            </div>
        """,
            unsafe_allow_html=True,
        )

        for exp in analysis_results["missing_experience"]:
            st.markdown(
                f"""
                <div class='skill-item fade-in'>
                    • {exp}
                </div>
            """,
                unsafe_allow_html=True,
            )

    # Отображаем детальный анализ
    st.markdown(
        """
        <div class='container fade-in'>
            <h2 style='margin-bottom: 1.5rem;'>📑 Детальный анализ</h2>
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
