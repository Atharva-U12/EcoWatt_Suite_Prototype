import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.express as px

# APP CONFIGURATION

st.set_page_config(
    page_title="EcoWatt Suite ⚡",
    layout="wide",
    page_icon="⚡"
)

st.title("⚡ EcoWatt Suite")
st.subheader("A Non-AI Based Electricity Consumption and Cost Analyzer")

st.sidebar.title("🔧 Navigation Panel")
app_mode = st.sidebar.radio("Select Module", ["🏠 EcoWatt Homes", "🏬 EcoWatt Shops", "🏢 EcoWatt Offices",'EcoWatt Simulator'])


# COMMON UTILITY FUNCTIONS

def get_appliance_recommendations(module, user_inputs):
    """Generate appliance-specific recommendations based on usage patterns."""
    recs = []

    if module == "🏠 EcoWatt Homes":
        if user_inputs["Monthly_AC_Usage_Hours"] > 150:
            recs.append("❄️ **AC:** Clean filters regularly and maintain 24°C for better efficiency.")
        if user_inputs["Refrigerator_Type"] != "None" and user_inputs["Monthly_Refrigerator_Usage_Hours"] > 160:
            recs.append("🧊 **Refrigerator:** Ensure good ventilation and avoid frequent door openings.")
        if user_inputs["Monthly_TV_Usage_Hours"] > 100:
            recs.append("📺 **TV:** Turn off completely instead of standby to save energy.")
        if user_inputs["Monthly_Geyser_Usage_Minutes"] > 300:
            recs.append("🚿 **Geyser:** Install a timer to limit unnecessary heating time.")
        if user_inputs["Monthly_Washing_Machine_Usage_Cycles"] > 20:
            recs.append("👕 **Washing Machine:** Use full loads and prefer cold water cycles.")

    elif module == "🏬 EcoWatt Shops":
        if user_inputs["Monthly_AC_Usage_Hours"] > 200:
            recs.append("❄️ **AC:** Maintain 24–26°C and clean filters weekly for optimal performance.")
        if user_inputs["Monthly_Refrigerator_Usage_Hours_Type_1"] > 250:
            recs.append("🧊 **Refrigerator_Type_1:** Defrost regularly and keep 6 inches away from walls.")
        if user_inputs["Monthly_Refrigerator_Usage_Hours_Type_2"] > 250:
            recs.append("🧊 **Refrigerator_Type_2:** Defrost regularly and keep 6 inches away from walls.")
        if user_inputs["Monthly_Light_Usage_Hours"] > 250:
            recs.append("💡 **Lighting:** Replace old bulbs with LEDs or motion sensors.")
        if user_inputs["Monthly_PC_Usage_Hours"] > 200:
            recs.append("🖥️ **Billing PC:** Enable sleep mode and shut down after hours.")

    elif module == "🏢 EcoWatt Offices":
        if user_inputs["Monthly_AC_Usage_Hours"] > 300:
            recs.append("❄️ **AC:** Use centralized scheduling or smart thermostats.")
        if user_inputs["Monthly_Lights_Usage_Hours"] > 300:
            recs.append("💡 **Lighting:** Utilize daylight and motion-based lighting.")
        if user_inputs["Monthly_PC_Usage_Hours"] > 400:
            recs.append("💻 **Computers:** Enable sleep mode after 10 minutes of inactivity.")
        if user_inputs["Monthly_Printer_Usage_Minutes"] > 500:
            recs.append("🖨️ **Printer:** Use duplex printing and turn off when idle.")
        if user_inputs["Monthly_Projector_Usage_Hours"] > 100:
            recs.append("📽️ **Projector:** Use Eco Mode and power off when not needed.")

    if not recs:
        recs.append("🌿 Your energy usage looks efficient across all appliances. Great job!")

    return recs


def aggregate_weekly_to_monthly_Homes(df):
    """
    Convert weekly data to monthly data by multiplying selected columns by 4.3
    This avoids affecting non-relevant numeric columns.
    """
    df_monthly = df.copy()

    #Specify only the usage columns that should be scaled
    cols_to_multiply = [
        "Monthly_AC_Usage_Hours",
        "Monthly_Fan_Usage_Hours",
        'Refrigerator_Usage_Hrs_Monthly',
        "Monthly_TV_Usage_Hours",
        "Monthly_Geyser_Usage_Minutes",
        "Monthly_Washing_Machine_Usage_Cycles"
    ]

    # Multiply the selected columns by 4.5
    df_monthly[cols_to_multiply] = df_monthly[cols_to_multiply] * 4.3

    return df_monthly


