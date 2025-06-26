#!/usr/bin/env python3
"""
Update fund configuration with user IDs from database by searching with aliases.
"""

import sys
import os
from pathlib import Path

# Add project root and src to path for imports
project_root = os.path.join(os.path.dirname(__file__), '..')
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, project_root)
sys.path.insert(0, src_path)

from core.bigquery_loader import BigQueryLoader
from core.fund_config import PREDEFINED_FUNDS, update_fund_user_id, get_fund_display_info


def get_fund_by_alias(alias, credentials_path=None, project_id="infinitepay-production"):
    """
    Get fund information by alias from the database.
    
    Args:
        alias: Fund alias to search for
        credentials_path: Optional path to service account credentials
        project_id: Google Cloud project ID
        
    Returns:
        dict: Fund information or None if not found
    """
    loader = BigQueryLoader(credentials_path, project_id)
    
    # Query to find fund by alias
    query = f"""
    SELECT 
        b.user_id,
        b.alias as fund_alias,
        COUNT(DISTINCT ce.id) as total_cessions,
        COUNT(DISTINCT co.id) as total_orders,
        MIN(co.created_at) as first_order_date,
        MAX(co.created_at) as last_order_date
    FROM `infinitepay-production.maindb.buyers` b
    LEFT JOIN `infinitepay-production.maindb.cessions` ce ON ce.buyer_id = b.user_id
    LEFT JOIN `infinitepay-production.maindb.cession_orders` co ON co.id = ce.cession_order_id
    WHERE b.alias = '{alias}'
    GROUP BY b.user_id, b.alias
    ORDER BY b.user_id
    """
    
    try:
        df, metadata = loader.load_from_query(query)
        if len(df) > 0:
            return df.iloc[0].to_dict()
        return None
    except Exception as e:
        print(f"❌ Error querying fund '{alias}': {e}")
        return None


def update_all_fund_configs():
    """
    Update all fund configurations by querying the database for user IDs.
    """
    print("🔍 UPDATING FUND CONFIGURATIONS FROM DATABASE")
    print("=" * 60)
    
    updated_count = 0
    not_found_count = 0
    already_configured_count = 0
    
    for fund_key, config in PREDEFINED_FUNDS.items():
        alias = config['alias']
        current_user_id = config['user_id']
        
        print(f"\n📋 Checking fund: {config['display_name']} (alias: {alias})")
        
        if current_user_id is not None:
            print(f"   ✅ Already configured with user ID: {current_user_id}")
            already_configured_count += 1
            continue
        
        # Query database for this alias
        print(f"   🔍 Searching database for alias '{alias}'...")
        fund_info = get_fund_by_alias(alias)
        
        if fund_info:
            user_id = int(fund_info['user_id'])
            fund_alias = fund_info['fund_alias']
            total_orders = fund_info['total_orders']
            
            print(f"   ✅ Found: {fund_alias} (ID: {user_id}, Orders: {total_orders})")
            
            # Update the configuration
            if update_fund_user_id(fund_key, user_id):
                print(f"   💾 Updated configuration")
                updated_count += 1
            else:
                print(f"   ❌ Failed to update configuration")
        else:
            print(f"   ⚠️  Not found in database")
            not_found_count += 1
    
    print(f"\n📊 SUMMARY")
    print("=" * 30)
    print(f"Already configured: {already_configured_count}")
    print(f"Updated: {updated_count}")
    print(f"Not found: {not_found_count}")
    print(f"Total funds: {len(PREDEFINED_FUNDS)}")
    
    if updated_count > 0:
        print(f"\n✅ Successfully updated {updated_count} fund configurations!")
        print("💡 Note: These updates are in memory only.")
        print("   To persist changes, you need to update the fund_config.py file manually.")
        
        print(f"\n📋 UPDATED CONFIGURATIONS:")
        print("-" * 40)
        for fund_key, config in PREDEFINED_FUNDS.items():
            if config['user_id'] is not None:
                print(f"{config['display_name']:15} | {config['alias']:15} | {config['user_id']}")
    
    return updated_count, not_found_count, already_configured_count


def search_fund_by_partial_alias(partial_alias):
    """
    Search for funds by partial alias match.
    
    Args:
        partial_alias: Partial alias to search for
    """
    loader = BigQueryLoader()
    
    query = f"""
    SELECT 
        b.user_id,
        b.alias as fund_alias,
        COUNT(DISTINCT co.id) as total_orders
    FROM `infinitepay-production.maindb.buyers` b
    LEFT JOIN `infinitepay-production.maindb.cessions` ce ON ce.buyer_id = b.user_id
    LEFT JOIN `infinitepay-production.maindb.cession_orders` co ON co.id = ce.cession_order_id
    WHERE LOWER(b.alias) LIKE LOWER('%{partial_alias}%')
    GROUP BY b.user_id, b.alias
    ORDER BY b.alias
    """
    
    try:
        df, metadata = loader.load_from_query(query)
        
        if len(df) > 0:
            print(f"🔍 SEARCH RESULTS FOR '{partial_alias}'")
            print("=" * 50)
            print(f"{'Alias':20} | {'User ID':10} | {'Orders':8}")
            print("-" * 40)
            
            for _, row in df.iterrows():
                alias = row['fund_alias'] or 'N/A'
                user_id = int(row['user_id']) if row['user_id'] else 'N/A'
                orders = int(row['total_orders']) if row['total_orders'] else 0
                
                print(f"{alias:20} | {str(user_id):10} | {orders:8}")
        else:
            print(f"❌ No funds found matching '{partial_alias}'")
            
    except Exception as e:
        print(f"❌ Error searching: {e}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Update fund configurations from database')
    parser.add_argument('--update-all', action='store_true', 
                       help='Update all fund configurations from database')
    parser.add_argument('--search', help='Search for funds by partial alias')
    parser.add_argument('--show-config', action='store_true',
                       help='Show current fund configurations')
    
    args = parser.parse_args()
    
    if args.show_config:
        print("🏦 CURRENT FUND CONFIGURATIONS")
        print("=" * 60)
        print(f"{'Display Name':20} | {'Alias':15} | {'User ID':10} | {'Status':15}")
        print("-" * 65)
        
        for info in get_fund_display_info():
            status = "✅ Configured" if info['configured'] else "⚠️  Needs Config"
            user_id_str = str(info['user_id']) if info['user_id'] else "Not Set"
            print(f"{info['display_name']:20} | {info['alias']:15} | {user_id_str:10} | {status:15}")
        
        return
    
    if args.search:
        search_fund_by_partial_alias(args.search)
        return
    
    if args.update_all:
        update_all_fund_configs()
        return
    
    # Default: show help
    parser.print_help()


if __name__ == "__main__":
    main() 