#!/usr/bin/env python3
"""
Fund configuration system for predefined funds.
"""

# Predefined fund configurations
PREDEFINED_FUNDS = {
    'pi': {
        'user_id': 20697244,
        'alias': 'pi',
        'name': 'PI Fund',
        'display_name': 'PI Fund',
        'description': 'PI Fund (Legacy)'
    },
    'ai': {
        'user_id': 19441218,
        'alias': 'ai', 
        'name': 'AI Fund',
        'display_name': 'AI Fund',
        'description': 'AI Fund (Legacy)'
    },
    'akira1': {
        'user_id': 942732,
        'alias': 'akira_1',
        'name': 'Akira 1',
        'display_name': 'Akira 1',
        'description': 'Akira Fund 1'
    },
    'akira2': {
        'user_id': 942740,
        'alias': 'akira_2',
        'name': 'Akira 2', 
        'display_name': 'Akira 2',
        'description': 'Akira Fund 2'
    },
    'bigpicture1': {
        'user_id': 16548294,
        'alias': 'bigpicture_1',
        'name': 'Big Picture 1',
        'display_name': 'Big Picture 1',
        'description': 'Big Picture Fund 1'
    },
    'bigpicture2': {
        'user_id': 16548300,
        'alias': 'bigpicture_2',
        'name': 'Big Picture 2',
        'display_name': 'Big Picture 2', 
        'description': 'Big Picture Fund 2'
    },
    'bigpicture3': {
        'user_id': 16548303,
        'alias': 'bigpicture_3',
        'name': 'Big Picture 3',
        'display_name': 'Big Picture 3',
        'description': 'Big Picture Fund 3'
    },
    'bigpicture4': {
        'user_id': 16548312,
        'alias': 'bigpicture_4',
        'name': 'Big Picture 4',
        'display_name': 'Big Picture 4',
        'description': 'Big Picture Fund 4'
    },
    'kickass1': {
        'user_id': None,  # To be filled with actual user ID
        'alias': 'kickass_1',
        'name': 'Kickass 1',
        'display_name': 'Kickass 1',
        'description': 'Kickass Fund 1'
    },
    'kickass2': {
        'user_id': None,  # To be filled with actual user ID
        'alias': 'kickass_2',
        'name': 'Kickass 2',
        'display_name': 'Kickass 2',
        'description': 'Kickass Fund 2'
    }
}


def get_fund_config(fund_alias):
    """
    Get fund configuration by alias.
    
    Args:
        fund_alias: Fund alias (e.g., 'pi', 'ai', 'akira1', etc.)
        
    Returns:
        dict: Fund configuration or None if not found
    """
    return PREDEFINED_FUNDS.get(fund_alias.lower())


def get_all_fund_aliases():
    """
    Get list of all predefined fund aliases.
    
    Returns:
        list: List of fund aliases
    """
    return list(PREDEFINED_FUNDS.keys())


def get_fund_user_id(fund_alias):
    """
    Get user ID for a fund alias.
    
    Args:
        fund_alias: Fund alias
        
    Returns:
        int: User ID or None if not found or not configured
    """
    config = get_fund_config(fund_alias)
    return config['user_id'] if config else None


def is_predefined_fund(fund_alias):
    """
    Check if a fund alias is predefined.
    
    Args:
        fund_alias: Fund alias to check
        
    Returns:
        bool: True if predefined, False otherwise
    """
    return fund_alias.lower() in PREDEFINED_FUNDS


def get_configured_funds():
    """
    Get list of funds that have user_id configured (not None).
    
    Returns:
        list: List of fund aliases that are fully configured
    """
    return [alias for alias, config in PREDEFINED_FUNDS.items() 
            if config['user_id'] is not None]


def get_fund_display_info():
    """
    Get display information for all predefined funds.
    
    Returns:
        list: List of dicts with display information
    """
    return [
        {
            'alias': alias,
            'display_name': config['display_name'],
            'user_id': config['user_id'],
            'description': config['description'],
            'configured': config['user_id'] is not None
        }
        for alias, config in PREDEFINED_FUNDS.items()
    ]


def update_fund_user_id(fund_alias, user_id):
    """
    Update user ID for a predefined fund.
    
    Args:
        fund_alias: Fund alias
        user_id: User ID to set
        
    Returns:
        bool: True if updated successfully, False if fund not found
    """
    if fund_alias.lower() in PREDEFINED_FUNDS:
        PREDEFINED_FUNDS[fund_alias.lower()]['user_id'] = user_id
        return True
    return False


if __name__ == "__main__":
    # Display all fund configurations
    print("🏦 PREDEFINED FUND CONFIGURATIONS")
    print("=" * 50)
    
    for info in get_fund_display_info():
        status = "✅ Configured" if info['configured'] else "⚠️  Needs User ID"
        user_id_str = str(info['user_id']) if info['user_id'] else "Not Set"
        print(f"{info['display_name']:15} | {info['alias']:12} | {user_id_str:10} | {status}")
    
    print("\n📊 SUMMARY")
    print(f"Total funds: {len(PREDEFINED_FUNDS)}")
    print(f"Configured: {len(get_configured_funds())}")
    print(f"Need configuration: {len(PREDEFINED_FUNDS) - len(get_configured_funds())}") 