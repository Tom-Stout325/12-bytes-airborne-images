from finance.models import Transaction, Keyword

try:
    old_subcat_id = 23
    new_subcat_id = 4

    old_subcat = SubCategory.objects.get(id=old_subcat_id)
    new_subcat = SubCategory.objects.get(id=new_subcat_id)

    # Update transactions
    updated_count = Transaction.objects.filter(sub_cat=old_subcat).update(sub_cat=new_subcat)
    print(f"✅ Updated {updated_count} transactions from sub_cat_id={old_subcat_id} to sub_cat_id={new_subcat_id}.")

    # Delete old subcategory
    old_subcat.delete()
    print(f"🗑️ Successfully deleted SubCategory with id={old_subcat_id}.")

except SubCategory.DoesNotExist as e:
    print(f"❌ SubCategory not found: {e}")
except Exception as e:
    print(f"❌ An unexpected error occurred: {e}")



# Run script:  python manage.py shell < scripts/fix_subcategory.py