def aggregate_weekly_to_monthly_Shops(df):
    """
    Convert weekly data to monthly data by multiplying selected columns by 4.3
    This avoids affecting non-relevant numeric columns.
    """
    df_monthly = df.copy()

    # Specify only the usage columns that should be scaled
    cols_to_multiply = [
            'Avg_Working_Hours_Monthly',
            'Monthly_AC_Usage_Hours',
            'Monthly_Fan_Usage_Hours',
            'Monthly_Refrigerator_Usage_Hours_Type_1',
            'Monthly_Refrigerator_Usage_Hours_Type_2',
            'Monthly_Lights_Usage_Hours',
            'Monthly_PC_Usage_Hours'
    ]

    # Multiply the selected columns by 4
    df_monthly[cols_to_multiply] = df_monthly[cols_to_multiply] * 4.3

    return df_monthly

def aggregate_weekly_to_monthly_Offices(df):
    """
    Convert weekly data to monthly data by multiplying selected columns by 4.3
    This avoids affecting non-relevant numeric columns.
    """
    df_monthly = df.copy()

    #Specify only the usage columns that should be scaled
    cols_to_multiply = [
       "Avg_Working_Hours_Monthly",
       "Monthly_AC_Usage_Hours",
       "Monthly_Fan_Usage_Hours",
       "Monthly_Lights_Usage_Hours",
       "Monthly_PC_Usage_Hours",
       "Monthly_Refrigerator_Usage_Hours",
       "Monthly_Printer_Usage_Minutes",
       "Monthly_Projector_Usage_Hours"
    ]

    # Multiply the selected columns by 4
    df_monthly[cols_to_multiply] = df_monthly[cols_to_multiply] * 4.3

    return df_monthly


def rule_based_cost_calculator(kwh):
    rate = 0
    cost = 0

    if State == "Maharashtra":
        if kwh <= 100:
            rate = 6.5
        elif kwh <= 300:
            rate = 8.2
        else:
            rate = 10.5

    elif State == "Gujarat":
        if kwh <= 100:
            rate = 6.0
        elif kwh <= 300:
            rate = 7.8
        else:
            rate = 9.8

    elif State == "Karnataka":
        if kwh <= 100:
            rate = 5.8
        elif kwh <= 300:
            rate = 7.5
        else:
            rate = 9.2

    elif State == "Tamil Nadu":
        if kwh <= 100:
            rate = 5.5
        elif kwh <= 300:
            rate = 7.0
        else:
            rate = 8.8

    elif State == "Delhi":
        if kwh <= 100:
            rate = 5.2
        elif kwh <= 300:
            rate = 6.8
        else:
            rate = 8.5

    elif State == "West Bengal":
        if kwh <= 100:
            rate = 6.0
        elif kwh <= 300:
            rate = 7.5
        else:
            rate = 9.0

    else:  # 'Others'
        if kwh <= 100:
            rate = 6.0
        elif kwh <= 300:
            rate = 7.5
        else:
            rate = 9.5

    cost = kwh * rate
    fixed_charge = 120
    total_cost = round(cost + fixed_charge, 2)

    return total_cost

def rule_based_cost_calculator_LT_2(kwh):
    rate = 0
    cost = 0

    if State == "Maharashtra":
        if kwh <= 100:
            rate = 8.5
        elif kwh <= 300:
            rate = 10.0
        else:
            rate = 12.0

    elif State == "Gujarat":
        if kwh <= 100:
            rate = 8.0
        elif kwh <= 300:
            rate = 9.5
        else:
            rate = 11.0

    elif State == "Karnataka":
        if kwh <= 100:
            rate = 7.8
        elif kwh <= 300:
            rate = 9.0
        else:
            rate = 10.5

    elif State == "Tamil Nadu":
        if kwh <= 100:
            rate = 7.5
        elif kwh <= 300:
            rate = 8.8
        else:
            rate = 10.0

    elif State == "Delhi":
        if kwh <= 100:
            rate = 7.2
        elif kwh <= 300:
            rate = 8.5
        else:
            rate = 9.8

    elif State == "West Bengal":
        if kwh <= 100:
            rate = 7.8
        elif kwh <= 300:
            rate = 9.0
        else:
            rate = 10.8

    else:  # 'Others'
        if kwh <= 100:
            rate = 8.0
        elif kwh <= 300:
            rate = 9.2
        else:
            rate = 11.0

    # Cost calculation
    cost = kwh * rate
    fixed_charge = 200  # Commercial connections generally have higher base charge
    total_cost = round(cost + fixed_charge, 2)

    return total_cost


