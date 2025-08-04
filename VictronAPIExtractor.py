import requests
import time
import json
import csv
import os

# =====================
# PARAMETRI PERSONALIZZABILI
# =====================
TOKEN = 'token value'
INSTALLATION_ID = 'your installation id'

# Mappa: instance -> nome dispositivo
INSTANCE_DEVICE_MAP = {
    293: "Inverter",
    291: "MPPT",
    290: "Batteria",
    1:   "BMS",
}

# File di log JSON incrementale
JSON_LOG_FILE = 'victron_full_responses.json'
# File CSV finale
CSV_OUTPUT_FILE = 'extracted_data.csv'

# =====================
# FUNZIONE: CARICA LOG ESISTENTE
# =====================
def load_existing_log():
    if os.path.exists(JSON_LOG_FILE):
        with open(JSON_LOG_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

# =====================
# FUNZIONE: SALVA LOG
# =====================
def save_log(log_data):
    with open(JSON_LOG_FILE, 'w') as f:
        json.dump(log_data, f, indent=2)

# =====================
# FUNZIONE PRINCIPALE
# =====================
def main():
    # Carica log esistente per resume
    full_responses = load_existing_log()

    # Determina attributi già processati (per resume)
    processed_keys = {(entry["attribute_id"], entry["instance"]) for entry in full_responses}

    # URL API
    url_template = f'https://vrmapi.victronenergy.com/v2/installations/{INSTALLATION_ID}/widgets/Graph?attributeIds%5B%5D={{}}&instance={{}}'

    headers = {
        'Content-Type': 'application/json',
        'x-authorization': f'Token {TOKEN}'
    }

    # Mappa dinamica compatibilità
    compatibility_map = {}

    # Range attribute_id
    attribute_ids = range(1, 3500)

    print("Inizio raccolta dati API...")

    for attribute_id in attribute_ids:
        for instance, device_name in INSTANCE_DEVICE_MAP.items():
            key = (attribute_id, instance)
            if key in processed_keys:
                continue  # già processato

            print(f"Richiedo attribute_id={attribute_id} per instance={instance} ({device_name})...")

            url = url_template.format(attribute_id, instance)
            try:
                response = requests.get(url, headers=headers)
                if response.status_code == 429:
                    print("Rate limit raggiunto, attendo 1 secondo...")
                    time.sleep(1)
                    continue

                api_data = response.json()

                # Salva nel log
                entry = {
                    "attribute_id": attribute_id,
                    "instance": instance,
                    "device_name": device_name,
                    "response": api_data
                }
                full_responses.append(entry)

                # Controllo compatibilità: dati non vuoti in data[attribute_id]
                records = api_data.get("records", {})
                data_dict = records.get("data", {})
                data_points = data_dict.get(str(attribute_id), [])

                if isinstance(data_points, list) and len(data_points) > 0:
                    # Compatibile: aggiungi device_name a lista
                    if attribute_id not in compatibility_map:
                        compatibility_map[attribute_id] = []
                    if device_name not in compatibility_map[attribute_id]:
                        compatibility_map[attribute_id].append(device_name)

                # Salva log ad ogni iterazione per sicurezza
                save_log(full_responses)

                # Rispetta rate limit
                time.sleep(0.33)

            except requests.exceptions.RequestException as e:
                print(f"Errore richiesta attribute_id={attribute_id} instance={instance}: {e}")
                continue

    print("Raccolta dati completata. Creazione CSV...")

    # Creazione CSV
    fieldnames = [
        'attribute_id', 'instance', 'device_name',
        'code', 'description',
        'formatted_value', 'format_value_only', 'format_with_unit',
        'dispositivi_compatibili'
    ]

    with open(CSV_OUTPUT_FILE, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        valid_records_count = 0

        for entry in full_responses:
            attribute_id = entry["attribute_id"]
            instance = entry["instance"]
            device_name = entry["device_name"]
            response = entry["response"]

            records = response.get("records", {})
            data_dict = records.get("data", {})
            meta_dict = records.get("meta", {})

            # Dati meta e compatibilità
            meta = meta_dict.get(str(attribute_id), {})
            code = meta.get("code", "N/A")
            description = meta.get("description", "N/A")
            format_value_only = meta.get("formatValueOnly", "N/A")
            format_with_unit = meta.get("formatWithUnit", "N/A")

            # Verifica compatibilità
            dispositivi_compatibili = compatibility_map.get(attribute_id, ["Non compatibile"])
            dispositivi_compatibili_str = ", ".join(dispositivi_compatibili)

            writer.writerow({
                'attribute_id': attribute_id,
                'instance': instance,
                'device_name': device_name,
                'code': code,
                'description': description,
                'formatted_value': "N/A",  # non presente nei tuoi esempi
                'format_value_only': format_value_only,
                'format_with_unit': format_with_unit,
                'dispositivi_compatibili': dispositivi_compatibili_str
            })

            valid_records_count += 1

    print(f"CSV creato: {CSV_OUTPUT_FILE}")
    print(f"Totale record processati: {valid_records_count}")


if __name__ == "__main__":
    main()
