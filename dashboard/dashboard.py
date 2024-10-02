import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go


# Load data
@st.cache_data
def load_data():
    day_df = pd.read_csv('data/day_cleaned.csv')
    hour_df = pd.read_csv('data/hour_cleaned.csv')

    day_df['date'] = pd.to_datetime(day_df['date'])
    hour_df['date'] = pd.to_datetime(hour_df['date'])

    return day_df, hour_df

day_df, hour_df = load_data()


st.title('🚴 Bike Rentals Dashboard')

# Sidebar untuk memilih tahun
year_options = day_df['date'].dt.year.unique()  # Mengambil daftar tahun yang unik
selected_year = st.sidebar.selectbox('Select Year', year_options)

# Filter data berdasarkan tahun yang dipilih
day_df = day_df[day_df['date'].dt.year == selected_year]
hour_df = hour_df[hour_df['date'].dt.year == selected_year]

# 1. Tren penyewaan sepeda harian dan bulanan
st.header('Daily and Monthly Bike Rentals Trend')

# Tren Harian
daily_trend = px.line(day_df, x='date', y='count_total', title='Daily Bike Rentals Trend',
                      labels={'count_total':'Total Bike Rentals'})

# Menghapus judul sumbu X
daily_trend.update_xaxes(title_text='')

st.plotly_chart(daily_trend)

# Tren Bulanan
day_df['month_year'] = day_df['date'].dt.to_period('M')
monthly_trend = day_df.groupby('month_year')['count_total'].sum()
monthly_trend_plot = px.line(monthly_trend, x=monthly_trend.index.astype(str), 
                             y=monthly_trend.values, title='Monthly Bike Rentals Trend',
                             labels={'y':'Total Bike Rentals'})

# Menghapus judul sumbu X
monthly_trend_plot.update_xaxes(title_text='')

st.plotly_chart(monthly_trend_plot)

# 2. Waktu sibuk penyewaan sepeda
st.header('Peak Hour Bike Rentals')

# Fungsi untuk menentukan tipe hari
def get_day_type(row):
    if row['holiday'] == 1:
        return 'Holiday'
    elif row['day'] in ['Sunday', 'Saturday']:  # 0 = Sunday, 6 = Saturday
        return 'Weekend'
    else:
        return 'Working Day'

hour_df['day_type'] = hour_df.apply(get_day_type, axis=1)

total_rentals = hour_df.groupby(['hour', 'day_type'])['count_total'].sum().reset_index()

busy_times = px.line(total_rentals, x='hour', y='count_total', color='day_type', 
                     title='Bike Rentals by Hour: Weekdays vs. Weekends vs. Holidays',
                     labels={'hour': 'Hour', 'count_total': 'Total Bike Rentals', 'day_type': 'Day Type'},
                     color_discrete_map={'Working Day': 'blue', 'Weekend': 'green', 'Holiday': 'red'})
st.plotly_chart(busy_times)

# 3. Pengaruh cuaca terhadap penyewaan sepeda
st.header('The Impact of Weather Conditions on Total Bike Rentals')

weather_impact = px.bar(day_df, x='weather', y='count_total', 
                        title='Distribution of Bike Rentals by Weather Condition',
                        labels={'count_total': 'Total Bike Rentals'})

# Menghapus judul sumbu X
weather_impact.update_xaxes(title_text='')

st.plotly_chart(weather_impact)

# 4. Hubungan suhu dengan penyewaan sepeda
st.header('Correlation between Temperature and Total Bike Rentals')

# Membuat dua kolom untuk layout bersebelahan
col1, col2 = st.columns(2)

with col1:
    st.subheader('Daily Data')
    temp_correlation_daily = px.scatter(day_df, x='temperature', y='count_total', 
                                        labels={'temperature': 'Temperature', 'count_total': 'Total Bike Rentals'},
                                        trendline='ols',
                                        trendline_color_override='red')  # Menambahkan garis tren
    st.plotly_chart(temp_correlation_daily, use_container_width=True)

    # Menghitung korelasi
    correlation_daily = day_df['temperature'].corr(day_df['count_total'])
    st.write(f"Correlation coefficient (daily): {correlation_daily:.2f}")

with col2:
    st.subheader('Hourly Data')
    temp_correlation_hourly = px.scatter(hour_df, x='temperature', y='count_total', 
                                         labels={'temperature': 'Temperature', 'count_total': 'Total Bike Rentals'},
                                         trendline='ols',
                                         trendline_color_override='red')  # Menambahkan garis tren
    st.plotly_chart(temp_correlation_hourly, use_container_width=True)

    # Menghitung korelasi
    correlation_hourly = hour_df['temperature'].corr(hour_df['count_total'])
    st.write(f"Correlation coefficient (hourly): {correlation_hourly:.2f}")

# 5. Penyewaan sepeda berdasarkan musim
st.header('Total Bike Rentals by Season')

season_rentals = px.bar(day_df, x='season', y='count_total', 
                        title='Total Bike Rentals by Season',
                        labels={'count_total': 'Total Bike Rentals'})

# Menghapus judul sumbu X
season_rentals.update_xaxes(title_text='')

st.plotly_chart(season_rentals)

# 6. Distribusi penyewaan antara pengguna biasa dan terdaftar
st.header('Proportion of Total Bike Rentals: Casual Users vs. Registered Users')

# Menghitung jumlah pengguna
labels = ['Casual Users', 'Registered Users']
values = [day_df['casual_users'].sum(), day_df['registered_users'].sum()]

# Membuat donut chart
fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.5, textinfo='label+percent', textposition='outside')])

# Judul dan pengaturan
fig.update_layout(showlegend=False)

# Menampilkan donut chart di Streamlit
st.plotly_chart(fig)

# 7. Tingkat penyewaan pada jam kerja vs di luar jam kerja
st.header('Total Bike Rentals: Working vs. Non-Working Hours')

hour_df['is_working_hour'] = (hour_df['hour'] >= '07') & (hour_df['hour'] <= '17')
# Menghitung total penyewaan untuk jam kerja dan di luar jam kerja
working_hours_rentals = hour_df[hour_df['is_working_hour']]['count_total'].sum()
non_working_hours_rentals = hour_df[~hour_df['is_working_hour']]['count_total'].sum()

# Membuat dataframe untuk visualisasi
comparison_df = pd.DataFrame({
    'Period': ['Working Hour', 'Non-Working Hour'],
    'Total Bike Rentals': [working_hours_rentals, non_working_hours_rentals]
})

# Membuat donut chart
fig = go.Figure(data=[go.Pie(labels=comparison_df['Period'], values=comparison_df['Total Bike Rentals'], 
                               hole=.5, textinfo='label+percent', textposition='outside', showlegend=False)])

# Judul dan pengaturan
fig.update_layout(title_text="Proportion of Total Bike Rentals: Working vs. Non-Working Hours")

# Menampilkan donut chart di Streamlit
st.plotly_chart(fig)


# Visualisasi distribusi penyewaan per jam
hourly_rentals = hour_df.groupby('hour')['count_total'].sum().reset_index()
hourly_fig = px.line(hourly_rentals, x='hour', y='count_total', 
                     title='Total Bike Rentals by Hour',
                     labels={'hour': 'Hour', 'count_total': 'Total Bike Rentals'})

# Menambahkan area yang diarsir untuk jam kerja
hourly_fig.add_vrect(x0=7, x1=17, 
                     fillcolor="LightSalmon", opacity=0.7, 
                     layer="below", line_width=0,
                     annotation_text="Working Hour", annotation_position="top left")

st.plotly_chart(hourly_fig)