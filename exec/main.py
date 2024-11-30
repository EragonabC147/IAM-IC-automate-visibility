import pandas as pd
import json
import os
import logging
from dotenv import load_dotenv
from sso_utils import SSOUtils

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Cargar variables de entorno
load_dotenv()
INSTANCE_ARN = os.getenv('INSTANCE_ARN')
IDENTITY_STORE_ID = os.getenv('IDENTITY_STORE_ID')

# Inicializar SSOUtils
sso_utils = SSOUtils(instance_arn=INSTANCE_ARN, identity_store_id=IDENTITY_STORE_ID)

# Logging para inicio
logging.info("Iniciando script para obtener detalles de Permission Sets...")

# Obtener Permission Sets
logging.info("Obteniendo lista de Permission Sets...")
permission_sets = sso_utils.list_permission_sets()
logging.info(f"Se encontraron {len(permission_sets)} Permission Sets.")

# Almacenar datos procesados
data = []

for permission_set_arn in permission_sets:
    details = sso_utils.get_permission_set_details(permission_set_arn)
    policies = sso_utils.get_permission_set_policies(permission_set_arn)
    assignments = sso_utils.get_permission_set_assignments(permission_set_arn)

    for assignment in assignments:
        principal_id = assignment['PrincipalId']
        principal_type = assignment['PrincipalType']
        account_id = assignment['AccountId']  # Extrae el AccountId
        principal_name = sso_utils.get_principal_name(principal_id, principal_type)
        assignment['PrincipalName'] = principal_name
        if principal_type == 'GROUP':
            group_info = f"{principal_name} ({principal_id})"
            group_users = []
            # Obtener los usuarios del grupo
            response = sso_utils.sso_identity_store.list_group_memberships(
                IdentityStoreId=IDENTITY_STORE_ID,
                GroupId=principal_id
            )
            for membership in response.get('GroupMemberships', []):
                user_id = membership['MemberId']['UserId']
                user_info = sso_utils.get_user_info(user_id)
                group_users.append(user_info['UserName'])
                
            while 'NextToken' in response:
                response = sso_utils.sso_identity_store.list_group_memberships(
                    IdentityStoreId=IDENTITY_STORE_ID,
                    GroupId=principal_id,
                    NextToken=response['NextToken']
                )
                for membership in response.get('GroupMemberships', []):
                    user_id = membership['MemberId']['UserId']
                    user_info = sso_utils.get_user_info(user_id)
                    group_users.append(user_info['UserName'])
                
            # Agregar una fila por cada usuario en el grupo
            for user_name in group_users:
                entry = {
                    'PermissionSetArn': permission_set_arn,
                    'Name': details.get('Name'),
                    'Description': details.get('Description'),
                    'SessionDuration': details.get('SessionDuration'),
                    'AWSManagedPolicies': json.dumps(policies['AWSManagedPolicies'], indent=4, default=sso_utils.json_serial),
                    'CustomerManagedPolicies': json.dumps(policies['CustomerManagedPolicies'], indent=4, default=sso_utils.json_serial),
                    'InlinePolicy': json.dumps(json.loads(policies['InlinePolicy']), indent=4) if policies['InlinePolicy'] != 'No Inline Policy' else 'No Inline Policy',
                    'Assignments': json.dumps(assignments, indent=4, default=sso_utils.json_serial),
                    'Group': group_info,
                    'User': user_name,
                    'AccountId': account_id  # Añade el AccountId para cada usuario
                }
                data.append(entry)
        else:
            entry = {
                'PermissionSetArn': permission_set_arn,
                'Name': details.get('Name'),
                'Description': details.get('Description'),
                'SessionDuration': details.get('SessionDuration'),
                'AWSManagedPolicies': json.dumps(policies['AWSManagedPolicies'], indent=4, default=sso_utils.json_serial),
                'CustomerManagedPolicies': json.dumps(policies['CustomerManagedPolicies'], indent=4, default=sso_utils.json_serial),
                'InlinePolicy': json.dumps(json.loads(policies['InlinePolicy']), indent=4) if policies['InlinePolicy'] != 'No Inline Policy' else 'No Inline Policy',
                'Assignments': json.dumps(assignments, indent=4, default=sso_utils.json_serial),
                'Group': 'N/A',
                'User': principal_name,
                'AccountId': account_id  # Añade el AccountId para el usuario
            }
            data.append(entry)

# Logging para exportación
logging.info("Exportando datos a archivo Excel...")

# Exportar a Excel
df = pd.DataFrame(data)
output_file = 'permission_sets_with_details.xlsx'
df.to_excel(output_file, index=False)

logging.info(f"Archivo Excel generado: {output_file}")
