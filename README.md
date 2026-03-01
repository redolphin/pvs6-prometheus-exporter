# PVS6 Prometheus Exporter

You can find detail information from [SunStrong pypvs](https://github.com/SunStrong-Management/pypvs) repo.

## Installation
```
export PVS6_IP=192.168.1.100
export PVS6_SN=ZN1234567890
export POLLING_INTERVAL=30
export EXPORTER_PORT=8000

docker run -d --name pvs6-exporter -e PVS6_IP=192.168.1.100 -e PVS6-SN=ZN1234567890 -p 8000:8000 redolphin/pvs6-prometheus-exporter:latest 
```

## Prometheus metrics
```
meter_power_kw = Gauge('pvs_meter_power_3ph_kw', '3-phase power in kW', ['serial_number'])
meter_voltage_v = Gauge('pvs_meter_voltage_3ph_v', '3-phase voltage in V', ['serial_number'])
meter_current_a = Gauge('pvs_meter_current_3ph_a', '3-phase current in A', ['serial_number'])
meter_freq_hz = Gauge('pvs_meter_frequency_hz', 'Frequency in Hz', ['serial_number'])
meter_lte_kwh = Gauge('pvs_meter_lte_3ph_kwh', 'LTE 3-phase kWh', ['serial_number'])
meter_ct_scale = Gauge('pvs_meter_ct_scale_factor', 'CT scale factor', ['serial_number'])
meter_i1_a = Gauge('pvs_meter_i1_a', 'Current I1 in A', ['serial_number'])
meter_i2_a = Gauge('pvs_meter_i2_a', 'Current I2 in A', ['serial_number'])
meter_neg_lte_kwh = Gauge('pvs_meter_neg_lte_kwh', 'Negative LTE kWh', ['serial_number'])
meter_net_lte_kwh = Gauge('pvs_meter_net_lte_kwh', 'Net LTE kWh', ['serial_number'])
meter_p1_kw = Gauge('pvs_meter_p1_kw', 'Power P1 in kW', ['serial_number'])
meter_p2_kw = Gauge('pvs_meter_p2_kw', 'Power P2 in kW', ['serial_number'])
meter_pos_lte_kwh = Gauge('pvs_meter_pos_lte_kwh', 'Positive LTE kWh', ['serial_number'])
meter_q3phsum_kvar = Gauge('pvs_meter_q3phsum_kvar', '3-phase reactive power in kVAR', ['serial_number'])
meter_s3phsum_kva = Gauge('pvs_meter_s3phsum_kva', '3-phase apparent power in kVA', ['serial_number'])
meter_tot_pf_ratio = Gauge('pvs_meter_tot_pf_ratio', 'Total power factor ratio', ['serial_number'])
meter_v12_v = Gauge('pvs_meter_v12_v', 'Line-to-line voltage V12 in V', ['serial_number'])
meter_v1n_v = Gauge('pvs_meter_v1n_v', 'Line-to-neutral voltage V1N in V', ['serial_number'])
meter_v2n_v = Gauge('pvs_meter_v2n_v', 'Line-to-neutral voltage V2N in V', ['serial_number'])

inverter_power_kw = Gauge('pvs_inverter_power_kw', 'Inverter power output in kW', ['serial_number'])
inverter_voltage_v = Gauge('pvs_inverter_voltage_v', 'Inverter voltage in V', ['serial_number'])
inverter_current_a = Gauge('pvs_inverter_current_a', 'Inverter current in A', ['serial_number'])
inverter_frequency_hz = Gauge('pvs_inverter_frequency_hz', 'Inverter frequency in Hz', ['serial_number'])
inverter_temperature_c = Gauge('pvs_inverter_temperature_c', 'Inverter temperature in Celsius', ['serial_number'])
inverter_lte_kwh = Gauge('pvs_inverter_lte_kwh', 'Inverter cumulative energy in kWh', ['serial_number'])
inverter_mppt_voltage_v = Gauge('pvs_inverter_mppt_voltage_v', 'Inverter MPPT voltage in V', ['serial_number'])
inverter_mppt_current_a = Gauge('pvs_inverter_mppt_current_a', 'Inverter MPPT current in A', ['serial_number'])
inverter_mppt_power_kw = Gauge('pvs_inverter_mppt_power_kw', 'Inverter MPPT power in kW', ['serial_number'])
inverter_model = Gauge('pvs_inverter_model', 'Inverter model', ['serial_number'])
inverter_last_report_date = Gauge('pvs_inverter_last_report_date', 'Inverter last report timestamp', ['serial_number'])
```