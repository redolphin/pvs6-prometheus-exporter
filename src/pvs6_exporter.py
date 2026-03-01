# from dotenv import load_dotenv
# load_dotenv()  # reads variables from a .env file and sets them in os.environ

import asyncio
import os
import logging
import base64
import aiohttp
from prometheus_client import start_http_server, Gauge

from pypvs.const import SupportedFeatures
from pypvs.exceptions import ENDPOINT_PROBE_EXCEPTIONS
from pypvs.models.common import CommonProperties
from pypvs.models.pvs import PVSData
from pypvs.pvs import PVS
from pypvs.updaters.meter import PVSProductionMetersUpdater
from pypvs.updaters.gateway import PVSGatewayUpdater
from pypvs.updaters.production_inverters import PVSProductionInvertersUpdater


# --- Configuration ---
PVS6_IP = os.getenv('PVS6_IP', '192.168.1.100')  # Set your PVS IP here
PVS6_SN = os.getenv('PVS6_SN', '')  # Used for password derivation
# Default password is last 5 chars of serial if not manually provided
PVS6_PASSWORD = os.getenv('PVS6_PASSWORD', PVS6_SN[-5:] if PVS6_SN else '')
POLLING_INTERVAL = int(os.getenv('POLLING_INTERVAL', '30'))
EXPORTER_PORT = int(os.getenv('EXPORTER_PORT', '8000'))
PVS6_USER = 'ssm_owner'

# --- Logging ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

if not PVS6_PASSWORD:
    logger.error("Error: PVS6_PASSWORD or PVS6_SERIAL environment variable is required.")
    exit(1)

# --- Prometheus Metrics ---
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

async def main():
    logger.info(f"Starting PVS Exporter on port {EXPORTER_PORT}")
    start_http_server(EXPORTER_PORT)

    async with aiohttp.ClientSession() as session:
        pvs = PVS(session=session, host=PVS6_IP, user=PVS6_USER)
        try:
            await pvs.discover()
            pvs_serial = pvs.serial_number
            # The password is the last 5 characters of the PVS serial number
            pvs_password = pvs_serial[-5:]
            await pvs.setup(auth_password=pvs_password)
            logging.info(f"Connected to PVS with serial: {pvs_serial}")
        except ENDPOINT_PROBE_EXCEPTIONS as e:
            logging.error(f"Cannot communicate with the PVS: {e}")
            return

        common_properties = CommonProperties()
        meter_updater = PVSProductionMetersUpdater(
            pvs.getVarserverVar, pvs.getVarserverVars, common_properties
        )
        gateway_updater = PVSGatewayUpdater(
            pvs.getVarserverVar, pvs.getVarserverVars, common_properties
        )

        discovered_features = SupportedFeatures(0)
        meter_is_there = await meter_updater.probe(discovered_features)
        gateway_is_there = await gateway_updater.probe(discovered_features)
        inverter_updater = PVSProductionInvertersUpdater(
            pvs.getVarserverVar, pvs.getVarserverVars, common_properties
        )

        if not meter_is_there:
            print("No meters found for that PVS on varserver")
            return

        if not gateway_is_there:
            print("No gateways found for that PVS on varserver")
            return

        if not gateway_is_there:
            print("No gateways found for that PVS on varserver")
            return

        # setup a periodic task to fetch data every 5 seconds
        pvs_data = PVSData()
        while True:
            await meter_updater.update(pvs_data)
            await gateway_updater.update(pvs_data)
            await inverter_updater.update(pvs_data)

            gateway = pvs_data.gateway

            logging.info("------------------------------")
            logging.info(">>>> Gateway:")
            logging.info("------------------------------")

            logging.info(f"{pvs.serial_number}: {gateway}")
            logging.info("------------------------------")
            logging.info(">>>>>> Meters:")
            logging.info("------------------------------")

            for k, v in enumerate(pvs_data.meters.values()):
                logging.info(f"{v.serial_number}: {v}")

                meter_power_kw.labels(serial_number=v.serial_number).set(float(v.power_3ph_kw))
                meter_voltage_v.labels(serial_number=v.serial_number).set(float(v.voltage_3ph_v))
                meter_current_a.labels(serial_number=v.serial_number).set(float(v.current_3ph_a))
                meter_freq_hz.labels(serial_number=v.serial_number).set(float(v.freq_hz))
                meter_lte_kwh.labels(serial_number=v.serial_number).set(float(v.lte_3ph_kwh))
                meter_ct_scale.labels(serial_number=v.serial_number).set(float(v.ct_scale_factor))
                meter_i1_a.labels(serial_number=v.serial_number).set(float(v.i1_a))
                meter_i2_a.labels(serial_number=v.serial_number).set(float(v.i2_a))
                meter_neg_lte_kwh.labels(serial_number=v.serial_number).set(float(v.neg_lte_kwh))
                meter_net_lte_kwh.labels(serial_number=v.serial_number).set(float(v.net_lte_kwh))
                meter_p1_kw.labels(serial_number=v.serial_number).set(float(v.p1_kw))
                meter_p2_kw.labels(serial_number=v.serial_number).set(float(v.p2_kw))
                meter_pos_lte_kwh.labels(serial_number=v.serial_number).set(float(v.pos_lte_kwh))
                meter_q3phsum_kvar.labels(serial_number=v.serial_number).set(float(v.q3phsum_kvar))
                meter_s3phsum_kva.labels(serial_number=v.serial_number).set(float(v.s3phsum_kva))
                meter_tot_pf_ratio.labels(serial_number=v.serial_number).set(float(v.tot_pf_ratio))
                meter_v12_v.labels(serial_number=v.serial_number).set(float(v.v12_v))
                meter_v1n_v.labels(serial_number=v.serial_number).set(float(v.v1n_v))
                meter_v2n_v.labels(serial_number=v.serial_number).set(float(v.v2n_v))

            for k, v in pvs_data.inverters.items():
                inverter_power_kw.labels(serial_number=v.serial_number).set(float(v.last_report_kw))
                inverter_voltage_v.labels(serial_number=v.serial_number).set(float(v.last_report_voltage_v))
                inverter_current_a.labels(serial_number=v.serial_number).set(float(v.last_report_current_a))
                inverter_frequency_hz.labels(serial_number=v.serial_number).set(float(v.last_report_frequency_hz))
                inverter_temperature_c.labels(serial_number=v.serial_number).set(float(v.last_report_temperature_c))
                inverter_lte_kwh.labels(serial_number=v.serial_number).set(float(v.lte_kwh))
                inverter_mppt_voltage_v.labels(serial_number=v.serial_number).set(float(v.last_mppt_voltage_v))
                inverter_mppt_current_a.labels(serial_number=v.serial_number).set(float(v.last_mppt_current_a))
                inverter_mppt_power_kw.labels(serial_number=v.serial_number).set(float(v.last_mppt_power_kw))

            logging.info("------------------------------")
            logging.info(">>>>>> Inverters:")
            logging.info("------------------------------")

            for inverter in pvs_data.inverters.values():
                logging.info(f"{inverter.serial_number}: {inverter}")

            await asyncio.sleep(POLLING_INTERVAL)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exiting...")