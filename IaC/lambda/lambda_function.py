import pandas as pd
import os
import logging
from datetime import datetime
from sso_utils import SSOUtils
from utils import process_permission_sets, upload_to_s3

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Variables de entorno
INSTANCE_ARN = os.environ['INSTANCE_ARN']
IDENTITY_STORE_ID = os.environ['IDENTITY_STORE_ID']
S3_BUCKET = os.environ['S3_BUCKET']

# Inicializar SSOUtils
sso_utils = SSOUtils(instance_arn=INSTANCE_ARN, identity_store_id=IDENTITY_STORE_ID)

def lambda_handler(event, context):
    try:
        logging.info("Iniciando procesamiento de Permission Sets...")

        # Obtener lista de Permission Sets
        permission_sets = sso_utils.list_permission_sets()
        logging.info(f"Se encontraron {len(permission_sets)} Permission Sets.")

        # Procesar los datos
        data = process_permission_sets(permission_sets, sso_utils, IDENTITY_STORE_ID)

        # Exportar a Excel
        output_file = f"/tmp/permission_sets_with_details_.xlsx"  # Incluye fecha y hora en el nombre
        df = pd.DataFrame(data)
        df.to_excel(output_file, index=False)
        logging.info(f"Archivo Excel generado: {output_file}")

        # Subir a S3
        s3_result = upload_to_s3(output_file, S3_BUCKET)
        logging.info(s3_result)

        return {
            'statusCode': 200,
            'body': {
                'message': 'Procesamiento completado y archivo subido a S3.',
                's3_result': s3_result
            }
        }
    except Exception as e:
        logging.error(f"Error durante la ejecución: {e}")
        return {
            'statusCode': 500,
            'body': {
                'message': 'Error durante la ejecución.',
                'error': str(e)
            }
        }