def show_recommendations(usage_type):
    """Provide personalized recommendations."""
    if usage_type == "Low Usage":
        return "✅ Great job! Keep maintaining your efficient energy usage."
    elif usage_type == "Medium Usage":
        return "⚠️ Moderate consumption. Try using appliances more efficiently."
    else:
        return "🚨 High energy consumption! Consider using power-saving devices or scheduling usage."



# MODULES

if app_mode == "🏠 EcoWatt Homes":
    st.header("EcoWatt Homes 🏠")

    st.write("### Enter your appliance usage details below:")

    State = st.selectbox("Choose Your State ??",['Delhi', 'Gujarat', 'Maharashtra', 'Karnataka', 'Tamil Nadu',"West Bengal","Others"])
    City = st.selectbox("Choose Your City ??",['Mumbai', 'Bengaluru', 'Ahmedabad', 'Chennai', 'Delhi', 'Pune',"Kolkata","Others"])
    Weather = st.selectbox("Choose the Weather ??",['Monsoon', 'Summer', 'Winter'])
    Number_of_Residents = st.number_input("Enter the Number of Residents in your House ??",min_value = 0)
    Home_Type = st.selectbox("Choose Your Home Type ??",['Apartment', 'Row House', 'Bungalow'])
    Electricity_Tariff_Type = st.selectbox("Choose Your Electricity Tariff Type ??",['LT-1'])
    AC_Type = st.selectbox("Choose Your AC Type ??",['None', 'Split AC', 'Window AC',"Inverter AC"])
    Monthly_AC_Usage_Hours = st.number_input("For How Many Hours You Use AC in a Combined manner on a Weekly Basis ??",min_value = 0)
    Fan_Type = st.selectbox("Choose Your Fan Type ?? ",['Crompton', 'Bajaj', 'Polycab', 'Havells', 'None'])
    Monthly_Fan_Usage_Hours = st.number_input("For How many Hours You use Fan in a Combined manner on a Weekly Basis ??",min_value=0)
    Refrigerator_Type = st.selectbox("Choose Your Refrgerator Type ??",['Double Door 3★', 'Double Door 4★', 'Side-by-Side 5★', 'None','Single Door 5★', 'Side-by-Side 4★', 'Single Door 4★','Single Door 3★', 'Double Door 5★'])
    Monthly_Refrigerator_Usage_Hours = st.number_input("For How many hours you use Refrigerator on a weekly basis ??",min_value = 0 )
    TV_Type = st.selectbox("Choose your TV Type ??",['LCD', 'SmartTV', 'LED', 'None'])
    Monthly_TV_Usage_Hours = st.number_input("For how many hours you use TV on a weekly basis ??",min_value=0)
    Geyser_Type = st.selectbox("Choose your Geyser Type ??",['15-25L', '30+L', 'None', '6-10L'])
    Monthly_Geyser_Usage_Minutes = st.number_input("For how many minutes you use geyser on a weekly basis ??",min_value=0)
    Washing_Machine_Type = st.selectbox("Choose your washing machine Type ??",['12kg', '6kg', '7kg', '8kg', 'None', '10kg'])
    Monthly_Washing_Machine_Usage_Cycles = st.number_input("How many Washing Machine usage cycles you have weekly ??",min_value=0)
    Washing_Machine_Age = st.selectbox("Choose your washing machine age category ?? (New -> 1-3yrs) (Mid -> 4-7yrs) (old -> 7+yrs)",['Mid', 'New', 'Old', 'None'])
    
    
    if st.button("🔍 Analyze Usage"):
        User_data = pd.DataFrame({
               
               'State':[State],
               "City" :[City],
               "Weather/Season":[Weather],
               "No_Of_Residents":[Number_of_Residents],
               "Home_Type":[Home_Type],
               "Electricity_Tariff_Type":[Electricity_Tariff_Type],
               "AC_Type":[AC_Type],
               "Monthly_AC_Usage_Hours":[Monthly_AC_Usage_Hours],
               "Fan_Type":[Fan_Type],
               "Monthly_Fan_Usage_Hours":[Monthly_Fan_Usage_Hours],
               "Refrigerator_Type":[Refrigerator_Type],
               'Refrigerator_Usage_Hrs_Monthly':[Monthly_Refrigerator_Usage_Hours],
               "TV_Type":[TV_Type],
               "Monthly_TV_Usage_Hours":[Monthly_TV_Usage_Hours],
               "Geyser_Type":[Geyser_Type],
               "Monthly_Geyser_Usage_Minutes":[Monthly_Geyser_Usage_Minutes],
               "Washing_Machine_Type":[Washing_Machine_Type],
               "Monthly_Washing_Machine_Usage_Cycles":[Monthly_Washing_Machine_Usage_Cycles],
               "Washing_Machine_Age":[Washing_Machine_Age]
 })



        # Step 1: Aggregate Weekly -> Monthly
        monthly_data = aggregate_weekly_to_monthly_Homes(User_data)

        # Step 2: Predict kWh using regression model
        model_reg = joblib.load(r"C:\Users\Atharva Uttekar\Desktop\EcoWatt Prototype\Models\Best_Model_EcoWatt_Homes (1).pkl")
        preprocessor_reg = joblib.load(r"C:\Users\Atharva Uttekar\Desktop\EcoWatt Prototype\Preprocessing_Models\Preprocessing_EcoWatt_Homes (1).pkl")
        transformed_data = preprocessor_reg.transform(monthly_data)
        kwh_pred = model_reg.predict(transformed_data)[0]
    
        # Step 3: Cost Calculation
        st.info(f" 🔋 Estimated Monthly kWh Consumption is: {round(kwh_pred)} units")
        cost_est = rule_based_cost_calculator(kwh_pred)
        st.info(f"💰 Estimated Monthly Cost: ₹ {cost_est}")

        # Step 4: Classification (Usage Type)
        if kwh_pred < 180 :
            usage_type = "Low Usage"
        elif kwh_pred < 300 :
            usage_type = "Medium Usage"
        else:
            usage_type = "High Usage"

        st.write(f"🏷️ Usage Category: **{usage_type}**")
        st.write(show_recommendations(usage_type))

         # Step 5: Recommendations (AFTER cost evaluation)
    st.info("### 🌟 Personalized Appliance Recommendations:")
    appliance_recs = get_appliance_recommendations("🏠 EcoWatt Homes", {
        "Monthly_AC_Usage_Hours": Monthly_AC_Usage_Hours,
        "Refrigerator_Type": Refrigerator_Type,
        "Monthly_Refrigerator_Usage_Hours": Monthly_Refrigerator_Usage_Hours,
        "Monthly_TV_Usage_Hours": Monthly_TV_Usage_Hours,
        "Monthly_Geyser_Usage_Minutes": Monthly_Geyser_Usage_Minutes,
        "Monthly_Washing_Machine_Usage_Cycles": Monthly_Washing_Machine_Usage_Cycles
         })
    for rec in appliance_recs:
        st.write("-", rec)


       
