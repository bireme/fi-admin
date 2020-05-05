
# IMPORTANT: CHANGE TO THE NEXT ID IN FI-ADMIN
START_ID=1

''' PRODUCTION

DATABASES = {
    'cwis': {
        'host': 'mysql.bireme.br',
        'user': 'oer',
        'password': 'oerhm',
        'db': 'cwis-ops',
    },
    'aux': {
        'host': 'mysql.bireme.br',
        'user': 'fi-admin',
        'password': 'fi-admin@bireme',
        'db': 'fi-admin',
    }
}
'''

''' TEST '''
DATABASES = {
    'cwis': {
        'host': 'mysql.bireme.br',
        'user': 'oer',
        'password': 'oerhm',
        'db': 'cwis-ops',
    },
    'aux': {
        'host': 'basalto08.bireme.br',
        'user': 'fi-admin-user',
        'password': 'fi@admin2015',
        'db': 'fi_admin_tst',
    }
}

export_filename='oer_regional_ops.json'
log_filename='oer_regional_ops.log'
cvsp_node='regional'
cc_code='PA1.1'
oer_content_type_id=75
