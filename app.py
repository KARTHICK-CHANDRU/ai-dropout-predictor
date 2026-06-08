# app.py-oda top-la irukkura imports-ai ipdi check pannunga
import streamlit as st
import pandas as pd
import plotly.express as px
try:
    from fpdf import FPDF
except ImportError:
    st.error("FPDF library missing. Please add 'fpdf' to your requirements.txt")

st.set_page_config(page_title="AI Dropout Predictor", layout="wide")

# --- Functions ---
def generate_pdf(df_high_risk):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="High Risk Student Report", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Name | Risk Status", ln=True)
    for index, row in df_high_risk.iterrows():
        pdf.cell(200, 10, txt=f"{row['Name']} | {row['Risk']}", ln=True)
    return pdf.output(dest='S').encode('latin-1')

def calculate_risk(attendance, marks, backlogs, socio_eco):
    risk_score = (100 - attendance) * 0.4 + (100 - marks) * 0.4 + (backlogs * 5) + (10 - socio_eco) * 2
    if risk_score > 60: return "High Risk"
    elif risk_score > 30: return "Moderate Risk"
    else: return "Low Risk"

def plot_radar(attendance, marks, backlogs, eco):
    df = pd.DataFrame(dict(r=[attendance, marks, backlogs*10, eco*10], theta=['Att', 'Marks', 'Backlogs', 'Eco']))
    fig = px.line_polar(df, r='r', theta='theta', line_close=True)
    st.plotly_chart(fig)

# --- CSS ---
st.markdown("""
    <style>
    .stButton>button {width: 100%; border-radius: 5px; height: 3em; background-color: #007BFF; color: white;}
    </style>
    """, unsafe_allow_html=True)

# --- UI Setup ---
st.title("🎓 Student Academic Intelligence System")
col1, col2, col3 = st.columns(3)
col1.metric("System Status", "Operational")
col2.metric("Version", "1.0.0")
col3.metric("Mode", "Analytics")
st.write("---")

st.subheader("📁 Data Processing Hub")
upload_col, info_col = st.columns([2, 1])

with upload_col:
    uploaded_file = st.file_uploader("Upload Student CSV", type=["csv"])
with info_col:
    st.info("Download our standard template here!")
    template_df = pd.DataFrame(columns=['Name', 'Attendance', 'Marks', 'Backlogs', 'Eco'])
    st.download_button("Download Template", template_df.to_csv(index=False), "template.csv")

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        if df.empty:
            st.error("⚠️ The uploaded file is empty.")
        else:
            df['Risk'] = df.apply(lambda x: calculate_risk(x['Attendance'], x['Marks'], x['Backlogs'], x['Eco']), axis=1)
            st.dataframe(df)
            
            st.markdown("---")
            if st.button("Generate High-Risk Report (PDF)"):
                high_risk_df = df[df['Risk'] == "High Risk"]
                if not high_risk_df.empty:
                    pdf_data = generate_pdf(high_risk_df)
                    st.download_button("Click to Download PDF", pdf_data, "High_Risk_Report.pdf", "application/pdf")
                    st.success("Report Ready!")
                else:
                    st.warning("No High Risk students found.")

            st.markdown("---")
            st.subheader("🔍 View Individual Graph from Batch")
            student_names = df['Name'].tolist()
            selected_student = st.selectbox("Select a student to view their Radar Graph:", student_names)
            student_data = df[df['Name'] == selected_student].iloc[0]
            plot_radar(student_data['Attendance'], student_data['Marks'], student_data['Backlogs'], student_data['Eco'])
            st.write(f"Risk Status for {selected_student}: **{student_data['Risk']}**")
            
            st.markdown("---")
            st.subheader("📊 Multi-Student Comparison")
            compare_students = st.multiselect("Select students to compare:", student_names, default=student_names[:2])
            if compare_students:
                comparison_df = df[df['Name'].isin(compare_students)]
                fig_comp = px.line_polar(
                    comparison_df.melt(id_vars='Name', value_vars=['Attendance', 'Marks', 'Backlogs', 'Eco'], var_name='Metric', value_name='Value'),
                    r='Value', theta='Metric', color='Name', line_close=True
                )
                st.plotly_chart(fig_comp)

    except Exception as e:
        st.error(f"Error reading CSV file: {e}")

# --- Individual Analysis ---
st.markdown("---")
st.subheader("📝 Individual Analysis & History")
col_input, col_result = st.columns(2)
with col_input:
    name = st.text_input("Student Name")
    attendance = st.number_input("Attendance (%)", 0, 100, 85)
    marks = st.number_input("Internal Marks (%)", 0, 100, 75)
    backlogs = st.number_input("Number of Backlogs", 0, 10, 0)
    socio_eco = st.number_input("Socio-Economic Index (1-10)", 1, 10, 5)
with col_result:
    if st.button("Analyze & Save"):
        risk = calculate_risk(attendance, marks, backlogs, socio_eco)
        st.write(f"### Predicted Risk: **{risk}**")
        plot_radar(attendance, marks, backlogs, socio_eco)
        new_record = pd.DataFrame({'Name': [name], 'Risk': [risk]})
        new_record.to_csv("history.csv", mode='a', header=False, index=False)
        st.success("Saved to History!")