# ADD MODULES FOR SHOPS & OFFICES

elif app_mode == "🏬 EcoWatt Shops":
    st.header("EcoWatt - Commercial Entities 🏬")
    st.write("### Enter your appliance usage details below:")
   
    State = st.selectbox("Choose Your State ??",['Maharashtra', 'Others', 'Delhi', 'West Bengal', 'Karnataka','Tamil Nadu', 'Gujarat'])
    City = st.selectbox("Choose Your City ??",['Kolhapur', 'Others', 'Mumbai', 'Pune', 'Bengaluru', 'Aurangabad','Nagpur', 'Chennai', 'Solapur', 'Delhi', 'Ahmedabad', 'Kolkata','Nashik'])
    Weather = st.selectbox("Choose the Weather ??",['Monsoon', 'Summer', 'Winter'])
    Shop_Type = st.selectbox("Choose Your Type Of Shop ??",['Bakery/SweetShop', 'Medicals', 'Clothing/Footwear', 'Grocery'])
    Shop_Scale = st.selectbox("Choose Your Shop Scale ??",['Large', 'Small', 'Medium'])
    Electricity_Tariff_Type = st.selectbox("Choose Your Electricity Tariff Type ??",['LT-2'])
    Avg_Working_Hours_Monthly = st.number_input("Enter Your Weekly working Hours ??",min_value = 0)
    No_of_AC = st.number_input("Enter the No.of AC you have in your Shop ??",min_value = 0)
    AC_Type = st.selectbox("Choose Your AC Type ??",['Split AC', 'None', 'Window AC', 'Inverter AC'])
    Monthly_AC_Usage_Hours = st.number_input("For How Many Hours You Use AC on a Weekly Basis ??",min_value = 0)
    No_of_Fans = st.number_input("Enter the No.of Fan you have in your Shop ??",min_value = 0)
    Fan_Type = st.selectbox("Choose Your Fan Type ??",['Crompton', 'Bajaj', 'Havells', 'None', 'Polycab'])
    Monthly_Fan_Usage_Hours = st.number_input("For How Many Hours You Use Fan on a Weekly Basis ??",min_value = 0)
    No_of_Refrigerators_Type_1 = st.number_input("Enter the No.of Refrigerator_Type_1 You have in Your Shop ??",min_value = 0)
    Refrigerator_Type_1 = st.selectbox("Choose Your Refrgerator Type ??",['Display Cooler (Double Door)', 'None','Display Cooler (Single Door)'])
    Monthly_Refrigerator_Usage_Hours_Type_1 = st.number_input("For How many hours you use Refrigerator_Type_1 on a weekly basis ??",min_value = 0 )
    No_of_Refrigerators_Type_2 = st.number_input("Enter the No.of Refrigerator_Type_2 You have in Your Shop ??",min_value = 0)
    Refrigerator_Type_2 = st.selectbox("Choose Your Refrgerator Type ??",['Deep Freezer (Single Lid)', 'Deep Freezer (Double Lid)', 'None'])
    Monthly_Refrigerator_Usage_Hours_Type_2 = st.number_input("For How many hours you use Refrigerator_Type_2 on a weekly basis ??",min_value = 0 )
    No_of_Lights = st.number_input("Enter the No.of Lights You Have in your Shop ??", min_value = 0)
    Light_Type = st.selectbox("Choose your Light Type ??",['Tube Light', 'LED', 'CFL'])
    Monthly_Light_Usage_Hours = st.number_input("For how many hours you use Light on a weekly basis ??",min_value=0)
    PC_Type = st.selectbox("Choose your PC Type ??",['HP', 'Dell', 'None', 'Lenovo'])
    Monthly_PC_Usage_Hours = st.number_input("For how many Hours you use PC/Billing_System on a weekly basis ??",min_value=0)



    if st.button("🔍 Analyze Usage"):
        user_data = pd.DataFrame({
               'State':[State],
               "City" :[City],
               "Weather/Season":[Weather],
               "Shop_Type":[Shop_Type],
               "Shop_Scale":[Shop_Scale],
               "Electricity_Tariff_Type":[Electricity_Tariff_Type],
               "Avg_Working_Hours_Monthly":[Avg_Working_Hours_Monthly],
               "No_of_AC":[No_of_AC],
               "AC_Type":[AC_Type],
               "Monthly_AC_Usage_Hours":[Monthly_AC_Usage_Hours],
               "No_of_Fans":[No_of_Fans],
               "Fan_Type":[Fan_Type],
               "Monthly_Fan_Usage_Hours":[Monthly_Fan_Usage_Hours],
               "No_of_Refrigerators_Type_1":[No_of_Refrigerators_Type_1],
               "Refrigerator_Type_1":[Refrigerator_Type_1],
               "Monthly_Refrigerator_Usage_Hours_Type_1":[Monthly_Refrigerator_Usage_Hours_Type_1],
               "No_of_Refrigerators_Type_2":[No_of_Refrigerators_Type_2],
               "Refrigerator_Type_2":[Refrigerator_Type_2],
               "Monthly_Refrigerator_Usage_Hours_Type_2":[Monthly_Refrigerator_Usage_Hours_Type_2],
               "No_of_Lights":[No_of_Lights],
               "Lights_Type":[Light_Type],
               "Monthly_Lights_Usage_Hours":[Monthly_Light_Usage_Hours],
               "Billing_System/PC_Type":[PC_Type],
               "Monthly_PC_Usage_Hours":[Monthly_PC_Usage_Hours]
 })



        # Step 1: Aggregate Weekly -> Monthly
        monthly_data = aggregate_weekly_to_monthly_Shops(user_data)

        # Step 2: Predict kWh using regression model
        model_reg = joblib.load(r"C:\Users\Atharva Uttekar\Desktop\EcoWatt Prototype\Models\Best_Model_EcoWatt_Shops.pkl")
        preprocessor_reg = joblib.load(r"C:\Users\Atharva Uttekar\Desktop\EcoWatt Prototype\Preprocessing_Models\Preprocessing_EcoWatt_Shops.pkl")
        transformed_data = preprocessor_reg.transform(monthly_data)
        kwh_pred = model_reg.predict(transformed_data)[0]

        # Step 3: Cost Calculation
        st.info(f" 🔋 Estimated Monthly kWh Consumption is: {round(kwh_pred)} units")
        cost_est = rule_based_cost_calculator_LT_2(kwh_pred)
        st.info(f"💰 Estimated Monthly Cost: ₹ {cost_est}")

        # Step 4: Classification (Usage Type)
        if kwh_pred < 350 :
            usage_type = "Low Usage"
        elif kwh_pred < 600 :
            usage_type = "Medium Usage"
        else:
            usage_type = "High Usage"

        st.write(f"🏷️ Usage Category: **{usage_type}**")
        st.write(show_recommendations(usage_type))


        # Step 4: Recommendations (AFTER cost evaluation)
    st.info("### 🌟 Appliance Efficiency Tips:")
    shop_recs = get_appliance_recommendations("🏬 EcoWatt Shops", {
        "Monthly_AC_Usage_Hours": Monthly_AC_Usage_Hours,
        "Monthly_Refrigerator_Usage_Hours_Type_1": Monthly_Refrigerator_Usage_Hours_Type_1,
        "Monthly_Refrigerator_Usage_Hours_Type_2": Monthly_Refrigerator_Usage_Hours_Type_2,
        "Monthly_Light_Usage_Hours": Monthly_Light_Usage_Hours,
        "Monthly_PC_Usage_Hours": Monthly_PC_Usage_Hours
    })
    for rec in shop_recs:
        st.write("-", rec)


