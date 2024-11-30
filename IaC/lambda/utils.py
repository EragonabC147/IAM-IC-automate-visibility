import json
import boto3

def process_permission_sets(permission_sets, sso_utils, identity_store_id):
    """
    Procesa los permission sets y retorna los datos en un formato estructurado.
    """
    data = []

    for permission_set_arn in permission_sets:
        details = sso_utils.get_permission_set_details(permission_set_arn)
        policies = sso_utils.get_permission_set_policies(permission_set_arn)
        assignments = sso_utils.get_permission_set_assignments(permission_set_arn)

        for assignment in assignments:
            principal_id = assignment['PrincipalId']
            principal_type = assignment['PrincipalType']
            account_id = assignment['AccountId']
            principal_name = sso_utils.get_principal_name(principal_id, principal_type)
            if principal_type == 'GROUP':
                group_info = f"{principal_name} ({principal_id})"
                group_users = []
                response = sso_utils.sso_identity_store.list_group_memberships(
                    IdentityStoreId=identity_store_id,
                    GroupId=principal_id
                )
                for membership in response.get('GroupMemberships', []):
                    user_id = membership['MemberId']['UserId']
                    user_info = sso_utils.get_user_info(user_id)
                    group_users.append(user_info['UserName'])

                while 'NextToken' in response:
                    response = sso_utils.sso_identity_store.list_group_memberships(
                        IdentityStoreId=identity_store_id,
                        GroupId=principal_id,
                        NextToken=response['NextToken']
                    )
                    for membership in response.get('GroupMemberships', []):
                        user_id = membership['MemberId']['UserId']
                        user_info = sso_utils.get_user_info(user_id)
                        group_users.append(user_info['UserName'])

                for user_name in group_users:
                    entry = {
                        'PermissionSetArn': permission_set_arn,
                        'Name': details.get('Name'),
                        'Description': details.get('Description'),
                        'SessionDuration': details.get('SessionDuration'),
                        'AWSManagedPolicies': json.dumps(policies['AWSManagedPolicies'], indent=4, default=sso_utils.json_serial),
                        'CustomerManagedPolicies': json.dumps(policies['CustomerManagedPolicies'], indent=4, default=sso_utils.json_serial),
                        'InlinePolicy': json.dumps(json.loads(policies['InlinePolicy']), indent=4) if policies['InlinePolicy'] != 'No Inline Policy' else 'No Inline Policy',
                        'Group': group_info,
                        'User': user_name,
                        'AccountId': account_id
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
                    'Group': 'N/A',
                    'User': principal_name,
                    'AccountId': account_id
                }
                data.append(entry)

    return data


from datetime import datetime
import boto3

def upload_to_s3(file_path, bucket_name, object_name=None):
    """
    Sube un archivo a un bucket S3, con la posibilidad de incluir fecha y hora en el nombre.
    """
    s3_client = boto3.client('s3')

    # Generar un nombre con la fecha y hora si no se proporciona uno
    if object_name is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        object_name = f"{file_path.split('/')[-1].replace('.xlsx', '')}_{timestamp}.xlsx"

    try:
        s3_client.upload_file(file_path, bucket_name, object_name)
        return f"Archivo subido exitosamente a s3://{bucket_name}/{object_name}"
    except Exception as e:
        raise RuntimeError(f"Error al subir archivo a S3: {e}")

