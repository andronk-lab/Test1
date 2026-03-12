import streamlit as st
import plotly.express as px
import pandas as pd

relief_df = pd.read_csv('isla_coralina_relief_operations.csv')
infra_df = pd.read_csv('isla_coralina_infrastructure.csv')

relief_df['date'] = pd.to_datetime(relief_df['date'])
relief_df['fulfillment_rate'] = relief_df['quantity_delivered'] / relief_df['quantity_requested']

st.title("Isla Coralina Relief Operations Monitor")

st.sidebar.header("Filter Results")

all_munis = relief_df['municipality'].unique().tolist()
selected_munis = st.sidebar.multiselect("Select Municipalities:", options=all_munis, default=all_munis)

all_supplies = relief_df['supply_type'].unique().tolist()
selected_supplies = st.sidebar.multiselect("Select Supply Types:", options=all_supplies, default=all_supplies)

filtered_relief = relief_df[
    (relief_df['municipality'].isin(selected_munis)) & 
    (relief_df['supply_type'].isin(selected_supplies))
]
filtered_infra = infra_df[infra_df['municipality'].isin(selected_munis)]

st.subheader(" Current Operational Metrics")

total_pop = filtered_infra['population_served'].sum()
avg_delay = filtered_relief['delivery_delay_hours'].mean()
low_fulfillment_pct = (filtered_relief['fulfillment_rate'] < 0.8).mean() * 100

critical_types = ['Hospital', 'Health Clinic', 'Water Treatment Plant', 'Power Substation']
non_op_critical = filtered_infra[
    (filtered_infra['operational_status'] == 'Non-Operational') & 
    (filtered_infra['facility_type'].isin(critical_types))
]
non_op_count = non_op_critical.groupby('municipality').size().to_dict()

st.write(f"- **Total Population Served:** {total_pop:,}")
st.write(f"- **Average Delivery Delay:** {avg_delay:.2f} hours")
st.write(f"- **Deliveries with < 80% Fulfillment:** {low_fulfillment_pct:.1f}%")

tab1, tab2 = st.tabs(["Infrastructure Status", "Relief Performance"])

with tab1:
    fig1 = px.pie(filtered_infra, names='operational_status', 
                 title="Facility Readiness Overview",
                 color_discrete_map={'Fully Operational':'#00CC96', 'Partially Operational':'#FFA15A', 'Non-Operational':'#EF553B'})
    
   
    fig2 = px.box(filtered_infra, x='municipality', y='damage_severity', 
                 title="Distribution of Damage Severity by Municipality",
                 color='municipality')
    
    col1, col2 = st.columns(2)
    with col1: st.plotly_chart(fig1, use_container_width=True)
    with col2: st.plotly_chart(fig2, use_container_width=True)

with tab2:
    delay_data = filtered_relief.groupby('transport_mode')['delivery_delay_hours'].mean().reset_index()
    fig3 = px.bar(delay_data, x='transport_mode', y='delivery_delay_hours', 
                 title="Average Delay by Transport Mode", color='transport_mode')
    
    
    fig4 = px.histogram(filtered_relief, x='fulfillment_rate', nbins=20,
                       title="Frequency of Fulfillment Rates",
                       labels={'fulfillment_rate': 'Fulfillment Rate (0.0 - 1.0)'})
    
    col3, col4 = st.columns(2)
    with col3: st.plotly_chart(fig3, use_container_width=True)
    with col4: st.plotly_chart(fig4, use_container_width=True)

st.divider()
st.markdown("""
### **Analytical Focus: Operational Briefing**

**What the Data Reveals:** The current operational data suggests a significant strain on the relief pipeline across Isla Coralina. A large portion of deliveries are failing to reach the established 80% fulfillment threshold, indicating that physical barriers are preventing supplies from reaching intended destinations. The average delay for convoys remains high, and when cross-referenced with infrastructure status, it is clear that the hardest-hit municipalities are suffering from a "double-hit" of extreme physical damage and logistical isolation. While some facilities have been restored to partial status, the lack of fully operational critical utilities in coastal sectors continues to slow the overall pace of recovery.

**Actionable Recommendations:**
1. **Prioritize Efficient Delivery:** Because ground and sea routes are showing significant bottlenecks, the incident commander should transition critical medical supplies and water to aerial transport. This is currently the only efficant and reliable way to bypass damaged road networks.
2. **Infrastructure Surge:** Engineering crews must prioritize the restoration of nonoperational critical sites, specifically water treatment plants and power substations. Restoring these hubs is essential to support the broader relief distribution network.
3. **Fulfillment Monitoring:** Coordinators should investigate deliveries falling at the lower end of the fulfillment scale. Specific attention should be paid to whether certain supply types, like heavy shelter materials, are being disproportionately affected by current transport constraints.
""")