elif app_mode == "🏢 EcoWatt Offices":
    st.header("EcoWatt Offices 🏢")
    st.write("### Enter your appliance usage details below:")
   
    State = st.selectbox("Choose Your State ??",['Delhi', 'Karnataka', 'Gujarat', 'Maharashtra', 'Others','Tamil Nadu',"West Bengal"])
    City = st.selectbox("Choose Your City ??",['New Delhi', 'Mysuru', 'Surat', 'Pune', 'Others', 'Ahmedabad','Bengaluru', 'Nagpur', 'Mumbai', 'Coimbatore', 'Chennai',"Kolkata"])
    Weather = st.selectbox("Choose the Weather ??",['Winter', 'Summer', 'Monsoon'])
    Office_Type = st.selectbox("Choose Your Office Type ??",['Startup', 'IT/Corporate', 'Government_Office'])
    Office_Scale = st.selectbox("Choose Your Office Scale ??",['Medium', 'Small', 'Large'])
    Electricity_Tariff_Type = st.selectbox("Choose Your Electricity Tariff Type ??",['LT-2 (Commercial)'])
    Avg_Working_Hours_Monthly = st.number_input("Enter Your Weekly working Hours ??",min_value = 0)
    No_of_AC = st.number_input("Enter the No.of ACs you have in your Office ??",min_value = 0)
    AC_Type = st.selectbox("Choose Your AC Type ??",['Split AC', 'Inverter AC', 'Window AC', 'None'])
    Monthly_AC_Usage_Hours = st.number_input("For How Many Hours You Use AC on a Weekly Basis ??",min_value = 0)
    No_of_Fan = st.number_input("Enter the No.of Fans you have in your Office ??",min_value = 0)
    Fan_Type = st.selectbox("Choose Your Fan Type ??",['Bajaj', 'Crompton', 'Havells', 'None', 'Polycab'])
    Monthly_Fan_Usage_Hours = st.number_input("For How Many Hours You Use Fan on a Weekly Basis ??",min_value = 0)
    No_Of_Lights = st.number_input("Enter How Many Lights you have in Your Office ??",min_value = 0)
    Lights_Type = st.selectbox("Choose the Type of Light ??",['CFL', 'LED', 'Tube Light'])
    Monthly_Lights_Usage_Hours = st.number_input("For How Many Hours You use Lights On a Weekly Basis ??" , min_value=0)
    No_Of_PCs = st.number_input("Enter the No.of PCs You have in Your Office ??",min_value = 0)
    PC_Type = st.selectbox("Choose Your PCs Type ??",['Laptop', 'Desktop'])
    Monthly_PCs_Usage_Hours = st.number_input("For How many hours you use PCs on a weekly basis ??",min_value = 0 )
    No_Of_Refrigerators = st.number_input("Enter the No.of Refrigerators You Have in your Office ??", min_value = 0)
    Refrigerators_Type = st.selectbox("Choose your Refrigerator Type ??",['Double Door 3★', 'Double Door 4★', 'Side-by-Side 5★', 'None','Single Door 5★', 'Side-by-Side 4★', 'Single Door 4★','Single Door 3★', 'Double Door 5★'])
    Monthly_Refrigerator_Usage_Hours = st.number_input("For how many hours you use Refrigerator on a weekly basis ??",min_value=0)
    No_Of_Printers = st.number_input("How many Printer You have in your Office ??",min_value = 0)
    Printer_Type = st.selectbox("Choose the Printer Type ??",['Sony', 'HP', 'Canon'])
    Monthly_Printer_Usage_Minutes = st.number_input("For how many Minutes You Use Printers on a weekly basis ??",min_value=0)
    No_Of_Projectors = st.number_input("Enter the No.Of Projectors You Have in your Office ??",min_value = 0)
    Projector_Type = st.selectbox("Choose Projector Type ??",['Sony', 'Epson'])
    Monthly_Projector_Usage_Hours = st.number_input("For How many Hours You use Projector in your Office On a Weekly Basis ??",min_value=0)



    if st.button("🔍 Analyze Usage"):
        user_data = pd.DataFrame({
               'State':[State],
               "City" :[City],
               "Weather/Season":[Weather],
               "Office_Type":[Office_Type],
               "Office_Scale":[Office_Scale],
               "Electricity_Tariff_Type":[Electricity_Tariff_Type],
               "Avg_Working_Hours_Monthly":[Avg_Working_Hours_Monthly],
               "No_Of_ACs":[No_of_AC],
               "AC_Type":[AC_Type],
               "Monthly_AC_Usage_Hours":[Monthly_AC_Usage_Hours],
               "No_Of_Fans":[No_of_Fan],
               "Fan_Type":[Fan_Type],
               "Monthly_Fan_Usage_Hours":[Monthly_Fan_Usage_Hours],
               "No_Of_Lights":[No_Of_Lights],
               "Lights_Type":[Lights_Type],
               "Monthly_Lights_Usage_Hours":[Monthly_Lights_Usage_Hours],
               "No_Of_PCs":[No_Of_PCs],
               "PC_Type":[PC_Type],
               "Monthly_PC_Usage_Hours":[Monthly_PCs_Usage_Hours],
               "No_Of_Refrigerators":[No_Of_Refrigerators],
               "Refrigerator_Type":[Refrigerators_Type],
               "Monthly_Refrigerator_Usage_Hours":[Monthly_Refrigerator_Usage_Hours],
               "No_Of_Printers":[No_Of_Printers],
               "Printer_Type":[Printer_Type],
               "Monthly_Printer_Usage_Minutes":[Monthly_Printer_Usage_Minutes],
               "No_Of_Projectors":[No_Of_Projectors],
               "Projector_Type":[Projector_Type],
               "Monthly_Projector_Usage_Hours":[Monthly_Projector_Usage_Hours]
 })



        # Step 1: Aggregate Weekly -> Monthly
        monthly_data = aggregate_weekly_to_monthly_Offices(user_data)

        # Step 2: Predict kWh using regression model
        model_reg = joblib.load(r"C:\Users\Atharva Uttekar\Desktop\EcoWatt Prototype\Models\Best_Model_EcoWatt_Office.pkl")
        preprocessor_reg = joblib.load(r"C:\Users\Atharva Uttekar\Desktop\EcoWatt Prototype\Preprocessing_Models\Preprocessing_EcoWatt_Office.pkl")
        transformed_data = preprocessor_reg.transform(monthly_data)
        kwh_pred = model_reg.predict(transformed_data)[0]

        # Simulated prediction for demo
        kwh_pred = np.random.uniform(100, 600)
        st.success(f"🔋 Estimated Monthly Consumption: {kwh_pred:.2f} kWh")

        # Step 3: Cost Calculation
        st.info(f" 🔋 Estimated Monthly kWh Consumption is: {round(kwh_pred)} units")
        cost_est = rule_based_cost_calculator_LT_2(kwh_pred)
        st.info(f"💰 Estimated Monthly Cost: ₹ {cost_est}")

        # Step 4: Classification (Usage Type)
        if kwh_pred < 800 :
            usage_type = "Low Usage"
        elif kwh_pred < 1600 :
            usage_type = "Medium Usage"
        else:
            usage_type = "High Usage"

        st.write(f"🏷️ Usage Category: **{usage_type}**")
        st.write(show_recommendations(usage_type))

        # Step 4: Recommendations (AFTER cost evaluation)
    st.info("### 🌟 Appliance Efficiency Insights:")
    office_recs = get_appliance_recommendations("🏢 EcoWatt Offices", {
        "Monthly_AC_Usage_Hours": Monthly_AC_Usage_Hours,
        "Monthly_Lights_Usage_Hours": Monthly_Lights_Usage_Hours,
        "Monthly_PC_Usage_Hours": Monthly_PCs_Usage_Hours,
        "Monthly_Printer_Usage_Minutes": Monthly_Printer_Usage_Minutes,
        "Monthly_Projector_Usage_Hours": Monthly_Projector_Usage_Hours
    })
    for rec in office_recs:
        st.write("-", rec)


