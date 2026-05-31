import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Настройка страницы (Пункт 1 задания)
st.set_page_config(
    page_title="Панель аналитики ТЛК",
    page_icon="🚚",
    layout="wide"  # Широкий формат для красивого расположения графиков
)

# Заголовок дашборда
st.title("🚚 Транспортно-логистическая компания (ТЛК)")
st.markdown("---")

# 2. Функция загрузки данных с кэшированием (чтобы сайт работал быстро)
@st.cache_data
def load_all_data():
    # ВНИМАНИЕ: Если вы пересохранили в UTF-8, оставьте 'utf-8-sig'. 
    # Если остались кракозябры, замените на 'cp1251'
    encoding_type = 'utf-8-sig' 
    
    # Загружаем таблицы
    cities = pd.read_csv('Датасет грузоперевозки - Города.csv', encoding=encoding_type)
    clients = pd.read_csv('Датасет грузоперевозки - Клиенты.csv', encoding=encoding_type)
    drivers = pd.read_csv('Датасет грузоперевозки - Водители.csv', encoding=encoding_type)
    transport = pd.read_csv('Датасет грузоперевозки - Транспорт.csv', encoding=encoding_type)
    routes = pd.read_csv('Датасет грузоперевозки - Маршруты.csv', encoding=encoding_type)
    flights = pd.read_csv('Датасет грузоперевозки - Рейсы.csv', encoding=encoding_type)
    cargo = pd.read_csv('Датасет грузоперевозки - Грузы.csv', encoding=encoding_type)
    
    # Очищаем названия колонок от невидимых пробелов
    for df in [cities, clients, drivers, transport, routes, flights, cargo]:
        df.columns = df.columns.str.strip()
        
    return cities, clients, drivers, transport, routes, flights, cargo

# Загружаем данные в переменные
df_cities, df_clients, df_drivers, df_transport, df_routes, df_flights, df_cargo = load_all_data()


# 3. Боковая панель (Sidebar) с фильтрами (Требование из Части 1, Пункт 10)
st.sidebar.header("Фильтрация данных")

# Выбор города (добавляем вариант "Все города")
city_list = ["Все города"] + list(df_cities['Название_города'].unique())
selected_city = st.sidebar.selectbox("Выберите город присутствия:", city_list)

# Фильтрация клиентов по выбранному городу
if selected_city != "Все города":
    city_id = df_cities[df_cities['Название_города'] == selected_city]['ID_города'].values[0]
    filtered_clients = df_clients[df_clients['ID_города'] == city_id]
    # Фильтруем грузы только этих клиентов
    filtered_cargo = df_cargo[df_cargo['ID_клиента'].isin(filtered_clients['ID_клиента'])]
else:
    filtered_clients = df_clients
    filtered_cargo = df_cargo


# 4. Создание вкладок (Главное требование ТЗ)
tab1, tab2, tab3 = st.tabs([
    "📊 Анализ клиентов и грузов", 
    "🚛 Эффективность логистики", 
    "🌐 География и Финансы"
])


