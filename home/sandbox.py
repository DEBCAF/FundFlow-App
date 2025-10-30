
"""
Sandbox utility for local maintenance.

Run from project root:
  python -m home.sandbox        # interactive prompt
  python -m home.sandbox --yes  # skip prompt

This script deletes all rows from the SavingChanges table when confirmed.
"""

from home import app, db
from home.db_models import SavingChanges
import argparse


def clear_saving_changes(confirm: bool) -> None:
	with app.app_context():
		before = SavingChanges.query.count()
		print(f"SavingChanges rows before: {before}")
		if before == 0:
			print("Nothing to delete.")
			return

		if not confirm:
			resp = input("Type DELETE to confirm deletion of ALL SavingChanges rows: ")
			if resp.strip() != 'DELETE':
				print("Aborted by user.")
				return

		# perform deletion
		SavingChanges.query.delete()
		db.session.commit()
		after = SavingChanges.query.count()
		print(f"Deletion complete. SavingChanges rows after: {after}")


def main():
	parser = argparse.ArgumentParser(description='Sandbox utilities for FundFlow local development')
	parser.add_argument('--yes', '-y', action='store_true', help='Skip confirmation prompt and delete immediately')
	args = parser.parse_args()

	clear_saving_changes(confirm=args.yes)


if __name__ == '__main__':
	main()