import boto3
from datetime import datetime

class SSOUtils:
    def __init__(self, instance_arn, identity_store_id):
        self.instance_arn = instance_arn
        self.identity_store_id = identity_store_id
        session = boto3.Session()
        self.sso_admin = session.client('sso-admin')
        self.sso_identity_store = session.client('identitystore')

    def json_serial(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")

    def list_permission_sets(self):
        try:
            permission_sets = []
            response = self.sso_admin.list_permission_sets(InstanceArn=self.instance_arn)
            permission_sets.extend(response['PermissionSets'])

            while 'NextToken' in response:
                response = self.sso_admin.list_permission_sets(
                    InstanceArn=self.instance_arn,
                    NextToken=response['NextToken']
                )
                permission_sets.extend(response['PermissionSets'])

            return permission_sets
        except Exception as e:
            raise RuntimeError(f"Error al listar Permission Sets: {e}")


    def get_permission_set_details(self, permission_set_arn):
        response = self.sso_admin.describe_permission_set(
            InstanceArn=self.instance_arn,
            PermissionSetArn=permission_set_arn
        )
        return response['PermissionSet']

    def get_permission_set_policies(self, permission_set_arn):
        policies = {}
        managed_policies_response = self.sso_admin.list_managed_policies_in_permission_set(
            InstanceArn=self.instance_arn,
            PermissionSetArn=permission_set_arn
        )
        policies['AWSManagedPolicies'] = managed_policies_response['AttachedManagedPolicies']

        customer_managed_policies_response = self.sso_admin.list_customer_managed_policy_references_in_permission_set(
            InstanceArn=self.instance_arn,
            PermissionSetArn=permission_set_arn
        )
        policies['CustomerManagedPolicies'] = customer_managed_policies_response['CustomerManagedPolicyReferences']

        inline_policy_response = self.sso_admin.get_inline_policy_for_permission_set(
            InstanceArn=self.instance_arn,
            PermissionSetArn=permission_set_arn
        )
        inline_policy = inline_policy_response.get('InlinePolicy', 'No Inline Policy')
        policies['InlinePolicy'] = inline_policy if inline_policy else 'No Inline Policy'

        return policies

    def get_permission_set_assignments(self, permission_set_arn):
        assignments = []
        accounts = []
        response = self.sso_admin.list_accounts_for_provisioned_permission_set(
            InstanceArn=self.instance_arn,
            PermissionSetArn=permission_set_arn
        )
        accounts.extend(response['AccountIds'])

        while 'NextToken' in response:
            response = self.sso_admin.list_accounts_for_provisioned_permission_set(
                InstanceArn=self.instance_arn,
                PermissionSetArn=permission_set_arn,
                NextToken=response['NextToken']
            )
            accounts.extend(response['AccountIds'])

        for account_id in accounts:
            response = self.sso_admin.list_account_assignments(
                InstanceArn=self.instance_arn,
                AccountId=account_id,
                PermissionSetArn=permission_set_arn
            )
            assignments.extend(response['AccountAssignments'])

            while 'NextToken' in response:
                response = self.sso_admin.list_account_assignments(
                    InstanceArn=self.instance_arn,
                    AccountId=account_id,
                    PermissionSetArn=permission_set_arn,
                    NextToken=response['NextToken']
                )
                assignments.extend(response['AccountAssignments'])

        return assignments

    def get_principal_name(self, principal_id, principal_type):
        try:
            if principal_type == 'USER':
                response = self.sso_identity_store.describe_user(
                    IdentityStoreId=self.identity_store_id,
                    UserId=principal_id
                )
                return response['UserName']
            elif principal_type == 'GROUP':
                response = self.sso_identity_store.describe_group(
                    IdentityStoreId=self.identity_store_id,
                    GroupId=principal_id
                )
                return response['DisplayName']
        except self.sso_identity_store.exceptions.ResourceNotFoundException:
            return 'Not Found'

    def get_user_info(self, user_id):
        response = self.sso_identity_store.describe_user(
            IdentityStoreId=self.identity_store_id,
            UserId=user_id
        )
        return {'UserName': response['UserName']}