elif app_mode =="EcoWatt Simulator":
    st.write("Use this simulator to explore how your monthly cost changes with different consumption levels.")

    st.sidebar.markdown("---")
    st.sidebar.subheader("⚙️ Consumption Controls")

    # Base electricity rate (₹ per kWh)
    base_rate = 8.5   # Change as per LT-2 or other tariff type

    # Sidebar slider for user input
    kwh_input = st.sidebar.slider(
        "Adjust your Monthly Consumption (in kWh):",
        min_value=50,
        max_value=1000,
        value=300,
        step=10,
        help="Slide to see how cost changes with usage."
    )

    # Cost calculation
    fixed_charge = 100  # Optional fixed charge per month
    cost = kwh_input * base_rate + fixed_charge

    # Visualization in main area
    st.markdown("### 📊 Monthly Cost Simulation")
    st.write("This chart shows how your electricity cost increases with higher consumption.")

    import plotly.express as px

    # Create data for visualization
    kwh_values = list(range(50, 1001, 50))
    cost_values = [kwh * base_rate + fixed_charge for kwh in kwh_values]

    # Plot the line chart
    fig = px.line(
        x=kwh_values,
        y=cost_values,
        title="Electricity Cost vs. Consumption",
        labels={"x": "Consumption (kWh)", "y": "Monthly Cost (₹)"},
        markers=True
    )

    # Highlight selected point
    fig.add_scatter(
        x=[kwh_input],
        y=[cost],
        mode='markers+text',
        text=[f"₹{cost:,.0f}"],
        textposition="top center",
        marker=dict(size=12, color='orange', symbol='circle')
    )

    st.plotly_chart(fig, use_container_width=True)

# Display result
    st.markdown(f"### 💰 Estimated Monthly Cost: *₹ {cost:,.2f}*")