# ==========================================
# ВКЛАДКА 1: АНАЛИЗ КЛИЕНТОВ И ГРУЗОВ
# ==========================================
with tab1:
    st.header("Анализ клиентской базы и типов грузов")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Топ-5 клиентов по стоимости грузов")
        # Агрегируем данные
        top_clients = filtered_cargo.groupby('ID_клиента')['Стоимость_груза'].sum().reset_index()
        top_clients = top_clients.merge(df_clients, on='ID_клиента').sort_values(by='Стоимость_груза', ascending=False).head(5)
        
        # Строим интерактивный график Plotly
        fig_clients = px.bar(
            top_clients, 
            x='Стоимость_груза', 
            y='Название_клиента', 
            orientation='h',
            labels={'Стоимость_груза': 'Сумма (руб.)', 'Название_клиента': 'Клиент'},
            color='Тип_клиента',
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_clients.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_clients, use_container_width=True)
        
    with col2:
        st.subheader("Распределение перевозок по типам грузов")
        cargo_types = filtered_cargo.groupby('Тип_груза')['Вес_тонн'].sum().reset_index()
        
        # Круговая диаграмма
        fig_pie = px.pie(
            cargo_types, 
            values='Вес_тонн', 
            names='Тип_груза',
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        st.plotly_chart(fig_pie, use_container_width=True)


# ==========================================
# ВКЛАДКА 2: ЭФФЕКТИВНОСТЬ ЛОГИСТИКИ
# ==========================================
# ==========================================
# ВКЛАДКА 2: ЭФФЕКТИВНОСТЬ ЛОГИСТИКИ
# ==========================================
with tab2:
    st.header("Показатели работы транспорта и водителей")
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("Средняя стоимость рейса по типам транспорта")
        
        # Склеиваем рейсы и транспорт по ID_транспорта
        transport_eff = df_flights.merge(df_transport, on='ID_транспорта')
        avg_cost = transport_eff.groupby('Тип_транспорта')['Стоимость_рейса'].mean().reset_index()
        
        fig_trans = px.bar(
            avg_cost,
            x='Тип_транспорта',
            y='Стоимость_рейса',
            text_auto='.2s',
            labels={'Стоимость_рейса': 'Ср. стоимость рейса (руб.)', 'Тип_транспорта': 'Тип транспорта'},
            color='Тип_транспорта',
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        st.plotly_chart(fig_trans, use_container_width=True)
        
    with col4:
        st.subheader("Топ-3 водителя по успешным доставкам")
        # Фильтруем только доставленные рейсы
        delivered_flights = df_flights[df_flights['Статус_рейса'] == 'Доставлен']
        
        driver_stats = delivered_flights.groupby('ID_водителя')['ID_рейса'].count().reset_index()
        driver_stats = driver_stats.merge(df_drivers, on='ID_водителя').sort_values(by='ID_рейса', ascending=False).head(3)
        driver_stats['ФИО'] = driver_stats['Имя'] + " " + driver_stats['Фамилия']
        
        fig_drivers = px.bar(
            driver_stats,
            x='ID_рейса',
            y='ФИО',
            orientation='h',
            labels={'ID_рейса': 'Успешные рейсы', 'ФИО': 'Водитель'},
            color='ФИО',
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        fig_drivers.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_drivers, use_container_width=True)

# ==========================================
# ВКЛАДКА 3: ГЕОГРАФИЯ И ФИНАНСЫ
# ==========================================
with tab3:
    st.header("Географическое покрытие и financial результаты")
    
    # 1. Интерактивная карта
    st.subheader("Карта сети городов присутствия компании")
    
    # Очищаем данные для карты: берем ТОЛЬКО координаты и переименовываем в 'lat' и 'lon'
    # Это железобетонный стандарт, который работает абсолютно во всех версиях Streamlit
    map_data = df_cities[['Широта', 'Долгота']].rename(columns={'Широта': 'lat', 'Долгота': 'lon'})
    st.map(map_data, zoom=3)
    
    st.markdown("---")
    
    # 2. Финансовый блок по маршрутам
    st.subheader("Финансовая эффективность маршрутов")
    
    # Создаем словарь для быстрого маппинга: ID_города -> Название_города
    city_mapping = dict(zip(df_cities['ID_города'], df_cities['Название_города']))
    
    # Безопасно подставляем названия городов отправления и назначения
    df_routes_clean = df_routes.copy()
    df_routes_clean['Откуда'] = df_routes_clean['ID_города_отправления'].map(city_mapping)
    df_routes_clean['Куда'] = df_routes_clean['ID_города_назначения'].map(city_mapping)
    df_routes_clean['Маршрут'] = df_routes_clean['Откуда'] + " ➡️ " + df_routes_clean['Куда']
    
    # Объединяем рейсы только с готовыми текстовыми названиями маршрутов
    route_fin = df_flights.merge(df_routes_clean[['ID_маршрута', 'Маршрут']], on='ID_маршрута')
    route_revenue = route_fin.groupby('Маршрут')['Стоимость_рейса'].sum().reset_index().sort_values(by='Стоимость_рейса', ascending=False)
    
    # Строим интерактивный график выручки по направлениям
    fig_routes = px.bar(
        route_revenue,
        x='Стоимость_рейса',
        y='Маршрут',
        orientation='h',
        labels={'Стоимость_рейса': 'Общая выручка (руб.)', 'Маршрут': 'Направление маршрута'},
        color='Стоимость_рейса',
        color_continuous_scale=px.colors.sequential.YlGnBu
    )
    fig_routes.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_routes, use_container_width=True)